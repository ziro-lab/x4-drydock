#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""DX-500 Blender-only handoff. No Egosoft binary, asset or exporter emulation.

blender -b --python-exit-code 1 --python tools/dx500_pipeline.py -- build OUT
blender -b OUT/dx500_handoff.blend --python-exit-code 1 --python tools/dx500_pipeline.py -- inspect OUT
xvfb-run -a blender -b OUT/dx500_handoff.blend --python-exit-code 1 --python tools/dx500_pipeline.py -- render OUT
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'ships/dx500_pilot/blockout_spec.json'
PALETTE = {'hull': (.68,.73,.74,1), 'frame': (.075,.10,.12,1),
           'cargo': (.73,.31,.075,1), 'dark': (.12,.17,.20,1),
           'glass': (.065,.34,.40,1)}
AXES = 'metres; +Y bow, +X starboard, +Z up; legacy (x,y,z) -> (y,-x,z)'
COLS = ['LOD0','LOD1','LOD2','LOD3','COLLISION_SOURCE','CONVEX_SOURCE','WRECK_SOURCE',
        'EDITABLE_SOURCE','EQUIPMENT_VIEW_ONLY','RESERVES_VIEW_ONLY','CANDIDATES','CAMERAS']

def vec(value, positive=False):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('expected three finite numbers')
    if any(isinstance(x, bool) or not isinstance(x, (int,float)) or not math.isfinite(x) for x in value):
        raise ValueError('expected three finite numbers')
    if positive and any(x <= 0 for x in value):
        raise ValueError('size must be positive')
    return value

def load_spec(path=SPEC):
    s = json.loads(Path(path).read_text(encoding='utf-8'))
    if s.get('schema_version') != 1 or s.get('units') != 'm':
        raise ValueError('unsupported spec version/units')
    mods = s.get('modules', [])
    if len(mods) != 8 or [m.get('name','')[:3] for m in mods] != [f'M{i:02d}' for i in range(1,9)]:
        raise ValueError('this pilot requires ordered M01-M08 modules')
    names=[]
    for m in mods:
        names.append(m['name']); vec(m['center']); vec(m['size'], True)
        b=m.get('bevel',0)
        if isinstance(b,bool) or not isinstance(b,(int,float)) or not math.isfinite(b) or b<0:
            raise ValueError('invalid bevel')
    if len(names)!=len(set(names)):
        raise ValueError('duplicate module name')
    if len(s.get('engines',[])) != 4:
        raise ValueError('pilot requires four legacy engine slots')
    for e in s['engines']:
        vec(e['center'])
    return s

def xyz(old):
    return (old[1], -old[0], old[2])

def overlap(a, b, eps=1e-5):
    return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i]) > eps for i in range(3))

def bounds(center,size):
    return ([center[i]-size[i]/2 for i in range(3)], [center[i]+size[i]/2 for i in range(3)])

def primitive(name, c, d, mat='hull', bevel=0, physics=True, level=3):
    return dict(name=name, center=list(c), size=list(d), material=mat,
                bevel=bevel, physics=physics, max_lod=level)

def design(s):
    """Fixed pilot edits are explicit: open M05, external mounts, no bespoke docks."""
    p=[]
    for m in s['modules']:
        c=xyz(m['center']); d=(m['size'][1],m['size'][0],m['size'][2])
        if m['name'].startswith('M05'):
            # Open lift/hangar well. Never replace this with one enclosing collision box.
            for side in (-1,1):
                p.append(primitive(f'M05_cargo_{side}',(side*92.5,-27.5,0),(75,85,160),'cargo',3))
            for y in (-66,11):
                p.append(primitive(f'M05_end_{y}',(0,y,0),(110,8,160),'frame',0))
            p.append(primitive('M05_floor',(0,-27.5,-75),(110,69,10),'frame'))
        else:
            p.append(primitive(m['name'],c,d,'frame' if m['name'].startswith('M07') else 'hull',3))
        # Side inset panels and repeated ribs: simple boxes, not fragile boolean detail.
        for side in (-1,1):
            p.append(primitive(m['name']+f'_panel_{side}',(side*(d[0]/2+.2),c[1],0),
                               (.4,max(8,d[1]-12),d[2]-24),'dark',0,False,1))
            for j in (-1,0,1):
                p.append(primitive(m['name']+f'_rib_{side}_{j}',(side*(d[0]/2+.6),c[1]+j*(d[1]-12)/3,0),
                                   (1.2,2,d[2]-8),'cargo' if m['name'].startswith('M08') else 'hull',0,False,0))
    for a,b in zip(s['modules'],s['modules'][1:]):
        start=a['center'][0]+a['size'][0]/2-2.5
        end=b['center'][0]-b['size'][0]/2+2.5
        for y,z in s['connector_pattern']['beam_offsets_yz_m']:
            p.append(primitive(f'link_{a["name"]}_{y}_{z}',xyz(((start+end)/2,y,z)),(8,end-start,8),'frame',.5))
    # Front sensor fascia and bridge glazing remain in every LOD.
    p += [primitive('sensor_face',(0,250.3,0),(96,.6,56),'dark',0,False),
          primitive('bridge_glass',(0,195.3,26),(128,.6,24),'glass',0,False)]
    for side in (-1,1):
        for j in range(4):
            p.append(primitive(f'hab_window_{side}_{j}',(side*121,93+j*14,35),(1,8,7),'glass',0,False,0))
        p.append(primitive(f'shield_pedestal_{side}',(side*62,47.5,79),(42,50,8),'frame'))
        for y in (115,-105):
            p.append(primitive(f'turret_pedestal_{side}_{y}',(side*121,y,0),(2,30,30),'frame'))
    # Engine attachment plates are in FRONT of the stern mounting plane.
    for x in (-85,85):
        for z in (-45,45):
            p.append(primitive(f'engine_mount_{x}_{z}',(x,-248,z),(58,4,58),'dark'))
    r=[dict(name='hangar_void',center=[0,-27.5,6],size=[100,60,152],kind='cavity'),
       dict(name='dock_upper',center=[0,-27.5,136],size=[110,74,108],kind='corridor'),
       dict(name='approach_forward',center=[0,172.5,160],size=[100,400,80],kind='corridor'),
       dict(name='departure_aft',center=[0,-227.5,160],size=[100,400,80],kind='corridor')]
    c=[]
    def slot(name,kind,pos,normal,size=None,center=None):
        c.append(dict(name=name,kind=kind,position=pos,normal=normal,
                      group_intent=kind,macro=None,tags=None,status='LOCAL_TOOL_CONFIRMATION_REQUIRED'))
        if size:
            r.append(dict(name=name,center=center,size=size,kind='equipment'))
    for x in (-85,85):
        for z in (-45,45):
            slot(f'cand_engine_{len(c)+1:02d}','engine_l',[x,-250,z],[0,-1,0],[56,56,56],[x,-278,z])
    for side in (-1,1):
        slot(f'cand_shield_{"port" if side<0 else "starboard"}','shield_l',[side*62,47.5,83],[0,0,1],[38,68,20],[side*62,47.5,93])
        for y in (115,-105):
            slot(f'cand_turret_{"port" if side<0 else "starboard"}_{"fore" if y>0 else "aft"}','turret_m',[side*122,y,0],[side,0,0],[50,40,40],[side*147,y,0])
    for name,pos in [('cockpit',[0,175,65]),('playercontrol',[0,175,65]),('dynamicroom',[0,175,65]),
                     ('aimtarget',[0,0,0]),('countermeasures',[0,-245,-70]),
                     ('dockarea',[0,-27.5,82]),('shipstorage',[0,-27.5,-5]),('dock_xs',[0,230,0])]:
        slot('cand_'+name,name,pos,[0,0,1])
    return p,r,c

def design_check(p,r):
    clashes=[]
    for zone in r:
        for part in p:
            if overlap(bounds(zone['center'],zone['size']),bounds(part['center'],part['size'])):
                clashes.append([zone['name'],part['name']])
    if clashes:
        raise ValueError('reserved-volume intrusion: '+json.dumps(clashes))
    return {'reserved_hull_intersections':clashes,'authority':'DESIGN_AABB_ONLY_NOT_EGOSOFT_CLEARANCE'}

def jsonout(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def coll(name):
    v=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(v); return v

def move(o,c):
    for old in list(o.users_collection): old.objects.unlink(o)
    c.objects.link(o)

def vertex_data(o):
    me=o.data
    uv=me.uv_layers.get('uv1') or me.uv_layers.new(name='uv1')
    lo=[min(v.co[i] for v in me.vertices) for i in range(3)]
    hi=[max(v.co[i] for v in me.vertices) for i in range(3)]
    # Tiled planar UVs per face. Intended for flat/tile materials, not unique baked paint.
    for f in me.polygons:
        axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
        for li in f.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=tuple((v[i]-lo[i])/max(hi[i]-lo[i],1e-8) for i in axes)
    for name,color in [('col',(1,1,1,1)),('paintmodmask',(0,0,0,1))]:
        layer=me.color_attributes.get(name) or me.color_attributes.new(name=name,type='BYTE_COLOR',domain='CORNER')
        for cell in layer.data: cell.color=color

def box(part, collection, lod=0, editable=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=part['center'])
    o=bpy.context.object; o.name=part['name']; o.scale=part['size']
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    width=part['bevel'] if lod<2 else (min(part['bevel'],1.5) if lod==2 else 0)
    if width:
        mod=o.modifiers.new('EdgeChamfer','BEVEL');mod.width=width;mod.segments=2 if lod==0 else 1
        if not editable: bpy.ops.object.modifier_apply(modifier=mod.name)
    if not editable:
        mod=o.modifiers.new('Triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(bpy.data.materials['preview_'+part['material']])
    o['part_id']=part['name'];o['physics_source']=part['physics'];vertex_data(o);move(o,collection)
    return o

def join(objects,name,collection):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR');move(o,collection);return o

def world_bounds(o):
    from mathutils import Vector
    vv=[o.matrix_world@Vector(v) for v in o.bound_box]
    return ([min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)])

def obj_write(path,objects):
    """Minimal native-coordinate OBJ escape hatch; no glTF/OBJ axis conversion magic."""
    lines=['# DX500 metres; +Y bow; +Z up','mtllib dx500.mtl']; off=0; uoff=0; noff=0
    for o in objects:
        me=o.data;me.calc_loop_triangles();uv=me.uv_layers['uv1']
        lines.append('o '+o.name)
        for v in me.vertices:
            q=o.matrix_world@v.co;lines.append('v '+' '.join(f'{x:.7g}' for x in q))
        for u in uv.data: lines.append(f'vt {u.uv.x:.7g} {u.uv.y:.7g}')
        for f in me.polygons: lines.append('vn '+' '.join(f'{x:.7g}' for x in f.normal))
        for f in me.polygons:
            lines.append('usemtl '+me.materials[f.material_index].name)
            lines.append('f '+' '.join(f'{me.loops[li].vertex_index+off+1}/{li+uoff+1}/{f.index+noff+1}' for li in f.loop_indices))
        off+=len(me.vertices);uoff+=len(me.loops);noff+=len(me.polygons)
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def build(out):
    from mathutils import Vector,Matrix
    s=load_spec();p,r,c=design(s);design_check(p,r)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    if sc.world is None:sc.world=bpy.data.worlds.new('PreviewWorld')
    sc['axis_contract']=AXES;sc['status']='X4_AWARE_BLENDER_HANDOFF_CANDIDATE'
    sc['source_commit']=os.getenv('SOURCE_COMMIT','UNCOMMITTED_LOCAL')
    sc['spec_sha256']=hashlib.sha256(SPEC.read_bytes()).hexdigest()
    cs={n:coll(n) for n in COLS}
    for key,color in PALETTE.items():
        m=bpy.data.materials.new('preview_'+key);m.diffuse_color=color;m.use_nodes=True
        bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color
        bs.inputs['Metallic'].default_value=.4;bs.inputs['Roughness'].default_value=.5
        m['x4_material_mapping']='UNRESOLVED_REMAP_IN_LOCAL_TOOLS'
    for level in range(4):
        cc=cs[f'LOD{level}']; groups={k:[] for k in PALETTE}
        for part in p:
            if part['max_lod']>=level: groups[part['material']].append(box(part,cc,level))
        for key,objects in groups.items():
            if objects: join(objects,'part_dx500_'+key+('' if level==0 else f'.LOD{level}'),cc)
    for part in p: box(part,cs['EDITABLE_SOURCE'],0,True)
    # Independent convex boxes preserve the hangar cavity. These are NOT cooked Jolt hulls.
    for i,part in enumerate(q for q in p if q['physics']):
        item=dict(part,bevel=0,material='frame')
        o=box(item,cs['CONVEX_SOURCE'],3);o.name=f'convex_source_{i:03d}'
    for o in list(cs['CONVEX_SOURCE'].objects):
        q=o.copy();q.data=o.data.copy();cs['COLLISION_SOURCE'].objects.link(q)
    join(list(cs['COLLISION_SOURCE'].objects),'part_dx500.col',cs['COLLISION_SOURCE'])
    for o in cs['LOD2'].objects:
        q=o.copy();q.data=o.data.copy();q.name=o.name.replace('.LOD2','.wreck');cs['WRECK_SOURCE'].objects.link(q)
    # A deliberately simple unchanged-silhouette wreck source, not a damage simulation.
    wm=bpy.data.materials.new('preview_wreck');wm.diffuse_color=(.075,.065,.055,1)
    for o in cs['WRECK_SOURCE'].objects:
        o.data.materials.clear();o.data.materials.append(wm)
        for f in o.data.polygons:f.material_index=0
    for zone in r:
        o=bpy.data.objects.new('RESERVE_'+zone['name'],None);cs['RESERVES_VIEW_ONLY'].objects.link(o)
        o.empty_display_type='CUBE';o.location=zone['center'];o.scale=[x/2 for x in zone['size']]
        o['not_official_clearance']=True
    for slot in c:
        o=bpy.data.objects.new(slot['name'],None);cs['CANDIDATES'].objects.link(o);o.location=slot['position']
        z=Vector(slot['normal']);y=Vector((0,1,0));y-=z*y.dot(z)
        if y.length<.01:y=Vector((0,0,1));y-=z*y.dot(z)
        y.normalize();x=y.cross(z);o.rotation_mode='QUATERNION';o.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion()
        o.empty_display_type='ARROWS';o.empty_display_size=12;o['kind']=slot['kind'];o['NOT_EGOSOFT_TAGGED']=True
        slot['quaternion_wxyz']=list(o.rotation_quaternion)
    # Removable display equipment. Never included in hull OBJ/collision/geometry-only .blend.
    for i,slot in enumerate(c):
        pos=slot['position'];kind=slot['kind']
        if kind=='engine_l':
            box(primitive(f'VIEW_engine_{i}',(pos[0],-270,pos[2]),(46,40,46),'frame',3),cs['EQUIPMENT_VIEW_ONLY'])
            box(primitive(f'VIEW_nozzle_{i}',(pos[0],-291,pos[2]),(34,2,34),'glass'),cs['EQUIPMENT_VIEW_ONLY'])
        elif kind=='shield_l':
            box(primitive(f'VIEW_shield_{i}',(pos[0],pos[1],89),(32,60,10),'dark',2),cs['EQUIPMENT_VIEW_ONLY'])
        elif kind=='turret_m':
            sign=1 if pos[0]>0 else -1
            box(primitive(f'VIEW_turret_{i}',(sign*135,pos[1],0),(22,22,22),'dark',2),cs['EQUIPMENT_VIEW_ONLY'])
            box(primitive(f'VIEW_barrel_{i}',(sign*153,pos[1],0),(16,4,4),'frame'),cs['EQUIPMENT_VIEW_ONLY'])
    box(primitive('VIEW_dock_lift',(0,-27.5,72),(98,58,2),'dark'),cs['EQUIPMENT_VIEW_ONLY'])
    box(primitive('VIEW_landing_mark',(0,-27.5,73.2),(35,2,.2),'cargo'),cs['EQUIPMENT_VIEW_ONLY'])
    for name,cc in cs.items():
        cc.hide_render=name not in ('LOD0','EQUIPMENT_VIEW_ONLY','CAMERAS')
        cc.hide_viewport=name in ('LOD1','LOD2','LOD3','COLLISION_SOURCE','CONVEX_SOURCE','WRECK_SOURCE','EDITABLE_SOURCE','RESERVES_VIEW_ONLY')
    bpy.ops.object.select_all(action='DESELECT')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.clip_end=5000;area.spaces.active.region_3d.view_distance=800
                area.spaces.active.shading.color_type='MATERIAL'
    text=bpy.data.texts.new('READ_ME_FIRST.txt')
    text.write('DX500 Blender handoff; NOT an installable MOD.\n'+AXES+'\nUse dx500_geometry_only.blend for local exporter setup.\nEquipment, dock floor and reservations are display-only.\nAll game material mappings / Connections / Jolt cooking remain local work.\n')
    report={'status':sc['status'],'axes':AXES,'source_commit':sc['source_commit'],'spec_sha256':sc['spec_sha256'],
            'blender':bpy.app.version_string,'parts':p,'reserved_volumes':r,'candidates':c,
            'design_validation':design_check(p,r),
            'changes_from_blockout':['legacy -X bow -> +Y bow','open M05 hangar cavity','two shield / four turret reserves','dock placeholder relocated over M05 cavity'],
            'local_unverified':['Mod Tools version compatibility','current clearance','materials / vertex-channel semantics','Connections / groups / macro binding','Jolt cooking','export / conversion','package / acquisition','X4 runtime']}
    jsonout(out/'design_manifest.json',report)
    jsonout(out/'material_mapping.json',{'policy':'preview only; remap to current installed-game materials first; no invented library IDs',
        'materials':[{'preview':m.name,'rgba':list(m.diffuse_color),'game_material':None} for m in bpy.data.materials]})
    with (out/'connection_candidates.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['name','kind','x_m','y_m','z_m','normal_x','normal_y','normal_z','state'])
        for q in c:w.writerow([q['name'],q['kind'],*q['position'],*q['normal'],q['status']])
    for level in range(4):obj_write(out/f'dx500_LOD{level}.obj',list(cs[f'LOD{level}'].objects))
    obj_write(out/'dx500_collision.obj',list(cs['COLLISION_SOURCE'].objects))
    obj_write(out/'dx500_wreck.obj',list(cs['WRECK_SOURCE'].objects))
    (out/'dx500.mtl').write_text('\n'.join('newmtl '+m.name+'\nKd '+' '.join(str(x) for x in m.diffuse_color[:3])+'\nillum 2\n' for m in bpy.data.materials),encoding='utf-8')
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'dx500_handoff.blend'),compress=True)
    keep={'LOD0','LOD1','LOD2','LOD3','COLLISION_SOURCE','CONVEX_SOURCE','WRECK_SOURCE'}
    for name,cc in cs.items():
        if name not in keep:
            for o in list(cc.objects):bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.collections.remove(cc)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'dx500_geometry_only.blend'),compress=True)

def inspect(out, geometry_only=False):
    import bmesh
    from mathutils import Vector
    # Hidden collections are not evaluated after reopen; expose them before querying matrix_world.
    # Inspection is read-only and never saves these temporary visibility changes.
    for collection in bpy.data.collections: collection.hide_viewport=False
    bpy.context.view_layer.update();errors=[];stats={}
    for level in range(4):
        name=f'LOD{level}';cc=bpy.data.collections.get(name)
        if not cc or not cc.objects:errors.append('missing '+name);continue
        stats[name]=sum(len(o.data.polygons) for o in cc.objects)
    if len(stats)!=4 or not all(stats.get(f'LOD{i}',0)>stats.get(f'LOD{i+1}',0)>0 for i in range(3)):
        errors.append('LOD counts must decrease strictly')
    for name in ('COLLISION_SOURCE','CONVEX_SOURCE','WRECK_SOURCE'):
        if not bpy.data.collections.get(name) or not bpy.data.collections[name].objects:errors.append('missing '+name)
    for ccname in ('COLLISION_SOURCE','CONVEX_SOURCE'):
        for ob in bpy.data.collections[ccname].objects:
            adjacency={v.index:set() for v in ob.data.vertices}
            for e in ob.data.edges:
                a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
            unseen=set(adjacency)
            while unseen:
                stack=[unseen.pop()];island=[]
                while stack:
                    idx=stack.pop();island.append(ob.matrix_world@ob.data.vertices[idx].co)
                    nxt=adjacency[idx]&unseen;unseen-=nxt;stack.extend(nxt)
                ib=([min(v[i] for v in island) for i in range(3)],[max(v[i] for v in island) for i in range(3)])
                if overlap(ib,bounds([0,-27.5,6],[100,60,152])):errors.append(ccname+' fills hangar cavity')
    for o in bpy.data.objects:
        if o.type!='MESH' or 'EDITABLE_SOURCE' in {c.name for c in o.users_collection}:continue
        if any(not math.isfinite(v) for vert in o.data.vertices for v in vert.co):errors.append(o.name+' nonfinite')
        if any(abs(v-1)>1e-6 for v in o.scale) or o.rotation_euler.to_matrix().determinant()<0:errors.append(o.name+' transform')
        if len(o.modifiers):errors.append(o.name+' unapplied modifier')
        if 'uv1' not in o.data.uv_layers or 'col' not in o.data.color_attributes:errors.append(o.name+' vertex data')
        if any(len(f.vertices)!=3 or f.area<1e-8 for f in o.data.polygons):errors.append(o.name+' degenerate / nontriangle')
        if any(not math.isfinite(v) for u in o.data.uv_layers['uv1'].data for v in u.uv):errors.append(o.name+' bad UV')
        bm=bmesh.new();bm.from_mesh(o.data)
        if any(not e.is_manifold for e in bm.edges):errors.append(o.name+' open/nonmanifold edges')
        if bm.calc_volume(signed=True)<=0:errors.append(o.name+' nonpositive signed volume')
        bm.free()
    manifest=json.loads((out/'design_manifest.json').read_text(encoding='utf-8'))
    if bpy.context.scene.get('source_commit')!=manifest['source_commit']:errors.append('source identity')
    if bpy.context.scene.unit_settings.scale_length!=1:errors.append('units')
    # Inspect actual saved EDITABLE objects, not just the numeric recipe.
    if not geometry_only:
        for zone in manifest['reserved_volumes']:
            for o in bpy.data.collections['EDITABLE_SOURCE'].objects:
                if overlap(bounds(zone['center'],zone['size']),world_bounds(o)):errors.append(zone['name']+' intersects '+o.name)
        for c in manifest['candidates']:
            o=bpy.data.objects.get(c['name'])
            if o is None or (o.location-Vector(c['position'])).length>1e-5:errors.append('candidate '+c['name'])
    else:
        allowed={'LOD0','LOD1','LOD2','LOD3','COLLISION_SOURCE','CONVEX_SOURCE','WRECK_SOURCE'}
        if set(c.name for c in bpy.data.collections)-allowed:errors.append('diagnostic collection leaked into geometry file')
        if any(o.type!='MESH' for o in bpy.data.objects):errors.append('non-mesh leaked into geometry file')
    bb=[world_bounds(o) for o in bpy.data.collections['LOD0'].objects]
    lo=[min(b[0][i] for b in bb) for i in range(3)];hi=[max(b[1][i] for b in bb) for i in range(3)]
    dims=[hi[i]-lo[i] for i in range(3)]
    if not (499<dims[1]<502 and 319<dims[0]<324 and 179<dims[2]<183):errors.append('unexpected hull envelope')
    result={'status':'PASS' if not errors else 'FAIL','blender':bpy.app.version_string,'source_commit':manifest['source_commit'],
            'file':Path(bpy.data.filepath).name,'triangles':stats,'hull_dimensions_LWH_m':[dims[1],dims[0],dims[2]],
            'convex_source_count':len(bpy.data.collections['CONVEX_SOURCE'].objects),'errors':errors,
            'boundaries':['topological closed-edge check is NOT a solid-union/self-intersection proof',
                'collision/convex meshes are uncooked source geometry','UVs intentionally tile; not a unique bake atlas',
                'design AABB checks are NOT current Egosoft clearance or runtime tests']}
    jsonout(out/('geometry_validation.json' if geometry_only else 'blender_validation.json'),result)
    print(json.dumps(result,ensure_ascii=False))
    if errors:raise RuntimeError('Blender validation failed')

def render(out):
    from mathutils import Vector,Matrix
    sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1600;sc.render.resolution_y=1000
    sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
    sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True
    sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.4;sh.curvature_valley_factor=1.2
    sh.show_object_outline=True;sh.background_type='WORLD';sc.world.color=(.06,.075,.09)
    sc.view_settings.view_transform='Standard'
    cameras=bpy.data.collections['CAMERAS'];target=Vector((0,-20,0))
    for name,pos,up in [('hero',(-700,820,570),(0,0,1)),('top',(0,0,900),(1,0,0)),
                        ('side',(-900,0,0),(0,0,1)),('front',(0,900,0),(0,0,1)),('rear',(0,-900,0),(0,0,1))]:
        data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);cameras.objects.link(cam);cam.location=target+Vector(pos)
        z=(cam.location-target).normalized();x=Vector(up).cross(z).normalized();y=z.cross(x)
        cam.rotation_euler=Matrix((x,y,z)).transposed().to_euler();data.type='ORTHO';data.clip_end=5000
        # Fit all visible hull and removable equipment, not the enormous diagnostic boxes.
        pts=[]
        for cc in ('LOD0','EQUIPMENT_VIEW_ONLY'):
            for o in bpy.data.collections[cc].objects:pts += [o.matrix_world@Vector(v)-target for v in o.bound_box]
        w=max(q.dot(x) for q in pts)-min(q.dot(x) for q in pts)
        h=max(q.dot(y) for q in pts)-min(q.dot(y) for q in pts)
        data.sensor_fit='HORIZONTAL';data.ortho_scale=max(w,h*1.6)*1.20
        sc.camera=cam;sc.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    # A collision-only view proves the cavity has not been filled by a giant hull box.
    bpy.data.collections['LOD0'].hide_render=True;bpy.data.collections['EQUIPMENT_VIEW_ONLY'].hide_render=True
    cc=bpy.data.collections['COLLISION_SOURCE'];cc.hide_viewport=False;cc.hide_render=False
    sc.camera=bpy.data.objects['hero'];sc.render.filepath=str(out/'collision.png');bpy.ops.render.render(write_still=True)

def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['check','build','inspect','inspect-geometry','render']);parser.add_argument('output',type=Path)
    a=parser.parse_args(args);out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if a.mode=='check':
        p,r,c=design(load_spec());print(json.dumps(design_check(p,r)));return
    global bpy
    import bpy
    if a.mode=='build':build(out)
    elif a.mode=='render':render(out)
    else:inspect(out,a.mode=='inspect-geometry')

if __name__=='__main__':main()
