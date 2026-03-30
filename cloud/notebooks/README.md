# Cloud Testing - Image Injection Attacks

This directory contains notebooks and configurations for **heavy computational testing** on cloud platforms (Google Colab, AWS, etc.).

## 📋 Contents

### Notebooks

- **`ImageInjection_MultiModel_Cloud.ipynb`** - Comprehensive multi-model evaluation
  - Tests on 4 vulnerable models: CLIP, MobileViT, BLIP-2, LLaVA
  - Computes ASR, ODS, SBR metrics across all models
  - Analyzes attack transferability (which models are vulnerable)
  - Generates comparative visualizations
  - **Only run in Colab** - requires GPU/TPU and model downloads

## 🚀 Quick Start on Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Open `ImageInjection_MultiModel_Cloud.ipynb`
3. Run cells sequentially:
   - **Step 1**: Clone repository + install dependencies
   - **Step 2**: Generate synthetic test images (local functions)
   - **Step 3**: Create attacked image variants (local functions)
   - **Step 4**: Test on CLIP, MobileViT, BLIP-2, LLaVA
   - **Step 5**: Compute metrics for all models
   - **Step 6**: Visualize vulnerability rankings
   - **Step 7**: Download results as JSON + PNG

## 📊 Workflow

```
LOCAL (Your Machine)                    CLOUD (Colab)
├── Generate test images            →   ├── Load functions from local utils
├── Create attack variants          →   ├── Test on heavy models
└── Define attacks                  →   ├── Compute metrics
                                    →   └── Download results
```

## 🔗 Data Flow

1. **Local test generation** → Creates test data in `tests/image_injection/`
2. **Cloud notebook** → Imports functions, runs heavy model testing
3. **Results download** → JSON metrics + visualizations back to local

## 💡 Why This Structure?

- ✅ **Local**: Lightweight code (PIL, numpy, scipy) for test generation
- ✅ **Cloud**: Heavy code (transformers, CLIP, BLIP) for model testing
- ✅ **Reproducible**: Code is local, results are downloadable
- ✅ **Scalable**: No GPU needed locally, unlimited compute on cloud
- ✅ **Cost-efficient**: Free Colab GPUs for expensive inference

## 🔧 Extending the Notebook

To add a new model test:

1. Create markdown cell with model info
2. Add code cell with model loading and inference
3. Update metrics computation step (Step 5)
4. Re-run visualization step

See existing cells (CLIP, MobileViT, BLIP-2, LLaVA) for examples.

## 📝 Tips

- **Keep test data small** (5-10 images) to stay within API call budget
- **Use low precision** (float16) for VRAM-constrained environments
- **Download results regularly** to avoid losing outputs
- **Check metric ranges**: ASR/ODS/SBR should be in [0, 1]
