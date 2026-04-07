# Local Model Robustness Report

- attack_type: patch
- dataset: clean=datasets\patch_original, perturbed=datasets\patch_poisoned
- num_samples: 1
- device: cpu

## Summary

| Model | Pairs | Change Rate | Target Hit Rate | Clean Acc | Perturbed Acc | Drop (pp) |
|---|---:|---:|---:|---:|---:|---:|
| resnet50_imagenet | 1 | 0.0% | N/A | N/A | N/A | N/A |