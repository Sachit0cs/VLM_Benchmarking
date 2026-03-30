# Image Injection Attack Tests

Local test suite for image injection attack implementation and lightweight model evaluation.

## 📋 Test Organization

```
tests/image_injection/
├── conftest.py                          # Pytest configuration & fixtures
├── test_attack_basic.py                 # ✅ Unit tests (no models)
├── test_attack_generation.py            # ✅ Test data generation
├── test_lightweight_models.py           # ⚠️ Local model testing (CLIP, MobileViT)
├── test_blip2_injection.py              # ⚠️ Local BLIP-2 testing  
├── test_image_injection.py              # Reference implementation
└── README.md                             # This file
```

## 🎯 Test Categories

### 1. **Unit Tests** (`test_attack_basic.py`)
✅ **Run locally - NO model downloads needed**

Tests core PromptInjectionAttack functionality:
- Attack instantiation
- Image embedding (white-on-white, low-opacity)
- HOUYI structure validation
- Separator types (syntax, semantic, visual_spacing)
- Position variants

**Run with:**
```bash
pytest tests/image_injection/test_attack_basic.py -v
```

**No external dependencies** - uses PIL, numpy only.

---

### 2. **Test Data Generation** (`test_attack_generation.py`)
✅ **Run locally - Creates test images & variants**

Local utilities to generate:
- 5 synthetic test images (face, animal, landscape)
- 30+ attacked variants (different techniques/separators)
- Evaluation metrics computation

**Use for:**
- Creating reproducible test datasets locally
- Generating input for cloud notebooks
- Offline evaluation without models

**Run with:**
```bash
python -m pytest tests/image_injection/test_attack_generation.py -v
# OR directly as script:
python tests/image_injection/test_attack_generation.py
```

**Creates:**
- `test_images/` - Original synthetic images
- `attacked_images/` - Injected variants

---

### 3. **Lightweight Model Tests** (`test_lightweight_models.py`)
⚠️ **Local testing - Small models (20-350MB)**

Tests on models that can run locally:
- **CLIP** (350MB) - Vision-language model
- **MobileViT** (20MB) - Tiny image classifier
- Other distilled/edge models

**When to use:**
- Quick local validation before cloud testing
- Small-scale attack effectiveness checking
- Development/debugging

**Notes:**
- Downloads models (150-400MB)
- Requires transformers, torch, PIL
- Single machine evaluation

---

### 4. **BLIP-2 Model Tests** (`test_blip2_injection.py`)
⚠️ **Local testing - BLIP-2 caption generation**

Real model inference with BLIP-2 (2.7B parameters):
- Tests on actual vision-language model
- Runs locally with GPU (CUDA)
- Generates image captions for clean/attacked variants

**When to use:**
- Local development with decent GPU
- Validation before cloud experiments
- Understanding model behavior locally

**Notes:**
- Requires 8GB+ VRAM (GPU recommended)
- ~2.7B parameter model download
- Slower than cloud GPU but good for debugging

---

### 5. **Reference Implementation** (`test_image_injection.py`)
📖 **Archive - Original implementation**

First version of image injection tests - kept for reference.
Combine features of basic + generation tests.

---

## 🔄 Workflow: Local → Cloud

### For Lightweight (Local) Testing:
```
1. Run unit tests (basic functionality)
   pytest tests/image_injection/test_attack_basic.py

2. Generate test data (locally)
   python tests/image_injection/test_attack_generation.py
   
3. Test on lightweight models (optional)
   python tests/image_injection/test_lightweight_models.py
```

### For Heavy Model Testing (Cloud):
```
1. Prepare functions locally (test_attack_generation.py)

2. Copy to Colab:
   - Open cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb
   - Clone repository in first cell
   
3. Run on cloud:
   - Import local functions from GitHub
   - Test on CLIP, MobileViT, BLIP-2, LLaVA
   - Download results
```

---

## 📊 Test Data Flow

```
test_attack_basic.py
  └─ Unit tests (no data)

test_attack_generation.py (LOCAL)
  ├─ create_test_images() → test_images/
  ├─ generate_attacked_images() → attacked_images/
  └─ compute_metrics() → metric evaluation

test_lightweight_models.py (LOCAL)
  ├─ Load CLIP/MobileViT
  ├─ Run on test images
  └─ Compute metrics

cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb (CLOUD)
  ├─ Import functions from test_attack_generation.py
  ├─ Generate test data (in Colab)
  ├─ Test on CLIP, MobileViT, BLIP-2, LLaVA
  └─ Download results
```

---

## 🚀 Quick Start

### Test Locally (No Models):
```bash
cd /path/to/SemesterProject
pytest tests/image_injection/test_attack_basic.py -v
```

### Generate Test Data:
```bash
python tests/image_injection/test_attack_generation.py
```

### Test on Local Lightweight Models:
```bash
python tests/image_injection/test_lightweight_models.py
```

### Heavy Model Testing (Cloud):
1. Go to [Google Colab](https://colab.research.google.com/)
2. Upload `cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb`
3. Run cells sequentially

---

## 📦 Dependencies

### For Local Tests:
```
PIL (Pillow)
numpy
scipy
pytest (for unit tests)
```

### For Lightweight Model Tests:
```
+ transformers
+ torch
+ torchvision
```

### For Cloud Tests (Colab):
```
+ CLIP
+ torchvision
+ sentence-transformers (optional)
```

---

## 🔍 Test Metrics

All tests compute:
- **ASR** (Attack Success Rate) - Did output change?
- **ODS** (Output Deviation Score) - How much did it change?
- **SBR** (Safety Bypass Rate) - Did it bypass safety checks?

Expected ranges: [0, 1] for all metrics

---

## 💡 Best Practices

1. **Always run unit tests first** - `test_attack_basic.py`
2. **Generate test data locally** - `test_attack_generation.py`
3. **Use Colab for heavy models** - GPU access, no local VRAM needed
4. **Keep test images small** (5-10) for cost efficiency
5. **Download results** from cloud notebooks regularly

---

## 📝 Adding New Tests

To add a new model test:

1. **Local lightweight**: Add function to `test_lightweight_models.py`
2. **Cloud heavy**: Add cell to `cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb`
3. **Update metrics**: Ensure ASR/ODS/SBR computed in Step 5
4. **Document**: Add model info above function/cell

See CLIP, MobileViT, BLIP-2 examples in respective files.

---

## ✅ Test Status

- ✅ `test_attack_basic.py` - All tests passing
- ✅ `test_attack_generation.py` - Image generation working
- ⚠️ `test_lightweight_models.py` - Requires model downloads
- ⚠️ `test_blip2_injection.py` - Requires GPU
- 📊 Cloud notebooks - Tested on Colab GPU

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `export PYTHONPATH=/path/to/SemesterProject:$PYTHONPATH` |
| Model download fails | Try running in Colab (better network) |
| Out of memory | Use cloud notebook with GPU |
| Test data not found | Run `test_attack_generation.py` first |
| Metrics all zeros | Check if model outputs are being generated |
