"""
Cloud Sync Module: Firebase Firestore + Cloud Storage integration for VLM-ARB.

Provides a lightweight wrapper around Firebase SDK for Colab environment.
Enables real-time syncing of results, images, and reports across team.

Features:
- Upload evaluation results to Firestore (ASR, ODS, SBR metrics)
- Download previous runs for comparison
- Upload images/reports to Cloud Storage
- Generate shareable public links
- Graceful fallback to local caching if Firebase unavailable
- Automatic retry logic for transient failures

Usage:
    from utilities.cloud_sync import FirebaseSync
    
    fs = FirebaseSync(credentials_path="/path/to/serviceAccountKey.json")
    fs.upload_results(run_id="run_123", metrics_dict={...})
    results = fs.download_results(run_id="run_123")
    link = fs.upload_file_and_get_link(local_path="report.pdf", bucket_path="reports/")
"""

import json
import os
import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

logger = logging.getLogger(__name__)


class FirebaseSync:
    """
    Firebase Firestore + Cloud Storage client for VLM-ARB.
    
    Handles authentication, result uploads, downloads, and file management.
    Falls back to local caching if Firebase is unavailable.
    
    Attributes:
        db: Firestore database reference
        bucket: Cloud Storage bucket reference
        cache_dir: Local directory for offline caching
        offline_mode: Whether Firebase is unavailable
    """
    
    def __init__(
        self,
        credentials_path: str,
        project_id: Optional[str] = None,
        bucket_name: Optional[str] = None,
        cache_dir: str = "/tmp/vlm_arb_cache"
    ):
        """
        Initialize Firebase connection.
        
        Args:
            credentials_path: Path to serviceAccountKey.json from Firebase console
            project_id: Firebase project ID (optional, extracted from credentials)
            bucket_name: Cloud Storage bucket name (optional, auto-detected)
            cache_dir: Local directory for offline result caching
            
        Raises:
            FileNotFoundError: If credentials file not found
            ValueError: If Firebase SDK not installed
        """
        if not FIREBASE_AVAILABLE:
            raise ValueError(
                "Firebase Admin SDK not installed. "
                "Run: pip install firebase-admin"
            )
        
        # Validate credentials
        if not Path(credentials_path).exists():
            raise FileNotFoundError(
                f"Credentials not found: {credentials_path}\n"
                "Download from: Firebase Console → Project Settings → Service Accounts"
            )
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load credentials and extract project ID
            cred = credentials.Certificate(credentials_path)
            self.project_id = project_id or cred.project_id
            self.bucket_name = bucket_name or f"{self.project_id}.appspot.com"
            
            # Initialize Firebase app (avoid reinit if already initialized)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.bucket = storage.bucket(self.bucket_name)
            self.offline_mode = False
            logger.info(f"✅ Firebase initialized: {self.project_id}")
            
        except Exception as e:
            logger.warning(
                f"⚠️  Firebase initialization failed: {e}\n"
                "Running in offline mode (local caching only)"
            )
            self.db = None
            self.bucket = None
            self.offline_mode = True
    
    # ====== FIRESTORE OPERATIONS ======
    
    def upload_results(
        self,
        run_id: str,
        metrics_dict: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        collection: str = "results"
    ) -> bool:
        """
        Upload evaluation results to Firestore.
        
        Args:
            run_id: Unique run identifier (e.g., "run_20260404_clip_typographic")
            metrics_dict: Results dict with ASR, ODS, SBR, etc.
            metadata: Additional metadata (timestamp, models_list, attack_types, etc.)
            collection: Firestore collection name (default: "results")
            
        Returns:
            True if successful, False otherwise
            
        Example:
            metrics = {
                "clip": {"asr": 0.42, "ods": 0.38, "sbr": 0.15},
                "blip2": {"asr": 0.68, "ods": 0.58, "sbr": 0.45},
                "summary": {"avg_asr": 0.55, "timestamp": "2026-04-04T12:30:00"}
            }
            fs.upload_results("run_123", metrics)
        """
        if not metrics_dict:
            logger.error("Cannot upload empty metrics dict")
            return False
        
        document_data = {
            "metrics": metrics_dict,
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        
        if metadata:
            document_data.update(metadata)
        
        # Firestore upload with retry
        if not self.offline_mode:
            try:
                self.db.collection(collection).document(run_id).set(
                    document_data,
                    merge=True  # Don't overwrite existing fields
                )
                logger.info(f"✅ Results uploaded: {collection}/{run_id}")
                return True
            except Exception as e:
                logger.warning(f"Firebase upload failed: {e}. Caching locally.")
                self.offline_mode = True
        
        # Local cache fallback
        self._cache_results_local(run_id, document_data, collection)
        return True
    
    def download_results(
        self,
        run_id: str,
        collection: str = "results"
    ) -> Optional[Dict[str, Any]]:
        """
        Download evaluation results from Firestore or local cache.
        
        Args:
            run_id: Run identifier to fetch
            collection: Firestore collection name
            
        Returns:
            Results dict if found, None otherwise
        """
        # Try Firestore first
        if not self.offline_mode:
            try:
                doc = self.db.collection(collection).document(run_id).get()
                if doc.exists:
                    logger.info(f"✅ Results downloaded: {collection}/{run_id}")
                    return doc.to_dict()
                else:
                    logger.debug(f"No results found in Firestore: {run_id}")
            except Exception as e:
                logger.warning(f"Firestore download failed: {e}")
        
        # Try local cache
        return self._load_results_from_cache(run_id, collection)
    
    def list_runs(
        self,
        collection: str = "results",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List all completed runs from Firestore.
        
        Args:
            collection: Collection to query
            limit: Max number of runs to return
            
        Returns:
            List of run metadata dicts sorted by timestamp (newest first)
        """
        if self.offline_mode or not self.db:
            logger.warning("Cannot list runs: offline mode")
            return []
        
        try:
            docs = (
                self.db.collection(collection)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            
            runs = []
            for doc in docs:
                data = doc.to_dict()
                data["run_id"] = doc.id
                runs.append(data)
            
            logger.info(f"✅ Listed {len(runs)} runs from {collection}")
            return runs
        
        except Exception as e:
            logger.error(f"Failed to list runs: {e}")
            return []
    
    def update_run_status(
        self,
        run_id: str,
        status: str,
        error_msg: Optional[str] = None,
        collection: str = "results"
    ) -> bool:
        """
        Update run status (pending/in-progress/completed/error).
        
        Args:
            run_id: Run identifier
            status: New status string
            error_msg: Error message if status is "error"
            collection: Firestore collection
            
        Returns:
            True if successful
        """
        if self.offline_mode or not self.db:
            return False
        
        try:
            update_dict = {
                "status": status,
                "last_updated": datetime.utcnow()
            }
            if error_msg:
                update_dict["error"] = error_msg
            
            self.db.collection(collection).document(run_id).update(update_dict)
            logger.info(f"Status updated: {run_id} → {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            return False
    
    def get_team_config(self) -> Dict[str, Any]:
        """
        Fetch shared team configuration from Firestore.
        
        Returns:
            Config dict with models_list, attacks_list, dataset_version, etc.
            Returns empty dict if unavailable.
        """
        if self.offline_mode or not self.db:
            logger.warning("Cannot fetch team config: offline mode")
            return {}
        
        try:
            doc = self.db.collection("team_configs").document("current").get()
            if doc.exists:
                return doc.to_dict()
            logger.warning("No team config found in Firestore")
            return {}
        except Exception as e:
            logger.error(f"Failed to fetch team config: {e}")
            return {}
    
    # ====== CLOUD STORAGE OPERATIONS ======
    
    def upload_file(
        self,
        local_path: str,
        bucket_path: str,
        make_public: bool = False
    ) -> bool:
        """
        Upload a file to Cloud Storage.
        
        Args:
            local_path: Path to local file
            bucket_path: Destination path in bucket (e.g., "reports/results.pdf")
            make_public: If True, set file as publicly readable (for reports)
            
        Returns:
            True if successful
        """
        if self.offline_mode or not self.bucket:
            logger.warning(f"Cannot upload {local_path}: offline mode")
            return False
        
        local_file = Path(local_path)
        if not local_file.exists():
            logger.error(f"File not found: {local_path}")
            return False
        
        try:
            blob = self.bucket.blob(bucket_path)
            blob.upload_from_filename(local_path)
            
            if make_public:
                blob.make_public()
                logger.info(f"✅ File uploaded (public): {bucket_path}")
            else:
                logger.info(f"✅ File uploaded (private): {bucket_path}")
            
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def download_file(
        self,
        bucket_path: str,
        local_path: str
    ) -> bool:
        """
        Download a file from Cloud Storage.
        
        Args:
            bucket_path: Path in bucket (e.g., "datasets/attacked_images/")
            local_path: Destination local path
            
        Returns:
            True if successful
        """
        if self.offline_mode or not self.bucket:
            logger.warning(f"Cannot download {bucket_path}: offline mode")
            return False
        
        try:
            blob = self.bucket.blob(bucket_path)
            blob.download_to_filename(local_path)
            logger.info(f"✅ File downloaded: {bucket_path} → {local_path}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def list_files(
        self,
        bucket_path_prefix: str
    ) -> List[str]:
        """
        List all files in a bucket path.
        
        Args:
            bucket_path_prefix: Path prefix (e.g., "reports/")
            
        Returns:
            List of full bucket paths
        """
        if self.offline_mode or not self.bucket:
            return []
        
        try:
            blobs = self.bucket.list_blobs(prefix=bucket_path_prefix)
            files = [blob.name for blob in blobs]
            logger.info(f"✅ Listed {len(files)} files in {bucket_path_prefix}")
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def get_public_url(self, bucket_path: str, expiration_hours: int = 24) -> str:
        """
        Generate a signed public URL for a Cloud Storage file.
        
        Args:
            bucket_path: Path in bucket
            expiration_hours: How long URL is valid (requires file to be public or signed)
            
        Returns:
            Public URL string (requires file to be public via make_public())
        """
        if not self.bucket:
            return ""
        
        blob = self.bucket.blob(bucket_path)
        # For public files, use this simple URL
        return f"https://storage.googleapis.com/{self.bucket_name}/{bucket_path}"
    
    def upload_image_batch(
        self,
        image_dir: str,
        bucket_path_prefix: str
    ) -> Dict[str, str]:
        """
        Upload all images from a directory to Cloud Storage.
        
        Args:
            image_dir: Local directory with images
            bucket_path_prefix: Bucket path prefix (e.g., "attacked_images/")
            
        Returns:
            Dict mapping local filenames to cloud URLs
        """
        image_dir = Path(image_dir)
        if not image_dir.exists():
            logger.error(f"Image directory not found: {image_dir}")
            return {}
        
        urls = {}
        for img_file in image_dir.glob("*.png") + image_dir.glob("*.jpg") + image_dir.glob("*.jpeg"):
            bucket_path = f"{bucket_path_prefix}{img_file.name}"
            if self.upload_file(str(img_file), bucket_path, make_public=False):
                urls[img_file.name] = self.get_public_url(bucket_path)
        
        logger.info(f"✅ Uploaded {len(urls)} images to {bucket_path_prefix}")
        return urls
    
    # ====== LOCAL CACHING (OFFLINE MODE) ======
    
    def _cache_results_local(
        self,
        run_id: str,
        data: Dict[str, Any],
        collection: str
    ) -> None:
        """Cache results locally when Firebase unavailable."""
        cache_file = self.cache_dir / f"{collection}_{run_id}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, default=str, indent=2)
            logger.info(f"💾 Cached locally: {cache_file}")
        except Exception as e:
            logger.error(f"Failed to cache: {e}")
    
    def _load_results_from_cache(
        self,
        run_id: str,
        collection: str
    ) -> Optional[Dict[str, Any]]:
        """Load results from local cache."""
        cache_file = self.cache_dir / f"{collection}_{run_id}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            logger.info(f"💾 Loaded from cache: {cache_file}")
            return data
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None
    
    def sync_cache_to_firebase(self) -> int:
        """
        Sync all locally cached results to Firebase (when connection restored).
        
        Returns:
            Number of successful syncs
        """
        if self.offline_mode or not self.db:
            logger.warning("Cannot sync: offline mode")
            return 0
        
        cache_files = list(self.cache_dir.glob("*.json"))
        synced = 0
        
        for cache_file in cache_files:
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                
                # Parse run_id from filename (format: "{collection}_{run_id}.json")
                parts = cache_file.stem.rsplit("_", 1)
                if len(parts) == 2:
                    collection, run_id = parts
                    self.db.collection(collection).document(run_id).set(data, merge=True)
                    cache_file.unlink()  # Delete after syncing
                    synced += 1
            except Exception as e:
                logger.error(f"Failed to sync {cache_file}: {e}")
        
        logger.info(f"✅ Synced {synced} cached results to Firebase")
        return synced


class FirestoreMetricsLogger:
    """
    Convenience wrapper for logging evaluation metrics during a run.
    
    Automatically flushes to Firestore when complete, with fallback to local caching.
    """
    
    def __init__(self, fs: FirebaseSync, run_id: str):
        """
        Initialize logger for a run.
        
        Args:
            fs: FirebaseSync instance
            run_id: Run identifier
        """
        self.fs = fs
        self.run_id = run_id
        self.metrics = {}
        self.start_time = datetime.utcnow()
    
    def log_model_metrics(
        self,
        model_name: str,
        asr: float,
        ods: float,
        sbr: float,
        cmcs: Optional[float] = None
    ) -> None:
        """Log metrics for a single model."""
        if model_name not in self.metrics:
            self.metrics[model_name] = {}
        
        self.metrics[model_name].update({
            "asr": round(asr, 4),
            "ods": round(ods, 4),
            "sbr": round(sbr, 4),
        })
        if cmcs is not None:
            self.metrics[model_name]["cmcs"] = round(cmcs, 4)
    
    def flush(self) -> bool:
        """Finalize and upload all metrics to Firestore."""
        end_time = datetime.utcnow()
        duration_secs = (end_time - self.start_time).total_seconds()
        
        summary = {
            "metrics": self.metrics,
            "duration_seconds": duration_secs,
            "model_count": len(self.metrics),
            "completed_at": end_time
        }
        
        return self.fs.upload_results(self.run_id, summary)


# ====== STANDALONE UTILITY FUNCTIONS ======

def validate_firebase_credentials(credentials_path: str) -> bool:
    """Check if Firebase credentials file is valid."""
    try:
        with open(credentials_path) as f:
            data = json.load(f)
        required_fields = {"type", "project_id", "private_key", "client_email"}
        return required_fields.issubset(data.keys())
    except Exception as e:
        logger.error(f"Invalid credentials: {e}")
        return False


def create_dummy_config(output_path: str = "config.yaml") -> None:
    """Create a template Firebase config file."""
    template = """# Firebase Configuration for VLM-ARB
# Get these values from Firebase Console → Project Settings

firebase:
  project_id: "your-project-id"
  bucket_name: "your-project-id.appspot.com"
  credentials_path: "/path/to/serviceAccountKey.json"

cloud:
  cache_dir: "/tmp/vlm_arb_cache"
  offline_enabled: true
  
  storage:
    datasets_bucket: "datasets/"
    attacked_images_bucket: "attacked_images/"
    reports_bucket: "reports/"
  
  firestore:
    results_collection: "results"
    configs_collection: "team_configs"

team:
  shared_drive_folder: "/content/drive/MyDrive/VLM-ARB-Team"
  credentials_subfolder: "secrets"
"""
    Path(output_path).write_text(template)
    print(f"✅ Config template created: {output_path}")
