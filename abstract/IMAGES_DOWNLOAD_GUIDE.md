# 📊 VLM-ARB Typographic Attack Visualizations - Download Guide

## ✅ All 5 Images Created Successfully

All visualization PNG files have been generated and are ready to download for your Prism LaTeX compilation.

---

## 📍 **File Location**
```
/Users/pratyushbhaskar/Developer/VLM_Benchmarking/abstract/
```

---

## 📋 **Image Files Ready for Download**

### 1. **typographic_model_comparison.png** (307 KB)
- **Description**: Three-panel comparison of ASR, CDS, and MRS across 5 models
- **Content**: Bar charts showing CLIP robustness vs. performance degradation
- **Use in LaTeX**: Figures 6 in your report (Section: Typographic Overlay Visualization)

### 2. **typographic_confidence_analysis.png** (169 KB)
- **Description**: Confidence stability analysis comparing original vs. poisoned images
- **Content**: Side-by-side bar charts with percentage change annotations
- **Use in LaTeX**: Figure 7 (confidence degradation patterns and model resilience)

### 3. **cross_attack_vulnerability.png** (150 KB)
- **Description**: Heatmap showing ASR values for Prompt Injection vs. Typographic Overlay
- **Content**: Color-coded matrix across 6 models with N/A for inapplicable combinations
- **Use in LaTeX**: Figure 8 (cross-attack comparison)
- **Key insight**: CLIP dominates both attack types; different models show distinct vulnerabilities

### 4. **typographic_mrs_ranking.png** (166 KB)
- **Description**: Horizontal bar chart ranking models by MRS with risk level indicators
- **Content**: Color-coded ranking (Green=Low Risk, Yellow=Moderate, Red=High, Dark Red=Critical)
- **Use in LaTeX**: Figure 9 (robustness ranking and deployment risk assessment)

### 5. **typographic_synthetic_vs_real.png** (220 KB)
- **Description**: Comparative analysis of synthetic vs. real-world (COCO) robustness gaps
- **Content**: Left panel shows ASR comparison, right panel shows relative improvement percentages
- **Use in LaTeX**: Figure 10 (validation that real-world robustness is better than synthetic)

---

## 🚀 **Steps to Download and Use**

### **Option 1: Direct Download from VS Code**
1. Open the File Explorer in VS Code
2. Navigate to: `VLM_Benchmarking/abstract/`
3. Select all 5 `typographic_*.png` files
4. Right-click → "Reveal in Finder"
5. Download/copy to your Prism folder

### **Option 2: Terminal One-Liner**
```bash
cp /Users/pratyushbhaskar/Developer/VLM_Benchmarking/abstract/typographic_*.png ~/Downloads/
```

### **Option 3: Prism Upload**
1. Log into Prism
2. Go to your project → Media/Resources
3. Upload all 5 PNG files
4. Copy the file paths provided by Prism
5. Update your LaTeX `\includegraphics` paths if needed

---

## 🔍 **LaTeX Integration Checklist**

Your LaTeX document already includes these figures. Just ensure:

✅ All 5 PNG files are in the same directory as your `.tex` file  
✅ File references use correct paths:
```latex
\includegraphics[width=0.95\textwidth]{typographic_model_comparison.png}
\includegraphics[width=0.95\textwidth]{typographic_confidence_analysis.png}
\includegraphics[width=0.95\textwidth]{cross_attack_vulnerability.png}
\includegraphics[width=0.95\textwidth]{typographic_mrs_ranking.png}
\includegraphics[width=0.95\textwidth]{typographic_synthetic_vs_real.png}
```

✅ Run pdflatex twice for proper TOC/references:
```bash
pdflatex VLM_ARB_Report_CLEAN.tex
pdflatex VLM_ARB_Report_CLEAN.tex
```

---

## 📊 **Image Properties**

| File | Size | DPI | Format | Color Profile |
|------|------|-----|--------|--------------|
| typographic_model_comparison.png | 307 KB | 300 | PNG (RGB) | sRGB |
| typographic_confidence_analysis.png | 169 KB | 300 | PNG (RGB) | sRGB |
| cross_attack_vulnerability.png | 150 KB | 300 | PNG (RGB) | sRGB |
| typographic_mrs_ranking.png | 166 KB | 300 | PNG (RGB) | sRGB |
| typographic_synthetic_vs_real.png | 220 KB | 300 | PNG (RGB) | sRGB |

**Total Size**: ~1 MB (compressed, high quality for printing)

---

## ✨ **What Each Visualization Shows**

### Model Comparison
- CLIP: ASR=0.28 (Low risk) ✅
- MobileNet: ASR=0.46 (Moderate)
- DeiT-Tiny: ASR=0.62 (Critical)
- MobileViT: ASR=0.75 (High)
- ResNet18: ASR=0.74 (High)

### Key Finding from Visualizations
**Vision-language alignment (CLIP) provides 2.6x better robustness than pure vision models against visible text overlays.**

---

## 🛠️ **Troubleshooting**

**Q: Images not showing in pdflatex?**  
A: Ensure `graphicx` package is loaded: `\usepackage{graphicx}`

**Q: Images appear blurry?**  
A: All images are 300 DPI - they're high quality. Check your PDF viewer zoom.

**Q: File paths giving errors?**  
A: Use relative paths if images are in same directory:
```latex
\includegraphics[width=0.95\textwidth]{typographic_model_comparison.png}
```

---

## 📝 **Next Steps**

1. ✅ Download all 5 PNG files from `/abstract/`
2. ✅ Upload to Prism
3. ✅ Update LaTeX document if needed
4. ✅ Run `pdflatex` twice
5. ✅ Verify all figures render correctly in PDF
6. ✅ Download final PDF from Prism

---

**Created:** April 8, 2026  
**Data Source:** VLM-ARB Typographic Evaluation (118 images, 5 models)  
**Report:** VLM_ARB_Report_CLEAN.tex (production-ready)
