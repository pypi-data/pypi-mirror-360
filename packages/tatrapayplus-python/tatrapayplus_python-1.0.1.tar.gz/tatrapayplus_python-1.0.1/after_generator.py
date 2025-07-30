import shutil
from pathlib import Path

GENERATED_PATH = Path("./tatrapayplus_client/tatra_pay_plus_api_client")
TARGET_MODELS_PATH = Path("./tatrapayplus/models")
TYPES_FILE = "types.py"
ROOT_DIR = Path("./tatrapayplus")

# Create target models directory if not exists
TARGET_MODELS_PATH.mkdir(parents=True, exist_ok=True)

# Move types.py to root
types_src = GENERATED_PATH / TYPES_FILE
types_dest = ROOT_DIR / TYPES_FILE

if types_src.exists():
    shutil.move(str(types_src), str(types_dest))
    print(f"✅ Moved {TYPES_FILE} to {types_dest}")

# Move all model files to tatrapayplus/models directory
models_src_path = GENERATED_PATH / "models"

for file_path in models_src_path.glob("*.py"):
    dest_file_path = TARGET_MODELS_PATH / file_path.name
    shutil.move(str(file_path), str(dest_file_path))
    print(f"✅ Moved model: {file_path.name}")

# Optionally, remove generated client folder
shutil.rmtree("./tatrapayplus_client")
print("✅ Removed generated client folder.")
