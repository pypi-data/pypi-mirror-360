#!/usr/bin/env python
"""Build script for creating a DXT extension package."""

import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


def build_dxt():
    """Build the DXT extension package."""
    print("Building huoshui-fetch DXT extension...")
    
    # Read manifest to get version
    with open("manifest.json", "r") as f:
        manifest = json.load(f)
    
    version = manifest["version"]
    output_name = f"huoshui-fetch-{version}.dxt"
    
    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy necessary files
        files_to_include = [
            "manifest.json",
            "huoshui_fetch/",
            "pyproject.toml",
            "README.md",
            "LICENSE" if Path("LICENSE").exists() else None,
        ]
        
        for file_path in files_to_include:
            if file_path is None:
                continue
                
            src = Path(file_path)
            if src.is_dir():
                shutil.copytree(src, temp_path / src.name)
            else:
                shutil.copy2(src, temp_path / src.name)
        
        # Create requirements.txt from pyproject.toml for compatibility
        print("Extracting requirements...")
        subprocess.run(
            ["uv", "pip", "compile", "pyproject.toml", "-o", str(temp_path / "requirements.txt")],
            check=True
        )
        
        # Create the DXT zip file
        print(f"Creating {output_name}...")
        with zipfile.ZipFile(output_name, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in temp_path.rglob("*"):
                if file_path.is_file() and "__pycache__" not in str(file_path):
                    arcname = file_path.relative_to(temp_path)
                    zf.write(file_path, arcname)
        
        # Get file size
        size_mb = Path(output_name).stat().st_size / (1024 * 1024)
        print(f"✅ Successfully built {output_name} ({size_mb:.2f} MB)")
        
        # Verify the extension
        print("\nVerifying extension structure...")
        with zipfile.ZipFile(output_name, "r") as zf:
            files = zf.namelist()
            
            # Check required files
            required = ["manifest.json", "huoshui_fetch/__main__.py"]
            for req in required:
                if req in files:
                    print(f"  ✓ {req}")
                else:
                    print(f"  ✗ {req} MISSING!")
            
            print(f"\nTotal files: {len(files)}")


if __name__ == "__main__":
    build_dxt()