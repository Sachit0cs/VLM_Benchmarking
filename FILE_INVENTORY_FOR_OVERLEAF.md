# 📁 COMPLETE FILE INVENTORY FOR OVERLEAF

All files available in your zip, ready to upload to Overleaf's Files panel.

---

## 🎯 PRIORITY CHARTS (Upload These First)

These are the most important charts for your main report:

### 1. Primary Evaluation Charts (MOST IMPORTANT)
```
eval_sample_20260407_183539_01_model_comparison.png
  → Shows: 3-panel comparison (ASR, ODS, SBR) for 4 models
  → Size: 97,210 bytes
  → Use: Section 6.1 - Model Comparison

eval_sample_20260407_183539_02_robustness_gap.png
  → Shows: Synthetic vs COCO robustness comparison
  → Size: 58,055 bytes
  → Use: Section 6.2 - Robustness Analysis
```

### 2. Threat Assessment Charts (HIGH PRIORITY)
```
eval_sample_20260407_193008_01_threat_assessment_4metrics.png
  → Shows: 4-metric threat assessment (ASR, ODS, SBR, CIMR)
  → Size: 173,833 bytes
  → Use: Section 7 - Threat Analysis

eval_sample_20260407_193008_02_cimr_threat_ranking.png
  → Shows: CIMR threat ranking visualization
  → Size: 67,561 bytes
  → Use: Section 7 - Critical Info Misrepresentation
```

### 3. Defense Benchmark Chart
```
defense_benchmark_chart_20260407_200758.png
  → Shows: Defense effectiveness comparison
  → Size: 51,446 bytes
  → Use: Section 8 - Defense Evaluation
```

---

## 📊 SUPPLEMENTARY CHARTS

### Typographic Evaluations
```
typographic_eval_20260407_211202_chart.png (118,569 bytes)
  → Latest typographic attack effectiveness

typographic_eval_20260407_190725_chart.png (102,069 bytes)
  → Previous typographic evaluation

typographic_eval_20260406_192123_chart.png (101,883 bytes)
  → Baseline typographic results
```

### Transferability Analysis
```
transferability_perturbation_20260407_201809.png (40,336 bytes)
  → Shows attack transferability across models
```

---

## 📈 DETAILED ANALYSIS PLOTS

### Perturbation Attack Analysis (10 Charts)
```
pertubations/plots/01_metric_comparison.png (97,210 bytes)
  → Metric comparison for perturbation attacks

pertubations/plots/02_risk_ranking.png (96,286 bytes)
  → Risk ranking of perturbation methods

pertubations/plots/03_robustness_scores.png (86,624 bytes)
  → Robustness scores per model

pertubations/plots/04_asr_ods_bubble.png (107,347 bytes)
  → ASR vs ODS bubble chart

pertubations/plots/05_metric_heatmap.png (144,059 bytes)
  → Heatmap of all metrics

pertubations/plots/06_correlation_heatmap.png (101,667 bytes)
  → Correlation analysis

pertubations/plots/07_radar_profiles.png (254,153 bytes)
  → Radar chart of model profiles

pertubations/plots/08_parallel_coordinates.png (259,304 bytes)
  → Parallel coordinates visualization

pertubations/plots/09_projected_events.png (103,026 bytes)
  → Event projection analysis

pertubations/plots/10_gap_to_best.png (60,636 bytes)
  → Performance gap to best model
```

### Patch Attack Analysis (10 Charts)
```
patch/plots/01_metric_comparison.png (82,395 bytes)
  → Metric comparison for patch attacks

patch/plots/02_risk_ranking.png (96,305 bytes)
  → Risk ranking of patch methods

patch/plots/03_robustness_scores.png (86,636 bytes)
  → Robustness scores against patches

patch/plots/04_asr_ods_bubble.png (113,871 bytes)
  → ASR vs ODS for patches

patch/plots/05_metric_heatmap.png (147,486 bytes)
  → Metric heatmap for patches

patch/plots/06_correlation_heatmap.png (83,348 bytes)
  → Correlation in patch results

patch/plots/07_radar_profiles.png (206,041 bytes)
  → Radar profiles for patches

patch/plots/08_parallel_coordinates.png (227,841 bytes)
  → Parallel coordinates for patches

patch/plots/09_projected_events.png (105,645 bytes)
  → Event projection for patches

patch/plots/10_gap_to_best.png (59,064 bytes)
  → Gap analysis for patches
```

---

## 📄 SUPPORTING DOCUMENTS

### Data Files (JSON)
```
reports/eval_sample_20260407_183539_results.json
  → Primary evaluation results (ASR, ODS, SBR, CIMR)
  → Include in: Appendix A - Raw Data

reports/eval_sample_20260407_193008_threat_analysis.json
  → Threat analysis results
  → Include in: Appendix B - Threat Data

reports/pertubations/eval_perturb_20260407_173401_metrics.json
  → Perturbation evaluation metrics
  → Include in: Appendix C - Perturbation Data

reports/patch/eval_patch_20260407_194711_metrics.json
  → Patch evaluation metrics
  → Include in: Appendix D - Patch Data

reports/defense_benchmark_20260407_200758.json
  → Defense benchmark results
  → Include in: Appendix E - Defense Data

reports/transferability_matrices_20260407_201809.json
  → Transferability analysis
  → Include in: Appendix F - Transferability Data
```

### CSV Files (For Tables)
```
reports/defense_benchmark_20260407_200758.csv
  → Defense benchmark summary

reports/pertubations/eval_perturb_20260407_173401_metrics_report_20260407_232034_summary.csv
  → Perturbation summary

reports/patch/eval_patch_20260407_194711_detailed_patch_report_summary.csv
  → Patch attack summary
```

### Report PDFs
```
reports/typographic_eval_20260407_211202_robustness_report.pdf
  → Typographic robustness analysis

reports/typographic_eval_20260407_190725_typographic_report.pdf
  → Typographic evaluation detailed report

reports/pertubations/eval_perturb_20260407_173401_metrics_report_20260407_232253.pdf
  → Perturbation metrics detailed report

reports/patch/eval_patch_20260407_194711_detailed_patch_report.pdf
  → Patch attack detailed report
```

---

## ✅ HOW TO USE THIS INVENTORY IN OVERLEAF

### Step 1: Upload Priority Charts (5 minutes)
1. Go to Overleaf → Your Project → Files panel
2. Click "Upload Files"
3. Upload these 5 files:
   - `eval_sample_20260407_183539_01_model_comparison.png`
   - `eval_sample_20260407_183539_02_robustness_gap.png`
   - `eval_sample_20260407_193008_01_threat_assessment_4metrics.png`
   - `eval_sample_20260407_193008_02_cimr_threat_ranking.png`
   - `defense_benchmark_chart_20260407_200758.png`

### Step 2: Add to Your LaTeX Document
```latex
% Section 6.1 - Model Comparison
\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{eval_sample_20260407_183539_01_model_comparison.png}
\caption{ASR, ODS, and SBR comparison across four VLMs.}
\label{fig:model_comparison}
\end{figure}

% Section 6.2 - Robustness Gap
\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{eval_sample_20260407_183539_02_robustness_gap.png}
\caption{Robustness gap between synthetic and real-world COCO images.}
\label{fig:robustness_gap}
\end{figure}

% Section 7 - Threat Assessment
\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{eval_sample_20260407_193008_01_threat_assessment_4metrics.png}
\caption{Four-metric threat assessment including CIMR.}
\label{fig:threat_assessment}
\end{figure}

% Section 7 - CIMR Ranking
\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{eval_sample_20260407_193008_02_cimr_threat_ranking.png}
\caption{Critical Information Misrepresentation Rate ranking.}
\label{fig:cimr_ranking}
\end{figure}

% Section 8 - Defense
\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{defense_benchmark_chart_20260407_200758.png}
\caption{Defense effectiveness against various attack types.}
\label{fig:defense_benchmark}
\end{figure}
```

### Step 3: Upload Supplementary Charts (Optional, 5 minutes)
- For appendix sections with more detailed analysis
- Typographic charts (3 files)
- Perturbation plots (10 files)
- Patch plots (10 files)

### Step 4: Add Appendices with JSON Data
```latex
\appendix

\section{Raw Evaluation Results}
\label{app:raw_results}

\subsection{Primary Evaluation}
\begin{verbatim}
{
  "run_id": "eval_sample_20260407_183539",
  "timestamp": "2026-04-07T18:35:42.474570",
  "metrics": {
    "clip": {"asr": 0.35, "ods": 0.28, "sbr": 0.0},
    "mobilevit": {"asr": 0.45, "ods": 0.38, "sbr": 0.0},
    "blip2": {"asr": 0.68, "ods": 0.58, "sbr": 0.05},
    "llava": {"asr": 0.78, "ods": 0.65, "sbr": 0.12}
  }
}
\end{verbatim}

\subsection{Threat Analysis}
\begin{verbatim}
{
  "run_id": "eval_sample_20260407_193008",
  "data": {
    "clip": {"asr": 0.35, "ods": 0.28, "sbr": 0.0, "cimr": 0.15},
    "mobilevit": {"asr": 0.45, "ods": 0.38, "sbr": 0.0, "cimr": 0.25},
    "blip2": {"asr": 0.68, "ods": 0.58, "sbr": 0.05, "cimr": 0.42},
    "llava": {"asr": 0.78, "ods": 0.65, "sbr": 0.12, "cimr": 0.48}
  }
}
\end{verbatim}
```

---

## 📊 TOTAL FILES AVAILABLE

```
Primary Charts (5):        5 files   ~500 KB
Typographic Charts (3):    3 files   ~320 KB
Detailed Plots (20):      20 files   ~2.1 MB
Supporting PDFs (4):       4 files   ~1.8 MB
JSON Data (6):            6 files   ~10 KB
CSV Files (3):            3 files   ~3 KB
─────────────────────────────────────────────
TOTAL:                    41 files   ~4.7 MB
```

---

## 🎯 RECOMMENDED FILE ORGANIZATION IN OVERLEAF

```
Overleaf Project Files
│
├─ Main Document
│  └─ main.tex (or VLM_ARB_Report.tex)
│
├─ Primary Figures (ESSENTIAL)
│  ├─ eval_sample_20260407_183539_01_model_comparison.png
│  ├─ eval_sample_20260407_183539_02_robustness_gap.png
│  ├─ eval_sample_20260407_193008_01_threat_assessment_4metrics.png
│  ├─ eval_sample_20260407_193008_02_cimr_threat_ranking.png
│  └─ defense_benchmark_chart_20260407_200758.png
│
├─ Supplementary Figures (OPTIONAL)
│  ├─ typographic/
│  ├─ perturbations/plots/
│  └─ patch/plots/
│
└─ Appendix Data
   ├─ eval_sample_20260407_183539_results.json
   ├─ eval_sample_20260407_193008_threat_analysis.json
   └─ [other supporting JSON files]
```

---

## ✨ QUICK COPY-PASTE READY

### Filename List for Quick Reference

**5 Main Charts to Upload:**
1. `eval_sample_20260407_183539_01_model_comparison.png`
2. `eval_sample_20260407_183539_02_robustness_gap.png`
3. `eval_sample_20260407_193008_01_threat_assessment_4metrics.png`
4. `eval_sample_20260407_193008_02_cimr_threat_ranking.png`
5. `defense_benchmark_chart_20260407_200758.png`

---

## 🚀 NEXT STEP

1. Extract the zip file completely
2. Copy these file names
3. Access Overleaf Files panel
4. Upload the 5 priority charts
5. Use the LaTeX code snippets above in your document
6. Click Recompile!

**All files are REAL data from your zip. No generation, no estimation. Just data from your actual evaluations.** ✅

