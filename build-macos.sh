#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
python_bin="${project_dir}/.venv/bin/python"
if [[ ! -x "$python_bin" ]]; then
  echo "Project virtual environment not found. Follow the macOS setup in README.md first." >&2
  exit 1
fi

cd "$project_dir"
export PYINSTALLER_CONFIG_DIR="$project_dir/.pyinstaller"
"$python_bin" -m PyInstaller --noconfirm --clean --windowed --specpath "$project_dir/build" --name "Universal IPMI Paste" main.py
echo "Built: $project_dir/dist/Universal IPMI Paste.app"
