"""Hands the finished front page to the grader."""

import os
import shutil
import hashlib

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(base_dir, "entry.png")
    
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    
    dest_path = os.path.join(output_dir, "entry.png")
    shutil.copy2(source_path, dest_path)
    
    with open(dest_path, "rb") as f:
        data = f.read()
        
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG signature")
        
    byte_count = len(data)
    sha256_hash = hashlib.sha256(data).hexdigest()[:12]
    
    print(f"Bytes: {byte_count}, SHA256 (12 chars): {sha256_hash}")

if __name__ == "__main__":
    main()
