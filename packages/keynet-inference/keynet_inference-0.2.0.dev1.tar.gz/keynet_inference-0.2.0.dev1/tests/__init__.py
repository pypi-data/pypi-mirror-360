import sys
from pathlib import Path

# Add the parent directory's keynet_inference to the path
# This allows direct imports like `from function import ...`
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / "keynet_inference"))
