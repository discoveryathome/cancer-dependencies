"""Compatibility entry point for the shared historical program evidence check."""
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    runpy.run_path(str(ROOT / 'research/program-v2-20261021/check_manifest.py'), run_name='__main__')
