#!/bin/bash
# usage: savefree.sh <uuid> <name>
cd /workspace/x-watchlist/dual-run-raw/2026-10-14
cp /workspace/agent-tools/$1.txt free/$2.json
python3 -c "
import sys;sys.path.insert(0,'/workspace/x-watchlist');from parse_x import parse
o,l=parse('free/$2.json');print('$2',len(o.get('data',[])),[p['id'] for p in o.get('data',[])],l,o.get('errors'))
"
date +%T
