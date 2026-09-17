#!/usr/bin/env python3
"""Prepare a sanitized static WEGC/MIRA deployment; never upload working credentials."""
from pathlib import Path
import shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for cmd in [['scripts/mira-apply-reviewed-checkpoint.py'],['scripts/mira-wire-landing.py'],['scripts/mira-build-demo.py'],['scripts/mira-build-documents.py','--downloads'],['scripts/mira-build-launch.py'],['scripts/mira-build-expo.py']]:subprocess.run([sys.executable,*cmd],cwd=ROOT,check=True)
out=ROOT/'_mira_site'
if out.exists():shutil.rmtree(out)
out.mkdir()
excluded={'.git','.github','.cursor','.netlify','node_modules','_site','_mira_site','project-bible','tests','scripts','cloudflare-worker','netlify','mira-recovery-manifest.json','netlify.toml','openai.chatgpt-0.5.53-universal.vsix'}
for item in ROOT.iterdir():
 if item.name in excluded or item.name.startswith('.')or item.suffix in {'.zip','.log','.py','.sqlite','.db','.env'}:continue
 if item.is_symlink():raise ValueError('Refuse symlink: '+item.name)
 if item.is_dir():shutil.copytree(item,out/item.name,ignore=shutil.ignore_patterns('__pycache__','.DS_Store','.env','*.sqlite','*.db','*.log'))
 else:shutil.copy2(item,out/item.name)
assert not(out/'project-bible').exists()
assert(out/'mira/phuket/index.html').exists()
print('Static files prepared; no database or authentication deployed.')
