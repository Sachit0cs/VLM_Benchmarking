# DATA FLOW: From Firestore to Your LaTeX Report

Visual diagram showing EXACTLY how real data flows from Firestore into your Overleaf document.

---

## 🔄 COMPLETE FLOW DIAGRAM

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         YOUR EVALUATION WORKFLOW                            │
└────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────────┐
     │  NOTEBOOK 2 RUNS    │  (Your Google Colab)
     │  (Evaluation)       │  • Tests 4 models
     │                     │  • Computes metrics
     │  OUTPUTS:           │  • ASR, ODS, SBR
     │  • Metrics (JSON)   │
     │  • Raw results      │
     └──────────┬──────────┘
                │
                ▼
     ┌──────────────────────────────────────────────┐
     │           FIRESTORE DATABASE                 │
     │                                              │
     │  Collection: results                         │
     │  Document: eval_XXXXXXX_XXXXXXX             │ ← HERE IS YOUR REAL DATA
     │                                              │
     │  {                                           │
     │    "run_id": "...",                         │
     │    "timestamp": "...",                       │
     │    "metrics": {                              │
     │      "clip": {                              │
     │        "asr": 0.35,  ← YOUR REAL VALUE    │
     │        "ods": 0.28,                         │
     │        "sbr": 0.00                          │
     │      },                                      │
     │      "mobilevit": { ... },                  │
     │      "blip2": { ... },                      │
     │      "llava": { ... }                       │
     │    },                                        │
     │    "synthetic_vs_coco": { ... }             │
     │  }                                           │
     │                                              │
     └──────────┬──────────────────────────────────┘
                │
         ┌──────┴──────────────────────┐
         │                             │
         ▼                             ▼
     ┌─────────────┐          ┌──────────────────┐
     │  GOOGLE     │          │   LOCAL CACHE    │
     │  DRIVE      │          │  (Backup JSON)   │
     └──────┬──────┘          └──────────────────┘
            │
            ▼
     ┌──────────────────────┐
     │  YOU (MANUALLY)      │  ← YOU COPY VALUES
     │                      │
     │ • Open Firestore     │
     │ • Read metrics       │
     │ • Note down values   │
     │ • Open OVERLEAF      │
     │ • Paste into 10 spots│
     └──────────┬───────────┘
                │
                ▼
     ┌────────────────────────────────────────────┐
     │           OVERLEAF (ONLINE LATEX)          │
     │                                            │
     │  VLM_ARB_Report.tex with REAL DATA:       │
     │                                            │
     │  Page 1: Your ASR values ✓                │
     │  Page 5: Your metrics table ✓              │
     │  Page 6: Your charts (PNG) ✓              │
     │  Page 10: Your JSON data ✓                │
     │                                            │
     │  Click: Recompile → PDF Preview ✓         │
     │  Click: Download → Your Report ✓          │
     │                                            │
     └────────────────────────────────────────────┘
                │
                ▼
     ┌──────────────────────┐
     │  FINAL PDF REPORT    │  ← READY TO SHARE!
     │                      │
     │ • Professional format│
     │ • Real data from DB  │
     │ • All charts visible │
     │ • Publication-ready  │
     │                      │
     └──────────────────────┘
```

---

## 📊 DATA MAPPING (Firestore → LaTeX Locations)

```
FIRESTORE DOCUMENT
│
├─ run_id
│    │
│    └──→ LaTeX LOCATION 7 (Metadata)
│         Line ~50: "Run ID: {value}"
│
├─ timestamp
│    │
│    └──→ LaTeX LOCATION 7 (Metadata)
│         Line ~51: "Timestamp: {value}"
│
├─ metrics
│    │
│    ├─ clip
│    │  ├─ asr: 0.35  ──→ LOCATION 1 (Executive Summary, Line ~55)
│    │  │               LOCATION 2 (Table 1, Line ~247)
│    │  │
│    │  ├─ ods: 0.28  ──→ LOCATION 2 (Table 1, Line ~247)
│    │  │
│    │  └─ sbr: 0.00  ──→ LOCATION 2 (Table 1, Line ~247)
│    │                    LOCATION 5 (Safety Table, Line ~315)
│    │
│    ├─ mobilevit
│    │  ├─ asr: 0.45  ──→ LOCATION 2 (Table 1, Line ~248)
│    │  ├─ ods: 0.38  ──→ LOCATION 2 (Table 1, Line ~248)
│    │  └─ sbr: 0.00  ──→ LOCATION 2 (Table 1, Line ~248)
│    │                    LOCATION 5 (Safety Table, Line ~316)
│    │
│    ├─ blip2
│    │  ├─ asr: 0.68  ──→ LOCATION 2 (Table 1, Line ~249)
│    │  │               LOCATION 4 (Typo analysis, Line ~290)
│    │  ├─ ods: 0.58  ──→ LOCATION 2 (Table 1, Line ~249)
│    │  └─ sbr: 0.05  ──→ LOCATION 2 (Table 1, Line ~249)
│    │                    LOCATION 5 (Safety Table, Line ~317)
│    │
│    └─ llava
│       ├─ asr: 0.78  ──→ LOCATION 1 (Executive Summary, Line ~55)
│       │               LOCATION 2 (Table 1, Line ~250)
│       ├─ ods: 0.65  ──→ LOCATION 2 (Table 1, Line ~250)
│       └─ sbr: 0.12  ──→ LOCATION 2 (Table 1, Line ~250)
│                        LOCATION 5 (Safety Table, Line ~318)
│
├─ synthetic_vs_coco
│    │
│    ├─ clip
│    │  ├─ synthetic_asr: 0.42     ──→ LOCATION 6 (New section, ~305)
│    │  ├─ coco_asr: 0.28
│    │  └─ robustness_gap: 0.14
│    │
│    ├─ mobilevit
│    │  ├─ synthetic_asr: 0.52     ──→ LOCATION 6
│    │  ├─ coco_asr: 0.38
│    │  └─ robustness_gap: 0.14
│    │
│    ├─ blip2
│    │  ├─ synthetic_asr: 0.75     ──→ LOCATION 6
│    │  ├─ coco_asr: 0.61
│    │  └─ robustness_gap: 0.14
│    │
│    └─ llava
│       ├─ synthetic_asr: 0.85     ──→ LOCATION 6
│       ├─ coco_asr: 0.71
│       └─ robustness_gap: 0.14
│
└─ [entire document]
     │
     └──→ LOCATION 10 (Appendix C, Line ~480)
          "Paste entire JSON here"
```

---

## 🖼️ IMAGE DATA FLOW

```
NOTEBOOK 3 OUTPUT
│
├─ 01_model_comparison.png
│  │
│  ├─ File: results/reports/01_model_comparison.png
│  │
│  ├─ Content: 3-panel bar chart
│  │   └─ ASR chart | ODS chart | SBR chart
│  │
│  ├─ You: Download/Save this file
│  │
│  ├─ Overleaf: Upload to Files panel
│  │
│  ├─ LaTeX: LOCATION 8 (Section 6.1, Line ~340)
│  │  └─ \includegraphics[width=0.9\textwidth]{01_model_comparison.png}
│  │
│  └─ PDF: Chart displays on Page 6 ✓
│
└─ 02_robustness_gap.png
   │
   ├─ File: results/reports/02_robustness_gap.png
   │
   ├─ Content: Robustness gap bar chart
   │   └─ Synthetic vs COCO comparison
   │
   ├─ You: Download/Save this file
   │
   ├─ Overleaf: Upload to Files panel
   │
   ├─ LaTeX: LOCATION 9 (Section 6.2, Line ~365)
   │  └─ \includegraphics[width=0.9\textwidth]{02_robustness_gap.png}
   │
   └─ PDF: Chart displays on Page 7 ✓
```

---

## 🔗 EXACT DATA FLOW (Step by Step)

### Step 1: Firestore has your data
```
Firestore DB
└─ results/eval_20260408_153022_a1b2c3d4
   └─ metrics
      └─ clip
         ├─ asr: 0.35 ← Real value from Notebook 2
```

### Step 2: You read it
```
You open Firestore Console
└─ See: "asr": 0.35
   Write it down: CLIP ASR = 0.35
```

### Step 3: You enter it in Overleaf
```
Overleaf LaTeX
└─ LOCATION 2 (Table 1)
   └─ Find: "CLIP & 0.35 & 0.28 & 0.00"
      └─ 0.35 ← Your Firestore value!
```

### Step 4: PDF renders with your value
```
PDF Preview
└─ Table shows: CLIP | 0.35 | 0.28 | 0.00
   └─ 0.35 ← Same as Firestore!
   └─ Render successful! ✓
```

---

## 📋 QUICK REFERENCE: What Goes Where

| From Firestore | To LaTeX | Goes in | Line |
|---|---|---|---|
| metrics.clip.asr | Table | LOCATION 2 | ~247 |
| metrics.clip.ods | Table | LOCATION 2 | ~247 |
| metrics.clip.sbr | Table + Safety | LOC 2 + 5 | 247, 315 |
| metrics.mobilevit.* | Table | LOCATION 2 | ~248 |
| metrics.blip2.* | Table | LOCATION 2 | ~249 |
| metrics.llava.* | Table | LOCATION 2 | ~250 |
| synthetic_vs_coco.clip.* | Text | LOCATION 6 | ~305 |
| synthetic_vs_coco.all | Text | LOCATION 6 | ~305 |
| run_id | Metadata | LOCATION 7 | ~50 |
| timestamp | Metadata | LOCATION 7 | ~51 |
| Entire doc | JSON | LOCATION 10 | ~480 |

---

## ✔️ VERIFICATION CHECKLIST

After adding each piece of data:

| Data | Source | Added to LaTeX | Visible in PDF |
|---|---|---|---|
| CLIP/MobileViT/BLIP-2/LLaVA metrics | Firestore | ✓ Check LOC 2 | ✓ Page 5 Table |
| Safety values | Firestore | ✓ Check LOC 5 | ✓ Page 6 Table |
| Synthetic vs COCO | Firestore | ✓ Check LOC 6 | ✓ Page 5-6 Text |
| Chart 1 (01_model_comparison.png) | Notebook 3 | ✓ Check LOC 8 | ✓ Page 6 Image |
| Chart 2 (02_robustness_gap.png) | Notebook 3 | ✓ Check LOC 9 | ✓ Page 7 Image |
| Raw JSON | Firestore | ✓ Check LOC 10 | ✓ Page 10 Code |
| Run ID + Timestamp | Firestore | ✓ Check LOC 7 | ✓ Page 1 Text |

---

## 🎯 CRITICAL RULE: No Bluffs!

```
┌──────────────────────────────────────────┐
│   EVERY VALUE IN YOUR REPORT MUST BE:    │
│                                          │
│   1. Real (from Firestore)              │
│   2. Exact (copy-paste, not rounded)    │
│   3. Traceable (show source in mind)    │
│   4. Verified (check Firestore = LaTeX) │
│                                          │
│   NOT:                                   │
│   ✗ Estimated                           │
│   ✗ Placeholders                        │
│   ✗ Made-up examples                    │
│   ✗ Generic descriptions                │
│                                          │
│   YOUR REPORT = Firestore Data Output  │
│   Not speculative, not generic.         │
│                                          │
└──────────────────────────────────────────┘
```

**Every metric you add = directly from Firestore DB** ✓

---

## 📱 Mobile Firestore Access

If you need to access Firestore on phone/tablet:

1. Firebase Console: https://console.firebase.google.com
2. Firestore Database (mobile version works)
3. Navigate: results → eval_XXXXX
4. View JSON in mobile-friendly format
5. Copy-paste to Overleaf

Alternative: Use Google Drive JSON file (easier on mobile)
- Path: VLM-ARB-Team/results/raw/
- Open any JSON in Google Drive
- Copy values directly

---

## 🔒 Data Integrity Check

Make sure your data is REAL:

```
✓ QUESTION: Do my Firestore values match LaTeX values?
  ANSWER: If not, re-copy from Firestore

✓ QUESTION: Are all 10 locations filled?
  ANSWER: Use VISUAL_DATA_MAP.md checklist

✓ QUESTION: Do my charts show in PDF?
  ANSWER: Verify both PNGs uploaded in Files

✓ QUESTION: Does my JSON in Appendix match Firestore?
  ANSWER: Copy-paste entire doc, not just pieces

✓ QUESTION: Are any placeholder values left?
  ANSWER: Search for "XX" or "___" in LaTeX
```

---

## 🚀 WHAT HAPPENS AFTER YOU'RE DONE

```
Your Completed Report (100% Real Data)
│
├─ PDF File: VLM_ARB_Report.pdf
│  └─ Ready to:
│     • Print ✓
│     • Share ✓
│     • Submit ✓
│     • Publish ✓
│
├─ LaTeX Source: VLM_ARB_Report.tex
│  └─ Includes all real metrics
│     • Reproducible ✓
│     • Editable ✓
│     • Archivable ✓
│
└─ Original Firestore Data
   └─ Saved as backup:
      • Appendix C (in PDF)
      • Google Drive (original)
      • Your notes (hard copy)
```

---

## 📌 REMEMBER

This entire workflow ensures:

✅ **Traceability**: Every number → Firestore source
✅ **Accuracy**: Copy-paste, not manual entry
✅ **Completeness**: All 10 locations filled
✅ **Verification**: Compare Firestore → LaTeX → PDF
✅ **Professionalism**: Publication-ready output

**Result**: A professional, data-backed report that's 100% rooted in your actual evaluation results. No speculation, no bluffs, no generic content.

Just: Real data → Real charts → Real report. ✓

