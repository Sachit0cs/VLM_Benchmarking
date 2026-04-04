# Firestore Schema & Security Rules

Complete documentation of Firestore collections, documents, and fields for VLM-ARB Cloud Framework.

---

## Collections Overview

```
Firestore Database
├─ results/                      # Evaluation results (primary collection)
│  ├─ eval_20260404_123456/     # Run ID
│  └─ eval_20260405_789012/
│
├─ team_configs/                 # Shared team configuration
│  ├─ current                     # Active dataset version + team settings
│  └─ history/         # Historical configurations
│
└─ reports/                       # Report metadata (optional)
   ├─ report_20260404_001/
   └─ report_20260405_002/
```

---

## 1. `results/` Collection

**Purpose**: Store evaluation results from model testing runs

### Document: `results/{run_id}`

```json
{
  "run_id": "eval_20260404_123456_alice@university.edu",
  "timestamp": "2026-04-04T12:34:56.789Z",
  "status": "completed",  // "pending" | "in-progress" | "completed" | "error"
  
  "metadata": {
    "user": "alice@university.edu",
    "dataset_version": "v20260404_120000_abc1234",
    "attack_types": ["typographic", "prompt_injection"],
    "models_tested": ["clip", "mobilevit", "blip2"],
    "duration_seconds": 1847.5,
    "colab_session": "random-session-id"
  },
  
  "metrics": {
    "clip": {
      "asr": 0.42,         // Attack Success Rate (0-1)
      "ods": 0.38,         // Output Deviation Score (0-1)
      "sbr": 0.0,          // Safety Bypass Rate (0-1)
      "cmcs": null         // Cross-Modal Conflict Score (optional)
    },
    "mobilevit": {
      "asr": 0.45,
      "ods": 0.42,
      "sbr": 0.0,
      "cmcs": null
    },
    "blip2": {
      "asr": 0.68,
      "ods": 0.58,
      "sbr": 0.05,         // Can be non-zero for text-generating models
      "cmcs": 0.52
    }
  },
  
  "summary": {
    "total_models": 3,
    "avg_asr": 0.517,
    "best_model": "clip",
    "worst_model": "blip2",
    "images_tested": 5,
    "variants_per_image": 24
  },
  
  "error": null            // Error message if status="error"
}
```

### Firestore Queries (Cloud Firestore Console Examples)

```javascript
// Get results for specific run
db.collection('results').doc('eval_20260404_123456_alice@university.edu').get()

// Get all completed runs
db.collection('results')
  .where('status', '==', 'completed')
  .orderBy('timestamp', 'desc')
  .limit(20)
  .get()

// Get runs by specific user
db.collection('results')
  .where('metadata.user', '==', 'alice@university.edu')
  .orderBy('timestamp', 'desc')
  .get()

// Get runs with specific model
db.collection('results')
  .where('metadata.models_tested', 'array-contains', 'blip2')
  .get()

// Get runs from specific date
db.collection('results')
  .where('timestamp', '>=', '2026-04-04T00:00:00Z')
  .where('timestamp', '<', '2026-04-05T00:00:00Z')
  .get()
```

### Index Required

For queries with multiple `where` clauses (auto-created by Firestore):

```
Collection: results
Fields:
  - metadata.user (Ascending)
  - timestamp (Descending)
```

---

## 2. `team_configs/` Collection

**Purpose**: Store shared team configuration and dataset info

### Document: `team_configs/current`

```json
{
  "dataset_version": "v20260404_120000_abc1234",
  
  "dataset_info": {
    "base_image_count": 5,
    "total_variants": 120,  // 5 images × 24 variants per image
    "attack_types": ["typographic", "prompt_injection"],
    "created_at": "2026-04-04T12:00:00.000Z",
    "created_by": "alice@university.edu",
    "git_version": "abc1234",
    
    "storage_paths": {
      "base_images": "datasets/base_images/",
      "attacked_images": "datasets/attacked_images/"
    },
    
    "variant_config": {
      "typographic": {
        "opacity_levels": ["high", "medium", "low"],
        "num_texts": 3,
        "samples_per_config": 1
      },
      "prompt_injection": {
        "opacity_levels": [50, 100, 150],
        "num_prompts": 2,
        "samples_per_config": 1
      }
    }
  },
  
  "team_settings": {
    "default_models": ["clip", "mobilevit", "blip2", "llava"],
    "default_attacks": ["typographic", "prompt_injection"],
    "inference_timeout_seconds": 300
  },
  
  "status": "active"  // "active" | "archived"
}
```

### Document: `team_configs/history/{version_id}`

```json
{
  "version": "v20260403_150000_xyz7890",
  "superseded_by": "v20260404_120000_abc1234",
  "created_at": "2026-04-03T15:00:00.000Z",
  "status": "archived",
  
  // ... same structure as current ...
}
```

### How to Use

```python
# Load current configuration
from utilities.cloud_sync import FirebaseSync

fs = FirebaseSync("path/to/credentials.json")
config = fs.get_team_config()

dataset_version = config['dataset_version']
storage_paths = config['dataset_info']['storage_paths']
```

---

## 3. `reports/` Collection (Optional)

**Purpose**: Track generated reports metadata

### Document: `reports/{report_id}`

```json
{
  "run_ids": ["eval_20260404_123456", "eval_20260404_567890"],
  "created_at": "2026-04-04T14:30:00.000Z",
  "created_by": "charlie@university.edu",
  
  "report_files": {
    "pdf": "reports/report_20260404_001_report.pdf",
    "html": "reports/report_20260404_001_report.html",
    "json": "reports/report_20260404_001_results.json",
    "chart_png": "reports/report_20260404_001_chart.png"
  },
  
  "public_links": {
    "pdf": "https://storage.googleapis.com/project-id.appspot.com/reports/...",
    "chart": "https://storage.googleapis.com/project-id.appspot.com/reports/..."
  },
  
  "summary": {
    "num_models": 3,
    "avg_asr": 0.517,
    "figure_count": 3
  }
}
```

---

## Firestore Security Rules

Save as `firestore-rules.txt` and upload to Firebase Console:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Allow service account (Colab) to read/write results
    match /results/{document=**} {
      allow read: if request.auth != null || request.auth.uid == 'colab-service-account';
      allow write: if request.auth != null || request.auth.uid == 'colab-service-account';
      allow delete: if false;  // Never delete results
    }
    
    // Allow service account to read/write team config
    match /team_configs/{document=**} {
      allow read: if request.auth != null || request.auth.uid == 'colab-service-account';
      allow write: if request.auth != null || request.auth.uid == 'colab-service-account';
    }
    
    // Allow service account to read reports
    match /reports/{document=**} {
      allow read: if request.auth != null || request.auth.uid == 'colab-service-account';
      allow write: if request.auth != null || request.auth.uid == 'colab-service-account';
    }
    
    // Default: deny all
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

---

## Cloud Storage Security Rules

Save as `storage-rules.txt` and upload to Firebase Console:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    
    // Base images: read/write by service account
    match /datasets/base_images/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null || request.auth.uid == 'colab-service-account';
    }
    
    // Attacked images: read/write by service account
    match /datasets/attacked_images/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null || request.auth.uid == 'colab-service-account';
    }
    
    // Reports: public read, authenticated write
    match /reports/{allPaths=**} {
      allow read: if true;                          // PUBLIC
      allow write: if request.auth != null;         // AUTH ONLY
      allow delete: if request.auth != null;
    }
    
    // Default: deny all
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```

---

## Writing Data Programmatically

### Upload Results from Notebook 2

```python
from utilities.cloud_sync import FirebaseSync

fs = FirebaseSync("path/to/credentials.json")

# After evaluation completes
metrics_dict = {
    "clip": {
        "asr": 0.42,
        "ods": 0.38,
        "sbr": 0.0,
    },
    "blip2": {
        "asr": 0.68,
        "ods": 0.58,
        "sbr": 0.05,
    }
}

metadata = {
    "user": "alice@university.edu",
    "dataset_version": "v20260404_120000_abc1234"
}

fs.upload_results(
    run_id="eval_20260404_123456_alice",
    metrics_dict=metrics_dict,
    metadata=metadata,
    collection="results"
)
```

### Update Dataset Configuration

```python
# From Notebook 1
dataset_info = {
    "base_image_count": 5,
    "total_variants": 120,
    "attack_types": ["typographic", "prompt_injection"],
    # ... see Document structure above ...
}

fs.upload_results(
    run_id="current",
    metrics_dict=dataset_info,
    metadata={"status": "active", "type": "dataset_config"},
    collection="team_configs"
)
```

---

## Reading Data Programmatically

### Fetch All Results

```python
from utilities.cloud_sync import FirebaseSync

fs = FirebaseSync("path/to/credentials.json")

# Get latest 20 runs
runs = fs.list_runs(collection="results", limit=20)

for run in runs:
    print(f"Run: {run['run_id']}")
    print(f"Metrics: {run['metrics']}")
    print(f"Status: {run['status']}")
```

### Fetch Specific Run

```python
run_id = "eval_20260404_123456_alice"
results = fs.download_results(run_id, collection="results")

if results:
    print(results['metrics'])
else:
    print("Run not found")
```

### Fetch Team Configuration

```python
config = fs.get_team_config()
print(f"Dataset Version: {config['dataset_version']}")
print(f"Storage Paths: {config['dataset_info']['storage_paths']}")
```

---

## Backup & Export

### Backup Firestore (Monthly Recommended)

```bash
# From terminal (requires gcloud CLI)
gcloud firestore export gs://your-bucket/backup-2026-04

# Will create timestamped backup folder
```

### Export to BigQuery (Optional)

For large-scale analysis:

```
Firebase Console → Firestore → Exports → Export to BigQuery
Select: results collection
BigQuery Dataset: vlm_arb_data
```

Then query in BigQuery SQL:

```sql
SELECT
  run_id,
  JSON_EXTRACT_SCALAR(metrics, '$.clip.asr') as clip_asr,
  JSON_EXTRACT_SCALAR(metrics, '$.blip2.asr') as blip2_asr
FROM `project-id.vlm_arb_data.results_*`
WHERE DATE(timestamp) >= '2026-04-01'
ORDER BY timestamp DESC;
```

---

## Monitoring & Debugging

### View Firestore Activity

```
Firebase Console → Firestore → Data tab
├─ Click on collection to see documents
└─ Click on document to see fields
```

### Check Quotas

```
Firebase Console → Usage tab
Shows:
  - Storage used (target: <1 GB)
  - Read ops (target: <50k/day)
  - Write ops (target: <1k/day)
```

### Enable Audit Logs

```
Firebase Console → Settings → Audit Logs
Enables tracking who accessed what, when
```

---

## Troubleshooting

### "Permission denied" error

Cause: Security rules blocking access

Fix:
1. Verify service account credentials path
2. Check Firestore rules allow `request.auth != null`
3. Ensure Cloud Storage rules allow writes to `reports/` path

### "Document not found"

Cause: Firestore write may not have completed

Fix:
1. Check `offline_mode` in cloud_sync
2. Verify results were uploaded successfully (check logs)
3. Wait a few seconds (network latency)
4. Check Firestore console directly

### Slow reads

Cause: Missing index or inefficient query

Fix:
1. Firebase will prompt to create index automatically
2. Check `Usage` tab for hot collections
3. Consider paginating large result sets

---

## Data Retention Policy

Recommended:

```
• Keep latest 10 runs: 3 months
• Archive old runs: 1 year
• Delete sensitive data: After publication
```

Configure in Firestore lifecycle policies:

```
Firebase Console → Firestore → Lifecycle Rules
If doc age > 90 days AND status != 'active'
→ Move to "archived" collection
```

---

**For questions or schema updates, see [COLAB_CLOUD_GUIDE.md](COLAB_CLOUD_GUIDE.md)**
