import sys
from pathlib import Path

root = Path(r"C:\Users\sreev\OneDrive\Desktop\smart-campus-data-hub")
sys.path.insert(0, str(root.resolve()))

from scripts.run_pipeline import run_pipeline

print("RUN_RESULT:", run_pipeline())
