#!/usr/bin/env python3
"""Publish campaign layouts without colliding with a concurrently released route.

The original layout module is preserved byte-for-byte. This explicit route
configuration reserves /business/ for the earlier independent implementation.
"""
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mira_campaign_layouts', Path(__file__).with_name('mira-campaign-layouts.py'))
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)
if set(layout.VARIANTS) != {'go', 'business', 'corporate'}:
    raise ValueError('Unexpected layout registry; reconcile routes before publication')
VARIANTS = {'go': layout.VARIANTS['go'], 'practical': layout.VARIANTS['business'], 'corporate': layout.VARIANTS['corporate']}
layout.VARIANTS = VARIANTS
build_page = layout.build_page

def build(root=ROOT):
    return layout.build(root)

if __name__ == '__main__':
    build()
