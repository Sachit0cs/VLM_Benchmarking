"""
Utilities for VLM-ARB Cloud Integration.

Modules:
- cloud_sync: Firebase Firestore + Cloud Storage client
- auth_helpers: Google Drive and credential management for Colab
"""

from .cloud_sync import FirebaseSync, FirestoreMetricsLogger, validate_firebase_credentials
from .auth_helpers import (
    is_colab_environment,
    mount_google_drive,
    setup_colab_auth,
    load_firebase_credentials,
    setup_user_context,
    get_or_create_run_id,
    install_required_packages,
    get_gpu_info,
    init_logging,
    quick_colab_setup,
)

__all__ = [
    "FirebaseSync",
    "FirestoreMetricsLogger",
    "validate_firebase_credentials",
    "is_colab_environment",
    "mount_google_drive",
    "setup_colab_auth",
    "load_firebase_credentials",
    "setup_user_context",
    "get_or_create_run_id",
    "install_required_packages",
    "get_gpu_info",
    "init_logging",
    "quick_colab_setup",
]
