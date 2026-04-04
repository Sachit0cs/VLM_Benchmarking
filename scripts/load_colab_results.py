#!/usr/bin/env python3
"""
Load and process results from Colab execution.

This script imports test results that were exported from the Colab notebook
and prepares them for local analysis and report generation.

Usage:
    python load_colab_results.py --zip colab_results.zip
    python load_colab_results.py --folder ~/Downloads/ImageInjection_Results/
    python load_colab_results.py --json results.json
"""

import json
import zipfile
import argparse
from pathlib import Path
from typing import Dict, Any, List
import sys

class ColabResultsLoader:
    """Load and normalize results exported from Colab."""
    
    def __init__(self, output_dir: str = "results/colab_imported"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
    
    def load_from_zip(self, zip_path: str) -> Dict[str, Any]:
        """
        Extract and load results from Colab-exported ZIP.
        
        Args:
            zip_path: Path to exported ZIP file from Colab
            
        Returns:
            Loaded results dictionary
        """
        print(f"📦 Loading results from {zip_path}...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # List contents
                files = z.namelist()
                print(f"   Found {len(files)} files:")
                for f in files[:5]:
                    print(f"     - {f}")
                if len(files) > 5:
                    print(f"     ... and {len(files)-5} more")
                
                # Extract to temp folder
                extract_path = self.output_dir / "colab_export"
                z.extractall(extract_path)
                print(f"\n✓ Extracted to {extract_path}")
                
                # Load JSON results
                results_data = self._find_and_load_json(extract_path)
        except zipfile.BadZipFile:
            print(f"❌ Invalid ZIP file: {zip_path}")
            return {}
        
        self.results = results_data
        self._save_normalized(results_data)
        return results_data
    
    def load_from_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Load results from extracted folder.
        
        Args:
            folder_path: Path to folder containing results
            
        Returns:
            Loaded results dictionary
        """
        print(f"📂 Loading results from folder: {folder_path}")
        folder = Path(folder_path)
        
        if not folder.exists():
            print(f"❌ Folder not found: {folder_path}")
            return {}
        
        results_data = self._find_and_load_json(folder)
        self.results = results_data
        self._save_normalized(results_data)
        return results_data
    
    def load_from_json(self, json_path: str) -> Dict[str, Any]:
        """
        Load results directly from JSON file.
        
        Args:
            json_path: Path to JSON results file
            
        Returns:
            Loaded results dictionary
        """
        print(f"📄 Loading results from JSON: {json_path}")
        json_file = Path(json_path)
        
        if not json_file.exists():
            print(f"❌ File not found: {json_path}")
            return {}
        
        try:
            with open(json_file, 'r') as f:
                results_data = json.load(f)
            print(f"✓ Loaded JSON with {len(str(results_data))} bytes")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return {}
        
        self.results = results_data
        self._save_normalized(results_data)
        return results_data
    
    def _find_and_load_json(self, search_path: Path) -> Dict[str, Any]:
        """
        Recursively find and load JSON result files.
        
        Args:
            search_path: Path to search for JSON files
            
        Returns:
            Combined results from all JSON files found
        """
        all_results = {}
        json_files = list(search_path.rglob("*.json"))
        
        print(f"\n🔍 Found {len(json_files)} JSON files:")
        
        for json_file in json_files:
            rel_path = json_file.relative_to(search_path)
            print(f"   - {rel_path}")
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Merge results
                if isinstance(data, dict):
                    if "results" in data:
                        all_results.update(data["results"])
                    else:
                        all_results.update(data)
                
            except json.JSONDecodeError:
                print(f"      ⚠️  Skipped invalid JSON")
        
        if not all_results:
            print(f"❌ No valid JSON data found")
        else:
            print(f"✓ Loaded data from {len(json_files)} files")
        
        return all_results
    
    def _save_normalized(self, results: Dict[str, Any]):
        """
        Save normalized results in standard format.
        
        Args:
            results: Results dictionary to save
        """
        # Save as JSON for easy loading
        output_file = self.output_dir / "colab_results_normalized.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Saved normalized results to: {output_file}")
        
        # Print summary
        if results:
            print(f"\n📊 Results Summary:")
            self._print_summary(results)
    
    def _print_summary(self, results: Dict[str, Any], indent: int = 0):
        """Pretty print results summary."""
        prefix = "   " * indent
        
        if isinstance(results, dict):
            # Show top-level keys
            for key, value in list(results.items())[:5]:
                if isinstance(value, dict):
                    print(f"{prefix}📌 {key}:")
                    self._print_summary(value, indent + 1)
                elif isinstance(value, (int, float)):
                    print(f"{prefix}   {key}: {value:.4f}" if isinstance(value, float) else f"{prefix}   {key}: {value}")
                else:
                    print(f"{prefix}   {key}: {type(value).__name__}")
            
            if len(results) > 5:
                print(f"{prefix}... and {len(results)-5} more")


def main():
    parser = argparse.ArgumentParser(
        description="Load and process results from Colab execution"
    )
    
    parser.add_argument(
        "--zip",
        type=str,
        help="Path to ZIP file exported from Colab"
    )
    parser.add_argument(
        "--folder",
        type=str,
        help="Path to folder containing extracted Colab results"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="Path to JSON file with Colab results"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/colab_imported",
        help="Output directory for normalized results"
    )
    
    args = parser.parse_args()
    
    if not any([args.zip, args.folder, args.json]):
        print("❌ Please provide one of: --zip, --folder, or --json")
        parser.print_help()
        sys.exit(1)
    
    loader = ColabResultsLoader(output_dir=args.output)
    
    if args.zip:
        results = loader.load_from_zip(args.zip)
    elif args.folder:
        results = loader.load_from_folder(args.folder)
    elif args.json:
        results = loader.load_from_json(args.json)
    
    if results:
        print(f"\n✅ Successfully loaded Colab results!")
        print(f"📍 Ready for local report generation")
    else:
        print(f"❌ Failed to load results")
        sys.exit(1)


if __name__ == "__main__":
    main()
