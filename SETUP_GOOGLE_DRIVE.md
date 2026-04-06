# VLM-ARB with Google Drive (Simplified Setup)

**Updated setup: Uses Google Drive for file storage + Firestore for metrics (optional)**

No Cloud Storage buckets needed. Just Google Drive folders!

---

## Setup (One-time by team lead) - 10 min

### 1. Create Google Drive Folder Structure

```
Google Drive → New Folder → "VLM-ARB-Team"
├─ datasets/
│  ├─ base_images/      (← Notebook 1 will save here)
│  └─ attacked_images/  (← Notebook 1 will save here)
├─ reports/             (← Notebook 3 will save here)
├─ secrets/             (← Optional: Firebase credentials)
└─ notebooks/           (← Copy 3 notebooks here)
```

### 2. (Optional) Setup Firebase for Metrics Logging

If you want real-time metrics tracking:

```
1. Go to https://console.firebase.google.com
2. Create project "VLM-ARB"
3. Create Firestore database (free tier)
4. Go to Project Settings → Service Accounts → Generate Key (JSON)
5. Save to Drive/VLM-ARB-Team/secrets/serviceAccountKey.json
```

**↪ Skip this if you only want results saved locally**

### 3. Share Folder with Team

```
1. Right-click VLM-ARB-Team folder
2. Share → Add team members
3. Give "Edit" access
```

---

## Usage (Team members)

### Run Notebook 1: Generate Datasets (First person, ~10 min)

```colab
1. https://colab.research.google.com
2. File → Open Notebook → Upload from computer
3. Select Notebook_1_Generate_Datasets.ipynb
4. Run all cells (Cell → Run All)

✅ Expected output:
   - Base images saved to Drive/VLM-ARB-Team/datasets/base_images/
   - Attack variants saved to Drive/VLM-ARB-Team/datasets/attacked_images/
   - (Optional) Metadata logged to Firestore
```

### Run Notebook 2: Evaluate Models (Anyone, ~30 min)

```colab
1. Open Notebook_2_Run_Model_Evaluations.ipynb
2. Run all cells

✅ Expected output:
   - CLIP model loads and runs inference
   - Results computed (ASR, ODS, SBR scores)
   - (Optional) Metrics logged to Firestore

💡 Can run simultaneously - each person gets unique run_id
```

### Run Notebook 3: Generate Reports (Anyone, ~10 min)

```colab
1. Open Notebook_3_Generate_Reports.ipynb
2. Run all cells

✅ Expected output:
   - PDF report
   - PNG comparison chart
   - JSON results
   - All saved to Drive/VLM-ARB-Team/reports/

🔗 To share: Right-click PDF → Share → Copy link
```

---

## File Storage Map

```
Google Drive (Your Team)
│
├─ datasets/
│  ├─ base_images/        ← Where Notebook 1 saves synthetic images
│  └─ attacked_images/    ← Where Notebook 1 saves attack variants
│                            (Read by Notebook 2)
│
├─ reports/
│  ├─ eval_20240406_120130_results.json
│  ├─ eval_20240406_120130_report.pdf
│  └─ eval_20240406_120130_chart.png
│                            (Written by Notebook 3)
│                            (Share these with team!)
│
└─ secrets/
   └─ serviceAccountKey.json  (Optional: for Firebase)
```

---

## Real-time Results Tracking (Optional)

If you set up Firebase in Step 2:

1. Open Firestore Console: https://console.firebase.google.com
2. Go to database → `results` collection
3. While Notebook 2 is running, refresh to see metrics appear
4. Each run gets a document with `{run_id}` name

**If you skip Firebase**: Results are still saved locally, just not real-time synced.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Google Drive not mounted" | Cell 2 should auto-mount. If not: run `from google.colab import drive; drive.mount('/content/drive')` |
| "Can't find datasets/base_images" | Run Notebook 1 first |
| "No reports appearing" | Check Drive/VLM-ARB-Team/reports/ folder exists |
| "Firebase credentials not found" | Firebase is optional. Leave secrets/ empty if not using |
| "Permission denied on Drive" | Make sure Drive folder is shared with edit access |

---

## Cost

✅ **$0/month** (everything is free)

- Google Drive: 15GB free storage (plenty for your images + reports)
- Firestore: Optional, 1GB free storage
- Colab: 8 GPU hours/week free

---

## Key Differences from Cloud Storage Setup

| Aspect | Old (Cloud Storage) | New (Google Drive) |
|--------|-------------------|-------------------|
| File Storage | Cloud Storage bucket | Google Drive folder |
| Billing | Requires credit card | None |
| Sharing | Public links | Drive share permissions |
| Real-time | Firestore (paid) | Firestore (optional, free) |
| Setup Time | 30 min | 5 min |
| Speed | Faster (cloud) | Slightly slower (Drive) |

---

## Next Steps

1. **Team lead**: Create VLM-ARB-Team folder ↓ share with team
2. **First person**: Run Notebook 1 (generates datasets)
3. **Team**: Run Notebook 2 (each member gets own run)
4. **Anyone**: Run Notebook 3 (generate PDF, share link)

**Questions?** See [COLAB_CLOUD_GUIDE.md](COLAB_CLOUD_GUIDE.md) for detailed help.

---

**🎉 You're ready to go! Start with Notebook 1 →**
