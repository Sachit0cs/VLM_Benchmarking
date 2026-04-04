"""
Authentication Helpers: Google Drive mounting and credential injection for Colab.

Provides utilities for:
- Mounting Google Drive in Colab environment
- Loading Firebase credentials from shared team folder
- Managing user authentication and team permissions
- Setting up environment variables for cloud access

Usage:
    from utilities.auth_helpers import setup_colab_auth, load_credentials
    
    # In Colab
    drive_path = setup_colab_auth()  # Mounts Google Drive
    creds = load_credentials(drive_path)  # Loads Firebase credentials
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def is_colab_environment() -> bool:
    """
    Check if code is running in Google Colab.
    
    Returns:
        True if running in Colab, False otherwise
    """
    try:
        import google.colab
        return True
    except ImportError:
        return False


def mount_google_drive(mount_point: str = "/content/drive") -> str:
    """
    Mount Google Drive in Colab environment.
    
    Args:
        mount_point: Directory to mount at (default: "/content/drive")
        
    Returns:
        User's main drive path (e.g., "/content/drive/MyDrive")
        
    Raises:
        RuntimeError: If not in Colab or mount fails
    """
    if not is_colab_environment():
        raise RuntimeError(
            "Not in Colab environment. "
            "This function only works in Google Colab notebooks."
        )
    
    try:
        from google.colab import drive
        
        # Check if already mounted
        my_drive = Path(f"{mount_point}/MyDrive")
        if my_drive.exists():
            logger.info(f"✅ Google Drive already mounted at {mount_point}")
            return str(my_drive)
        
        # Mount
        drive.mount(mount_point)
        logger.info(f"✅ Google Drive mounted at {mount_point}")
        return str(my_drive)
        
    except Exception as e:
        raise RuntimeError(f"Failed to mount Google Drive: {e}")


def setup_colab_auth(
    team_folder_name: str = "VLM-ARB-Team",
    mount_point: str = "/content/drive"
) -> Path:
    """
    Complete Colab setup: mount Drive and return team folder path.
    
    This is the main entry point for Colab setup.
    
    Args:
        team_folder_name: Name of shared team folder in Drive
        mount_point: Where to mount Google Drive
        
    Returns:
        Path to team folder (e.g., "/content/drive/MyDrive/VLM-ARB-Team")
        
    Example:
        team_drive = setup_colab_auth()
        # Now use team_drive.joinpath("secrets/serviceAccountKey.json")
    """
    if not is_colab_environment():
        logger.warning("⚠️  Not in Colab. Skipping Drive mount.")
        return Path("./VLM-ARB-Team")  # Local fallback
    
    try:
        my_drive = mount_google_drive(mount_point)
        team_path = Path(my_drive) / team_folder_name
        
        if not team_path.exists():
            raise FileNotFoundError(
                f"Team folder not found: {team_path}\n"
                "Please create/share the VLM-ARB-Team folder in your Google Drive"
            )
        
        logger.info(f"✅ Team folder ready: {team_path}")
        return team_path
        
    except Exception as e:
        logger.error(f"Colab auth setup failed: {e}")
        raise


def load_firebase_credentials(
    credentials_path: str
) -> Dict[str, str]:
    """
    Load Firebase service account credentials from JSON file.
    
    Args:
        credentials_path: Path to serviceAccountKey.json
        
    Returns:
        Credentials dict
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        json.JSONDecodeError: If file is invalid JSON
    """
    cred_path = Path(credentials_path)
    
    if not cred_path.exists():
        raise FileNotFoundError(
            f"Credentials not found: {credentials_path}\n"
            "Expected: {team_folder}/secrets/serviceAccountKey.json\n"
            "Download from: Google Cloud Console → Service Accounts → Keys"
        )
    
    try:
        with open(cred_path, "r") as f:
            creds = json.load(f)
        
        # Validate required fields
        required = {"type", "project_id", "private_key", "client_email"}
        if not required.issubset(creds.keys()):
            raise ValueError(
                f"Invalid credentials format. Missing fields: {required - set(creds.keys())}"
            )
        
        logger.info(f"✅ Credentials loaded: {creds.get('project_id')}")
        return creds
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in credentials: {e}", "", 0
        )


def setup_user_context(
    team_folder: Path,
    user_email: Optional[str] = None
) -> Dict[str, str]:
    """
    Set up user context: load credentials and set environment variables.
    
    Args:
        team_folder: Path to shared team folder
        user_email: Email of user (optional, for logging/permissions)
        
    Returns:
        Context dict with paths and credentials
        
    Example:
        context = setup_user_context(team_folder, user_email="student@university.edu")
        # context["creds_path"], context["run_id"], etc.
    """
    context = {
        "team_folder": str(team_folder),
        "secrets_folder": str(team_folder / "secrets"),
        "creds_path": str(team_folder / "secrets" / "serviceAccountKey.json"),
        "user_email": user_email or os.getenv("USER", "anonymous"),
        "is_colab": is_colab_environment()
    }
    
    # Verify credentials exist
    cred_path = Path(context["creds_path"])
    if not cred_path.exists():
        raise FileNotFoundError(
            f"Credentials not found at {context['creds_path']}\n"
            "Please ensure serviceAccountKey.json is in the secrets folder"
        )
    
    logger.info(f"✅ User context ready: {context['user_email']} (Colab: {context['is_colab']})")
    return context


def get_or_create_run_id(
    team_folder: Path,
    prefix: str = "run"
) -> str:
    """
    Generate unique run ID for this evaluation.
    
    Format: "{prefix}_{YYYYMMDD}_{HHMMSS}_{user_short}"
    
    Args:
        team_folder: Path to team folder (for tracking)
        prefix: Run ID prefix (default: "run")
        
    Returns:
        Unique run ID string
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user = os.getenv("USER", "colab").split("@")[0][:8]  # First 8 chars of email
    run_id = f"{prefix}_{timestamp}_{user}"
    
    logger.info(f"✅ Run ID: {run_id}")
    return run_id


# ====== COLAB-SPECIFIC HELPERS ======

def install_required_packages() -> bool:
    """
    Install required pip packages in Colab.
    
    Installs:
    - firebase-admin (Firebase SDK)
    - gdown (Google Drive downloads)
    - pillow (Image processing)
    - transformers, torch (Model dependencies)
    
    Returns:
        True if all packages installed successfully
    """
    if not is_colab_environment():
        logger.warning("Not in Colab. Skipping package installation.")
        return True
    
    packages = [
        "firebase-admin",
        "gdown",
        "Pillow",
        "transformers",
        "torch",
        "torchvision",
        "numpy",
        "scipy",
        "matplotlib",
    ]
    
    try:
        import subprocess
        for pkg in packages:
            logger.info(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])
        
        logger.info("✅ All packages installed")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Package installation failed: {e}")
        return False


def get_gpu_info() -> Dict[str, str]:
    """
    Get info about available GPU in Colab.
    
    Returns:
        Dict with gpu_name, memory_total, memory_free, etc.
    """
    if not is_colab_environment():
        return {"gpu_available": False}
    
    try:
        gpu_info = {}
        
        # Check if GPU available
        import torch
        if torch.cuda.is_available():
            gpu_info["gpu_available"] = True
            gpu_info["gpu_name"] = torch.cuda.get_device_name(0)
            gpu_info["gpu_memory_total_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
            gpu_info["gpu_memory_reserved_gb"] = torch.cuda.memory_reserved(0) / 1e9
            gpu_info["gpu_memory_allocated_gb"] = torch.cuda.memory_allocated(0) / 1e9
        else:
            gpu_info["gpu_available"] = False
            gpu_info["warning"] = "No GPU available. Request GPU in Colab settings."
        
        return gpu_info
    except Exception as e:
        logger.error(f"Failed to get GPU info: {e}")
        return {"gpu_available": False, "error": str(e)}


def check_colab_quotas() -> Dict[str, str]:
    """
    Check if Colab session is in good standing (execution time, etc.).
    
    Returns:
        Dict with quota status
    """
    if not is_colab_environment():
        return {"in_colab": False}
    
    info = {"in_colab": True}
    
    try:
        # Note: Colab doesn't expose real-time quota info via API
        # This is informational only
        logger.info(
            "Colab quotas: 12 hours runtime/day, 5GB temporary storage, 15GB Drive quota"
        )
        return info
    except Exception as e:
        logger.warning(f"Could not retrieve quota info: {e}")
        return info


# ====== INIT HELPERS ======

def init_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for Colab + local environment.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to log to (in addition to stdout)
    """
    log_format = "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")


def quick_colab_setup() -> Tuple[Path, Dict[str, str], Dict]:
    """
    One-liner Colab setup: auth + credentials + environment.
    
    Returns:
        Tuple of (team_folder, context_dict, gpu_info_dict)
        
    Example:
        team_folder, context, gpu_info = quick_colab_setup()
        print(f"Ready! GPU: {gpu_info.get('gpu_name', 'None')}")
    """
    # Init logging
    init_logging("INFO")
    
    # Install packages
    install_required_packages()
    
    # Auth
    team_folder = setup_colab_auth()
    
    # Context
    context = setup_user_context(team_folder)
    
    # GPU info
    gpu_info = get_gpu_info()
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 COLAB SETUP COMPLETE")
    logger.info(f"Team folder: {team_folder}")
    logger.info(f"User: {context['user_email']}")
    logger.info(f"GPU: {gpu_info.get('gpu_name', 'None')}")
    logger.info("=" * 60)
    
    return team_folder, context, gpu_info
