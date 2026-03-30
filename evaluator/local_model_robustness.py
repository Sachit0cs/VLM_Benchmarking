"""
Unified local-model robustness evaluator.

This module is the single engine for local model robustness runs across:
- typographic attacks (clean vs poisoned image pairs from mapping CSV)
- perturbation attacks (clean vs perturbed folders with optional labels)
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch
from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _normalize_text(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def _extract_target_label(poison_text: str) -> Optional[str]:
    text = _normalize_text(poison_text)
    if "output cat" in text:
        return "cat"
    if "apple" in text:
        return "apple"
    if "answer only yes" in text:
        return "yes"
    if "safe output" in text:
        return "safe"
    if "stop" in text:
        return "stop sign"
    if "warning" in text:
        return "warning"
    return None


@dataclass
class PairRecord:
    filename: str
    clean_path: Path
    perturbed_path: Path
    attack_type: str
    poison_text: Optional[str] = None
    target_label: Optional[str] = None
    label: Optional[str] = None


class VisionClassifier:
    def predict(self, image: Image.Image) -> Tuple[str, float]:
        raise NotImplementedError


class TorchVisionClassifier(VisionClassifier):
    def __init__(self, model_name: str, device: str = "cpu"):
        from torchvision.models import (
            ResNet50_Weights,
            ViT_B_16_Weights,
            resnet50,
            vit_b_16,
        )

        self.model_name = model_name
        self.device = device

        if model_name == "resnet50":
            self.weights = ResNet50_Weights.DEFAULT
            self.model = resnet50(weights=self.weights).eval().to(self.device)
            self.categories = self.weights.meta["categories"]
            self.preprocess = self.weights.transforms()
        elif model_name == "vit_b_16":
            self.weights = ViT_B_16_Weights.DEFAULT
            self.model = vit_b_16(weights=self.weights).eval().to(self.device)
            self.categories = self.weights.meta["categories"]
            self.preprocess = self.weights.transforms()
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Tuple[str, float]:
        tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        logits = self.model(tensor)
        probs = torch.softmax(logits, dim=-1)[0]
        conf, idx = torch.max(probs, dim=0)
        return self.categories[idx.item()], float(conf.item())


class DinoV2Classifier(VisionClassifier):
    def __init__(self, device: str = "cpu"):
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        self.device = device
        model_id = "facebook/dinov2-base-imagenet1k-1-layer"
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageClassification.from_pretrained(model_id).to(self.device).eval()
        self.id2label = self.model.config.id2label

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Tuple[str, float]:
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        conf, idx = torch.max(probs, dim=0)
        label = self.id2label[int(idx.item())]
        return label, float(conf.item())


class ClipZeroShotClassifier(VisionClassifier):
    def __init__(self, labels: Sequence[str], device: str = "cpu"):
        from transformers import CLIPModel, CLIPProcessor

        self.device = device
        self.model_id = "openai/clip-vit-base-patch32"
        self.processor = CLIPProcessor.from_pretrained(self.model_id)
        self.model = CLIPModel.from_pretrained(self.model_id).to(self.device).eval()
        self.labels = list(dict.fromkeys([l for l in labels if l]))
        if not self.labels:
            self.labels = [
                "cat",
                "dog",
                "apple",
                "banana",
                "person",
                "car",
                "tree",
                "building",
                "food",
                "street",
                "indoor scene",
                "outdoor scene",
                "stop sign",
                "warning",
                "safe",
                "yes",
            ]

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Tuple[str, float]:
        texts = [f"a photo of {label}" for label in self.labels]
        inputs = self.processor(text=texts, images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        outputs = self.model(**inputs)
        logits = outputs.logits_per_image[0]
        probs = torch.softmax(logits, dim=-1)
        conf, idx = torch.max(probs, dim=0)
        return self.labels[idx.item()], float(conf.item())


def _load_typographic_pairs(mapping_csv: Path) -> List[PairRecord]:
    pairs: List[PairRecord] = []
    with mapping_csv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            clean = Path(row["original_path"])
            pert = Path(row["poison_path"])
            if not clean.exists() or not pert.exists():
                continue
            poison_text = row.get("poison_text", "")
            pairs.append(
                PairRecord(
                    filename=row.get("filename", clean.name),
                    clean_path=clean,
                    perturbed_path=pert,
                    attack_type="typographic",
                    poison_text=poison_text,
                    target_label=_extract_target_label(poison_text),
                )
            )
    return pairs


def _load_perturbation_pairs(clean_dir: Path, perturbed_dir: Path, labels_csv: Optional[Path]) -> List[PairRecord]:
    pairs: List[PairRecord] = []
    label_map: Dict[str, str] = {}

    if labels_csv and labels_csv.exists():
        with labels_csv.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                image_file = row.get("image_file")
                label = row.get("label")
                if image_file:
                    label_map[image_file] = label or ""

    if label_map:
        for image_file, label in label_map.items():
            clean_path = clean_dir / image_file
            pert_path = perturbed_dir / image_file
            if clean_path.exists() and pert_path.exists():
                pairs.append(
                    PairRecord(
                        filename=image_file,
                        clean_path=clean_path,
                        perturbed_path=pert_path,
                        attack_type="perturbation",
                        label=label,
                    )
                )
    else:
        clean_files = {
            p.name: p
            for p in clean_dir.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        }
        pert_files = {
            p.name: p
            for p in perturbed_dir.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        }
        for name in sorted(set(clean_files).intersection(pert_files)):
            pairs.append(
                PairRecord(
                    filename=name,
                    clean_path=clean_files[name],
                    perturbed_path=pert_files[name],
                    attack_type="perturbation",
                )
            )

    return pairs


def _accuracy(preds: List[str], labels: List[str]) -> Optional[float]:
    if not labels:
        return None
    correct = sum(int(p == y) for p, y in zip(preds, labels))
    return correct / len(labels)


def _evaluate_model(model_name: str, model: VisionClassifier, pairs: List[PairRecord]) -> Dict:
    details: List[Dict] = []
    changed = 0
    target_hits = 0
    target_total = 0
    failed_images = 0

    clean_preds: List[str] = []
    pert_preds: List[str] = []
    labels: List[str] = []

    for pair in pairs:
        try:
            with Image.open(pair.clean_path) as img_c:
                clean_img = img_c.convert("RGB")
            with Image.open(pair.perturbed_path) as img_p:
                pert_img = img_p.convert("RGB")

            pred_clean, conf_clean = model.predict(clean_img)
            pred_pert, conf_pert = model.predict(pert_img)
        except Exception as exc:
            failed_images += 1
            details.append(
                {
                    "filename": pair.filename,
                    "attack_type": pair.attack_type,
                    "poison_text": pair.poison_text,
                    "target_label": pair.target_label,
                    "label": pair.label,
                    "error": str(exc),
                }
            )
            continue

        is_changed = pred_clean != pred_pert
        changed += int(is_changed)

        target_hit = None
        if pair.target_label:
            target_total += 1
            target_hit = pair.target_label in _normalize_text(pred_pert)
            target_hits += int(target_hit)

        if pair.label:
            labels.append(pair.label)
            clean_preds.append(pred_clean)
            pert_preds.append(pred_pert)

        details.append(
            {
                "filename": pair.filename,
                "attack_type": pair.attack_type,
                "poison_text": pair.poison_text,
                "target_label": pair.target_label,
                "label": pair.label,
                "clean_pred": pred_clean,
                "clean_conf": conf_clean,
                "perturbed_pred": pred_pert,
                "perturbed_conf": conf_pert,
                "prediction_changed": is_changed,
                "target_hit": target_hit,
            }
        )

    n = len(details)
    clean_acc = _accuracy(clean_preds, labels)
    pert_acc = _accuracy(pert_preds, labels)

    payload = {
        "num_pairs": n,
        "failed_images": failed_images,
        "prediction_change_rate": (changed / n) if n else 0.0,
        "target_hit_rate": (target_hits / target_total) if target_total else None,
        "avg_conf_clean": (sum(d["clean_conf"] for d in details) / n) if n else 0.0,
        "avg_conf_perturbed": (sum(d["perturbed_conf"] for d in details) / n) if n else 0.0,
        "clean_accuracy": clean_acc,
        "perturbed_accuracy": pert_acc,
        "accuracy_drop_abs": (clean_acc - pert_acc) if clean_acc is not None and pert_acc is not None else None,
        "accuracy_drop_pct_points": (
            (clean_acc - pert_acc) * 100.0 if clean_acc is not None and pert_acc is not None else None
        ),
        "details": details,
    }
    return payload


def _resolve_existing_dir(candidates: Sequence[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return candidates[0]


def _write_markdown_report(report: Dict, output_md: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Local Model Robustness Report",
        "",
        f"- attack_type: {report['attack_type']}",
        f"- dataset: {report['dataset']}",
        f"- num_samples: {report['num_samples']}",
        f"- device: {report['device']}",
        "",
        "## Summary",
        "",
        "| Model | Pairs | Change Rate | Target Hit Rate | Clean Acc | Perturbed Acc | Drop (pp) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for model_name, metrics in report["results"].items():
        thr = "N/A" if metrics["target_hit_rate"] is None else f"{100.0 * metrics['target_hit_rate']:.1f}%"
        clean_acc = "N/A" if metrics["clean_accuracy"] is None else f"{100.0 * metrics['clean_accuracy']:.1f}%"
        pert_acc = "N/A" if metrics["perturbed_accuracy"] is None else f"{100.0 * metrics['perturbed_accuracy']:.1f}%"
        drop_pp = "N/A" if metrics["accuracy_drop_pct_points"] is None else f"{metrics['accuracy_drop_pct_points']:.2f}"
        lines.append(
            f"| {model_name} | {metrics['num_pairs']} | {100.0 * metrics['prediction_change_rate']:.1f}% | {thr} | {clean_acc} | {pert_acc} | {drop_pp} |"
        )

    if report["skipped"]:
        lines.append("")
        lines.append("## Skipped")
        lines.append("")
        for model_name, reason in report["skipped"].items():
            lines.append(f"- {model_name}: {reason}")

    output_md.write_text("\n".join(lines), encoding="utf-8")


def run_local_robustness(
    mode: str,
    clean_dir: Path,
    perturbed_dir: Path,
    labels: Optional[Path],
    mapping_csv: Path,
    output: Path,
    output_md: Optional[Path],
    device: Optional[str],
    model_names: Optional[Sequence[str]] = None,
    max_samples: Optional[int] = None,
) -> Dict:
    device_name = device or ("cuda" if torch.cuda.is_available() else "cpu")

    if mode == "typographic":
        pairs = _load_typographic_pairs(mapping_csv)
        dataset_name = str(mapping_csv)
    else:
        clean_dir = _resolve_existing_dir(
            [
                clean_dir,
                Path("datasets") / "Pertubation_original",
                Path("datasets") / "perturbation_original",
            ]
        )
        perturbed_dir = _resolve_existing_dir(
            [
                perturbed_dir,
                Path("datasets") / "pertubation_pertubated",
                Path("datasets") / "perturbation_perturbed",
            ]
        )
        label_path = labels if labels else clean_dir / "labels.csv"
        pairs = _load_perturbation_pairs(clean_dir, perturbed_dir, label_path)
        dataset_name = f"clean={clean_dir}, perturbed={perturbed_dir}"

    if not pairs:
        raise RuntimeError("No valid pairs found for evaluation.")

    if isinstance(max_samples, int) and max_samples > 0:
        pairs = pairs[:max_samples]

    clip_labels = [
        p.label for p in pairs if p.label
    ] + [
        p.target_label for p in pairs if p.target_label
    ] + [
        "cat",
        "dog",
        "apple",
        "banana",
        "person",
        "car",
        "tree",
        "building",
        "food",
        "street",
        "indoor scene",
        "outdoor scene",
        "stop sign",
        "warning",
        "safe",
        "yes",
    ]

    model_factories = {
        "clip_vit_b32": lambda: ClipZeroShotClassifier(labels=clip_labels, device=device_name),
        "dinov2_base_imagenet1k": lambda: DinoV2Classifier(device=device_name),
        "resnet50_imagenet": lambda: TorchVisionClassifier("resnet50", device=device_name),
        "vit_b_16_imagenet": lambda: TorchVisionClassifier("vit_b_16", device=device_name),
    }

    selected_models = list(model_factories.keys())
    if model_names:
        requested = [m.strip() for m in model_names if m and m.strip()]
        invalid = sorted(set(requested) - set(model_factories.keys()))
        if invalid:
            raise ValueError(
                f"Unknown model names: {invalid}. Supported: {sorted(model_factories.keys())}"
            )
        selected_models = requested

    results: Dict[str, Dict] = {}
    skipped: Dict[str, str] = {}

    for model_name in selected_models:
        factory = model_factories[model_name]
        try:
            model = factory()
            results[model_name] = _evaluate_model(model_name, model, pairs)
        except Exception as exc:
            skipped[model_name] = str(exc)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "attack_type": mode,
        "dataset": dataset_name,
        "num_samples": len(pairs),
        "device": device_name,
        "selected_models": selected_models,
        "results": results,
        "skipped": skipped,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    if output_md:
        _write_markdown_report(payload, output_md)

    return payload


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Unified local-model robustness evaluator")
    parser.add_argument("--mode", choices=["typographic", "perturbation"], default="perturbation")
    parser.add_argument("--clean-dir", type=Path, default=Path("datasets") / "Pertubation_original")
    parser.add_argument("--perturbed-dir", type=Path, default=Path("datasets") / "pertubation_pertubated")
    parser.add_argument("--labels", type=Path, default=None)
    parser.add_argument("--mapping-csv", type=Path, default=Path("datasets") / "typographic_mapping.csv")
    parser.add_argument("--output", type=Path, default=Path("results") / "reports" / "local_model_robustness.json")
    parser.add_argument("--output-md", type=Path, default=Path("results") / "reports" / "local_model_robustness.md")
    parser.add_argument("--device", type=str, default=None, help="cpu or cuda; default auto")
    parser.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Optional model keys to run (clip_vit_b32, dinov2_base_imagenet1k, resnet50_imagenet, vit_b_16_imagenet)",
    )
    parser.add_argument("--max-samples", type=int, default=None, help="Optional cap on number of image pairs")
    args = parser.parse_args(argv)

    payload = run_local_robustness(
        mode=args.mode,
        clean_dir=args.clean_dir,
        perturbed_dir=args.perturbed_dir,
        labels=args.labels,
        mapping_csv=args.mapping_csv,
        output=args.output,
        output_md=args.output_md,
        device=args.device,
        model_names=args.models,
        max_samples=args.max_samples,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
