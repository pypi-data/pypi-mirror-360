#!/usr/bin/env python3
"""Setup script for claude-pyhooks package."""

import subprocess
import sys
from pathlib import Path


def clean_build():
    """Clean build artifacts."""
    import shutil
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed {path}")


def build_package():
    """Build the package using python -m build."""
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("✅ Package built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


def check_package():
    """Check the built package using twine."""
    try:
        subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"], 
                      shell=True, check=True)
        print("✅ Package validation passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Package validation failed: {e}")
        sys.exit(1)


def upload_test():
    """Upload to TestPyPI."""
    try:
        subprocess.run([
            sys.executable, "-m", "twine", "upload", 
            "--repository", "testpypi", "dist/*"
        ], shell=True, check=True)
        print("✅ Uploaded to TestPyPI successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ TestPyPI upload failed: {e}")
        sys.exit(1)


def upload_prod():
    """Upload to production PyPI."""
    try:
        subprocess.run([
            sys.executable, "-m", "twine", "upload", "dist/*"
        ], shell=True, check=True)
        print("✅ Uploaded to PyPI successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ PyPI upload failed: {e}")
        sys.exit(1)


def main():
    """Main setup function."""
    if len(sys.argv) < 2:
        print("Usage: python setup.py <command>")
        print("Commands:")
        print("  clean       - Clean build artifacts")
        print("  build       - Build package")
        print("  check       - Check package validity")
        print("  test-upload - Upload to TestPyPI")
        print("  upload      - Upload to production PyPI")
        print("  all         - Clean, build, and check")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "clean":
        clean_build()
    elif command == "build":
        build_package()
    elif command == "check":
        check_package()
    elif command == "test-upload":
        upload_test()
    elif command == "upload":
        upload_prod()
    elif command == "all":
        clean_build()
        build_package()
        check_package()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()