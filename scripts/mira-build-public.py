#!/usr/bin/env python3
"""The exact public build used by both Pages and release acceptance."""
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
STEPS = ['mira-wire-landing.py', 'mira-build-demo.py', 'mira-build-documents.py --downloads', 'mira-build-catalog.py', 'mira-build-launch.py', 'mira-build-expo.py', 'mira-build-campaign.py', 'mira-build-exhibition.py --downloads', 'mira-wire-analytics.py', 'mira-wire-brand.py', 'mira-wire-navigation.py']
def build():
    for step in STEPS:
        script, *args = step.split()
        subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *args], cwd=ROOT, check=True)
if __name__ == '__main__': build()
