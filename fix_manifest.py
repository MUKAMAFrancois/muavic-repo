import os
from pathlib import Path
from mtedx_utils import prepare_mtedx_avsr_manifests

if __name__ == "__main__":
    # 1. CRITICAL FIX: Force the "Current Directory" to be the folder containing this script.
    # This ensures Path("data") correctly finds the folder, no matter where you run the command from.
    os.chdir(Path(__file__).parent)

    # 2. Use "data" (Relative Path)
    # This ensures the output TSV contains "data/muavic/..." instead of "D:/Fall2025..."
    root = Path("data")
    
    mtedx_path = root / "mtedx"
    muavic_path = root / "muavic"

    print("Generating missing .tsv files for German...")
    
    # 3. Generate the manifests
    prepare_mtedx_avsr_manifests(mtedx_path, "de", muavic_path)
    print("Done! Check data/muavic/de/ folder.")