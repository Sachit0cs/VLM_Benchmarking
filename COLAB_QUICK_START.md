# 🚀 Quick Start: Colab Tests → Local Reports

Get results from your Colab tests displayed locally in 3 simple steps.

---

## 3-Step Workflow

### Step 1️⃣: Export from Colab

**Add this as the LAST cell in your Colab notebook:**

```python
# 📤 Export results for local viewing
import sys
sys.path.insert(0, '/content/SemesterProject')
from scripts.export_colab_for_download import export_results

zip_file = export_results()
```

✓ Creates downloadable `colab_image_injection_results.zip` with all results

---

### Step 2️⃣: Import Results Locally

**After downloading the ZIP:**

```bash
cd ~/Documents/Development/Projects/SemesterProject

# Load the ZIP (auto-extracts & normalizes)
python scripts/load_colab_results.py --zip ~/Downloads/colab_image_injection_results.zip
```

✓ Creates `results/colab_imported/colab_results_normalized.json`

---

### Step 3️⃣: Generate & View Report

```bash
# Generate interactive HTML report
python scripts/generate_colab_report.py

# Open in browser
open results/colab_reports/report.html
```

✓ View metrics, tables, visualizations - all locally!

---

## 📦 What Gets Exported?

```
colab_image_injection_results.zip
├── colab_image_injection_results.json  (all test results & metrics)
├── attacked_images/                    (generated adversarial images)
└── test_images/                        (original test images)
```

---

## 🎯 Complete Example

```bash
# 1. Load Colab results
python scripts/load_colab_results.py --zip ~/Downloads/colab_results.zip
# ✓ Normalized: results/colab_imported/colab_results_normalized.json

# 2. Generate report
python scripts/generate_colab_report.py --input results/colab_imported
# ✓ Created: results/colab_reports/report.html

# 3. View instantly
open results/colab_reports/report.html
```

That's it! No re-running tests needed.

---

## 🔧 Advanced Options

### Load From Different Sources

```bash
# From JSON directly
python scripts/load_colab_results.py --json ~/Downloads/results.json

# From extracted folder
python scripts/load_colab_results.py --folder ~/Downloads/colab_export/
```

### Generate Different Report Formats

```bash
# HTML only (faster)
python scripts/generate_colab_report.py --format html

# PDF only (requires reportlab)
python scripts/generate_colab_report.py --format pdf

# Both HTML and PDF
python scripts/generate_colab_report.py --format both
```

### Custom Output Locations

```bash
python scripts/load_colab_results.py --zip colab_results.zip --output my_results/

python scripts/generate_colab_report.py --input my_results/ --output my_reports/
```

---

## 📊 What's in the Report?

- ✅ **Model Summary** - Which models were tested
- ✅ **Attack Success Rates** - ASR per model
- ✅ **Test Count** - How many tests per model
- ✅ **Average Metrics** - Overall performance
- ✅ **Timestamp** - When results were generated

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| ZIP not downloading from Colab | Check left sidebar "Files" panel, refresh |
| "File not found" error | Check path is correct: `~/Downloads/` not `/Downloads/` |
| Report shows no metrics | Click "Refresh" in VS Code's file explorer after loading |
| PDF generation fails | Install reportlab: `pip install reportlab` |

---

## 📚 See Also

- [COLAB_RESULTS_WORKFLOW.md](COLAB_RESULTS_WORKFLOW.md) - Detailed workflow guide
- [Colab Notebook](cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb) - Run tests here
- [image_injection_evaluator.py](evaluator/image_injection_evaluator.py) - Evaluation logic

---

**Next Step:** Go to your Colab notebook and add the export cell! 🚀
