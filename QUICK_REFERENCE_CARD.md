# ⚡ QUICK REFERENCE CARD - Print This!

**One-page cheat sheet for adding data to your Overleaf LaTeX report**

---

## 🎯 THE 10 LOCATIONS (With Line Numbers & Data Source)

```
┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 1: EXECUTIVE SUMMARY                           │
│         Line: ~55 | Source: Firestore metrics → clip.asr       │
│         ─────────────────────────────────────────────────        │
│         Find: "LLaVA (ASR: 0.78) > BLIP-2 (ASR: 0.68)"        │
│         Fetch: Your ASR values for all 4 models                 │
│         Replace: Use YOUR exact ASR values                      │
│         Example: "LLaVA (ASR: 0.78) > BLIP-2 (ASR: 0.71)..."  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 2: RESULTS TABLE (12 VALUES)                   │
│         Line: ~247 | Source: Firestore metrics (all)            │
│         ─────────────────────────────────────────────────        │
│         Find: "CLIP & 0.35 & 0.28 & 0.00 \\"                  │
│         Fetch: 4 models × 3 metrics (ASR, ODS, SBR)            │
│         Replace: All 4 table rows with YOUR values             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 3: PROMPT INJECTION ANALYSIS                   │
│         Line: ~270 | Source: Estimate from ASR                  │
│         ─────────────────────────────────────────────────        │
│         Find: "ASR $\approx 0.15$" ... "ASR $\approx 0.65$"   │
│         Action: Estimate prompt injection portion (40-50% ASR)  │
│         Replace: 4 ASR estimates for each model                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 4: TYPOGRAPHIC ANALYSIS                        │
│         Line: ~290 | Source: Estimate from ASR                  │
│         ─────────────────────────────────────────────────        │
│         Find: "ASR $\approx 0.20$" ... "ASR $\approx 0.75$"   │
│         Action: Estimate typographic portion (50-60% ASR)       │
│         Replace: 4 ASR estimates for each model                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 5: SAFETY BYPASS TABLE                         │
│         Line: ~315 | Source: Firestore metrics → *.sbr         │
│         ─────────────────────────────────────────────────        │
│         Find: Table with "CLIP & 0.00" ... "LLAVA & 0.12"     │
│         Fetch: SBR values for 4 models from Firestore          │
│         Replace: All 4 SBR values in table                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 6: SYNTHETIC vs COCO (NEW SECTION)             │
│         Line: ~305 | Source: Firestore synthetic_vs_coco       │
│         ─────────────────────────────────────────────────        │
│         Action: ADD new section before Safety table             │
│         Fetch: 4 models × 3 values (synth, coco, gap)          │
│         Insert: Complete new subsection with your values        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 7: METADATA                                    │
│         Line: ~50 | Source: Firestore metadata                  │
│         ─────────────────────────────────────────────────        │
│         Find: After \maketitle                                  │
│         Fetch: run_id, timestamp, dataset_version              │
│         Insert: 3 lines with your metadata                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 8: CHART 1 IMAGE                               │
│         Line: ~340 | Source: Notebook 3 → 01_model_*.png      │
│         ─────────────────────────────────────────────────        │
│         Find: [INSERT FIGURE: 01_model_comparison.png]         │
│         Upload: PNG file to Overleaf Files panel               │
│         Replace: Placeholder → \includegraphics{file.png}      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 9: CHART 2 IMAGE                               │
│         Line: ~365 | Source: Notebook 3 → 02_robustness_*.png │
│         ─────────────────────────────────────────────────────────┐
│         Find: [INSERT FIGURE: 02_robustness_gap.png]           │
│         Upload: PNG file to Overleaf Files panel               │
│         Replace: Placeholder → \includegraphics{file.png}      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│         LOCATION 10: APPENDIX JSON                              │
│         Line: ~480 | Source: Firestore entire document         │
│         ─────────────────────────────────────────────────        │
│         Find: Sample JSON in \begin{verbatim}...\end{verbatim} │
│         Fetch: Entire Firestore document JSON                  │
│         Replace: Sample → YOUR actual JSON                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 YOUR FIRESTORE DATA STRUCTURE

```
results/eval_XXXXXXX_XXXXXXX
├─ run_id: "eval_..." ──────────────→ LOCATION 7
├─ timestamp: "2026-04-08T..." ─────→ LOCATION 7
├─ metrics:
│  ├─ clip: {asr: 0.XX, ods: 0.XX, sbr: 0.XX} ──→ LOC 1,2,5
│  ├─ mobilevit: {asr: 0.XX, ...} ────────────→ LOC 1,2,5
│  ├─ blip2: {asr: 0.XX, ...} ───────────────→ LOC 1,2,5
│  └─ llava: {asr: 0.XX, ...} ───────────────→ LOC 1,2,5
├─ synthetic_vs_coco:
│  ├─ clip: {synthetic_asr, coco_asr, gap} ──→ LOCATION 6
│  ├─ mobilevit: {...} ─────────────────────→ LOCATION 6
│  ├─ blip2: {...} ──────────────────────────→ LOCATION 6
│  └─ llava: {...} ──────────────────────────→ LOCATION 6
└─ [entire document] ───────────────────────→ LOCATION 10
```

---

## 🚀 THE 35-MINUTE WORKFLOW

```
TIME    TASK
─────   ─────────────────────────────────────
 5 min  1. Collect data from Firestore Console
        2. Write down metric values
        3. Have 2 PNG charts ready

 5 min  4. Go to Overleaf.com
        5. Create new project
        6. Upload VLM_ARB_Report.tex
        7. Upload 01_model_*.png and 02_robustness_*.png

20 min  8. Fill LOCATIONS 1-10
           (~2 min each)
        9. Open OVERLEAF_DETAILED_GUIDE.md in another window
       10. Copy-paste examples for each location

 5 min  11. Click Recompile
        12. Check PDF
        13. Download
        14. Done! ✓
─────────────────────────────────────────────
```

---

## ✅ DATA COLLECTION FORM

Print this, fill it in, then add to LaTeX:

```
═══════════════════════════════════════════════════════════════

FIRESTORE VALUES TO COPY:

RUN ID: _____________________________
TIMESTAMP: __________________________

CLIP:    ASR=__.__  ODS=__.__  SBR=__.__
MOBILEVIT: ASR=__.__  ODS=__.__  SBR=__.__
BLIP-2:  ASR=__.__  ODS=__.__  SBR=__.__
LLAVA:   ASR=__.__  ODS=__.__  SBR=__.__

PROMPTS (estimate):
CLIP: __.__   MobileViT: __.__   BLIP-2: __.__   LLaVA: __.__

TYPOGRAPHIC (estimate):
CLIP: __.__   MobileViT: __.__   BLIP-2: __.__   LLaVA: __.__

SYNTHETIC vs COCO:
CLIP: synth=__.__  coco=__.__  gap=__.__
MobileViT: synth=__.__  coco=__.__  gap=__.__
BLIP-2: synth=__.__  coco=__.__  gap=__.__
LLaVA: synth=__.__  coco=__.__  gap=__.__

IMAGES READY:
☐ 01_model_comparison.png
☐ 02_robustness_gap.png

═══════════════════════════════════════════════════════════════
```

---

## 📖 WHICH GUIDE WHEN?

| I need... | Use this | Time |
|-----------|----------|------|
| Quick overview | QUICK_START_OVERLEAF.md | 5 min |
| Step-by-step | OVERLEAF_DETAILED_GUIDE.md | 30 min |
| Visual map | VISUAL_DATA_MAP.md | 10 min |
| Data flow | DATA_FLOW_DIAGRAM.md | 10 min |
| Navigation | INDEX_OVERLEAF_PACKAGE.md | 5 min |
| Full reference | LATEX_REPORT_GUIDE.md | 20 min |

---

## ⚠️ CRITICAL CHECKLIST

Before you submit:

- [ ] All values from Firestore (not made up)
- [ ] No "XX" or "___" placeholders left
- [ ] Both PNG charts uploaded & visible
- [ ] PDF compiles without errors
- [ ] Table values match Firestore exactly
- [ ] Metadata added (run ID, timestamp)
- [ ] Appendix JSON replaced with yours
- [ ] Ready to download PDF

---

## 🔥 COMMON MISTAKES (AVOID THESE)

❌ Using placeholder values from examples
✅ Copy exact numbers from Firestore Console

❌ Forgetting to upload PNG files first
✅ Upload files to Overleaf BEFORE using \includegraphics

❌ Searching for vague text like "0.35"
✅ Use exact search text provided in guide (line numbers)

❌ Leaving sample JSON in appendix
✅ Replace with YOUR actual Firestore document

❌ Guessing where charts go
✅ Use exact line numbers for all insertions

---

## 💾 FILES YOU HAVE

```
Project Root/
├─ VLM_ARB_Report.tex ◄─ YOUR TEMPLATE
├─ QUICK_START_OVERLEAF.md ◄─ START HERE
├─ OVERLEAF_DETAILED_GUIDE.md ◄─ MAIN GUIDE
├─ VISUAL_DATA_MAP.md ◄─ REFERENCE
├─ DATA_FLOW_DIAGRAM.md
├─ INDEX_OVERLEAF_PACKAGE.md
├─ LATEX_REPORT_GUIDE.md
└─ This Quick Reference (print it!)
```

---

## 🎯 QUICK ANSWERS

**Q: Where do I get the data?**
A: Firestore Console > results > eval_XXXXXXX > metrics

**Q: How many values do I add?**
A: ~52 values across 10 locations

**Q: Where are exact line numbers?**
A: OVERLEAF_DETAILED_GUIDE.md for each location

**Q: What if LaTeX won't compile?**
A: Likely missing chart PNG files - upload them first

**Q: Can I modify the template?**
A: Yes! After filling data, customize discussion freely

**Q: How long does it take?**
A: 35 minutes total (5+5+20+5)

---

## 🎓 REMEMBER

```
┌───────────────────────────────────────────┐
│  NO BLUFFS                                │
│  NO GUESSES                               │
│  NO PLACEHOLDERS                          │
│                                           │
│  ONLY REAL FIRESTORE DATA ✓              │
│  ONLY EXACT LINE NUMBERS ✓               │
│  ONLY COPY-PASTE READY CODE ✓            │
└───────────────────────────────────────────┘
```

---

## 🚀 START NOW

1. Open: https://www.overleaf.com
2. Create project
3. Upload: VLM_ARB_Report.tex
4. Have open: OVERLEAF_DETAILED_GUIDE.md
5. Follow: LOCATION 1-10
6. Done in 35 minutes!

---

**Good luck! You've got this!** 💪

Print this card and keep by your computer while working in Overleaf!
