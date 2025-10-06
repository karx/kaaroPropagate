#!/usr/bin/env python3
"""
Download JPL SPICE kernels for planetary ephemerides.

Downloads the necessary kernels from NASA NAIF server.
"""

import os
import requests
from pathlib import Path


# NAIF server base URL
NAIF_URL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels"

# Kernels to download
KERNELS = {
    # Leap seconds kernel (required)
    'lsk/naif0012.tls': 'naif0012.tls',
    
    # Planetary constants
    'pck/pck00011.tpc': 'pck00011.tpc',
    
    # Planetary ephemeris (DE440 - modern, accurate)
    # Note: This is a large file (~100MB)
    'spk/planets/de440.bsp': 'de440.bsp',
}


def download_kernel(url: str, output_path: Path, force: bool = False):
    """Download a SPICE kernel file."""
    if output_path.exists() and not force:
        print(f"✓ {output_path.name} already exists")
        return
    
    print(f"Downloading {output_path.name}...")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"  Progress: {percent:.1f}%", end='\r')
        
        print(f"✓ Downloaded {output_path.name} ({downloaded / 1024 / 1024:.1f} MB)")
        
    except Exception as e:
        print(f"✗ Failed to download {output_path.name}: {e}")
        if output_path.exists():
            output_path.unlink()


def main():
    """Download all required SPICE kernels."""
    # Determine kernel directory
    script_dir = Path(__file__).parent
    kernel_dir = script_dir.parent / "data" / "kernels"
    kernel_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("SPICE Kernel Downloader")
    print("=" * 60)
    print(f"\nKernel directory: {kernel_dir}")
    print(f"Downloading {len(KERNELS)} kernels...\n")
    
    # Download each kernel
    for remote_path, local_name in KERNELS.items():
        url = f"{NAIF_URL}/{remote_path}"
        output_path = kernel_dir / local_name
        download_kernel(url, output_path)
    
    print("\n" + "=" * 60)
    print("Download complete!")
    print("=" * 60)
    
    # List downloaded files
    print("\nDownloaded kernels:")
    for kernel_file in sorted(kernel_dir.glob("*")):
        size_mb = kernel_file.stat().st_size / 1024 / 1024
        print(f"  {kernel_file.name:20s} ({size_mb:6.1f} MB)")
    
    print("\nYou can now use these kernels with SPICEYPY.")
    print("See backend/app/data/spice_loader.py for usage examples.")


if __name__ == "__main__":
    main()
