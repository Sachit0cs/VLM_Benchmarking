# VLM-ARB System Architecture

## High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VLM-ARB BENCHMARKING FRAMEWORK                  │
└─────────────────────────────────────────────────────────────────────────┘

                              INPUT LAYER
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  Original Images (VQAv2, TextVQA)  →  Synthetic Test Images (256×256)   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          ATTACK GENERATION LAYER
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────┐       │
│  │ Typographic  │  │ Perturbation│  │   Prompt     │  │ Patches │ ...  │
│  │  (Overlay)   │  │  (Pixel)    │  │  Injection   │  │ (USB)   │       │
│  └──────────────┘  └─────────────┘  └──────────────┘  └─────────┘       │
│         │                │                 │                │             │
│    Text overlays    FGSM/PGD noise    White-on-white   Universal        │
│    3 visibility     gradient attacks    Steganography    adversarial     │
│                                         HOUYI-based      stickers        │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                         ↓ (Generate 24+ variants)
                      MODEL INFERENCE LAYER
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   CLIP       │  │  MobileViT   │  │   BLIP-2     │  │   LLaVA      │ │
│  │  (350MB)     │  │   (20MB)     │  │  (2.7B opt)  │  │  (7B)        │ │
│  │              │  │              │  │              │  │              │ │
│  │ OpenAI API   │  │ HF pretrained│  │ HF pretrained│  │ HF pretrained│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│         +                  +                 +                 +         │
│  ┌──────────────┐  ┌──────────────┐                                      │
│  │   GPT-4V     │  │   Claude 3   │  (Roadmap - not in mid-eval)        │
│  │ (OpenAI API) │  │(Anthropic API)│                                     │
│  └──────────────┘  └──────────────┘                                      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                Multiple inferences per image × 24 variants
                         ↓
                    EVALUATION LAYER
┌──────────────────────────────────────────────────────────────────────────┐
│                         METRICS COMPUTATION                              │
│                                                                           │
│  Clean Output + Attacked Output → Metrics                               │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │     ASR      │  │     ODS      │  │     SBR      │                   │
│  │   (Success)  │  │ (Deviation)  │  │   (Safety)   │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                           +                                              │
│              ┌────────────────────────────┐                              │
│              │   ⭐ CMCS (Novel Metric)   │                              │
│              │  Cross-Modal Conflict Score│                              │
│              │  (Modality Dominance)      │                              │
│              └────────────────────────────┘                              │
│                                                                           │
│  Scorer: Aggregates metrics across all attacks × all models             │
│  Comparator: Cross-model analysis & finding generation                  │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
                       RESULTS AGGREGATION
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Results Dictionary                                              │   │
│  │ {                                                               │   │
│  │   "summary": {                                                  │   │
│  │     "total_models": 4,                                          │   │
│  │     "models": ["CLIP", "MobileViT", "BLIP-2", "LLaVA"]         │   │
│  │   },                                                            │   │
│  │   "models": {                                                   │   │
│  │     "clip": {"asr": 0.42, "ods": 0.38, "sbr": 0.25, ...},    │   │
│  │     "blip2": {"asr": 0.68, "ods": 0.58, "sbr": 0.45, ...},  │   │
│  │     ...                                                         │   │
│  │   },                                                            │   │
│  │   "transferability": { ... cross-model transfer rates ... },   │   │
│  │   "vulnerability_ranking": [ ... ]                             │   │
│  │ }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
                        REPORTING LAYER
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │  PDF Report  │  │   JSON Data  │  │  PNG Charts  │                   │
│  │              │  │              │  │              │                   │
│  │ - Title page │  │ Structured   │  │ Bar charts   │                   │
│  │ - Executive  │  │   results    │  │ (ASR, ODS,   │                   │
│  │   summary    │  │ Metrics for  │  │  SBR, CMCS)  │                   │
│  │ - Methodology│  │ post-process │  │ Heatmaps     │                   │
│  │ - Tables     │  │ analysis &   │  │ (Transfer)   │                   │
│  │ - Visuals    │  │ visualization│  │              │                   │
│  │ - Findings   │  │              │  │              │                   │
│  │ - Conclusions│  │              │  │              │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
                        DELIVERABLES
                  (Download from Cloud or Local)
```

---

## Data Flow Diagram

```
Input Image
    ↓
    ├─→ [Typographic Attack] ──→ Text Overlay (Visible/Invisible)
    │       ↓
    │       └─→ Attacked Image #1
    │
    ├─→ [Perturbation Attack] ──→ Pixel Noise (FGSM/PGD)
    │       ↓
    │       └─→ Attacked Image #2
    │
    ├─→ [Prompt Injection] ──→ White-on-white Text / Steganography
    │       ↓
    │       └─→ Attacked Images #3-4
    │
    └─→ [Patch Attack] ──→ Universal Adversarial Patches
            ↓
            └─→ Attacked Image #5

                    ↓ (Repeat for all 4 images + 3 techniques = 24 variants)
                    
        [Clean Image] + [Attacked Image] pair
                    ↓
            [CLIP] → Output A
            [MobileViT] → Output B
            [BLIP-2] → Output C
            [LLaVA] → Output D
                    ↓
        Compute Metrics:
        - ASR: % where clean ≠ attacked
        - ODS: Semantic similarity distance
        - SBR: Safety rule violations
        - CMCS: Modality conflicts
                    ↓
        Aggregate across all attacks
                    ↓
        Generate Results + Report
```

---

## Module Dependency Graph

```
┌────────────────────────────────────────────────────────────┐
│                  BENCHMARK.PY (Orchestrator)              │
└────────────────────────────────────────────────────────────┘
       ↓         ↓          ↓          ↓         ↓
┌─────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌────────┐
│ DATASETS│ │ATTACKS │ │  MODELS  │ │EVALUATOR│ │ REPORT │
└─────────┘ └────────┘ └──────────┘ └────────┘ └────────┘
     ↓          ↓           ↓           ↓          ↓
┌─────────────────────────────────────────────────────────┐
│                    CONFIGURATION                         │
│  - config.yaml: Model selection, attack params, paths   │
│  - requirements.txt: Dependency specification           │
└─────────────────────────────────────────────────────────┘
     ↓          ↓           ↓           ↓          ↓
┌─────────────────────────────────────────────────────────┐
│               EXTERNAL SERVICES (Optional)              │
│  - OpenAI API (GPT-4V)                                  │
│  - Anthropic API (Claude 3)                             │
│  - HuggingFace Hub (Model weights)                       │
│  - Google Colab GPU                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Class Hierarchy

### Attack Classes
```
BaseAttack (abstract)
    ├── TypographicAttack
    │   ├── visibility_level: [low, medium, high]
    │   ├── font_size: configurable
    │   └── position: [random, center, corners]
    │
    ├── PerturbationAttack
    │   ├── method: [fgsm, pgd, ...]
    │   ├── epsilon: noise magnitude
    │   └── iterations: optimization steps
    │
    ├── PromptInjectionAttack
    │   ├── technique: [white_on_white, steganography]
    │   ├── separator_type: [syntax, semantic]
    │   ├── opacity: 0.0-1.0
    │   └── use_houyi_structure: boolean
    │
    ├── PatchAttack
    │   ├── patch_size: (H, W)
    │   ├── location: configurable
    │   └── universal: boolean
    │
    └── CrossModalAttack
        ├── text_weight: importance of language
        ├── vision_weight: importance of vision
        └── conflict_type: [text_dominance, vision_dominance]
```

### Model Classes
```
BaseModel (abstract)
    ├── GPT4VisionModel
    │   └── API: OpenAI
    │
    ├── ClaudeVisionModel
    │   └── API: Anthropic
    │
    ├── BLIP2Model
    │   └── Source: HuggingFace
    │
    └── LLaVAModel
        └── Source: HuggingFace
```

### Metric Functions
```
Metrics (module)
    ├── attack_success_rate(clean, attacked) → [0,1]
    ├── output_deviation_score(clean, attacked) → [0,1]
    ├── safety_bypass_rate(safety_rules, output) → [0,1]
    ├── cross_modal_conflict_score(vision, language) → [0,1]
    └── transferability_score(source_asr, target_asr) → [0,1]
```

---

## Execution Flow (Cloud Notebook)

```
Cell 1:   Load title + description
    ↓
Cell 2:   Install dependencies (Pillow, transformers, torch, etc.)
    ↓
Cell 3:   Authenticate & clone repository
    ↓
Cell 4:   Load attack implementations
    ↓
Cell 5-6: Generate test images (synthetic)
    ↓
Cell 7:   Generate attacked variants (3 techniques × 2 injections × 4 images)
    ↓
Cell 8:   Test CLIP model
Cell 9:   Test MobileViT model
Cell 10:  Test BLIP-2 model
Cell 11:  Test LLaVA model (optional, memory intensive)
    ↓ (Collect results)
    ↓
Cell 12:  Compute metrics for all models
    ↓
Cell 13:  Generate visualizations (bar charts)
    ↓
Cell 14:  Print results summary
    ↓
Cell 15:  Generate PDF report
    ↓
Cell 16:  Export JSON results
    ↓
Cell 17:  Download files or create public links
    ↓
DONE:    All results ready (~30 minutes on Colab GPU)
```

---

## Performance Characteristics

| Component | Size | Speed | Memory |
|-----------|------|-------|--------|
| CLIP | 350MB | ~100 img/s | 2GB |
| MobileViT | 20MB | ~500 img/s | 1GB |
| BLIP-2 | 2.7B | ~5 img/s | 8GB |
| LLaVA-7B | 7B | ~2 img/s | 14GB |
| All Attacks | N/A | <1s per image | <500MB |

---

## Key Design Decisions

### 1. **Modular Attack System**
- Each attack is independent, composable
- Can combine attacks (e.g., typographic + perturbation)
- Easy to add new attack types

### 2. **Unified Model Interface**
- All models implement `BaseModel`
- Consistent `infer(image) → output` API
- Abstracts away API vs local model differences

### 3. **Metric Independence**
- Metrics don't depend on implementation details
- Can be applied to any model output
- Extensible to new metrics

### 4. **Cloud-First Architecture**
- Notebook handles GPU management
- No local GPU required
- Results downloadable as standard formats

### 5. **Configuration-Driven**
- Attack/model selection via config.yaml
- Parameters easily adjustable
- Reproducible runs

---

## Testing Strategy

```
Unit Tests (Local, No GPU)
    ├── test_attack_basic.py
    │   └── Test each attack generates valid images
    │       - Shape preservation
    │       - Mode correctness (RGB)
    │       - File I/O
    │
    ├── test_attack_generation.py
    │   └── Test variant generation
    │       - Correct number of variants
    │       - All files written
    │       - Config consistency
    │
    └── Integration Tests (GPU Optional)
        ├── test_lightweight_models.py
        │   └── Test CLIP & MobileViT
        │
        └── test_blip2_injection.py
            └── Test BLIP-2 specifically

Cloud Tests (Full Pipeline)
    └── ImageInjection_MultiModel_Cloud.ipynb
        └── End-to-end evaluation on all models
```

---

## Metrics Computation Example

```python
# Clean output
clean = "a white cat sitting on a chair"

# Attacked output  
attacked = "a dog sitting on a chair"

# ASR: Did output change?
asr = 1.0 if clean != attacked else 0.0  # True→1.0, False→0.0

# ODS: How different?
similarity = semantic_similarity(clean, attacked)
ods = 1.0 - similarity  # Range: 0.0 (same) to 1.0 (completely different)
# In this case: ~0.6 (word substitution, but same structure)

# SBR: Did it bypass safety?
sbr = contains_harmful_content(attacked)  # boolean → 0.0 or 1.0
# In this case: 0.0 (harmless output)

# CMCS: Vision vs language dominance
vision_confidence = 0.8  # How much did vision drive the output?
language_confidence = 0.2
cmcs = 1.0 - abs(vision_confidence - language_confidence)
# In this case: 0.6 (mostly vision-driven)
```

This illustrates how a single image+attack+model combination produces 4 metrics.

---

## Publications & Research Artifacts

### Currently in Development
1. **Semester Project Report** (~30 pages)
   - Problem statement
   - Literature review
   - Methodology
   - Results & analysis
   - Conclusions

2. **Research Paper** (targeting CVPR/EMNLP workshop)
   - Title: "Cross-Modal Vulnerability Assessment of Vision-Language Models to Image Injection Attacks"
   - Novel CMCS metric
   - Transferability analysis
   - Model profiling findings

3. **Benchmarking Leaderboard** (future)
   - Public results comparison
   - Extensible evaluation framework
   - Community contributions

---

## Summary

This architecture provides:
- ✅ **Flexibility**: Mix & match attacks, models, metrics
- ✅ **Extensibility**: Add new attacks/models without touching core
- ✅ **Reproducibility**: Cloud notebook ensures consistent evaluation
- ✅ **Scalability**: Handle multiple models efficiently
- ✅ **Transparency**: Modular design exposes all steps
- ✅ **Professional Output**: Publication-ready reports

