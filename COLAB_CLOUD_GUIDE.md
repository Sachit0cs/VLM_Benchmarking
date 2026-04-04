# VLM-ARB Cloud Framework Guide

**Complete guide to running VLM-ARB evaluation entirely from Google Colab with Firebase**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start (5 min)](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Running Notebooks](#running-notebooks)
5. [Team Collaboration](#team-collaboration)
6. [Troubleshooting](#troubleshooting)
7. [Cost & Quotas](#cost--quotas)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  COLAB NOTEBOOKS (3 specialized notebooks)          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Notebook 1: Generate Datasets                      │
│  └─→ Synthetic test images + attack variants       │
│                                                      │
│  Notebook 2: Run Model Evaluations                 │
│  └─→ Test CLIP, MobileViT, BLIP-2, LLaVA          │
│                                                      │
│  Notebook 3: Generate Reports                      │
│  └─→ PDF reports, charts, history                 │
│                                                      │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│  FIREBASE (Real-time sync layer)                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  • Firestore Database                              │
│    └─ Collections: results, team_configs           │
│                                                      │
│  • Cloud Storage                                    │
│    └─ Buckets: datasets/, reports/                 │
│                                                      │
│  • Security Rules (firestore-rules.txt)           │
│    └─ Auth: service account (Colab)                │
│                                                      │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│  TEAM ACCESS                                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  • Google Drive (shared folder)                    │
│    └─ Credentials, notebooks, config              │
│                                                      │
│  • Firestore Console                               │
│    └─ Real-time results viewing                    │
│                                                      │
│  • Public Report Links                             │
│    └─ Shareable PDF/HTML reports                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

### For Team Lead (One-time setup)

1. **Create Firebase Project** (5 min)
   ```bash
   # Go to https://console.firebase.google.com
   # Create new project → Enable Firestore + Cloud Storage (free tier)
   # Download service account credentials
   ```

2. **Create Google Drive Folder** (2 min)
   ```
   Google Drive → Create folder "VLM-ARB-Team"
   └─ subfolder "secrets"
   └─ subfolder "notebooks"
   Share with team members
   ```

3. **Upload Credentials** (1 min)
   ```
   Drive/VLM-ARB-Team/secrets/
   └─ serviceAccountKey.json (downloaded from Firebase)
   ```

4. **Share Notebooks** (2 min)
   Copy the 3 notebooks to Drive/VLM-ARB-Team/notebooks/

### For Each Team Member (First-time)

1. **Accept Folder Invite**
   - Access shared Google Drive folder

2. **Open Notebook 1** in Google Colab
   - Click "Open in Colab" button (or import from Drive)
   - Run cells in order

3. **Done!** 
   - Proceed to Notebook 2 and 3

---

## Detailed Setup

### Step 1: Firebase Project Setup

#### 1a. Create Firebase Project

```
1. Go to https://console.firebase.google.com
2. Click "Create a project"
3. Project name: "vlm-arb-{your-name}"
4. Disable Google Analytics (optional)
5. Create project
```

#### 1b. Enable Firestore

```
1. Firebase Console → Firestore Database
2. Create database
3. Production mode (security rules will restrict access)
4. Region: us-central1
5. Create
```

#### 1c. Enable Cloud Storage

```
1. Firebase Console → Storage
2. Get Started
3. Default bucket: {project-id}.appspot.com
4. Start in Production mode
5. Continue
```

#### 1d. Create Service Account Account

```
1. Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save JSON file as "serviceAccountKey.json"
4. ⚠️  KEEP THIS SECURE - contains credentials
```

#### 1e. Set Security Rules

```
1. Firestore → Rules tab
2. Replace with: (see firestore-rules.txt)
3. Publish

2. Cloud Storage → Rules tab  
2. Replace with: (see storage-rules.txt)
3. Publish
```

### Step 2: Google Drive Setup

#### 2a. Create Team Folder

```
Google Drive → New Folder
Name: "VLM-ARB-Team"
├─ secrets/           (Firebase credentials)
├─ notebooks/         (Colab notebooks)
└─ results/           (generated reports)
```

#### 2b. Upload Credentials

```
Drive/VLM-ARB-Team/secrets/
└─ serviceAccountKey.json
```

Share securely with team:
- Email-based access control (recommended)
- Link-based access (simpler, less secure)

#### 2c. Configure config.yaml

```yaml
firebase:
  project_id: "your-actual-project-id"
  credentials_path: "/root/VLM-ARB-Team/secrets/serviceAccountKey.json"
```

### Step 3: Copy Notebooks to Drive

Download the 3 notebooks from repo and upload to Drive:

```
Drive/VLM-ARB-Team/notebooks/
├─ Notebook_1_Generate_Datasets.ipynb
├─ Notebook_2_Run_Model_Evaluations.ipynb
└─ Notebook_3_Generate_Reports.ipynb
```

---

## Running Notebooks

### Notebook 1: Generate Datasets

**Purpose**: Create synthetic test images and attack variants (run once per team)

**Duration**: ~5-10 minutes

**Steps**:
1. Open in Colab
2. Run Cell 1-2: Install dependencies + auth
3. Run Cell 3: Define generation functions
4. Run Cell 4-5: Check idempotency + generate base images
5. Run Cell 6: Generate attack variants
6. Run Cell 7-9: Upload to Cloud Storage + log to Firestore
7. Run Cell 10: Summary

**Output**:
- Cloud Storage: `datasets/base_images/` and `datasets/attacked_images/`
- Firestore: `team_configs.current` document with dataset version

**Notes**:
- ✅ **Idempotent**: If run twice, detects existing data and skips regeneration
- ⚠️ **GPU not needed** for dataset generation

### Notebook 2: Run Model Evaluations

**Purpose**: Test models on attack variants, compute metrics, log results

**Duration**: 20-45 minutes (depends on GPU and models)

**Steps**:
1. Open in Colab
2. Run Cell 1-2: Dependencies + auth + load dataset info
3. Run Cell 3: Download images from Cloud Storage
4. Run Cell 4: Load models (graceful fallback if insufficient GPU)
   - CLIP: ~350MB (✅ always works)
   - MobileViT: ~20MB (✅ always works)
   - BLIP-2: ~2.7B (⚠️ needs ~10GB GPU memory)
   - LLaVA: ~7B (⚠️ needs ~14GB GPU memory)
5. Run Cell 5: Run CLIP inference
6. Run Cell 6-7: Compute metrics + log to Firestore
7. Run Cell 8: Cleanup

**Output**:
- Firestore: `results.{run_id}` document with ASR, ODS, SBR metrics
- Local: Cached results in `/tmp/vlm_arb_cache`

**Monitor Progress**:
- Open Firestore Console in parallel
- Watch results appear in real-time as model inference completes

**Notes**:
- 💻 **Request GPU in Colab**: Runtime → Change runtime type → GPU
- 🔄 **Real-time logging**: Results upload to Firestore as they compute
- ⏸️ **Can pause/resume**: Notebook saves intermediate results

### Notebook 3: Generate Reports

**Purpose**: Fetch results from Firestore, visualize, generate PDF/HTML reports

**Duration**: ~5-10 minutes

**Steps**:
1. Open in Colab
2. Run Cell 1-2: Dependencies + auth + fetch results
3. Run Cell 3: Select run(s) to report on
4. Run Cell 4: Generate visualization charts
5. Run Cell 5: Create PDF report
6. Run Cell 6: Upload to Cloud Storage
7. Run Cell 7-8: Generate shareable links

**Output**:
- Cloud Storage: `reports/{run_id}_report.pdf`, `_chart.png`, `_results.json`
- Public URLs: Shareable links for team (print in notebook)

**Share Results**:
```
Copy from Cell 7 output:
✅ PDF Report: https://storage.googleapis.com/...
✅ Chart: https://storage.googleapis.com/...
✅ JSON: https://storage.googleapis.com/...

→ Paste in team Slack, email, etc.
```

**Notes**:
- 🌐 **Public links**: Anyone with URL can view (no auth needed)
- 📊 **Historical reports**: Notebook 3 also shows all past reports

---

## Team Collaboration

### Sync Model (Each team member independent)

```
Team Member 1                 Team Member 2
   ↓                             ↓
Run Notebook 2              Run Notebook 2
   ↓                             ↓
Firebase (Firestore) ← Shared database
   ↓
Run Notebook 3 (any team member) → All see results
```

### Best Practices

1. **Use unique run IDs**:
   - Auto-generated: `eval_20260404_123456_user@example`
   - Manual: `eval_clip_typographic_v2`

2. **Coordinate updates**:
   - Notebook 1 (datasets): Run once, document version in team chat
   - Notebook 2 (evaluation): Run independently, results auto-sync
   - Notebook 3 (reporting): Any team member can run anytime

3. **Share results**:
   - Copy public links from Notebook 3
   - Post to team Slack, email, or shared doc
   - Link includes PDF + charts + JSON for downstream analysis

### Example Team Workflow

```
Monday 10am: Team Lead runs Notebook 1 → "Dataset v20260404 ready"

Monday 11am-1pm: 
  - Person A runs Notebook 2 on GPU-T4 → Tests CLIP, MobileViT
  - Person B runs Notebook 2 on GPU-A100 → Tests BLIP-2, LLaVA

Monday 1:30pm: Person C runs Notebook 3 → Generates combined report

Monday 2pm: Team view report links in #research Slack channel
```

---

## Troubleshooting

### Firebase Won't Connect

**Error**: `ConnectionError: Failed to connect to Firestore`

**Solutions**:
1. Check credentials path: `/root/VLM-ARB-Team/secrets/serviceAccountKey.json` exists
2. Verify Firebase credentials are valid (try Console)
3. Check internet connection (Colab has connectivity)
4. Offline mode enabled: Results cache locally until online

**Workaround**: Notebook runs offline-first, syncs when Connection restored.

### Out of GPU Memory

**Error**: `CUDA out of memory`

**Solutions**:
1. **Reduce batch size**: Edit Notebook 2, Cell 4
   ```python
   batch_size = 2  # Instead of 5
   ```

2. **Skip large models**: Comment out in Cell 4
   ```python
   # models_status['blip2'] = "⏭️ Skipped"
   # models_status['llava'] = "⏭️ Skipped"
   ```

3. **Use CPU**: Runtime → Change runtime type → CPU (slower)

4. **Request better GPU**: Colab → Runtime → Change runtime type → GPU (may need Colab Pro)

### Images Not Downloading

**Error**: `FileNotFoundError: datasets/base_images/...`

**Solutions**:
1. Run Notebook 1 first (generates datasets)
2. Check Firestore `team_configs.current` has dataset_version
3. Verify Cloud Storage permissions in Firebase Console

### Report Links Don't Work

**Error**: `403 Forbidden` when opening report link

**Solutions**:
1. Check Cloud Storage rules: `reports/*` must have public read
   ```
   Verify in Firebase Console → Storage → Rules:
   match /reports/{document=**} {
     allow read: if true;  // Public
     allow write: if request.auth != null;  // Auth only
   }
   ```

2. Regenerate links from Notebook 3, Cell 7

---

## Cost & Quotas

### Firebase Free Tier (Sufficient for Research)

| Resource | Free Tier | Your Need |
|----------|-----------|-----------|
| Firestore | 1 GB storage, 50k reads/day | ✅ ~10MB, few hundred reads |
| Cloud Storage | 5 GB | ✅ ~500MB (images + reports) |
| Data egress | 1 GB/month | ✅ Minimal |
| **Cost** | **$0/month** | **$0/month** |

### Colab Quotas (Free)

| Resource | Free | Your Need |
|----------|------|-----------|
| GPU hours/week | 8 hours | ✅ ~2-3 hours/notebook run |
| Execution timeout | 12 hours | ✅ Each notebook <1 hour |
| Storage | 15 GB (Google Drive) | ✅ ~1-2 GB |
| **Cost** | **$0/month** | **$0/month** |

### Staying Within Quotas

✅ **Do**:
- Run Notebook 1 once per week → Generate dataset version
- Run Notebook 2 as needed → Each run logs to single document
- Run Notebook 3 anytime → Reads cached results

❌ **Avoid**:
- Re-running Notebook 1 constantly (uses write quota)
- Testing every image variant per run (clip to representative subset)
- Storing raw images >1-2 GB (use Cloud Storage, not Drive)

---

## Environment Variables

(Optional) Set in Colab for convenience:

```python
import os
os.environ['FIREBASE_PROJECT_ID'] = 'your-project-id'
os.environ['FIREBASE_CREDENTIALS_PATH'] = '/root/VLM-ARB-Team/secrets/serviceAccountKey.json'
os.environ['COLAB_SHARED_DRIVE'] = '/content/drive/MyDrive/VLM-ARB-Team'
```

---

## API Keys (If Using GPT-4V / Claude)

If adding API-based models (separate Notebook 2b):

1. Store API keys in shared folder:
   ```
   Drive/VLM-ARB-Team/secrets/
   ├─ serviceAccountKey.json
   ├─ openai-api-key.txt
   └─ anthropic-api-key.txt
   ```

2. Load in Notebook:
   ```python
   with open('/root/VLM-ARB-Team/secrets/openai-api-key.txt') as f:
       openai_key = f.read().strip()
   ```

3. API costs tracked separately (not covered by quota)

---

## What's Next?

✅ **Notebooks running?** Your cloud setup is complete!

**Next steps**:
1. Run Notebook 1 → Generate datasets
2. Run Notebook 2 → Evaluate models  
3. Run Notebook 3 → Generate reports
4. Share results with team

**Want to customize?**
- Modify `config.yaml` for different models/attacks
- Edit Notebook 1 to add new attack types
- Extend Notebook 3 with custom visualiz ations

**Questions?**
- See [Firestore Schema Guide](FIRESTORE_SCHEMA.md)
- Check logs in Notebook cells for detailed errors
- Monitor Firestore Console in parallel tab

---

**Happy researching! 🚀**
