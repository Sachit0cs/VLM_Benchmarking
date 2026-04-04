# 🔄 Colab → Local Results Workflow

How to run tests on Colab and view results locally.

---

## 🔗 Workflow: Two-Way Bridge

```
COLAB NOTEBOOK                   LOCAL DEVELOPMENT
    │                                   │
    ├─→ Run Tests                       │
    │   - CLIP, LLaVA, BLIP-2           │
    │   - Attacked images               │
    │   - Metrics computation           │
    │                                   │
    ├─→ Export Results                  │
    │   (to JSON + ZIP)                 │
    │                                   │
    ├─→ Download ZIP                    │
    │   (Files app or wget)             │
    │                                   │
    └──────────────────────────────────>│
                                        │
                                ├─→ Load Results
                                │   python load_colab_results.py
                                │
                                ├─→ Generate Reports
                                │   python generate_colab_report.py
                                │
                                └─→ View Locally
                                    (HTML/PDF)
```

---

## 📋 Step-by-Step

### Step 1: Run Tests on Colab

1. Open [ImageInjection_MultiModel_Cloud.ipynb](cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb)
2. Run cells up to test completion
3. **Last cell exports results automatically**

### Step 2: Export Results (Colab)

Add this as the **final cell** in Colab notebook:

```python
# Export results for local import
import sys
sys.path.insert(0, '/content/SemesterProject')
from scripts.export_colab_for_download import export_results

zip_file = export_results()
print(f"\n✅ Download this file: {zip_file}")
```

This creates a ZIP with:
- `colab_image_injection_results.json` - All metrics & test outputs
- `attacked_images/` - Generated adversarial images
- `test_images/` - Original test images

### Step 3: Download Results

In Colab, the ZIP file appears in the Files panel on the left. Click the download icon.

Or from command line:
```bash
# If you know the Colab runtime ID
wget https://colab.research.google.com/files/... -O colab_results.zip
```

### Step 4: Import Results Locally

```bash
# Option A: From ZIP file
python scripts/load_colab_results.py --zip ~/Downloads/colab_results.zip

# Option B: From folder
python scripts/load_colab_results.py --folder ~/Downloads/colab_export/

# Option C: Direct JSON
python scripts/load_colab_results.py --json ~/Downloads/colab_results.json
```

**Output:** Creates `results/colab_imported/colab_results_normalized.json`

### Step 5: Generate Report Locally

Once results are loaded:

```bash
python scripts/generate_colab_report.py --input results/colab_imported/colab_results_normalized.json
```

Creates:
- `results/colab_reports/report.html` - Interactive dashboard
- `results/colab_reports/report.pdf` - Printable PDF

---

## 🎯 Key Features

| Feature | Details |
|---------|---------|
| **No Manual Transfer** | Automatic ZIP export from Colab |
| **Local Analysis** | Full report generation without re-running tests |
| **Preserved Images** | Test & attacked images included |
| **Metrics Tracking** | ASR, SBR, Transferability scores |
| **Comparison Ready** | Format supports multi-run analysis |

---

## 🔧 Troubleshooting

**Q: Colab export not showing?**
- Add the export cell at the very end
- Click "Refresh" in Files panel (left sidebar)

**Q: ZIP too large?**
- Remove images: `python load_colab_results.py --json colab_results.json` (JSON only)
- Use cloud storage: Export to Google Drive instead

**Q: Results not loading locally?**
- Check file is valid JSON: `python -c "import json; json.load(open('file.json'))"`
- Try `--json` option explicitly if folder extraction fails

---

## 📊 Example Usage

```bash
# Workflow:
cd ~/Documents/Development/Projects/SemesterProject

# 1. After downloading from Colab
python scripts/load_colab_results.py --zip ~/Downloads/colab_results.zip

# 2. Generate report
python scripts/generate_colab_report.py

# 3. View
open results/colab_reports/report.html
```

---

## 💡 Pro Tips

- **Keep results**: Results stored in `results/colab_imported/` for future reference
- **Batch runs**: Download multiple Colab runs and compare them
- **Version tracking**: Colab results include timestamp for versioning
- **CI/CD ready**: Can integrate into automated reporting pipeline

---

## 📚 Related Files

- [ImageInjection_MultiModel_Cloud.ipynb](cloud/notebooks/ImageInjection_MultiModel_Cloud.ipynb) - Colab notebook
- [load_colab_results.py](scripts/load_colab_results.py) - Local importer
- [generate_colab_report.py](scripts/generate_colab_report.py) - Report generator
- [image_injection_evaluator.py](evaluator/image_injection_evaluator.py) - Evaluation class
