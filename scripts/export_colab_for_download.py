#!/usr/bin/env python3
"""
Script to run ON COLAB to export results for local import.

This script should be added as the final cell in the Colab notebook
to export all test results in a format that can be easily downloaded
and imported locally.

Usage in Colab (add at end of notebook):
    !python -c "import sys; sys.path.insert(0, '/content/SemesterProject'); from scripts.export_colab_for_download import export_results; export_results()"
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime
import os

def export_results(output_name: str = "colab_image_injection_results"):
    """
    Export all test results from Colab in downloadable format.
    
    Args:
        output_name: Name of the export file (without extension)
    """
    print("=" * 60)
    print("📤 EXPORTING RESULTS FROM COLAB")
    print("=" * 60)
    
    # Collect all results
    results_to_export = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": "Colab",
            "export_script": "export_colab_for_download.py"
        },
        "results": {}
    }
    
    # Define locations where results might be stored
    result_locations = [
        '/tmp/test_results.json',
        '/content/SemesterProject/results/image_injection/results.json',
        '/content/image_injection_results.json',
    ]
    
    # Collect variables from notebook globals (these would be set by cells above)
    try:
        import __main__
        notebook_vars = vars(__main__)
        
        # Look for any variables that end with 'results' or 'metrics'
        for var_name, var_value in notebook_vars.items():
            if 'result' in var_name.lower() or 'metric' in var_name.lower():
                print(f"   Found variable: {var_name}")
                results_to_export["results"][var_name] = var_value
    except Exception as e:
        print(f"   (Could not access notebook variables: {e})")
    
    # Try to load from file locations
    for loc in result_locations:
        if os.path.exists(loc):
            print(f"\n📂 Found results at: {loc}")
            try:
                with open(loc, 'r') as f:
                    file_results = json.load(f)
                results_to_export["results"][f"file_{Path(loc).stem}"] = file_results
                print(f"   ✓ Loaded")
            except Exception as e:
                print(f"   ✗ Error loading: {e}")
    
    # Save consolidated results
    print(f"\n💾 Saving consolidated results...")
    export_path = f"/tmp/{output_name}.json"
    with open(export_path, 'w') as f:
        json.dump(results_to_export, f, indent=2, default=str)
    print(f"   ✓ Saved to {export_path}")
    
    # Create ZIP for download
    zip_path = f"/tmp/{output_name}.zip"
    print(f"\n📦 Creating downloadable ZIP...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # Add JSON results
        z.write(export_path, arcname=f"{output_name}.json")
        
        # Add any images if they exist
        attacked_dir = Path('/tmp/attacked_images')
        if attacked_dir.exists():
            print(f"   Adding {len(list(attacked_dir.glob('*.png')))} attacked images...")
            for img in attacked_dir.glob('*.png'):
                z.write(str(img), arcname=f"attacked_images/{img.name}")
        
        test_dir = Path('/tmp/test_images')
        if test_dir.exists():
            print(f"   Adding {len(list(test_dir.glob('*.png')))} test images...")
            for img in test_dir.glob('*.png'):
                z.write(str(img), arcname=f"test_images/{img.name}")
    
    print(f"   ✓ Created {zip_path}")
    
    # Get file size
    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("✅ EXPORT COMPLETE!")
    print("=" * 60)
    print(f"\n📥 To download:\n   colab_results.zip ({zip_size_mb:.1f} MB)")
    print(f"\n📋 Files included:")
    print(f"   - {output_name}.json (results)")
    print(f"   - attacked_images/ (if generated)")
    print(f"   - test_images/ (if generated)")
    print(f"\n💻 To import locally:")
    print(f"   python scripts/load_colab_results.py --zip colab_results.zip")
    print("\n" + "=" * 60)
    
    return zip_path


if __name__ == "__main__":
    # This runs standalone (simulates Colab environment)
    export_results()
