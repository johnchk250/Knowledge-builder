"""Versioned, evidence-labeled geometry. Never writes canonical plant assertions."""
import hashlib
import json
import math
from .store import dumps, now, uid
from .ingest import save_bytes

AXES=('x','y','z')
MAX_ITEMS=1000
MAX_TRIANGLES=150000
SHAPES=('box','cylinder','sphere','conveyor','motor','gearbox','sensor','hopper','pulley','stockpile','pump','fan','valve','gate','filter','building','stacker','unloader','mesh')
GUIDE='''\nAlways assess 3D applicability and return geometry_suggestions (an empty array is valid): at most 5 objects {entity:"existing or staged temporary entity ID",shape:"box|cylinder|sphere|conveyor|motor|gearbox|sensor|hopper|pulley|stockpile|pump|fan|valve|gate|filter|building|stacker|unloader",reason:"what the drawing establishes and what remains unknown",parameters:{"size.x":{value:10,basis:"document",note:"overall length converted to metres",evidence:[{evidence_id:"...",quote:"exact text",region:optional [0,0,1,1]}]}}}. Only include parameters actually supported by evidence. size.x/y/z are full bounding dimensions in metres; position.x/y/z are centre coordinates in metres in an explicitly established shared frame; rotation.x/y/z are degrees (Rx then Ry then Rz). P&ID symbol coordinates, connectivity and drawing page pixels DO NOT establish physical placement, size, elevation, pipe routing or orientation. Never fill absent dimensions with realistic guesses. Schematic templates will fill unknown parameters locally and label them schematic. A proposed shape is itself an approximate proxy, never detailed reconstructed CAD. These suggestions remain separate from plant assertions and require their own review after the plant proposal is accepted. Empty geometry_suggestions is valid. Do not treat geometry as evidence for subsequent plant facts.\n'''


def initialize(store):
    (store.root/'meshes').mkdir(exist_ok=True)
    with store.transaction() as db:
        db.execute('CREATE TABLE IF NOT EXISTS spatial_revisions(revision INTEGER PRIMARY KEY,model_version INTEGER NOT NULL,scene TEXT NOT NULL,created TEXT NOT NULL,reason TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS spatial_suggestions(id TEXT PRIMARY KEY,run_id TEXT REFERENCES runs(id),proposal_id TEXT REFERENCES proposals(id),body TEXT NOT NULL,errors TEXT NOT NULL,created TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS spatial_decisions(suggestion_id TEXT PRIMARY KEY REFERENCES spatial_suggestions(id),decision TEXT NOT NULL,revision INTEGER,created TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS mesh_assets(sha256 TEXT PRIMARY KEY,name TEXT NOT NULL,vertices TEXT NOT NULL,bounds TEXT NOT NULL,created TEXT NOT NULL)')
        for table in ('spatial_revisions','spatial_suggestions','spatial_decisions','mesh_assets'):
            for action in ('UPDATE','DELETE'):
                db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'immutable record'); END")
        db.execute("INSERT OR IGNORE INTO spatial_revisions VALUES(0,0,'[]',?,'Empty spatial layer')",(now(),))
        db.execute("UPDATE meta SET value='3' WHERE key='schema_version' AND CAST(value AS INTEGER)<3")


def current(store,db=None,revision=None):
    rows=store.rows('SELECT * FROM spatial_revisions '+('ORDER BY revision DESC LIMIT 1' if revision is None else 'WHERE revision=?'),() if revision is None else (int(revision),),db)
    if not rows: raise ValueError('Spatial revision not found')
    return {**rows[0],'scene':json.loads(rows[0]['scene'])}


def state(store):
    reconstructions=[]
    folder=store.root/'reconstructions'
    if folder.exists():
        for path in sorted(folder.glob('*/summary.json')):
            try:
                summary=json.loads(path.read_text(encoding='utf-8'))
                if summary.get('entity_id')==path.parent.name:
                    reconstructions.append(summary)
            except (ValueError,OSError):pass
    return {**current(store),'reconstructions':reconstructions,'history':store.rows('SELECT revision,model_version,created,reason FROM spatial_revisions ORDER BY revision DESC'),
            'suggestions':[{**s,'body':json.loads(s['body']),'errors':json.loads(s['errors'])} for s in store.rows("SELECT s.*,coalesce(d.decision,'pending') status FROM spatial_suggestions s LEFT JOIN spatial_decisions d ON d.suggestion_id=s.id ORDER BY s.created DESC")]}


def parameter(value,note='Illustrative value; not measured or established by source evidence.'):
    return {'value':value,'basis':'schematic','evidence':[],'note':note}


def template(entity,index,model):
    from .spatial_knowledge import shape_for
    types=[a['value'] for a in model['assertions'] if a['canonical_subject']==entity['id'] and a['predicate']=='instance_of' and not a['retirement']]
    shape=shape_for(types)
    dims={'conveyor':[8,.8,1.5],'motor':[1.4,.8,.8],'gearbox':[1,.7,.8],'sensor':[.3,.4,.3],'hopper':[2,2.5,2],'cylinder':[1.5,2,1.5],
          'pulley':[1.5,.8,.8],'stockpile':[20,5,10],'pump':[1.5,1,1],'fan':[1.5,2,2],'valve':[.6,.8,.5],
          'gate':[1.5,2,.5],'filter':[3,5,3],'building':[8,6,8],'stacker':[18,9,6],'unloader':[12,20,8]}.get(shape,[1.5,1,1.5])
    return {'entity_id':entity['id'],'shape':shape,'mesh_sha256':None,'parameters':{
        **{'size.'+axis:parameter(dims[i]) for i,axis in enumerate(AXES)},
        **{'position.'+axis:parameter([(index%4)*11,dims[1]/2,(index//4)*6][i],'Illustrative grid placement; graph connectivity is not a measured location.') for i,axis in enumerate(AXES)},
        **{'rotation.'+axis:parameter(0) for axis in AXES}},'notes':'Generic '+shape+' proxy. Its surface detail is not reconstructed from a drawing.'}


def evidence_errors(store,refs,visual_ids=None,document_id=None,db=None):
    if not isinstance(refs,list) or not 1<=len(refs)<=10: return ['Document-supported values require 1–10 source references.']
    errors=[]
    for r in refs:
        if not isinstance(r,dict) or set(r)-{'evidence_id','quote','region'} or not isinstance(r.get('evidence_id'),str): errors.append('Invalid evidence reference');continue
        rows=store.rows('SELECT * FROM evidence WHERE id=?',(r['evidence_id'],),db)
        if not rows or (document_id and rows[0]['document_id']!=document_id): errors.append('Unknown or unrelated source evidence');continue
        e=rows[0];q=r.get('quote','');box=r.get('region')
        if not isinstance(q,str) or (q and q not in e['text']): errors.append('Source quote does not match immutable text')
        if box is not None:
            valid=e['image'] and (visual_ids is None or e['id'] in visual_ids) and isinstance(box,list) and len(box)==4 and all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1 for v in box)
            if not valid or not (box[0]<box[2] and box[1]<box[3]):errors.append('Invalid or unsent drawing region')
        if not q and box is None:errors.append('Supporting quote or image region required')
    return errors


def validate_parameters(store,params,complete=True,visual_ids=None,document_id=None,db=None):
    errors=[];keys={group+'.'+a for group in ('size','position','rotation') for a in AXES}
    if not isinstance(params,dict) or set(params)-keys or (complete and set(params)!=keys):return ['Invalid geometry parameters; use size, position and rotation x/y/z.']
    for key,p in params.items():
        if not isinstance(p,dict) or set(p)!={'value','basis','evidence','note'}:errors.append(key+': value, basis, evidence and note are required');continue
        value=p['value'];basis=p['basis']
        if type(value) not in (int,float) or abs(value)>100000 or not math.isfinite(value) or (key.startswith('size.') and value<=0):errors.append(key+': invalid finite value or nonpositive size')
        if basis not in ('schematic','document','operator'):errors.append(key+': invalid basis')
        if not isinstance(p['note'],str) or len(p['note'])>1200:errors.append(key+': invalid note')
        if basis=='operator' and (not isinstance(p['note'],str) or not p['note'].strip()):errors.append(key+': identify the measurement or operator basis')
        if basis=='document': errors.extend(key+': '+e for e in evidence_errors(store,p['evidence'],visual_ids,document_id,db))
        elif p['evidence']!=[]:errors.append(key+': source references require document basis')
    return errors


def validate_scene(store,scene,db=None):
    if not isinstance(scene,list) or len(scene)>MAX_ITEMS:return [f'Scene must contain at most {MAX_ITEMS} equipment representations.']
    model=store.model(db=db);ids={e['id'] for e in model['entities'] if e['id']==e['canonical_id']};seen=set();errors=[]
    for item in scene:
        if not isinstance(item,dict) or set(item)!={'entity_id','shape','mesh_sha256','parameters','notes'}:errors.append('Invalid scene item fields');continue
        eid=item['entity_id']
        if not isinstance(eid,str) or eid not in ids or eid in seen:errors.append('Representation must use a unique, current canonical entity ID');continue
        seen.add(eid)
        if item['shape'] not in SHAPES:errors.append('Unsupported shape')
        if not isinstance(item['notes'],str) or len(item['notes'])>2000:errors.append('Invalid geometry notes')
        if item['shape']=='mesh':
            if not isinstance(item['mesh_sha256'],str) or not store.rows('SELECT sha256 FROM mesh_assets WHERE sha256=?',(item['mesh_sha256'],),db):errors.append('Imported mesh not found')
        elif item['mesh_sha256'] is not None:errors.append('Only mesh shapes can reference mesh assets')
        errors.extend(validate_parameters(store,item['parameters'],db=db))
    return list(dict.fromkeys(errors))


def save(store,scene,expected_revision,model_version,reason,db=None):
    if db is None:
        with store.transaction() as conn:return save(store,scene,expected_revision,model_version,reason,conn)
    old=current(store,db)
    if type(expected_revision) is not int or old['revision']!=expected_revision or type(model_version) is not int or store.version(db)!=model_version:raise ValueError('Spatial layer or plant model changed. Reload the scene before saving.')
    if not isinstance(reason,str) or not reason.strip() or len(reason)>1000:raise ValueError('A short change reason is required')
    errors=validate_scene(store,scene,db)
    if not errors:
        total=sum(len(world_mesh(store,item,db))//3 for item in scene)
        if total>MAX_TRIANGLES:errors.append('Scene exceeds 150,000 triangles. Simplify imported meshes.')
    if errors:raise ValueError('; '.join(errors))
    rev=expected_revision+1
    db.execute('INSERT INTO spatial_revisions VALUES(?,?,?,?,?)',(rev,model_version,dumps(scene),now(),reason))
    return {'revision':rev}


def sync(store):
    from .spatial_knowledge import build
    return build(store)


def suggestion(store,run_id,proposal_id,body,db):
    errors=[]
    if not isinstance(body,dict) or set(body)!={'entity','shape','reason','parameters'}:errors=['Invalid geometry suggestion fields']
    else:
        if not isinstance(body['entity'],str) or body['shape'] not in SHAPES[:-1] or not isinstance(body['reason'],str) or not body['reason'].strip() or len(body['reason'])>2000:errors.append('Invalid entity, proxy shape or reason')
        from .patches import visual_evidence_for_run
        doc=store.rows('SELECT document_id FROM runs WHERE id=?',(run_id,),db)[0]['document_id']
        errors.extend(validate_parameters(store,body['parameters'],False,visual_evidence_for_run(store,run_id,db),doc,db))
        if isinstance(body['parameters'],dict) and any(isinstance(v,dict) and v.get('basis')!='document' for v in body['parameters'].values()):errors.append('AI-suggested values must be supported by document evidence; omit unknown values.')
    db.execute('INSERT INTO spatial_suggestions VALUES(?,?,?,?,?,?)',(uid('geometry'),run_id,proposal_id,dumps(body),dumps(errors),now()))


def draft_suggestion(store,sid):
    rows=store.rows('SELECT * FROM spatial_suggestions WHERE id=?',(sid,))
    if not rows or store.rows('SELECT * FROM spatial_decisions WHERE suggestion_id=?',(sid,)):raise ValueError('Pending geometry suggestion not found')
    s=rows[0]
    if json.loads(s['errors']):raise ValueError('This geometry suggestion failed validation; reject it and use a manually reviewed scene edit.')
    p=store.rows('SELECT * FROM proposals WHERE id=?',(s['proposal_id'],))[0]
    if p['status']!='accepted':raise ValueError('Accept the associated plant proposal first so geometry can link to persistent equipment identities.')
    v=store.rows('SELECT patch FROM versions WHERE proposal_id=?',(p['id'],))[0]
    mapping=json.loads(v['patch'])['entity_ids'];body=json.loads(s['body']);eid=mapping.get(body['entity'],body['entity'])
    model=store.model();entity=next((e for e in model['entities'] if e['id']==eid and e['id']==e['canonical_id']),None)
    if not entity:raise ValueError('Geometry target is not a current canonical entity; resolve its identity before modeling.')
    old=current(store);scene=json.loads(dumps(old['scene']));item=next((i for i in scene if i['entity_id']==eid),None)
    if item is None:item=template(entity,len(scene),model);scene.append(item)
    changes=[]
    for key,param in body['parameters'].items():
        if item['parameters'][key]!=param:changes.append({'parameter':key,'previous':item['parameters'][key],'proposed':param})
        item['parameters'][key]=param
    item.update(shape=body['shape'],mesh_sha256=None,notes=body['reason']+' Shape remains an approximate proxy.')
    return {**old,'model_version':model['version'],'scene':scene,'changes':changes,'suggestion_id':sid}


def decide(store,body):
    if body.get('decision')=='reject':
        with store.transaction() as db:
            if not store.rows('SELECT id FROM spatial_suggestions WHERE id=?',(body.get('id'),),db) or store.rows('SELECT * FROM spatial_decisions WHERE suggestion_id=?',(body.get('id'),),db):raise ValueError('Pending geometry suggestion not found')
            db.execute('INSERT INTO spatial_decisions VALUES(?,?,NULL,?)',(body['id'],'rejected',now()))
        return {'status':'rejected'}
    if body.get('decision')!='approve':raise ValueError('Choose approve or reject')
    # Never allow unreviewed raw AI output to bypass the ordinary scene validator.
    with store.transaction() as db:
        if not store.rows('SELECT id FROM spatial_suggestions WHERE id=?',(body.get('id'),),db) or store.rows('SELECT * FROM spatial_decisions WHERE suggestion_id=?',(body.get('id'),),db):raise ValueError('Pending geometry suggestion not found')
        s=store.rows('SELECT * FROM spatial_suggestions WHERE id=?',(body['id'],),db)[0]
        if json.loads(s['errors']) or store.rows('SELECT status FROM proposals WHERE id=?',(s['proposal_id'],),db)[0]['status']!='accepted':raise ValueError('Source proposal must be accepted and geometry suggestion validated first')
        mapping=json.loads(store.rows('SELECT patch FROM versions WHERE proposal_id=?',(s['proposal_id'],),db)[0]['patch'])['entity_ids']
        target=json.loads(s['body'])['entity'];target=mapping.get(target,target)
        if not isinstance(body.get('scene'),list) or not any(isinstance(i,dict) and i.get('entity_id')==target for i in body['scene']):raise ValueError('Include the target equipment representation, or reject this suggestion instead.')
        result=save(store,body.get('scene'),body.get('expected_revision'),body.get('model_version'),body.get('reason'),db)
        db.execute('INSERT INTO spatial_decisions VALUES(?,?,?,?)',(body['id'],'approved',result['revision'],now()))
        return result


def import_obj(store,entity_id,name,content,scale):
    if not name.lower().endswith('.obj') or not 0<len(content)<=10*1024*1024:raise ValueError('Use an OBJ file up to 10 MB.')
    if type(scale) not in (int,float) or not math.isfinite(scale) or not 0<scale<=1000:raise ValueError('Specify a positive metres-per-unit scale.')
    points=[];triangles=[]
    for line in content.decode('utf-8-sig').splitlines():
        parts=line.split()
        if not parts or parts[0].startswith('#'):continue
        if parts[0]=='v':
            if len(parts)!=4:raise ValueError('OBJ vertices must use x y z without colors or homogeneous coordinates.')
            p=[float(x) for x in parts[1:]]
            if not all(math.isfinite(x) and abs(x)<1e7 for x in p):raise ValueError('Invalid OBJ vertex')
            points.append(p)
            if len(points)>100000:raise ValueError('OBJ vertex limit is 100,000.')
        elif parts[0]=='f':
            # Triangle/quad faces only; avoid inventing triangulations of arbitrary concave polygons.
            if len(parts) not in (4,5):raise ValueError('Export the mesh with triangle or planar convex quad faces.')
            indices=[]
            for term in parts[1:]:
                n=int(term.split('/')[0]);index=n-1 if n>0 else len(points)+n
                if n==0 or not 0<=index<len(points):raise ValueError('Invalid OBJ face reference')
                indices.append(index)
            if len(indices)==4:
                a,b,c,d=[points[k] for k in indices]
                subtract=lambda a,b:[a[k]-b[k] for k in range(3)]
                cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
                dot=lambda a,b:sum(a[k]*b[k] for k in range(3))
                normal=cross(subtract(b,a),subtract(c,a));length=math.hypot(*normal)
                corners=[a,b,c,d]
                if length<1e-12 or abs(dot(normal,subtract(d,a)))>1e-6*length*max(1,math.dist(d,a)) or any(dot(cross(subtract(corners[(k+1)%4],corners[k]),subtract(corners[(k+2)%4],corners[(k+1)%4])),normal)<=0 for k in range(4)):
                    raise ValueError('OBJ quad must be planar and convex; triangulate it in the source application.')
            for j in range(1,len(indices)-1):triangles.extend(points[k] for k in [indices[0],indices[j],indices[j+1]])
            if len(triangles)>150000:raise ValueError('OBJ limit is 50,000 triangles.')
        elif parts[0] not in ('vn','vt','o','g','s','usemtl','mtllib'):
            raise ValueError('Unsupported OBJ record. Export a plain polygon mesh.')
    if not triangles:raise ValueError('OBJ contains no triangle faces.')
    lows=[min(p[i] for p in triangles) for i in range(3)];highs=[max(p[i] for p in triangles) for i in range(3)]
    size=[highs[i]-lows[i] for i in range(3)]
    if min(size)<=1e-9:raise ValueError('Use a volumetric 3D mesh, not a flat drawing.')
    normalized=[[(p[i]-(lows[i]+highs[i])/2)/size[i] for i in range(3)] for p in triangles]
    model=store.model();entity=next((e for e in model['entities'] if e['id']==entity_id and e['id']==e['canonical_id']),None)
    if not entity:raise ValueError('Select a current plant entity before importing geometry.')
    sha=hashlib.sha256(content).hexdigest();save_bytes(store.root/'meshes'/sha,content)
    with store.transaction() as db:db.execute('INSERT OR IGNORE INTO mesh_assets VALUES(?,?,?,?,?)',(sha,name[:200],dumps(normalized),dumps(size),now()))
    old=current(store);scene=json.loads(dumps(old['scene']));item=next((i for i in scene if i['entity_id']==entity_id),None)
    if item is None:item=template(entity,len(scene),model);scene.append(item)
    item.update(shape='mesh',mesh_sha256=sha,notes='Imported OBJ surface. Original scale/orientation and as-built accuracy are not verified. Unit scale supplied: '+str(scale)+' metres per OBJ unit.')
    for i,a in enumerate(AXES):item['parameters']['size.'+a]=parameter(size[i]*scale,'Imported mesh extents with unverified unit scale '+str(scale)+' m/unit.')
    return {**old,'model_version':model['version'],'scene':scene}


def unit_mesh(shape):
    triangles=[]
    def tri(a,b,c):triangles.extend([a,b,c])
    def box(center=(0,0,0),size=(1,1,1)):
        v=[[center[k]+size[k]*(.5 if i&(1<<k) else -.5) for k in range(3)] for i in range(8)]
        for a,b,c,d in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]:tri(v[a],v[b],v[c]);tri(v[a],v[c],v[d])
    def cylinder(center=(0,0,0),size=(1,1,1),axis=1,segments=20):
        def point(angle,end):
            p=[math.cos(angle)*.5,end*.5,math.sin(angle)*.5]
            if axis==0:p=[p[1],p[0],p[2]]
            if axis==2:p=[p[0],p[2],p[1]]
            return [p[k]*size[k]+center[k] for k in range(3)]
        for n in range(segments):
            a=2*math.pi*n/segments;b=2*math.pi*(n+1)/segments
            p,q,r,s=point(a,-1),point(b,-1),point(b,1),point(a,1)
            tri(p,q,r);tri(p,r,s)
            for end,v,w in [(-1,q,p),(1,s,r)]:
                c=list(center);c[axis]+=size[axis]*end*.5;tri(c,v,w)
    if shape in ('box','gearbox'):box()
    elif shape=='cylinder':cylinder()
    elif shape=='pulley':cylinder(axis=0)
    elif shape=='stockpile':
        a,b,c,d=[[-.5,-.5,-.5],[.5,-.5,-.5],[.5,-.5,.5],[-.5,-.5,.5]]
        p,q=[-.32,.5,0],[.32,.5,0]
        tri(a,b,q);tri(a,q,p);tri(d,p,q);tri(d,q,c);tri(a,p,d);tri(b,c,q);tri(a,d,c);tri(a,c,b)
    elif shape=='pump':
        cylinder((.25,0,0),(.45,.8,.8),0);cylinder((-.25,0,0),(.55,.6,.6),0)
        cylinder((.25,.4,0),(.15,.3,.15));box((0,-.43,0),(1,.14,.85))
    elif shape=='fan':
        cylinder((0,0,0),(.65,.85,.85),0);box((0,.35,.3),(.7,.3,.4));box((0,-.45,0),(.8,.1,.7))
    elif shape=='valve':
        cylinder((0,-.2,0),(1,.4,.4),0);cylinder((0,.1,0),(.25,.5,.25));cylinder((0,.43,0),(.6,.1,.6))
    elif shape=='gate':
        box((0,0,0),(1,1,.4));box((0,.25,.3),(.65,.4,.2))
    elif shape=='filter':
        box((0,.1,0),(1,.8,1))
        for x in (-.4,.4):
            for z in (-.4,.4):box((x,-.4,z),(.08,.3,.08))
    elif shape=='building':
        box((0,.05,0),(1,.9,1));box((0,-.46,0),(1,.08,1))
    elif shape in ('stacker','unloader'):
        box((0,-.4,0),(.55,.2,.8));box((0,0,0),(.25,.8,.35))
        box((.15,.35,0),(.7,.12,.18));box((-.3,.15,0),(.25,.2,.35))
        if shape=='unloader':box((.45,0,0),(.08,.8,.14))
    elif shape=='sphere':
        def pt(a,b):return [.5*math.cos(a)*math.sin(b),.5*math.cos(b),.5*math.sin(a)*math.sin(b)]
        for x in range(20):
            for y in range(12):
                a=x*math.pi/10;b=(x+1)*math.pi/10;c=y*math.pi/12;d=(y+1)*math.pi/12
                tri(pt(a,c),pt(b,c),pt(b,d));tri(pt(a,c),pt(b,d),pt(a,d))
    elif shape=='conveyor':
        box((0,.3,0),(1,.18,1));box((0,.12,0),(.9,.15,.85))
        for x in (-.4,.4):
            for z in (-.38,.38):box((x,-.15,z),(.035,.7,.07))
        for x in (-.43,.43):cylinder((x,.27,0),(.13,.26,1),2)
    elif shape=='motor':
        cylinder((0,.02,0),(.85,.8,.8),0);cylinder((.45,.02,0),(.15,.17,.17),0)
        box((0,-.42,0),(.65,.16,.95));box((-.12,.42,0),(.35,.2,.4))
    elif shape=='sensor':cylinder((0,.04,0),(.65,.8,.65));box((0,-.43,0),(1,.14,1))
    elif shape=='hopper':
        top=[[-.5,.5,-.5],[.5,.5,-.5],[.5,.5,.5],[-.5,.5,.5]];bottom=[[-.15,-.5,-.15],[.15,-.5,-.15],[.15,-.5,.15],[-.15,-.5,.15]]
        for i in range(4):j=(i+1)%4;tri(top[i],bottom[i],bottom[j]);tri(top[i],bottom[j],top[j])
        tri(bottom[0],bottom[2],bottom[1]);tri(bottom[0],bottom[3],bottom[2])
    else:raise ValueError('Unknown mesh shape')
    lo=[min(p[i] for p in triangles) for i in range(3)];hi=[max(p[i] for p in triangles) for i in range(3)]
    return [[(p[i]-(lo[i]+hi[i])/2)/(hi[i]-lo[i]) for i in range(3)] for p in triangles]


def world_mesh(store,item,db=None):
    if item['shape']=='mesh':
        rows=store.rows('SELECT vertices FROM mesh_assets WHERE sha256=?',(item['mesh_sha256'],),db)
        if not rows:raise ValueError('Mesh asset missing')
        vertices=json.loads(rows[0]['vertices'])
    else:vertices=unit_mesh(item['shape'])
    params=item['parameters'];size=[params['size.'+a]['value'] for a in AXES];pos=[params['position.'+a]['value'] for a in AXES];rot=[params['rotation.'+a]['value']*math.pi/180 for a in AXES]
    cx,cy,cz=[math.cos(r) for r in rot];sx,sy,sz=[math.sin(r) for r in rot]
    output=[]
    for v in vertices:
        x,y,z=[v[i]*size[i] for i in range(3)]
        y,z=y*cx-z*sx,y*sx+z*cx;x,z=x*cy+z*sy,-x*sy+z*cy;x,y=x*cz-y*sz,x*sz+y*cz
        output.append([x+pos[0],y+pos[1],z+pos[2]])
    return output


def rendered(store,revision=None,scene_override=None):
    snapshot=current(store,revision=revision) if scene_override is None else scene_override
    model=store.model(snapshot['model_version']);entities={e['id']:e for e in model['entities']}
    total=0;items=[]
    for item in snapshot['scene']:
        vertices=world_mesh(store,item);total+=len(vertices)//3
        if total>MAX_TRIANGLES:raise ValueError('Scene exceeds the 150,000-triangle viewer limit. Simplify imported meshes.')
        items.append({**item,'label':entities.get(item['entity_id'],{}).get('label',item['entity_id']),'vertices':vertices})
    ids={i['entity_id'] for i in items}
    return {**snapshot,'items':items,'triangle_count':total,'relationships':[{'id':a['id'],'subject':a['canonical_subject'],'object':a['canonical_object'],'predicate':a['predicate']} for a in model['assertions'] if not a['retirement'] and a['canonical_subject'] in ids and a['canonical_object'] in ids],
            'warning':'Geometry is an evidence-labeled representation, not certified as-built CAD. Relationship lines are logical links, never measured pipe/cable routes.'}


def export_gltf(store,revision=None):
    import struct,base64
    scene=rendered(store,revision);data=bytearray();views=[];accessors=[];meshes=[];nodes=[]
    for item in scene['items']:
        vertices=item['vertices'];offset=len(data)
        for v in vertices:data.extend(struct.pack('<fff',*v))
        views.append({'buffer':0,'byteOffset':offset,'byteLength':len(data)-offset,'target':34962})
        accessors.append({'bufferView':len(views)-1,'componentType':5126,'count':len(vertices),'type':'VEC3','min':[min(v[k] for v in vertices) for k in range(3)],'max':[max(v[k] for v in vertices) for k in range(3)]})
        meshes.append({'primitives':[{'attributes':{'POSITION':len(accessors)-1},'material':0,'mode':4}]})
        nodes.append({'name':item['label'],'mesh':len(meshes)-1,'extras':{k:item[k] for k in ['entity_id','shape','mesh_sha256','parameters','notes']}})
    result={'asset':{'version':'2.0','generator':'CHP Knowledge Builder 0.4'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'extras':{'spatial_revision':scene['revision'],'plant_model_version':scene['model_version'],'warning':scene['warning'],'relationships':scene['relationships'],'coordinate_system':'metres, +Y up; rotations baked into vertices'}}
    if nodes:result.update(meshes=meshes,accessors=accessors,bufferViews=views,buffers=[{'byteLength':len(data),'uri':'data:application/octet-stream;base64,'+base64.b64encode(data).decode()}],materials=[{'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.25,.5,.8,1],'metallicFactor':0,'roughnessFactor':.8}}])
    return result
