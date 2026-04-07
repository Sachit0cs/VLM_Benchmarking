# VISUAL MAP: Where Everything Goes in VLM_ARB_Report.tex

This is a visual guide showing EXACTLY where each piece of real data goes in the LaTeX document.

---

## PAGE-BY-PAGE ROADMAP

### 📄 PAGE 1: TITLE & EXECUTIVE SUMMARY

```
┌─────────────────────────────────────────────────────────┐
│  VLM-ARB: Adversarial Robustness Benchmarking          │
│  Vision-Language Models Under Attack                    │
│                                                          │
│  Evaluation Report                                      │
│  [DATE TODAY]                                           │
│                                                          │
│  ───────────────────────────────────────────────────   │
│                                                          │
│  Run ID: eval_20260408_153022_a1b2c3d4 ← LOCATION 7   │
│  Timestamp: 2026-04-08 15:30:22 ← LOCATION 7          │
│  Dataset Version: v20260408_120000_abc1234 ← L7        │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  EXECUTIVE SUMMARY                                      │
│                                                          │
│  This report presents evaluation results of 4 VLMs...  │
│                                                          │
│  Key Findings:                                          │
│  • Tested models: CLIP, MobileViT, BLIP-2, LLaVA      │
│  • Attack types: Prompt Injection, Typographic        │
│  • Metrics: ASR, ODS, SBR                             │
│                                                          │
│  Vulnerability Summary: Most vulnerable to least      │
│  robust:                                               │
│  LLaVA (ASR: 0.XX) > BLIP-2 (ASR: 0.XX) >  ← LOC 1  │
│  MobileViT (ASR: 0.XX) > CLIP (ASR: 0.XX)            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**ACTION**: Update LOCATION 1 (line ~55) with YOUR values from Firestore

---

### 📄 PAGES 2-4: METHODOLOGY & MODELS

These pages are FIXED — no data to add.

```
┌─────────────────────────────────────────────────────────┐
│  METHODOLOGY                                            │
│  • Attack 1: Prompt Injection (HOUYI structure)        │
│  • Attack 2: Typographic Overlay                       │
│  (All hardcoded from your PROJECT_OVERVIEW)            │
│                                                          │
│  MODELS EVALUATED                                       │
│  • CLIP (vision-only classifier)                       │
│  • MobileViT (lightweight classifier)                  │
│  • BLIP-2 (generative VLM)                            │
│  • LLaVA (generative VLM)                             │
│  (All hardcoded from your notebook specs)              │
│                                                          │
│  EVALUATION METRICS                                     │
│  • ASR (Attack Success Rate)                           │
│  • ODS (Output Deviation Score)                        │
│  • SBR (Safety Bypass Rate)                            │
│  (All formulas and definitions hardcoded)              │
│                                                          │
│  DATASETS                                               │
│  • Synthetic base images (5)                           │
│  • COCO 2017 variants                                  │
│  • Total variants (~150-165)                           │
│  (Hardcoded specifications)                            │
└─────────────────────────────────────────────────────────┘
```

✅ **NO ACTION NEEDED** — Content is fixed

---

### 📄 PAGE 5-6: RESULTS (YOUR REAL DATA)

```
┌─────────────────────────────────────────────────────────┐
│  RESULTS                                                │
│                                                          │
│  Table 1: Model Comparison - Key Metrics               │
│  ┌──────────────┬─────────┬─────────┬─────────┐       │
│  │ Model        │   ASR   │   ODS   │   SBR   │       │
│  ├──────────────┼─────────┼─────────┼─────────┤       │
│  │ CLIP         │ 0.XX ←──┤ 0.XX    │ 0.XX    │       │
│  │ MOBILEVIT    │ 0.XX ←──┤ 0.XX    │ 0.XX    │       │ ← LOCATION 2
│  │ BLIP-2       │ 0.XX ←──┤ 0.XX    │ 0.XX    │       │   Line ~245
│  │ LLAVA        │ 0.XX ←──┤ 0.XX    │ 0.XX    │       │
│  └──────────────┴─────────┴─────────┴─────────┘       │
│                                                          │
│  Attack Effectiveness Analysis                          │
│                                                          │
│  Prompt Injection:                                      │
│  • CLIP: ASR ≈ 0.XX ← LOCATION 3 (Line ~270)         │
│  • MobileViT: ASR ≈ 0.XX ← LOCATION 3                │
│  • BLIP-2: ASR ≈ 0.XX ← LOCATION 3                   │
│  • LLaVA: ASR ≈ 0.XX ← LOCATION 3                    │
│                                                          │
│  Typographic Overlay:                                   │
│  • CLIP: ASR ≈ 0.XX ← LOCATION 4 (Line ~290)         │
│  • MobileViT: ASR ≈ 0.XX ← LOCATION 4                │
│  • BLIP-2: ASR ≈ 0.XX ← LOCATION 4                   │
│  • LLaVA: ASR ≈ 0.XX ← LOCATION 4                    │
│                                                          │
│  Synthetic vs COCO:                                     │
│  • CLIP: Synth=0.XX, COCO=0.XX, Gap=0.XX             │ ← LOCATION 6
│  • MobileViT: Synth=0.XX, COCO=0.XX, Gap=0.XX        │   (New section)
│  • BLIP-2: Synth=0.XX, COCO=0.XX, Gap=0.XX           │
│  • LLaVA: Synth=0.XX, COCO=0.XX, Gap=0.XX            │
│                                                          │
│  Safety Bypass Analysis                                 │
│  ┌──────────────┬─────────┬──────────────────────────┐ │
│  │ Model        │   SBR   │ Safety Status            │ │
│  ├──────────────┼─────────┼──────────────────────────┤ │
│  │ CLIP         │ 0.XX ←──┤ Effective (no text gen)  │ │← LOCATION 5
│  │ MOBILEVIT    │ 0.XX    │ Effective (no text gen)  │ │  Line ~315
│  │ BLIP-2       │ 0.XX    │ Strong (rare bypass)     │ │
│  │ LLAVA        │ 0.XX    │ Moderate (occ. bypass)   │ │
│  └──────────────┴─────────┴──────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**ACTIONS**:
- [ ] LOCATION 2 (Line ~245): Update 4 models × 3 metrics = 12 values
- [ ] LOCATION 3 (Line ~270): Update 4 prompt injection ASR estimates
- [ ] LOCATION 4 (Line ~290): Update 4 typographic ASR estimates
- [ ] LOCATION 5 (Line ~315): Update 4 models SBR values
- [ ] LOCATION 6 (Line ~300-310): Add new section with synthetic vs COCO

---

### 📄 PAGES 6-7: VISUALIZATIONS (YOUR CHART IMAGES)

```
┌─────────────────────────────────────────────────────────┐
│  VISUALIZATIONS                                         │
│                                                          │
│  6.1 Model Robustness Comparison                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │      [YOUR 01_model_comparison.png]            │   │
│  │                                                 │   │
│  │   3-panel bar chart: ASR | ODS | SBR          │   │ ← LOCATION 8
│  │                                                 │   │  Line ~340
│  │   CLIP:      ASR=0.XX   ODS=0.XX   SBR=0.XX  │   │
│  │   MobileViT: ASR=0.XX   ODS=0.XX   SBR=0.XX  │   │
│  │   BLIP-2:    ASR=0.XX   ODS=0.XX   SBR=0.XX  │   │
│  │   LLaVA:     ASR=0.XX   ODS=0.XX   SBR=0.XX  │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  6.2 Robustness Gap: Synthetic vs Real Images          │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │      [YOUR 02_robustness_gap.png]             │   │
│  │                                                 │   │
│  │   Gap analysis showing ASR difference         │   │ ← LOCATION 9
│  │   between synthetic and COCO images.          │   │  Line ~365
│  │                                                 │   │
│  │   Positive gap = synthetic more vulnerable    │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  6.3 Additional Charts                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [Add your custom visualizations here if any]  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**ACTIONS**:
- [ ] LOCATION 8 (Line ~340): Replace placeholder with `\includegraphics{01_model_comparison.png}`
- [ ] LOCATION 9 (Line ~365): Replace placeholder with `\includegraphics{02_robustness_gap.png}`
- [ ] Upload both PNG files to Overleaf first!

---

### 📄 PAGES 7-9: DISCUSSION & CONCLUSION

These pages are MOSTLY FIXED — but can customize:

```
┌─────────────────────────────────────────────────────────┐
│  DISCUSSION                                             │
│                                                          │
│  Key Findings (AUTO-FILLED based on your metrics)       │
│  • Vision-only models robust to prompt injection       │
│  • Generative models vulnerable to both attacks        │
│  • Safety mechanisms insufficient (SBR > 0)            │
│  • Synthetic images more vulnerable                    │
│                                                          │
│  OPTIONAL: Customize conclusions based on YOUR         │
│  specific findings and research                        │
│                                                          │
│  CONCLUSION                                             │
│  Summary and recommendations based on metrics.         │
│  (Hardcoded template, can be customized)               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

✅ No mandatory changes, but can edit for custom insights

---

### 📄 PAGE 10: APPENDICES (YOUR RAW DATA)

```
┌─────────────────────────────────────────────────────────┐
│  APPENDIX C: RAW DATA SAMPLE                            │
│                                                          │
│  Sample Evaluation Run                                  │
│                                                          │
│  {                                                      │
│    "run_id": "eval_20260408_153022_a1b2c3d4",         │
│    "timestamp": "2026-04-08T15:30:22.789Z",           │
│    "metrics": {                                        │
│      "clip": {                                         │
│        "asr": 0.XX, ← LOCATION 10 (Line ~480)        │
│        "ods": 0.XX,                                   │
│        "sbr": 0.XX                                    │
│      },                                                │
│      "mobilevit": {                                    │
│        "asr": 0.XX,                                   │
│        "ods": 0.XX,                                   │
│        "sbr": 0.XX                                    │
│      },                                                │
│      "blip2": {                                        │
│        "asr": 0.XX,                                   │
│        "ods": 0.XX,                                   │
│        "sbr": 0.XX                                    │
│      },                                                │
│      "llava": {                                        │
│        "asr": 0.XX,                                   │
│        "ods": 0.XX,                                   │
│        "sbr": 0.XX                                    │
│      }                                                 │
│    }                                                   │
│  }                                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**ACTION**:
- [ ] LOCATION 10 (Line ~480): Replace with actual Firestore JSON document

---

## SUMMARY: ALL LOCATIONS AT A GLANCE

| Loc | Section | Type | Source | Lines | Action |
|-----|---------|------|--------|-------|--------|
| 1 | Exec Summary | Text | Firestore metrics | ~55 | Fill ASR values |
| 2 | Results Table | Table | Firestore metrics | ~245 | Fill 12 values |
| 3 | Prompt Injection | Text | Estimate from ASR | ~270 | Fill 4 ASR values |
| 4 | Typographic | Text | Estimate from ASR | ~290 | Fill 4 ASR values |
| 5 | Safety Table | Table | Firestore metrics | ~315 | Fill 4 SBR values |
| 6 | Synthetic vs COCO | Text | Firestore data | ~305 NEW | Fill 4×3 values |
| 7 | Metadata | Text | Firestore metadata | ~50 | Fill run_id, timestamp |
| 8 | Chart 1 | Image | PNG from Notebook 3 | ~340 | Add includegraphics |
| 9 | Chart 2 | Image | PNG from Notebook 3 | ~365 | Add includegraphics |
| 10 | Appendix | JSON | Firestore document | ~480 | Replace JSON block |

---

## QUICK FILL-IN FORM

Print this out and fill in your FIRESTORE VALUES, then transfer to Overleaf:

```
╔════════════════════════════════════════════════════════╗
║          VLM-ARB REPORT - DATA COLLECTION FORM          ║
╚════════════════════════════════════════════════════════╝

RUN METADATA (From Firestore > run_id document):
  Run ID: ________________________________
  Timestamp: ________________________________
  Dataset Version: ________________________________

MODEL METRICS (From Firestore > metrics):

CLIP:
  ASR: __.___%    ODS: __.___%    SBR: __.___%
  Prompt Injection ASR estimate: __.___%
  Typographic ASR estimate: __.___%

MobileViT:
  ASR: __.___%    ODS: __.___%    SBR: __.___%
  Prompt Injection ASR estimate: __.___%
  Typographic ASR estimate: __.___%

BLIP-2:
  ASR: __.___%    ODS: __.___%    SBR: __.___%
  Prompt Injection ASR estimate: __.___%
  Typographic ASR estimate: __.___%

LLaVA:
  ASR: __.___%    ODS: __.___%    SBR: __.___%
  Prompt Injection ASR estimate: __.___%
  Typographic ASR estimate: __.___%

SYNTHETIC vs COCO (From Firestore > synthetic_vs_coco):

CLIP:
  Synthetic ASR: __.___%  |  COCO ASR: __.___%  |  Gap: __.___%

MobileViT:
  Synthetic ASR: __.___%  |  COCO ASR: __.___%  |  Gap: __.___%

BLIP-2:
  Synthetic ASR: __.___%  |  COCO ASR: __.___%  |  Gap: __.___%

LLaVA:
  Synthetic ASR: __.___%  |  COCO ASR: __.___%  |  Gap: __.___%

CHARTS (From Notebook 3):
  ☐ 01_model_comparison.png uploaded
  ☐ 02_robustness_gap.png uploaded

COMPLETE FIRESTORE JSON:
[Paste entire Firestore document here for Appendix C]

╔════════════════════════════════════════════════════════╗
║              TOTAL VALUES TO FILL IN: 52               ║
║  (12 metrics + 8 ASR est. + 12 synth/coco + 1 JSON)   ║
╚════════════════════════════════════════════════════════╝
```

---

## EXAMPLE: COMPLETED FORM

```
╔════════════════════════════════════════════════════════╗
║          VLM-ARB REPORT - DATA COLLECTION FORM          ║
╚════════════════════════════════════════════════════════╝

RUN METADATA (From Firestore > run_id document):
  Run ID: eval_20260408_153022_a1b2c3d4
  Timestamp: 2026-04-08 15:30:22
  Dataset Version: v20260408_120000_abc1234

MODEL METRICS (From Firestore > metrics):

CLIP:
  ASR: 0.35%    ODS: 0.28%    SBR: 0.00%
  Prompt Injection ASR estimate: 0.15%
  Typographic ASR estimate: 0.20%

MobileViT:
  ASR: 0.45%    ODS: 0.38%    SBR: 0.00%
  Prompt Injection ASR estimate: 0.22%
  Typographic ASR estimate: 0.23%

BLIP-2:
  ASR: 0.68%    ODS: 0.58%    SBR: 0.05%
  Prompt Injection ASR estimate: 0.55%
  Typographic ASR estimate: 0.68%

LLaVA:
  ASR: 0.78%    ODS: 0.65%    SBR: 0.12%
  Prompt Injection ASR estimate: 0.65%
  Typographic ASR estimate: 0.75%

SYNTHETIC vs COCO (From Firestore > synthetic_vs_coco):

CLIP:
  Synthetic ASR: 0.42%  |  COCO ASR: 0.28%  |  Gap: 0.14%

MobileViT:
  Synthetic ASR: 0.52%  |  COCO ASR: 0.38%  |  Gap: 0.14%

BLIP-2:
  Synthetic ASR: 0.75%  |  COCO ASR: 0.61%  |  Gap: 0.14%

LLaVA:
  Synthetic ASR: 0.85%  |  COCO ASR: 0.71%  |  Gap: 0.14%

CHARTS (From Notebook 3):
  ☑ 01_model_comparison.png uploaded
  ☑ 02_robustness_gap.png uploaded

╔════════════════════════════════════════════════════════╗
║              TOTAL VALUES FILLED IN: 52 ✅             ║
╚════════════════════════════════════════════════════════╝
```

---

## FINAL CHECKLIST BEFORE SUBMITTING

- [ ] All 10 LOCATIONS updated in Overleaf
- [ ] All values come from FIRESTORE (real data)
- [ ] No placeholder values left (search for "XX" or "___")
- [ ] Both PNG charts uploaded and displaying
- [ ] PDF compiles without errors
- [ ] All metrics visible in PDF preview
- [ ] Appendix shows actual run data
- [ ] Report metadata (run ID, timestamp) visible
- [ ] Discussion makes sense with YOUR specific values
- [ ] Ready to download & share! ✅

---

This visual map ensures ZERO confusion about where things go. Every section, every value, every image placement is crystal clear.

