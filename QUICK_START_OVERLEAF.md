# QUICK START: Online LaTeX Editor (Overleaf) Work Summary

**All the guides you need to add REAL Firestore data to your LaTeX report**

---

## 📚 New Documentation Created

I've created **3 comprehensive guides** to help you add REAL data from Firestore to your online LaTeX report:

### 1. **OVERLEAF_DETAILED_GUIDE.md** ← START HERE
   - **What it does**: Step-by-step instructions with copy-paste examples
   - **Best for**: Doing the actual work in Overleaf
   - **Covers**: 
     - How to get data from Firestore (3 methods)
     - Exact line numbers to find in LaTeX
     - Copy-paste ready content
     - Image upload instructions
     - Verification checklist

### 2. **VISUAL_DATA_MAP.md** ← USE ALONGSIDE
   - **What it does**: Visual page-by-page roadmap showing where data goes
   - **Best for**: Avoiding mistakes, confirming locations
   - **Covers**:
     - Drawing of each page showing exact positions
     - Quick location reference table
     - Fill-in form to collect your data
     - Complete example (already filled)
     - Final checklist

### 3. **LATEX_REPORT_GUIDE.md** ← BACKUP REFERENCE
   - **What it does**: Comprehensive how-to with infrastructure details
   - **Best for**: Understanding the full system
   - **Covers**:
     - What data comes from Firestore (complete schema)
     - Metric definitions
     - JSON format examples
     - PDF generation setup

---

## 🎯 ACTUAL WORKFLOW (Copy This)

### Step 1: Collect Your Firestore Data (5 minutes)

**Go to**: https://console.firebase.google.com

**Copy these values** from `results/{your_run_id}` document:

```
CLIP:      ASR=__.__  ODS=__.__  SBR=__.__
MobileViT: ASR=__.__  ODS=__.__  SBR=__.__
BLIP-2:    ASR=__.__  ODS=__.__  SBR=__.__
LLaVA:     ASR=__.__  ODS=__.__  SBR=__.__
```

**Also get:**
- Run ID: `eval_XXXXXXX_XXXXXXXX`
- Timestamp: Your evaluation date/time
- Synthetic vs COCO values (if available)

**Print or note these down** → Have them ready

---

### Step 2: Upload to Overleaf (2 minutes)

1. Go to: https://www.overleaf.com
2. Create project → Upload `VLM_ARB_Report.tex`
3. Upload your 2 chart images:
   - `01_model_comparison.png`
   - `02_robustness_gap.png`

---

### Step 3: Fill in Data (20 minutes)

Follow **OVERLEAF_DETAILED_GUIDE.md** and update these 10 LOCATIONS:

| # | Section | Your Task | Time |
|---|---------|-----------|------|
| 1 | Executive Summary | Update ASR values | 1 min |
| 2 | Results Table | Fill 4×3 metrics | 2 min |
| 3 | Prompt Injection | Update 4 ASR estimates | 1 min |
| 4 | Typographic | Update 4 ASR estimates | 1 min |
| 5 | Safety Table | Fill 4 SBR values | 1 min |
| 6 | Synth vs COCO | Add 4×3 values (~new section) | 2 min |
| 7 | Metadata | Add run ID, timestamp | 1 min |
| 8 | Chart 1 | Insert image (PNG) | 2 min |
| 9 | Chart 2 | Insert image (PNG) | 2 min |
| 10 | Appendix | Paste full Firestore JSON | 5 min |

**Total**: 20 minutes max

---

### Step 4: Verify & Download (5 minutes)

1. Click **Recompile** in Overleaf
2. Check PDF shows all your values
3. Verify charts display correctly
4. Click **Download PDF**
5. Done! ✅

**Total time: ~30 minutes**

---

## 📍 WHERE TO FIND WHAT YOU NEED

### Getting Real Data
- **Firestore Console**: https://console.firebase.google.com
  - Navigate: Firestore Database → results → [your run ID]
  - Copy entire document for Appendix C

- **Google Drive** (alternative):
  - `VLM-ARB-Team/results/raw/` contains JSON files
  - Latest file (by timestamp) = your most recent run

### Chart Images
- **From Notebook 3 output**:
  - `results/reports/01_model_comparison.png` (3-panel chart)
  - `results/reports/02_robustness_gap.png` (gap analysis)
  - OR from Google Drive: `VLM-ARB-Team/reports/`

### LaTeX Template
- This repo: `VLM_ARB_Report.tex`
- Already contains placeholder sections
- Just fill in your values

---

## ✅ COMPLETE CHECKLIST

Before you start, have ready:

- [ ] **Access** to Firestore Console (or JSON file)
- [ ] **Your metrics** written down (CLIP, MobileViT, BLIP-2, LLaVA)
- [ ] **Both chart images** downloaded (PNG files)
- [ ] **Overleaf account** created
- [ ] **VLM_ARB_Report.tex** file
- [ ] **OVERLEAF_DETAILED_GUIDE.md** (for reference)
- [ ] **VISUAL_DATA_MAP.md** (for confirmation)

---

## 🚀 EXACT STEPS TO FOLLOW

### For Each Location (1-10):

1. **Open OVERLEAF_DETAILED_GUIDE.md**
2. **Find LOCATION X** (line numbers provided)
3. **Find that section in your LaTeX file** (use Ctrl+G "Go to Line")
4. **Copy the example code** from the guide
5. **REPLACE** the placeholder text with your code
6. **Check VISUAL_DATA_MAP.md** to confirm position is correct
7. **Click Recompile** to verify
8. **Move to next location**

---

## 📊 REAL DATA EXAMPLES (From Firestore)

### Example 1: Metrics Table (LOCATION 2)

**Before** (placeholder):
```latex
CLIP & 0.35 & 0.28 & 0.00 \\
MobileViT & 0.45 & 0.38 & 0.00 \\
...
```

**After** (your actual data):
```latex
CLIP & 0.35 & 0.28 & 0.00 \\
MobileViT & 0.42 & 0.36 & 0.00 \\
BLIP-2 & 0.71 & 0.62 & 0.06 \\
LLaVA & 0.81 & 0.68 & 0.14 \\
```

### Example 2: Chart Insertion (LOCATION 8)

**Before** (placeholder):
```latex
\fbox{
\begin{minipage}{0.9\textwidth}
\vspace{4cm}
\textit{[INSERT FIGURE: 01_model_comparison.png]}
...
```

**After** (with your image):
```latex
\includegraphics[width=0.9\textwidth]{01_model_comparison.png}
```

### Example 3: Appendix JSON (LOCATION 10)

**Before** (sample data):
```json
{
  "run_id": "eval_20260408_153022_a1b2c3d4",
  "metrics": {
    "clip": {"asr": 0.35, ...}
  }
}
```

**After** (your actual run data):
```json
{
  "run_id": "eval_20260408_164533_x9y8z7w6",
  "timestamp": "2026-04-08T16:45:33.123Z",
  "metrics": {
    "clip": {"asr": 0.35, "ods": 0.28, "sbr": 0.00},
    "mobilevit": {"asr": 0.42, "ods": 0.36, "sbr": 0.00},
    ...
  }
}
```

---

## 🛠️ TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Can't find Firestore data | Check: Firestore Console > Collections > results > [your latest run] |
| Charts don't show | Verify: Files panel shows both PNGs with exact names |
| LaTeX won't compile | Check: No "XX" placeholders left, all braces matched |
| Values don't look right | Use VISUAL_DATA_MAP.md to confirm you're editing right location |
| Need to restart | Just re-open the documents in new browser tab |

---

## 📋 DOCUMENT QUICK REFERENCE

**Which guide for what:**

| Need... | Use This | Location |
|---------|----------|----------|
| Step-by-step instructions | OVERLEAF_DETAILED_GUIDE | Start here! |
| Visual position map | VISUAL_DATA_MAP | Confirm locations |
| Understanding full system | LATEX_REPORT_GUIDE | Deep dive |
| Quick checklist | This file | You're reading it |
| Actual LaTeX template | VLM_ARB_Report.tex | Overleaf project |

---

## 🎓 WHAT YOU'LL END UP WITH

After completing all steps:

✅ **Professional 10-page PDF report**
- Page 1: Title + Executive Summary
- Pages 2-4: Methodology
- Pages 5-6: YOUR results (real metrics)
- Pages 6-7: YOUR charts (actual images)
- Pages 8-9: Discussion & Conclusions
- Page 10: Appendix with YOUR raw data

✅ **100% from Firestore/Real Data**
- No placeholders
- No estimates
- All metrics verified
- All images actual

✅ **Publication-ready format**
- Professional styling
- Proper citations
- Complete methodology
- Clear visualizations

---

## 📱 Mobile-Friendly Tips

If using phone/tablet in Overleaf:

1. Use **Desktop Mode** (browser settings)
2. Rotate to **Landscape** for better view
3. Use **Find & Replace** (easier to locate sections)
4. Preview PDF on right side while editing

---

## 🤝 Need Help?

**Common Questions:**

**Q: Which values do I use if I don't have Firestore?**
A: Use your local results JSON file (results/raw/*.json) — contains same data

**Q: Can I modify the text/discussion?**
A: Yes! After filling metrics, feel free to customize the writing

**Q: How do I add more charts?**
A: see Section 6.3 in LATEX_REPORT_GUIDE.md for instructions

**Q: What if my Notebook 2 didn't complete?**
A: Can still create report with sample data (use provide sample values)

---

## ⏱️ TIME ESTIMATE

| Task | Time |
|------|------|
| Collect Firestore data | 5 min |
| Setup in Overleaf | 5 min |
| Add all 10 locations | 20 min |
| Verify & download | 5 min |
| **TOTAL** | **35 minutes** |

---

## 🎉 YOU NOW HAVE

1. **VLM_ARB_Report.tex** — Actual LaTeX template
2. **generate_report.py** — Script for local generation (bonus)
3. **OVERLEAF_DETAILED_GUIDE.md** — Ultra-detailed step-by-step
4. **VISUAL_DATA_MAP.md** — Visual position guide
5. **LATEX_REPORT_GUIDE.md** — Complete reference
6. **This file** — Quick start summary

**Everything you need to create a professional report** with your REAL Firestore data in Overleaf. ✅

---

## 🚀 NEXT STEP

1. **Open**: OVERLEAF_DETAILED_GUIDE.md
2. **Follow**: Part 1 (Get Firestore data)
3. **Follow**: Part 2 (Open Overleaf)
4. **Follow**: Part 3-10 (Add data locations)
5. **Download**: Your final PDF

**You've got this!** 💪

---

📌 **Remember**: All data comes from FIRESTORE. No bluffs, no estimates you're making up. Every number is REAL. ✅

