import os
import sys
from pathlib import Path

main_path = Path("/app/main.py")

if not main_path.exists():
    print("ERROR: /app/main.py not found. Please bind-mount your script.", file=sys.stderr)
    sys.exit(1)

os.execvp("python", ["python", str(main_path)])
