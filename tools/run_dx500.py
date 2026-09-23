#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded fresh-process pipeline, usable on Actions and local Windows/Linux."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--blender',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--skip-render',action='store_true')
    a=ap.parse_args();out=a.output.resolve();blender=a.blender.resolve()
    if not blender.is_file():ap.error('Blender executable not found')
    if out.exists() and any(out.iterdir()):ap.error('Output must be empty; never reuse stale artifacts')
    out.mkdir(parents=True,exist_ok=True)
    version=subprocess.check_output([str(blender),'--version'],text=True,timeout=30).splitlines()[0]
    if version not in ('Blender 5.2.1','Blender 5.2.1 LTS'):
        ap.error('This pilot is pinned to Blender 5.2.1, got '+version)
    source='UNCOMMITTED_LOCAL'
    if shutil.which('git'):
        git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,timeout=15)
        if git.returncode==0:source=git.stdout.strip()
    env=dict(os.environ,SOURCE_COMMIT=source)
    script=str(ROOT/'tools/dx500_pipeline.py')
    stages=[('build',None),('inspect','dx500_handoff.blend'),('inspect-geometry','dx500_geometry_only.blend')]
    if not a.skip_render:stages.append(('render','dx500_handoff.blend'))
    timings={}
    for mode,file in stages:
        cmd=[str(blender),'--background']
        if file:cmd.append(str(out/file))
        cmd+=['--python-exit-code','1','--python',script,'--',mode,str(out)]
        start=time.monotonic()
        with (out/(mode+'.log')).open('w',encoding='utf-8') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        timings[mode]=round(time.monotonic()-start,3)
        if result.returncode:
            print((out/(mode+'.log')).read_text(encoding='utf-8')[-24000:]);raise SystemExit(result.returncode)
    required=['dx500_handoff.blend','dx500_geometry_only.blend','design_manifest.json','material_mapping.json',
              'connection_candidates.csv','blender_validation.json','geometry_validation.json','dx500.mtl',
              'dx500_collision.obj','dx500_wreck.obj']+[f'dx500_LOD{i}.obj' for i in range(4)]
    if not a.skip_render:required += [n+'.png' for n in ('hero','top','side','front','rear','collision')]
    for f in required:
        if not (out/f).is_file() or (out/f).stat().st_size==0:raise RuntimeError('missing/empty '+f)
    for f in ['blender_validation.json','geometry_validation.json']:
        if json.loads((out/f).read_text())['status']!='PASS':raise RuntimeError(f+' not PASS')
    for sourcefile,dest in [('ships/dx500_pilot/PIPELINE.md','START_HERE.md'),('ASSET_LICENSE.md','ASSET_LICENSE.md')]:
        shutil.copy2(ROOT/sourcefile,out/dest)
    shutil.copy2(ROOT/'ships/dx500_pilot/blockout_spec.json',out/'input_blockout_spec.json')
    identity={'source_commit':source,'blender':version,'run_id':os.getenv('GITHUB_RUN_ID'),
              'stages_seconds':timings,'rendered':not a.skip_render,
              'status':'BLENDER_HANDOFF_VALIDATED_NOT_GAME_READY',
              'script_sha256':hashlib.sha256(Path(script).read_bytes()).hexdigest()}
    (out/'build_identity.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
    sums=[]
    for f in sorted(out.iterdir()):
        if f.is_file() and f.name!='SHA256SUMS.txt':sums.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name)
    (out/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n',encoding='utf-8')
    print(json.dumps(identity,indent=2))
    print((out/'blender_validation.json').read_text())

if __name__=='__main__':main()
