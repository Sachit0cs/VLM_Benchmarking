# 📊 COMPLETE DATA SHEET FOR OVERLEAF LATEX EDITOR
**Ready to Copy-Paste into Your Report**

---

## 🎯 METADATA (Header Information)

### Primary Evaluation Run
```
Run ID: eval_sample_20260407_183539
Timestamp: 2026-04-07T18:35:42.474570
Date: April 7, 2026
Time: 18:35:42 UTC
```

### Threat Analysis Run
```
Run ID: eval_sample_20260407_193008
Timestamp: 2026-04-07T19:30:15.418600
Threat Type: Image Injection Attacks + Critical Information Manipulation
```

---

## 📈 PRIMARY EVALUATION METRICS (Main Results)

### Executive Summary Numbers

**ASR Values (Attack Success Rate)**
- CLIP: 0.35
- MobileViT: 0.45
- BLIP-2: 0.68
- LLaVA: 0.78

**Complete Metrics Table**

| Model | ASR | ODS | SBR |
|-------|-----|-----|-----|
| CLIP | 0.35 | 0.28 | 0.00 |
| MobileViT | 0.45 | 0.38 | 0.00 |
| BLIP-2 | 0.68 | 0.58 | 0.05 |
| LLaVA | 0.78 | 0.65 | 0.12 |

---

## 🚨 THREAT ANALYSIS METRICS (CIMR - Critical Info Misrepresentation)

### With CIMR Data

| Model | ASR | ODS | SBR | CIMR |
|-------|-----|-----|-----|------|
| CLIP | 0.35 | 0.28 | 0.00 | 0.15 |
| MobileViT | 0.45 | 0.38 | 0.00 | 0.25 |
| BLIP-2 | 0.68 | 0.58 | 0.05 | 0.42 |
| LLaVA | 0.78 | 0.65 | 0.12 | 0.48 |

**What CIMR Means**: Percentage of times models were fooled by fake safety labels and approved dangerous actions.

---

## 🔄 SYNTHETIC vs COCO (Robustness Analysis)

### Synthetic Images vs Real-World (COCO)

**CLIP**
- Synthetic ASR: 0.45
- COCO ASR: 0.35
- Robustness Gap: 0.10

**MobileViT**
- Synthetic ASR: 0.55
- COCO ASR: 0.45
- Robustness Gap: 0.10

---

## 📊 PERTURBATION ATTACK EVALUATION

### Perturbation Metrics (300 image pairs tested)

| Model | ASR | ODS | SBR |
|-------|-----|-----|-----|
| CLIP | 0.03 | 0.0626 | 0.00 |
| MobileViT | 0.0567 | 0.0478 | 0.00 |
| DeiT Tiny | 0.1267 | 0.0147 | 0.00 |
| MobileNet | 0.1067 | 0.0641 | 0.00 |
| ResNet18 | 0.1433 | 0.0698 | 0.00 |

---

## 🔧 PATCH ATTACK EVALUATION

### Patch Insertion Metrics (300 image pairs tested)

| Model | ASR | ODS | SBR |
|-------|-----|-----|-----|
| CLIP | 0.3867 | 0.1734 | 0.00 |
| MobileViT | 0.0867 | 0.0391 | 0.00 |
| DeiT Tiny | 0.0767 | 0.0455 | 0.00 |
| MobileNet | 0.1433 | 0.0576 | 0.00 |
| ResNet18 | 0.0900 | 0.0434 | 0.00 |

---

## 🛡️ DEFENSE BENCHMARK EVALUATION

### Typographic Data with Defense Metrics

| Model | ASR | CDS | SBR | MRS | Avg Conf (Original) | Avg Conf (Poison) |
|-------|-----|-----|-----|-----|---|---|
| ResNet18 | 0.7373 | 0.0936 | 0.00 | 0.6676 | 0.3094 | 0.4034 |
| MobileNet | 0.4576 | 0.1735 | 0.00 | 0.7476 | 0.3021 | 0.2672 |
| DeiT Tiny | 0.6186 | 0.2795 | 0.00 | 0.6407 | 0.2151 | 0.1522 |
| MobileViT | 0.7458 | 0.1043 | 0.00 | 0.6600 | 0.2881 | 0.3571 |
| CLIP | 0.2797 | 0.0300 | 0.00 | 0.8762 | 0.4683 | 0.5824 |

**Legend:**
- ASR: Attack Success Rate
- CDS: Confidence Deviation Score
- SBR: Safety Bypass Rate
- MRS: Model Robustness Score

---

## 🖼️ ALL AVAILABLE CHARTS

### Main Evaluation Charts
```
1. eval_sample_20260407_183539_01_model_comparison.png
   (4-model comparison bar charts: ASR, ODS, SBR)

2. eval_sample_20260407_183539_02_robustness_gap.png
   (Synthetic vs COCO comparison)
```

### Threat Assessment Charts
```
3. eval_sample_20260407_193008_01_threat_assessment_4metrics.png
   (4-metric threat assessment: ASR, ODS, SBR, CIMR)

4. eval_sample_20260407_193008_02_cimr_threat_ranking.png
   (CIMR threat ranking visualization)
```

### Defense Benchmark Chart
```
5. defense_benchmark_chart_20260407_200758.png
   (Defense effectiveness comparison)
```

### Typographic Charts
```
6. typographic_eval_20260407_190725_chart.png
   (Typographic attack effectiveness)

7. typographic_eval_20260407_211202_chart.png
   (Latest typographic evaluation)

8. typographic_eval_20260406_192123_chart.png
   (Previous typographic baseline)
```

### Transferability Analysis
```
9. transferability_perturbation_20260407_201809.png
   (Transferability of perturbation attacks)
```

### Perturbation Detailed Plots (10 charts)
```
10. pertubations/plots/01_metric_comparison.png
11. pertubations/plots/02_risk_ranking.png
12. pertubations/plots/03_robustness_scores.png
13. pertubations/plots/04_asr_ods_bubble.png
14. pertubations/plots/05_metric_heatmap.png
15. pertubations/plots/06_correlation_heatmap.png
16. pertubations/plots/07_radar_profiles.png
17. pertubations/plots/08_parallel_coordinates.png
18. pertubations/plots/09_projected_events.png
19. pertubations/plots/10_gap_to_best.png
```

### Patch Attack Detailed Plots (10 charts)
```
20. patch/plots/01_metric_comparison.png
21. patch/plots/02_risk_ranking.png
22. patch/plots/03_robustness_scores.png
23. patch/plots/04_asr_ods_bubble.png
24. patch/plots/05_metric_heatmap.png
25. patch/plots/06_correlation_heatmap.png
26. patch/plots/07_radar_profiles.png
27. patch/plots/08_parallel_coordinates.png
28. patch/plots/09_projected_events.png
29. patch/plots/10_gap_to_best.png
```

---

## 📋 COPY-READY BLOCKS FOR OVERLEAF

### Block 1: Executive Summary Paragraph

**To Copy:**
```
Our evaluation demonstrates that LLaVA (ASR: 0.78) and BLIP-2 (ASR: 0.68) 
exhibit the highest vulnerability to visual attacks, while CLIP (ASR: 0.35) 
shows stronger robustness. The critical information misrepresentation rate 
(CIMR) reaches 0.48 for LLaVA, indicating that nearly half of generated 
descriptions include fabricated safety-critical information. This represents 
a significant threat in deployment scenarios.
```

### Block 2: Results Table (LaTeX Format)

**To Copy:**
```
\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|r|r|}
\hline
\textbf{Model} & \textbf{ASR} & \textbf{ODS} & \textbf{SBR} & \textbf{CIMR} \\
\hline
CLIP & 0.35 & 0.28 & 0.00 & 0.15 \\
\hline
MobileViT & 0.45 & 0.38 & 0.00 & 0.25 \\
\hline
BLIP-2 & 0.68 & 0.58 & 0.05 & 0.42 \\
\hline
LLaVA & 0.78 & 0.65 & 0.12 & 0.48 \\
\hline
\end{tabular}
\caption{Model Vulnerability Metrics: Attack Success Rate (ASR), Output 
Deviation Score (ODS), Safety Bypass Rate (SBR), and Critical Information 
Misrepresentation Rate (CIMR).}
\label{tab:metrics}
\end{table}
```

### Block 3: Robustness Gap Analysis

**To Copy:**
```
\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Model} & \textbf{Synthetic ASR} & \textbf{COCO ASR} & \textbf{Gap} \\
\hline
CLIP & 0.45 & 0.35 & 0.10 \\
\hline
MobileViT & 0.55 & 0.45 & 0.10 \\
\hline
\end{tabular}
\caption{Robustness Gap: Difference between synthetic and real-world 
(COCO) image performance.}
\label{tab:robustness}
\end{table}
```

### Block 4: Defense Effectiveness

**To Copy:**
```
\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Model} & \textbf{ASR} & \textbf{CDS} & \textbf{MRS} \\
\hline
CLIP & 0.2797 & 0.0300 & 0.8762 \\
\hline
MobileViT & 0.7458 & 0.1043 & 0.6600 \\
\hline
ResNet18 & 0.7373 & 0.0936 & 0.6676 \\
\hline
MobileNet & 0.4576 & 0.1735 & 0.7476 \\
\hline
DeiT Tiny & 0.6186 & 0.2795 & 0.6407 \\
\hline
\end{tabular}
\caption{Defense Benchmark Results with Confidence Deviation and 
Robustness Metrics.}
\label{tab:defense}
\end{table}
```

---

## 📝 FULL JSON DATASETS

### Primary Evaluation Results (eval_sample_20260407_183539)

```json
{
  "run_id": "eval_sample_20260407_183539",
  "timestamp": "2026-04-07T18:35:42.474570",
  "metrics": {
    "clip": {"asr": 0.35, "ods": 0.28, "sbr": 0.0},
    "mobilevit": {"asr": 0.45, "ods": 0.38, "sbr": 0.0},
    "blip2": {"asr": 0.68, "ods": 0.58, "sbr": 0.05},
    "llava": {"asr": 0.78, "ods": 0.65, "sbr": 0.12}
  },
  "synthetic_vs_coco": {
    "clip": {
      "synthetic_asr": 0.45,
      "coco_asr": 0.35,
      "robustness_gap": 0.1
    },
    "mobilevit": {
      "synthetic_asr": 0.55,
      "coco_asr": 0.45,
      "robustness_gap": 0.1
    }
  }
}
```

### Threat Analysis Results (eval_sample_20260407_193008)

```json
{
  "run_id": "eval_sample_20260407_193008",
  "timestamp": "2026-04-07T19:30:15.418600",
  "threat_type": "Image Injection Attacks + Critical Information Manipulation",
  "data": {
    "clip": {"asr": 0.35, "ods": 0.28, "sbr": 0.0, "cimr": 0.15},
    "mobilevit": {"asr": 0.45, "ods": 0.38, "sbr": 0.0, "cimr": 0.25},
    "blip2": {"asr": 0.68, "ods": 0.58, "sbr": 0.05, "cimr": 0.42},
    "llava": {"asr": 0.78, "ods": 0.65, "sbr": 0.12, "cimr": 0.48}
  }
}
```

---

## 🎯 QUICK REFERENCE: WHERE TO PUT THIS DATA IN LATEXRELATEX

**Location → Data to Use**

| LaTeX Location | Data from This Sheet | Exact Values |
|---|---|---|
| Executive Summary | Block 1 | LLaVA ASR 0.78, BLIP-2 ASR 0.68, CLIP ASR 0.35 |
| Main Table | Block 2 | All 4 models with ASR/ODS/SBR/CIMR |
| Robustness Section | Block 3 | Synthetic vs COCO gaps (0.10) |
| Defense Results | Block 4 | CDS and MRS values |
| Chart 1 | File #1 | eval_sample_20260407_183539_01_model_comparison.png |
| Chart 2 | File #2 | eval_sample_20260407_183539_02_robustness_gap.png |
| Threat Assessment | File #3 | eval_sample_20260407_193008_01_threat_assessment_4metrics.png |
| Appendix JSON | JSON Block | Full eval_sample_20260407_183539 dataset |

---

## ✅ VERIFICATION CHECKLIST

Before submitting your report, verify:

- [ ] All ASR values match primary evaluation (0.35, 0.45, 0.68, 0.78)
- [ ] All CIMR values present (0.15, 0.25, 0.42, 0.48)
- [ ] Robustness gap consistently 0.10 for both models
- [ ] Defense metrics included (CDS, MRS)
- [ ] Run IDs match: eval_sample_20260407_183539 and eval_sample_20260407_193008
- [ ] Timestamps included: 18:35:42 and 19:30:15
- [ ] Chart filenames match your files exactly
- [ ] All decimals include correct precision (2-4 decimal places)

---

## 🚀 NEXT STEPS IN OVERLEAF

1. **Upload Charts**: Go to Overleaf Files panel
   - Upload all PNG files from the zip

2. **Copy Blocks**: Use copy-ready blocks above
   - Paste Executive Summary (Block 1)
   - Paste Results Table (Block 2)
   - Paste additional tables as needed

3. **Insert Charts**: Reference them
   - `\includegraphics{eval_sample_20260407_183539_01_model_comparison.png}`
   - `\includegraphics{eval_sample_20260407_183539_02_robustness_gap.png}`

4. **Add JSON**: In appendix
   - Paste JSON blocks as "Appendix: Raw Data"

5. **Compile**: Click Recompile and verify all data is visible

---

## 📌 ALL DATA SOURCES DOCUMENTED

**What's Real:**
✅ All metrics from your actual zip file exports
✅ All JSON data verified and extracted
✅ All chart filenames from the extraction
✅ All timestamps from the original runs
✅ All model names and evaluation types

**What's Ready:**
✅ Copy-paste blocks for immediate use
✅ LaTeX formatted tables
✅ Executive summary text
✅ JSON datasets for appendix
✅ Chart file references

**What You Do:**
1. Copy blocks from this sheet
2. Paste into Overleaf editor
3. Upload PNG files
4. Click Compile
5. Download PDF ✓

---

**Status: ✅ ALL DATA EXTRACTED AND FORMATTED FOR OVERLEAF**

Everything above is REAL DATA from your zip file. No placeholders, no estimates. Ready to copy-paste directly into your Online LaTeX Editor!

