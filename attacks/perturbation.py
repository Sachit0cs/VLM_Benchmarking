"""
Adversarial Perturbation Attack: Add pixel-level noise using FGSM/PGD.

This attack adds imperceptible noise to images using gradient-based methods
(FGSM or PGD) to fool Vision-Language Models while remaining visually similar.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

import argparse
import csv
from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F
from PIL import Image as PILImage
from PIL.Image import Image
from torchvision import models
from tqdm import tqdm

from .base import BaseAttack


class PerturbationAttack(BaseAttack):
    """
    Adversarial perturbation attack using FGSM or PGD methods.
    
    Parameters:
    -----------
    method : str
        Either "fgsm" (fast, one-step) or "pgd" (iterative, stronger)
    epsilon : float
        Maximum perturbation magnitude (typically 8/255 ≈ 0.031)
    alpha : float, optional
        Step size for PGD (default: 2/255 ≈ 0.008)
    iterations : int, optional
        Number of PGD iterations (default: 7)
    """
    
    def __init__(
        self,
        method: str = "fgsm",
        epsilon: float = 8 / 255,
        alpha: float = 2 / 255,
        iterations: int = 7,
        device: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the perturbation attack."""
        super().__init__(name="Perturbation", **kwargs)
        if method not in ["fgsm", "pgd"]:
            raise ValueError(f"method must be 'fgsm' or 'pgd', got {method}")
        self.method = method
        self.epsilon = epsilon
        self.alpha = alpha
        self.iterations = iterations
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self._mean = torch.tensor([0.485, 0.456, 0.406], device=self.device).view(1, 3, 1, 1)
        self._std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1, 3, 1, 1)
        self.model = self._load_surrogate_model()

    def _load_surrogate_model(self) -> torch.nn.Module:
        """Load a fixed surrogate classifier used to compute FGSM/PGD gradients."""
        try:
            weights = models.ResNet18_Weights.IMAGENET1K_V1
            model = models.resnet18(weights=weights)
        except Exception:
            # Fallback if pretrained weights are unavailable in the runtime.
            model = models.resnet18(weights=None)
        model = model.to(self.device)
        model.eval()
        for param in model.parameters():
            param.requires_grad_(False)
        return model

    def _to_tensor(self, image: Image) -> torch.Tensor:
        """Convert PIL Image to BCHW float tensor in [0, 1]."""
        image = image.convert("RGB")
        x = torch.from_numpy(torch.ByteTensor(torch.ByteStorage.from_buffer(image.tobytes())).numpy())
        x = x.view(image.height, image.width, 3).permute(2, 0, 1).float() / 255.0
        return x.unsqueeze(0).to(self.device)

    def _to_pil(self, x: torch.Tensor) -> Image:
        """Convert BCHW float tensor in [0, 1] back to PIL Image."""
        x = x.detach().clamp(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy()
        x = (x * 255.0).round().astype("uint8")
        return PILImage.fromarray(x)

    def _normalize(self, x: torch.Tensor) -> torch.Tensor:
        return (x - self._mean) / self._std

    def _untargeted_loss(self, x: torch.Tensor) -> torch.Tensor:
        """Maximize classification loss for the model's own prediction."""
        with torch.no_grad():
            y_pred = self.model(self._normalize(x)).argmax(dim=1)
        logits = self.model(self._normalize(x))
        return F.cross_entropy(logits, y_pred)

    def _fgsm(self, x: torch.Tensor) -> torch.Tensor:
        x_adv = x.clone().detach().requires_grad_(True)
        loss = self._untargeted_loss(x_adv)
        loss.backward()
        grad_sign = x_adv.grad.sign()
        x_adv = x_adv + self.epsilon * grad_sign
        return x_adv.detach().clamp(0, 1)

    def _pgd(self, x: torch.Tensor) -> torch.Tensor:
        x_orig = x.clone().detach()
        x_adv = x.clone().detach()
        for _ in range(self.iterations):
            x_adv.requires_grad_(True)
            loss = self._untargeted_loss(x_adv)
            loss.backward()
            grad_sign = x_adv.grad.sign()
            x_adv = x_adv.detach() + self.alpha * grad_sign
            delta = torch.clamp(x_adv - x_orig, min=-self.epsilon, max=self.epsilon)
            x_adv = torch.clamp(x_orig + delta, min=0.0, max=1.0)
        return x_adv.detach()
    
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply adversarial perturbation to the image.
        
        Args:
            image: PIL Image to attack
            prompt: Optional context prompt (used to generate attack target)
        
        Returns:
            Modified image with adversarial noise added
        
        Uses a surrogate image classifier to compute gradients and generate
        transferable perturbations for VLM benchmarking.
        """
        x = self._to_tensor(image)
        if self.method == "fgsm":
            x_adv = self._fgsm(x)
        else:
            x_adv = self._pgd(x)
        return self._to_pil(x_adv)


def run_batch_perturbation(
    input_dir: Path,
    output_dir: Path,
    labels_file: Path,
    method: str,
    epsilon: float,
    alpha: float,
    iterations: int,
    device: Optional[str] = None,
) -> None:
    """Generate perturbed images for every entry in labels_file."""
    output_images = output_dir / "images"
    output_images.mkdir(parents=True, exist_ok=True)

    attack = PerturbationAttack(
        method=method,
        epsilon=epsilon,
        alpha=alpha,
        iterations=iterations,
        device=device,
    )

    with labels_file.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in tqdm(rows, desc=f"Applying {method.upper()} perturbations"):
        rel_image = row["image_file"].replace("\\", "/")
        src = input_dir / rel_image
        dst = output_dir / rel_image
        dst.parent.mkdir(parents=True, exist_ok=True)

        image = PILImage.open(src).convert("RGB")
        perturbed = attack.apply(image)
        perturbed.save(dst)

    # Keep the same labels schema and paths for downstream evaluation.
    out_labels = output_dir / "labels.csv"
    with out_labels.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch FGSM/PGD perturbation generator")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("datasets") / "Pertubation_original",
        help="Input dataset directory containing labels.csv and images/",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("datasets") / "pertubation_pertubated",
        help="Output dataset directory for perturbed images",
    )
    parser.add_argument(
        "--labels-file",
        type=Path,
        default=None,
        help="Optional labels file path; defaults to <input-dir>/labels.csv",
    )
    parser.add_argument("--method", choices=["fgsm", "pgd"], default="fgsm")
    parser.add_argument("--epsilon", type=float, default=8 / 255)
    parser.add_argument("--alpha", type=float, default=2 / 255)
    parser.add_argument("--iterations", type=int, default=7)
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to run on (e.g., cpu, cuda). Default: auto",
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()
    labels_file = args.labels_file or (args.input_dir / "labels.csv")

    run_batch_perturbation(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        labels_file=labels_file,
        method=args.method,
        epsilon=args.epsilon,
        alpha=args.alpha,
        iterations=args.iterations,
        device=args.device,
    )


if __name__ == "__main__":
    main()
