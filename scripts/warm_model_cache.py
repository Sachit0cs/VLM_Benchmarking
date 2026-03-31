"""
Warm local model cache for perturbation robustness evaluation.

Usage examples:
  python scripts/warm_model_cache.py
  python scripts/warm_model_cache.py --models clip_vit_b32 dinov2_base_imagenet1k
  python scripts/warm_model_cache.py --cache-dir .model_cache
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable


def configure_cache(cache_dir: Path) -> tuple[Path, Path]:
    cache_root = cache_dir.resolve()
    hf_home = cache_root / "huggingface"
    torch_home = cache_root / "torch"

    hf_home.mkdir(parents=True, exist_ok=True)
    torch_home.mkdir(parents=True, exist_ok=True)

    os.environ["HF_HOME"] = str(hf_home)
    os.environ.setdefault("TRANSFORMERS_CACHE", str(hf_home / "transformers"))
    os.environ["TORCH_HOME"] = str(torch_home)

    return hf_home, torch_home


def warm_clip(hf_cache: Path) -> None:
    from transformers import CLIPModel, CLIPProcessor

    model_id = "openai/clip-vit-base-patch32"
    print(f"Warming {model_id}...")
    CLIPProcessor.from_pretrained(model_id, cache_dir=str(hf_cache))
    CLIPModel.from_pretrained(model_id, cache_dir=str(hf_cache))


def warm_dino(hf_cache: Path) -> None:
    from transformers import AutoImageProcessor, AutoModelForImageClassification

    model_id = "facebook/dinov2-base-imagenet1k-1-layer"
    print(f"Warming {model_id}...")
    AutoImageProcessor.from_pretrained(model_id, cache_dir=str(hf_cache))
    AutoModelForImageClassification.from_pretrained(model_id, cache_dir=str(hf_cache))


def warm_resnet50() -> None:
    from torchvision.models import ResNet50_Weights

    print("Warming torchvision ResNet50 weights...")
    ResNet50_Weights.DEFAULT.get_state_dict(progress=True)


def warm_vit_b16() -> None:
    from torchvision.models import ViT_B_16_Weights

    print("Warming torchvision ViT-B/16 weights...")
    ViT_B_16_Weights.DEFAULT.get_state_dict(progress=True)


def run_selected(models: Iterable[str], hf_cache: Path) -> None:
    for name in models:
        if name == "clip_vit_b32":
            warm_clip(hf_cache)
        elif name == "dinov2_base_imagenet1k":
            warm_dino(hf_cache)
        elif name == "resnet50_imagenet":
            warm_resnet50()
        elif name == "vit_b_16_imagenet":
            warm_vit_b16()
        else:
            raise ValueError(f"Unsupported model key: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-download model weights into a local project cache")
    parser.add_argument("--cache-dir", type=Path, default=Path(".model_cache"))
    parser.add_argument(
        "--models",
        nargs="*",
        default=[
            "clip_vit_b32",
            "dinov2_base_imagenet1k",
            "resnet50_imagenet",
            "vit_b_16_imagenet",
        ],
        help="Model keys to warm",
    )
    args = parser.parse_args()

    hf_cache, torch_cache = configure_cache(args.cache_dir)
    print(f"Local model cache root: {args.cache_dir.resolve()}")
    print(f"HF cache: {hf_cache}")
    print(f"Torch cache: {torch_cache}")

    run_selected(args.models, hf_cache)
    print("Model cache warmup complete.")


if __name__ == "__main__":
    main()
