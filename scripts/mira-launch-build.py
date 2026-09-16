#!/usr/bin/env python3
"""Build the canonical research/product dashboard, or a separate private overlay."""
from pathlib import Path
import argparse
import importlib.util
import os

ROOT=Path(__file__).resolve().parents[1]

def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

_source=load('mira_launch_source','mira-launch-source.py')
_ops=load('mira_launch_operations','mira-launch-operations.py')

def __getattr__(name):
    return getattr(_source,name)

def build(root,source_commit):
    root=Path(root)
    _ops.protect_generated_register(root)
    return _ops.augment_public(root,_source.build(root,source_commit))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--source-commit',default=os.environ.get('GITHUB_SHA','local-uncommitted'))
    parser.add_argument('--operator-state',type=Path)
    parser.add_argument('--private-output',type=Path)
    args=parser.parse_args()
    if bool(args.operator_state)!=bool(args.private_output):
        parser.error('--operator-state and --private-output must be supplied together')
    if args.operator_state:
        _ops.private_overlay(args.root,args.operator_state,args.private_output)
    else:
        build(args.root,args.source_commit)
