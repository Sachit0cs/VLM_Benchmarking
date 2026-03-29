# VLM-ARB: Adversarial Robustness Benchmarking Framework for Vision-Language Models

## Overview

**VLM-ARB** is a unified benchmarking framework for evaluating the adversarial robustness of Vision-Language Models (VLMs). The goal is to systematically stress-test VLMs with adversarial attacks, measure their vulnerability, compare robustness across models, and generate research-quality findings.

This is simultaneously:
- A **semester project** (working implementation + written report)
- A **research paper candidate** (targeting arXiv, CVPR workshops, EMNLP, or similar venues)

## Key Features

### 5 Attack Types
1. **Typographic Attack** — Overlay misleading text labels on images
2. **Adversarial Perturbation** — Pixel-level noise (FGSM/PGD)
3. **Prompt Injection** — Hidden text instructions in images (white-on-white, steganography)
4. **Adversarial Patch** — Universal stickers that fool models
5. **Cross-Modal Conflict** ⭐ — Novel: measure vision vs language dominance

### 4 VLM Targets
- **GPT-4o Vision** (OpenAI API)
- **Claude 3** (Anthropic API)
- **BLIP-2** (HuggingFace, lightweight open-source)
- **LLaVA-7B** (HuggingFace, open-source)

### 5 Evaluation Metrics
- **ASR** (Attack Success Rate) — % attacks that changed output
- **ODS** (Output Deviation Score) — Semantic distance of changes
- **CMCS** (Cross-Modal Conflict Score) ⭐ — Novel metric for modality dominance
- **SBR** (Safety Bypass Rate) — % safety filters bypassed
- **CRS** (Composite Robustness Score) — Single number per model

## Novel Research Contributions

1. **Cross-Modal Conflict Score (CMCS)** — First formally defined metric for measuring modality dominance in VLMs
2. **Transferability Analysis** — First systematic study of adversarial example transfer across VLM families
3. **Modality Dominance Profiling** — Maps which modality (vision vs language) each VLM prioritizes
4. **Robustness vs Capability Tradeoff** — Analyzes if more capable models are more or less robust

## Project Structure

```
vlm-arb/
├── attacks/                      # 5 attack implementations
│   ├── base.py                   # BaseAttack abstract class
│   ├── typographic.py
│   ├── perturbation.py
│   ├── prompt_injection.py
│   ├── patch.py
│   └── crossmodal.py
├── models/                       # 4 VLM wrappers
│   ├── base.py                   # BaseModel abstract class
│   ├── gpt4v.py
│   ├── claude.py
│   ├── blip2.py
│   └── llava.py
├── evaluator/                    # Evaluation metrics & scoring
│   ├── metrics.py                # ASR, ODS, CMCS, SBR functions
│   ├── scorer.py                 # Result aggregation
│   └── comparator.py             # Cross-model analysis
├── datasets/                     # Dataset loading
│   ├── loader.py                 # VQAv2, TextVQA loaders
│   └── sampler.py                # Balanced sampling
├── report/                       # Report generation
│   ├── generator.py              # PDF/HTML report builder
│   ├── visualizer.py             # Charts, heatmaps
│   └── templates/                # HTML templates
├── ui/                           # Optional dashboard
│   └── app.py                    # Gradio/Streamlit UI
├── results/
│   ├── raw/                      # JSON results (raw output)
│   └── reports/                  # Generated reports
├── tests/                        # Test suite (TBD)
├── notebooks/                    # Jupyter notebooks for analysis
├── docs/                         # Documentation
├── benchmark.py                  # Main entry point
├── config.yaml                   # Configuration (models, attacks, settings)
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for API keys
├── .gitignore                    # Git ignore list
└── README.md                     # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Clone repo and navigate to project
cd vlm-arb

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy .env template
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# HUGGINGFACE_TOKEN=hf_...
nano .env
```

### 3. Configure Benchmark Settings

Edit `config.yaml` to enable/disable models and attacks:

```yaml
models:
  - name: gpt4v
    enabled: true
  - name: claude
    enabled: true
  - name: blip2
    enabled: false  # Requires GPU

attacks:
  typographic:
    enabled: true
  crossmodal:
    enabled: true
  # ... other attacks
```

### 4. Run Benchmark

```bash
# Run full benchmark
python benchmark.py

# Run with custom config
python benchmark.py --config custom.yaml

# Generate report only (skip benchmark)
python benchmark.py --skip-benchmark --generate-report
```

Results are saved to `results/` directory as JSON + PDF/HTML report.

### 5. Interactive Dashboard (Optional)

```bash
# Launch Streamlit UI
streamlit run ui/app.py
```

## Configuration Reference

### config.yaml

```yaml
models:
  - name: gpt4v
    enabled: true
    config:
      max_tokens: 1024
      temperature: 0.7

attacks:
  typographic:
    enabled: true
    config:
      font_size: 40
      opacity: 1.0

dataset:
  name: vqav2
  sample_size: 100

evaluation:
  metrics:
    - "asr"
    - "ods"
    - "cmcs"
  weights:
    asr: 0.25
    ods: 0.25
    cmcs: 0.25
```

See `config.yaml` for complete options.

## Dependencies

- **Python 3.10+**
- **PyTorch 2.0+** (for vision models)
- **HuggingFace Transformers** (BLIP-2, LLaVA)
- **OpenAI API** (GPT-4o)
- **Anthropic API** (Claude)
- **torchattacks** (FGSM/PGD perturbations)
- **Pillow** (image manipulation)
- **sentence-transformers** (semantic similarity)
- **matplotlib, seaborn** (visualization)

See `requirements.txt` for full list.

## Coding Conventions

1. **Every attack inherits from `BaseAttack`** with `apply(image, prompt) → Image` method
2. **Every model inherits from `BaseModel`** with `query(image, prompt) → str` method
3. **All results saved as JSON** to `results/raw/{timestamp}.json`
4. **Config always loaded** from `config.yaml` (never hardcoded)
5. **API keys from `.env`** via `python-dotenv` (never committed)
6. **Type hints on all functions**
7. **Docstrings on all public methods**

## References

- [VQAv2 Dataset](https://visualqa.org/)
- [TextVQA Dataset](https://github.com/facebookresearch/TextVQA)
- [BLIP-2 Paper](https://arxiv.org/abs/2301.12597)
- [LLaVA Paper](https://arxiv.org/abs/2304.08485)
- [torchattacks Library](https://github.com/Harry24k/adversarial-attacks-pytorch)
- [Adversarial Examples Explained](https://openai.com/research/adversarial-examples-not-bugs/)

## License

[Specify your license here — e.g., MIT, Apache 2.0]

## Contact

[Team members and contact info]

---

**Ready to benchmark?** Start with `python benchmark.py` after configuration!
