"""
Local robustness evaluation on clean vs perturbed datasets.

Evaluates multiple local models (no API calls) by:
1) extracting embeddings for all images,
2) building class centroids from clean images,
3) classifying clean and perturbed images by nearest centroid,
4) reporting accuracy drop.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from tqdm import tqdm


@dataclass
class DatasetEntry:
    image_file: str
    label: str


def load_labels(labels_csv: Path) -> List[DatasetEntry]:
    with labels_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [DatasetEntry(image_file=r["image_file"], label=r["label"]) for r in rows]


def cosine_nearest_centroid(
    embeddings: torch.Tensor,
    centroids: torch.Tensor,
    class_names: List[str],
) -> List[str]:
    sims = embeddings @ centroids.T
    indices = sims.argmax(dim=1).tolist()
    return [class_names[i] for i in indices]


def accuracy(preds: List[str], labels: List[str]) -> float:
    if not labels:
        return 0.0
    correct = sum(int(p == y) for p, y in zip(preds, labels))
    return correct / len(labels)


class TorchvisionBackbone:
    def __init__(self, model_name: str, device: torch.device):
        from torchvision import models

        self.model_name = model_name
        self.device = device

        if model_name == "resnet50":
            weights = models.ResNet50_Weights.IMAGENET1K_V2
            model = models.resnet50(weights=weights)
            model.fc = nn.Identity()
            self.transform = weights.transforms()
        elif model_name == "vit_b_16":
            weights = models.ViT_B_16_Weights.IMAGENET1K_V1
            model = models.vit_b_16(weights=weights)
            model.heads = nn.Identity()
            self.transform = weights.transforms()
        else:
            raise ValueError(f"Unsupported torchvision model: {model_name}")

        self.model = model.to(device)
        self.model.eval()

    def embed_image(self, image: Image.Image) -> torch.Tensor:
        x = self.transform(image.convert("RGB")).unsqueeze(0).to(self.device)
        with torch.no_grad():
            feat = self.model(x)
            if feat.ndim > 2:
                feat = torch.flatten(feat, start_dim=1)
            feat = F.normalize(feat, dim=1)
        return feat.squeeze(0).cpu()


class ClipVisionBackbone:
    def __init__(self, device: torch.device):
        from transformers import CLIPImageProcessor, CLIPVisionModel

        self.device = device
        self.processor = CLIPImageProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model = CLIPVisionModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        self.model.eval()

    def embed_image(self, image: Image.Image) -> torch.Tensor:
        inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.model(**inputs)
            feat = out.pooler_output
            feat = F.normalize(feat, dim=1)
        return feat.squeeze(0).cpu()


class DinoV2Backbone:
    def __init__(self, device: torch.device):
        from transformers import AutoImageProcessor, Dinov2Model

        self.device = device
        self.processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
        self.model = Dinov2Model.from_pretrained("facebook/dinov2-base").to(device)
        self.model.eval()

    def embed_image(self, image: Image.Image) -> torch.Tensor:
        inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.model(**inputs)
            feat = out.pooler_output if out.pooler_output is not None else out.last_hidden_state[:, 0, :]
            feat = F.normalize(feat, dim=1)
        return feat.squeeze(0).cpu()


def extract_embeddings(
    entries: List[DatasetEntry],
    image_root: Path,
    embed_fn: Callable[[Image.Image], torch.Tensor],
    desc: str,
) -> torch.Tensor:
    vectors: List[torch.Tensor] = []
    for row in tqdm(entries, desc=desc):
        img_path = image_root / row.image_file
        image = Image.open(img_path).convert("RGB")
        vectors.append(embed_fn(image))
    return torch.stack(vectors, dim=0)


def evaluate_model(
    model_name: str,
    entries: List[DatasetEntry],
    clean_root: Path,
    pert_root: Path,
    embed_fn: Callable[[Image.Image], torch.Tensor],
) -> Dict[str, float]:
    labels = [e.label for e in entries]
    class_names = sorted(set(labels))

    clean_emb = extract_embeddings(entries, clean_root, embed_fn, f"{model_name} clean")
    pert_emb = extract_embeddings(entries, pert_root, embed_fn, f"{model_name} perturbed")

    label_to_idx = {c: i for i, c in enumerate(class_names)}
    y = torch.tensor([label_to_idx[l] for l in labels], dtype=torch.long)

    centroids = []
    for i, _class_name in enumerate(class_names):
        class_vecs = clean_emb[y == i]
        centroid = F.normalize(class_vecs.mean(dim=0, keepdim=True), dim=1)
        centroids.append(centroid.squeeze(0))
    centroids_t = torch.stack(centroids, dim=0)

    clean_preds = cosine_nearest_centroid(clean_emb, centroids_t, class_names)
    pert_preds = cosine_nearest_centroid(pert_emb, centroids_t, class_names)

    clean_acc = accuracy(clean_preds, labels)
    pert_acc = accuracy(pert_preds, labels)

    return {
        "clean_accuracy": clean_acc,
        "perturbed_accuracy": pert_acc,
        "accuracy_drop_abs": clean_acc - pert_acc,
        "accuracy_drop_pct_points": (clean_acc - pert_acc) * 100.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate clean vs perturbed accuracy on local models")
    parser.add_argument("--clean-dir", type=Path, default=Path("datasets") / "Pertubation_original")
    parser.add_argument("--perturbed-dir", type=Path, default=Path("datasets") / "pertubation_pertubated")
    parser.add_argument("--labels", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("results") / "local_robustness_results.json")
    parser.add_argument("--device", type=str, default=None, help="cpu or cuda; default auto")
    args = parser.parse_args()

    device = torch.device(args.device if args.device else ("cuda" if torch.cuda.is_available() else "cpu"))
    labels_path = args.labels or (args.clean_dir / "labels.csv")

    entries = load_labels(labels_path)
    clean_root = args.clean_dir
    pert_root = args.perturbed_dir

    model_builders = {
        "clip_vit_b32": lambda: ClipVisionBackbone(device),
        "dinov2_base": lambda: DinoV2Backbone(device),
        "resnet50": lambda: TorchvisionBackbone("resnet50", device),
        "vit_b_16": lambda: TorchvisionBackbone("vit_b_16", device),
    }

    results: Dict[str, Dict[str, float]] = {}
    skipped: Dict[str, str] = {}

    for name, builder in model_builders.items():
        try:
            backbone = builder()
            metrics = evaluate_model(
                model_name=name,
                entries=entries,
                clean_root=clean_root,
                pert_root=pert_root,
                embed_fn=backbone.embed_image,
            )
            results[name] = metrics
        except Exception as exc:
            skipped[name] = str(exc)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "clean_dir": str(clean_root),
        "perturbed_dir": str(pert_root),
        "num_images": len(entries),
        "device": str(device),
        "results": results,
        "skipped": skipped,
    }
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
