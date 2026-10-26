/* === BEGIN EMBEDDED PlantYard3D === */
/* On-Demand, Dimension-Accurate 3D Kinematic Model for Coal Stackers (EAD-1..4)
 * and Full Portal Scraper Reclaimers (EAF-1..4).
 *
 * Lazy-mounted ONLY when the user opens the `view=3d` mode on a Stacker or Reclaimer.
 * Zero WebGL contexts, zero geometry buffers, and zero animation loops exist during
 * normal Plant Explorer browsing; all GPU resources are disposed immediately on exit.
 *
 * Coordinate Convention (1 unit = 1.000 metre, millimetre precision):
 *   Y : Elevation above rail top (EL +0.000 m = top of UIC60 rail)
 *   X : Cross-rail / stockpile / portal span axis (m)
 *   Z : Along-rail long-travel axis (m)
 */
(function(root){
'use strict';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const V3={
  add:(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]],
  sub:(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]],
  mul:(a,s)=>[a[0]*s,a[1]*s,a[2]*s],
  dot:(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2],
  cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],
  len:a=>Math.hypot(a[0],a[1],a[2]),
  norm:a=>{const l=Math.hypot(a[0],a[1],a[2])||1;return [a[0]/l,a[1]/l,a[2]/l];},
  lerp:(a,b,t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t],
  rotY:(p,rad)=>{const c=Math.cos(rad),s=Math.sin(rad);return [p[0]*c+p[2]*s,p[1],-p[0]*s+p[2]*c];},
  rotZ:(p,rad)=>{const c=Math.cos(rad),s=Math.sin(rad);return [p[0]*c-p[1]*s,p[0]*s+p[1]*c,p[2]];}
};

function rayTriangle(origin,dir,a,b,c){
  const e1=V3.sub(b,a),e2=V3.sub(c,a),h=V3.cross(dir,e2),det=V3.dot(e1,h);
  if(Math.abs(det)<1e-8)return null;
  const inv=1/det,s=V3.sub(origin,a),u=V3.dot(s,h)*inv;
  if(u<0||u>1)return null;
  const q=V3.cross(s,e1),v=V3.dot(dir,q)*inv;
  if(v<0||u+v>1)return null;
  const t=V3.dot(e2,q)*inv;
  return t>0.05?t:null;
}

// --- Parametric 3D Engineering Geometry Builders (1 unit = 1.000 m) ---

function pushQuad(tris,p0,p1,p2,p3){
  tris.push(p0,p1,p2,p0,p2,p3);
}

function addBox(tris,cx,cy,cz,sx,sy,sz){
  const hx=sx/2,hy=sy/2,hz=sz/2;
  const p=[
    [cx-hx,cy-hy,cz-hz],[cx+hx,cy-hy,cz-hz],[cx+hx,cy+hy,cz-hz],[cx-hx,cy+hy,cz-hz],
    [cx-hx,cy-hy,cz+hz],[cx+hx,cy-hy,cz+hz],[cx+hx,cy+hy,cz+hz],[cx-hx,cy+hy,cz+hz]
  ];
  pushQuad(tris,p[4],p[5],p[6],p[7]); // +Z
  pushQuad(tris,p[1],p[0],p[3],p[2]); // -Z
  pushQuad(tris,p[5],p[1],p[2],p[6]); // +X
  pushQuad(tris,p[0],p[4],p[7],p[3]); // -X
  pushQuad(tris,p[3],p[7],p[6],p[2]); // +Y
  pushQuad(tris,p[0],p[1],p[5],p[4]); // -Y
}

function basisFromAxis(axis,upHint=[0,1,0]){
  const fwd=V3.norm(axis);
  let right=V3.cross(fwd,upHint);
  if(V3.len(right)<1e-4)right=V3.cross(fwd,[0,0,1]);
  right=V3.norm(right);
  const up=V3.norm(V3.cross(right,fwd));
  return {fwd,right,up};
}

function addOrientedBox(tris,p0,p1,width,height,upHint=[0,1,0]){
  const diff=V3.sub(p1,p0);
  if(V3.len(diff)<1e-5)return;
  const {right,up}=basisFromAxis(diff,upHint);
  const r=V3.mul(right,width/2),u=V3.mul(up,height/2);
  const a0=V3.sub(V3.sub(p0,r),u),a1=V3.sub(V3.add(p0,r),u),a2=V3.add(V3.add(p0,r),u),a3=V3.add(V3.sub(p0,r),u);
  const b0=V3.sub(V3.sub(p1,r),u),b1=V3.sub(V3.add(p1,r),u),b2=V3.add(V3.add(p1,r),u),b3=V3.add(V3.sub(p1,r),u);
  pushQuad(tris,a1,a0,a3,a2);
  pushQuad(tris,b0,b1,b2,b3);
  pushQuad(tris,a0,b0,b3,a3);
  pushQuad(tris,b1,a1,a2,b2);
  pushQuad(tris,a3,b3,b2,a2);
  pushQuad(tris,a0,a1,b1,b0);
}

function addCylinder(tris,p0,p1,r0,r1=r0,segs=14){
  const diff=V3.sub(p1,p0);
  if(V3.len(diff)<1e-5)return;
  const {right,up}=basisFromAxis(diff);
  const ring0=[],ring1=[];
  for(let i=0;i<segs;i++){
    const ang=(i/segs)*Math.PI*2,c=Math.cos(ang),s=Math.sin(ang);
    const radial=V3.add(V3.mul(right,c),V3.mul(up,s));
    ring0.push(V3.add(p0,V3.mul(radial,r0)));
    ring1.push(V3.add(p1,V3.mul(radial,r1)));
  }
  for(let i=0;i<segs;i++){
    const ni=(i+1)%segs;
    pushQuad(tris,ring0[i],ring1[i],ring1[ni],ring0[ni]);
    if(r0>1e-4)tris.push(p0,ring0[ni],ring0[i]);
    if(r1>1e-4)tris.push(p1,ring1[i],ring1[ni]);
  }
}

function addRingY(tris,cx,cy,cz,rInner,rOuter,height,segs=28){
  const y0=cy-height/2,y1=cy+height/2;
  for(let i=0;i<segs;i++){
    const a0=(i/segs)*Math.PI*2,a1=((i+1)/segs)*Math.PI*2;
    const c0=Math.cos(a0),s0=Math.sin(a0),c1=Math.cos(a1),s1=Math.sin(a1);
    const p00=[cx+rInner*c0,y0,cz+rInner*s0],p01=[cx+rOuter*c0,y0,cz+rOuter*s0];
    const p10=[cx+rInner*c1,y0,cz+rInner*s1],p11=[cx+rOuter*c1,y0,cz+rOuter*s1];
    const q00=[cx+rInner*c0,y1,cz+rInner*s0],q01=[cx+rOuter*c0,y1,cz+rOuter*s0];
    const q10=[cx+rInner*c1,y1,cz+rInner*s1],q11=[cx+rOuter*c1,y1,cz+rOuter*s1];
    pushQuad(tris,q00,q01,q11,q10); // top
    pushQuad(tris,p01,p00,p10,p11); // bottom
    pushQuad(tris,p01,p11,q11,q01); // outer
    pushQuad(tris,p10,p00,q00,q10); // inner
  }
}

function addTrussGirder(tris,p0,p1,width,height,bays,chordThick=0.18,braceThick=0.11,upHint=[0,1,0]){
  const diff=V3.sub(p1,p0);
  if(V3.len(diff)<1e-4)return;
  const {right,up}=basisFromAxis(diff,upHint);
  const hw=width/2,hh=height/2;
  const corner=(t,sx,sy)=>V3.add(V3.lerp(p0,p1,t),V3.add(V3.mul(right,sx*hw),V3.mul(up,sy*hh)));
  // 4 longitudinal main chords
  for(const sx of [-1,1]){
    for(const sy of [-1,1]){
      addOrientedBox(tris,corner(0,sx,sy),corner(1,sx,sy),chordThick,chordThick,up);
    }
  }
  const nBays=Math.max(2,bays);
  for(let i=0;i<=nBays;i++){
    const t0=i/nBays;
    const bl=corner(t0,-1,-1),br=corner(t0,1,-1),tl=corner(t0,-1,1),tr=corner(t0,1,1);
    addOrientedBox(tris,bl,tl,braceThick,braceThick,right);
    addOrientedBox(tris,br,tr,braceThick,braceThick,right);
    addOrientedBox(tris,bl,br,braceThick,braceThick,up);
    addOrientedBox(tris,tl,tr,braceThick,braceThick,up);
    if(i<nBays){
      const t1=(i+1)/nBays;
      const nbl=corner(t1,-1,-1),nbr=corner(t1,1,-1),ntl=corner(t1,-1,1),ntr=corner(t1,1,1);
      // Warren web diagonals on both side faces + top lateral bracing
      if(i%2===0){
        addOrientedBox(tris,bl,ntl,braceThick,braceThick,right);
        addOrientedBox(tris,br,ntr,braceThick,braceThick,right);
        addOrientedBox(tris,tl,ntr,braceThick*0.85,braceThick*0.85,up);
      }else{
        addOrientedBox(tris,tl,nbl,braceThick,braceThick,right);
        addOrientedBox(tris,tr,nbr,braceThick,braceThick,right);
        addOrientedBox(tris,tr,ntl,braceThick*0.85,braceThick*0.85,up);
      }
    }
  }
}

function addTroughBelt(tris,p0,p1,beltWidth=2.0,troughDeg=35,upHint=[0,1,0]){
  const diff=V3.sub(p1,p0);
  if(V3.len(diff)<1e-4)return;
  const {right,up}=basisFromAxis(diff,upHint);
  const centerW=beltWidth*0.38,wingW=beltWidth*0.31;
  const rad=troughDeg*Math.PI/180;
  const dy=Math.sin(rad)*wingW,dx=Math.cos(rad)*wingW;
  // Center flat run
  addOrientedBox(tris,p0,p1,centerW,0.06,up);
  // Left & right 35-deg trough wings
  for(const s of [-1,1]){
    const wOff=V3.add(V3.mul(right,s*(centerW/2+dx/2)),V3.mul(up,dy/2));
    const wingUp=V3.norm(V3.add(V3.mul(up,Math.cos(rad)),V3.mul(right,-s*Math.sin(rad))));
    addOrientedBox(tris,V3.add(p0,wOff),V3.add(p1,wOff),wingW,0.055,wingUp);
  }
}

function addStockpilePrism(tris,xMin,xMax,zMin,zMax,peakH,yBase=0.0,segsZ=12){
  const xMid=(xMin+xMax)/2,halfW=(xMax-xMin)/2;
  for(let i=0;i<segsZ;i++){
    const z0=zMin+(zMax-zMin)*(i/segsZ),z1=zMin+(zMax-zMin)*((i+1)/segsZ);
    // Taper ends like a real chevron conical-end windrow stockpile
    const endFactor=z=>{
      const d=Math.min(z-zMin,zMax-z);
      return Math.min(1,Math.max(0.18,d/14));
    };
    const f0=endFactor(z0),f1=endFactor(z1);
    const h0=peakH*f0,h1=peakH*f1;
    const w0=halfW*(0.35+0.65*f0),w1=halfW*(0.35+0.65*f1);
    const l0=[xMid-w0,yBase,z0],r0=[xMid+w0,yBase,z0],m0=[xMid,yBase+h0,z0];
    const l1=[xMid-w1,yBase,z1],r1=[xMid+w1,yBase,z1],m1=[xMid,yBase+h1,z1];
    // Left slope & right slope
    pushQuad(tris,l0,l1,m1,m0);
    pushQuad(tris,m0,m1,r1,r0);
    if(i===0)tris.push(l0,m0,r0);
    if(i===segsZ-1)tris.push(r1,m1,l1);
  }
}

function transformVertices(tris,rotYRad,tx,ty,tz){
  const c=Math.cos(rotYRad),s=Math.sin(rotYRad);
  return tris.map(p=>[
    p[0]*c+p[2]*s+tx,
    p[1]+ty,
    -p[0]*s+p[2]*c+tz
  ]);
}

function transformLuffAndSlew(tris,pivotX,pivotY,luffRad,slewRad,tx,ty,tz){
  const cl=Math.cos(luffRad),sl=Math.sin(luffRad);
  const cs=Math.cos(slewRad),ss=Math.sin(slewRad);
  return tris.map(p=>{
    const dx=p[0]-pivotX,dy=p[1]-pivotY,dz=p[2];
    const lx=pivotX+dx*cl-dy*sl;
    const ly=pivotY+dx*sl+dy*cl;
    return [
      lx*cs+dz*ss+tx,
      ly+ty,
      -lx*ss+dz*cs+tz
    ];
  });
}

// --- Entity Matcher for Stacker (EAD-1..4) and Portal Reclaimer (EAF-1..4) ---

function resolveEntityMap(scene){
  const nodes=scene.nodes||[];
  const find=(re,kindFilter=null)=>{
    const hit=nodes.find(n=>re.test(n.label)&&(!kindFilter||n.kind===kindFilter));
    return hit?hit.id:scene.id;
  };
  if(scene.kind==='stacker'){
    return {
      self:scene.id,
      tripper:find(/travelling tripper$/i)||find(/tripper/i),
      tripperPulley:find(/tripper head pulley|discharge pulley/i)||find(/tripper/i),
      tripperBogies:find(/tripper rail bogies/i)||find(/tripper/i),
      tripperIdlers:find(/tripper carrying idlers/i)||find(/tripper/i),
      tripperChute:find(/tripper skirtboard|transfer chute/i)||find(/tripper/i),
      boom:find(/boom conveyor$/i)||find(/boom conveyor/i),
      boomBelt:find(/belt and pulleys/i)||find(/boom conveyor$/i)||find(/boom conveyor/i),
      weigher:find(/belt weigher$/i)||find(/weighbridge|weigher/i),
      boomDrive:find(/boom conveyor drive group$/i)||find(/boom conveyor drive motors|drive group motors|drive group/i),
      boomMotors:find(/boom conveyor drive motors|drive group motors/i)||find(/boom conveyor drive/i),
      boomCouplings:find(/fluid couplings/i)||find(/boom conveyor drive/i),
      boomGearboxes:find(/bevel-helical gearboxes|drive group gearboxes/i)||find(/boom conveyor drive/i),
      boomBrakes:find(/thruster brakes/i)||find(/boom conveyor drive/i),
      luffSys:find(/luffing system$/i)||find(/luffing/i),
      luffCyl:find(/luffing.*cylinder/i)||find(/luffing/i),
      luffHpp:find(/luffing.*hydraulic power pack/i)||find(/luffing hpp/i)||find(/luffing/i),
      slewSys:find(/slew system$/i)||find(/slew/i),
      slewRing:find(/ring bearing and pinions/i)||find(/slew system/i),
      slewMotors:find(/slew.*hydraulic.*motors/i)||find(/slew system/i),
      slewHpp:find(/slew.*hydraulic power pack/i)||find(/slew hpp/i)||find(/slew system/i),
      travelSys:find(/travel system$/i)||find(/travel/i),
      travelWheels:find(/rails and wheels|rail bogies and wheels/i)||find(/travel system/i),
      travelMotors:find(/travel.*geared motors/i)||find(/travel system/i),
      railClamps:find(/rail clamps and storm anchors/i)||find(/travel system/i),
      cabin:find(/operator cabin/i),
      ehouse:find(/electrical house/i),
      fire:find(/fire detection and clean-agent/i)||find(/fmz5000/i),
      dss:find(/onboard plain-water dss$/i)||find(/dss/i),
      lube:find(/central grease lubrication$/i)||find(/lubrication/i),
      upstreamBelt:nodes.find(n=>n.role==='connected'&&/^EAC-/i.test(n.label))?.id||scene.id,
      stockpile:nodes.find(n=>n.role==='connected'&&(/^EAE-/i.test(n.label)||n.kind==='pile'))?.id||scene.id
    };
  }
  return {
    self:scene.id,
    mainBoom:find(/main scraper boom$/i)||find(/main.*boom/i),
    mainChain:find(/main.*scraper chain/i)||find(/main scraper boom/i),
    mainBlades:find(/main.*scraper blades/i)||find(/main scraper boom/i),
    mainTakeup:find(/main.*take-up/i)||find(/main scraper boom/i),
    mainDrive:find(/main scraper boom drive group$/i)||find(/main.*vfd motors|main.*gearboxes|main scraper boom drive/i),
    mainMotors:find(/main.*motors/i)||find(/main scraper boom/i),
    mainGearboxes:find(/main.*gearboxes/i)||find(/main scraper boom/i),
    auxBoom:find(/auxiliary scraper boom$/i)||find(/aux.*boom/i),
    auxChain:find(/aux.*scraper chain/i)||find(/auxiliary scraper boom/i),
    auxBlades:find(/aux.*scraper blades/i)||find(/auxiliary scraper boom/i),
    auxTakeup:find(/aux.*take-up/i)||find(/auxiliary scraper boom/i),
    auxDrive:find(/auxiliary scraper boom drive group$/i)||find(/aux.*vfd motors|aux.*gearboxes|auxiliary scraper boom/i),
    hoistSys:find(/hoist system$/i)||find(/hoist/i),
    hoistWinch:find(/winch.*rope and sheaves/i)||find(/hoist system/i),
    hoistMotor:find(/hoist.*motor/i)||find(/hoist system/i),
    hoistGearbox:find(/hoist.*gearbox/i)||find(/hoist system/i),
    hoistBrakes:find(/hoist.*thruster brakes/i)||find(/hoist system/i),
    travelSys:find(/travel system$/i)||find(/travel/i),
    travelWheels:find(/rails and.*wheels/i)||find(/travel system/i),
    travelMotors:find(/travel.*geared motors/i)||find(/travel system/i),
    hydClamps:find(/hydraulic rail clamps/i)||find(/travel system/i),
    stormAnchors:find(/manual rail clamps/i)||find(/travel system/i),
    buffers:find(/spring buffers/i)||find(/travel system/i),
    powerReel:find(/power cable reel/i),
    controlReel:find(/control cable reel/i),
    greaseLube:find(/central grease lubrication$/i)||find(/grease lubrication/i),
    chainOilLube:find(/chain oil lubrication$/i)||find(/chain oil/i),
    dss:find(/onboard plain-water dss$/i)||find(/dss/i),
    stockpile:nodes.find(n=>n.role==='connected'&&(/^EAE-/i.test(n.label)||n.kind==='pile'))?.id||scene.id,
    reclaimBelt:nodes.find(n=>n.role==='connected'&&/^EBA-/i.test(n.label))?.id||scene.id
  };
}

// --- Stacker (EAD-1..4) True-Scale 3D Procedural Builder ---
// Exact Dimensions from MAITREE-00-EAF-DA-175126-ISG-1 & Stability Calc 175117-ISG-3:
// - Rail gauge: 8.400 m (Z = -4.200 m & Z = +4.200 m, UIC60 rails)
// - Wheelbase along rail: 8.500 m (X = -4.250 m to +4.250 m, 22 wheels: 8 on Corner A, 7 on B, 7 on C)
// - Slew bearing height: EL +4.475 m (Rothe Erde 132.50.4000.102.04.03F4, OD 4.395 m, track Ø4.000 m)
// - Rotating platform: EL +5.400 m; Boom pivot: X = 0.000 m, EL +7.980 m
// - Boom length: 41.755 m (pivot to head pulley), head walkway at 44.750 m, luffing -8° to +14°
// - Luffing cylinders (2x MAHA Ø250/180 x 2190 mm): lower pin (+4.250 m, EL +4.790 m), upper pin (+6.525 m, EL +8.440 m)
// - Counterweight arm: X = -6.150 m, EL +8.500 m (143 t counterweight)
// - Mast apex: EL +15.000 m
// - Travelling tripper: 47.878 m horizontal length (61.480 m belt length), Ø1000 mm discharge pulley
// - Electrical house: 10.5 x 3.0 x 2.7 m; Operator cabin: 2.4 x 1.9 x 2.4 m

function buildStackerScene3D(scene,state3d){
  const map=resolveEntityMap(scene);
  const slewDeg=state3d.slewDeg??48;
  const luffDeg=state3d.luffDeg??8;
  const travelM=state3d.travelM??0;
  const phase=state3d.phase??0;
  const explode=state3d.exploded?1:0;

  // In Stacker 3D space:
  // Rail axis = X (-65 m to +55 m), Cross-rail gauge = Z (-4.200 m to +4.200 m), Elevation = Y (EL +m)
  // At Slew = 0 deg, boom points along +X (parallel to yard rail). At Slew = 90 deg, boom points across stockpile (+Z).
  const slewRad=(slewDeg*Math.PI)/180;
  const luffRad=(luffDeg*Math.PI)/180;
  const items=[];

  const pushPart=(id,label,network,color,tris,specSummary,explodeVec=[0,0,0],isContext=false)=>{
    if(!tris.length)return;
    const verts=explode?tris.map(v=>[v[0]+explodeVec[0],v[1]+explodeVec[1],v[2]+explodeVec[2]]):tris;
    let lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
    for(const v of verts)for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],v[k]);hi[k]=Math.max(hi[k],v[k]);}
    const centre=[(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2];
    items.push({
      entity_id:id,
      part_key:label,
      label,
      network,
      color,
      spec:specSummary,
      isContext,
      centre,
      bbox:{lo,hi,size:[hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]]},
      vertices:verts
    });
  };

  // 1. Yard Rails (UIC60, 8400 mm gauge at Z = -4.200 m and Z = +4.200 m) & Yard Belt EAC
  {
    const railTris=[];
    for(const zRail of [-4.2,4.2]){
      addBox(railTris,-5,0.08,zRail,130,0.16,0.15);
      addBox(railTris,-5,-0.18,zRail,130,0.36,0.65);
    }
    for(let x=-68;x<=58;x+=4.0){
      addBox(railTris,x,-0.32,0,0.35,0.16,9.6);
    }
    pushPart(map.travelWheels,'UIC60 Yard Rails (8,400 mm Gauge)','mechanical',[0.46,0.52,0.49],railTris,'8,400 mm rail gauge · UIC60 rail section · max wheel load 27.0 t',[0,-2.5,0],true);
  }

  // 2. Upstream Yard Belt Conveyor (EAC-5/7/9/11, 2000 mm steel-cord belt running through gantry at Z = 0)
  {
    const beltTris=[];
    addTroughBelt(beltTris,[-68,1.15,0],[travelM-47.878,1.15,0],2.0,35,[0,1,0]);
    addTroughBelt(beltTris,[travelM+2.5,1.15,0],[58,1.15,0],2.0,35,[0,1,0]);
    for(let x=-66;x<=56;x+=3.0){
      if(x<travelM-48||x>travelM+3){
        addBox(beltTris,x,0.58,-1.15,0.12,1.15,0.12);
        addBox(beltTris,x,0.58,1.15,0.12,1.15,0.12);
      }
    }
    pushPart(map.upstreamBelt,'Yard Conveyor (2,000 mm Belt · 35° Trough)','material',[0.28,0.43,0.38],beltTris,'2,000 mm steel-cord belt · 35° trough angle · 3,400 / 3,740 TPH',[0,-1.5,0],true);
  }

  // 3. 3-Corner Equalizer Travel Bogies (Corner A: 8 wheels at Z=+4.2m; Corner B: 7 wheels at X=+4.25m, Z=-4.2m; Corner C: 7 wheels at X=-4.25m, Z=-4.2m)
  {
    const bogieTris=[],motorTris=[],clampTris=[];
    const corners=[
      {cx:travelM,cz:4.2,nWheels:8,span:6.8},
      {cx:travelM+4.25,cz:-4.2,nWheels:7,span:5.8},
      {cx:travelM-4.25,cz:-4.2,nWheels:7,span:5.8}
    ];
    for(const c of corners){
      // Primary & secondary equalizer beams
      addBox(bogieTris,c.cx,0.92,c.cz,c.span+0.8,0.48,0.68);
      addBox(bogieTris,c.cx-c.span*0.24,0.58,c.cz,c.span*0.46,0.32,0.56);
      addBox(bogieTris,c.cx+c.span*0.24,0.58,c.cz,c.span*0.46,0.32,0.56);
      for(let i=0;i<c.nWheels;i++){
        const wx=c.cx-c.span/2+(c.span/(c.nWheels-1))*i;
        addCylinder(bogieTris,[wx,0.315,c.cz-0.18],[wx,0.315,c.cz+0.18],0.315,0.315,14);
        if(i%2===0){
          // 12 x 5.5 kW VVVF Bevel-Helical Travel Geared Motors
          const side=c.cz>0?0.48:-0.48;
          addCylinder(motorTris,[wx,0.42,c.cz+side*0.4],[wx,0.42,c.cz+side*1.15],0.22,0.22,12);
        }
      }
      // Hydraulic rail clamps & manual storm tie-down anchors at bogie ends
      addBox(clampTris,c.cx+c.span/2+0.55,0.38,c.cz,0.52,0.55,0.52);
    }
    pushPart(map.travelSys,'3-Corner Equalizer Bogies (22 Wheels: 8+7+7 · 8.4 m × 8.5 m)','mechanical',[0.32,0.48,0.43],bogieTris,'22 wheels (8 on Corner A, 7 on B, 7 on C) · 8,400 mm gauge × 8,500 mm leg span · max 27.0 t/wheel',[0,-1.8,0]);
    pushPart(map.travelMotors,'Long-Travel Geared Motors (12 × 5.5 kW VVVF · i=141.93)','electrical',[0.35,0.56,0.49],motorTris,'12 × 5.5 kW VVVF 4-stage bevel-helical geared motors (7 / 20 m/min)',[0,-1.8,1.8]);
    pushPart(map.railClamps,'Hydraulic Rail Clamps & Storm Anchors (73 m/s)','protection',[0.78,0.58,0.24],clampTris,'Motorized hydraulic rail clamps & manual storm tie-downs (35 m/s clamped, 73 m/s anchored)',[0,-1.8,-1.8]);
  }

  // 4. Stacker Portal Gantry Frame (EL +1.15 m to EL +4.475 m, spanning 8.400 m across yard belt)
  {
    const gantryTris=[];
    // Corner A central portal leg (Z = +4.2 m)
    addOrientedBox(gantryTris,[travelM,1.15,4.2],[travelM,4.25,2.1],0.75,0.75,[1,0,0]);
    addOrientedBox(gantryTris,[travelM-3.2,1.15,4.2],[travelM-1.2,4.15,2.1],0.45,0.45,[1,0,0]);
    addOrientedBox(gantryTris,[travelM+3.2,1.15,4.2],[travelM+1.2,4.15,2.1],0.45,0.45,[1,0,0]);
    // Corner B & C double legs (X = ±4.25 m, Z = -4.2 m)
    addOrientedBox(gantryTris,[travelM+4.25,1.15,-4.2],[travelM+1.8,4.25,-2.1],0.68,0.68,[1,0,0]);
    addOrientedBox(gantryTris,[travelM-4.25,1.15,-4.2],[travelM-1.8,4.25,-2.1],0.68,0.68,[1,0,0]);
    addOrientedBox(gantryTris,[travelM-4.25,2.2,-4.2],[travelM+4.25,2.2,-4.2],0.42,0.48,[0,1,0]);
    // Gantry top ring beam & platform at EL +3.51 m .. +4.30 m
    addBox(gantryTris,travelM,4.05,0,5.2,0.65,5.2);
    addRingY(gantryTris,travelM,4.32,0,1.65,2.35,0.28,28);
    pushPart(map.self,'Portal Gantry Structure (32 t · EL +3.51 m CG · 8.4 m Span)','mechanical',[0.42,0.58,0.52],gantryTris,'3-point portal gantry frame spanning 8,400 mm rails over yard conveyor',[0,0,0]);
  }

  // 5. Travelling Trailer Tripper Car (47.878 m horizontal length, 61.480 m belt length, Ø1000 mm head pulley)
  {
    const tripStruct=[],tripBelt=[],tripPulley=[],tripBogie=[],tripChute=[];
    const xTail=travelM-47.878,xHead=travelM-0.45;
    // Inclined lattice bridge from EL +1.35 m at tail to EL +11.15 m at discharge pulley over slew center
    addTrussGirder(tripStruct,[xTail,1.45,0],[xHead,10.85,0],2.65,1.45,14,0.16,0.09,[0,1,0]);
    // Support portal legs along tripper frame riding on 8.4 m rails
    for(const frac of [0.12,0.48,0.82]){
      const xt=xTail+(xHead-xTail)*frac;
      const yt=1.45+(10.85-1.45)*frac;
      addOrientedBox(tripStruct,[xt,yt,-1.35],[xt,0.75,-4.2],0.32,0.32,[1,0,0]);
      addOrientedBox(tripStruct,[xt,yt,1.35],[xt,0.75,4.2],0.32,0.32,[1,0,0]);
      for(const zr of [-4.2,4.2]){
        addBox(tripBogie,xt,0.58,zr,1.8,0.28,0.42);
        addCylinder(tripBogie,[xt-0.55,0.25,zr-0.15],[xt-0.55,0.25,zr+0.15],0.25,0.25,12);
        addCylinder(tripBogie,[xt+0.55,0.25,zr-0.15],[xt+0.55,0.25,zr+0.15],0.25,0.25,12);
      }
    }
    // Tow bar coupling tripper to stacker gantry
    addOrientedBox(tripBogie,[xTail+39.2,0.75,-4.2],[travelM-4.25,0.75,-4.2],0.22,0.22,[0,1,0]);
    addOrientedBox(tripBogie,[xTail+39.2,0.75,4.2],[travelM,0.75,4.2],0.22,0.22,[0,1,0]);
    // Inclined 2000 mm belt & carrying idlers (1.0 m max pitch)
    addTroughBelt(tripBelt,[xTail,1.75,0],[xHead,11.25,0],2.0,35,[0,1,0]);
    // Ø1000 mm Head Discharge Pulley & Bend Pulleys
    addCylinder(tripPulley,[xHead,11.15,-1.15],[xHead,11.15,1.15],0.50,0.50,18);
    addCylinder(tripPulley,[xHead-2.4,9.15,-1.15],[xHead-2.4,9.15,1.15],0.40,0.40,16);
    addCylinder(tripPulley,[xHead+1.8,1.25,-1.15],[xHead+1.8,1.25,1.15],0.40,0.40,16);
    // Transfer Chute & Skirtboard feeding central boom hopper along slew axis
    addBox(tripChute,travelM,10.25,0,2.2,2.4,2.1);
    addCylinder(tripChute,[travelM,8.45,0],[travelM,10.1,0],0.78,0.95,16);

    pushPart(map.tripper,'Travelling Tripper Structure (47,878 mm Horiz · 61,480 mm Belt)','material',[0.48,0.61,0.54],tripStruct,'47,878 mm horizontal length · 61,480 mm inclined belt length · R=100 m curve',[-5,1.5,0]);
    pushPart(map.tripperIdlers,'Tripper Carrying & Impact Idlers (2,000 mm · 1.0 m Pitch)','material',[0.26,0.42,0.36],tripBelt,'2,000 mm belt · 35° trough · max 1.0 m idler spacing for steel-cord belt',[-5,2.2,0]);
    pushPart(map.tripperPulley,'Tripper Ø1,000 mm Discharge Pulley (550 kN) & Bend Pulleys','mechanical',[0.76,0.62,0.32],tripPulley,'Ø1,000 mm head discharge pulley (550 kN rating) + primary/secondary scrapers',[-5,2.8,0]);
    pushPart(map.tripperBogies,'Tripper Rail Bogies (Ø500 mm Wheels) & Tow Bar','mechanical',[0.36,0.50,0.44],tripBogie,'Ø500 mm rail wheels on 8,400 mm gauge + rigid tow bar coupled to stacker',[-5,-1.2,0]);
    pushPart(map.tripperChute,'Tripper Skirtboard & Central Slew Transfer Chute','material',[0.74,0.66,0.45],tripChute,'Hardox-lined transfer hood & central cylindrical chute feeding boom conveyor',[0,2.8,0]);
  }

  // 6. Slewing Bearing (EL +4.475 m, Rothe Erde 132.50.4000.102.04.03F4, OD 4.395 m) & Slew Drives
  {
    const slewRingTris=[],slewDriveTris=[],slewHppTris=[];
    addRingY(slewRingTris,travelM,4.475,0,1.794,2.1975,0.36,36);
    // 2 x HMB20 Hydraulic Slew Motors & Pinions (z=18, m=25) at X = -2.4 m in slewing frame
    const smLocal=[];
    for(const zSide of [-1.25,1.25]){
      addCylinder(smLocal,[-2.15,4.55,zSide],[-2.15,5.65,zSide],0.28,0.28,14);
      addCylinder(smLocal,[-2.15,4.28,zSide],[-2.15,4.65,zSide],0.225,0.225,12);
    }
    // Slew HPP (300 L tank, 22 kW motor, air-oil cooler) at X = -0.95 m, Y = 6.45 m, Z = +3.36 m
    const hppLocal=[];
    addBox(hppLocal,-1.4,6.15,3.1,1.6,1.1,1.1);
    addCylinder(hppLocal,[-1.4,6.85,3.1],[-0.5,6.85,3.1],0.24,0.24,12);

    pushPart(map.slewRing,'Slewing Ring Bearing (Rothe Erde Ø4,395 mm OD · EL +4.475 m)','mechanical',[0.78,0.65,0.34],slewRingTris,'Xuzhou Rothe Erde 132.50.4000.102.04.03F4 · OD 4,395 mm (track Ø4,000 mm) · z=173, m=25 · 6,449 kg',[0,0.8,0]);
    pushPart(map.slewMotors,'Slew Hydraulic Motors & Pinions (2 × HMB20 · 0–100°)','mechanical',[0.54,0.44,0.68],transformVertices(smLocal,slewRad,travelM,0,0),'2 × HMB20 hydraulic motors (20 L/rev) driving z=18 pinions · 0.0758 rpm',[0,1.4,-2.2]);
    pushPart(map.slewHpp,'Slewing Hydraulic Power Pack (22 kW · 300 L · 160/230 bar)','utility',[0.32,0.58,0.66],transformVertices(hppLocal,slewRad,travelM,0,0),'22 kW EM1 motor + 42 L/min Q1 pump + 300 L tank + air-oil cooler',[0,1.8,3.2]);
  }

  // 7. Rotating Turntable Platform (EL +5.40 m), A-Frame Mast (EL +15.00 m), Counterweight Arm (X = -6.15 m, EL +8.50 m, 143 t)
  {
    const superLocal=[];
    // Turntable deck platform at EL +5.40 m
    addBox(superLocal,-1.2,5.15,0,7.8,0.55,5.4);
    // Boom pivot pedestal at X = 0.00 m, EL +7.98 m
    for(const zSide of [-1.45,1.45]){
      addOrientedBox(superLocal,[0,5.4,zSide],[0,8.15,zSide],0.55,0.55,[1,0,0]);
      // A-Frame Mast rising to EL +15.00 m
      addOrientedBox(superLocal,[-1.8,5.4,zSide],[0,15.0,zSide*0.75],0.42,0.42,[1,0,0]);
      addOrientedBox(superLocal,[1.6,5.4,zSide],[0,15.0,zSide*0.75],0.42,0.42,[1,0,0]);
    }
    addOrientedBox(superLocal,[0,15.0,-1.1],[0,15.0,1.1],0.45,0.45,[0,1,0]);
    addOrientedBox(superLocal,[0,11.2,-1.25],[0,11.2,1.25],0.32,0.32,[0,1,0]);
    // Rear Counterweight Cantilever Arm extending to X = -6.150 m, EL +8.500 m (clear headroom >= 2.1 m below)
    addTrussGirder(superLocal,[0,7.98,0],[-6.8,8.5,0],2.6,1.35,4,0.18,0.11,[0,1,0]);
    // Pendant tie-rods from Mast Apex (0, 15.0) to Counterweight Arm (-6.15, 9.1)
    for(const zSide of [-1.05,1.05]){
      addCylinder(superLocal,[0,14.85,zSide],[-6.15,9.15,zSide],0.065,0.065,8);
    }
    // 143-Ton Counterweight Block at X = -6.150 m, EL +8.500 m
    addBox(superLocal,-6.15,8.50,0,2.45,2.35,3.85);

    pushPart(map.slewSys,'Rotating Superstructure, A-Frame Mast (EL +15.0 m) & 143 t Counterweight','mechanical',[0.45,0.59,0.53],transformVertices(superLocal,slewRad,travelM,0,0),'Rotating upper platform (EL +5.40 m), A-frame mast (EL +15.0 m), and 143 t counterweight at X = -6.15 m, EL +8.50 m',[-3.5,2.2,0]);
  }

  // 8. Twin MAHA Luffing Hydraulic Cylinders (Ø250/180 x 2190 mm stroke) & Luffing HPP
  // Exact Pin Coordinates (Stability Calc 175117-ISG-3 p.2):
  // - Lower pin on rotating platform: X = +4.250 m, Y = +4.790 m
  // - Upper pin on boom (at 0 deg): X = +6.525 m, Y = +8.440 m (pivoted around boom pivot 0.000, +7.980 m)
  {
    const cylLocal=[],luffHppLocal=[];
    const pPivot=[0,7.98];
    const dxU=6.525-pPivot[0],dyU=8.440-pPivot[1];
    const cl=Math.cos(luffRad),sl=Math.sin(luffRad);
    const upperX=pPivot[0]+dxU*cl-dyU*sl;
    const upperY=pPivot[1]+dxU*sl+dyU*cl;
    for(const zSide of [-1.35,1.35]){
      const pBot=[4.250,4.790,zSide];
      const pTop=[upperX,upperY,zSide];
      const pMid=V3.lerp(pBot,pTop,0.56);
      // Cylinder barrel (Ø250 mm outer tube, shown at 0.22 m radius for crisp visibility) & chrome piston rod (Ø180 mm)
      addCylinder(cylLocal,pBot,pMid,0.18,0.18,14);
      addCylinder(cylLocal,pMid,pTop,0.125,0.125,14);
      // Trunnion & spherical plain bearing mounts (SKF GE-120 TE-2RS)
      addBox(cylLocal,pBot[0],pBot[1],zSide,0.48,0.48,0.42);
      addBox(cylLocal,pTop[0],pTop[1],zSide,0.44,0.44,0.38);
    }
    // Luffing HPP (400 L reservoir, 22 kW axial piston pump) on rotating platform
    addBox(luffHppLocal,1.35,6.15,-2.95,1.85,1.25,1.25);
    addCylinder(luffHppLocal,[0.8,6.95,-2.95],[1.9,6.95,-2.95],0.25,0.25,12);

    pushPart(map.luffCyl,'MAHA Luffing Hydraulic Cylinders (2 × Ø250/180 × 2,190 mm Stroke)','mechanical',[0.24,0.52,0.62],transformVertices(cylLocal,slewRad,travelM,0,0),'2 × MAHA double-acting cylinders (Bore Ø250 mm, Rod Ø180 mm, Stroke 2,190 mm, 140/210 bar) · pins (4.25 m, +4.79 m) → (6.525 m, +8.44 m)',[1.5,1.8,0]);
    pushPart(map.luffHpp,'Luffing Hydraulic Power Pack (22 kW · 400 L Reservoir · 180 bar)','utility',[0.30,0.56,0.66],transformVertices(luffHppLocal,slewRad,travelM,0,0),'22 kW motor + axial piston pump + 400 L reservoir + TP29/TP30 over-centre & burst valves',[0,1.6,-3.2]);
  }

  // 9. Luffing Boom Conveyor (41.755 m Pivot-to-Head Pulley, Pivoted at X = 0.000 m, EL +7.980 m)
  // Plus Pendant Suspension Tie-Rods from Mast Apex (0, 15.00) to Boom Mid/Head
  {
    const boomTrussLocal=[],boomBeltLocal=[],weigherLocal=[],driveLocal=[];
    // Main 41.755 m Boom Space-Frame Truss (from tail X = -2.80 m to head pulley X = +41.755 m and walkway X = +44.75 m)
    addTrussGirder(boomTrussLocal,[-2.8,7.98,0],[42.2,7.98,0],2.75,1.85,18,0.17,0.10,[0,1,0]);
    // Boom head discharge hood & maintenance walkway to X = 44.75 m
    addBox(boomTrussLocal,43.1,7.85,0,2.2,1.65,2.4);
    addBox(boomTrussLocal,20.0,7.15,1.72,43.5,0.12,0.80); // 800 mm maintenance walkway along boom
    // Upper pendant tie-bars from Mast Apex to Boom (at X = 22.5 m)
    const pPivot=[0,7.98],cl=Math.cos(luffRad),sl=Math.sin(luffRad);
    const anchorX=22.5,anchorY=8.95;
    const rotAnchorX=pPivot[0]+(anchorX-pPivot[0])*cl-(anchorY-pPivot[1])*sl;
    const rotAnchorY=pPivot[1]+(anchorX-pPivot[0])*sl+(anchorY-pPivot[1])*cl;
    const tieWorld=[];
    for(const zSide of [-1.05,1.05]){
      addCylinder(tieWorld,[0,14.85,zSide],[rotAnchorX,rotAnchorY,zSide],0.06,0.06,8);
    }

    // Boom Conveyor 2000 mm Belt, Ø800 mm Drive Pulley (X = -2.50 m, EL +9.215 m) & Head Non-Drive Pulley (X = +41.755 m)
    addTroughBelt(boomBeltLocal,[-2.5,8.95,0],[41.755,8.95,0],2.0,35,[0,1,0]);
    addCylinder(boomBeltLocal,[-2.5,8.85,-1.15],[-2.5,8.85,1.15],0.42,0.42,16); // Ø800 mm drive pulley
    addCylinder(boomBeltLocal,[41.755,8.75,-1.15],[41.755,8.75,1.15],0.42,0.42,16); // Ø800 mm head pulley
    // Carrying idlers (every 2.5 m visually, representing 1.0 m pitch)
    for(let x=0;x<=40;x+=2.5){
      addCylinder(boomBeltLocal,[x,8.72,-1.05],[x,8.72,1.05],0.08,0.08,8);
    }

    // 4-Idler Load-Cell Boom Belt Weigher (Thermo Fisher Micro-Tech 9101/9201) at X = 11.5 m .. 15.5 m
    addBox(weigherLocal,13.5,8.68,0,4.2,0.38,2.45);
    addBox(weigherLocal,13.5,9.55,1.65,0.55,0.68,0.42); // Integrator & summing box

    // Boom Conveyor Dual Drive Group (2 x 132 kW Motors + Fluid Couplings + 20:1 Bevel-Helical Gearboxes + Ø400 mm Thruster Brakes) at X = -1.30 m, EL +9.00 m
    const gboxLocal=[],fcoupLocal=[],bmotLocal=[],bbrakeLocal=[];
    for(const zSide of [-1.95,1.95]){
      addBox(gboxLocal,-2.1,8.85,zSide,1.35,1.05,0.95); // 20:1 Bevel-helical gearbox
      addCylinder(fcoupLocal,[-1.1,8.85,zSide],[-0.45,8.85,zSide],0.34,0.34,14); // Fluid coupling
      addCylinder(bmotLocal,[-0.4,8.85,zSide],[0.85,8.85,zSide],0.42,0.42,14); // 132 kW motor
      addCylinder(bbrakeLocal,[-1.4,9.45,zSide],[-1.4,9.85,zSide],0.22,0.22,12); // Ø400 mm thruster drum brake
    }

    const boomTrussWorld=[
      ...transformLuffAndSlew(boomTrussLocal,0,7.98,luffRad,slewRad,travelM,0,0),
      ...transformVertices(tieWorld,slewRad,travelM,0,0)
    ];
    pushPart(map.boom,'Luffing Boom Lattice Girder (41,755 mm Pivot-to-Head · EL +7.98 m Pivot)','material',[0.52,0.65,0.58],boomTrussWorld,'41.755 m boom length (44.75 m to head walkway) · luffing -8° to +14° · 800 mm walkway',[3.5,2.5,0]);
    pushPart(map.boomBelt,'Boom Conveyor Belt & Ø800 mm Pulleys (2,000 mm · 3.6 m/s · 3,740 TPH)','material',[0.24,0.39,0.34],transformLuffAndSlew(boomBeltLocal,0,7.98,luffRad,slewRad,travelM,0,0),'2,000 mm belt · 3.6 m/s · 3,400 rated / 3,740 design TPH · Ø800 mm drive & head pulleys',[3.5,3.2,0]);
    pushPart(map.weigher,'Boom 4-Idler Load-Cell Belt Weigher (Thermo Fisher Micro-Tech)','control',[0.82,0.64,0.26],transformLuffAndSlew(weigherLocal,0,7.98,luffRad,slewRad,travelM,0,0),'4-idler pivoting weighbridge + 350-ohm load cells + 60-12C speed sensor + Micro-Tech 9101/9201 integrator',[3.5,3.8,1.5]);
    pushPart(map.boomMotors,'Boom Drive Motors (2 × 132 kW · 1,485 rpm)','electrical',[0.36,0.58,0.51],transformLuffAndSlew(bmotLocal,0,7.98,luffRad,slewRad,travelM,0,0),'2 × 132 kW, 1,485 rpm squirrel-cage induction motors driving boom conveyor',[-1.5,3.2,2.8]);
    pushPart(map.boomCouplings,'Boom Constant-Fill Fluid Couplings (2 × 132 kW · Fusible Plug)','mechanical',[0.80,0.68,0.36],transformLuffAndSlew(fcoupLocal,0,7.98,luffRad,slewRad,travelM,0,0),'2 × 132 kW delayed-chamber constant-fill fluid couplings with 130°C/140°C fusible plugs',[-2.2,3.2,2.4]);
    pushPart(map.boomGearboxes,'Boom 3-Stage Bevel-Helical Gearboxes (2 × i=20:1)','mechanical',[0.56,0.46,0.72],transformLuffAndSlew(gboxLocal,0,7.98,luffRad,slewRad,travelM,0,0),'2 × 3-stage bevel-helical gearboxes (nominal ratio 20:1) with shrink-disc output couplings',[-3.0,3.2,2.0]);
    pushPart(map.boomBrakes,'Boom Electro-Hydraulic Thruster Drum Brakes (2 × Ø400 mm)','protection',[0.78,0.56,0.26],transformLuffAndSlew(bbrakeLocal,0,7.98,luffRad,slewRad,travelM,0,0),'2 × Ø400 mm electro-hydraulic thruster drum brakes (Series YWZ5 / DIN 15435)',[-2.6,3.8,2.4]);
  }

  // 10. Electrical House (10.5 x 3.0 x 2.7 m), Operator Cabin (2.4 x 1.9 x 2.4 m), Fire Detection (FMZ5000), Onboard DSS & Central Grease Lube
  {
    const ehouseLocal=[],cabinLocal=[],dssLocal=[],lubeLocal=[];
    // Electrical House (10.5 m x 3.0 m x 2.7 m) mounted on rear/side cantilever of rotating deck
    addBox(ehouseLocal,-3.6,6.85,-3.95,10.5,2.7,3.0);
    // Operator Cabin (2.4 m x 1.9 m x 2.4 m) on forward boom-side cantilever boom-view arm
    addBox(cabinLocal,3.4,9.65,3.35,2.4,2.4,1.9);
    addOrientedBox(cabinLocal,[1.2,7.2,2.2],[3.4,8.45,3.35],0.45,0.45,[0,1,0]);
    // Onboard Plain-Water DSS Skid & SS Water Tank (4.9 m3/h pump set + tank + hose reel)
    addCylinder(dssLocal,[-4.8,6.05,3.25],[-4.8,7.65,3.25],0.85,0.85,16);
    addBox(dssLocal,-3.2,6.05,3.25,1.4,0.95,1.1);
    // Central Grease Lubrication (3 x Lincoln KSP8-65S / ZPU 08/14 pump stations)
    addBox(lubeLocal,0.6,6.15,3.25,1.2,1.1,0.95);

    pushPart(map.ehouse,'Electrical House (10.5 × 3.0 × 2.7 m · Z101 Clean-Agent Protected)','electrical',[0.62,0.71,0.67],transformVertices(ehouseLocal,slewRad,travelM,0,0),'10.5 × 3.0 × 2.7 m pressurized E-House protected by FMZ5000 & Z101 HFC-227ea cylinders (2 × 80 L)',[-3.0,2.5,-3.5]);
    pushPart(map.cabin,'Operator Cabin (2.4 × 1.9 × 2.4 m A/C · Z201 Protected)','control',[0.76,0.84,0.80],transformVertices(cabinLocal,slewRad,travelM,0,0),'2.4 × 1.9 × 2.4 m dust-proof A/C cabin with PLC HMI & Z201 HFC-227ea protection',[2.5,3.0,3.5]);
    pushPart(map.dss,'Onboard Plain-Water DSS (SS Tank + 4.9 m³/h Pump + AP-1/2/3 Sprays)','utility',[0.32,0.64,0.72],transformVertices(dssLocal,slewRad,travelM,0,0),'SS water tank + 1W+1S 4.9 m³/h pumps + AP-1 (6 nozzles), AP-2 (12 nozzles), AP-3 (16 nozzles)',[-2.5,2.0,3.5]);
    pushPart(map.lube,'Lincoln Motorized Central Grease Lubrication (3 Circuits · 30 MPa)','utility',[0.76,0.64,0.32],transformVertices(lubeLocal,slewRad,travelM,0,0),'3 independent Lincoln KSP8-65S / ZPU 08/14 grease circuits (Slew/Boom, Long-Travel, Tripper)',[1.0,2.0,3.5]);
  }

  // 11. 3D Coal Stockpile (EAE-1..4: 52.0 m Base Width x 16.0 m Peak Height, 37° Angle of Repose) & Falling Coal Trajectory
  {
    const pileTris=[],streamTris=[];
    addStockpilePrism(pileTris,-32,48,-62.5,-10.5,16.0,0.0,14);
    // Compute exact 3D world position of Boom Head Pulley (42.2, 8.75, 0) after luff & slew
    const headPt=transformLuffAndSlew([[42.2,8.55,0]],0,7.98,luffRad,slewRad,travelM,0,0)[0];
    const groundY=headPt[2]<-11?Math.max(0.5,Math.min(15.5,16.0*(1-Math.abs(headPt[2]+36.5)/26))):0.2;
    // Animated falling coal trajectory stream from boom head to stockpile
    const segs=8;
    for(let i=0;i<segs;i++){
      const t0=i/segs,t1=(i+1)/segs;
      const p0=[headPt[0],headPt[1]*(1-t0*t0)+groundY*(t0*t0),headPt[2]];
      const p1=[headPt[0],headPt[1]*(1-t1*t1)+groundY*(t1*t1),headPt[2]];
      const rPulse=0.42+0.12*Math.sin(phase*6+i*1.3);
      addCylinder(streamTris,p0,p1,rPulse*(0.7+0.3*t0),rPulse*(0.7+0.5*t1),10);
    }
    pushPart(map.stockpile,'Coal Stockpile Windrow (52.0 m Width × 16.0 m Height · 37° Repose)','material',[0.24,0.31,0.32],pileTris,'52.0 m base width × 16.0 m max height × 710 m length · 37° angle of repose · 0.8–1.1 t/m³',[0,0,6.0],true);
    pushPart(map.boom,'Active Stacking Coal Stream (3,400 / 3,740 TPH Discharge)','material',[0.68,0.46,0.22],streamTris,'3,400 TPH rated / 3,740 TPH design coal discharge trajectory from boom head pulley',[0,0,0]);
  }

  // Engineering Dimension Callout Anchors in 3D World Space
  const headWorld=transformLuffAndSlew([[41.755,8.75,0]],0,7.98,luffRad,slewRad,travelM,0,0)[0];
  const pivotWorld=[travelM,7.98,0];
  const cwtWorld=transformVertices([[-6.15,8.50,0]],slewRad,travelM,0,0)[0];
  const dimLines=[
    {a:[travelM+12,0.2,-4.2],b:[travelM+12,0.2,4.2],label:'Rail Gauge: 8,400 mm (UIC60)'},
    {a:[travelM-4.25,0.4,-5.5],b:[travelM+4.25,0.4,-5.5],label:'Bogie Leg Span: 8,500 mm (22 Wheels)'},
    {a:[travelM-47.878,2.2,-2.2],b:[travelM-6.0,2.2,-2.2],label:'Travelling Tripper: 47,878 mm Horiz (61.48 m Belt)'},
    {a:pivotWorld,b:headWorld,label:`Luffing Boom: 41,755 mm (Luff ${luffDeg>=0?'+'+luffDeg:luffDeg}°, Slew ${slewDeg}°)`},
    {a:[travelM,4.5,0],b:[travelM,15.0,0],label:'Mast Apex: EL +15.00 m (Pivot EL +7.98 m)'},
    {a:pivotWorld,b:cwtWorld,label:'Counterweight Arm: 6,150 mm (143 t @ EL +8.50 m)'},
    {a:[18,0.4,-62.5],b:[18,0.4,-10.5],label:'Stockpile Width: 52,000 mm × 16.0 m H (37°)'}
  ];

  // Calculate exact Luffing Cylinder stroke extension for HUD readout
  const dxU=6.525,dyU=8.440-7.980;
  const uX=dxU*Math.cos(luffRad)-dyU*Math.sin(luffRad);
  const uY=7.980+dxU*Math.sin(luffRad)+dyU*Math.cos(luffRad);
  const cylLenMm=Math.round(Math.hypot(uX-4.250,uY-4.790)*1000);
  const strokeMm=Math.max(0,Math.min(2190,cylLenMm-3560));

  return {
    items,
    dimLines,
    telemetry:[
      {label:'Rail Gauge',value:'8,400 mm (UIC60)'},
      {label:'Boom Length',value:'41,755 mm (Pivot EL +7.98 m)'},
      {label:'Slew Angle',value:`${slewDeg.toFixed(1)}° (0–100° · Ø4,395 Ring)`},
      {label:'Luff Angle / Cyl',value:`${luffDeg>=0?'+'+luffDeg.toFixed(1):luffDeg.toFixed(1)}° (Stroke ${strokeMm} / 2,190 mm)`},
      {label:'Tripper Length',value:'47,878 mm Horiz / 61,480 mm Belt'},
      {label:'Counterweight',value:'143 t @ -6,150 mm Arm'}
    ]
  };
}

// --- Full Portal Scraper Reclaimer (EAF-1..4) True-Scale 3D Procedural Builder ---
// Exact Dimensions from Tenova BOD 47039270 (175119-ISG-2), Stability 47039272 (175118-ISG-1) & GA 175127-ISG:
// - Rail Track Span: 55.800 m (Pendulum Side Rail B at X = -27.900 m [Tenova X=0.0m], Fixed Side Rail A at X = +27.900 m [Tenova X=55.8m])
// - Yard Reclaim Conveyor (EBA-8/10/12/14): at Tenova X = 58.000 m (X = +30.100 m, 2.200 m outboard of Fixed Rail A)
// - Fixed Side Bogies (Rail A): Corner A1 (6 wheels) at Z = +8.000 m, Corner A2 (8 wheels) at Z = -7.000 m -> 15.000 m span, 14 wheels (Ø630 mm)
// - Pendulum Side Bogies (Rail B): Corner B1 (4 wheels) at Z = +3.500 m, Corner B2 (4 wheels) at Z = -3.500 m -> 7.000 m span, 8 wheels (Ø630 mm)
// - Pendulum Hinge Pin: EL +3.710 m above Rail B
// - Portal Centerline: Z = +3.500 m from boom axis (Pendulum center at Z = +2.555 m)
// - Portal Bridge Structure: 55.800 m span, ~20.0 m crown height, 266,479 kg (417,025 kg total machine mass)
// - Main Scraper Boom: 37.145 m sprocket centers, 500 mm chain pitch, 1500 kN, 2500 x 500 mm Hardox blades @ 1000 mm spacing, 0.69 m/s, 2x110 kW drive
// - Auxiliary Scraper Boom: 14.800 m sprocket centers, Ø1294 mm sprocket, 400 mm chain pitch, 1800 x 450 mm blades @ 800 mm spacing, 0.62 m/s, 2x30 kW drive
// - Portal Boom Hoist Winch: 45 kW VFD, Ø1300 mm winch drum, Ø800 mm sheaves, Ø28 mm wire rope (34 m/min rope, 3 m/min boom)

function buildReclaimerScene3D(scene,state3d){
  const map=resolveEntityMap(scene);
  const mainBoomDeg=state3d.mainBoomDeg??-14;
  const auxBoomDeg=state3d.auxBoomDeg??-16;
  const travelM=state3d.travelM??0;
  const phase=state3d.phase??0;
  const explode=state3d.exploded?1:0;

  // Scene X is centered between Rail B and Rail A:
  // Rail B (Pendulum Side, Tenova X = 0.000 m) -> xB = -27.900 m
  // Rail A (Fixed Side, Tenova X = 55.800 m)   -> xA = +27.900 m (Span = 55.800 m)
  // Yard Reclaim Conveyor (Tenova X = 58.000 m)-> xConv = +30.100 m
  const xB=-27.9,xA=27.9,xConv=30.1;
  const zBoom=travelM;
  const zPortal=travelM+3.5; // Portal is 3.500 m offset from boom centerline per Tenova BOD p.10
  const items=[];

  const pushPart=(id,label,network,color,tris,specSummary,explodeVec=[0,0,0],isContext=false)=>{
    if(!tris.length)return;
    const verts=explode?tris.map(v=>[v[0]+explodeVec[0],v[1]+explodeVec[1],v[2]+explodeVec[2]]):tris;
    let lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
    for(const v of verts)for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],v[k]);hi[k]=Math.max(hi[k],v[k]);}
    const centre=[(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2];
    items.push({
      entity_id:id,
      part_key:label,
      label,
      network,
      color,
      spec:specSummary,
      isContext,
      centre,
      bbox:{lo,hi,size:[hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]]},
      vertices:verts
    });
  };

  // 1. 55.800 m Span UIC60 Rails (Rail B at X = -27.90 m, Rail A at X = +27.90 m) & Reclaim Conveyor EBA at X = +30.10 m
  {
    const railTris=[],convTris=[];
    for(const xr of [xB,xA]){
      addBox(railTris,xr,0.08,0,0.16,0.16,96);
      addBox(railTris,xr,-0.18,0,0.75,0.36,96);
    }
    // Yard Reclaim Conveyor (EBA-8/10/12/14) at Tenova X = 58.000 m (2.200 m outboard of Fixed Rail A) + 8.0 m Impact Table
    addTroughBelt(convTris,[xConv,1.35,-46],[xConv,1.35,46],1.8,35,[0,1,0]);
    addBox(convTris,xConv,1.15,zBoom,2.3,0.45,8.0); // 8.0 m impact table & receiving skirt trough at X=58.0m, Z=1.351m
    for(let z=-44;z<=44;z+=4.0){
      addBox(convTris,xConv-0.95,0.65,z,0.12,1.3,0.12);
      addBox(convTris,xConv+0.95,0.65,z,0.12,1.3,0.12);
    }
    pushPart(map.travelWheels,'UIC60 Portal Rails (55,800 mm Track Span · Rail B & Rail A)','mechanical',[0.46,0.52,0.49],railTris,'55.800 m rail centres (UIC60) · 714.75 m travel distance · 740.965 m buffer-to-buffer',[0,-2.5,0],true);
    pushPart(map.reclaimBelt,'Yard Reclaim Conveyor & 8.0 m Impact Table (X = 58.000 m)','material',[0.26,0.42,0.36],convTris,'Located at X = 58.000 m (2.200 m outboard of Fixed Rail A) · 8.0 m impact table @ EL +1.351 m',[3.5,-1.5,0],true);
  }

  // 2. Travel Bogies (Fixed Side A1: 6 wheels @ +8.0m, A2: 8 wheels @ -7.0m [15.0m span]; Pendulum Side B1: 4 wheels @ +3.5m, B2: 4 wheels @ -3.5m [7.0m span])
  {
    const bogieTris=[],motorTris=[],clampTris=[],anchorTris=[],bufferTris=[];
    const corners=[
      {x:xA,z:zBoom+8.0,nWheels:6,span:5.2,nDrives:4,tag:'A1 Fixed'},
      {x:xA,z:zBoom-7.0,nWheels:8,span:6.8,nDrives:4,tag:'A2 Fixed'},
      {x:xB,z:zBoom+2.555+3.5,nWheels:4,span:3.6,nDrives:2,tag:'B1 Pendulum'},
      {x:xB,z:zBoom+2.555-3.5,nWheels:4,span:3.6,nDrives:2,tag:'B2 Pendulum'}
    ];
    for(const c of corners){
      addBox(bogieTris,c.x,0.92,c.z,0.82,0.52,c.span+0.9);
      addBox(bogieTris,c.x,0.56,c.z-c.span*0.24,0.68,0.34,c.span*0.45);
      addBox(bogieTris,c.x,0.56,c.z+c.span*0.24,0.68,0.34,c.span*0.45);
      for(let i=0;i<c.nWheels;i++){
        const wz=c.z-c.span/2+(c.span/(c.nWheels-1))*i;
        // Ø630 mm travel wheel (radius 0.315 m)
        addCylinder(bogieTris,[c.x-0.18,0.315,wz],[c.x+0.18,0.315,wz],0.315,0.315,14);
        if(i<c.nDrives){
          const side=c.x>0?-0.52:0.52;
          addCylinder(motorTris,[c.x+side*0.4,0.44,wz],[c.x+side*1.2,0.44,wz],0.22,0.22,12);
        }
      }
      // 8 Spring Buffers (210 mm stroke, 2 per corner end)
      for(const sEnd of [-1,1]){
        const bz=c.z+sEnd*(c.span/2+0.65);
        addCylinder(bufferTris,[c.x,0.52,bz],[c.x,0.52,bz+sEnd*0.45],0.16,0.14,10);
      }
    }
    // 2 Hydraulic Rail Clamps (10 t capacity) on Fixed & Pendulum rails
    addBox(clampTris,xA,0.42,zBoom+0.5,0.62,0.62,0.75);
    addBox(clampTris,xB,0.42,zBoom+2.555,0.62,0.62,0.75);
    // TAKRAF Storm Anchor System (73 m/s wind lock: pin at 9.225 m on Rail A side, 2.858 m on Rail B side)
    addOrientedBox(anchorTris,[xA,9.225,zBoom+0.5],[xA,0.35,zBoom+0.5],0.26,0.26,[1,0,0]);
    addOrientedBox(anchorTris,[xB,2.858,zBoom+2.555],[xB,0.35,zBoom+2.555],0.26,0.26,[1,0,0]);

    pushPart(map.travelWheels,'Portal Travel Bogies (22 × Ø630 mm Wheels: A1=6, A2=8, B1=4, B2=4)','mechanical',[0.32,0.48,0.43],bogieTris,'Fixed Side Rail A: 6+8=14 wheels (15.0 m span) · Pendulum Side Rail B: 4+4=8 wheels (7.0 m span) · Ø630 mm · 270 kN max',[0,-1.8,0]);
    pushPart(map.travelMotors,'Travel Geared Motors (12 × 5.5 kW VFD Bevel-Helical)','electrical',[0.35,0.56,0.49],motorTris,'12 × 5.5 kW VFD hollow-shaft bevel-helical geared motors (8 Fixed + 4 Pendulum · 2–8 / 20 m/min)',[0,-1.8,2.0]);
    pushPart(map.hydClamps,'Hydraulic Rail Clamps (2 × 10 t Clamping Force)','protection',[0.78,0.58,0.24],clampTris,'2 × 10 t motorized hydraulic rail clamps acting on UIC60 rails',[0,-1.8,-2.0]);
    pushPart(map.stormAnchors,'TAKRAF Manual Storm Anchors (73 m/s Wind Lock · Pins @ 9.225 m & 2.858 m)','protection',[0.82,0.52,0.22],anchorTris,'Drawing 175135-ISG-0: storm tie-downs for 73 m/s wind (Rail A pin EL +9.225 m, Rail B pin EL +2.858 m)',[0,-1.2,-2.5]);
    pushPart(map.buffers,'Spring Buffers (8 Nos · 210 mm Stroke · 39 kN)','protection',[0.68,0.56,0.28],bufferTris,'8 × spring buffers (4 Fixed Side + 4 Pendulum Side · 210 mm stroke)',[0,-2.2,0]);
  }

  // 3. 55.800 m Span Full Portal Bridge & Head Beam Assembly (266,479 kg, Polygonal Pitched A-Frame Arch, Crown Sheave EL +22.80 m, Pendulum Pin EL +3.710 m)
  // Exact Tenova Geometry (Wind Load & Stability Calcs 47039272 / 175118-ISG-1 & Drawing 175135-ISG-0):
  // - Pendulum Leg Hinge Pin: X_tenova = 0.000 m (X = -27.90 m), Z = zBoom + 2.555 m, EL +3.710 m (Head beam CG EL +2.016 m)
  // - Long Sloped Pendulum Lattice Leg (~38.5° matching 37° stockpile): spans 23.40 m horizontally from X = -27.90 m (EL +3.71 m) -> knee (-16.20 m, EL +12.90 m) -> Left Crown Shoulder X = -4.50 m [X_tenova = 23.40 m] (EL +21.80 m)
  // - Compact Horizontal Portal Crown Section: only 11.00 m wide (~19.7% of 55.8 m span), from X = -4.50 m to X = +6.50 m [X_tenova = 23.40..34.40 m] at EL +21.80 m
  // - Crown Sheave Support Frame: X_tenova = 35.800 m (X = +7.90 m), EL +22.800 m
  // - Long Sloped Fixed-Side Double-Leg A-Frame: spans 21.40 m horizontally from Fixed Head Beam at X = +27.90 m [X_tenova = 55.80 m] (EL +7.464 m, storm lock pin EL +9.225 m) -> knee (+17.50 m, EL +14.80 m) -> Right Crown Shoulder X = +6.50 m (EL +21.80 m)
  {
    const portalTris=[];
    const zA1=zBoom+8.0,zA2=zBoom-7.0;
    const zPend=zBoom+2.555,zB1=zPend+3.5,zB2=zPend-3.5;

    // Pendulum Side (Rail B, X = -27.90 m): Equalizer Rocker Triangle from B1/B2 bogies (7.0 m span) up to Pendulum Hinge Pin at EL +3.710 m
    addOrientedBox(portalTris,[xB,1.15,zB1],[xB,3.71,zPend],0.62,0.62,[1,0,0]);
    addOrientedBox(portalTris,[xB,1.15,zB2],[xB,3.71,zPend],0.62,0.62,[1,0,0]);
    addOrientedBox(portalTris,[xB,1.35,zB2],[xB,1.35,zB1],0.55,0.55,[0,1,0]);
    // Pendulum Hinge Pin at EL +3.710 m (Y_tenova = +2.555 m)
    addCylinder(portalTris,[xB,3.71,zPend-0.75],[xB,3.71,zPend+0.75],0.44,0.44,16);

    // Long Sloped Pendulum Lattice Leg (23.40 m horizontal run closely clearing the 37° stockpile slope):
    // Lower inclined segment: (-27.90, 3.71, zPend) -> intermediate polygonal knee (-16.20, 12.90, zPortal)
    // Upper inclined segment: (-16.20, 12.90, zPortal) -> Left Crown Shoulder (-4.50, 21.80, zPortal)
    const pKnee=[-16.20,12.90,zPortal];
    const pCrownL=[-4.50,21.80,zPortal];
    const pCrownR=[6.50,21.80,zPortal];
    const fKnee1=[17.50,14.80,zPortal+2.8];
    const fKnee2=[17.50,14.80,zPortal-2.8];
    addTrussGirder(portalTris,[xB,3.71,zPend],pKnee,1.95,1.85,6,0.22,0.12,[0,0,1]);
    addTrussGirder(portalTris,pKnee,pCrownL,2.10,1.95,6,0.22,0.12,[0,0,1]);

    // Fixed Side (Rail A, X = +27.90 m): Lower Portal Frame (15.0 m span A1..A2, Head Beam at EL +7.464 m, Storm Pin at EL +9.225 m)
    addOrientedBox(portalTris,[xA,1.35,zA2],[xA,1.35,zA1],0.75,0.85,[0,1,0]); // Lower bogie tie beam
    // Fixed-side vertical/battered lower portal columns from bogies (EL +1.35 m) to Fixed Head Beam deck (EL +7.464 m)
    addTrussGirder(portalTris,[xA,1.35,zA1],[xA-0.8,7.464,zA1-1.2],1.65,1.65,4,0.22,0.12,[0,0,1]);
    addTrussGirder(portalTris,[xA,1.35,zA2],[xA-0.8,7.464,zA2+1.2],1.65,1.65,4,0.22,0.12,[0,0,1]);
    // Fixed Side Head Beam horizontal portal girder at EL +7.464 m (spanning between A1 and A2 columns)
    addTrussGirder(portalTris,[xA-0.8,7.464,zA2+0.8],[xA-0.8,7.464,zA1-0.8],1.75,1.55,6,0.22,0.11,[0,1,0]);

    // Long Sloped Fixed-Side A-Frame Double Lattice Legs (21.40 m horizontal run from X = +27.1 m, EL +7.464 m up to Right Crown Shoulder X = +6.50 m, EL +21.80 m)
    addTrussGirder(portalTris,[xA-0.8,7.464,zA1-1.2],fKnee1,1.85,1.75,5,0.22,0.12,[0,0,1]);
    addTrussGirder(portalTris,[xA-0.8,7.464,zA2+1.2],fKnee2,1.85,1.75,5,0.22,0.12,[0,0,1]);
    addTrussGirder(portalTris,fKnee1,[pCrownR[0],pCrownR[1],zPortal+1.1],1.95,1.85,6,0.22,0.12,[0,0,1]);
    addTrussGirder(portalTris,fKnee2,[pCrownR[0],pCrownR[1],zPortal-1.1],1.95,1.85,6,0.22,0.12,[0,0,1]);
    // Cross-portal K-bracing & tie strut between Fixed A-frame legs at intermediate knee (X = +17.50 m, EL +14.80 m) and winch deck (X = +20.90 m, EL +12.30 m)
    addOrientedBox(portalTris,fKnee2,fKnee1,0.52,0.62,[0,1,0]);
    addOrientedBox(portalTris,[20.90,12.0,zA2+2.2],[20.90,12.0,zA1-2.2],0.55,0.65,[0,1,0]);

    // Compact Top Horizontal Portal Crown Girder (-4.50 m to +6.50 m at EL +21.80 m -> only 11.0 m wide, ~19.7% of span!)
    addTrussGirder(portalTris,pCrownL,pCrownR,2.50,2.20,5,0.24,0.13,[0,1,0]);
    // Knee haunch struts under crown shoulders (-4.50 m and +6.50 m) for authentic Tenova polygonal arch silhouette
    addOrientedBox(portalTris,[-8.8,18.4,zPortal],[-2.2,21.0,zPortal],0.45,0.52,[0,0,1]);
    addOrientedBox(portalTris,[10.8,18.6,zPortal],[4.2,21.0,zPortal],0.45,0.52,[0,0,1]);

    // Elevated Crown Sheave Support Frame at X_tenova = 35.800 m (X = +7.90 m), EL +22.800 m
    addBox(portalTris,7.90,22.45,zPortal,2.6,1.3,2.8);
    addOrientedBox(portalTris,[6.50,21.80,zPortal],[7.90,22.80,zBoom],0.48,0.58,[0,1,0]);

    pushPart(map.self,'55.8 m Span Polygonal Portal Arch & Pendulum Leg (266.5 t · EL +22.8 m Crown)','mechanical',[0.42,0.58,0.52],portalTris,'55.800 m rail span · long ~38.5° sloped legs (44.8 m combined run) + compact 11.0 m central crown @ EL +21.8–22.8 m · 266,479 kg',[0,2.8,0]);
  }

  // 4. Luffable Main Scraper Boom (37.145 m Sprocket Centres, 62,495 kg, 1250/1375 TPH)
  // Pivoted on Fixed Side near X = +26.8 m (Tenova X = 54.7 m), EL +4.75 m, discharging at X = +30.1 m (Tenova X = 58.0 m)
  const mainPivot=[26.8,4.75,zBoom];
  const mainRad=(mainBoomDeg*Math.PI)/180;
  // Main boom extends toward -X (into stockpile): angle mainBoomDeg tips the tail down/up
  const mainTail=[
    mainPivot[0]-37.145*Math.cos(mainRad),
    mainPivot[1]+37.145*Math.sin(mainRad),
    zBoom
  ];
  {
    const mBoomTris=[],mChainTris=[],mBladeTris=[],mTakeupTris=[],mDriveTris=[];
    const mHead=[mainPivot[0]+2.6,mainPivot[1]+0.65,zBoom];
    addTrussGirder(mBoomTris,mainTail,mHead,2.6,1.65,15,0.18,0.10,[0,1,0]);
    // Discharge chute from Main Boom head into Yard Reclaim Conveyor (xConv = +30.1 m)
    addBox(mBoomTris,xConv-0.4,3.15,zBoom,2.4,2.6,2.4);

    // Sprockets (Head Drive Sprocket & Tail Take-up Sprocket, 37.145 m C-C)
    addCylinder(mChainTris,[mainPivot[0],mainPivot[1],zBoom-1.25],[mainPivot[0],mainPivot[1],zBoom+1.25],0.68,0.68,16);
    addCylinder(mChainTris,[mainTail[0],mainTail[1],zBoom-1.25],[mainTail[0],mainTail[1],zBoom+1.25],0.62,0.62,16);

    // Dual-Strand 500 mm Pitch Roller-Bush Chain (1500 kN) & 2500 x 500 mm Hardox Scraper Blades (1000 mm spacing)
    const boomVec=V3.sub(mainPivot,mainTail);
    const {up:bUp}=basisFromAxis(boomVec,[0,1,0]);
    const topOff=V3.mul(bUp,0.62),botOff=V3.mul(bUp,-0.62);
    for(const zChain of [zBoom-1.15,zBoom+1.15]){
      addOrientedBox(mChainTris,[mainTail[0]+topOff[0],mainTail[1]+topOff[1],zChain],[mainPivot[0]+topOff[0],mainPivot[1]+topOff[1],zChain],0.12,0.14,bUp);
      addOrientedBox(mChainTris,[mainTail[0]+botOff[0],mainTail[1]+botOff[1],zChain],[mainPivot[0]+botOff[0],mainPivot[1]+botOff[1],zChain],0.12,0.14,bUp);
    }
    // 36 Scraper Blades (2500 mm wide x 500 mm high) along lower scraping run (moving toward +X reclaim belt) & upper return run
    const nBlades=19;
    const shift=((phase*0.69)%1.0);
    for(let i=0;i<nBlades;i++){
      const tBot=(i+shift)/nBlades;
      const pBot=V3.add(V3.lerp(mainTail,mainPivot,tBot),botOff);
      addBox(mBladeTris,pBot[0],pBot[1],zBoom,0.14,0.50,2.50);
      const tTop=((i+1-shift)%nBlades)/nBlades;
      const pTop=V3.add(V3.lerp(mainTail,mainPivot,tTop),topOff);
      addBox(mBladeTris,pTop[0],pTop[1],zBoom,0.12,0.45,2.50);
    }

    // Hydraulic-Assisted Chain Take-Up (500 mm stroke) at Main Boom Tail
    addCylinder(mTakeupTris,mainTail,V3.lerp(mainTail,mainPivot,0.06),0.22,0.22,12);

    // Main Boom Dual Drive Group (2 x 110 kW VFD Motors + Couplings + 180:1 CW/CCW Hollow-Shaft Shrink-Disc Gearboxes)
    const mGboxTris=[],mMotTris=[];
    for(const side of [-1,1]){
      const zd=zBoom+side*1.85;
      addBox(mGboxTris,mainPivot[0],mainPivot[1],zd,1.45,1.15,0.95); // 180:1 Gearbox
      addCylinder(mMotTris,[mainPivot[0]+0.95,mainPivot[1],zd],[mainPivot[0]+2.15,mainPivot[1],zd],0.42,0.42,14); // 110 kW VFD motor
    }

    pushPart(map.mainBoom,'Main Scraper Boom Girder (37,145 mm C-C · 62.5 t · 1,250/1,375 TPH)','material',[0.54,0.65,0.56],mBoomTris,'37.145 m sprocket center distance · 62,495 kg · 12 mm Hardox 400 discharge chute',[0,1.5,-2.2]);
    pushPart(map.mainChain,'Main Boom Roller-Bush Chain (500 mm Pitch · 1,500 kN · 0.69 m/s)','mechanical',[0.34,0.44,0.40],mChainTris,'Dual-strand roller-bush chain · 500 mm pitch · 1,500 kN breaking strength · 0.69 m/s',[0,1.8,-2.8]);
    pushPart(map.mainBlades,'Main Scraper Blades (2,500 × 500 mm E350BR + Hardox 400 Lip · 1,000 mm Pitch)','material',[0.78,0.58,0.26],mBladeTris,'2,500 × 500 mm scraper flights spaced at 1,000 mm · 554 kg/m material load',[0,1.2,-3.2]);
    pushPart(map.mainTakeup,'Main Boom Hydraulic-Assisted Chain Take-Up (500 mm Stroke)','mechanical',[0.28,0.55,0.62],mTakeupTris,'Hydraulic-assisted take-up system at boom tail · 500 mm stroke',[0,1.8,-3.5]);
    pushPart(map.mainMotors,'Main Boom VFD Motors (2 × 110 kW · 1,500 rpm)','electrical',[0.36,0.58,0.51],mMotTris,'2 × 110 kW (1,500 rpm VFD) squirrel-cage motors driving main scraper chain',[3.2,2.2,-2.2]);
    pushPart(map.mainGearboxes,'Main Boom Bevel-Helical Gearboxes (2 × 180:1 CW/CCW Shrink-Disc)','mechanical',[0.56,0.46,0.72],mGboxTris,'2 × 180:1 bevel-helical hollow-shaft gearboxes with shrink discs (1 CW + 1 CCW)',[2.4,2.2,-2.2]);
  }

  // 5. Luffable Auxiliary Scraper Boom (14.800 m Sprocket Centres, 30,871 kg, 500–660 TPH)
  // Pivoted at Articulation Link near X_tenova = 18.70 m..19.70 m (X = -8.2 m), scraping outer pile toe into Main Boom
  const auxPivot=[-8.2,mainTail[1]+1.65,zBoom-1.65];
  const auxRad=(auxBoomDeg*Math.PI)/180;
  const auxTail=[
    auxPivot[0]-14.800*Math.cos(auxRad),
    auxPivot[1]+14.800*Math.sin(auxRad),
    zBoom-1.65
  ];
  {
    const aBoomTris=[],aChainTris=[],aBladeTris=[],aTakeupTris=[],aDriveTris=[];
    addTrussGirder(aBoomTris,auxTail,auxPivot,1.95,1.25,8,0.15,0.08,[0,1,0]);
    // Articulation Link Bar connecting Aux Boom Pivot to Main Boom (Tenova Wind Load Table Item 6: Link at X_tenova = 18.70 m)
    addOrientedBox(aBoomTris,[auxPivot[0],auxPivot[1],auxPivot[2]+0.65],[mainTail[0]+1.2,mainTail[1]+0.4,zBoom-0.65],0.32,0.38,[0,1,0]);
    // Ø1294 mm 10-Tooth Drive Sprocket & Tail Sprocket (14.800 m C-C)
    addCylinder(aChainTris,[auxPivot[0],auxPivot[1],auxPivot[2]-0.95],[auxPivot[0],auxPivot[1],auxPivot[2]+0.95],0.647,0.647,14);
    addCylinder(aChainTris,[auxTail[0],auxTail[1],auxTail[2]-0.95],[auxTail[0],auxTail[1],auxTail[2]+0.95],0.55,0.55,14);

    // 400 mm Pitch Chain (500 kN) & 1800 x 450 mm Blades (800 mm spacing, 0.62 m/s)
    const aVec=V3.sub(auxPivot,auxTail);
    const {up:aUp}=basisFromAxis(aVec,[0,1,0]);
    const topOff=V3.mul(aUp,0.48),botOff=V3.mul(aUp,-0.48);
    for(const zChain of [auxPivot[2]-0.85,auxPivot[2]+0.85]){
      addOrientedBox(aChainTris,[auxTail[0]+topOff[0],auxTail[1]+topOff[1],zChain],[auxPivot[0]+topOff[0],auxPivot[1]+topOff[1],zChain],0.10,0.12,aUp);
      addOrientedBox(aChainTris,[auxTail[0]+botOff[0],auxTail[1]+botOff[1],zChain],[auxPivot[0]+botOff[0],auxPivot[1]+botOff[1],zChain],0.10,0.12,aUp);
    }
    const nAuxBlades=11;
    const shift=((phase*0.62)%1.0);
    for(let i=0;i<nAuxBlades;i++){
      const tBot=(i+shift)/nAuxBlades;
      const pBot=V3.add(V3.lerp(auxTail,auxPivot,tBot),botOff);
      addBox(aBladeTris,pBot[0],pBot[1],auxPivot[2],0.12,0.45,1.80);
      const tTop=((i+1-shift)%nAuxBlades)/nAuxBlades;
      const pTop=V3.add(V3.lerp(auxTail,auxPivot,tTop),topOff);
      addBox(aBladeTris,pTop[0],pTop[1],auxPivot[2],0.10,0.40,1.80);
    }
    addCylinder(aTakeupTris,auxTail,V3.lerp(auxTail,auxPivot,0.09),0.18,0.18,10);
    for(const side of [-1,1]){
      const zd=auxPivot[2]+side*1.35;
      addBox(aDriveTris,auxPivot[0],auxPivot[1],zd,1.15,0.92,0.78);
      addCylinder(aDriveTris,[auxPivot[0]+0.75,auxPivot[1],zd],[auxPivot[0]+1.65,auxPivot[1],zd],0.32,0.32,12);
    }

    pushPart(map.auxBoom,'Auxiliary Scraper Boom (14,800 mm C-C · 30.9 t · 500–660 TPH)','material',[0.58,0.68,0.55],aBoomTris,'14.800 m sprocket centers · 30,871 kg · Ø1,294 mm 10-tooth 42CrMo4V drive sprocket',[-2.0,1.5,-2.5]);
    pushPart(map.auxChain,'Auxiliary Boom Chain (400 mm Pitch · 500 kN · 0.62 m/s)','mechanical',[0.36,0.46,0.42],aChainTris,'Roller-bush chain · 400 mm pitch · 500 kN breaking strength · 0.62 m/s',[-2.0,1.8,-3.0]);
    pushPart(map.auxBlades,'Auxiliary Scraper Blades (1,800 × 450 mm · 800 mm Spacing)','material',[0.80,0.62,0.30],aBladeTris,'1,800 × 450 mm blades spaced at 800 mm transferring outer pile coal to Main Boom',[-2.0,1.2,-3.4]);
    pushPart(map.auxTakeup,'Auxiliary Boom Hydraulic Take-Up (400 mm Stroke)','mechanical',[0.28,0.55,0.62],aTakeupTris,'Hydraulic-assisted take-up at auxiliary boom tail · 400 mm stroke',[-2.0,1.8,-3.8]);
    pushPart(map.auxDrive,'Auxiliary Boom Drive Group (2 × 30 kW VFD + 160:1 Gearboxes)','mechanical',[0.58,0.48,0.74],aDriveTris,'2 × 30 kW (1500 rpm VFD) motors + flexible couplings + 160:1 bevel-helical gearboxes',[-2.0,2.2,-2.5]);
  }

  // 6. Boom Hoist Winch System (Exact Tenova Wind Load Coordinates: Winch Drum on Fixed-Side Leg @ X_tenova = 48.80 m [X = +20.90 m], EL +12.30 m; Crown Sheave Support @ X_tenova = 35.80 m [X = +7.90 m], EL +22.80 m)
  {
    const winchTris=[],ropeTris=[],hoistDriveTris=[];
    // Helper to get Portal Arch elevation at any X_scene along the sloped legs or central crown
    const archElevAtX=(x)=>{
      if(x<-16.20) return 3.71+(12.90-3.71)*((x-(-27.90))/(-16.20-(-27.90)));
      if(x<-4.50)  return 12.90+(21.80-12.90)*((x-(-16.20))/(-4.50-(-16.20)));
      if(x<=6.50)  return 21.80;
      if(x<=17.50) return 21.80+(14.80-21.80)*((x-6.50)/(17.50-6.50));
      return 14.80+(7.464-14.80)*((x-17.50)/(27.10-17.50));
    };

    // Ø1300 mm Hoist Winch Drum & 45 kW VFD Drive Deck on Fixed-Side Sloped Leg Platform (X = +20.90 m [X_tenova = 48.80 m], EL +12.30 m, Z = zBoom + 5.00 m)
    const zWinch=zBoom+5.0;
    addBox(winchTris,20.90,11.65,zWinch,2.8,0.35,3.2); // Winch platform deck on Fixed Leg
    addCylinder(winchTris,[20.40,12.30,zWinch-1.05],[20.40,12.30,zWinch+1.05],0.65,0.65,18); // Ø1,300 mm grooved winch drum
    addBox(hoistDriveTris,21.65,12.30,zWinch-0.35,1.45,1.15,1.35); // 35.5:1 Gearbox + 5.294:1 gear
    addCylinder(hoistDriveTris,[21.65,12.30,zWinch+0.45],[21.65,12.30,zWinch+1.55],0.36,0.36,14); // 45 kW VFD Motor
    addCylinder(hoistDriveTris,[22.15,12.95,zWinch+0.25],[22.15,13.35,zWinch+0.25],0.22,0.22,12); // Dual 292 Nm Thruster Brakes (Ø315 mm drum)

    // Crown Deflection Sheave Bank at Portal Apex (X_tenova = 35.80 m -> X = +7.90 m, EL +22.80 m)
    const apexSheave=[7.90,22.80,zPortal];
    addCylinder(winchTris,[apexSheave[0],apexSheave[1],zPortal-0.55],[apexSheave[0],apexSheave[1],zPortal+0.55],0.45,0.45,16);
    // Main hoist wire ropes ascending from Fixed-Leg Winch Drum (20.40, 12.30) along the Fixed Sloped Leg up to the EL +22.80 m Crown Sheave Support (7.90, 22.80)
    addCylinder(ropeTris,[20.40,12.85,zWinch-0.45],[apexSheave[0],apexSheave[1]+0.35,zPortal-0.35],0.048,0.048,8);
    addCylinder(ropeTris,[20.40,12.85,zWinch+0.45],[apexSheave[0],apexSheave[1]+0.35,zPortal+0.35],0.048,0.048,8);

    // Ø800 mm Boom Suspension Sheaves & Outrigger Brackets mounted along the Sloped Leg / Crown Arch
    const mAttach1=V3.lerp(mainTail,mainPivot,0.16);
    const mAttach2=V3.lerp(mainTail,mainPivot,0.56);
    const aAttach=V3.lerp(auxTail,auxPivot,0.28);
    const sheavePts=[
      {s:[mAttach1[0],archElevAtX(mAttach1[0])+0.35,zBoom],b:[mAttach1[0],mAttach1[1]+0.75,zBoom]},
      {s:[mAttach2[0],archElevAtX(mAttach2[0])+0.35,zBoom],b:[mAttach2[0],mAttach2[1]+0.75,zBoom]},
      {s:[aAttach[0],archElevAtX(aAttach[0])+0.35,zBoom-1.65],b:[aAttach[0],aAttach[1]+0.60,zBoom-1.65]}
    ];
    for(const sp of sheavePts){
      // Outrigger cantilever bracket from Portal Arch (zPortal) to Boom Sheave plane (sp.s[2])
      addOrientedBox(winchTris,[sp.s[0],sp.s[1]+0.15,zPortal],[sp.s[0],sp.s[1]+0.15,sp.s[2]-0.35],0.38,0.48,[0,1,0]);
      addOrientedBox(winchTris,[sp.s[0],sp.s[1]-0.95,zPortal],[sp.s[0],sp.s[1]+0.05,sp.s[2]],0.26,0.26,[0,1,0]);
      // Ø800 mm suspension sheave
      addCylinder(winchTris,[sp.s[0],sp.s[1],sp.s[2]-0.22],[sp.s[0],sp.s[1],sp.s[2]+0.22],0.40,0.40,14);
      // Twin Ø28 mm vertical/inclined hoist wire ropes down to Main & Aux Booms
      addCylinder(ropeTris,[sp.s[0]-0.18,sp.s[1],sp.s[2]],[sp.b[0]-0.18,sp.b[1],sp.b[2]],0.045,0.045,8);
      addCylinder(ropeTris,[sp.s[0]+0.18,sp.s[1],sp.s[2]],[sp.b[0]+0.18,sp.b[1],sp.b[2]],0.045,0.045,8);
      // Wire rope distribution along the sloped arch from Crown Sheave Support (7.90, 22.80) to each boom sheave
      addCylinder(ropeTris,[sp.s[0],sp.s[1]+0.35,zPortal],[apexSheave[0],apexSheave[1]+0.25,zPortal],0.042,0.042,8);
    }

    pushPart(map.hoistWinch,'Boom Hoist Winch Drum (Ø1,300 mm @ EL +12.3 m), Crown Sheaves (EL +22.8 m) & Ø28 mm Ropes','mechanical',[0.30,0.55,0.64],winchTris.concat(ropeTris),'Ø1,300 mm winch drum on Fixed Leg (X=48.8 m, EL +12.3 m) · Crown sheave support @ X=35.8 m, EL +22.8 m · Ø28 mm wire rope',[0,3.8,0]);
    pushPart(map.hoistSys,'Boom Hoist 45 kW VFD Drive, 35.5:1 Gearbox & Dual 292 Nm Thruster Brakes','mechanical',[0.56,0.46,0.72],hoistDriveTris,'45 kW VFD motor + Ø315 mm brake coupling + 2 × 292 Nm thruster brakes + 35.5:1 gearbox on Fixed Leg winch platform',[1.5,4.2,1.5]);
  }

  // 7. Fixed-Side E-House (EL +10.475 m), Cable Reels (7.5 kW Power & 3.7 kW Control), Dual Lubrication & Onboard DSS (2,000 L Tank @ EL +10.05 m)
  // Exact Coordinates from Tenova Wind Load Calcs (47039272 p.5 & p.9) & Storm Anchor Drawing 175135-ISG-0 (Elevation A-Side):
  // - E-House: X_tenova = 54.500 m (X = +26.60 m), Y = +0.500 m, EL +10.475 m (40.0 m² side area)
  // - Onboard DSS Water Tank (2,000 L): X_tenova = 55.800 m (X = +27.90 m), Y = -9.960 m, EL +10.050 m
  // - Power Cable Reel Drum: X = +27.90 m, Y = +8.726 m, EL +4.50 m
  {
    const pReelTris=[],cReelTris=[],greaseTris=[],oilTris=[],dssTris=[];
    // Pressurized Electrical House (E-House) & Operator Cabin at Fixed-Side Portal Deck (X = +26.60 m, EL +10.475 m)
    addBox(pReelTris,26.60,10.475,zBoom+0.50,3.8,3.2,8.4);
    // Power Cable Reel (7.5 kW mono-spiral at Z = zBoom + 8.726 m, EL +4.50 m per Tenova Wind Load Table) & Control Cable Reel
    addCylinder(pReelTris,[xA+1.15,4.50,zBoom+8.726],[xA+1.65,4.50,zBoom+8.726],1.65,1.65,22);
    addCylinder(cReelTris,[xA+1.15,4.50,zBoom-7.50],[xA+1.65,4.50,zBoom-7.50],1.40,1.40,22);
    // Central Grease Lubrication (Lincoln ZPU 14G-50XB, 50 L) & Chain Oil Lubrication (MFE5-BW30, 30 L, 16 nozzles)
    addBox(greaseTris,xA-1.2,7.8,zBoom+5.6,1.1,1.3,1.1);
    addBox(oilTris,xA-1.2,7.8,zBoom-4.6,1.0,1.1,1.0);
    // Onboard Plain-Water DSS (2,000 L SS Tank at X_tenova = 55.800 m [X = +27.90 m], Y = -9.960 m, EL +10.050 m + PRP-1A Pump + 6 Nozzles at EBA receipt)
    addCylinder(dssTris,[xA,9.15,zBoom-9.96],[xA,10.95,zBoom-9.96],0.80,0.80,16);
    addBox(dssTris,xConv-0.2,2.6,zBoom,0.8,0.6,2.8); // AP-1 6-nozzle spray bar over EBA conveyor receipt

    pushPart(map.powerReel,'Fixed-Side E-House (EL +10.475 m) & Mono-Spiral Power Cable Reel (7.5 kW)','electrical',[0.68,0.56,0.28],pReelTris,'E-House @ X=54.5 m, EL +10.475 m (40 m²) + 7.5 kW mono-spiral power cable reel @ Y=+8.726 m',[3.0,0,2.5]);
    pushPart(map.controlReel,'Mono-Spiral Control Cable Reel (3.7 kW Drive)','control',[0.74,0.62,0.32],cReelTris,'1 × mono-spiral electromechanical control cable reel (3.7 kW)',[3.0,0,-2.5]);
    pushPart(map.greaseLube,'Lincoln Central Grease Lubrication (ZPU 14G-50XB · 50 L · 400 bar)','utility',[0.76,0.64,0.32],greaseTris,'Lincoln ZPU 14G-50XB pump (14 L/h, 50 L reservoir) + DU1 GK changeover + VSG/SSV distributors',[2.2,1.2,2.0]);
    pushPart(map.chainOilLube,'Chain Oil Projection Lubrication (MFE5-BW30 · 30 L · 16 AC-A Nozzles)','utility',[0.72,0.58,0.26],oilTris,'MFE5-BW30 pump (0.5 L/min, 30 L tank) + Model 350 distributor + 16 × AC-A projection nozzles',[2.2,1.2,-2.0]);
    pushPart(map.dss,'Onboard Plain-Water DSS (2,000 L SS Tank @ EL +10.05 m + PRP-1A Pump + 6 Nozzles)','utility',[0.32,0.64,0.72],dssTris,'2,000 L SS tank @ X=55.8 m, Y=-9.96 m, EL +10.05 m + PRP-1A pump (1.0 m³/h @ 45 mWC) + 6 nozzles @ EBA',[2.8,1.5,-3.0]);
  }

  // 8. 3D Coal Stockpile with Active Reclaiming Bench Cut (52.0 m Width x 16.0 m Peak Height spanned by the 55.8 m Portal Arch)
  {
    const pileTris=[];
    // Unreclaimed 16.0 m high stockpile directly behind the active scraper booms (z = -48 m to zBoom - 2.8 m)
    addStockpilePrism(pileTris,-26.0,26.0,-48,zBoom-2.8,16.0,0.0,12);
    pushPart(map.stockpile,'Coal Stockpile EAE (52.0 m Width × 16.0 m Height · 37° Repose · Active Reclaim Bench)','material',[0.24,0.31,0.32],pileTris,'52.0 m base width × 16.0 m height (37° angle of repose) closely cleared by the ~38.5° sloped portal legs',[0,-2.5,0],true);
  }

  // Engineering Dimension Callout Anchors in 3D World Space
  const dimLines=[
    {a:[xB,0.25,zBoom+13],b:[xA,0.25,zBoom+13],label:'Portal Rail Span: 55,800 mm (Rail B X=0 → Rail A X=55.8 m)'},
    {a:[xB,3.71,zBoom+2.555],b:[-4.50,21.80,zPortal],label:'Sloped Pendulum Leg: 23.4 m Horiz Run (~38.5° · Pin EL +3.71 m)'},
    {a:[-4.50,22.20,zPortal],b:[6.50,22.20,zPortal],label:'Compact Crown Beam: 11.0 m (~19.7% of Span · Sheave EL +22.8 m)'},
    {a:[27.10,7.464,zPortal],b:[6.50,21.80,zPortal],label:'Sloped Fixed Leg: 21.4 m Horiz Run (Winch @ EL +12.3 m)'},
    {a:[xA,0.5,zBoom-7.0],b:[xA,0.5,zBoom+8.0],label:'Fixed Bogie Span (A1–A2): 15,000 mm (14 Wheels)'},
    {a:[xB,0.5,zBoom+2.555-3.5],b:[xB,0.5,zBoom+2.555+3.5],label:'Pendulum Bogies (B1–B2): 7,000 mm (8 Wheels)'},
    {a:mainTail,b:mainPivot,label:`Main Scraper Boom: 37,145 mm C-C (${mainBoomDeg}° · 500 mm Pitch)`},
    {a:auxTail,b:auxPivot,label:`Aux Scraper Boom: 14,800 mm C-C (${auxBoomDeg}° · 400 mm Pitch)`}
  ];

  return {
    items,
    dimLines,
    telemetry:[
      {label:'Portal Rail Span',value:'55,800 mm (UIC60 · 417 t Mass)'},
      {label:'Reclaim Belt Axis',value:'X = 58,000 mm (8.0 m Impact Table)'},
      {label:'Main Boom (37.145 m)',value:`${mainBoomDeg.toFixed(1)}° (500 mm Chain · 2500×500 Blades)`},
      {label:'Aux Boom (14.800 m)',value:`${auxBoomDeg.toFixed(1)}° (400 mm Chain · 1800×450 Blades)`},
      {label:'Travel Bogies',value:'22 × Ø630 mm (A1:6, A2:8, B1:4, B2:4)'},
      {label:'Portal Arch / Winch',value:'11.0 m Crown (EL +22.8m) · Winch @ EL +12.3m'}
    ]
  };
}

// --- WebGL 3D Viewport Renderer & Interactive Controller (Lazy-Initialized) ---

class YardKinematicViewer{
  constructor(canvas,onSelect,onHover,onFrame){
    this.canvas=canvas;
    this.onSelect=onSelect;
    this.onHover=onHover;
    this.onFrame=onFrame;
    this.items=[];
    this.dimLines=[];
    this.yaw=0.68;
    this.pitch=0.38;
    this.target=[0,6.5,0];
    this.distance=68;
    this.selected='';
    this.hoveredPart=null;
    this.activeLayer='all';
    this.gl=canvas.getContext('webgl',{antialias:true,alpha:false});
    if(!this.gl)throw new Error('WebGL hardware acceleration is unavailable.');
    this.buffers=[];
    this.initGL();
    this.bindEvents();
    this.resizeObserver=new ResizeObserver(()=>this.draw());
    this.resizeObserver.observe(canvas);
  }
  initGL(){
    const gl=this.gl;
    const compile=(type,src)=>{
      const s=gl.createShader(type);
      gl.shaderSource(s,src);
      gl.compileShader(s);
      if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s)||'Shader error');
      return s;
    };
    const vs=compile(gl.VERTEX_SHADER,`
      attribute vec3 position;
      attribute vec3 normal;
      uniform vec3 eye;
      uniform vec3 right;
      uniform vec3 up;
      uniform vec3 forward;
      uniform float aspect;
      uniform float nearClip;
      uniform float farClip;
      varying float vShade;
      varying float vSpec;
      void main(){
        vec3 d=position-eye;
        float z=dot(d,forward);
        float f=1.7320508;
        gl_Position=vec4(
          dot(d,right)*f/aspect,
          dot(d,up)*f,
          z*(farClip+nearClip)/(farClip-nearClip)-2.0*farClip*nearClip/(farClip-nearClip),
          z
        );
        vec3 n=normalize(normal+vec3(0.00001));
        vec3 viewDir=normalize(-d+vec3(0.00001));
        vec3 sun1=normalize(vec3(0.55,0.88,0.42));
        vec3 sun2=normalize(vec3(-0.55,0.38,-0.62));
        float diff1=abs(dot(n,sun1));
        float diff2=max(0.0,dot(n,sun2));
        float hemi=0.5+0.5*n.y;
        vec3 hVec=normalize(sun1+viewDir);
        vSpec=pow(max(0.0,abs(dot(n,hVec))),20.0)*0.14;
        vShade=0.38+0.48*diff1+0.16*diff2+0.10*hemi;
      }
    `);
    const fs=compile(gl.FRAGMENT_SHADER,`
      precision mediump float;
      uniform vec3 color;
      uniform float unlit;
      uniform float alpha;
      varying float vShade;
      varying float vSpec;
      void main(){
        if(unlit>0.5){
          gl_FragColor=vec4(color,alpha);
          return;
        }
        vec3 lit=color*vShade+vec3(vSpec);
        gl_FragColor=vec4(clamp(lit,0.0,1.0),alpha);
      }
    `);
    const p=gl.createProgram();
    gl.attachShader(p,vs);
    gl.attachShader(p,fs);
    gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS)){
      throw new Error(gl.getProgramInfoLog(p)||'WebGL shader link error');
    }
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    this.program=p;
    this.attrib={p:gl.getAttribLocation(p,'position'),n:gl.getAttribLocation(p,'normal')};
    this.uni={};
    for(const k of ['eye','right','up','forward','aspect','nearClip','farClip','color','unlit','alpha']){
      this.uni[k]=gl.getUniformLocation(p,k);
    }
    gl.enable(gl.DEPTH_TEST);
    gl.disable(gl.CULL_FACE);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  }
  createBuffer(vertices,lines=false){
    const gl=this.gl,out=[];
    if(lines){
      for(let i=0;i<vertices.length;i++)out.push(...vertices[i],0,1,0);
    }else{
      for(let i=0;i<vertices.length;i+=3){
        const n=V3.norm(V3.cross(V3.sub(vertices[i+1],vertices[i]),V3.sub(vertices[i+2],vertices[i])));
        out.push(...vertices[i],...n,...vertices[i+1],...n,...vertices[i+2],...n);
      }
    }
    const b=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,b);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(out),gl.STATIC_DRAW);
    this.buffers.push(b);
    return {buffer:b,count:vertices.length,lines};
  }
  updateScene(sceneData,resetCamera=false){
    const gl=this.gl;
    for(const b of this.buffers)gl.deleteBuffer(b);
    this.buffers=[];
    this.items=sceneData.items||[];
    this.dimLines=sceneData.dimLines||[];
    for(const item of this.items){
      item.gpu=this.createBuffer(item.vertices,false);
      const edgeVerts=[];
      const v=item.vertices;
      // Extract clean perimeter edges of each quad (2 triangles = 6 vertices: 0-1, 1-2, 3-4, 4-5)
      for(let i=0;i+5<v.length;i+=6){
        edgeVerts.push(v[i],v[i+1],v[i+1],v[i+2],v[i+3],v[i+4],v[i+4],v[i+5]);
      }
      item.edgeGpu=edgeVerts.length?this.createBuffer(edgeVerts,true):null;
    }
    // Build metric engineering ground grid (every 5.0 m)
    const gridVerts=[];
    const range=65,step=5;
    for(let d=-range;d<=range;d+=step){
      gridVerts.push([-range,-0.02,d],[range,-0.02,d],[d,-0.02,-range],[d,-0.02,range]);
    }
    this.gridGpu=this.createBuffer(gridVerts,true);
    // Build 3D dimension callout lines buffer
    const dimVerts=[];
    for(const dl of this.dimLines){
      dimVerts.push(dl.a,dl.b);
    }
    this.dimGpu=dimVerts.length?this.createBuffer(dimVerts,true):null;

    if(resetCamera){
      this.fitView();
    }else{
      this.draw();
    }
  }
  fitView(focusItem=null){
    const coreItems=this.items.filter(i=>!i.isContext);
    const list=focusItem?[focusItem]:(coreItems.length?coreItems:this.items);
    if(!list.length)return;
    let lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
    for(const it of list){
      for(let k=0;k<3;k++){
        lo[k]=Math.min(lo[k],it.bbox.lo[k]);
        hi[k]=Math.max(hi[k],it.bbox.hi[k]);
      }
    }
    this.target=[(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2];
    const radius=Math.max(4,Math.hypot(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2])/2);
    this.distance=radius*1.18;
    this.draw();
  }
  camera(){
    const offset=[
      Math.cos(this.pitch)*Math.sin(this.yaw),
      Math.sin(this.pitch),
      Math.cos(this.pitch)*Math.cos(this.yaw)
    ];
    const eye=V3.add(this.target,V3.mul(offset,this.distance));
    const forward=V3.norm(V3.sub(this.target,eye));
    const right=V3.norm(V3.cross(forward,[0,1,0]));
    const up=V3.norm(V3.cross(right,forward));
    return {eye,forward,right,up};
  }
  project(pt){
    const c=this.camera(),d=V3.sub(pt,c.eye),z=V3.dot(d,c.forward);
    if(z<=0.1)return null;
    const w=this.canvas.clientWidth||this.canvas.parentElement?.clientWidth||960,h=this.canvas.clientHeight||this.canvas.parentElement?.clientHeight||620;
    return {
      x:w/2+(V3.dot(d,c.right)*1.7320508*h)/(2*z),
      y:h/2-(V3.dot(d,c.up)*1.7320508*h)/(2*z),
      z
    };
  }
  draw(){
    if(this.disposed)return;
    const gl=this.gl,c=this.canvas;
    const dpr=Math.min(window.devicePixelRatio||1,2);
    const cw=c.clientWidth||c.parentElement?.clientWidth||960;
    const ch=c.clientHeight||c.parentElement?.clientHeight||620;
    const width=Math.max(1,Math.round(cw*dpr));
    const height=Math.max(1,Math.round(ch*dpr));
    if(c.width!==width||c.height!==height){c.width=width;c.height=height;}
    gl.viewport(0,0,width,height);
    gl.clearColor(0.945,0.962,0.948,1.0);
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(this.program);
    const cam=this.camera();
    for(const k of ['eye','right','up','forward'])gl.uniform3fv(this.uni[k],cam[k]);
    gl.uniform1f(this.uni.aspect,width/height);
    gl.uniform1f(this.uni.nearClip,Math.max(0.2,this.distance/500));
    gl.uniform1f(this.uni.farClip,Math.max(500,this.distance*8));

    const drawBuf=(gpu,color,unlit=0,alpha=1.0)=>{
      if(!gpu)return;
      gl.bindBuffer(gl.ARRAY_BUFFER,gpu.buffer);
      gl.enableVertexAttribArray(this.attrib.p);
      gl.enableVertexAttribArray(this.attrib.n);
      gl.vertexAttribPointer(this.attrib.p,3,gl.FLOAT,false,24,0);
      gl.vertexAttribPointer(this.attrib.n,3,gl.FLOAT,false,24,12);
      gl.uniform3fv(this.uni.color,color);
      gl.uniform1f(this.uni.unlit,unlit);
      gl.uniform1f(this.uni.alpha,alpha);
      gl.drawArrays(gpu.lines?gl.LINES:gl.TRIANGLES,0,gpu.count);
    };

    drawBuf(this.gridGpu,[0.79,0.84,0.81],1,0.75);
    if(this.showDims&&this.dimGpu){
      drawBuf(this.dimGpu,[0.20,0.45,0.38],1,0.9);
    }

    gl.enable(gl.POLYGON_OFFSET_FILL);
    gl.polygonOffset(1.0,1.0);
    for(const item of this.items){
      const isSel=this.selected&&item.entity_id===this.selected;
      const isHov=this.hoveredPart===item;
      const layerMatch=this.activeLayer==='all'||item.network===this.activeLayer;
      let col=item.color;
      let alpha=1.0;
      if(isSel)col=[0.94,0.54,0.12];
      else if(isHov)col=[0.88,0.68,0.22];
      else if(!layerMatch){
        col=[0.76,0.80,0.78];
        alpha=0.28;
      }
      drawBuf(item.gpu,col,0,alpha);
    }
    gl.disable(gl.POLYGON_OFFSET_FILL);
    for(const item of this.items){
      if(!item.edgeGpu)continue;
      const isSel=this.selected&&item.entity_id===this.selected;
      const isHov=this.hoveredPart===item;
      const layerMatch=this.activeLayer==='all'||item.network===this.activeLayer;
      if(!layerMatch&&!isSel&&!isHov)continue;
      const edgeCol=isSel?[0.55,0.25,0.02]:isHov?[0.48,0.34,0.05]:item.color.map(c=>Math.max(0.08,c*0.52));
      drawBuf(item.edgeGpu,edgeCol,1,isSel||isHov?0.95:0.42);
    }

    if(this.onFrame){
      this.onFrame({
        parts:this.items.map(i=>({
          entity_id:i.entity_id,
          label:i.label,
          spec:i.spec,
          network:i.network,
          screen:this.project(i.centre)
        })),
        dims:this.dimLines.map(d=>({
          label:d.label,
          a:this.project(d.a),
          b:this.project(d.b),
          mid:this.project(V3.lerp(d.a,d.b,0.5))
        }))
      });
    }
  }
  raycast(x,y){
    const w=this.canvas.clientWidth||1,h=this.canvas.clientHeight||1,c=this.camera();
    const dir=V3.norm(V3.add(
      c.forward,
      V3.add(
        V3.mul(c.right,(2*x-w)/(h*1.7320508)),
        V3.mul(c.up,(h-2*y)/(h*1.7320508))
      )
    ));
    let best=Infinity,hit=null;
    for(const item of this.items){
      const verts=item.vertices;
      for(let i=0;i<verts.length;i+=3){
        const t=rayTriangle(c.eye,dir,verts[i],verts[i+1],verts[i+2]);
        if(t!==null&&t<best){best=t;hit=item;}
      }
    }
    return hit;
  }
  bindEvents(){
    const c=this.canvas;
    this.abort=new AbortController();
    const opts={signal:this.abort.signal};
    let drag=null;
    c.addEventListener('pointerdown',e=>{
      c.setPointerCapture(e.pointerId);
      drag={x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,pan:e.button===2||e.shiftKey};
    },opts);
    c.addEventListener('pointermove',e=>{
      const r=c.getBoundingClientRect();
      if(!drag){
        const hit=this.raycast(e.clientX-r.left,e.clientY-r.top);
        if(hit!==this.hoveredPart){
          this.hoveredPart=hit;
          this.draw();
          if(this.onHover)this.onHover(hit,e.clientX-r.left,e.clientY-r.top);
        }
        return;
      }
      const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
      if(drag.pan){
        const cam=this.camera(),scale=this.distance/Math.max(200,c.clientHeight);
        this.target=V3.add(this.target,V3.add(V3.mul(cam.right,-dx*scale),V3.mul(cam.up,dy*scale)));
      }else{
        this.yaw-=dx*0.0075;
        this.pitch=Math.max(-1.35,Math.min(1.42,this.pitch+dy*0.0075));
      }
      drag.x=e.clientX;drag.y=e.clientY;
      this.draw();
    },opts);
    c.addEventListener('pointerup',e=>{
      if(drag&&Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)<5){
        const r=c.getBoundingClientRect();
        const hit=this.raycast(e.clientX-r.left,e.clientY-r.top);
        if(hit){
          this.selected=hit.entity_id;
          this.draw();
          if(this.onSelect)this.onSelect(hit);
        }
      }
      drag=null;
    },opts);
    c.addEventListener('pointerleave',()=>{
      if(this.hoveredPart){
        this.hoveredPart=null;
        this.draw();
        if(this.onHover)this.onHover(null,0,0);
      }
    },opts);
    c.addEventListener('contextmenu',e=>e.preventDefault(),opts);
    c.addEventListener('wheel',e=>{
      e.preventDefault();
      this.distance=Math.max(4,Math.min(260,this.distance*Math.exp(e.deltaY*0.0011)));
      this.draw();
    },{...opts,passive:false});
  }
  dispose(){
    if(this.disposed)return;
    this.disposed=true;
    this.abort.abort();
    this.resizeObserver.disconnect();
    for(const b of this.buffers)this.gl.deleteBuffer(b);
    this.buffers=[];
    if(this.program)this.gl.deleteProgram(this.program);
    this.gl.getExtension('WEBGL_lose_context')?.loseContext();
  }
}

// --- Public PlantYard3D Controller ---

let activeInstance=null;
const savedStateByEquip=new Map();

function getEquipState(scene){
  if(!savedStateByEquip.has(scene.id)){
    savedStateByEquip.set(scene.id,scene.kind==='stacker'?{
      slewDeg:48,
      luffDeg:8,
      travelM:0,
      phase:0,
      animating:false,
      exploded:false,
      showDims:false,
      showLabels:false,
      camera:null
    }:{
      mainBoomDeg:-14,
      auxBoomDeg:-16,
      travelM:0,
      phase:0,
      animating:false,
      exploded:false,
      showDims:false,
      showLabels:false,
      camera:null
    });
  }
  return savedStateByEquip.get(scene.id);
}

function renderStageMarkup(scene){
  const st=getEquipState(scene);
  const isStacker=scene.kind==='stacker';
  const slidersHtml=isStacker?`
    <label class="ps-3d-slider"><span>Slew (0–100°) <b id="ps-3d-slew-val">${st.slewDeg}°</b></span><input type="range" id="ps-3d-slew" min="0" max="100" step="1" value="${st.slewDeg}"></label>
    <label class="ps-3d-slider"><span>Luff (-8°..+14°) <b id="ps-3d-luff-val">${st.luffDeg>=0?'+'+st.luffDeg:st.luffDeg}°</b></span><input type="range" id="ps-3d-luff" min="-8" max="14" step="0.5" value="${st.luffDeg}"></label>
    <label class="ps-3d-slider"><span>Rail Travel <b id="ps-3d-travel-val">${st.travelM} m</b></span><input type="range" id="ps-3d-travel" min="-18" max="18" step="0.5" value="${st.travelM}"></label>
  `:`
    <label class="ps-3d-slider"><span>Main Boom <b id="ps-3d-main-val">${st.mainBoomDeg}°</b></span><input type="range" id="ps-3d-main" min="-28" max="10" step="0.5" value="${st.mainBoomDeg}"></label>
    <label class="ps-3d-slider"><span>Aux Boom <b id="ps-3d-aux-val">${st.auxBoomDeg}°</b></span><input type="range" id="ps-3d-aux" min="-26" max="12" step="0.5" value="${st.auxBoomDeg}"></label>
    <label class="ps-3d-slider"><span>Portal Travel <b id="ps-3d-travel-val">${st.travelM} m</b></span><input type="range" id="ps-3d-travel" min="-18" max="18" step="0.5" value="${st.travelM}"></label>
  `;

  return `
    <div class="ps-yard3d-shell" id="ps-yard3d-shell" data-equip="${esc(scene.id)}" data-kind="${esc(scene.kind)}">
      <div class="ps-3d-control-bar" role="region" aria-label="3D kinematic controls and camera presets">
        <div class="ps-3d-sliders">${slidersHtml}</div>
        <div class="ps-3d-toggles">
          <button type="button" class="ps-3d-btn ${st.animating?'is-active':''}" id="ps-3d-anim">${st.animating?'Ⅱ Pause Cycle':'▷ Animate Operation'}</button>
          <button type="button" class="ps-3d-btn ${st.showDims?'is-active':''}" id="ps-3d-dims">📏 Dimensions</button>
          <button type="button" class="ps-3d-btn ${st.showLabels?'is-active':''}" id="ps-3d-labels">🏷 Part Callouts</button>
          <button type="button" class="ps-3d-btn ${st.exploded?'is-active':''}" id="ps-3d-explode">⊞ Explode Subsystems</button>
        </div>
        <div class="ps-3d-cam-group" role="group" aria-label="Camera presets">
          <button type="button" class="ps-3d-cam-btn" data-cam="iso">3D Iso</button>
          <button type="button" class="ps-3d-cam-btn" data-cam="side">GA Side</button>
          <button type="button" class="ps-3d-cam-btn" data-cam="front">Rail Span</button>
          <button type="button" class="ps-3d-cam-btn" data-cam="top">Plan View</button>
          <button type="button" class="ps-3d-cam-btn" data-cam="fit">Fit All</button>
        </div>
      </div>
      <div class="ps-yard3d-stage" id="ps-yard3d-stage">
        <canvas id="ps-yard3d-canvas" tabindex="0" aria-label="${esc(scene.title)} 3D dimension-accurate kinematic model"></canvas>
        <div class="ps-yard3d-overlay" id="ps-yard3d-overlay" aria-hidden="true"></div>
        <div class="ps-yard3d-telemetry" id="ps-yard3d-telemetry" aria-label="Live GA engineering coordinates and dimensions"></div>
        <div class="ps-yard3d-tooltip" id="ps-yard3d-tooltip" hidden></div>
        <div class="ps-canvas-hint">Drag to orbit 3D · Shift+Drag (or Right-Drag) to pan · Wheel to zoom · Click any 3D subassembly to inspect its SQLite specs & drawings</div>
      </div>
    </div>
  `;
}

function unmount(){
  if(!activeInstance)return;
  if(activeInstance.rafId)cancelAnimationFrame(activeInstance.rafId);
  if(activeInstance.viewer&&activeInstance.state){
    activeInstance.state.camera={
      yaw:activeInstance.viewer.yaw,
      pitch:activeInstance.viewer.pitch,
      distance:activeInstance.viewer.distance,
      target:activeInstance.viewer.target.slice()
    };
  }
  activeInstance.viewer?.dispose();
  activeInstance=null;
}

function mount(scene,options={}){
  const canvas=document.getElementById('ps-yard3d-canvas');
  if(activeInstance&&activeInstance.equipId===scene.id&&activeInstance.viewer?.canvas===canvas&&!activeInstance.viewer.disposed){
    activeInstance.onSelect=options.onSelect;
    activeInstance.viewer.selected=options.selectedId||'';
    activeInstance.viewer.activeLayer=options.layer||'all';
    activeInstance.viewer.draw();
    return;
  }
  unmount();
  const overlay=document.getElementById('ps-yard3d-overlay');
  const telemetryEl=document.getElementById('ps-yard3d-telemetry');
  const tooltipEl=document.getElementById('ps-yard3d-tooltip');
  if(!canvas)return;

  const st=getEquipState(scene);
  const isStacker=scene.kind==='stacker';
  let viewer=null;

  const renderOverlay=frameData=>{
    if(!overlay)return;
    const html=[];
    const placedBoxes=[];
    if(st.showDims){
      const cw=canvas.clientWidth||960,ch=canvas.clientHeight||620;
      for(const d of frameData.dims){
        if(!d.mid)continue;
        let dx=Math.round(d.mid.x),dy=Math.round(d.mid.y);
        if(dx<60||dx>cw-60||dy<48||dy>ch-36)continue;
        // Nudge vertically if too close to an existing dimension tag
        for(let step=0;step<5;step++){
          if(!placedBoxes.some(b=>Math.abs(b.x-dx)<175&&Math.abs(b.y-dy)<26))break;
          dy+=(step%2===0?1:-1)*(step+1)*24;
        }
        if(dy<48||dy>ch-36)continue;
        placedBoxes.push({x:dx,y:dy});
        html.push(`<div class="ps-3d-dim-tag" style="left:${dx}px;top:${dy}px">${esc(d.label)}</div>`);
      }
    }
    if(st.showLabels){
      const seenIds=new Set();
      // Prioritize selected part first so it is always labeled
      const sortedParts=[...frameData.parts].sort((a,b)=>(viewer?.selected===b.entity_id?1:0)-(viewer?.selected===a.entity_id?1:0));
      for(const p of sortedParts){
        if(!p.screen||seenIds.has(p.entity_id))continue;
        const sx=Math.round(p.screen.x),sy=Math.round(p.screen.y);
        if(sx<55||sx>canvas.clientWidth-55||sy<35||sy>canvas.clientHeight-40)continue;
        const isSel=viewer?.selected===p.entity_id;
        if(!isSel&&placedBoxes.some(b=>Math.abs(b.x-sx)<118&&Math.abs(b.y-sy)<28))continue;
        seenIds.add(p.entity_id);
        placedBoxes.push({x:sx,y:sy});
        const shortName=p.label.split('(')[0].trim();
        html.push(`<button type="button" class="ps-3d-part-pin ${isSel?'is-selected':''}" style="left:${sx}px;top:${sy}px" data-entity="${esc(p.entity_id)}" title="${esc(p.spec)}">${esc(shortName)}</button>`);
      }
    }
    overlay.innerHTML=html.join('');
  };

  try{
    viewer=new YardKinematicViewer(
      canvas,
      hit=>{if(activeInstance?.onSelect)activeInstance.onSelect(hit.entity_id);else if(options.onSelect)options.onSelect(hit.entity_id);},
      (hit,x,y)=>{
        if(!tooltipEl)return;
        if(!hit){tooltipEl.hidden=true;return;}
        tooltipEl.hidden=false;
        tooltipEl.style.left=Math.min(canvas.clientWidth-260,x+14)+'px';
        tooltipEl.style.top=Math.max(12,y-18)+'px';
        tooltipEl.innerHTML=`<strong>${esc(hit.label)}</strong><span>${esc(hit.spec)}</span>`;
      },
      renderOverlay
    );
  }catch(err){
    if(overlay)overlay.innerHTML=`<div class="ps-3d-fallback">${esc(err.message)}</div>`;
    return;
  }

  const onSelCb=options.onSelect||options.onPick;
  options.onSelect=onSelCb;
  viewer.selected=options.selectedId||options.selected||'';
  viewer.activeLayer=options.layer||'all';
  viewer.showDims=st.showDims;

  const rebuild=(resetCam=false)=>{
    const data=isStacker?buildStackerScene3D(scene,st):buildReclaimerScene3D(scene,st);
    viewer.showDims=st.showDims;
    viewer.updateScene(data,resetCam);
    if(telemetryEl&&data.telemetry){
      telemetryEl.innerHTML=data.telemetry.map(t=>`<div class="ps-3d-stat"><span>${esc(t.label)}</span><strong>${esc(t.value)}</strong></div>`).join('');
    }
  };

  if(st.camera){
    viewer.yaw=st.camera.yaw;
    viewer.pitch=st.camera.pitch;
    viewer.distance=st.camera.distance;
    viewer.target=st.camera.target.slice();
    rebuild(false);
  }else{
    viewer.yaw=isStacker?0.52:0.42;
    viewer.pitch=isStacker?0.30:0.28;
    rebuild(true);
  }

  // Wire overlay pin clicks to select part
  overlay?.addEventListener('click',e=>{
    const pin=e.target.closest('.ps-3d-part-pin[data-entity]');
    const cb=activeInstance?.onSelect||options.onSelect;if(pin&&cb){
      viewer.selected=pin.dataset.entity;
      viewer.draw();
      cb(pin.dataset.entity);
    }
  });

  // Wire kinematic sliders
  const bindSlider=(id,valId,prop,suffix='°',plusSign=false)=>{
    const el=document.getElementById(id),valEl=document.getElementById(valId);
    if(!el)return;
    el.oninput=()=>{
      st[prop]=Number(el.value);
      if(valEl)valEl.textContent=(plusSign&&st[prop]>0?'+'+st[prop]:st[prop])+suffix;
      rebuild(false);
    };
  };
  if(isStacker){
    bindSlider('ps-3d-slew','ps-3d-slew-val','slewDeg','°',false);
    bindSlider('ps-3d-luff','ps-3d-luff-val','luffDeg','°',true);
    bindSlider('ps-3d-travel','ps-3d-travel-val','travelM',' m',false);
  }else{
    bindSlider('ps-3d-main','ps-3d-main-val','mainBoomDeg','°',false);
    bindSlider('ps-3d-aux','ps-3d-aux-val','auxBoomDeg','°',false);
    bindSlider('ps-3d-travel','ps-3d-travel-val','travelM',' m',false);
  }

  // Wire mode buttons
  const animBtn=document.getElementById('ps-3d-anim');
  const dimsBtn=document.getElementById('ps-3d-dims');
  const labelsBtn=document.getElementById('ps-3d-labels');
  const explodeBtn=document.getElementById('ps-3d-explode');

  const tick=()=>{
    if(!activeInstance||!st.animating)return;
    st.phase+=0.025;
    if(isStacker){
      st.slewDeg=Math.round((50+35*Math.sin(st.phase*0.35))*10)/10;
      const slewEl=document.getElementById('ps-3d-slew'),slewVal=document.getElementById('ps-3d-slew-val');
      if(slewEl)slewEl.value=String(st.slewDeg);
      if(slewVal)slewVal.textContent=`${st.slewDeg}°`;
    }
    rebuild(false);
    activeInstance.rafId=requestAnimationFrame(tick);
  };

  if(animBtn){
    animBtn.onclick=()=>{
      st.animating=!st.animating;
      animBtn.classList.toggle('is-active',st.animating);
      animBtn.textContent=st.animating?'Ⅱ Pause Cycle':'▷ Animate Operation';
      if(st.animating)activeInstance.rafId=requestAnimationFrame(tick);
      else if(activeInstance?.rafId)cancelAnimationFrame(activeInstance.rafId);
    };
  }
  if(dimsBtn){
    dimsBtn.onclick=()=>{
      st.showDims=!st.showDims;
      dimsBtn.classList.toggle('is-active',st.showDims);
      viewer.showDims=st.showDims;
      viewer.draw();
    };
  }
  if(labelsBtn){
    labelsBtn.onclick=()=>{
      st.showLabels=!st.showLabels;
      labelsBtn.classList.toggle('is-active',st.showLabels);
      viewer.draw();
    };
  }
  if(explodeBtn){
    explodeBtn.onclick=()=>{
      st.exploded=!st.exploded;
      explodeBtn.classList.toggle('is-active',st.exploded);
      rebuild(false);
    };
  }

  document.querySelectorAll('.ps-3d-cam-btn[data-cam]').forEach(btn=>{
    btn.onclick=()=>{
      const mode=btn.dataset.cam;
      if(mode==='iso'){viewer.yaw=isStacker?0.52:0.42;viewer.pitch=isStacker?0.30:0.28;viewer.fitView();}
      else if(mode==='side'){viewer.yaw=0;viewer.pitch=0.08;viewer.fitView();}
      else if(mode==='front'){viewer.yaw=Math.PI/2;viewer.pitch=0.12;viewer.fitView();}
      else if(mode==='top'){viewer.yaw=0;viewer.pitch=1.42;viewer.fitView();}
      else if(mode==='fit'){
        const selItem=viewer.items.find(i=>i.entity_id===viewer.selected);
        viewer.fitView(selItem||null);
      }
    };
  });

  activeInstance={equipId:scene.id,viewer,state:st,onSelect:options.onSelect,rafId:st.animating?requestAnimationFrame(tick):null};
  if(typeof requestAnimationFrame!=='undefined')requestAnimationFrame(()=>viewer?.draw());
}

root.PlantYard3D=globalThis.PlantYard3D={
  renderStageMarkup,
  shellHtml:renderStageMarkup,
  mount,
  mount3DHost:mount,
  unmount,
  destroy3DHost:unmount,
  buildStackerScene3D,
  buildReclaimerScene3D,
  isMounted:()=>!!activeInstance
};

if(typeof module!=='undefined'&&module.exports)module.exports=root.PlantYard3D;
})(typeof window==='undefined'?globalThis:window);
/* === END EMBEDDED PlantYard3D === */

/* Continuous, visual-first navigation over the accepted plant graph. */
'use strict';
const PlantScene=(()=>{
  const M=PlantSceneModel;
  let p,api,s,cleanup,viewport={x:0,y:0,w:1200,h:720},viewKey='',lastPick='',wheelZoomMode=true,activeFloorBounds=null;
  const q=()=>new URLSearchParams(location.hash.split('?')[1]||'');
  const h=()=>q().get('pick');
  const safe=x=>esc(x??'');
  const url=changes=>{const v=q();for(const[k,x]of Object.entries(changes)){if(x===null||x===undefined||x==='')v.delete(k);else v.set(k,x);}return '#overview'+(v.size?'?'+v:'');};
  const home='#overview';
  const areaURL=area=>'#overview?area='+encodeURIComponent(area);
  const openURL=id=>{let trail=(q().get('trail')||'').split(',').filter(x=>p.entities.has(x));if(trail.includes(id))trail=trail.slice(0,trail.indexOf(id));else if(s.id&&s.id!==id&&(p.assembly(s.id).some(n=>n.id===id)||s.nodes.some(n=>n.id===id&&n.role==='located'))){if(!trail.includes(s.id))trail.push(s.id);}else trail=[];return url({equipment:id,pick:null,edge:null,tab:null,view:null,trail:trail.slice(-12).join(','),browse:null,scene:null,layer:null,spread:null,opmode:null,floor:null,iso:null});};
  const pickURL=id=>url({pick:id,edge:null,browse:null});
  function sourceBadgeLabel(a){
    if(!a?.evidence?.length)return 'Source ↗';
    const idx=typeof state!=='undefined'&&(state.evidence_index||[]);
    const ev=idx&&idx.find(e=>e.id===a.evidence[0].evidence_id);
    if(ev?.page)return `p.${ev.page} ↗`;
    if(ev?.locator)return `${ev.locator.length>14?ev.locator.slice(0,12)+'…':ev.locator} ↗`;
    return 'Source ↗';
  }
  const source=(a,title)=>a?.evidence?.length?`<button class="ps-source-chip" data-action="fact-source" data-id="${safe(a.id)}" data-support="0" title="Inspect source document & evidence crop">${safe(title||sourceBadgeLabel(a))}</button>`:'';
  const nice=PlantExplorerModel.pretty;
  const text=(x,y,t,cls='ps-label',anchor='middle')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${safe(t)}</text>`;
  function lines(label,max=25){const words=label.split(/\s+/),out=[''];for(const w of words){if((out.at(-1)+' '+w).trim().length>max&&out.at(-1))out.push(w);else out[out.length-1]=(out.at(-1)+' '+w).trim();}return out;}
  function short(n){
    const root=s.id?p.entities.get(s.id)?.label:'';
    let out=n.label;
    if(root&&out.startsWith(root+' '))out=out.slice(root.length+1);
    else{
      const tag=root.match(/^[A-Z]{2,5}-\d+[AB]?\b/)?.[0];
      if(tag&&out.startsWith(tag+' '))out=out.slice(tag.length+1);
      else{
        const sysTag=root.match(/\(([A-Z]{2,5}-\d+)\)/)?.[1]||(/^UEF-13 Coal Sampling/i.test(root)?'EAU-2':/^UEF-3 Coal Sampling/i.test(root)?'EAU-1':/^Coal Ship Unloader-([123])/i.test(root)?'SUL-'+root.match(/([123])/)[1]:null);
        if(sysTag&&out.startsWith(sysTag+' '))out=out.slice(sysTag.length+1);
      }
    }
    if(['stacker','reclaimer','boom','slew','cylinder','hoist','bogie'].includes(s?.kind)){
      out=out.replace(/^(?:Boom conveyor Drive group|Boom conveyor|Main scraper boom Drive group|Main scraper boom|Main boom|Auxiliary scraper boom Drive group|Auxiliary scraper boom|Aux boom|Slew system|Luffing system|Hoist system|Travel system)\s+/i,'');
      if(!/^(?:Slew|Luffing|Hoist|Travel)\s+system$/i.test(out)){
        out=out.replace(/^(?:Slew|Luffing|Hoist|Travel)\s+/i,'');
      }
      out=out.replace(/^([a-z])/,m=>m.toUpperCase());
    }
    if(['conveyor','feeder','mechanical','drive','takeup','protection'].includes(s?.kind)){
      out=out.replace(/^(?:Belt and mechanical assemblies|Belt and mechanical assembly|Mechanical and structural assemblies|Mechanical and structural assembly|Belt protection and instrumentation devices|Belt protection devices|Protection and instrumentation|Drive assembly)\s+/i,'');
      out=out.replace(/^(?:Tail bend and take-up pulley group)\s+/i,'');
      out=out.replace(/^(?:Vertical gravity take-up|Horizontal gravity take-up|Take-up assembly)\s+/i,m=>/^(?:Counterweight|Rope|Wire rope|Sheave|Trolley)/i.test(out.slice(m.length))?'Take-up ':'');
      if(/^Idlers\s+/i.test(out)){
        const rest=out.replace(/^Idlers\s+/i,'');
        out=/idler|roller/i.test(rest)?rest:rest+' idlers';
      }
      out=out.replace(/\s+Level and temperature instruments\s+/i,' ');
      out=out.replace(/\s+Onboard(?: plain-water)? DSS\s+/i,' DSS ');
      out=out.replace(/\s+Suction duct and hoods\s+/i,' Hood ');
      out=out.replace(/\s+Drive assembly Scoop coupling\s+/i,' ');
    }
    if(/dust-suppression|onboard.*dss/i.test(root)){
      out=out.replace(/^(?:Onboard(?: plain-water)? DSS|DSS)\s+/i,'');
    }
    if(/spds/i.test(root)){
      out=out.replace(/^(?:Coal Yard \d+ SPDS|SPDS Common|SPDS|Stockpile Sequential Controller)\s+/i,'');
      out=out.replace(/^Sprinkler risers AP-\d+ to AP-\d+\s+/i,'');
    }
    if(/runoff|sump/i.test(root)){
      out=out.replace(/^(?:Coal Yard \d+ Runoff (?:collection|sump)|EAE-\d+ (?:Runoff|and UEF-\d+ runoff sump)|Stockpile \d+ and UEF-\d+ sump)\s+/i,'');
    }
    if(/hydraulic power pack/i.test(root)){
      out=out.replace(/^(?:Slew HPP|Luffing HPP|Slew system Hydraulic power pack|Luffing system Hydraulic power pack)\s+/i,'');
    }
    if(/fire detection/i.test(root)){
      out=out.replace(/^(?:Fire detection and clean-agent system|Fire detection)\s+/i,'');
      out=out.replace(/^(?:Z[12]01 Protected zone|Z[12]01)\s+/i,'');
    }
    if(/lubrication/i.test(root))out=out.replace(/^(?:Central grease lubrication|Chain oil lubrication|Lubrication)\s+/i,'');
    if(/belt weigher|eat-[1-4]/i.test(root)){
      out=out.replace(/^(?:EBA-\d+|EAD-\d+ Boom)\s+Belt weigher\s+/i,'');
      out=out.replace(/^(?:Four-idler weighbridge|Speed sensor60-12C|Calibration test-weight arrangement)\s+/i,'');
    }
    if(/travelling tripper|^tt-\d+|^ftr-\d+/i.test(root)){
      out=out.replace(/^(?:Tripper|pulley hood and discharge assembly)\s+/i,'');
    }
    if(/^EBC-\d+\s+/i.test(root)&&n.role==='connected'){
      out=out.replace(/^(?:Rotor bearings and seals|Drive assembly|Protection and monitoring|Hydraulic opening system)\s+/i,'');
    }
    return out;
  }
  function symbol(kind,x,y,w=180,height=120){return `<svg x="${x}" y="${y}" width="${w}" height="${height}" viewBox="0 0 180 120" aria-hidden="true"><use href="#ps-${kind}"/></svg>`;}
  function defs(){return `<defs>
    <symbol id="ps-mechanical-part" viewBox="0 0 180 120"><path d="M12 61H168" class="ps-shaft"/><path d="M65 32H115V92H65Z" class="ps-metal"/><ellipse cx="115" cy="62" rx="16" ry="30" class="ps-metal"/><circle cx="115" cy="62" r="9" class="ps-wheel"/><path d="M41 92V106H75M144 86V106H109" class="ps-floor"/></symbol>
    <symbol id="ps-marker" viewBox="0 0 180 120"><path d="M20 105V17H142V104M62 17V46M58 43H106L116 86Q83 115 49 86Z" class="ps-metal"/><path d="M66 38H101M51 86H115" class="ps-shaft"/></symbol>
    <pattern id="ps-grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#cbd7d4"/></pattern>
    <linearGradient id="ps-metal" x2="0" y2="1"><stop stop-color="#ecf3f0"/><stop offset="1" stop-color="#b5c9c4"/></linearGradient>
    <linearGradient id="ps-coal" x2="0" y2="1"><stop stop-color="#607272"/><stop offset="1" stop-color="#354b4c"/></linearGradient>
    <marker id="ps-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#ab7337"/></marker>
    <marker id="ps-water-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#4388a3"/></marker>
    <marker id="ps-drive-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#7e69a0"/></marker>
    <symbol id="ps-conveyor" viewBox="0 0 180 120"><path class="ps-metal" d="M19 88L19 102M63 76L63 103M111 60L111 103M157 49L157 102M13 103H168M19 88L63 102L63 76L111 103L111 61L157 102"/><path d="M22 80L150 39Q166 37 169 47Q172 57 158 62L30 102Q14 105 11 93Q8 84 22 80Z" fill="#8a9f99" stroke="#3d6460" stroke-width="2"/><path d="M23 84L153 43M29 97L160 57" class="ps-belt-line"/><circle cx="22" cy="91" r="7" class="ps-metal"/><circle cx="158" cy="50" r="7" class="ps-metal"/><path d="M50 77L55 89M79 68L84 79M107 59L112 70M135 50L140 61" stroke="#dce7df" stroke-width="3"/><path d="M38 78L54 66L65 70L74 60L91 61L108 48L121 52L139 38L150 41" fill="none" stroke="#364c49" stroke-width="5"/></symbol>
    <symbol id="ps-belt" viewBox="0 0 180 120"><path d="M30 51L130 25Q164 37 153 63L54 102Q20 93 30 51Z" fill="#5f8070" stroke="#3d6352" stroke-width="3"/><path d="M40 52L133 33Q151 43 143 58L51 94Q32 85 40 52Z" fill="#d7e1d2" stroke="#829e88" stroke-width="2"/><path d="M46 53L130 41M49 83L135 54" stroke="#344e3d" stroke-width="8"/></symbol>
    <symbol id="ps-idler" viewBox="0 0 180 120"><path d="M12 104H166M21 97V65M154 98V65" stroke="#799783" stroke-width="5"/><path d="M24 45L58 82M62 84H116M119 81L151 44" stroke="#628974" stroke-width="16"/><path d="M22 45L57 82M64 84H114M121 81L153 44" stroke="#b7cbbb" stroke-width="6"/></symbol>
    <symbol id="ps-scraper" viewBox="0 0 180 120"><path d="M28 36H153L127 74H48Z" fill="#c7b385" stroke="#96824e" stroke-width="3"/><path d="M40 64H137L126 83H48Z" fill="#6c8973" stroke="#54715d" stroke-width="2"/><path d="M20 88H163M37 75V105M145 74V105" stroke="#75947b" stroke-width="5"/></symbol>
    <symbol id="ps-takeup" viewBox="0 0 180 120"><path d="M36 109V15H142V109M38 15L141 109M141 15L39 109" fill="none" stroke="#8da88d" stroke-width="3"/><circle cx="90" cy="43" r="20" class="ps-metal"/><path d="M70 44V69H110V44M90 70V88" fill="none" stroke="#607d63" stroke-width="3"/><path d="M64 87H116V107H64Z" fill="#b8c6aa" stroke="#718469" stroke-width="2"/></symbol>
    <symbol id="ps-counterweight" viewBox="0 0 180 120"><path d="M44 14V108M136 14V108" stroke="#7a9380" stroke-width="4"/><path d="M68 14V44M112 14V44" stroke="#5a7262" stroke-width="3" stroke-dasharray="4 3"/><rect x="52" y="42" width="76" height="16" rx="2" fill="#9eb4a2" stroke="#4f6b58" stroke-width="2"/><rect x="52" y="61" width="76" height="16" rx="2" fill="#88a18d" stroke="#4f6b58" stroke-width="2"/><rect x="52" y="80" width="76" height="18" rx="2" fill="#738e79" stroke="#4f6b58" stroke-width="2"/><path d="M34 108H146" stroke="#5a7262" stroke-width="4"/></symbol>
    <symbol id="ps-shaft-coupling" viewBox="0 0 180 120"><path d="M8 66H173" stroke="#51715f" stroke-width="9"/><ellipse cx="65" cy="65" rx="18" ry="33" class="ps-metal"/><path d="M64 32H113V98H64Z" fill="#95b099" stroke="#56785f" stroke-width="2"/><ellipse cx="114" cy="65" rx="18" ry="33" fill="#c5d5bf" stroke="#56785f" stroke-width="2"/><path d="M77 35V95M101 35V95" stroke="#55755e" stroke-width="3"/><circle cx="118" cy="44" r="3" fill="#55755e"/><circle cx="118" cy="86" r="3" fill="#55755e"/></symbol>
    <symbol id="ps-pile" viewBox="0 0 180 120"><ellipse cx="92" cy="103" rx="80" ry="10" fill="#d8e1dc"/><path d="M10 100L48 56L77 35L106 48L132 70L171 100Z" fill="url(#ps-coal)" stroke="#354e4c" stroke-width="2"/><path d="M48 56L83 73L106 48M77 35L83 73L55 99M83 73L132 70L117 100" fill="none" stroke="#96aaa1" stroke-opacity=".5"/></symbol>
    <symbol id="ps-shed" viewBox="0 0 180 120"><path d="M13 103V50Q90 -10 168 50V103M13 50H168M37 38V103M62 26V103M90 21V103M118 27V103M145 38V103" fill="none" stroke="#8ba49b" stroke-width="3"/><path d="M13 50Q90 -10 168 50L149 62Q90 9 32 62Z" fill="#dfe9e2" fill-opacity=".7" stroke="#829c91"/></symbol>
    <symbol id="ps-stacker" viewBox="0 0 180 120"><path d="M15 104H171M26 111H166" stroke="#94aaa1" stroke-width="3"/><path d="M52 94V48H75V94M51 62L155 22L160 35L75 77Z" class="ps-metal"/><path d="M63 65L86 57L82 72L104 49L99 65L123 42L119 57L147 33" fill="none" stroke="#547b70" stroke-width="2"/><path d="M58 48V22L152 24M59 24L115 51M62 31L19 73" fill="none" stroke="#829b91" stroke-width="2"/><rect x="42" y="82" width="47" height="18" rx="3" fill="#4c8276"/><rect x="39" y="51" width="23" height="20" class="ps-window"/><circle cx="50" cy="103" r="6" class="ps-wheel"/><circle cx="80" cy="103" r="6" class="ps-wheel"/><path d="M154 37L155 60" stroke="#b6874b" stroke-dasharray="4 4" stroke-width="3"/></symbol>
    <symbol id="ps-reclaimer" viewBox="0 0 180 120"><path d="M9 109H173M19 113H165" stroke="#a8b9ad" stroke-width="2"/><path d="M23 103L47 17H133L158 103M33 73H149M47 17L66 46H116L133 17M48 18L55 77M132 18L127 77" fill="none" stroke="#527e72" stroke-width="6"/><path d="M41 95L90 50L138 95" fill="none" stroke="#c49c5d" stroke-width="9"/><path d="M43 94L89 53L136 94" fill="none" stroke="#5e6d61" stroke-width="3" stroke-dasharray="3 5"/><path d="M74 21V65M107 21V66" stroke="#879d94" stroke-width="2"/><circle cx="23" cy="104" r="7" class="ps-wheel"/><circle cx="158" cy="104" r="7" class="ps-wheel"/></symbol>
    <symbol id="ps-transfer" viewBox="0 0 180 120"><path d="M40 108V22L90 8L144 22V108M40 22H144M40 63H144M40 102H144M62 24V100M122 24V100" fill="#e5ece5" fill-opacity=".65" stroke="#7c998d" stroke-width="2"/><path d="M9 36H84V60H105V86H166" fill="none" stroke="#5c8475" stroke-width="13"/><path d="M9 32H88V59H109V82H166" fill="none" stroke="#c59a60" stroke-width="3"/><path d="M48 18L89 5L143 18M150 110V33M145 39H157M145 51H157M145 63H157M145 75H157M145 87H157M145 99H157" fill="none" stroke="#789384" stroke-width="2"/></symbol>
    <symbol id="ps-building" viewBox="0 0 180 120"><path d="M29 105V35L90 11L150 35V105ZM29 35H150" class="ps-metal"/><rect x="49" y="49" width="23" height="23" class="ps-window"/><rect x="104" y="49" width="24" height="23" class="ps-window"/><path d="M76 105V80H104V105" class="ps-metal"/></symbol>
    <symbol id="ps-cabin" viewBox="0 0 180 120"><path d="M35 98V32L135 32L152 66V98Z" class="ps-metal"/><polygon points="46,42 128,42 141,66 46,66" class="ps-window"/><path d="M24 98H162M52 98V110M132 98V110" stroke="#5e7d6c" stroke-width="4"/></symbol>
    <symbol id="ps-motor" viewBox="0 0 180 120"><rect x="25" y="39" width="112" height="54" rx="14" fill="#5b9281" stroke="#335e53" stroke-width="2"/><ellipse cx="135" cy="66" rx="14" ry="27" fill="#a5c2b5" stroke="#335e53" stroke-width="2"/><path d="M145 66H171" stroke="#496b61" stroke-width="9"/><path d="M42 43V87M53 43V87M64 43V87M75 43V87M86 43V87M97 43V87M108 43V87" stroke="#b7d0bc" stroke-width="3"/><path d="M32 96H58M107 96H133" stroke="#325d50" stroke-width="7"/><rect x="58" y="27" width="37" height="16" rx="3" class="ps-metal"/></symbol>
    <symbol id="ps-coupling" viewBox="0 0 180 120"><path d="M8 70H174" stroke="#527264" stroke-width="10"/><path d="M53 32Q88 10 123 32V95Q88 113 53 95Z" fill="#d2b777" stroke="#8b7954" stroke-width="2"/><ellipse cx="123" cy="64" rx="17" ry="35" fill="#e2cd9a" stroke="#8b7954" stroke-width="2"/><ellipse cx="122" cy="64" rx="8" ry="18" class="ps-metal"/><path d="M68 26V100M82 23V103M96 25V99" stroke="#aa905b" stroke-width="2"/><path d="M82 27V12H110V35" fill="none" stroke="#8b7954" stroke-width="3"/></symbol>
    <symbol id="ps-gearbox" viewBox="0 0 180 120"><path d="M33 99V34L120 21L149 42V96L62 109Z" fill="#d5e1d6" stroke="#6b8877" stroke-width="2"/><path d="M33 34L62 54L149 42M62 54V109" fill="none" stroke="#6b8877" stroke-width="2"/><circle cx="98" cy="73" r="23" fill="#a8bca9" stroke="#5c7a66" stroke-width="5" stroke-dasharray="7 3"/><circle cx="98" cy="73" r="8" class="ps-metal"/><path d="M12 60H39M139 72H170" stroke="#527264" stroke-width="9"/><path d="M68 111H147" stroke="#527264" stroke-width="5"/></symbol>
    <symbol id="ps-drive" viewBox="0 0 180 120"><svg x="0" y="27" width="80" height="80" viewBox="0 0 180 120"><use href="#ps-motor"/></svg><svg x="68" y="30" width="52" height="73" viewBox="0 0 180 120"><use href="#ps-coupling"/></svg><svg x="105" y="18" width="80" height="91" viewBox="0 0 180 120"><use href="#ps-gearbox"/></svg><path d="M9 107H178" stroke="#809789" stroke-width="3"/></symbol>
    <symbol id="ps-pulley" viewBox="0 0 180 120"><path d="M40 28L127 16V95L40 109Z" fill="#a9bfb0" stroke="#4a7160" stroke-width="2"/><ellipse cx="126" cy="56" rx="24" ry="40" fill="#789b83" stroke="#4a7160" stroke-width="2"/><path d="M132 57H169M8 68H40" stroke="#476953" stroke-width="9"/><ellipse cx="41" cy="68" rx="20" ry="40" fill="#d2dfd2" stroke="#4a7160" stroke-width="2"/><path d="M63 25V105M89 22V101M115 19V96" stroke="#779c80" stroke-width="2"/></symbol>
    <symbol id="ps-brake" viewBox="0 0 180 120"><circle cx="84" cy="58" r="34" class="ps-metal"/><circle cx="84" cy="58" r="9" class="ps-wheel"/><path d="M51 29L40 64L65 93M117 29L128 64L103 93M65 93H143V48" fill="none" stroke="#b98853" stroke-width="9"/><rect x="135" y="36" width="18" height="33" rx="3" fill="#cfa971"/><path d="M42 105H155" stroke="#6a8371" stroke-width="4"/></symbol>
    <symbol id="ps-thruster" viewBox="0 0 180 120"><rect x="58" y="42" width="64" height="58" rx="6" fill="#cfa971" stroke="#8b6b3b" stroke-width="2"/><rect x="74" y="16" width="32" height="28" rx="4" class="ps-metal"/><path d="M90 16V6M74 6H106M42 100H138" stroke="#6a8371" stroke-width="5"/></symbol>
    <symbol id="ps-pump" viewBox="0 0 180 120"><path d="M90 28V13H144V29M36 67H10M99 96V108H158" fill="none" stroke="#6b9dac" stroke-width="11"/><circle cx="91" cy="64" r="37" fill="#c1d9d9" stroke="#4a858b" stroke-width="3"/><path d="M88 39Q115 42 111 66Q107 89 88 86Q65 83 70 63Q75 48 88 58Q98 65 88 72" fill="none" stroke="#4a858b" stroke-width="5"/></symbol>
    <symbol id="ps-cooler" viewBox="0 0 180 120"><rect x="30" y="20" width="120" height="83" rx="4" fill="#d0e0dc" stroke="#6b8a7d" stroke-width="3"/><path d="M41 31H139M41 41H139M41 51H139M41 61H139M41 71H139M41 81H139M41 91H139" stroke="#829e94" stroke-width="3"/><circle cx="91" cy="63" r="26" fill="#ecf1e9" fill-opacity=".75" stroke="#64877b"/><path d="M90 39L98 60L114 74L90 69L71 77L83 60Z" fill="#5d8778"/></symbol>
    <symbol id="ps-tank" viewBox="0 0 180 120"><path d="M40 32V93Q90 122 140 93V32Z" fill="#c3d8d5" stroke="#698f83" stroke-width="2"/><ellipse cx="90" cy="32" rx="50" ry="16" fill="#e0ebe3" stroke="#698f83" stroke-width="2"/><path d="M42 72Q90 94 138 72" fill="none" stroke="#759c96" stroke-width="3"/><path d="M141 89H167V102" fill="none" stroke="#598997" stroke-width="6"/></symbol>
    <symbol id="ps-direct-drive" viewBox="0 0 180 120"><path d="M30 68H174" class="ps-shaft"/><svg x="0" y="15" width="115" height="90" viewBox="0 0 180 120"><use href="#ps-motor"/></svg><svg x="103" y="28" width="70" height="75" viewBox="0 0 180 120"><use href="#ps-coupling"/></svg><path d="M9 107H178" stroke="#809789" stroke-width="3"/></symbol>
    <symbol id="ps-filter" viewBox="0 0 180 120"><path d="M21 55H66M112 55H160" stroke="#5d94a2" stroke-width="8"/><path d="M63 27H116V84L104 104H75L63 84Z" fill="#d8e6df" stroke="#6b9181" stroke-width="3"/><path d="M73 37L105 85M73 55L99 94M81 35L108 74M75 84L105 37M73 65L95 36M88 94L109 58" stroke="#8ea89a" stroke-width="2"/></symbol>
    <symbol id="ps-sensor" viewBox="0 0 180 120"><path d="M91 79V107M69 106H112" stroke="#9d7545" stroke-width="5"/><rect x="56" y="33" width="69" height="49" rx="7" fill="#efd8a9" stroke="#b0884a" stroke-width="2"/><circle cx="92" cy="57" r="16" fill="#fff4d5" stroke="#b0884a" stroke-width="2"/><path d="M92 58L101 47M58 39L43 18" stroke="#a07840" stroke-width="3"/></symbol>
    <symbol id="ps-level-sensor" viewBox="0 0 180 120"><rect x="68" y="14" width="44" height="30" rx="5" fill="#efd8a9" stroke="#b0884a" stroke-width="2"/><path d="M78 44L70 62H110L102 44Z" class="ps-metal"/><path d="M68 74Q90 88 112 74M56 88Q90 106 124 88M44 102Q90 122 136 102" fill="none" stroke="#b0884a" stroke-width="3" stroke-dasharray="4 3"/></symbol>
    <symbol id="ps-protection" viewBox="0 0 180 120"><path d="M90 14L142 32V63Q139 94 90 112Q41 94 38 63V32Z" fill="#f0deba" stroke="#b39861" stroke-width="3"/><path d="M66 64L85 81L117 43" stroke="#947441" stroke-width="7" fill="none"/></symbol>
    <symbol id="ps-valve" viewBox="0 0 180 120"><path d="M18 77H163" stroke="#548c9d" stroke-width="8"/><path d="M47 48L126 99V49L47 100Z" fill="#a7cdd0" stroke="#52818a" stroke-width="3"/><path d="M87 76V27M63 26H112" stroke="#6f8271" stroke-width="5"/></symbol>
    <symbol id="ps-airlock" viewBox="0 0 180 120"><rect x="64" y="12" width="52" height="16" class="ps-metal"/><rect x="64" y="92" width="52" height="16" class="ps-metal"/><circle cx="90" cy="60" r="34" fill="#d5e1d6" stroke="#5c7a66" stroke-width="3"/><path d="M90 26V94M56 60H124M66 36L114 84M114 36L66 84" stroke="#5c7a66" stroke-width="3"/><circle cx="90" cy="60" r="8" class="ps-wheel"/></symbol>
    <symbol id="ps-dryer" viewBox="0 0 180 120"><rect x="36" y="18" width="108" height="86" rx="7" fill="#d0e0dc" stroke="#5a858b" stroke-width="2.5"/><rect x="48" y="30" width="42" height="62" rx="3" fill="#e6f0ee" stroke="#6b9dac" stroke-width="2"/><path d="M54 44H84M54 56H84M54 68H84M54 80H84" stroke="#6b9dac" stroke-width="3"/><circle cx="116" cy="52" r="16" fill="#f0f6f5" stroke="#5a858b" stroke-width="2"/><path d="M108 52L124 52M116 44L116 60" stroke="#5a858b" stroke-width="2.5"/></symbol>
    <symbol id="ps-spray" viewBox="0 0 180 120"><path d="M90 108V45L105 31" stroke="#619baa" stroke-width="7" fill="none"/><path d="M100 21L117 38" stroke="#437d89" stroke-width="7"/><path d="M116 23L148 9M121 29L161 25M123 36L159 46M119 41L145 62" stroke="#70b4c2" stroke-width="3" stroke-dasharray="3 5"/></symbol>
    <symbol id="ps-water" viewBox="0 0 180 120"><use href="#ps-spray"/><path d="M9 103H88M20 103V72H65V103" fill="none" stroke="#79a4aa" stroke-width="5"/><circle cx="43" cy="88" r="10" fill="#cadfe1" stroke="#6b9ba4" stroke-width="2"/></symbol>
    <symbol id="ps-chute" viewBox="0 0 180 120"><path d="M36 13H117V45L145 80L111 110L77 69H36Z" fill="#d1decf" stroke="#77917c" stroke-width="3"/><path d="M47 17V55H82L120 101M115 45L82 55" fill="none" stroke="#9fb39c" stroke-width="3"/><path d="M69 21V43L92 61L117 89" fill="none" stroke="#b58f51" stroke-width="5" stroke-dasharray="5 5"/></symbol>
    <symbol id="ps-silo" viewBox="0 0 180 120"><path d="M37 29Q90 0 144 29V77L107 104H77L37 77Z" fill="#d2ddcd" stroke="#7d947b" stroke-width="2"/><path d="M37 29Q90 52 144 29M37 77Q90 99 144 77M45 80V112M136 83V112M80 105V115H108V104" fill="none" stroke="#7d947b" stroke-width="3"/></symbol>
    <symbol id="ps-bunker" viewBox="0 0 180 120"><path d="M32 16H148V56L108 104H72L32 56Z" fill="#cfdcd2" stroke="#5f7f6d" stroke-width="2.5"/><path d="M32 32H148M32 56H148M72 104V114H108V104" fill="none" stroke="#5f7f6d" stroke-width="2.5"/><path d="M52 56L78 102M128 56L102 102" stroke="#8aa394" stroke-width="2" stroke-dasharray="4 3"/></symbol>
    <symbol id="ps-bunker-bay" viewBox="0 0 180 120"><rect x="14" y="14" width="152" height="94" rx="5" class="ps-building-frame"/><svg x="16" y="20" width="52" height="84" viewBox="0 0 180 120"><use href="#ps-bunker"/></svg><svg x="64" y="20" width="52" height="84" viewBox="0 0 180 120"><use href="#ps-bunker"/></svg><svg x="112" y="20" width="52" height="84" viewBox="0 0 180 120"><use href="#ps-bunker"/></svg></symbol>
    <symbol id="ps-sampler-system" viewBox="0 0 180 120"><rect x="26" y="10" width="128" height="102" rx="6" class="ps-building-frame"/><path d="M44 28H136M44 58H136M44 86H136" class="ps-floor"/><circle cx="72" cy="43" r="10" fill="#d6bc88" stroke="#8d7853" stroke-width="2"/><rect x="96" y="35" width="28" height="16" rx="3" class="ps-metal"/><circle cx="66" cy="72" r="11" fill="#aabd9d" stroke="#5c7a66" stroke-width="2"/><ellipse cx="112" cy="96" rx="20" ry="8" fill="#c7b385" stroke="#8b7954" stroke-width="2"/><path d="M72 53V61M110 51V88" stroke="#b0874b" stroke-width="3"/></symbol>
    <symbol id="ps-sampler" viewBox="0 0 180 120"><rect x="28" y="24" width="124" height="72" rx="8" class="ps-metal"/><path d="M44 60H136" stroke="#527264" stroke-width="6"/><path d="M76 30L94 60L76 90H104L122 60L104 30Z" fill="#d2b777" stroke="#8b7954" stroke-width="2.5"/><circle cx="52" cy="60" r="10" class="ps-wheel"/></symbol>
    <symbol id="ps-collector" viewBox="0 0 180 120"><ellipse cx="90" cy="40" rx="56" ry="18" fill="#d8e4d6" stroke="#5f7f6d" stroke-width="2.5"/><path d="M90 16V40" stroke="#b0874b" stroke-width="6"/><rect x="42" y="54" width="20" height="44" rx="4" fill="#c3d8d5" stroke="#598997" stroke-width="2"/><rect x="68" y="58" width="20" height="44" rx="4" fill="#c3d8d5" stroke="#598997" stroke-width="2"/><rect x="94" y="58" width="20" height="44" rx="4" fill="#c3d8d5" stroke="#598997" stroke-width="2"/><rect x="120" y="54" width="20" height="44" rx="4" fill="#c3d8d5" stroke="#598997" stroke-width="2"/></symbol>
    <symbol id="ps-screw-conveyor" viewBox="0 0 180 120"><rect x="20" y="42" width="140" height="36" rx="6" class="ps-metal"/><path d="M26 60H154" stroke="#527264" stroke-width="4"/><path d="M34 45L48 75L62 45L76 75L90 45L104 75L118 45L132 75L146 45" fill="none" stroke="#8b7954" stroke-width="3.5"/><path d="M34 26V42M138 78V98" stroke="#5f7f6d" stroke-width="8"/></symbol>
    <symbol id="ps-hoist" viewBox="0 0 180 120"><path d="M16 24H164M24 18H156" stroke="#5c7a66" stroke-width="6"/><rect x="62" y="24" width="56" height="32" rx="5" fill="#6b9281" stroke="#355e50" stroke-width="2"/><circle cx="74" cy="20" r="6" class="ps-wheel"/><circle cx="106" cy="20" r="6" class="ps-wheel"/><path d="M84 56V82M96 56V82" stroke="#4f6b58" stroke-width="3"/><circle cx="90" cy="84" r="9" class="ps-metal"/><path d="M90 93Q90 110 78 106Q72 102 78 96" fill="none" stroke="#96743d" stroke-width="5"/></symbol>
    <symbol id="ps-bogie" viewBox="0 0 180 120"><path d="M10 98H170" stroke="#7d8f82" stroke-width="5"/><path d="M26 62H154L140 84H40Z" class="ps-metal"/><circle cx="52" cy="86" r="14" class="ps-wheel"/><circle cx="52" cy="86" r="5" fill="#d8e4d6"/><circle cx="128" cy="86" r="14" class="ps-wheel"/><circle cx="128" cy="86" r="5" fill="#d8e4d6"/><rect x="68" y="38" width="44" height="24" rx="4" fill="#6b9281" stroke="#355e50" stroke-width="2"/></symbol>
    <symbol id="ps-rail-clamp" viewBox="0 0 180 120"><path d="M14 102H166M82 102V84H98V102" stroke="#6c8273" stroke-width="6"/><path d="M48 34H132V56H48Z" class="ps-metal"/><path d="M62 56L76 92M118 56L104 92" stroke="#b08448" stroke-width="8" stroke-linecap="round"/><rect x="74" y="14" width="32" height="22" rx="3" fill="#cfa971" stroke="#8b6b3b" stroke-width="2"/></symbol>
    <symbol id="ps-cable-reel" viewBox="0 0 180 120"><circle cx="90" cy="56" r="40" fill="#d5e1d6" stroke="#527264" stroke-width="3"/><circle cx="90" cy="56" r="26" fill="none" stroke="#8b7954" stroke-width="5" stroke-dasharray="6 4"/><circle cx="90" cy="56" r="10" class="ps-wheel"/><path d="M90 56L62 104H118Z" fill="#9eb4a2" stroke="#527264" stroke-width="2"/><path d="M44 104H136" stroke="#527264" stroke-width="4"/></symbol>
    <symbol id="ps-tripper" viewBox="0 0 180 120"><path d="M12 98H168" stroke="#7d8f82" stroke-width="4"/><path d="M34 88L54 34H128L144 88Z" fill="#d8e4d6" stroke="#5c7a66" stroke-width="2.5"/><path d="M16 74L72 34Q88 26 92 42L68 72Q64 82 82 82H164" fill="none" stroke="#3d6352" stroke-width="5"/><circle cx="82" cy="40" r="10" class="ps-metal"/><circle cx="68" cy="72" r="9" class="ps-metal"/><circle cx="52" cy="92" r="7" class="ps-wheel"/><circle cx="128" cy="92" r="7" class="ps-wheel"/></symbol>
    <symbol id="ps-switchboard" viewBox="0 0 180 120"><rect x="20" y="16" width="140" height="88" rx="4" class="ps-metal"/><path d="M55 16V104M90 16V104M125 16V104M20 44H160M20 74H160" stroke="#658477" stroke-width="2"/><rect x="28" y="24" width="18" height="12" fill="#8eaaa0"/><rect x="63" y="24" width="18" height="12" fill="#8eaaa0"/><rect x="98" y="24" width="18" height="12" fill="#8eaaa0"/><rect x="133" y="24" width="18" height="12" fill="#cfa971"/></symbol>
    <symbol id="ps-elevator" viewBox="0 0 180 120"><rect x="52" y="10" width="76" height="100" rx="4" fill="#e5ece5" stroke="#6b8877" stroke-width="2.5"/><rect x="64" y="42" width="52" height="48" rx="3" class="ps-metal"/><rect x="72" y="50" width="36" height="18" class="ps-window"/><path d="M82 10V42M98 10V42" stroke="#527264" stroke-width="2.5"/><path d="M90 20L83 28H97ZM90 36L83 28H97Z" fill="#4c8276"/></symbol>
    <symbol id="ps-grab" viewBox="0 0 180 120"><path d="M78 10V42M102 10V42" stroke="#527264" stroke-width="3"/><circle cx="90" cy="42" r="8" class="ps-wheel"/><path d="M90 42L46 68M90 42L134 68" stroke="#527264" stroke-width="4"/><path d="M42 66Q38 104 86 102L86 68Z" fill="#8a9f99" stroke="#3d6460" stroke-width="2.5"/><path d="M138 66Q142 104 94 102L94 68Z" fill="#8a9f99" stroke="#3d6460" stroke-width="2.5"/></symbol>
    <symbol id="ps-trolley" viewBox="0 0 180 120"><path d="M12 36H168" stroke="#5c7a66" stroke-width="6"/><rect x="44" y="40" width="92" height="34" rx="5" class="ps-metal"/><circle cx="58" cy="34" r="8" class="ps-wheel"/><circle cx="122" cy="34" r="8" class="ps-wheel"/><path d="M74 74L64 104M106 74L116 104" stroke="#527264" stroke-width="3"/></symbol>
    <symbol id="ps-boom" viewBox="0 0 180 120"><path d="M18 92L154 24L164 42L28 106Z" fill="#dce6dc" stroke="#547b70" stroke-width="2.5"/><path d="M28 90L52 68L60 84L84 52L92 68L118 36L126 52L152 28" fill="none" stroke="#547b70" stroke-width="2.5"/><circle cx="24" cy="96" r="8" class="ps-wheel"/><circle cx="158" cy="34" r="8" class="ps-wheel"/></symbol>
    <symbol id="ps-slew" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="68" ry="34" fill="#d5e1d6" stroke="#5c7a66" stroke-width="6" stroke-dasharray="9 4"/><ellipse cx="90" cy="64" rx="46" ry="22" fill="#f4f7f0" stroke="#5c7a66" stroke-width="2.5"/><circle cx="146" cy="42" r="14" fill="#cfa971" stroke="#8b6b3b" stroke-width="2.5"/></symbol>
    <symbol id="ps-crusher" viewBox="0 0 180 120"><path d="M38 18H142L124 49V105H54V49Z" fill="#d6dfce" stroke="#7d9276" stroke-width="3"/><circle cx="89" cy="69" r="25" fill="#aabd9d" stroke="#6b835e" stroke-width="5" stroke-dasharray="6 3"/><circle cx="89" cy="69" r="7" class="ps-wheel"/><path d="M64 88Q89 111 115 87" fill="none" stroke="#829179" stroke-width="3"/><path d="M77 106V116M105 106V116" stroke="#829179" stroke-width="5"/></symbol>
    <symbol id="ps-screen" viewBox="0 0 180 120"><path d="M25 34L155 54L144 90L16 70Z" fill="#d2ddca" stroke="#809776" stroke-width="3"/><path d="M31 43L145 61M28 53L144 70M44 41L39 65M68 45L63 69M91 49L86 73M114 53L109 77M139 57L134 81M25 76V110M144 94V110" stroke="#829476" stroke-width="3"/></symbol>
    <symbol id="ps-ship" viewBox="0 0 180 120"><path d="M54 106H176M60 112V106M92 112V106M124 112V106M156 112V106" stroke="#6b8577" stroke-width="2.5"/><path d="M4 96H48L42 112H4Z" fill="#7c9a8d" stroke="#48685b" stroke-width="1.8"/><path d="M4 115Q18 109 32 115T56 115" fill="none" stroke="#6fa3b0" stroke-width="2.2"/><path d="M74 32L82 6L94 32" fill="none" stroke="#486e60" stroke-width="3" stroke-linejoin="round"/><path d="M82 7L18 32M82 7L154 21" fill="none" stroke="#6e8c7e" stroke-width="1.8"/><rect x="96" y="19" width="40" height="13" rx="2" fill="#b7cbbd" stroke="#486e60" stroke-width="2"/><rect x="138" y="21" width="26" height="11" rx="2" fill="#d2e0d5" stroke="#486e60" stroke-width="1.8"/><path d="M10 35L16 31H168V37H10Z" fill="#dce7df" stroke="#3f6557" stroke-width="2.2"/><path d="M18 36L28 32L38 36L48 32L58 36L68 32L78 36L90 32L102 36L114 32L126 36L138 32L150 36" fill="none" stroke="#537a6b" stroke-width="1.4"/><path d="M74 37V103M80 37V103M146 37V103M152 37V103" stroke="#446b5c" stroke-width="2.4"/><path d="M74 52H80M74 72H80M146 52H152M146 72H152M80 44L146 44" stroke="#638475" stroke-width="1.8"/><rect x="61" y="40" width="12" height="9" rx="1.5" fill="#e6f2ef" stroke="#446b5c" stroke-width="1.6"/><rect x="23" y="37" width="20" height="5" rx="1.5" fill="#4c7a69" stroke="#2f5245" stroke-width="1.5"/><path d="M29 42V60M37 42V60" stroke="#48685b" stroke-width="1.6"/><path d="M33 58L21 67Q20 79 32 78V66ZM33 58L45 67Q46 79 34 78V66Z" fill="#4f6c66" stroke="#2e4742" stroke-width="1.8"/><path d="M36 52Q65 40 98 48" fill="none" stroke="#b57c3c" stroke-width="2" stroke-dasharray="3 2"/><path d="M84 47H124L114 66H94Z" fill="#c7d7cb" stroke="#446b5c" stroke-width="2"/><path d="M84 47L79 53" stroke="#9e7b42" stroke-width="2.2"/><polygon points="92,67 124,69 122,75 92,73" fill="#dfc48a" stroke="#856835" stroke-width="1.8"/><rect x="84" y="79" width="58" height="6" rx="3" fill="#7c998b" stroke="#385c4e" stroke-width="1.8"/><circle cx="88" cy="82" r="2.5" class="ps-wheel"/><circle cx="138" cy="82" r="2.5" class="ps-wheel"/><path d="M89 86V94M137 86V94" stroke="#b57c3c" stroke-width="2.2" stroke-dasharray="2 2"/><rect x="83" y="94" width="14" height="6" rx="2" fill="#547568" stroke="#314d42" stroke-width="1.4"/><rect x="130" y="94" width="14" height="6" rx="2" fill="#547568" stroke="#314d42" stroke-width="1.4"/><rect x="67" y="100" width="18" height="4" rx="1" fill="#557a6b"/><circle cx="71" cy="105" r="2.8" class="ps-wheel"/><circle cx="81" cy="105" r="2.8" class="ps-wheel"/><rect x="140" y="100" width="18" height="4" rx="1" fill="#557a6b"/><circle cx="144" cy="105" r="2.8" class="ps-wheel"/><circle cx="154" cy="105" r="2.8" class="ps-wheel"/></symbol>
    <symbol id="ps-reference" viewBox="0 0 180 120"><path d="M49 9H111L134 32V111H49Z" fill="#eef2e8" stroke="#809b7e" stroke-width="3"/><path d="M111 9V32H134M65 52H116M65 68H116M65 84H104" fill="none" stroke="#809b7e" stroke-width="3"/></symbol>
    <symbol id="ps-assembly" viewBox="0 0 180 120"><path d="M44 79V37L91 14L140 37V80L92 107Z" fill="#d8e4d6" stroke="#809b7e" stroke-width="2"/><path d="M44 37L91 61L140 37M91 61V107" fill="none" stroke="#809b7e" stroke-width="2"/><circle cx="92" cy="57" r="16" fill="#ecf2e8" stroke="#809b7e" stroke-width="2"/><path d="M83 57H101M92 48V66" stroke="#638465" stroke-width="3"/></symbol>
    <style>
      .ps-Subtle { fill: #516863; font-size: 9.5px; font-weight: 700; letter-spacing: .02em; font-family: "IBM Plex Sans", "Segoe UI", sans-serif; }
      .ps-banner-note { fill: #3f5953; font-size: 8.3px; font-weight: 700; letter-spacing: .015em; font-family: "IBM Plex Sans", "Segoe UI", sans-serif; }
    </style>
    <symbol id="ps-jetty" viewBox="0 0 180 120"><path d="M8 94Q26 88 44 94T80 94T116 94T152 94T176 94" fill="none" stroke="#5b96a5" stroke-width="3"/><path d="M8 106Q26 100 44 106T80 106T116 106T152 106T176 106" fill="none" stroke="#7ab0bd" stroke-width="2.2"/><rect x="14" y="54" width="152" height="10" rx="2" fill="#c7d6cc" stroke="#47695b" stroke-width="2.2"/><path d="M28 64V96M56 64V96M88 64V96M120 64V96M150 64V96" stroke="#547466" stroke-width="4.5"/><path d="M28 74L56 88M56 74L88 88M88 74L120 88M120 74L150 88" stroke="#6d8c7e" stroke-width="2"/><rect x="22" y="45" width="136" height="6" rx="2" fill="#6f8f80" stroke="#3f6153" stroke-width="1.6"/><path d="M44 54V22L54 14L64 22V54M106 54V22L116 14L126 22V54" fill="none" stroke="#45695a" stroke-width="2.5"/><path d="M24 26H82M86 26H144" stroke="#45695a" stroke-width="3"/></symbol>
    <symbol id="ps-shuttle-conveyor" viewBox="0 0 180 120"><path d="M12 96H168" stroke="#6c8577" stroke-width="3.5"/><path d="M22 44H158" stroke="#856835" stroke-width="2.5" stroke-dasharray="5 3"/><path d="M22 44L30 39V49ZM158 44L150 39V49Z" fill="#856835"/><rect x="26" y="56" width="128" height="18" rx="9" fill="#89a195" stroke="#3c6155" stroke-width="2.5"/><circle cx="36" cy="65" r="7" class="ps-metal"/><circle cx="144" cy="65" r="7" class="ps-metal"/><circle cx="64" cy="62" r="3.5" fill="#dce7df"/><circle cx="90" cy="62" r="3.5" fill="#dce7df"/><circle cx="116" cy="62" r="3.5" fill="#dce7df"/><rect x="40" y="74" width="100" height="10" rx="2" class="ps-metal"/><circle cx="54" cy="90" r="6" class="ps-wheel"/><circle cx="126" cy="90" r="6" class="ps-wheel"/><path d="M18 65H8M162 65H172" stroke="#b37736" stroke-width="3" stroke-dasharray="3 2"/></symbol>
    <symbol id="ps-vibro-feeder" viewBox="0 0 180 120"><polygon points="24,34 158,44 152,72 24,62" fill="#dfd0a6" stroke="#7d6637" stroke-width="2.5"/><path d="M34 44L148 53" stroke="#5a4926" stroke-width="4" stroke-dasharray="6 4"/><circle cx="72" cy="78" r="13" fill="#b7cbbd" stroke="#44695a" stroke-width="2.2"/><circle cx="104" cy="80" r="13" fill="#b7cbbd" stroke="#44695a" stroke-width="2.2"/><path d="M66 78L78 78M104 74L104 86" stroke="#365448" stroke-width="2.5"/><path d="M36 63L44 71L30 79L44 87L36 96M138 71L146 78L132 85L146 92L138 98" fill="none" stroke="#44695a" stroke-width="3.5" stroke-linejoin="round"/><path d="M18 98H162" stroke="#5f7a6d" stroke-width="4"/></symbol>
    <symbol id="ps-hopper" viewBox="0 0 180 120"><path d="M24 20H156" stroke="#4b6c5d" stroke-width="4.5"/><path d="M34 20V14M52 20V14M70 20V14M88 20V14M106 20V14M124 20V14M142 20V14" stroke="#7d6637" stroke-width="2.5"/><polygon points="28,22 152,22 118,86 62,86" fill="#cfdcd2" stroke="#4b6c5d" stroke-width="2.5"/><path d="M44 36H136M54 58H126" stroke="#7e998b" stroke-width="2" stroke-dasharray="5 3"/><rect x="60" y="86" width="60" height="12" rx="2" fill="#dfc48a" stroke="#7d6637" stroke-width="2"/><path d="M28 42V104M152 42V104" stroke="#5f7d6e" stroke-width="3.5"/></symbol>
    <symbol id="ps-grizzly-grid" viewBox="0 0 180 120"><polygon points="28,26 152,26 166,94 14,94" fill="#dce6de" stroke="#496b5c" stroke-width="3"/><path d="M24 42H156M20 60H160M17 78H163" stroke="#496b5c" stroke-width="3.5"/><path d="M46 26L36 94M68 26L62 94M90 26V94M112 26L118 94M134 26L144 94" stroke="#6e5a31" stroke-width="3.5"/></symbol>
    <symbol id="ps-transformer" viewBox="0 0 180 120"><rect x="38" y="34" width="104" height="68" rx="5" fill="#cad8d0" stroke="#486a5c" stroke-width="2.5"/><rect x="24" y="42" width="14" height="52" rx="2" fill="#9eb4a8" stroke="#486a5c" stroke-width="2"/><rect x="142" y="42" width="14" height="52" rx="2" fill="#9eb4a8" stroke="#486a5c" stroke-width="2"/><path d="M56 34V16M90 34V16M124 34V16" stroke="#7c5d2c" stroke-width="4"/><ellipse cx="56" cy="22" rx="6" ry="3" fill="#dfc48a"/><ellipse cx="90" cy="22" rx="6" ry="3" fill="#dfc48a"/><ellipse cx="124" cy="22" rx="6" ry="3" fill="#dfc48a"/><circle cx="74" cy="68" r="16" fill="none" stroke="#3e6253" stroke-width="2.8"/><circle cx="106" cy="68" r="16" fill="none" stroke="#7c5d2c" stroke-width="2.8"/><path d="M18 104H162" stroke="#486a5c" stroke-width="4"/></symbol>
    <symbol id="ps-dg-set" viewBox="0 0 180 120"><rect x="18" y="88" width="144" height="12" rx="2" fill="#6b8577" stroke="#3d594b" stroke-width="2"/><rect x="26" y="38" width="76" height="50" rx="4" fill="#b7cbbd" stroke="#426455" stroke-width="2.5"/><path d="M38 38V24H50V38M62 38V24H74V38M86 38V24H94V38" fill="#8da698" stroke="#426455" stroke-width="1.8"/><path d="M44 24V14H28" fill="none" stroke="#5b7667" stroke-width="4"/><rect x="106" y="46" width="46" height="42" rx="8" fill="#dfc48a" stroke="#7c6332" stroke-width="2.5"/><path d="M92 59L82 71H92L84 82" fill="none" stroke="#7c6332" stroke-width="2.5"/></symbol>
    <symbol id="ps-anemometer" viewBox="0 0 180 120"><path d="M90 36V106M64 106H116" stroke="#4b6c5d" stroke-width="4.5"/><path d="M74 106L90 66L106 106" fill="none" stroke="#6d8c7e" stroke-width="2.5"/><circle cx="90" cy="36" r="7" fill="#dfc48a" stroke="#7c6332" stroke-width="2"/><path d="M38 36H142M90 36L58 18" stroke="#4b6c5d" stroke-width="3"/><path d="M38 26A10 10 0 1 0 38 46Z" fill="#709b8b" stroke="#3b5e50" stroke-width="2"/><path d="M142 26A10 10 0 1 1 142 46Z" fill="#709b8b" stroke="#3b5e50" stroke-width="2"/><circle cx="56" cy="17" r="8" fill="#c3d8d5" stroke="#4b6c5d" stroke-width="2"/></symbol>
    <symbol id="ps-pru" viewBox="0 0 180 120"><rect x="20" y="18" width="140" height="84" rx="8" fill="#eef4f0" stroke="#6b8d80" stroke-width="2" stroke-dasharray="6 3"/><path d="M12 66H168" stroke="#49899c" stroke-width="6"/><rect x="34" y="50" width="26" height="32" rx="3" fill="#d5e2df" stroke="#437682" stroke-width="2"/><polygon points="72,52 104,68 104,52 72,68" fill="#dfc48a" stroke="#7d6431" stroke-width="2"/><path d="M88 60V36M76 36H100" stroke="#4b6c5d" stroke-width="3"/><circle cx="132" cy="40" r="13" fill="#fff8e6" stroke="#7d6431" stroke-width="2"/><path d="M132 53V66M132 40L139 33" stroke="#7d6431" stroke-width="2.2"/></symbol>
    <symbol id="ps-fas" viewBox="0 0 180 120"><rect x="22" y="24" width="136" height="74" rx="6" fill="#d8e5df" stroke="#4d7061" stroke-width="2.5"/><rect x="32" y="34" width="34" height="54" rx="2" fill="#f0f5f1" stroke="#6b8a7c" stroke-width="2"/><path d="M38 38L58 48L38 58L58 68L38 78L58 84" fill="none" stroke="#6b8a7c" stroke-width="2.2"/><circle cx="106" cy="61" r="22" fill="#bfd4ca" stroke="#446859" stroke-width="2.2"/><path d="M106 43L114 58L124 66L106 65L92 72L99 57Z" fill="#4c7a68"/><path d="M158 48H172M158 74H172" stroke="#49899c" stroke-width="5"/></symbol>
    <symbol id="ps-bulldozer" viewBox="0 0 180 120"><rect x="26" y="72" width="96" height="26" rx="13" fill="#6d8276" stroke="#384d42" stroke-width="3"/><circle cx="42" cy="85" r="8" class="ps-wheel"/><circle cx="74" cy="85" r="8" class="ps-wheel"/><circle cx="106" cy="85" r="8" class="ps-wheel"/><path d="M34 72V44H78L92 26H122V72Z" fill="#dfc48a" stroke="#7d6431" stroke-width="2.5"/><rect x="94" y="32" width="22" height="20" class="ps-window"/><path d="M114 78H146M146 42Q164 68 146 98L158 98Q172 68 156 42Z" fill="#b7cbbd" stroke="#426455" stroke-width="2.5"/></symbol>
    <symbol id="ps-loader" viewBox="0 0 180 120"><path d="M24 76V46L52 42V26H88L102 48V76Z" fill="#dfc48a" stroke="#7d6431" stroke-width="2.5"/><rect x="58" y="32" width="24" height="18" class="ps-window"/><circle cx="44" cy="82" r="16" fill="#495e54" stroke="#2c3d35" stroke-width="3"/><circle cx="44" cy="82" r="6" fill="#cfdcd2"/><circle cx="92" cy="82" r="16" fill="#495e54" stroke="#2c3d35" stroke-width="3"/><circle cx="92" cy="82" r="6" fill="#cfdcd2"/><path d="M88 46L136 62M88 58L134 76" stroke="#537262" stroke-width="4.5"/><path d="M134 46L164 52L158 88H132Z" fill="#9eb4a6" stroke="#3f6152" stroke-width="2.5"/></symbol>
    <symbol id="ps-vacuum" viewBox="0 0 180 120"><path d="M40 24H98V68L78 96H60L40 68Z" fill="#c7d8d6" stroke="#426e78" stroke-width="2.5"/><ellipse cx="69" cy="24" rx="29" ry="8" fill="#e2eeec" stroke="#426e78" stroke-width="2"/><rect x="112" y="52" width="44" height="44" rx="6" fill="#89a89c" stroke="#3d6153" stroke-width="2.5"/><circle cx="134" cy="74" r="12" class="ps-wheel"/><path d="M84 24V12H134V52" fill="none" stroke="#49899c" stroke-width="5"/><path d="M14 54Q26 34 40 42" fill="none" stroke="#5c7a6d" stroke-width="5" stroke-dasharray="5 3"/></symbol>
    <symbol id="ps-scraper-chain" viewBox="0 0 180 120"><rect x="14" y="38" width="152" height="44" rx="22" fill="none" stroke="#4a6958" stroke-width="4"/><circle cx="38" cy="60" r="14" fill="#d5e1d6" stroke="#4a6958" stroke-width="3" stroke-dasharray="5 3"/><circle cx="142" cy="60" r="14" fill="#d5e1d6" stroke="#4a6958" stroke-width="3" stroke-dasharray="5 3"/><path d="M52 24V44M82 24V44M112 24V44M66 76V96M96 76V96M126 76V96" stroke="#856835" stroke-width="6" stroke-linecap="round"/><path d="M24 60H156" stroke="#6c8576" stroke-width="2.5" stroke-dasharray="8 4"/></symbol>
    <symbol id="ps-buffer" viewBox="0 0 180 120"><rect x="24" y="24" width="22" height="72" rx="3" fill="#6b8577" stroke="#3c5749" stroke-width="2.5"/><rect x="46" y="42" width="54" height="36" rx="3" class="ps-metal"/><rect x="100" y="48" width="36" height="24" rx="2" fill="#c7d6cc" stroke="#486a5c" stroke-width="2"/><path d="M136 32V88" stroke="#8b6b3b" stroke-width="10" stroke-linecap="round"/><path d="M54 46L64 74L74 46L84 74L94 46" fill="none" stroke="#486a5c" stroke-width="3"/></symbol>
    <symbol id="ps-compressor" viewBox="0 0 180 120"><rect x="21" y="24" width="136" height="73" rx="9" class="ps-metal"/><path d="M29 102H150M36 97V108M142 97V108M157 48H172V22" stroke="#6b9dac" stroke-width="6" fill="none"/><circle cx="62" cy="61" r="22" class="ps-wheel"/><path d="M50 61H74M62 49V73M100 43H140M100 55H140M100 67H140M100 79H140" stroke="#638a88" stroke-width="4"/></symbol>
    <symbol id="ps-yard" viewBox="0 0 180 120"><use href="#ps-pile"/><svg x="67" y="-6" width="119" height="110" viewBox="0 0 180 120"><use href="#ps-stacker"/></svg></symbol>
    <symbol id="ps-mechanical" viewBox="0 0 180 120"><use href="#ps-conveyor"/></symbol>
    <marker id="ps-power-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#507ba1"/></marker>
    <symbol id="ps-silo-house" viewBox="0 0 180 120"><path class="ps-building-frame" d="M12 115V15H168V115M12 55H168M12 100H168"/><svg x="15" y="12" width="75" height="100" viewBox="0 0 180 120"><use href="#ps-silo"/></svg><svg x="90" y="12" width="75" height="100" viewBox="0 0 180 120"><use href="#ps-silo"/></svg></symbol>
    <symbol id="ps-extractor" viewBox="0 0 180 120"><ellipse cx="90" cy="70" rx="70" ry="25" class="ps-metal"/><path d="M38 62L90 15L142 62Q90 95 38 62Z" fill="#d9c28f" stroke="#8c805f" stroke-width="2"/><path d="M58 80L89 96L125 79M83 90V115H105V90" class="ps-metal"/><path d="M25 74Q90 106 155 74" fill="none" stroke="#816c9d" stroke-width="5"/><path d="M20 94H52M129 94H164" stroke="#637869" stroke-width="8"/></symbol>
    <symbol id="ps-cone" viewBox="0 0 180 120"><path d="M18 92H162M90 33V113M28 48L151 110M153 48L27 110" stroke="#799381" stroke-width="5"/><path d="M37 81L90 12L143 81Q90 116 37 81Z" fill="#d8c395" stroke="#9b8963" stroke-width="2"/></symbol>
    <symbol id="ps-platform" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="78" ry="40" class="ps-metal"/><ellipse cx="90" cy="64" rx="27" ry="15" fill="#546b61"/><path d="M18 84V112M162 84V112" stroke="#7b9582" stroke-width="5"/></symbol>
    <symbol id="ps-blade" viewBox="0 0 180 120"><ellipse cx="90" cy="66" rx="70" ry="38" fill="none" stroke="#beccb9" stroke-dasharray="5 5" stroke-width="3"/><g class="ps-rotor"><path d="M20 58L87 40L150 79L110 89L85 63L24 76Z" fill="#a8b8a3" stroke="#628269" stroke-width="3"/><circle cx="88" cy="62" r="10" class="ps-wheel"/></g></symbol>
    <symbol id="ps-bearing" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="73" ry="39" fill="#b9c5ae" stroke="#7e7093" stroke-width="8" stroke-dasharray="8 3"/><ellipse cx="90" cy="64" rx="50" ry="23" fill="#f2f5e9" stroke="#738c71" stroke-width="3"/></symbol>
    <symbol id="ps-sleeve" viewBox="0 0 180 120"><path d="M30 33V89Q90 119 150 89V33" class="ps-metal"/><ellipse cx="90" cy="33" rx="60" ry="22" class="ps-metal"/><ellipse cx="90" cy="33" rx="44" ry="13" fill="#6b8475"/></symbol>
    <symbol id="ps-seal" viewBox="0 0 180 120"><ellipse cx="90" cy="64" rx="69" ry="36" fill="#c2cbb4" stroke="#758a71" stroke-width="5"/><ellipse cx="90" cy="64" rx="57" ry="28" fill="none" stroke="#758a71" stroke-width="3"/><ellipse cx="90" cy="64" rx="44" ry="20" fill="#f2f5e9" stroke="#758a71" stroke-width="4"/></symbol>
    <symbol id="ps-lubrication" viewBox="0 0 180 120"><rect x="55" y="45" width="69" height="58" rx="7" class="ps-metal"/><path d="M65 43V20H115V43M90 22V8M57 78H20V35M123 78H158V35" fill="none" stroke="#619baa" stroke-width="7"/><path d="M89 54Q70 79 90 85Q109 79 89 54" fill="#c5a567"/></symbol>
    <symbol id="ps-panel" viewBox="0 0 180 120"><rect x="43" y="10" width="94" height="101" rx="4" class="ps-metal"/><rect x="58" y="26" width="64" height="27" fill="#8eaaa0" stroke="#658477"/><path d="M64 72H75M94 72H105M64 87H105" stroke="#527b69" stroke-width="5"/></symbol>
    <symbol id="ps-fan" viewBox="0 0 180 120"><circle cx="90" cy="60" r="45" class="ps-metal"/><path d="M88 58Q43 18 68 22Q109 13 93 54Q145 37 129 68Q105 95 94 66Q70 111 55 83Q50 58 85 61Z" fill="#709b8b"/><circle cx="90" cy="60" r="9" class="ps-wheel"/><path d="M54 100H129" stroke="#607c67" stroke-width="6"/></symbol>
    <symbol id="ps-gate" viewBox="0 0 180 120"><path d="M58 8H122V40L163 92L128 114L90 68L52 114L17 92L58 40Z" class="ps-metal"/><path d="M59 26L101 68" stroke="#b0874b" stroke-width="7"/><circle cx="61" cy="28" r="8" fill="#698474"/></symbol>
    <symbol id="ps-feeder" viewBox="0 0 180 120"><path d="M15 45H150V83H15Z" class="ps-metal"/><rect x="10" y="77" width="155" height="23" rx="11" fill="#89a18d" stroke="#4e735b" stroke-width="3"/><path d="M22 102V115M148 102V115M24 52H143" stroke="#58795e" stroke-width="4"/><circle cx="24" cy="88" r="7" class="ps-wheel"/><circle cx="149" cy="88" r="7" class="ps-wheel"/></symbol>
    <symbol id="ps-access" viewBox="0 0 180 120"><path d="M27 112V15H153V112M19 15H162M76 17V66Q104 65 103 82Q96 103 80 90" fill="none" stroke="#8e9f84" stroke-width="7"/><path d="M24 45H46M24 67H46M24 89H46" stroke="#8e9f84" stroke-width="4"/></symbol>
    <symbol id="ps-duct" viewBox="0 0 180 120"><path d="M24 103V37Q24 17 45 17H159V48H63V103Z" class="ps-metal"/><path d="M35 93V40Q35 29 49 29H142" fill="none" stroke="#79a0a5" stroke-width="3" stroke-dasharray="8 6"/></symbol>
    <symbol id="ps-spray-system" viewBox="0 0 180 120"><use href="#ps-water"/></symbol>
    <symbol id="ps-crusher-housing" viewBox="0 0 180 120"><path d="M30 30L90 8L148 30V95L91 115L30 95Z" class="ps-metal"/><path d="M45 45L87 30V94L45 81Z" fill="#708b78"/><path d="M105 32L137 44V80L105 94Z" fill="#a7c1ad" stroke="#718f79" stroke-width="2"/><path d="M45 45L14 56V93L45 81" fill="#d8e6d6" stroke="#718f79" stroke-width="3"/></symbol>
    <symbol id="ps-damper" viewBox="0 0 180 120"><path d="M15 33H166V90H15Z" fill="#dce5da" stroke="#789282" stroke-width="3"/><path d="M44 35L69 87M87 35L112 87M130 35L154 87" stroke="#6c8875" stroke-width="6"/><path d="M91 33V16H132" fill="none" stroke="#789282" stroke-width="4"/><rect x="128" y="5" width="35" height="24" rx="5" class="ps-metal"/></symbol>
    <symbol id="ps-crusher-house" viewBox="0 0 180 120"><use href="#ps-transfer"/></symbol>
    <symbol id="ps-screenhouse" viewBox="0 0 180 120"><path class="ps-building-frame" d="M22 108V22L90 8L158 22V108M22 22H158M22 64H158M22 102H158"/><svg x="32" y="22" width="116" height="76" viewBox="0 0 180 120"><use href="#ps-screen"/></svg></symbol>
    <symbol id="ps-crusher-rotor" viewBox="0 0 180 120"><path d="M8 64H172" stroke="#6e7d6b" stroke-width="10"/><g class="ps-rotor"><circle cx="90" cy="64" r="37" fill="#d6bc88" stroke="#8d7853" stroke-width="3"/><circle cx="90" cy="64" r="26" fill="none" stroke="#b28e51" stroke-width="10" stroke-dasharray="7 5"/><path d="M90 28V100M54 64H126" stroke="#77674a" stroke-width="4"/><circle cx="90" cy="64" r="10" class="ps-wheel"/></g></symbol>
    <symbol id="ps-cage" viewBox="0 0 180 120"><path d="M25 29Q25 111 139 105L157 79Q57 85 49 20Z" class="ps-metal"/><path d="M32 48L54 40M42 67L67 57M57 83L80 72M77 95L94 82M99 103L112 85M120 105L130 85" stroke="#65836e" stroke-width="4"/></symbol>
    <symbol id="ps-foundation" viewBox="0 0 180 120"><path d="M12 32H168V52H12Z" class="ps-metal"/><path d="M26 56L43 64L26 71L43 78L26 85L43 92M75 56L92 64L75 71L92 78L75 85L92 92M128 56L145 64L128 71L145 78L128 85L145 92M12 99H168" fill="none" stroke="#7b8b74" stroke-width="4"/></symbol>
    <symbol id="ps-hydraulic" viewBox="0 0 180 120"><use href="#ps-lubrication"/><path d="M115 30H165V97" stroke="#68919f" stroke-width="6" fill="none"/></symbol>
    <symbol id="ps-cylinder" viewBox="0 0 180 120"><path d="M15 64H170" stroke="#687c70" stroke-width="10"/><rect x="38" y="47" width="72" height="33" class="ps-metal"/><path d="M56 48V27M95 48V27" stroke="#6498a2" stroke-width="5"/></symbol>
    <symbol id="ps-actuator" viewBox="0 0 180 120"><use href="#ps-cylinder"/><rect x="43" y="12" width="47" height="35" rx="6" class="ps-metal"/><circle cx="30" cy="31" r="15" fill="none" stroke="#728b73" stroke-width="3"/></symbol>
    <symbol id="ps-exciter" viewBox="0 0 180 120"><path d="M10 66H170" stroke="#728674" stroke-width="7"/><rect x="35" y="41" width="110" height="48" rx="15" class="ps-metal"/><circle cx="91" cy="64" r="28" fill="#ddc58e" stroke="#8c7851" stroke-width="3"/><path d="M65 62Q90 110 117 63Z" fill="#a38a55"/></symbol>
    <symbol id="ps-cyclone" viewBox="0 0 180 120"><path d="M48 17H135V56L100 98V116H82V98L48 56Z" class="ps-metal"/><path d="M90 17V4M15 30H49" stroke="#77959c" stroke-width="10"/><path d="M66 32Q136 38 66 51Q110 69 88 85" fill="none" stroke="#88a7a4" stroke-width="3"/></symbol>
    <symbol id="ps-de-house" viewBox="0 0 180 120"><use href="#ps-cyclone"/><svg x="75" y="40" width="95" height="80" viewBox="0 0 180 120"><use href="#ps-fan"/></svg></symbol>
    <symbol id="ps-de-stream" viewBox="0 0 180 120"><use href="#ps-de-house"/></symbol>
    <symbol id="ps-detector" viewBox="0 0 180 120"><path d="M23 98V20H151V98M23 34H151M23 87H151" stroke="#9a824f" stroke-width="9" fill="none"/><path d="M14 68H162" stroke="#6c8876" stroke-width="12"/><path d="M50 45Q90 70 130 45" stroke="#d2b572" stroke-dasharray="5 5" fill="none"/><rect x="151" y="31" width="23" height="43" rx="4" class="ps-metal"/></symbol>
    <symbol id="ps-weigher" viewBox="0 0 180 120"><path d="M12 53H167M28 94H151" stroke="#7c957e" stroke-width="7"/><path d="M35 63V90M142 63V90" stroke="#b39658" stroke-width="8"/><path d="M42 94L58 104L42 112M123 94L139 104L123 112" stroke="#9f8453" stroke-width="4" fill="none"/><g fill="#abc0ac" stroke="#658274" stroke-width="3"><circle cx="35" cy="53" r="10"/><circle cx="70" cy="53" r="10"/><circle cx="106" cy="53" r="10"/><circle cx="142" cy="53" r="10"/></g></symbol>
    <symbol id="ps-receiver" viewBox="0 0 180 120"><rect x="54" y="8" width="72" height="97" rx="30" class="ps-metal"/><path d="M57 99V116M122 99V116M15 43H54M126 43H165" stroke="#629baa" stroke-width="6"/><circle cx="90" cy="31" r="12" fill="#f6eed1" stroke="#a7915a" stroke-width="2"/></symbol>
    <symbol id="ps-pipe" viewBox="0 0 180 120"><path d="M12 85H85V32H165" stroke="#6099a7" stroke-width="12" fill="none"/><path d="M25 73V97M73 48H97M146 20V44" stroke="#407582" stroke-width="5"/></symbol>
    <symbol id="ps-rotor-shaft" viewBox="0 0 180 120"><path d="M8 60H172" stroke="#7c6896" stroke-width="3" stroke-dasharray="6 3"/><rect x="14" y="50" width="26" height="20" rx="2" class="ps-metal"/><rect x="40" y="42" width="100" height="36" rx="3" fill="#c7d6cc" stroke="#4c6b5b" stroke-width="2.5"/><rect x="140" y="50" width="26" height="20" rx="2" class="ps-metal"/><rect x="52" y="47" width="76" height="8" rx="2" fill="#7c9688"/><path d="M48 42V78M132 42V78M22 50V70M158 50V70" stroke="#4c6b5b" stroke-width="2"/><circle cx="27" cy="60" r="5" class="ps-wheel"/><circle cx="153" cy="60" r="5" class="ps-wheel"/></symbol>
    <symbol id="ps-rotor-disc" viewBox="0 0 180 120"><path d="M12 64H168" stroke="#5b7667" stroke-width="8"/><ellipse cx="48" cy="64" rx="14" ry="42" fill="#c5d4c5" stroke="#4c6b5b" stroke-width="2.5"/><ellipse cx="76" cy="64" rx="12" ry="38" fill="#dce6db" stroke="#5b7a69" stroke-width="2"/><ellipse cx="104" cy="64" rx="12" ry="38" fill="#dce6db" stroke="#5b7a69" stroke-width="2"/><ellipse cx="132" cy="64" rx="14" ry="42" fill="#c5d4c5" stroke="#4c6b5b" stroke-width="2.5"/><circle cx="48" cy="34" r="4" fill="#3d5a4b"/><circle cx="48" cy="94" r="4" fill="#3d5a4b"/><circle cx="132" cy="34" r="4" fill="#3d5a4b"/><circle cx="132" cy="94" r="4" fill="#3d5a4b"/><path d="M36 34H144M36 94H144" stroke="#8b7954" stroke-width="3" stroke-dasharray="5 3"/></symbol>
    <symbol id="ps-suspension-bar" viewBox="0 0 180 120"><rect x="18" y="24" width="144" height="12" rx="5" fill="#d8c390" stroke="#7d683b" stroke-width="2"/><rect x="18" y="44" width="144" height="12" rx="5" fill="#e2cf9f" stroke="#7d683b" stroke-width="2"/><rect x="18" y="64" width="144" height="12" rx="5" fill="#d8c390" stroke="#7d683b" stroke-width="2"/><rect x="18" y="84" width="144" height="12" rx="5" fill="#cbb37b" stroke="#6e5a31" stroke-width="2" stroke-dasharray="8 2"/><path d="M30 18V102M150 18V102" stroke="#4f6d5c" stroke-width="5"/><circle cx="156" cy="90" r="5" fill="#99231b"/></symbol>
    <symbol id="ps-ring-hammer" viewBox="0 0 180 120"><path d="M16 44H164" stroke="#7d683b" stroke-width="7"/><circle cx="62" cy="64" r="32" fill="#d5bc84" stroke="#6e592f" stroke-width="3"/><circle cx="62" cy="64" r="14" fill="#f4f5ef" stroke="#6e592f" stroke-width="2.5"/><path d="M62 26L68 33L56 33ZM94 46L99 54L89 52ZM94 82L89 74L99 72ZM62 102L56 95L68 95ZM30 82L35 74L25 72ZM30 46L25 54L35 52Z" fill="#6e592f"/><circle cx="122" cy="64" r="30" fill="#c7d5c8" stroke="#4a6958" stroke-width="3"/><circle cx="122" cy="64" r="13" fill="#f4f5ef" stroke="#4a6958" stroke-width="2.5"/><circle cx="62" cy="44" r="5" fill="#7d683b"/><circle cx="122" cy="44" r="5" fill="#7d683b"/></symbol>
    <symbol id="ps-screen-plate" viewBox="0 0 180 120"><path d="M24 22Q32 96 154 98L162 76Q54 74 46 18Z" fill="#cedbd0" stroke="#4b6b59" stroke-width="2.5"/><path d="M36 42L56 36M44 60L64 52M58 76L76 64M78 88L92 72M102 94L112 76M128 96L134 78" stroke="#395747" stroke-width="5"/><circle cx="70" cy="78" r="3.5" fill="#f4f5ef"/><circle cx="90" cy="84" r="3.5" fill="#f4f5ef"/><circle cx="112" cy="88" r="3.5" fill="#f4f5ef"/><circle cx="134" cy="90" r="3.5" fill="#f4f5ef"/></symbol>
    <symbol id="ps-cage-adjuster" viewBox="0 0 180 120"><path d="M26 94L86 34" stroke="#537261" stroke-width="8"/><path d="M40 80L54 66L44 58L64 50L54 42L74 34" fill="none" stroke="#a68344" stroke-width="4"/><circle cx="122" cy="46" r="24" fill="#e2ebd9" stroke="#527260" stroke-width="3"/><circle cx="122" cy="46" r="7" class="ps-wheel"/><path d="M122 22V70M98 46H146" stroke="#527260" stroke-width="2.5"/><path d="M86 34H122M98 70L138 98" stroke="#6c8576" stroke-width="5"/></symbol>
    <symbol id="ps-wear-liner" viewBox="0 0 180 120"><rect x="20" y="22" width="66" height="36" rx="3" fill="#d8c596" stroke="#7c683c" stroke-width="2.5"/><rect x="92" y="22" width="66" height="36" rx="3" fill="#cdb682" stroke="#7c683c" stroke-width="2.5"/><rect x="20" y="64" width="66" height="36" rx="3" fill="#cdb682" stroke="#7c683c" stroke-width="2.5"/><rect x="92" y="64" width="66" height="36" rx="3" fill="#d8c596" stroke="#7c683c" stroke-width="2.5"/><g fill="#5b4b29"><circle cx="32" cy="34" r="3.5"/><circle cx="74" cy="34" r="3.5"/><circle cx="32" cy="46" r="3.5"/><circle cx="74" cy="46" r="3.5"/><circle cx="104" cy="34" r="3.5"/><circle cx="146" cy="34" r="3.5"/><circle cx="104" cy="46" r="3.5"/><circle cx="146" cy="46" r="3.5"/><circle cx="32" cy="76" r="3.5"/><circle cx="74" cy="76" r="3.5"/><circle cx="104" cy="76" r="3.5"/><circle cx="146" cy="76" r="3.5"/></g></symbol>
    <symbol id="ps-tramp-trap" viewBox="0 0 180 120"><path d="M24 22H122V50L156 58V98H56L24 68Z" fill="#d4e0d5" stroke="#4f6e5d" stroke-width="2.5"/><path d="M58 26L86 64L64 88" fill="none" stroke="#a67c38" stroke-width="4" stroke-dasharray="5 4"/><rect x="112" y="64" width="32" height="24" rx="3" fill="#cfa971" stroke="#7c5d2c" stroke-width="2"/><path d="M156 58L168 44" stroke="#4f6e5d" stroke-width="4"/></symbol>
    <symbol id="ps-spring-isolator" viewBox="0 0 180 120"><rect x="16" y="18" width="148" height="14" rx="3" class="ps-metal"/><rect x="16" y="94" width="148" height="12" rx="2" fill="#8fa495" stroke="#4c6958" stroke-width="2"/><path d="M34 32L52 41L28 51L52 61L28 71L52 81L34 94M84 32L102 41L78 51L102 61L78 71L102 81L84 94" fill="none" stroke="#3c624f" stroke-width="4.5" stroke-linejoin="round"/><rect x="122" y="36" width="26" height="58" rx="4" fill="#c7b385" stroke="#7a663b" stroke-width="2.5"/><path d="M135 18V46" stroke="#4c6958" stroke-width="5"/></symbol>
    <symbol id="ps-brake-shoe" viewBox="0 0 180 120"><circle cx="78" cy="60" r="30" class="ps-metal"/><circle cx="78" cy="60" r="10" class="ps-wheel"/><path d="M44 26Q22 60 44 94" fill="none" stroke="#9e6b32" stroke-width="10" stroke-linecap="round"/><path d="M112 26Q134 60 112 94" fill="none" stroke="#9e6b32" stroke-width="10" stroke-linecap="round"/><path d="M44 22H126L142 46" fill="none" stroke="#4e6c5b" stroke-width="4"/><rect x="132" y="46" width="24" height="44" rx="3" fill="#d8c390" stroke="#7d683b" stroke-width="2"/><path d="M24 102H158" stroke="#5b7667" stroke-width="4"/></symbol>
    <symbol id="ps-coupling-hub" viewBox="0 0 180 120"><path d="M10 60H170" stroke="#527264" stroke-width="9"/><rect x="44" y="26" width="92" height="68" rx="6" fill="#d5e1d6" stroke="#4c6b5b" stroke-width="2.5"/><rect x="56" y="38" width="30" height="44" rx="2" fill="#9eb4a4" stroke="#4c6b5b" stroke-width="2"/><rect x="94" y="38" width="30" height="44" rx="2" fill="#9eb4a4" stroke="#4c6b5b" stroke-width="2"/><path d="M56 38H124M56 82H124" stroke="#8b7954" stroke-width="4" stroke-dasharray="5 3"/><circle cx="90" cy="31" r="3" fill="#3b5949"/><circle cx="90" cy="89" r="3" fill="#3b5949"/></symbol>
    <symbol id="ps-hose-reel" viewBox="0 0 180 120"><circle cx="82" cy="56" r="38" fill="#d2e2e5" stroke="#437d89" stroke-width="3"/><circle cx="82" cy="56" r="26" fill="none" stroke="#49899c" stroke-width="6" stroke-dasharray="9 3"/><circle cx="82" cy="56" r="16" fill="none" stroke="#49899c" stroke-width="5" stroke-dasharray="6 3"/><circle cx="82" cy="56" r="7" class="ps-wheel"/><path d="M82 56L54 104H110Z" fill="#9eb4a2" stroke="#4c6b5b" stroke-width="2"/><path d="M116 38H158V78" fill="none" stroke="#49899c" stroke-width="6"/><circle cx="158" cy="84" r="9" fill="#dfc48a" stroke="#8b6f36" stroke-width="2"/></symbol>
    <symbol id="ps-grease-pump" viewBox="0 0 180 120"><rect x="44" y="18" width="68" height="52" rx="5" fill="#f3e5be" stroke="#94783e" stroke-width="2.5"/><path d="M46 46H110" stroke="#cfa968" stroke-width="3"/><path d="M78 24V66M62 56H94" stroke="#7d6431" stroke-width="3.5"/><rect x="38" y="70" width="80" height="32" rx="4" class="ps-metal"/><circle cx="136" cy="52" r="14" fill="#fff8e6" stroke="#8b6f36" stroke-width="2"/><path d="M136 52L143 44M118 82H162M118 92H162" stroke="#49899c" stroke-width="4"/></symbol>
    <symbol id="ps-changeover-valve" viewBox="0 0 180 120"><rect x="46" y="34" width="88" height="52" rx="6" fill="#d5e2df" stroke="#467682" stroke-width="2.5"/><rect x="22" y="44" width="24" height="32" rx="3" fill="#e6cfa0" stroke="#8b6f36" stroke-width="2"/><rect x="134" y="44" width="24" height="32" rx="3" fill="#e6cfa0" stroke="#8b6f36" stroke-width="2"/><path d="M90 12V34M68 86V108M112 86V108" stroke="#49899c" stroke-width="6"/><path d="M62 52L118 68M62 68L118 52" stroke="#386672" stroke-width="3"/><circle cx="68" cy="98" r="5" fill="#2c788c"/><circle cx="112" cy="98" r="5" fill="#9c7a38"/></symbol>
    <symbol id="ps-distributor-block" viewBox="0 0 180 120"><rect x="36" y="20" width="108" height="80" rx="5" fill="#d7e3da" stroke="#4d6d5c" stroke-width="2.5"/><path d="M36 40H144M36 60H144M36 80H144" stroke="#688776" stroke-width="2"/><g fill="#7d683b"><circle cx="56" cy="30" r="4"/><circle cx="56" cy="50" r="4"/><circle cx="56" cy="70" r="4"/><circle cx="56" cy="90" r="4"/><circle cx="124" cy="30" r="4"/><circle cx="124" cy="50" r="4"/><circle cx="124" cy="70" r="4"/><circle cx="124" cy="90" r="4"/></g><path d="M18 30H36M18 50H36M18 70H36M18 90H36M144 30H162M144 50H162M144 70H162M144 90H162" stroke="#49899c" stroke-width="3.5"/></symbol>
    <symbol id="ps-needle-rods" viewBox="0 0 180 120"><rect x="20" y="20" width="140" height="80" rx="4" fill="none" stroke="#4b6b59" stroke-width="5"/><path d="M34 24V96M48 24V96M62 24V96M76 24V96M90 24V96M104 24V96M118 24V96M132 24V96M146 24V96" stroke="#94783e" stroke-width="4" stroke-linecap="round"/><path d="M14 50H166M14 70H166" stroke="#5b7a69" stroke-width="3"/></symbol>
    <symbol id="ps-rack-pinion" viewBox="0 0 180 120"><rect x="20" y="68" width="140" height="16" rx="2" fill="#c7d5c8" stroke="#4a6958" stroke-width="2.5"/><path d="M28 68V60H36V68M44 68V60H52V68M60 68V60H68V68M76 68V60H84V68M92 68V60H100V68M108 68V60H116V68M124 68V60H132V68M140 68V60H148V68" fill="#4a6958"/><circle cx="90" cy="40" r="20" fill="#dfc48a" stroke="#7d6431" stroke-width="3" stroke-dasharray="6 3"/><circle cx="90" cy="40" r="7" class="ps-wheel"/><path d="M24 94H156" stroke="#6c8576" stroke-width="4"/></symbol>
    <symbol id="ps-electromagnet" viewBox="0 0 180 120"><path d="M52 10V28M128 10V28" stroke="#527264" stroke-width="4"/><rect x="34" y="26" width="112" height="44" rx="6" fill="#d9c087" stroke="#7d622b" stroke-width="2.5"/><rect x="48" y="34" width="84" height="28" rx="3" fill="#b84b39" stroke="#7a281b" stroke-width="2"/><path d="M22 50L34 38M158 50L146 38M22 50H158" stroke="#3c5e4e" stroke-width="4"/><path d="M54 76Q90 102 126 76M68 86Q90 108 112 86" fill="none" stroke="#b84b39" stroke-width="3" stroke-dasharray="4 3"/><path d="M14 102H166" stroke="#2e5343" stroke-width="6"/></symbol>
    <symbol id="ps-radiation-source" viewBox="0 0 180 120"><rect x="44" y="12" width="92" height="26" rx="4" fill="#c7d8d6" stroke="#426e78" stroke-width="2.5"/><path d="M18 58H162" stroke="#2e5343" stroke-width="8"/><path d="M68 40L90 74L112 40M78 40L90 74L102 40" fill="none" stroke="#c48a2b" stroke-width="2.5" stroke-dasharray="3 3"/><rect x="52" y="76" width="76" height="32" rx="6" fill="#efd8a4" stroke="#8c6d2e" stroke-width="2.5"/><circle cx="90" cy="92" r="9" fill="#99231b"/><circle cx="90" cy="92" r="3" fill="#efd8a4"/></symbol>
    <symbol id="ps-search-coil" viewBox="0 0 180 120"><polygon points="36,34 144,34 162,54 18,54" fill="none" stroke="#9a7d42" stroke-width="4"/><polygon points="36,72 144,72 162,92 18,92" fill="none" stroke="#9a7d42" stroke-width="4"/><path d="M12 63H168" stroke="#2e5343" stroke-width="7"/><path d="M58 44Q90 63 122 44M58 82Q90 63 122 82" fill="none" stroke="#49899c" stroke-width="2.5" stroke-dasharray="4 3"/></symbol>
    <symbol id="ps-sprag-holdback" viewBox="0 0 180 120"><circle cx="90" cy="56" r="36" fill="#d5e1d6" stroke="#4c6b5b" stroke-width="3"/><circle cx="90" cy="56" r="18" fill="#ebd49e" stroke="#7d6431" stroke-width="2.5"/><path d="M90 20L96 36M126 56L110 62M90 92L84 76M54 56L70 50" stroke="#4c6b5b" stroke-width="3.5"/><path d="M122 72L156 102H116Z" fill="#9eb4a2" stroke="#4c6b5b" stroke-width="2"/></symbol>
    <symbol id="ps-impeller" viewBox="0 0 180 120"><path d="M84 12V46M96 12V46" stroke="#49899c" stroke-width="4"/><path d="M44 46H136L148 78H32Z" fill="#c1d9d9" stroke="#437d89" stroke-width="2.5"/><path d="M62 54Q90 72 118 54M54 68Q90 86 126 68" fill="none" stroke="#356873" stroke-width="3.5"/><rect x="48" y="78" width="84" height="24" rx="3" fill="#dce8e6" stroke="#437d89" stroke-width="2" stroke-dasharray="4 2"/></symbol>
    <symbol id="ps-elevator-car" viewBox="0 0 180 120"><path d="M38 10V110M142 10V110" stroke="#5b7667" stroke-width="4"/><rect x="52" y="28" width="60" height="68" rx="4" class="ps-metal"/><rect x="60" y="38" width="44" height="24" class="ps-window"/><rect x="122" y="44" width="14" height="40" rx="2" fill="#8b7954" stroke="#5c4d2e" stroke-width="2"/><path d="M82 10V28M129 10V44" stroke="#4c6b5b" stroke-width="2.5"/></symbol>
  </defs>`;}
  function nodeMatchesLayer(n,layer){
    if(!layer||layer==='all')return true;
    const k=n.kind||'',l=(n.label||'').toLowerCase();
    if(layer==='material')return ['conveyor','feeder','chute','gate','silo','bunker','bunker-bay','pile','stacker','reclaimer','ship','screen','crusher','extractor','tripper','sampler','collector','screw-conveyor','airlock'].includes(k);
    if(layer==='mechanical')return ['drive','motor','coupling','shaft-coupling','gearbox','pulley','brake','thruster','idler','scraper','takeup','counterweight','bearing','blade','cone','platform','crusher-rotor','cage','exciter','hoist','bogie','rail-clamp','slew','trolley','boom','grab'].includes(k)||/drive|motor|gearbox|pulley|coupling|brake|idler|take-up|bearing|rotor/i.test(l);
    if(layer==='utility')return ['spray','spray-system','water','pump','tank','filter','pipe','valve','compressor','dryer','receiver','lubrication','hydraulic','cylinder','cooler','cyclone','de-house','de-stream','fan','duct','damper'].includes(k)||/water|spray|dfds|dust|sump|pump|lube|hydraulic|air|vent/i.test(l);
    if(layer==='electrical')return ['motor','switchboard','cable-reel','panel'].includes(k)||/motor|vfd|switchboard|mcc|power|transformer|cable|feeder panel/i.test(l);
    if(layer==='control')return ['sensor','level-sensor','protection','detector','weigher','panel','actuator'].includes(k)||/control|sensor|switch|pcs|bss|zss|weigher|detector|probe|plc|interlock|monitoring/i.test(l);
    return true;
  }
  function hotspot(n,x,y,w=160,height=106,opts={}){
    const labels=lines(opts.label||short(n),opts.max||26),selected=h()===n.id;
    const above=n.kind==='shed'&&s.kind==='yard'&&q().get('spread')!=='1',labelY=above?-15:height+17;
    const partCount=(p.children.get(n.id)||[]).filter(a=>!p.refs.has(a.canonical_subject)).length;
    const canOpen=n.id!==s.id&&n.role!=='self';
    const resolveNodeVisual=node=>{
      const l=node.label||'',k=node.kind||'assembly';
      if(k==='ship'||/^Coal Ship Unloader/i.test(l))return {sym:'ship',label:'grab unloader'};
      if(/^Coal Jetty$/i.test(l))return {sym:'jetty',label:'marine berth'};
      if(/shuttle conveyor/i.test(l))return {sym:'shuttle-conveyor',label:'shuttle belt'};
      if(/vibro-feeder|vibrating grizzly feeder|vibrating feeder|\bvgf-/i.test(l)){
        if(/lining/i.test(l))return {sym:'wear-liner',label:'wear liner'};
        if(/suspension spring/i.test(l))return {sym:'spring-isolator',label:'coil spring'};
        if(/trough and Grizzly/i.test(l))return {sym:'grizzly-grid',label:'grizzly trough'};
        return {sym:'vibro-feeder',label:'vibro-feeder'};
      }
      if(/receiving hopper|surge hopper|weigh hopper|collecting hopper|reject bin/i.test(l)){
        if(/grizzly grid/i.test(l)&&!/receiving hopper.*assembly/i.test(l))return {sym:'grizzly-grid',label:'grizzly grid'};
        if(/\bgate\b/i.test(l)&&!/grizzly and regulating gate|spillage-flap\/gate|receiving hopper.*assembly/i.test(l))return {sym:'rack-pinion',label:'hopper gate'};
        if(/spillage flap/i.test(l)&&!/receiving hopper.*assembly/i.test(l))return {sym:'gate',label:'spillage flap'};
        return {sym:'hopper',label:'receiving hopper'};
      }
      if(/grizzly grid|protective grid/i.test(l))return {sym:'grizzly-grid',label:'grizzly grid'};
      if(/rack-and-pinion|pinion-and-crown|open gear pinion/i.test(l))return {sym:'rack-pinion',label:'rack & pinion'};
      if(/transformer|\b00BBT|\b00BFT/i.test(l)&&!/rectifier/i.test(l))return {sym:'transformer',label:'transformer'};
      if(/diesel-generator|emergency dg/i.test(l))return {sym:'dg-set',label:'diesel generator'};
      if(/anemometer|wind speed/i.test(l))return {sym:'anemometer',label:'anemometer'};
      if(/spray-header group downstream PRU-/i.test(l))return {sym:'spray',label:'spray header'};
      if(/PRU-\d+[A-Z]?\s+Air regulating branch/i.test(l))return {sym:'pipe',label:'air branch'};
      if(/PRU-\d+[A-Z]?\s+Water regulating branch/i.test(l))return {sym:'water',label:'water branch'};
      if(/\bPRU-\d+/i.test(l))return {sym:'pru',label:'pressure reg unit'};
      if(/\bFAS-\d+|pressurization.*ventilation|pressure ventilation/i.test(l))return {sym:'fas',label:'air supply unit'};
      if(/air conditioning/i.test(l)&&k==='assembly')return {sym:'cooler',label:'hvac cooling'};
      if(/bulldozer|\bBD355|coal dozer/i.test(l))return {sym:'bulldozer',label:'coal bulldozer'};
      if(/wheel loader|pay\s*loader|front[- ]end.*loader|\bBL200|\bBL40/i.test(l))return {sym:'loader',label:'wheel loader'};
      if(/vacuum cleaning|\bVAC-2100/i.test(l))return {sym:'vacuum',label:'vacuum system'};
      if(/scraper chain|flight blade|sprocket|chain tensioner|chain guide/i.test(l))return {sym:'scraper-chain',label:'scraper chain'};
      if(/buffer|end-stop|bump stop/i.test(l))return {sym:'buffer',label:'impact buffer'};
      if(/storm anchor|tie-down|anchoring bracket|locking pin/i.test(l))return {sym:'rail-clamp',label:'storm anchor'};
      if(/silo extract|\bRE-1\b|\bRE-2\b/i.test(l)&&k==='assembly')return {sym:'extractor',label:'rotary extractor'};
      if(/run-off pond|runoff collection|service water|potable water|drinking.*water|hose box|washdown|SW & PW/i.test(l)&&k==='assembly')return {sym:'water',label:'water service'};
      if(/grease lubrication/i.test(l)&&k==='assembly')return {sym:'lubrication',label:'grease lubrication'};
      if(/temperature transmitter|\bTT1\b/i.test(l)&&k==='assembly')return {sym:'sensor',label:'temp transmitter'};
      if(/pressure relief and recirculation/i.test(l)&&k==='assembly')return {sym:'valve',label:'pressure relief'};
      if(/solenoid box/i.test(l)&&k==='assembly')return {sym:'panel',label:'solenoid box'};
      if(/crossover damper/i.test(l)&&k==='assembly')return {sym:'damper',label:'crossover damper'};
      if(/compressed-air supply train/i.test(l)&&k==='assembly')return {sym:'compressor',label:'compressed air'};
      if(/starter panel|vfd.*panel/i.test(l)&&k==='assembly')return {sym:'switchboard',label:'starter panel'};
      if(/houses, cabins|machinery house|electrical house|operator cabin/i.test(l)&&k==='assembly')return {sym:'cabin',label:'enclosure house'};
      if(/portal and bridge|gantry structure|support portal|portal frame|support frame|support legs|steel structure/i.test(l)&&k==='assembly')return {sym:'reclaimer',label:'portal structure'};
      if(/travelling carriage|carriage frame|sample container carousel/i.test(l))return {sym:'trolley',label:'carriage'};
      if(/lifting arrangement|chain pulley block|maintenance hoist|wire rope and hook|sheave block|rope drum/i.test(l))return {sym:'hoist',label:'hoist gear'};
      if(/sample crusher/i.test(l))return {sym:'crusher',label:'sample crusher'};
      if(/primary cutter|secondary cutter|rotary disc divider/i.test(l))return {sym:'sampler',label:'sample cutter'};
      if(/dosing feeder|belt feeder/i.test(l)&&k==='assembly')return {sym:'feeder',label:'belt feeder'};
      if(/equalizer beam|wheel block|bogie/i.test(l)&&k==='assembly')return {sym:'bogie',label:'bogie gear'};
      if(/take-up|turnbuckle/i.test(l)&&k==='assembly')return {sym:'takeup',label:'take-up'};
      if(/skirtboard|sealing strip|dust curtain|rubber seal/i.test(l)&&k==='assembly')return {sym:'scraper',label:'skirtboard seal'};
      if(/liner|hardox|wear plate|impact plate|wearing plate/i.test(l)&&k==='assembly')return {sym:'wear-liner',label:'wear liner'};
      if(/test weight|calibration weight|counterweight/i.test(l)&&k==='assembly')return {sym:'counterweight',label:'test weight'};
      if(/evidence gap|ledger|isolation boundary|boundary group|decision register|disposition group|verification index|backbone index|release certificate|hand-off register|candidate group|qualification/i.test(l)&&k==='assembly')return {sym:'reference',label:'reference dossier'};
      if(/^Maitree Coal Handling Plant$/i.test(l))return {sym:'transfer',label:'coal handling plant'};
      if(k==='drive')return {sym:M.driveSymbol(p,node.id),label:'drive'};
      if(k==='coupling'&&/low.speed|geared coupling|flexible coupling/i.test(l))return {sym:'shaft-coupling',label:'shaft coupling'};
      return {sym:k,label:nice(k)};
    };
    const vis=resolveNodeVisual(n);
    const kindLabel=vis.label;const hint=opts.sub||(n.role==='located'?'located here':n.role==='connected'?'connected '+kindLabel:kindLabel+(partCount?' · '+partCount+' parts ↗':''));
    const activeFloor=q().get('floor');
    const inFloor=!activeFloor||activeFloor==='all'||!activeFloorBounds||(y+height/2>=activeFloorBounds.yMin&&y+height/2<=activeFloorBounds.yMax);
    const layer=q().get('layer')||'all';
    const edgeEndpoints=s._activeLayerEndpoints;
    const inLayer=layer==='all'||(edgeEndpoints&&edgeEndpoints.has(n.id))||nodeMatchesLayer(n,layer);
    const inRouteStream=!s._routeStreamNodes||!s._routeStreamNodes.has(n.id)||(s._activeRouteNodes&&s._activeRouteNodes.has(n.id));
    const dimClass=(!inFloor||!inLayer)?'ps-dimmed-node':(!inRouteStream?'ps-stream-dimmed':'');
    const matchClass=(layer!=='all'&&inLayer)?'ps-xray-match':(s._activeRouteNodes&&s._activeRouteNodes.has(n.id)?'ps-stream-active':'');
    const openBadge=canOpen?`<g class="ps-open-pill" data-action="scene-open" data-id="${safe(n.id)}" role="button" tabindex="-1" aria-label="Open ${safe(n.label)} schematic"><rect x="${w-48}" y="-6" width="54" height="18" rx="9"/><text x="${w-21}" y="6" text-anchor="middle">Open ↗</text></g>`:'';
    return `<g class="ps-hotspot ${selected?'is-selected':''} ${n.role==='connected'?'ps-external':''} ${dimClass} ${matchClass}" data-node="${safe(n.id)}" data-action="scene-pick" data-id="${safe(n.id)}" data-x="${x}" data-y="${y}" data-w="${w}" data-h="${height}" tabindex="0" role="button" aria-label="Inspect ${safe(n.label)}" transform="translate(${x} ${y})"><title>${safe(n.label)} · ${canOpen?'Click to inspect, double-click or click Open ↗ to enter assembly':'Select to inspect'}</title><rect class="ps-halo" x="-10" y="-8" width="${w+20}" height="${height+labels.length*18+24}" rx="16"/>${symbol(vis.sym,0,0,w,height)}${openBadge}${labels.map((t,i)=>text(w/2,labelY+i*18,t)).join('')}${text(w/2,above?-33:height+20+labels.length*18,hint,'ps-node-hint')}</g>`;
  }
  function isIsoStack(){
    return q().get('iso')!=='0'&&['crusher-house','silo-house','sampler-system','transfer','screenhouse'].includes(s?.kind);
  }
  function isoDeckSVG(decks,frameX,frameW,wellXs=[]){
    const iso=isIsoStack();
    const activeFloor=q().get('floor')||'all';
    const found=decks.find(d=>d.key===activeFloor);
    activeFloorBounds=found?{yMin:found.yMin,yMax:found.yMax,y:found.y,h:found.h}:null;
    s._sceneDecks=decks;
    if(!iso)return '';
    const dx=28,dy=16;
    const topY=decks[0].y,botY=decks[decks.length-1].y+decks[decks.length-1].h;
    const pillars=[
      `<path class="ps-iso-pillar" d="M${frameX} ${topY}V${botY}M${frameX+frameW} ${topY}V${botY}M${frameX+dx} ${topY-dy}V${botY-dy}M${frameX+frameW+dx} ${topY-dy}V${botY-dy}"/>`
    ];
    const slabs=decks.map((d,idx)=>{
      const isFocused=activeFloor===d.key;
      const isDim=activeFloor!=='all'&&!isFocused;
      const x=frameX,y=d.y,w=frameW,h=d.h;
      const topFace=`M${x} ${y}L${x+dx} ${y-dy}H${x+w+dx}L${x+w} ${y}Z`;
      const mainFace=`M${x} ${y}H${x+w}V${y+h}H${x}Z`;
      const sideFace=`M${x+w} ${y}L${x+w+dx} ${y-dy}V${y+h-dy}L${x+w} ${y+h}Z`;
      const frontLip=`M${x} ${y+h}H${x+w}V${y+h+7}H${x}Z`;
      const wells=wellXs.map(wx=>`<ellipse class="ps-iso-well" cx="${wx}" cy="${y+h-18}" rx="46" ry="11"/>`).join('');
      const badgeW=142,badgeX=x-badgeW-10,badgeY=y+Math.round(h/2)-20;
      const nextKey=isFocused?null:d.key;
      return `<g class="ps-iso-deck ${isFocused?'is-focused':''} ${isDim?'is-dimmed':''}" data-action="scene-floor" data-floor="${safe(nextKey||'all')}" role="button" tabindex="0" aria-label="Isolate floor ${safe(d.elev+' '+d.title)}"><path class="ps-iso-top" d="${topFace}"/><path class="ps-iso-face" d="${mainFace}"/><path class="ps-iso-side" d="${sideFace}"/><path class="ps-iso-lip" d="${frontLip}"/>${wells}<g class="ps-iso-badge" transform="translate(${badgeX} ${badgeY})"><rect x="0" y="0" width="${badgeW}" height="38" rx="8"/><text x="10" y="15" class="ps-iso-elev">${safe(d.elev)}</text><text x="10" y="30" class="ps-iso-name">${safe(d.title)}</text></g></g>`;
    });
    return pillars.join('')+slabs.join('');
  }
  function xrayExtraEdges(positions,alreadyDrawn){
    const layer=q().get('layer')||'all';
    if(layer==='all')return [];
    const byId=new Map(s.nodes.map(n=>[n.id,n]));
    const drawnKeys=new Set((alreadyDrawn||[]).map(a=>a.id||`${a.canonical_subject}>${a.canonical_object}|${a.context?.network}`));
    return s.edges.filter(a=>{
      if(a.context?.network!==layer)return false;
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      const nu=byId.get(u),nv=byId.get(v);
      if(nu&&['mechanical','assembly','protection'].includes(nu.kind)||nv&&['mechanical','assembly','protection'].includes(nv.kind))return false;
      const pu=positions.get(u),pv=positions.get(v);
      if(Math.abs(pu.y-pv.y)>240)return false;
      const key=a.id||`${u}>${v}|${layer}`;
      return !drawnKeys.has(key);
    });
  }
  function orthoStep(x1,y1,x2,y2,midY){
    if(Math.abs(x1-x2)<4)return `M${x1} ${y1}L${x2} ${y2}`;
    const clampedMid=Math.max(Math.min(y1,y2)+8,Math.min(Math.max(y1,y2)-8,midY));
    const r=Math.min(8,Math.abs(x2-x1)/2,Math.abs(clampedMid-y1)/2,Math.abs(y2-clampedMid)/2);
    if(r<2)return `M${x1} ${y1}V${clampedMid}H${x2}V${y2}`;
    const sx=x2>x1?1:-1,sy1=clampedMid>y1?1:-1,sy2=y2>clampedMid?1:-1;
    return `M${x1} ${y1}V${clampedMid-sy1*r}Q${x1} ${clampedMid} ${x1+sx*r} ${clampedMid}H${x2-sx*r}Q${x2} ${clampedMid} ${x2} ${clampedMid+sy2*r}V${y2}`;
  }
  function chuteStep(x1,y1,x2,y2){
    if(Math.abs(x1-x2)<4)return `M${x1} ${y1}L${x2} ${y2}`;
    const dy=y2-y1;
    if(dy<26)return orthoStep(x1,y1,x2,y2,Math.round((y1+y2)/2));
    const stub1=Math.min(11,Math.round(dy*0.18)),stub2=Math.min(13,Math.round(dy*0.22));
    const yA=y1+stub1,yB=y2-stub2;
    return `M${x1} ${y1}L${x1} ${yA}L${x2} ${yB}L${x2} ${y2}`;
  }
  function smartRoute(a,b,positions,idx=0,portOffsets=null){
    const all=[...positions.values()];
    const sameRow=Math.abs(a.y-b.y)<=32;
    if(sameRow){
      const minX=Math.min(a.x+a.w,b.x+b.w),maxX=Math.max(a.x,b.x);
      const blocked=all.some(c=>c!==a&&c!==b&&Math.abs(c.y-a.y)<=32&&c.x+c.w>minX+8&&c.x<maxX-8);
      if(!blocked){
        const right=b.x>=a.x;
        const x1=right?a.x+a.w+2:a.x-2,x2=right?b.x-4:b.x+b.w+4,y=Math.round((a.y+a.h/2+b.y+b.h/2)/2);
        return `M${x1} ${y}L${x2} ${y}`;
      }
      const ux=Math.round(a.x+a.w/2),vx=Math.round(b.x+b.w/2),uy=a.y-4,vy=b.y-6,chY=Math.min(a.y,b.y)-18-(idx%2)*8;
      return orthoStep(ux,uy,vx,vy,chY);
    }
    if(b.y>a.y+32){
      const ux=Math.round(a.x+a.w/2+(portOffsets?.dx1||0));
      const uy=a.y+a.h+(portOffsets?.yPad??40);
      const vx=Math.round(b.x+b.w/2+(portOffsets?.dx2||0));
      const vy=b.y-6;
      if(b.y-a.y<=245){
        return chuteStep(ux,uy,vx,vy);
      }
      const minX=Math.min(...all.map(c=>c.x)),maxX=Math.max(...all.map(c=>c.x+c.w));
      const useLeft=(ux+vx)/2<(minX+maxX)/2;
      const gx=useLeft?Math.max(18,minX-24-(idx%3)*8):Math.min(1182,maxX+24+(idx%3)*8);
      const yExit=uy+10,yEnter=vy-14;
      return `M${ux} ${uy}V${yExit}H${gx}V${yEnter}H${vx}V${vy}`;
    }
    const ux=Math.round(a.x+a.w/2),uy=a.y-4,vx=Math.round(b.x+b.w/2),vy=b.y+b.h+42;
    if(a.y-b.y<=225){
      return chuteStep(ux,uy,vx,vy);
    }
    const minX=Math.min(...all.map(c=>c.x)),maxX=Math.max(...all.map(c=>c.x+c.w));
    const useLeft=(ux+vx)/2<(minX+maxX)/2;
    const gx=useLeft?Math.max(18,minX-24-(idx%3)*8):Math.min(1182,maxX+24+(idx%3)*8);
    return `M${ux} ${uy}V${uy-12}H${gx}V${vy+12}H${vx}V${vy}`;
  }
  function routePath(a,b){return Math.abs(b.y-a.y)<25?`M${a.x} ${a.y}L${b.x} ${b.y}`:chuteStep(a.x,a.y,b.x,b.y);}
  function shortEdgeTag(pred,net){
    const p=String(pred||'').toLowerCase();
    if(p==='drives'||p==='mechanically_drives')return 'drives';
    if(p==='couples_to')return 'couples';
    if(p==='acts_on'||p==='brakes')return p==='brakes'?'brakes':'acts on';
    if(p==='supports')return 'supports';
    if(p==='monitors_equipment')return 'monitors';
    if(p==='control_signal_to'||p==='protects_equipment')return 'interlock';
    if(p==='electrical_supply_to'||p==='electrical_feed_to'||p==='electrically_feeds')return 'power';
    if(p==='sprays_at')return 'sprays';
    if(p==='lubricates')return 'lube';
    if(p==='hydraulic_flow_to')return 'hydraulic';
    if(p==='utility_supply_to'||p==='supplies_water_to')return 'supply';
    if(net==='material')return 'coal flow';
    return nice(p||net).slice(0,12);
  }
  function edgeMidpoint(a,b,portOffsets=null){
    if(Math.abs(a.y-b.y)<=32){
      const right=b.x>=a.x;
      const x1=right?a.x+a.w+2:a.x-2,x2=right?b.x-4:b.x+b.w+4;
      return {x:Math.round((x1+x2)/2),y:Math.round((a.y+a.h/2+b.y+b.h/2)/2)-8};
    }
    const ux=Math.round(a.x+a.w/2+(portOffsets?.dx1||0)),vx=Math.round(b.x+b.w/2+(portOffsets?.dx2||0));
    const uy=b.y>a.y?a.y+a.h+(portOffsets?.yPad??40):a.y-4,vy=b.y>a.y?b.y-6:b.y+b.h+42;
    return {x:Math.round((ux+vx)/2),y:Math.round((uy+vy)/2)-4};
  }
  function edgeMarkup(edges,positions,routes=new Map(),fromOverride=null,allEdgesForPorts=null){
    const getFromBox=(u,v)=>fromOverride?fromOverride(u,v):positions.get(u);
    const grouped=M.groupEdges(edges),seenCoord=new Set();
    const uniqueVisual=grouped.filter(e=>{
      const a=getFromBox(e.from,e.to),b=positions.get(e.to);if(!a||!b||a===b)return false;
      const dupKey=[a.x,a.y,b.x,b.y,e.network].join('|');
      if(seenCoord.has(dupKey))return false;
      seenCoord.add(dupKey);return true;
    });
    const portBasis=allEdgesForPorts?M.groupEdges(allEdgesForPorts).filter(e=>{const a=getFromBox(e.from,e.to),b=positions.get(e.to);return a&&b&&a!==b;}):uniqueVisual;

    // Compute multi-port exit (dx1) and entry (dx2) fan-out offsets for all downward inter-row connections
    // so dual-leg flap gates (FG-1, FG-2, etc.) exit from distinct left/right spouts and dual-inlet
    // conveyors receive separate arrowheads without lines ever merging!
    const outBySource=new Map(),inByTarget=new Map();
    for(const e of portBasis){
      const a=getFromBox(e.from,e.to),b=positions.get(e.to);
      if(!a||!b||b.y<=a.y+32||b.y-a.y>245)continue;
      const sk=`${a.x},${a.y}`,tk=`${b.x},${b.y}`;
      if(!outBySource.has(sk))outBySource.set(sk,[]);
      outBySource.get(sk).push({e,a,b});
      if(!inByTarget.has(tk))inByTarget.set(tk,[]);
      inByTarget.get(tk).push({e,a,b});
    }
    const portMap=new Map();
    for(const list of outBySource.values()){
      list.sort((x,y)=>(x.b.x+x.b.w/2)-(y.b.x+y.b.w/2));
      const n=list.length,w=list[0].a.w;
      const step=n>1?Math.min(34,Math.max(18,Math.floor((w-42)/(n-1)))):0;
      list.forEach((item,i)=>{
        const key=item.e.from+'>'+item.e.to+'|'+item.e.network;
        const prev=portMap.get(key)||{};
        prev.dx1=Math.round((i-(n-1)/2)*step);
        portMap.set(key,prev);
      });
    }
    for(const list of inByTarget.values()){
      list.sort((x,y)=>(x.a.x+x.a.w/2)-(y.a.x+y.a.w/2));
      const n=list.length,w=list[0].b.w;
      const step=n>1?Math.min(34,Math.max(18,Math.floor((w-42)/(n-1)))):0;
      list.forEach((item,i)=>{
        const key=item.e.from+'>'+item.e.to+'|'+item.e.network;
        const prev=portMap.get(key)||{};
        prev.dx2=Math.round((i-(n-1)/2)*step);
        portMap.set(key,prev);
      });
    }

    const showPills=uniqueVisual.length<=10&&s.kind!=='plant'&&s.kind!=='area';
    return uniqueVisual.map((e,idx)=>{
      const a=getFromBox(e.from,e.to),b=positions.get(e.to);if(!a||!b||a===b)return '';
      const net=e.network,layer=q().get('layer')||'all';if(layer!=='all'&&net!==layer)return '';
      const po=portMap.get(e.from+'>'+e.to+'|'+e.network)||null;
      const d=routes.get(e.from+'>'+e.to)||(e.from===e.to?`M${a.x+a.w} ${a.y+a.h/2}C${a.x+a.w+55} ${a.y+a.h/2} ${a.x+a.w+55} ${a.y-25} ${a.x+a.w/2} ${a.y-25}V${a.y}`:smartRoute(a,b,positions,idx,po));
      const predLabel=nice(e.facts[0]?.predicate||net);
      const tag=shortEdgeTag(e.facts[0]?.predicate,net);
      const mp=edgeMidpoint(a,b,po);
      const clearGap=b.x>=a.x?b.x-(a.x+a.w):a.x-(b.x+b.w);
      const pillW=tag.length*6.8+12;
      const showThisPill=showPills&&Math.abs(a.y-b.y)<=32&&clearGap>=pillW+22;
      const strokeColor=net==='utility'?'#5996a7':net==='mechanical'?'#8d77a6':net==='electrical'?'#507ba1':net==='control'?'#a5964b':'#ae844b';
      const strokeW=net==='mechanical'?'3':'2.5';
      const pill=`<g class="ps-edge-pill ${showThisPill?'is-visible':''}" transform="translate(${mp.x} ${mp.y})"><rect x="${-pillW/2}" y="-9" width="${pillW}" height="15" rx="7"/><text x="0" y="2" text-anchor="middle">${safe(tag)}</text></g>`;
      return `<g class="ps-edge ps-edge-${safe(net)}" data-from="${safe(e.from)}" data-to="${safe(e.to)}"><path class="ps-edge-line" fill="none" stroke="${strokeColor}" stroke-width="${strokeW}" stroke-linejoin="round" d="${d}" marker-end="url(#ps-${net==='utility'?'water-':net==='mechanical'?'drive-':net==='electrical'?'power-':''}arrow)"/><path class="ps-edge-hit" fill="none" d="${d}" data-action="scene-edge" data-id="${safe(e.facts[0].id)}" tabindex="0" role="button" aria-label="Inspect ${safe(p.entities.get(e.from)?.label)} to ${safe(p.entities.get(e.to)?.label)} connection"><title>${safe(p.entities.get(e.from)?.label)} → ${safe(p.entities.get(e.to)?.label)} (${safe(predLabel)})</title></path>${pill}</g>`;
    }).join('');
  }
  function plant(){
    const stageKinds=['ship','screen','transfer','yard','conveyor','silo','crusher','conveyor','silo'];
    const pos=new Map(p.stages.map(st=>[st.id,{x:105+(st.col-1)*375,y:26+(st.row-1)*210,w:180,h:110}]));
    const path=p.paths.find(x=>x.id===q().get('path'));
    let paths=p.links.map(l=>{
      const a=pos.get(l.from),b=pos.get(l.to);if(!a||!b)return '';
      let d;
      if(a.y===b.y)d=routePath({x:a.x+(b.x>a.x?202:-22),y:a.y+72},{x:b.x+(b.x>a.x?-22:202),y:b.y+72});
      else if(a.x===b.x)d=`M${a.x+90} ${a.y+182}V${b.y-12}`;
      else d=`M${a.x+202} ${a.y+105}H${a.x+242}V${b.y-22}H${b.x+90}V${b.y-12}`;
      const inRoute=!path||(path.stages.includes(l.from)&&path.stages.includes(l.to));
      const edgeCls=path?(inRoute?'ps-route-edge-active':'ps-dimmed'):'';
      return `<g class="ps-edge ps-edge-material ${edgeCls}"><path d="${d}" marker-end="url(#ps-arrow)"/><path d="${d}" class="ps-edge-hit" data-action="plant-branch" data-id="${l.id}" tabindex="0" role="button" aria-label="Inspect ${safe(l.from)} to ${safe(l.to)} flow"/></g>`;
    }).join('');
    if(q().get('layer')&&!['all','material'].includes(q().get('layer')))paths='';
    s.width=1200;s.height=665;s.initialHeight=665;
    const cards=p.stages.map((st,i)=>{
      const posn=pos.get(st.id);
      const inStage=!path||path.stages.includes(st.id);
      const stCls=path?(inStage?'ps-route-stage-active':'ps-dimmed'):'';
      return `<a href="${areaURL(st.id)}" class="ps-stage-scene ${stCls}" aria-label="Explore ${safe(st.title)}"><g transform="translate(${posn.x} ${posn.y})"><rect class="ps-halo" x="-18" y="-8" width="216" height="186" rx="18"/>${text(-6,14,String(st.number).padStart(2,'0'),'ps-stage-index','start')}${symbol(stageKinds[i],0,0,180,112)}${text(90,136,st.title,'ps-stage-title')}${text(90,154,st.tags,'ps-stage-tags')}${text(90,171,path&&inStage?'Active in Path '+path.id+' · Explore →':'Explore area →','ps-node-hint')}</g></a>`;
    }).join('');
    return cards+paths;
  }
  function routeSummaryBanner(){
    if(s.kind!=='plant')return '';
    const path=p.paths.find(x=>x.id===q().get('path'));
    if(!path)return '';
    const numFact=path.facts.find(a=>a.predicate==='design_numeric_requirement');
    const activeStages=p.stages.filter(st=>path.stages.includes(st.id));
    const stageEntityIds=new Set(activeStages.flatMap(st=>st.entities.map(e=>e.id)));
    let minCap=Infinity,maxCap=-Infinity,minEquip=null,minFact=null;
    for(const eid of stageEntityIds){
      if(!PlantExplorerModel.isPrimaryEquipment(p,eid))continue;
      const cls=p.classes.get(eid)||[];
      if(!cls.some(c=>/belt_conveyor|ship_unloader|stacker|reclaimer|ring_granulator|roller_screen/.test(c)))continue;
      for(const a of (p.outgoing.get(eid)||[])){
        if(a.predicate==='rated_capacity'&&typeof a.value==='number'&&/t\/h|tph/i.test(a.unit||'')){
          if(a.value>=400&&a.value<minCap){minCap=a.value;minEquip=p.entities.get(eid);minFact=a;}
          if(a.value>maxCap)maxCap=a.value;
        }
      }
    }
    const bottleneckHtml=Number.isFinite(minCap)&&minEquip?`<span class="ps-route-limit" title="Lowest rated primary stream equipment along active stages">Bottleneck: <strong>${minCap}${maxCap>minCap?'–'+maxCap:''} t/h</strong> (${safe(minEquip.label)}) ${source(minFact)}</span>`:(numFact?`<span class="ps-route-limit"><strong>${safe(numFact.value)}${numFact.unit?' '+safe(numFact.unit):' t/h'}</strong> (${safe(numFact.context?.condition||'rated flow')}) ${source(numFact)}</span>`:'');
    const allEvents=(typeof state!=='undefined'&&Array.isArray(state?.events))?state.events:[];
    const openRouteEvents=allEvents.filter(ev=>ev.current_status==='open'&&stageEntityIds.has(ev.canonical_equipment));
    const alertHtml=openRouteEvents.length?`<a href="#desk" class="ps-route-alert">⚠ ${openRouteEvents.length} open issue${openRouteEvents.length===1?'':'s'} on route</a>`:'';
    return `<div class="ps-active-route-banner" role="region" aria-label="Selected operating route details"><div class="ps-route-banner-main"><span class="ps-route-badge">PATH ${safe(path.id)}</span><strong>${safe(path.title)}</strong><span>— ${safe(path.summary?.value||'')}</span>${path.summary?source(path.summary):''}${bottleneckHtml}${alertHtml}<div class="ps-route-banner-stages">${activeStages.map(st=>`<a href="${areaURL(st.id)}" class="ps-route-stage-chip"><span>${st.number}</span>${safe(st.short)}</a>`).join('<span class="ps-route-arrow">→</span>')}</div><button data-action="scene-path-source" class="ps-source" style="margin-left:auto">Route permissives & notes (${path.facts.length}) ↗</button></div></div>`;
  }
  function siloScene(){
    const positions=new Map(),routes=new Map(),drawn=new Map(),decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(id,x,y,w=160,h=95,title)=>{const n=byId.get(id);if(!n)return;const pos={x,y,w,h};positions.set(id,pos);drawn.set(id,{n,...pos,title});};
    const placeKind=(k,x,y,w,h)=>{const n=parts.find(n=>n.kind===k&&!drawn.has(n.id));if(n)put(n.id,x,y,w,h);};
    const pick=(pattern,x,y,w=150,h=95)=>{const n=parts.find(n=>pattern.test(n.label));if(n)put(n.id,x,y,w,h);};
    let height=840;
    if(s.kind==='silo-house'){
      const columns=M.siloColumns(p,s.id);height=970;
      const decks=[
        {key:'inlet',elev:'EL +42.0m',title:'ROOF INLETS',y:36,h:108,yMin:20,yMax:155},
        {key:'storage',elev:'EL +28.0m',title:'STORAGE SILOS',y:175,h:145,yMin:160,yMax:332},
        {key:'extraction',elev:'EL +16.5m',title:'EXTRACTION',y:338,h:118,yMin:333,yMax:468},
        {key:'feeding',elev:'EL +11.2m',title:'BELT FEEDING',y:474,h:118,yMin:469,yMax:602},
        {key:'selection',elev:'EL +7.5m',title:'ROUTE GATES',y:608,h:118,yMin:603,yMax:745},
        {key:'outlet',elev:'EL +3.5m',title:'OUTLET BELTS',y:812,h:112,yMin:746,yMax:960}
      ];
      const wellXs=columns.map((_,i)=>375+i*340);
      if(isIsoStack()){
        decor.push(isoDeckSVG(decks,200,680,wellXs),text(540,16,'UEE-2 · SILO HOUSE (2.5D ELEVATION STACK)','ps-zone-label'),text(1005,110,'HOUSE SERVICES','ps-zone-label'));
      }else{
        isoDeckSVG(decks,200,680,wellXs);
        decor.push(`<rect x="200" y="156" width="680" height="660" rx="9" class="ps-building-frame"/>`,text(220,179,'UEE-2 · SILO HOUSE','ps-zone-label','start'));
        decor.push(text(530,24,'RECEIVING FROM DISTRIBUTION & RECLAIM','ps-zone-label'),text(1005,110,'HOUSE SERVICES','ps-zone-label'));
        const levels=[[330,'STORAGE'],[466,'EXTRACTION'],[599,'BELT FEEDING'],[733,'ROUTE SELECTION']];
        for(const[y,title]of levels)decor.push(`<path d="M214 ${y}H866" class="ps-floor"/>`,text(184,y-20,title,'ps-zone-label','end'));
      }
      columns.forEach((column,i)=>{
        const x=285+i*340;
        column.inlets.forEach((id,j)=>put(id,x-55+j*160,45,130,77));
        put(column.vessel,x,195,180,105);
        column.extractors.forEach((id,j)=>put(id,x+j*155,355,180,77));
        column.feeders.forEach((id,j)=>put(id,x+j*155,488,180,77));
        column.gates.forEach((id,j)=>put(id,x+15+j*140,622,150,72));
      });
      const gates=new Set(columns.flatMap(c=>c.gates));
      const outlets=[...new Set(s.edges.filter(a=>a.context.network==='material'&&gates.has(a.canonical_subject)).map(a=>a.canonical_object))].sort((a,b)=>p.entities.get(a).label.localeCompare(p.entities.get(b).label));
      outlets.forEach((id,i)=>put(id,285+i*340,830,180,80));
      decor.push(text(540,800,'SELECTED OUTLET → CRUSHER HOUSE','ps-zone-label'));
      const services=parts.filter(n=>!drawn.has(n.id));
      services.forEach((n,i)=>put(n.id,960,135+i*148,155,82,
        /Vent-Filter/.test(n.label)?'Silo vent filters':/Local DFDS/.test(n.label)?'DFDS · ten spray zones':/Service and drinking/.test(n.label)?'Service & drinking water':/Maintenance access/.test(n.label)?'Access & lifting':/Sump Pumps/.test(n.label)?'Sump pumps SP-7A / B':short(n)));
      height=Math.max(height,180+services.length*148);
    }else if(s.kind==='extractor'){
      const frameX=165,frameW=870;
      decor.push(
        `<rect x="${frameX}" y="42" width="${frameW}" height="740" rx="10" class="ps-building-frame"/>`,
        text(frameX+22,66,s.title.toUpperCase()+' · ROTARY EXTRACTOR MECHANICAL & COAL FLOW CUTAWAY','ps-zone-label','start'),
        `<path d="M${frameX+14} 195H${frameX+frameW-14}M${frameX+14} 340H${frameX+frameW-14}M${frameX+14} 490H${frameX+frameW-14}M${frameX+14} 635H${frameX+frameW-14}" class="ps-floor"/>`
      );
      placeKind('cone',500,75,180,76);
      pick(/Adjusting sleeve$/,810,75,160,76);
      placeKind('lubrication',210,75,160,76);
      placeKind('platform',500,220,180,74);
      pick(/Labyrinth seal$/,810,220,160,74);
      pick(/Common VFD$/,210,220,160,74);
      pick(/Slew bearing and external gear$/,500,365,180,76);
      const drives=parts.filter(n=>n.kind==='drive').sort((a,b)=>a.label.localeCompare(b.label));
      drives.forEach((n,i)=>{
        put(n.id,i?805:205,365,175,76);
        for(const a of p.children.get(n.id)||[])positions.set(a.canonical_subject,positions.get(n.id));
      });
      placeKind('blade',505,515,175,74);
      pick(/Local control station$/,810,515,160,74);
      const chute=parts.find(n=>n.kind==='chute');if(chute)put(chute.id,515,660,155,76);
    }else{
      decor.push(`<path class="ps-building-frame" d="M396 120H804V428L633 622H567L396 428Z"/>`,text(600,34,'VESSEL · VENTING · ACCESS · OUTLET','ps-zone-label'));
      const shell=parts.find(n=>/Shell and sloping liner$/.test(n.label));if(shell)put(shell.id,460,218,280,210);
      placeKind('filter',520,50,160,96);pick(/Level and temperature instruments$/,885,210,185,117);
      pick(/Manholes and access openings$/,85,212,190,115);pick(/Emergency bypass chute$/,885,478,175,113);
      const out=s.nodes.find(n=>n.role==='connected'&&n.kind==='extractor');if(out)put(out.id,510,639,180,95);
      decor.push(text(600,583,'COAL DISCHARGES TO THE EXTRACTOR BELOW','ps-zone-label'));
    }
    const extra=parts.filter(n=>!drawn.has(n.id));
    extra.forEach((n,i)=>put(n.id,55+(i%5)*230,height+30+Math.floor(i/5)*190,160,100));
    if(extra.length)height+=60+Math.ceil(extra.length/5)*190;
    const layer=q().get('layer')||'all';
    const edges=s.edges.filter(a=>{
      const u=positions.get(a.canonical_subject),v=positions.get(a.canonical_object);
      if(!u||!v||u===v)return false;
      if(layer==='all'){
        if(s.kind==='silo-house'&&a.context?.network!=='material')return false;
        if(s.kind==='extractor'&&(!['material','mechanical'].includes(a.context?.network)||Math.abs(u.y-v.y)>220))return false;
      }
      return true;
    });

    s.height=height;s.initialHeight=height;
    return decor.join('')+edgeMarkup(edges,positions,routes)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title})).join('');
  }
  function crusherSelection(){
    const columns=M.crusherColumns(p,s.id),index=Math.max(0,Math.min(columns.length-1,Number(q().get('line'))||0)),column=columns[index];
    const route=q().get('coalroute')==='bypass'?'bypass':'screen',outlet=column?.outlets.includes(q().get('outlet'))?q().get('outlet'):column?.outlets[0];
    return {columns,index,column,route,outlet};
  }
  function crusherRouteGuide(){
    if(s.kind==='transfer')return transferRouteGuide();
    if(s.kind!=='crusher-house'||q().get('scene')==='connections')return '';
    const v=crusherSelection();
    const group=(title,items,key,selected)=>`<div><span>${title}</span><nav aria-label="${title}">${items.map(([id,name])=>`<a href="${safe(url({[key]:id,pick:null,edge:null}))}" ${String(id)===String(selected)?'aria-current="true"':''}>${safe(name)}</a>`).join('')}</nav></div>`;
    return `<div class="ps-crusher-guide">${group('Follow a stream',v.columns.map((c,i)=>[i,c.inlets.map(x=>p.entities.get(x).label).join(' / ')||p.entities.get(c.crusher).label]),'line',v.index)}${group('Coal path',[['screen','Screen & crush'],['bypass','Direct bypass']],'coalroute',v.route)}${group('Selected outlet',(v.column?.outlets||[]).map(id=>[id,p.entities.get(id).label]),'outlet',v.outlet)}<small>Illustrate a route · no live status or commands</small></div>`;
  }
  function crusherHouseScene(){
    const v=crusherSelection(),positions=new Map(),drawn=new Map(),routes=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(id,x,y,w=135,h=78,title)=>{const n=byId.get(id);if(n){positions.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});}};
    const decks=[
      {key:'inlet-belts',elev:'EL +38.500',title:'SILO FEED BELTS',y:42,h:104,yMin:20,yMax:160},
      {key:'inlet',elev:'EL +34.200',title:'INLET GATES',y:172,h:106,yMin:161,yMax:288},
      {key:'screen',elev:'EL +24.000',title:'GRIZZLY SCREENS',y:292,h:112,yMin:289,yMax:418},
      {key:'crusher',elev:'EL +18.000',title:'RING CRUSHERS',y:424,h:126,yMin:419,yMax:575},
      {key:'feeder',elev:'EL +10.900',title:'BELT FEEDERS',y:585,h:242,yMin:576,yMax:845},
      {key:'outlet',elev:'EL +4.500',title:'BUNKER BELTS',y:875,h:110,yMin:846,yMax:1020}
    ];
    const wellXs=v.columns.map((_,i)=>348+i*340);
    const decor=[];
    if(isIsoStack()){
      decor.push(isoDeckSVG(decks,195,665,wellXs),text(530,18,'FROM BLENDING SILO HOUSE · UEE-2 (2.5D ELEVATION STACK)','ps-zone-label'),text(1010,148,'HOUSE SERVICES','ps-zone-label'));
    }else{
      isoDeckSVG(decks,195,665,wellXs);
      decor.push(`<rect x="195" y="170" width="665" height="675" rx="10" class="ps-building-frame"/>`,text(530,34,'FROM BLENDING SILO HOUSE · UEE-2','ps-zone-label'),text(1010,148,'HOUSE SERVICES','ps-zone-label'));
      for(const[y,title]of [[147,'+34.200 · INLET'],[381,'+24.000 · SCREEN'],[552,'+18.000 · CRUSHER'],[694,'+10.900 · FEEDER']])decor.push(`<path d="M213 ${y}H842" class="ps-floor"/>`,text(180,y-16,title,'ps-zone-label','end'));
    }
    v.columns.forEach((c,i)=>{
      const x=275+i*340;
      c.inlets.forEach((id,j)=>put(id,x+j*148,55,145,75));
      c.inletGates.forEach((id,j)=>put(id,x+14+j*130,190,115,70));
      c.screens.forEach((id,j)=>put(id,x+j*155,305,145,75));
      put(c.crusher,x,437,145,85);
      c.feeders.forEach((id,j)=>put(id,x-12+j*160,603,170,70));
      c.outletGates.forEach((id,j)=>put(id,x+13+j*125,747,120,60));
      for(const gate of c.inletGates)for(const feeder of c.feeders)routes.set(gate+'>'+feeder,`M${x+129} 222H${x+185}V624H${x+158}`);
      for(const screen of c.screens)for(const feeder of c.feeders)routes.set(screen+'>'+feeder,`M${x} 345H${x-32}V624H${x-12}`);
      decor.push(text(x+183,403,'BYPASS','ps-route-label'),text(x-38,480,'UNDERSIZE','ps-route-label','end'));
    });
    const outlets=[...new Set(v.columns.flatMap(c=>c.outlets))];outlets.forEach((id,i)=>put(id,283+i*330,890,160,78));
    decor.push(text(530,870,'TO UEF-13 · BUNKER FEED','ps-zone-label'));
    const services=s.nodes.filter(n=>n.role==='part'&&!drawn.has(n.id));
    services.forEach((n,i)=>put(n.id,925,187+i*157,175,82,/DE System/.test(n.label)?'Dust extraction · DE-1 / 2':/Local DFDS/.test(n.label)?'DFDS · six spray zones':/Maintenance access/.test(n.label)?'Access & lifting':/Service and drinking/.test(n.label)?'Water services':/Drainage sump/.test(n.label)?'Drainage sump & pumps':short(n)));
    const relevant=s.edges.filter(a=>a.context.network==='material'&&positions.has(a.canonical_subject)&&positions.has(a.canonical_object)&&a.canonical_subject!==s.id&&a.canonical_object!==s.id);

    const active=M.crusherRoute(p,v.column,v.route,v.outlet),keys=new Set(active.map(a=>a.canonical_subject+'>'+a.canonical_object));
    const inactive=relevant.filter(a=>!keys.has(a.canonical_subject+'>'+a.canonical_object));
    s._routeStreamNodes=new Set(relevant.flatMap(a=>[a.canonical_subject,a.canonical_object]));
    s._activeRouteNodes=new Set(active.flatMap(a=>[a.canonical_subject,a.canonical_object]));
    s.height=Math.max(1050,240+services.length*157);s.initialHeight=s.height;
    const xEdges=xrayExtraEdges(positions,[...inactive,...active]);return decor.join('')+`<g class="ps-route-inactive">${edgeMarkup(inactive,positions,routes,null,relevant)}</g><g class="ps-route-active">${edgeMarkup(active,positions,routes,null,relevant)}</g>`+edgeMarkup(xEdges,positions,routes,null,relevant)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title})).join('');
  }
  function crusherMachineScene(){
    const positions=new Map(),routes=new Map(),drawn=[],parts=s.nodes.filter(n=>n.role==='part'),decor=[];
    const put=(n,x,y,w=165,h=82)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h});};
    const pick=(rx,...pos)=>put(parts.find(n=>rx.test(n.label)),...pos);
    const frameX=185,frameW=830;
    if(s.kind==='crusher'){
      decor.push(
        `<rect x="${frameX}" y="48" width="${frameW}" height="685" rx="10" class="ps-building-frame"/>`,
        text(frameX+22,72,s.title.toUpperCase()+' · RING GRANULATOR MECHANICAL & CRUSHING ARRANGEMENT','ps-zone-label','start'),
        `<path d="M${frameX+14} 230H${frameX+frameW-14}M${frameX+14} 405H${frameX+frameW-14}M${frameX+14} 575H${frameX+frameW-14}" class="ps-floor"/>`,
        text(frameX-14,135,'HOUSING & HYDRAULICS','ps-zone-label','end'),
        text(frameX-14,310,'MAIN ROTOR AXIS','ps-zone-label','end'),
        text(frameX-14,485,'CAGE & MONITORING','ps-zone-label','end'),
        text(frameX-14,645,'ISOLATED BASE','ps-zone-label','end')
      );
      pick(/Housing and access$/,235,95,180,82);
      pick(/Hydraulic opening system$/,510,95,180,82);
      pick(/Protection and monitoring$/,785,95,180,82);
      pick(/Drive assembly$/,235,265,185,84);
      pick(/Rotor assembly$/,510,265,185,84);
      pick(/Rotor bearings and seals$/,785,265,185,84);
      pick(/Screen cage and adjustment$/,510,435,185,82);
      pick(/Isolated foundation$/,510,600,185,78);
    }else{
      decor.push(
        `<rect x="${frameX}" y="48" width="${frameW}" height="520" rx="10" class="ps-building-frame"/>`,
        text(frameX+22,72,s.title.toUpperCase()+' · SECONDARY GRIZZLY SCREEN ARRANGEMENT','ps-zone-label','start'),
        `<path d="M${frameX+14} 235H${frameX+frameW-14}M${frameX+14} 405H${frameX+frameW-14}" class="ps-floor"/>`,
        text(frameX-14,140,'EXCITER DRIVE','ps-zone-label','end'),
        text(frameX-14,310,'GRIZZLY DECK','ps-zone-label','end'),
        text(frameX-14,475,'ISOLATION SPRINGS','ps-zone-label','end')
      );
      pick(/Vibrating drive assembly$/,510,95,185,82);
      pick(/Screen body and deck$/,510,265,185,84);
      pick(/Springs and supports$/,510,435,185,78);
      const out=s.nodes.filter(n=>n.role==='connected'&&['crusher','feeder'].includes(n.kind));
      out.forEach((n,i)=>put(n,805,200+i*165,165,78));
    }
    for(const n of s.nodes.filter(n=>n.role==='detail')){const parent=M.closestParents(p,n.id).find(id=>positions.has(id));if(parent)positions.set(n.id,positions.get(parent));}
    const used=new Set(drawn.map(x=>x.n.id));
    const extra=parts.filter(n=>!used.has(n.id));
    extra.forEach((n,i)=>put(n,210+i%4*205,765+Math.floor(i/4)*160,165,78));
    const layer=q().get('layer')||'all';
    const cleanEdges=s.edges.filter(a=>{
      const u=positions.get(a.canonical_subject),v=positions.get(a.canonical_object);
      if(!u||!v||u===v)return false;
      if(layer==='all'){
        const su=p.entities.get(a.canonical_subject)?.label||'',sv=p.entities.get(a.canonical_object)?.label||'';
        if(/Isolated foundation/i.test(su)&&/Housing|Rotor/i.test(sv)&&Math.abs(u.y-v.y)>200)return false;
        if(/Protection and monitoring/i.test(su))return /Rotor bearings/i.test(sv);
        if(/Hydraulic opening/i.test(su)&&/Screen cage/i.test(sv))return false;
        if(/Springs and supports/i.test(su)&&u.y>v.y)return false;
      }
      return true;
    });
    s.height=extra.length?820+Math.ceil(extra.length/4)*160:780;s.initialHeight=Math.min(s.height,860);
    return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+drawn.map(x=>hotspot(x.n,x.x,x.y,x.w,x.h)).join('');
  }
  function dustExtractionScene(){
    const parts=s.nodes.filter(n=>n.role==='part'),pos=new Map(),drawn=[],decor=[];
    const put=(n,x,y,w=170,h=95)=>{if(n&&!pos.has(n.id)){pos.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h});}};
    if(s.kind==='de-house'&&parts.some(n=>n.kind==='de-stream')){
      decor.push(text(600,35,'CAPTURE → SEPARATE → FILTER → EXHAUST','ps-zone-label'));
      parts.filter(n=>n.kind==='de-stream').forEach((n,i)=>put(n,235+i*490,90,245,160));
      parts.filter(n=>!/de-stream/.test(n.kind)).forEach((n,i)=>put(n,95+(i%4)*285,450+Math.floor(i/4)*215,185,110));
      decor.push(text(600,370,'Each stream has four hoods · open a stream to follow air and collected dust','ps-caption'));
    }else if(s.kind==='de-house'){
      // Bunker House Dust Extraction System (175013-ISG-2): Bagfilter -> Fan -> Stack, RALV Return, Compressed Air Pulse Train
      decor.push(`<rect x="165" y="60" width="870" height="540" rx="10" class="ps-building-frame"/>`,
        text(185,84,s.title.toUpperCase()+' · BAGFILTER, EXHAUST FAN, RALV & PULSE-AIR TRAIN','ps-zone-label','start'),
        `<path d="M180 245H1020M180 420H1020" class="ps-floor"/>`,
        text(150,155,'FILTRATION','ps-zone-label','end'),
        text(150,330,'COMPRESSED AIR','ps-zone-label','end'),
        text(150,505,'CONTROLS & VACUUM','ps-zone-label','end'));
      const row1=parts.filter(n=>['filter','fan','airlock'].includes(n.kind));
      const row2=parts.filter(n=>!row1.includes(n)&&['compressor','dryer','receiver','valve'].includes(n.kind));
      const row3=parts.filter(n=>!row1.includes(n)&&!row2.includes(n));
      row1.forEach((n,i)=>put(n,215+i*275,105,175,85));
      row2.forEach((n,i)=>put(n,215+i*275,275,175,85));
      row3.forEach((n,i)=>put(n,215+i*275,450,175,85));
    }else{
      const groups=['duct','cyclone','filter','fan'];groups.forEach((k,i)=>put(parts.find(n=>n.kind===k),60+i*292,165,185,123));
      const used=new Set(drawn.map(x=>x.n.id));parts.filter(n=>!used.has(n.id)).forEach((n,i)=>put(n,75+i%5*225,492+Math.floor(i/5)*200,165,100));
      decor.push(text(600,65,'DUST-LADEN AIR THROUGH THE EXTRACTION STREAM','ps-zone-label'),text(600,429,'Pulse cleaning, hopper discharge and damper controls stay with their equipment','ps-caption'));
    }
    const boundary=s.nodes.filter(n=>n.role==='connected');
    const bottom=Math.max(660,...drawn.map(x=>x.y+x.h+135));
    if(boundary.length)decor.push(text(600,bottom-25,'CONNECTIONS OUTSIDE THIS ASSEMBLY','ps-zone-label'));
    boundary.forEach((n,i)=>put(n,75+i%5*225,bottom+Math.floor(i/5)*195,165,92));
    const partIds=new Set(parts.map(n=>n.id));
    for(const x of drawn)if(partIds.has(x.n.id))for(const child of p.assembly(x.n.id))if(!pos.has(child.id)){pos.set(child.id,pos.get(x.n.id));partIds.add(child.id);}
    const edges=filterCleanInternalEdges(p.networks,pos,partIds).filter(a=>Math.abs(pos.get(a.canonical_subject).y-pos.get(a.canonical_object).y)<=220);
    s.height=Math.max(780,...drawn.map(x=>x.y+x.h+110));s.initialHeight=Math.min(s.height,920);
    return decor.join('')+edgeMarkup(edges,pos)+drawn.map(x=>hotspot(x.n,x.x,x.y,x.w,x.h)).join('');
  }
  function sprayScene(){
    const nodes=s.nodes.filter(n=>n.role==='part'),applications=nodes.filter(n=>(p.classes.get(n.id)||[]).includes('spray_application_point'));
    if(!applications.length)return null;
    const connected=connectedSprayScene(applications);if(connected)return connected;
    const groups=[[],[],[]];
    for(const n of applications){
      const target=(p.outgoing.get(n.id)||[]).find(a=>a.predicate==='sprays_at'),dest=p.entities.get(target?.canonical_object);
      const role=(p.outgoing.get(n.id)||[]).find(a=>a.predicate==='equipment_role')?.value||'';
      const row=/receiving/i.test(role)?2:(p.classes.get(dest?.id)||[]).includes('belt_feeder')?1:0;
      groups[row].push({n,dest});
    }
    let body=text(600,35,'DUST CONTROL AT EACH COAL TRANSFER','ps-zone-label');
    let visibleRows=0;
    groups.forEach((group,row)=>{
      if(!group.length)return;
      const y=90+(visibleRows++)*205;
      body+=text(45,y,['INCOMING CONVEYOR DISCHARGES','BELT-FEEDER DISCHARGES','RECEIVING CHUTES'][row],'ps-zone-label','start')+`<path d="M45 ${y+15}H1150" class="ps-floor"/>`;
      group.sort((a,b)=>a.n.label.localeCompare(b.n.label)).forEach(({n,dest},i)=>{
        const x=600-(group.length*230)/2+i*230+25;
        body+=hotspot(n,x,y+38,165,90,{label:n.label.replace(/^UEE-\d+ /,'')+(dest?' · '+dest.label:'')});
      });
    });
    const other=s.nodes.filter(n=>n.role!=='self'&&!applications.includes(n));
    const controlsY=95+visibleRows*205;
    body+=text(45,controlsY,'LOCAL CONTROLS & SHARED SUPPLY','ps-zone-label','start');
    other.forEach((n,i)=>body+=hotspot(n,65+(i%5)*230,controlsY+32+Math.floor(i/5)*195,165,95));
    s.height=controlsY+240+Math.max(0,Math.ceil(other.length/5)-1)*195;s.initialHeight=s.height;return body;
  }
  function connectedSprayScene(applications){
    const utilities=p.networks.filter(a=>a.context?.network==='utility');
    const chains=applications.map(ap=>{
      const descendants=new Set(p.assembly(ap.id).map(e=>e.id));
      const pru=utilities.find(a=>descendants.has(a.canonical_object)&&!descendants.has(a.canonical_subject))?.canonical_subject;
      const fas=utilities.find(a=>a.canonical_object===pru)?.canonical_subject;
      const dest=(p.outgoing.get(ap.id)||[]).find(a=>a.predicate==='sprays_at')?.canonical_object;
      return {ap,pru,fas,dest};
    });
    if(chains.some(c=>!c.pru||!c.fas))return null;
    chains.sort((a,b)=>a.ap.label.localeCompare(b.ap.label));
    const narrow=window.matchMedia('(max-width:760px)').matches,pos=new Map(),drawn=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(id,x,y,w=165,h=95,title)=>{if(!p.entities.has(id))return;const n=byId.get(id)||{id,label:p.entities.get(id).label,kind:M.kind(p,id),role:'connected'};pos.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});};
    const branchIds=new Set(chains.flatMap(c=>[c.ap.id,c.pru,c.fas,c.dest]));
    const supply=s.nodes.filter(n=>n.role!=='self'&&!branchIds.has(n.id));
    supply.forEach((n,i)=>put(n.id,50+i%(narrow?2:5)*230,65+Math.floor(i/(narrow?2:5))*180));
    const start=125+Math.ceil(supply.length/(narrow?2:5))*180;
    const decor=[text(narrow?280:600,30,'LOCAL SUPPLY, CONTROLS & SHARED BOUNDARIES','ps-zone-label')];
    chains.forEach((c,i)=>{
      const y=start+i*(narrow?350:180);
      put(c.fas,50,y,165,95);put(c.pru,narrow?300:310,y,165,95);
      const count=(p.outgoing.get(c.ap.id)||[]).find(a=>a.predicate==='scheduled_nozzle_count')?.value||p.assembly(c.ap.id).flatMap(e=>p.outgoing.get(e.id)||[]).find(a=>a.predicate==='quantity'&&a.unit==='nozzles')?.value;
      put(c.ap.id,narrow?175:580,narrow?y+175:y,185,95,short(c.ap)+(count!==undefined?' · '+count+' nozzles':''));
      decor.push(text(50,y-20,(p.outgoing.get(c.ap.id)||[]).find(a=>a.predicate==='equipment_role')?.value||short(c.ap),'ps-zone-label','start'));
    });
    const destinations=[...new Set(chains.map(c=>c.dest).filter(Boolean))];
    const bottom=start+chains.length*(narrow?350:180);
    destinations.forEach((id,i)=>put(id,narrow?50+i%2*230:950,narrow?bottom+100+Math.floor(i/2)*180:start+i*230,175,100));
    for(const d of drawn.values())if(d.n.role!=='connected')for(const child of p.assembly(d.n.id))if(!pos.has(child.id))pos.set(child.id,pos.get(d.n.id));
    const regulators=new Set(chains.map(c=>c.pru)),consumers=new Set(destinations);
    const localIds=new Set(p.assembly(s.id).map(e=>e.id));
    const edges=p.networks.filter(a=>['utility','control'].includes(a.context?.network)&&localIds.has(a.canonical_subject)&&localIds.has(a.canonical_object)&&pos.has(a.canonical_subject)&&pos.has(a.canonical_object)&&pos.get(a.canonical_subject)!==pos.get(a.canonical_object)&&pos.get(a.canonical_object).y>=pos.get(a.canonical_subject).y-15&&pos.get(a.canonical_object).y-pos.get(a.canonical_subject).y<=220&&!(regulators.has(a.canonical_subject)&&consumers.has(a.canonical_object)));
    edges.push(...chains.flatMap(c=>(p.outgoing.get(c.ap.id)||[]).filter(a=>a.predicate==='sprays_at'&&pos.has(a.canonical_object)&&Math.abs(pos.get(a.canonical_object).y-pos.get(c.ap.id).y)<=220).map(a=>({...a,context:{...a.context,network:'utility'}}))));
    decor.push(text(50,start-55,'FAS → PRU → APPLICATION · QUALIFIED DESIGN DESTINATIONS','ps-zone-label','start'));
    s.width=narrow?570:1200;s.height=Math.max(bottom+140,...[...drawn.values()].map(d=>d.y+d.h+100));s.initialHeight=narrow?820:950;
    return decor.join('')+edgeMarkup(edges,pos)+[...drawn.values()].map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title})).join('');
  }

  /**
   * Dedicated Multi-Floor Gravity Sampling Cascade Schematic (EAU-1 in UEF-3 & EAU-2 in UEF-13)
   * Follows the exact process/mechanical schematic in drawings 175048 & 175049-ISG-2:
   * Primary Cutters (1 & 2) -> Primary Sample Chutes -> Reversible Belt Feeder
   *   ├── Left (Reverse Bias Check): Reverse Bias Chute -> Bias Sample Bin
   *   └── Right (Normal Crushing & Secondary Cut): Forward Chute -> Hammer Crusher -> Crushed Chute -> Secondary Sampler
   *         ├── Left: Final Sample Chute -> 4-Station Rotary Sample Collector
   *         └── Right: Reject Inlet Chute -> Reject Screw Conveyor -> Reject Slide Gate -> Reject Return Chutes (A/B) -> Downstream Conveyors
   */
  function samplingScene(){
    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const put=(n,x,y,w=148,h=68,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};
    const findPart=rx=>parts.find(n=>rx.test(n.label)&&!positions.has(n.id));

    const frameX=185,frameY=48,frameW=780;
    const decks=[
      {key:'stage1',elev:'LEVEL 5 · TOP',title:'PRIMARY CUTTERS',y:58,h:145,yMin:40,yMax:210},
      {key:'feeder',elev:'LEVEL 4',title:'FEEDER & BIAS BIN',y:222,h:145,yMin:211,yMax:374},
      {key:'crusher',elev:'LEVEL 3',title:'SAMPLE CRUSHER',y:386,h:145,yMin:375,yMax:538},
      {key:'stage2',elev:'LEVEL 2',title:'SECONDARY CUT & COLLECTOR',y:550,h:145,yMin:539,yMax:702},
      {key:'reject',elev:'LEVEL 1 · BASE',title:'REJECT SCREW & RETURN',y:714,h:155,yMin:703,yMax:895}
    ];
    if(isIsoStack()){
      decor.push(
        isoDeckSVG(decks,frameX,frameW,[380,580,780]),
        text(frameX+22,22,s.title.toUpperCase()+' · 2.5D GRAVITY SAMPLING TOWER CASCADE','ps-zone-label','start'),
        text(1085,70,'CONTROLS & INTERFACES','ps-zone-label')
      );
    }else{
      isoDeckSVG(decks,frameX,frameW,[380,580,780]);
      decor.push(
        `<rect x="${frameX}" y="${frameY}" width="${frameW}" height="835" rx="10" class="ps-building-frame"/>`,
        text(frameX+22,frameY+24,s.title.toUpperCase()+' · TWO-STAGE GRAVITY SAMPLING & REJECT RETURN SCHEMATIC','ps-zone-label','start'),
        text(1085,70,'CONTROLS & INTERFACES','ps-zone-label')
      );
      decks.forEach((d,idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${d.y-6}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,d.y+48,d.title,'ps-zone-label','end'));
      });
    }

    // Deck 1 (y=72): Primary Sampler-1, Primary 1 chute, Primary Sampler-2, Primary 2 chute
    put(findPart(/Primary Sampler-1$/i),215,72,150,68);
    put(findPart(/primary1 sample chute/i),395,72,150,68);
    put(findPart(/Primary Sampler-2$/i),595,72,150,68);
    put(findPart(/primary2 sample chute/i),775,72,150,68);

    // Deck 2 (y=236): Bias Sample Bin <-- Reverse bias chute <-- Reversible Belt Feeder --> Forward feeder chute
    put(findPart(/Bias Sample Bin/i),210,236,148,68);
    put(findPart(/reverse bias discharge chute/i),390,236,148,68);
    put(findPart(/Reversible Belt Feeder/i),585,236,155,68);
    put(findPart(/forward feeder discharge chute/i),775,236,148,68);

    // Deck 3 (y=400): Hammer Crusher --> Crushed sample chute
    put(findPart(/Hammer Crusher/i),475,400,160,68);
    put(findPart(/crushed sample chute/i),685,400,155,68);

    // Deck 4 (y=564): Rotary Sample Collector <-- Final sample chute <-- Secondary Sampler --> Reject inlet chute
    put(findPart(/Rotary Sample Collector/i),210,564,152,68);
    put(findPart(/final sample chute/i),395,564,148,68);
    put(findPart(/Secondary Sampler/i),580,564,155,68);
    put(findPart(/reject inlet chute/i),775,564,148,68);

    // Deck 5 (y=728): Reject Screw Conveyor --> Reject Slide Gate --> Reject return chutes
    const retChutes=parts.filter(n=>/reject return chute/i.test(n.label)&&!positions.has(n.id));
    put(findPart(/Reject Screw Conveyor/i),225,728,155,68);
    put(findPart(/Reject Slide Gate/i),425,728,150,68);
    retChutes.forEach((n,i)=>put(n,615+i*170,728,150,68));

    const sideParts=[...parts.filter(n=>!positions.has(n.id)),...outside.filter(n=>!['conveyor'].includes(n.kind))];
    sideParts.forEach((n,i)=>put(n,1010,85+i*148,160,70));

    let curBottom=900;
    const convs=outside.filter(n=>n.kind==='conveyor'&&!positions.has(n.id));
    if(convs.length){
      decor.push(text(575,curBottom+22,'SAMPLED MAIN-STREAM & REJECT-RECEIVING CONVEYORS','ps-zone-label'));
      convs.forEach((n,i)=>put(n,270+i*210,curBottom+40,165,72));
      curBottom+=155;
    }

    const partIds=new Set(parts.map(n=>n.id));
    const internalClean=filterCleanInternalEdges(s.edges,positions,partIds).filter(a=>{
      const u=positions.get(a.canonical_subject),v=positions.get(a.canonical_object);
      return u&&v&&v.y>=u.y-15&&v.y-u.y<=220;
    });
    const retSet=new Set(retChutes.map(n=>n.id)),convSet=new Set(convs.map(n=>n.id));
    const returnEdges=s.edges.filter(a=>retSet.has(a.canonical_subject)&&convSet.has(a.canonical_object));
    const baseEdges=[...internalClean,...returnEdges];
    const cleanEdges=[...baseEdges,...xrayExtraEdges(positions,baseEdges)];

    s.width=1220;
    s.height=Math.max(960,curBottom+35);
    s.initialHeight=Math.min(s.height,960);
    return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
  }

  function topoSortBand(items,edges){
    if(items.length<=1)return items;
    const ids=new Set(items.map(n=>n.id));
    const roleRank=n=>{
      const l=n.label.toLowerCase(),k=n.kind;
      if(k==='motor'||/motor/i.test(l))return 1;
      if(k==='coupling'&&!/low.speed|output/i.test(l))return 2;
      if(k==='gearbox'||/gearbox/i.test(l))return 3;
      if(k==='coupling'||k==='shaft-coupling')return 4;
      if(k==='actuator'||k==='exciter'||k==='thruster')return 5;
      if(k==='takeup'||k==='counterweight'||/take-up/i.test(l))return 6;
      if(/sprocket|scraper chain|chain|rotor|pulley|flap blade|screen body/i.test(l))return 7;
      if(/blade|flight|liner|casing|deck|cage/i.test(l))return 8;
      if(k==='brake'||/brake/i.test(l))return 9;
      return 10;
    };
    const sorted=[...items].sort((a,b)=>roleRank(a)-roleRank(b)||a.label.localeCompare(b.label,undefined,{numeric:true}));
    const adj=new Map(sorted.map(n=>[n.id,new Set()])),indeg=new Map(sorted.map(n=>[n.id,0]));
    for(const a of edges){
      const u=a.canonical_subject,v=a.canonical_object;
      if(ids.has(u)&&ids.has(v)&&u!==v&&!adj.get(v).has(u)&&!adj.get(u).has(v)){
        adj.get(u).add(v);indeg.set(v,indeg.get(v)+1);
      }
    }
    const queue=sorted.filter(n=>indeg.get(n.id)===0),out=[];
    while(queue.length){
      queue.sort((a,b)=>roleRank(a)-roleRank(b)||a.label.localeCompare(b.label,undefined,{numeric:true}));
      const u=queue.shift();out.push(u);
      for(const vid of adj.get(u.id)){
        indeg.set(vid,indeg.get(vid)-1);
        if(indeg.get(vid)===0)queue.push(sorted.find(x=>x.id===vid));
      }
    }
    for(const n of sorted)if(!out.includes(n))out.push(n);
    return out;
  }

  function filterCleanInternalEdges(edges,positions,partIds){
    const layer=q().get('layer')||'all';
    const valid=edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!partIds.has(u)||!partIds.has(v)||!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      if(layer==='all'&&!['material','mechanical','utility'].includes(a.context?.network))return false;
      return true;
    });
    // Suppress transitive shortcut edges (u -> v when u -> w -> v exists in valid) so arrows step cleanly node-to-node
    const adj=new Map();
    for(const a of valid){
      if(!adj.has(a.canonical_subject))adj.set(a.canonical_subject,new Set());
      adj.get(a.canonical_subject).add(a.canonical_object);
    }
    return valid.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      const uNext=adj.get(u)||new Set();
      for(const w of uNext){
        if(w!==v&&(adj.get(w)||new Set()).has(v))return false;
      }
      return true;
    });
  }

  function classifyYardMachineAnatomy(parts){
    if(s.kind==='stacker'){
      const z1Tripper=parts.filter(n=>/tripper/i.test(n.label)).sort((a,b)=>{
        const r=x=>x.kind==='tripper'?1:x.kind==='pulley'?2:3;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const z2BoomBelt=parts.filter(n=>!z1Tripper.includes(n)&&(/^boom conveyor$|belt and pulleys|belt weigher/i.test(n.label)||['boom','belt','weigher'].includes(n.kind))).sort((a,b)=>{
        const r=x=>x.kind==='boom'?1:x.kind==='belt'?2:3;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const z3Luffing=parts.filter(n=>!z1Tripper.includes(n)&&!z2BoomBelt.includes(n)&&/luffing/i.test(n.label)).sort((a,b)=>{
        const r=x=>/luffing system$/i.test(x.label)?1:x.kind==='hydraulic'?2:3;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const z4Slew=parts.filter(n=>!z1Tripper.includes(n)&&!z2BoomBelt.includes(n)&&!z3Luffing.includes(n)&&/slew/i.test(n.label)).sort((a,b)=>{
        const r=x=>/slew system$/i.test(x.label)?1:x.kind==='hydraulic'?2:x.kind==='motor'?3:4;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const z5Travel=parts.filter(n=>!z1Tripper.includes(n)&&!z2BoomBelt.includes(n)&&!z3Luffing.includes(n)&&!z4Slew.includes(n)&&(/travel|rail clamp|storm anchor/i.test(n.label)||['bogie','rail-clamp'].includes(n.kind))).sort((a,b)=>{
        const r=x=>/travel system$/i.test(x.label)?1:x.kind==='motor'?2:x.kind==='bogie'?3:4;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const z6BoomDrive=parts.filter(n=>!z1Tripper.includes(n)&&!z2BoomBelt.includes(n)&&!z3Luffing.includes(n)&&!z4Slew.includes(n)&&!z5Travel.includes(n)&&(/boom conveyor/i.test(n.label)||['motor','coupling','shaft-coupling','gearbox','brake','drive'].includes(n.kind))).sort((a,b)=>{
        const r=x=>x.kind==='drive'?0:x.kind==='motor'?1:x.kind==='coupling'?2:x.kind==='gearbox'?3:x.kind==='shaft-coupling'?4:x.kind==='brake'?5:6;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const z7Houses=parts.filter(n=>!z1Tripper.includes(n)&&!z2BoomBelt.includes(n)&&!z3Luffing.includes(n)&&!z4Slew.includes(n)&&!z5Travel.includes(n)&&!z6BoomDrive.includes(n)&&['cabin','building','protection'].includes(n.kind));
      const z8Services=parts.filter(n=>![...z1Tripper,...z2BoomBelt,...z3Luffing,...z4Slew,...z5Travel,...z6BoomDrive,...z7Houses].includes(n));
      return {z1Tripper,z2BoomBelt,z3Luffing,z4Slew,z5Travel,z6BoomDrive,z7Houses,z8Services};
    }
    const isAux=n=>/auxiliary|aux boom/i.test(n.label);
    const isMain=n=>/main scraper|main boom/i.test(n.label);
    const isDrive=n=>['motor','coupling','shaft-coupling','gearbox','brake','drive'].includes(n.kind);
    const boomOrder=x=>x.kind==='boom'?1:x.kind==='scraper'?2:x.kind==='blade'?3:x.kind==='takeup'?4:5;
    const driveOrder=x=>x.kind==='drive'?0:x.kind==='motor'?1:x.kind==='coupling'?2:x.kind==='brake'?3:x.kind==='gearbox'?4:x.kind==='hoist'?5:6;
    const z1AuxBoom=parts.filter(n=>isAux(n)&&!isDrive(n)).sort((a,b)=>boomOrder(a)-boomOrder(b)||a.label.localeCompare(b.label));
    const z2MainBoom=parts.filter(n=>isMain(n)&&!isDrive(n)).sort((a,b)=>boomOrder(a)-boomOrder(b)||a.label.localeCompare(b.label));
    const z3Hoist=parts.filter(n=>!isAux(n)&&!isMain(n)&&/hoist|winch/i.test(n.label)).sort((a,b)=>{
      const r=x=>/hoist system$/i.test(x.label)?1:driveOrder(x)+1;
      return r(a)-r(b)||a.label.localeCompare(b.label);
    });
    const z4MainDrive=parts.filter(n=>isMain(n)&&isDrive(n)).sort((a,b)=>driveOrder(a)-driveOrder(b)||a.label.localeCompare(b.label));
    const z5AuxDrive=parts.filter(n=>isAux(n)&&isDrive(n)).sort((a,b)=>driveOrder(a)-driveOrder(b)||a.label.localeCompare(b.label));
    const z6Travel=parts.filter(n=>!isAux(n)&&!isMain(n)&&!z3Hoist.includes(n)&&(/travel|rail clamp|storm anchor|spring buffer/i.test(n.label)||['bogie','rail-clamp'].includes(n.kind))).sort((a,b)=>{
      const r=x=>/travel system$/i.test(x.label)?1:x.kind==='motor'?2:/rails and|wheels/i.test(x.label)?3:/hydraulic rail/i.test(x.label)?4:/manual rail/i.test(x.label)?5:6;
      return r(a)-r(b)||a.label.localeCompare(b.label);
    });
    const z7ReelsLube=parts.filter(n=>!isAux(n)&&!isMain(n)&&!z3Hoist.includes(n)&&!z6Travel.includes(n)&&['cable-reel','lubrication'].includes(n.kind));
    const z8Services=parts.filter(n=>![...z1AuxBoom,...z2MainBoom,...z3Hoist,...z4MainDrive,...z5AuxDrive,...z6Travel,...z7ReelsLube].includes(n));
    return {z1AuxBoom,z2MainBoom,z3Hoist,z4MainDrive,z5AuxDrive,z6Travel,z7ReelsLube,z8Services};
  }

  function yardMachineMatrixScene(){
    const narrow=window.matchMedia('(max-width:760px)').matches;
    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const put=(n,x,y,w=136,h=70,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};

    const ownSet=new Set([s.id,...parts.map(n=>n.id)]);
    const matEdges=s.edges.filter(a=>a.context?.network==='material');
    const upstream=[],downstream=[],auxOutside=[];
    for(const n of outside){
      const feedsUs=matEdges.some(a=>a.canonical_subject===n.id&&ownSet.has(a.canonical_object));
      const fedByUs=matEdges.some(a=>ownSet.has(a.canonical_subject)&&a.canonical_object===n.id);
      if(feedsUs&&!fedByUs&&['pile','conveyor','tripper'].includes(n.kind))upstream.push(n);
      else if(fedByUs&&['pile','conveyor','chute'].includes(n.kind))downstream.push(n);
      else auxOutside.push(n);
    }

    const frameX=narrow?20:165,frameW=narrow?520:880,centerX=frameX+frameW/2,rowH=164;
    let curY=48;
    const frameTop=curY;
    const bands=[];
    const placeGridBand=(label,items,customCols=null)=>{
      if(!items.length)return;
      bands.push([curY,label]);
      const rowY=curY+28;
      const cols=customCols||(narrow?3:Math.min(items.length,4));
      const spacing=narrow?168:(cols>=5?162:196),boxW=cols>=5?126:142;
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,rowY+r*rowH,boxW,68);
      });
      curY=rowY+Math.ceil(items.length/cols)*rowH;
    };

    const anat=classifyYardMachineAnatomy(parts);
    if(s.kind==='stacker'){
      placeGridBand('1 · TRAVELLING TRIPPER CAR & LUFFING BOOM CONVEYOR',[...anat.z1Tripper,...anat.z2BoomBelt]);
      placeGridBand('2 · BOOM CONVEYOR DRIVE POWERTRAIN',anat.z6BoomDrive,narrow?3:Math.min(anat.z6BoomDrive.length,5));
      placeGridBand('3 · HYDRAULIC LUFFING & TURNTABLE SLEWING SYSTEMS',[...anat.z3Luffing,...anat.z4Slew]);
      placeGridBand('4 · GANTRY LONG-TRAVEL BOGIES & RAIL CLAMPS',anat.z5Travel);
      placeGridBand('5 · CABIN, E-HOUSE, FIRE PROTECTION, DSS & LUBRICATION',[...anat.z7Houses,...anat.z8Services]);
    }else{
      placeGridBand('1 · MAIN & AUXILIARY SCRAPER BOOM CHAINS, BLADES & TAKE-UP',[...anat.z2MainBoom,...anat.z1AuxBoom]);
      placeGridBand('2 · MAIN & AUXILIARY SCRAPER BOOM DRIVE POWERTRAINS',[...anat.z4MainDrive,...anat.z5AuxDrive],narrow?3:6);
      placeGridBand('3 · PORTAL CROWN BOOM HOIST WINCH SYSTEM',anat.z3Hoist);
      placeGridBand('4 · PORTAL GANTRY LONG-TRAVEL BOGIES, RAIL CLAMPS & BUFFERS',anat.z6Travel);
      placeGridBand('5 · CABLE REELS, DUAL LUBRICATION & ONBOARD WATER-MIST DSS',[...anat.z7ReelsLube,...anat.z8Services]);
    }

    const frameH=Math.max(240,curY-frameTop+12);
    decor.unshift(
      `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
      text(frameX+20,frameTop+20,`${s.title.toUpperCase()} · CATEGORIZED SUBSYSTEM COMPONENT MATRIX`,'ps-zone-label','start')
    );
    for(const [y] of bands.slice(1))decor.push(`<path d="M${frameX+14} ${y}H${frameX+frameW-14}" class="ps-floor"/>`);
    for(const [y,label] of bands)decor.push(text(frameX+22,y+18,label,'ps-zone-label','start'));

    const extAll=[...upstream,...downstream,...auxOutside];
    if(extAll.length){
      const botY=frameTop+frameH+48;
      decor.push(text(centerX,botY-16,'CONNECTED STOCKPILE, CONVEYOR & STOCKYARD INTERFACES','ps-zone-label'));
      extAll.forEach((n,i)=>put(n,frameX+30+(i%4)*210,botY+Math.floor(i/4)*156,148,68));
      curY=botY+Math.ceil(extAll.length/4)*156+25;
    }

    s.width=narrow?570:1220;
    s.height=Math.max(780,curY+35);
    s.initialHeight=Math.min(s.height,940);
    const cleanEdges=xrayExtraEdges(positions,[]);
    return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
  }

  function yardMachineScene(){
    const narrow=window.matchMedia('(max-width:760px)').matches;
    if(narrow||q().get('spread')==='1')return yardMachineMatrixScene();

    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const self=s.nodes.find(n=>n.role==='self');
    const put=(n,x,y,w=112,h=62,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};

    const ownSet=new Set([s.id,...parts.map(n=>n.id)]);
    const matEdges=s.edges.filter(a=>a.context?.network==='material');
    const upstream=[],downstream=[],auxOutside=[];
    for(const n of outside){
      const feedsUs=matEdges.some(a=>a.canonical_subject===n.id&&ownSet.has(a.canonical_object));
      const fedByUs=matEdges.some(a=>ownSet.has(a.canonical_subject)&&a.canonical_object===n.id);
      if(feedsUs&&!fedByUs&&['pile','conveyor','tripper'].includes(n.kind))upstream.push(n);
      else if(fedByUs&&['pile','conveyor','chute'].includes(n.kind))downstream.push(n);
      else auxOutside.push(n);
    }

    const frameX=178,frameY=38,frameW=1364;
    const cardRowH=158,boxW=112,boxH=62;

    const placeZoneCard=(cardX,cardY,cardW,cardH,cols,badgeNum,title,subtitle,items,tint='#f6faf2',stroke='#b7c8b0',badgeFill='#355d47')=>{
      decor.push(
        `<rect x="${cardX}" y="${cardY}" width="${cardW}" height="${cardH}" rx="10" fill="${tint}" fill-opacity=".82" stroke="${stroke}" stroke-width="1.6"/>`,
        `<rect x="${cardX+10}" y="${cardY+9}" width="20" height="18" rx="5" fill="${badgeFill}"/>`,
        `<text x="${cardX+20}" y="${cardY+22}" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">${safe(badgeNum)}</text>`,
        text(cardX+36,cardY+21,title,'ps-zone-label','start'),
        subtitle?`<text x="${cardX+cardW-10}" y="${cardY+21}" text-anchor="end" fill="#6b7e6b" font-size="9" font-weight="600">${safe(subtitle)}</text>`:``
      );
      if(!items.length)return;
      const itemStartY=cardY+36;
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
        const rStep=Math.min(Math.floor((cardW-20)/Math.max(1,cols)),178);
        const rowSpan=rowCount*rStep;
        const startX=Math.round(cardX+(cardW-rowSpan)/2+(rStep-boxW)/2);
        put(n,startX+c*rStep,itemStartY+r*cardRowH,boxW,boxH);
      });
    };

    const anat=classifyYardMachineAnatomy(parts);
    const upperY=74;
    let curY=upperY;
    let profileBandY=0,profileBandH=124;
    let driveSet=new Set();

    if(s.kind==='stacker'){
      const {z1Tripper,z2BoomBelt,z3Luffing,z4Slew,z5Travel,z6BoomDrive,z7Houses,z8Services}=anat;
      driveSet=new Set(z6BoomDrive.map(n=>n.id));

      // Tier 1: Zone 1 (Travelling Tripper), Zone 2 (Boom Conveyor & Weigher), Zone 3 (Hydraulic Luffing System)
      const u1X=194,u1W=432,u1Cols=3;
      const u2X=638,u2W=436,u2Cols=3;
      const u3X=1086,u3W=440,u3Cols=3;
      const upperRows=Math.max(1,Math.ceil(z1Tripper.length/u1Cols),Math.ceil(z2BoomBelt.length/u2Cols),Math.ceil(z3Luffing.length/u3Cols));
      const upperCardH=upperRows*cardRowH+36;

      placeZoneCard(u1X,upperY,u1W,upperCardH,u1Cols,'1','TRAVELLING TRIPPER CAR','YARD BELT TAKE-OFF',z1Tripper,'#f7faf2','#b6c8af');
      placeZoneCard(u2X,upperY,u2W,upperCardH,u2Cols,'2','LUFFING BOOM CONVEYOR','2000 MM · 2800 TPH',z2BoomBelt,'#f3f8ef','#9eb898');
      placeZoneCard(u3X,upperY,u3W,upperCardH,u3Cols,'3','HYDRAULIC LUFFING SYSTEM','CYLINDERS & HPU',z3Luffing,'#f2f7f8','#96b8c2');

      // Tier 2: Center Side-Elevation Luffing-Slewing Stacker Kinematic Profile
      profileBandY=upperY+upperCardH+14;
      const pTop=profileBandY,pBot=pTop+profileBandH,railY=pBot-18;
      if(self&&!positions.has(s.id))positions.set(s.id,{x:260,y:pTop+18,w:1180,h:profileBandH-36});

      decor.push(
        `<rect x="${u1X}" y="${pTop}" width="${u3X+u3W-u1X}" height="${profileBandH}" rx="12" fill="#e6efe0" fill-opacity=".68" stroke="#96ae92" stroke-width="1.6"/>`,
        // 8400 mm gauge rail track
        `<path d="M225 ${railY}H1495" class="ps-rail"/>`,
        // Yard belt & Travelling Tripper car on left (x=250..560)
        `<path d="M235 ${railY-22}H420L525 ${pTop+34}H568" fill="none" stroke="#4d6e5d" stroke-width="5" stroke-linecap="round"/>`,
        `<path d="M420 ${railY-22}L515 ${railY-22}" fill="none" stroke="#6d8778" stroke-width="3" stroke-dasharray="5 3"/>`,
        `<circle cx="556" cy="${pTop+36}" r="11" class="ps-belt-drum"/>`,
        `<polygon points="546,${pTop+44} 574,${pTop+44} 592,${pTop+72} 564,${pTop+72}" fill="#d8c390" stroke="#8b7340" stroke-width="1.5"/>`,
        `<circle cx="390" cy="${railY-6}" r="6.5" class="ps-wheel"/><circle cx="485" cy="${railY-6}" r="6.5" class="ps-wheel"/>`,
        text(365,pTop+26,'TRAVELLING TRIPPER LOOP  ▶▶','ps-belt-flow-arrow'),
        // Gantry portal, Ø4000 mm Slew Turntable Ring, A-Frame Mast & Counterweight
        `<rect x="655" y="${railY-24}" width="180" height="16" rx="3" fill="#527e72" stroke="#35584e" stroke-width="1.6"/>`,
        `<circle cx="685" cy="${railY-5}" r="7.5" class="ps-wheel"/><circle cx="805" cy="${railY-5}" r="7.5" class="ps-wheel"/>`,
        `<ellipse cx="745" cy="${railY-28}" rx="56" ry="7" fill="#d9c693" stroke="#856d38" stroke-width="1.8"/>`,
        `<path d="M715 ${railY-35}L745 ${pTop+16}L775 ${railY-35}" fill="none" stroke="#456b5e" stroke-width="4" stroke-linejoin="round"/>`,
        `<path d="M715 ${pTop+54}H612V${pTop+74}H715" fill="#9fb4a7" stroke="#4d6a5c" stroke-width="1.6"/>`,
        `<rect x="596" y="${pTop+48}" width="44" height="28" rx="3" fill="#6b8475" stroke="#3c5447" stroke-width="1.6"/>`,
        text(618,pTop+42,'COUNTERWEIGHT','ps-belt-flow-arrow'),
        text(745,railY-5,'Ø4000 SLEW RING & GANTRY BOGIES (8400 MM GAUGE)','ps-belt-flow-arrow'),
        // Luffing Hydraulic Cylinders & Inclined 45 m Luffing Boom Conveyor
        `<path d="M768 ${railY-42}L965 ${pTop+52}" stroke="#397587" stroke-width="5.5" stroke-linecap="round"/>`,
        `<path d="M745 ${pTop+16}L1355 ${pTop+24}" stroke="#7d968a" stroke-width="2" stroke-dasharray="6 3"/>`,
        `<path d="M755 ${pTop+68}L1365 ${pTop+24}L1372 ${pTop+38}L762 ${pTop+82}Z" fill="#b7c9be" fill-opacity=".85" stroke="#44695c" stroke-width="2"/>`,
        `<path d="M760 ${pTop+65}L1362 ${pTop+21}" stroke="#ab7337" stroke-width="3.5" stroke-dasharray="9 4"/>`,
        `<circle cx="762" cy="${pTop+74}" r="11" class="ps-belt-drum"/><circle cx="1365" cy="${pTop+30}" r="12" class="ps-belt-drum"/>`,
        text(1065,pTop+16,'45 M LUFFING BOOM CONVEYOR (-10.5° TO +16°)  ▶▶▶  2800 TPH','ps-belt-flow-arrow'),
        text(865,pTop+94,'HYDRAULIC LUFFING CYLINDERS','ps-Subtle'),
        // Coal Trajectory & Stockpile Cone on right
        `<path d="M1378 ${pTop+32}Q1415 ${pTop+50} 1425 ${railY-28}" fill="none" stroke="#ab7337" stroke-width="3.5" stroke-dasharray="5 4"/>`,
        `<path d="M1365 ${railY-2}L1425 ${railY-44}L1485 ${railY-2}Z" fill="url(#ps-coal)" stroke="#354e4c" stroke-width="1.8"/>`,
        text(1425,pTop+22,'STOCKPILE DISCHARGE','ps-belt-flow-arrow')
      );

      // Tier 3: Zone 4 (Turntable Slewing System, 4 cols) + Zone 5 (Gantry Long-Travel & Rail Clamps, 4 cols)
      const lowerY=profileBandY+profileBandH+14;
      const l1X=194,l1W=658,l1Cols=Math.min(4,Math.max(2,z4Slew.length));
      const l2X=864,l2W=662,l2Cols=Math.min(4,Math.max(2,z5Travel.length));
      const lowerRows=Math.max(1,Math.ceil(z4Slew.length/l1Cols),Math.ceil(z5Travel.length/l2Cols));
      const lowerCardH=lowerRows*cardRowH+36;

      placeZoneCard(l1X,lowerY,l1W,lowerCardH,l1Cols,'4','TURNTABLE SLEWING (Ø4000 MM)','PINIONS · MOTORS · HPU',z4Slew,'#f7faf2','#b6c8af');
      placeZoneCard(l2X,lowerY,l2W,lowerCardH,l2Cols,'5','GANTRY TRAVEL & RAIL CLAMPS','8400 MM GAUGE · 12×5.5 kW',z5Travel,'#f2f7f4','#8fb0a1');

      // Tier 4: Zone 6 (Boom Conveyor Drive Powertrain Shaft Line)
      curY=lowerY+lowerCardH+16;
      if(z6BoomDrive.length){
        const dCols=Math.min(z6BoomDrive.length,6);
        const dRows=Math.ceil(z6BoomDrive.length/dCols);
        const driveCardH=dRows*144+44;
        const driveCardW=u3X+u3W-u1X;
        const shaftY=curY+38+31;
        const dStep=Math.floor((driveCardW-36)/Math.max(1,dCols));
        const dBoxW=124,dBoxH=62;
        const startX=u1X+18+Math.round((dStep-dBoxW)/2);

        decor.push(
          `<rect x="${u1X}" y="${curY}" width="${driveCardW}" height="${driveCardH}" rx="10" fill="#f3f0f8" fill-opacity=".78" stroke="#a697c2" stroke-width="1.8"/>`,
          `<rect x="${u1X+10}" y="${curY+9}" width="20" height="18" rx="5" fill="#5e4982"/>`,
          `<text x="${u1X+20}" y="${curY+22}" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">6</text>`,
          text(u1X+36,curY+21,'BOOM CONVEYOR DRIVE POWERTRAIN (2×132 kW MOTORS → FLUID COUPLINGS → BEVEL-HELICAL GEARBOXES → THRUSTER BRAKES)','ps-zone-label','start'),
          `<path class="ps-belt-shaft" d="M${startX+30} ${shaftY}H${startX+(dCols-1)*dStep+dBoxW-30}"/>`
        );
        z6BoomDrive.forEach((n,i)=>{
          const r=Math.floor(i/dCols),c=i%dCols;
          put(n,startX+c*dStep,curY+38+r*144,dBoxW,dBoxH);
        });
        curY+=driveCardH+16;
      }

      // Tier 5: Zone 7 (Cabin, E-House & Fire Detection) + Zone 8 (Onboard DSS, Grease Lube & Stockyard Context)
      const z8All=[...z8Services,...auxOutside].filter(n=>!positions.has(n.id));
      if(z7Houses.length||z8All.length){
        const z7Cols=Math.min(3,Math.max(2,z7Houses.length));
        const z8Cols=Math.min(4,Math.max(2,z8All.length));
        const z7W=556,z8X=u1X+z7W+12,z8W=(u3X+u3W)-z8X;
        const botRows=Math.max(1,Math.ceil(z7Houses.length/z7Cols),Math.ceil(z8All.length/z8Cols));
        const botCardH=botRows*cardRowH+36;

        placeZoneCard(u1X,curY,z7W,botCardH,z7Cols,'7','CABIN, E-HOUSE & FIRE PROTECTION','OPERATOR CABIN · FMZ5000',z7Houses,'#fbf7ec','#d2be8c');
        placeZoneCard(z8X,curY,z8W,botCardH,z8Cols,'8','ONBOARD DSS, CENTRAL LUBE & YARD','DSS · GREASE · DCS · QRC',z8All,'#eff5f6','#9ebec7');
        curY+=botCardH+16;
      }
    }else{
      const {z1AuxBoom,z2MainBoom,z3Hoist,z4MainDrive,z5AuxDrive,z6Travel,z7ReelsLube,z8Services}=anat;
      driveSet=new Set([...z4MainDrive,...z5AuxDrive,...z3Hoist].map(n=>n.id));

      // Tier 1: Zone 1 (Auxiliary Scraper Boom, 2 cols), Zone 2 (Main Scraper Boom, 2 cols), Zone 3 (Portal Crown Boom Hoist Winch System, 3 cols)
      const u1X=194,u1W=432,u1Cols=2;
      const u2X=638,u2W=436,u2Cols=2;
      const u3X=1086,u3W=440,u3Cols=3;
      const upperRows=Math.max(1,Math.ceil(z1AuxBoom.length/u1Cols),Math.ceil(z2MainBoom.length/u2Cols),Math.ceil(z3Hoist.length/u3Cols));
      const upperCardH=upperRows*cardRowH+36;

      placeZoneCard(u1X,upperY,u1W,upperCardH,u1Cols,'1','AUXILIARY SCRAPER BOOM','400 MM CHAIN · BLADES',z1AuxBoom,'#f7faf2','#b6c8af');
      placeZoneCard(u2X,upperY,u2W,upperCardH,u2Cols,'2','MAIN SCRAPER BOOM (1850 TPH)','500 MM CHAIN · HARDOX',z2MainBoom,'#f3f8ef','#9eb898');
      placeZoneCard(u3X,upperY,u3W,upperCardH,u3Cols,'3','PORTAL BOOM HOIST WINCH','45 kW VFD · Ø1300 DRUM',z3Hoist,'#f2f7f8','#96b8c2');

      // Tier 2: Center 55.8 m Span Portal Bridge Scraper Reclaimer Kinematic Profile
      profileBandY=upperY+upperCardH+14;
      const pTop=profileBandY,pBot=pTop+profileBandH,railY=pBot-16;
      if(self&&!positions.has(s.id))positions.set(s.id,{x:260,y:pTop+18,w:1180,h:profileBandH-36});

      decor.push(
        `<rect x="${u1X}" y="${pTop}" width="${u3X+u3W-u1X}" height="${profileBandH}" rx="12" fill="#e6efe0" fill-opacity=".68" stroke="#96ae92" stroke-width="1.6"/>`,
        // 55.8 m span portal rails
        `<path d="M225 ${railY}H1495" class="ps-rail"/>`,
        // 55.8 m Span Portal Arch Frame (Left Fixed Leg at x=295 to Right Hinged Leg at x=1425)
        `<path d="M295 ${railY-8}L395 ${pTop+18}H1325L1425 ${railY-8}" fill="none" stroke="#456b5e" stroke-width="6.5" stroke-linejoin="round"/>`,
        `<path d="M355 ${pTop+44}H1365" fill="none" stroke="#6c8c7e" stroke-width="2.5" stroke-dasharray="8 4"/>`,
        `<circle cx="285" cy="${railY-5}" r="7" class="ps-wheel"/><circle cx="310" cy="${railY-5}" r="7" class="ps-wheel"/>`,
        `<circle cx="1410" cy="${railY-5}" r="7" class="ps-wheel"/><circle cx="1435" cy="${railY-5}" r="7" class="ps-wheel"/>`,
        text(860,pTop+13,'55.8 M SPAN PORTAL A-FRAME BRIDGE & CROWN HOIST SHEAVES (DRAWING 175138-ISG-1)','ps-belt-flow-arrow'),
        // Twin Stockpile Cones beneath portal arch
        `<path d="M445 ${railY-2}L565 ${pTop+52}L685 ${railY-2}Z" fill="url(#ps-coal)" fill-opacity=".55" stroke="#496360" stroke-width="1.5"/>`,
        `<path d="M775 ${railY-2}L935 ${pTop+42}L1095 ${railY-2}Z" fill="url(#ps-coal)" fill-opacity=".75" stroke="#354e4c" stroke-width="1.8"/>`,
        // Hoist Suspension Ropes from Portal Crown
        `<path d="M535 ${pTop+18}V${pTop+62}M965 ${pTop+18}V${pTop+56}" stroke="#397587" stroke-width="2.5" stroke-dasharray="4 3"/>`,
        // Auxiliary Scraper Boom (left) & Main Scraper Boom (center-right scraping toward reclaim conveyor at right leg)
        `<path d="M415 ${railY-18}L645 ${pTop+56}" stroke="#b08544" stroke-width="7" stroke-linecap="round"/>`,
        `<path d="M420 ${railY-18}L640 ${pTop+56}" stroke="#4e6259" stroke-width="2.5" stroke-dasharray="4 5"/>`,
        `<path d="M745 ${pTop+48}L1355 ${railY-16}" stroke="#ab7337" stroke-width="8.5" stroke-linecap="round"/>`,
        `<path d="M750 ${pTop+48}L1350 ${railY-16}" stroke="#354e4c" stroke-width="3" stroke-dasharray="5 5"/>`,
        // Reclaim discharge chute at right portal leg
        `<polygon points="1352,${railY-26} 1388,${railY-26} 1396,${railY-4} 1360,${railY-4}" fill="#d8c390" stroke="#8b7340" stroke-width="1.6"/>`,
        text(535,pTop+46,'AUX SCRAPER BOOM  ▶▶','ps-belt-flow-arrow'),
        text(1065,pTop+42,'MAIN SCRAPER BOOM (1850 TPH)  ▶▶▶  RECLAIM BELT','ps-belt-flow-arrow'),
        text(860,railY-5,'PORTAL TRAVEL BOGIES (Ø630 MM WHEELS · 55.8 M RAIL SPAN)','ps-belt-flow-arrow')
      );

      // Tier 3: Zone 4 (Main Scraper Boom Drive Powertrain, 3 cols) + Zone 5 (Auxiliary Scraper Boom Drive Powertrain, 3 cols)
      const driveY=profileBandY+profileBandH+14;
      const d1X=194,d1W=658,d1Cols=Math.min(3,Math.max(1,z4MainDrive.length));
      const d2X=864,d2W=662,d2Cols=Math.min(3,Math.max(1,z5AuxDrive.length));
      const driveCardH=144+42;

      const placeDriveCard=(cardX,cardW,cols,badgeNum,title,items)=>{
        const shaftY=driveY+38+31;
        const dStep=Math.floor((cardW-32)/Math.max(1,cols));
        const dBoxW=124,dBoxH=62;
        const startX=cardX+16+Math.round((dStep-dBoxW)/2);
        decor.push(
          `<rect x="${cardX}" y="${driveY}" width="${cardW}" height="${driveCardH}" rx="10" fill="#f3f0f8" fill-opacity=".78" stroke="#a697c2" stroke-width="1.8"/>`,
          `<rect x="${cardX+10}" y="${driveY+9}" width="20" height="18" rx="5" fill="#5e4982"/>`,
          `<text x="${cardX+20}" y="${driveY+22}" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">${safe(badgeNum)}</text>`,
          text(cardX+36,driveY+21,title,'ps-zone-label','start'),
          items.length>1?`<path class="ps-belt-shaft" d="M${startX+28} ${shaftY}H${startX+(items.length-1)*dStep+dBoxW-28}"/>`:``
        );
        items.forEach((n,i)=>put(n,startX+i*dStep,driveY+38,dBoxW,dBoxH));
      };

      placeDriveCard(d1X,d1W,d1Cols,'4','MAIN BOOM DRIVE POWERTRAIN (2×110 kW VFD → COUPLINGS → 180:1 GEARBOXES)',z4MainDrive);
      placeDriveCard(d2X,d2W,d2Cols,'5','AUX BOOM DRIVE POWERTRAIN (2×30 kW VFD → COUPLINGS → 160:1 GEARBOXES)',z5AuxDrive);

      // Tier 4: Zone 6 (Portal Gantry Long-Travel, Rail Clamps & Storm Anchors, 3 cols) + Zone 7 (Cable Reels & Dual Lubrication, 2 cols) + Zone 8 (Onboard DSS & Yard Services, 2 cols)
      curY=driveY+driveCardH+16;
      const z8All=[...z8Services,...auxOutside].filter(n=>!positions.has(n.id));
      const b1X=194,b1W=520,b1Cols=3;
      const b2X=726,b2W=388,b2Cols=2;
      const b3X=1126,b3W=400,b3Cols=2;
      const botRows=Math.max(1,Math.ceil(z6Travel.length/b1Cols),Math.ceil(z7ReelsLube.length/b2Cols),Math.ceil(z8All.length/b3Cols));
      const botCardH=botRows*cardRowH+36;

      placeZoneCard(b1X,curY,b1W,botCardH,b1Cols,'6','PORTAL TRAVEL & RAIL CLAMPS','55.8 M SPAN · BOGIES',z6Travel,'#f2f7f4','#8fb0a1');
      placeZoneCard(b2X,curY,b2W,botCardH,b2Cols,'7','CABLE REELS & LUBRICATION','REELS · GREASE & OIL',z7ReelsLube,'#fbf7ec','#d2be8c');
      placeZoneCard(b3X,curY,b3W,botCardH,b3Cols,'8','ONBOARD DSS & YARD SERVICES','DSS · DCS · SPDS QRC',z8All,'#eff5f6','#9ebec7');
      curY+=botCardH+16;
    }

    const frameH=curY-frameY;
    decor.unshift(
      `<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="14" class="ps-building-frame"/>`,
      text(frameX+20,frameY+22,`${s.title.toUpperCase()} · ${s.kind==='stacker'?'ANATOMICAL LUFFING-SLEWING STACKER PROFILE, SUBSYSTEM ZONES & POWERTRAIN':'ANATOMICAL 55.8 M PORTAL BRIDGE SCRAPER RECLAIMER PROFILE, SUBSYSTEM ZONES & POWERTRAINS'}`,'ps-zone-label','start')
    );

    // Left Column Dock: UPSTREAM SOURCE (x=12..164)
    let leftBottom=0;
    if(upstream.length){
      const inH=upstream.length*158+42;
      decor.push(
        `<rect x="12" y="${upperY}" width="152" height="${inH}" rx="10" fill="#fbf8f0" fill-opacity=".82" stroke="#cbb88e" stroke-width="1.6"/>`,
        text(88,upperY+21,s.kind==='stacker'?'UPSTREAM YARD BELT':'STOCKPILE SOURCE','ps-zone-label')
      );
      upstream.forEach((n,i)=>put(n,22,upperY+36+i*158,132,64));
      leftBottom=upperY+inH;
    }

    // Right Column Dock: DOWNSTREAM ROUTE (x=1556..1708)
    let rightBottom=0;
    if(downstream.length){
      const outH=downstream.length*158+42;
      decor.push(
        `<rect x="1556" y="${upperY}" width="152" height="${outH}" rx="10" fill="#fbf8f0" fill-opacity=".82" stroke="#cbb88e" stroke-width="1.6"/>`,
        text(1632,upperY+21,s.kind==='stacker'?'STOCKPILE TARGET':'RECLAIM CONVEYOR','ps-zone-label')
      );
      downstream.forEach((n,i)=>put(n,1566,upperY+36+i*158,132,64));
      rightBottom=upperY+outH;
    }

    const upSet=new Set(upstream.map(n=>n.id));
    const downSet=new Set(downstream.map(n=>n.id));
    const entryNode=s.kind==='stacker'?(anat.z1Tripper[0]||anat.z2BoomBelt[0]):(anat.z2MainBoom[0]||anat.z1AuxBoom[0]);
    const exitNode=s.kind==='stacker'?(anat.z2BoomBelt[0]||anat.z1Tripper[0]):(anat.z2MainBoom[0]);

    for(const u of upstream){
      const pu=positions.get(u.id);
      if(pu)routes.set(u.id+'>'+(entryNode?entryNode.id:s.id),`M${pu.x+pu.w+2} ${Math.round(pu.y+pu.h/2)}H170V${profileBandY+Math.round(profileBandH/2)}H225`);
    }
    for(const v of downstream){
      const pv=positions.get(v.id);
      if(pv)routes.set((exitNode?exitNode.id:s.id)+'>'+v.id,`M1495 ${profileBandY+Math.round(profileBandH/2)}H1548V${Math.round(pv.y+pv.h/2)}H${pv.x-4}`);
    }

    const remappedEdges=s.edges.map(a=>{
      if(a.context?.network==='material'){
        if(upSet.has(a.canonical_subject)&&a.canonical_object===s.id&&entryNode)return {...a,canonical_object:entryNode.id};
        if(a.canonical_subject===s.id&&downSet.has(a.canonical_object)&&exitNode)return {...a,canonical_subject:exitNode.id};
      }
      return a;
    });

    const cleanEdges=remappedEdges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      if(routes.has(u+'>'+v))return true;
      if(a.context?.network==='mechanical'&&driveSet.has(u)&&driveSet.has(v)){
        const pu=positions.get(u),pv=positions.get(v);
        if(Math.abs(pu.y-pv.y)<25&&pv.x>pu.x&&pv.x-pu.x<320)return true;
      }
      return false;
    });

    const allClean=[...cleanEdges,...xrayExtraEdges(positions,cleanEdges)];
    s.width=1720;
    s.height=Math.max(820,frameY+frameH+36,leftBottom+40,rightBottom+40);
    s.initialHeight=Math.min(s.height,960);
    return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:19})).join('');
  }

  function conveyorMechanicalScene(){
    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const put=(n,x,y,w=144,h=72,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};

    const beltAndPulleys=topoSortBand(parts.filter(n=>['belt','pulley'].includes(n.kind)&&!/take-up pulley/i.test(n.label)),s.edges);
    const idlers=topoSortBand(parts.filter(n=>!beltAndPulleys.includes(n)&&n.kind==='idler'),s.edges);
    const takeupParts=topoSortBand(parts.filter(n=>!beltAndPulleys.includes(n)&&!idlers.includes(n)&&(['takeup','counterweight','hydraulic','cylinder'].includes(n.kind)||/take-up|counterweight|hgtu/i.test(n.label))),s.edges);
    const cleanersAndChutes=topoSortBand(parts.filter(n=>!beltAndPulleys.includes(n)&&!idlers.includes(n)&&!takeupParts.includes(n)),s.edges);

    const frameX=175,frameW=880,centerX=frameX+frameW/2,rowH=162;
    let curY=58;
    const frameTop=curY;
    const bands=[];

    const layoutBand=(label,items)=>{
      if(!items.length)return;
      bands.push([curY,label]);
      const rowY=curY+30,cols=Math.min(items.length,4),spacing=198,boxW=144;
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,rowY+r*rowH,boxW,72);
      });
      curY=rowY+Math.ceil(items.length/cols)*rowH;
    };

    layoutBand('BELT & DRUMS',beltAndPulleys);
    layoutBand('IDLER GROUPS',idlers);
    layoutBand('CLEANERS & SKIRTS',cleanersAndChutes);
    layoutBand('TAKE-UP SYSTEM',takeupParts);

    const frameH=Math.max(240,curY-frameTop+12);
    decor.unshift(
      `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
      text(frameX+22,frameTop+22,s.title.toUpperCase()+' · PHYSICAL MECHANICAL LOOP','ps-zone-label','start')
    );
    bands.forEach(([y,lbl],idx)=>{
      if(idx>0)decor.push(`<path d="M${frameX+14} ${y}H${frameX+frameW-14}" class="ps-floor"/>`);
      decor.push(text(frameX-14,y+52,lbl,'ps-zone-label','end'));
    });

    if(outside.length){
      const sideY=frameTop+frameH+48;
      decor.push(text(centerX,sideY-16,'CONNECTED DRIVE & UPSTREAM / DOWNSTREAM INTERFACES','ps-zone-label'));
      outside.forEach((n,i)=>put(n,175+(i%4)*210,sideY+Math.floor(i/4)*152,155,74));
      curY=sideY+Math.ceil(outside.length/4)*152+20;
    }

    const takeupSet=new Set(takeupParts.map(n=>n.id));
    const cleanEdges=s.edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      if(takeupSet.has(u)&&takeupSet.has(v)&&Math.abs(positions.get(u).y-positions.get(v).y)<30)return true;
      return false;
    });
    s.width=1200;
    s.height=Math.max(760,curY+35);
    s.initialHeight=Math.min(s.height,920);
    return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
  }

  function structuredEquipmentScene(){
    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    if(!parts.length&&s.kind!=='switchboard'&&!/switchgear|switch board|mcc-\d/i.test(s.title))return null;
    const put=(n,x,y,w=148,h=74,title,sub)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title,sub});};

    // 1. Bespoke Longitudinal & Radial Rotor Cutaway Schematic (EBC-1 / EBC-2 Rotor Assembly, Drawing CS.1.1-12483)
    if(s.kind==='crusher-rotor'){
      const frameX=105,frameTop=46,frameW=1005;
      const shaftParts=parts.filter(n=>/rotor shaft|end discs|spacing discs|suspension arms/i.test(n.label)).sort((a,b)=>{
        const r=l=>/rotor shaft/i.test(l)?1:/end discs/i.test(l)?2:/spacing discs/i.test(l)?3:4;
        return r(a.label)-r(b.label);
      });
      const hammerParts=parts.filter(n=>!shaftParts.includes(n)).sort((a,b)=>{
        const r=l=>/suspension bars/i.test(l)?1:/ring hammers/i.test(l)?2:3;
        return r(a.label)-r(b.label);
      });

      // Technical longitudinal rotor shaft + disc barrel + radial hammer swing circle cutaway backdrop
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="432" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · LONGITUDINAL ROTOR BARREL & Ø1600 MM RADIAL HAMMER SWING CUTAWAY (CS.1.1-12483)`,'ps-zone-label','start'),
        // Longitudinal stepped shaft & disc barrel cross-section graphic
        `<rect x="135" y="142" width="665" height="22" rx="4" fill="#d9e4dc" stroke="#5b7a69" stroke-width="2" opacity=".7"/>`,
        `<path d="M120 153H825" stroke="#7b639e" stroke-width="5" stroke-dasharray="10 4" opacity=".65"/>`,
        `<rect x="245" y="106" width="18" height="94" rx="3" fill="#c5d5c8" stroke="#4d6d5c" stroke-width="1.8" opacity=".65"/>`,
        `<rect x="665" y="106" width="18" height="94" rx="3" fill="#c5d5c8" stroke="#4d6d5c" stroke-width="1.8" opacity=".65"/>`,
        `<path d="M285 112V194M325 112V194M365 112V194M405 112V194M445 112V194M485 112V194M525 112V194M565 112V194M605 112V194M645 112V194" stroke="#8da696" stroke-width="2" opacity=".55"/>`,
        // Radial hammer swing circle & screen cage cross-section callout on right side of frame
        `<circle cx="985" cy="252" r="88" fill="#eef4ec" stroke="#6c8776" stroke-width="2" stroke-dasharray="7 4" opacity=".85"/>`,
        `<circle cx="985" cy="252" r="56" fill="#dce6db" stroke="#4d6d5c" stroke-width="2" opacity=".85"/>`,
        `<circle cx="985" cy="252" r="18" fill="#7b639e" fill-opacity=".28" stroke="#5a4678" stroke-width="2"/>`,
        `<circle cx="985" cy="196" r="14" fill="#d8c390" stroke="#7d683b" stroke-width="2"/><circle cx="1041" cy="252" r="14" fill="#c7d5c8" stroke="#4a6958" stroke-width="2"/>`,
        `<circle cx="985" cy="308" r="14" fill="#d8c390" stroke="#7d683b" stroke-width="2"/><circle cx="929" cy="252" r="14" fill="#c7d5c8" stroke="#4a6958" stroke-width="2"/>`,
        `<path d="M892 262Q905 355 1008 353" fill="none" stroke="#395747" stroke-width="6" stroke-dasharray="8 3"/>`,
        text(985,152,'RADIAL CUTAWAY · 592 RPM','ps-belt-flow-arrow'),
        text(985,372,'SCREEN CAGE ARC (35 MM GAP)','ps-belt-flow-arrow'),
        `<path d="M${frameX+14} 258H860" class="ps-floor"/>`,
        text(frameX+20,94,'TIER 1 · FORGED EN24 ROTOR SHAFT, CLAMPING END DISCS (2x), SPACING DISCS (58x) & HARDFACED SUSPENSION ARMS (28x)','ps-zone-label','start'),
        text(frameX+20,278,'TIER 2 · 4-ROW SUSPENSION BARS (Ø60x2195 EN24), RING HAMMERS (28 TOOTHED + 28 PLAIN) & MAINTENANCE EXTRACTOR BAR','ps-zone-label','start')
      );

      shaftParts.forEach((n,i)=>put(n,132+i*186,112,144,74));
      hammerParts.forEach((n,i)=>put(n,165+i*240,296,168,76));

      // Explicit clean step-by-step mechanical torque/retention path
      for(let i=0;i<shaftParts.length-1;i++){
        const u=positions.get(shaftParts[i].id),v=positions.get(shaftParts[i+1].id);
        if(u&&v)routes.set(shaftParts[i].id+'>'+shaftParts[i+1].id,`M${u.x+u.w+4} ${u.y+37}H${v.x-6}`);
      }
      if(shaftParts.length&&hammerParts.length){
        const lastShaft=shaftParts.at(-1),firstHammer=hammerParts[0];
        const u=positions.get(lastShaft.id),v=positions.get(firstHammer.id);
        if(u&&v)routes.set(lastShaft.id+'>'+firstHammer.id,`M${u.x+Math.round(u.w/2)} ${u.y+u.h+32}V258H${v.x+Math.round(v.w/2)}V${v.y-4}`);
      }
      for(let i=0;i<hammerParts.length-1;i++){
        const u=positions.get(hammerParts[i].id),v=positions.get(hammerParts[i+1].id);
        if(u&&v)routes.set(hammerParts[i].id+'>'+hammerParts[i+1].id,`M${u.x+u.w+4} ${u.y+38}H${v.x-6}`);
      }

      let curY=505;
      if(outside.length){
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${Math.ceil(outside.length/4)*154+46}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,'CONNECTED BEARING PEDESTALS (SKF 22240), SCOOP COUPLING TORQUE INPUT & CRUSHING CAGE INTERFACES','ps-zone-label','start')
        );
        outside.forEach((n,i)=>put(n,135+(i%4)*235,curY+38+Math.floor(i/4)*152,175,74));
        curY+=Math.ceil(outside.length/4)*152+60;
      }

      const partIds=new Set(parts.map(n=>n.id));
      const cleanEdges=s.edges.filter(a=>partIds.has(a.canonical_subject)&&partIds.has(a.canonical_object)&&routes.has(a.canonical_subject+'>'+a.canonical_object));
      s.width=1200;s.height=Math.max(760,curY+20);s.initialHeight=Math.min(s.height,880);
      return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // 2. Bespoke Onboard Water Mist Dust Suppression P&ID Schematic (SUL-1..3, EAD-1..4, EAF-1..4 Onboard DSS)
    if(/onboard.*dust-suppression|onboard.*plain-water dss/i.test(s.title)){
      const isReclaimer=/^eaf-\d+/i.test(s.title);
      const isStacker=/^ead-\d+/i.test(s.title);
      const frameX=55,frameTop=42,frameW=1410;
      const sprayZones=parts.filter(n=>n.kind==='spray'||/spray|ap-\d|zone-\d|solenoid box/i.test(n.label)).sort((a,b)=>{
        const r=x=>/solenoid box/i.test(x.label)&&!/ap-1/i.test(x.label)?0:1;
        return r(a)-r(b)||a.label.localeCompare(b.label,undefined,{numeric:true});
      });
      const storageSupply=parts.filter(n=>!sprayZones.includes(n)&&(['hose-reel','tank','level-sensor','panel'].includes(n.kind)||/hose reel|water tank|inlet solenoid|level switch|control panel|local dss panel|starter/i.test(n.label))).sort((a,b)=>{
        const r=x=>x.kind==='hose-reel'?1:/inlet solenoid/i.test(x.label)?2:x.kind==='tank'?3:x.kind==='level-sensor'?4:5;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });
      const pumpFilter=parts.filter(n=>!sprayZones.includes(n)&&!storageSupply.includes(n)).sort((a,b)=>{
        const r=x=>x.kind==='filter'?1:/differential/i.test(x.label)?2:x.kind==='pump'?3:/discharge pressure/i.test(x.label)?4:/relief/i.test(x.label)?5:6;
        return r(a)-r(b)||a.label.localeCompare(b.label);
      });

      const s1Cols=storageSupply.length>3?2:1;
      const s2Cols=pumpFilter.length>3?2:1;
      const s3Cols=sprayZones.length>3?2:1;
      const maxRows=Math.max(Math.ceil(storageSupply.length/s1Cols),Math.ceil(pumpFilter.length/s2Cols),Math.ceil(sprayZones.length/s3Cols),2);
      const stageH=maxRows*158+92;

      const s1Title=isReclaimer?'STAGE 1 · HOSE REEL, INLET SV & 2000 L SS TANK':'STAGE 1 · HOSE REEL, FLOAT VALVE & 10 m³ SS TANK';
      const s2Title=isReclaimer?'STAGE 2 · PRP-1A PUMP (1.0 m³/h), PRV & PS':'STAGE 2 · STRAINER, 1W+1S PUMP SKID & PRV';
      const s3Title=isReclaimer?'STAGE 3 · SB20-PRM1 & AP-1 MIST HEADER (6 NOZZLES)':isStacker?'STAGE 3 · SPRAY HEADERS AP-1..3 (34 NOZZLES)':'STAGE 3 · SPRAY HEADERS (31 NOZZLES)';
      const pBadge=isReclaimer?'4.5b':isStacker?'5.0b':'7.5b';

      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${stageH}" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · ONBOARD WATER-MIST P&ID HYDRAULIC FLOW, INTERLOCKS & NOZZLE MANIFOLD SCHEMATIC`,'ps-zone-label','start'),
        `<path d="M515 ${frameTop+38}V${frameTop+stageH-14}M985 ${frameTop+38}V${frameTop+stageH-14}" class="ps-floor"/>`,
        text(285,frameTop+54,s1Title,'ps-zone-label'),
        text(750,frameTop+54,s2Title,'ps-zone-label'),
        text(1225,frameTop+54,s3Title,'ps-zone-label'),
        // Pressurized distribution header pipe & PI gauge between Stage 2 and Stage 3
        `<path d="M945 ${frameTop+138}H1012M1012 ${frameTop+108}V${frameTop+stageH-42}" stroke="#49899c" stroke-width="6" fill="none" stroke-linecap="round"/>`,
        `<circle cx="1012" cy="${frameTop+82}" r="14" fill="#fcfdf8" stroke="#366c7d" stroke-width="2"/>`,
        text(1012,frameTop+86,pBadge,'ps-belt-flow-arrow')
      );

      const placeColItems=(items,xBase,colW,cols)=>{
        items.forEach((n,i)=>{
          const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
          const step=Math.floor(colW/Math.max(1,cols));
          const bw=cols===2?168:190,bh=66;
          const startX=xBase+Math.round((colW-rowCount*step)/2+(step-bw)/2);
          put(n,startX+c*step,frameTop+82+r*158,bw,bh);
        });
      };

      placeColItems(storageSupply,75,420,s1Cols);
      placeColItems(pumpFilter,535,430,s2Cols);
      placeColItems(sprayZones,1032,415,s3Cols);

      let curY=frameTop+stageH+24;
      if(outside.length){
        const dockCols=Math.min(outside.length,5);
        const dockH=Math.ceil(outside.length/dockCols)*152+46;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,isReclaimer||isStacker?'CONNECTED SPDS MAKEUP QRC SUPPLY & DUST-SUPPRESSED MACHINE TRANSFER ZONES':'CONNECTED JETTY WATER SUPPLY & DUST-SUPPRESSED TRANSFER ZONES','ps-zone-label','start')
        );
        outside.forEach((n,i)=>put(n,frameX+32+(i%dockCols)*272,curY+38+Math.floor(i/dockCols)*152,186,68));
        curY+=dockH+20;
      }

      const partIds=new Set(parts.map(n=>n.id));
      const cleanEdges=filterCleanInternalEdges(s.edges,positions,partIds).filter(a=>{
        const u=positions.get(a.canonical_subject),v=positions.get(a.canonical_object);
        return u&&v&&v.x>=u.x-20&&Math.abs(v.x-u.x)<=520&&Math.abs(v.y-u.y)<=220;
      });
      const allClean=[...cleanEdges,...xrayExtraEdges(positions,cleanEdges)];
      s.width=1520;s.height=Math.max(760,curY+20);s.initialHeight=Math.min(s.height,920);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:21})).join('');
    }

    // 3. Bespoke Centralized Dual-Line & Progressive Grease / Chain Oil Lubrication Schematic (SUL-1..3, EAD-1..4, EAF-1..4, EBE-CES-1..2)
    if(s.kind==='lubrication'||/lubrication/i.test(s.title)){
      const isChainOil=/chain oil/i.test(s.title);
      const frameX=75,frameTop=44,frameW=1250;
      const manualPumps=parts.filter(n=>/manual hand-pump/i.test(n.label));
      const pumpsAndPanels=parts.filter(n=>!manualPumps.includes(n)&&(['grease-pump','panel','pump','tank'].includes(n.kind)||/pump|panel|timer|reservoir/i.test(n.label)));
      const distAndNozzles=parts.filter(n=>!pumpsAndPanels.includes(n)&&!manualPumps.includes(n)&&(['distributor-block','spray','slew','bogie','pulley'].includes(n.kind)||/distributor|nozzle|slewing|wheels|pulleys/i.test(n.label)));
      const middleItems=[...parts.filter(n=>!pumpsAndPanels.includes(n)&&!distAndNozzles.includes(n)&&!manualPumps.includes(n)),...manualPumps];

      const maxRows=Math.max(pumpsAndPanels.length,middleItems.length,distAndNozzles.length,2);
      const stageH=Math.max(440,maxRows*162+96);
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${stageH}" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,`${(s.title.length>54?s.title.slice(0,52)+'…':s.title).toUpperCase()} · ${isChainOil?'MOTORIZED DRIP / PROJECTION CHAIN OIL LUBRICATION SCHEMATIC':'CENTRALIZED DUAL-LINE & PROGRESSIVE GREASE LUBRICATION SCHEMATIC'}`,'ps-zone-label','start'),
        `<path d="M485 ${frameTop+38}V${frameTop+stageH-14}M895 ${frameTop+38}V${frameTop+stageH-14}" class="ps-floor"/>`,
        text(280,frameTop+50,isChainOil?'STAGE 1 · MFE5 OIL PUMP & RESERVOIR':'STAGE 1 · PUMP STATION & TIMER CONTROL','ps-zone-label'),
        text(690,frameTop+50,isChainOil?'STAGE 2 · LEVEL INTERLOCK & PROTECTION':'STAGE 2 · DU1-GKS CHANGEOVER, RELIEF & LEVEL','ps-zone-label'),
        text(1110,frameTop+50,isChainOil?'STAGE 3 · METERING & 4 PROJECTION NOZZLES':'STAGE 3 · VSG/SSV DISTRIBUTORS & BEARING ZONES','ps-zone-label'),
        // Supply header lines placed cleanly at y = frameTop+76..84 with label at frameTop+68 and hotspots starting at y = frameTop+106
        `<path d="M415 ${frameTop+78}H965" stroke="#2c788c" stroke-width="4" stroke-dasharray="10 4" opacity=".68"/>`,
        isChainOil?``:`<path d="M415 ${frameTop+86}H965" stroke="#9c7a38" stroke-width="4" stroke-dasharray="6 4" opacity=".68"/>`,
        text(690,frameTop+70,isChainOil?'PRESSURIZED CHAIN OIL DELIVERY HEADER TO BOOM SPROCKETS':'DUAL-LINE HIGH-PRESSURE GREASE HEADERS (LINE A & LINE B · 400 BAR)','ps-belt-flow-arrow')
      );

      pumpsAndPanels.forEach((n,i)=>put(n,185,frameTop+106+i*162,195,68));
      middleItems.forEach((n,i)=>put(n,592,frameTop+106+i*162,195,68));
      distAndNozzles.forEach((n,i)=>put(n,1005,frameTop+106+i*162,205,68));

      let curY=frameTop+stageH+26;
      if(outside.length){
        const dockH=Math.ceil(outside.length/4)*152+46;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,'LUBRICATED SLEW / LUFFING / BOOM / LONG-TRAVEL BOGIE BEARINGS & ASSOCIATED MACHINERY','ps-zone-label','start')
        );
        outside.forEach((n,i)=>put(n,frameX+42+(i%4)*295,curY+38+Math.floor(i/4)*152,190,68));
        curY+=dockH+20;
      }

      const partIds=new Set(parts.map(n=>n.id));
      const cleanEdges=filterCleanInternalEdges(s.edges,positions,partIds).filter(a=>{
        const u=positions.get(a.canonical_subject),v=positions.get(a.canonical_object);
        return u&&v&&v.x>=u.x-10&&v.x-u.x<=460;
      });
      const allClean=[...cleanEdges,...xrayExtraEdges(positions,cleanEdges)];
      s.width=1400;s.height=Math.max(740,curY+20);s.initialHeight=Math.min(s.height,880);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:23})).join('');
    }

    // 4. Bespoke Hydraulic Power Pack (HPP) P&ID Schematic (Stacker Slew & Luffing HPPs, Drawing 175145-ISG)
    if(s.kind==='hydraulic'||/hydraulic power pack/i.test(s.title)){
      const frameX=75,frameTop=44,frameW=1250;
      const resAndPumps=parts.filter(n=>['tank','motor','pump'].includes(n.kind)||/tank|reservoir|pump|motor em1/i.test(n.label));
      const valvesAndCtrl=parts.filter(n=>!resAndPumps.includes(n)&&(['valve','panel'].includes(n.kind)||/valve|directional|controller|drive control/i.test(n.label)));
      const coolAndInst=parts.filter(n=>!resAndPumps.includes(n)&&!valvesAndCtrl.includes(n));

      const s1Cols=resAndPumps.length>3?2:1;
      const s2Cols=valvesAndCtrl.length>3?2:1;
      const s3Cols=coolAndInst.length>3?2:1;
      const maxRows=Math.max(Math.ceil(resAndPumps.length/s1Cols),Math.ceil(valvesAndCtrl.length/s2Cols),Math.ceil(coolAndInst.length/s3Cols),2);
      const stageH=maxRows*158+88;

      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${stageH}" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · HYDRAULIC POWER PACK (HPP) CIRCUIT, PROPORTIONAL MANIFOLD & OIL COOLING P&ID`,'ps-zone-label','start'),
        `<path d="M495 ${frameTop+38}V${frameTop+stageH-14}M905 ${frameTop+38}V${frameTop+stageH-14}" class="ps-floor"/>`,
        text(285,frameTop+52,'STAGE 1 · OIL RESERVOIR, PUMP & MOTOR EM1','ps-zone-label'),
        text(700,frameTop+52,'STAGE 2 · PROPORTIONAL & OVER-CENTRE VALVES','ps-zone-label'),
        text(1115,frameTop+52,'STAGE 3 · AIR-OIL COOLER EM2, FILTERS & SENSORS','ps-zone-label')
      );

      const placeCol=(items,xBase,colW,cols)=>{
        items.forEach((n,i)=>{
          const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
          const step=Math.floor(colW/Math.max(1,cols));
          const bw=cols===2?168:192,bh=66;
          const startX=xBase+Math.round((colW-rowCount*step)/2+(step-bw)/2);
          put(n,startX+c*step,frameTop+78+r*158,bw,bh);
        });
      };
      placeCol(resAndPumps,85,395,s1Cols);
      placeCol(valvesAndCtrl,508,384,s2Cols);
      placeCol(coolAndInst,918,395,s3Cols);

      let curY=frameTop+stageH+24;
      if(outside.length){
        const dockH=Math.ceil(outside.length/4)*152+46;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,'CONNECTED HYDRAULIC ACTUATORS (LUFFING CYLINDERS / SLEW MOTORS) & PARENT SUBSYSTEM','ps-zone-label','start')
        );
        outside.forEach((n,i)=>put(n,frameX+42+(i%4)*295,curY+38+Math.floor(i/4)*152,190,68));
        curY+=dockH+20;
      }
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1400;s.height=Math.max(720,curY+20);s.initialHeight=Math.min(s.height,880);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // 5. Bespoke Stockyard SPDS System Schematic (DS-1 Common Station & Coal Yard 1..4 SPDS Ring Header / Sectors / Risers)
    if(/coal yard \d+ spds|coal stockpile plain water ds system/i.test(s.title)){
      const isMainDS1=/ds-1/i.test(s.title);
      const frameX=55,frameTop=42,frameW=1410;
      const headersAndPumps=parts.filter(n=>['pump','filter','pipe'].includes(n.kind)||/header|pump|filter|recirculation|qrc/i.test(n.label));
      const controllers=parts.filter(n=>!headersAndPumps.includes(n)&&(['panel','sensor'].includes(n.kind)||/controller|sc-0\d|pressure switch|starter/i.test(n.label)));
      const sectorsAndRisers=parts.filter(n=>!headersAndPumps.includes(n)&&!controllers.includes(n)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));

      let curY=frameTop+42;
      const bands=[];
      const placeBand=(lbl,items,cols=5)=>{
        if(!items.length)return;
        bands.push([curY,lbl]);
        const rowY=curY+28,step=Math.floor((frameW-40)/cols),bw=cols>=6?158:182,bh=66;
        items.forEach((n,i)=>{
          const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
          const startX=frameX+20+Math.round(((frameW-40)-rowCount*step)/2+(step-bw)/2);
          put(n,startX+c*step,rowY+r*156,bw,bh);
        });
        curY=rowY+Math.ceil(items.length/cols)*156+8;
      };

      placeBand(isMainDS1?'1 · SPDSP-1A/1B BOOSTER PUMPS, DUPLEX SUCTION STRAINER & COMMON DISTRIBUTION HEADERS':'1 · YARD PERIMETER RING HEADER & MACHINE MAKEUP QRC CONNECTIONS',headersAndPumps,Math.min(5,Math.max(2,headersAndPumps.length)));
      placeBand(isMainDS1?'2 · SEQUENTIAL CONTROLLERS (SC-02..04), LOCAL STARTER PANEL & PRESSURE SWITCHES':'2 · SEQUENTIAL CONTROLLER (SC-01..04) & AUTOMATIC SECTOR CONTROL GROUP',controllers,Math.min(5,Math.max(2,controllers.length)));
      placeBand(isMainDS1?'3 · YARD SPDS SUBSYSTEMS & ES-65PC SWIVELLING SPRINKLER ASSEMBLIES':'3 · SEQUENTIAL SPRINKLER SECTORS (S1..S14) & PERIMETER RISERS (28 SWIVELLING SPRINKLERS)',sectorsAndRisers,sectorsAndRisers.length>8?6:Math.min(4,Math.max(2,sectorsAndRisers.length)));

      const frameH=curY-frameTop+8;
      decor.unshift(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${frameH}" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · STOCKPILE PERIMETER DUST SUPPRESSION (SPDS) HYDRAULIC & SEQUENTIAL CONTROL SCHEMATIC`,'ps-zone-label','start')
      );
      bands.forEach(([y,lbl],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX+24,y+18,lbl,'ps-zone-label','start'));
      });

      // Filter connected items to top-level yard/plant interfaces so child hose-reels/tanks of machines don't clutter the dock
      const filteredOutside=outside.filter(n=>!/hose reel|water tank|compartment|motorized valve|level switch/i.test(n.label)||outside.length<=8);
      curY=frameTop+frameH+24;
      if(filteredOutside.length){
        const dCols=Math.min(filteredOutside.length,5);
        const dockH=Math.ceil(filteredOutside.length/dCols)*152+46;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,'CONNECTED WATER SUPPLY (TANK-2 / PUMP HOUSE-2), SERVED STOCKPILES (EAE-1..4) & YARD MACHINES','ps-zone-label','start')
        );
        filteredOutside.forEach((n,i)=>put(n,frameX+32+(i%dCols)*272,curY+38+Math.floor(i/dCols)*152,186,66));
        curY+=dockH+20;
      }
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(760,curY+20);s.initialHeight=Math.min(s.height,940);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:21})).join('');
    }

    // 6. Bespoke Coal Stockpile Yard Aggregate & Mobile Equipment Fleet Schematic
    if(s.title==='Coal Stockpile Yard'){
      const frameX=75,frameTop=44,frameW=1250;
      const yards=parts.filter(n=>n.kind==='yard').sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
      const mobileFleet=parts.filter(n=>!yards.includes(n));
      const stageH=385;
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${stageH}" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,'COAL STOCKPILE YARD · 4 PARALLEL YARD LANES (COAL YARDS 1–4) & MOBILE COAL HANDLING FLEET','ps-zone-label','start'),
        `<path d="M${frameX+14} ${frameTop+198}H${frameX+frameW-14}" class="ps-floor"/>`,
        text(frameX+24,frameTop+50,'1 · NUMBERED STOCKYARD LANES (COAL YARDS 1 TO 4 · STACKING, STORAGE & RECLAIMING)','ps-zone-label','start'),
        text(frameX+24,frameTop+218,'2 · STOCKYARD MOBILE EQUIPMENT FLEET (BEML BD355 DOZERS, BL200-1 PAY LOADERS & BL40 FRONT-END LOADERS)','ps-zone-label','start')
      );
      yards.forEach((n,i)=>put(n,135+i*285,frameTop+68,200,70));
      mobileFleet.forEach((n,i)=>put(n,115+i*235,frameTop+238,186,68));

      let curY=frameTop+stageH+26;
      if(outside.length){
        const dockH=Math.ceil(outside.length/4)*152+46;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,'SHARED STOCKPILE PLAIN-WATER DUST SUPPRESSION SYSTEM (DS-1)','ps-zone-label','start')
        );
        outside.forEach((n,i)=>put(n,frameX+42+(i%4)*295,curY+38+Math.floor(i/4)*152,195,68));
        curY+=dockH+20;
      }
      s.width=1400;s.height=Math.max(700,curY+20);s.initialHeight=Math.min(s.height,860);
      return decor.join('')+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // Helper to render a titled engineering zone card with a multi-column grid of hotspots
    const drawZoneCard=(x,y,w,cols,badge,title,subtitle,items,fill='#f6faf6',stroke='#9db5a5')=>{
      if(!items.length)return 0;
      const rows=Math.ceil(items.length/cols);
      const titleEstW=34+title.length*9.2;
      const subEstW=subtitle?subtitle.length*7.4+18:0;
      const stackSub=Boolean(subtitle&&(titleEstW+subEstW+28>w));
      const headH=stackSub?42:28;
      const cardH=rows*154+headH+14;
      decor.push(
        `<rect x="${x}" y="${y}" width="${w}" height="${cardH}" rx="9" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>`,
        `<rect x="${x}" y="${y}" width="${w}" height="${headH}" rx="9" fill="${stroke}" opacity=".22"/>`,
        `<circle cx="${x+18}" cy="${y+14}" r="9" fill="${stroke}"/>`,
        text(x+18,y+18,badge,'ps-belt-flow-arrow'),
        text(x+34,y+18,title,'ps-zone-label','start'),
        subtitle?(stackSub?text(x+34,y+33,subtitle,'ps-Subtle','start'):text(x+w-12,y+18,subtitle,'ps-Subtle','end')):''
      );
      const padX=14,availW=w-padX*2,step=Math.floor(availW/cols),bw=cols>=3?154:cols===2?168:192,bh=66;
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
        const sx=x+padX+Math.round((availW-rowCount*step)/2+(step-bw)/2);
        put(n,sx+c*step,y+headH+10+r*154,bw,bh);
      });
      return cardH;
    };

    const drawBottomDock=(frameX,curY,frameW,title,items,maxCols=5)=>{
      if(!items.length)return curY;
      const cols=Math.min(items.length,maxCols);
      const step=Math.floor((frameW-40)/cols),bw=cols>=5?176:192,bh=66;
      const dockH=Math.ceil(items.length/cols)*152+46;
      decor.push(
        `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
        text(frameX+22,curY+22,title,'ps-zone-label','start')
      );
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols;
        put(n,frameX+28+c*step,curY+38+r*152,bw,bh);
      });
      return curY+dockH+20;
    };

    // 7. Bespoke Grab Ship Unloader (Coal Ship Unloader-1..3 / SUL-1..3, 1700 TPH) & Coal Jetty Schematic
    if(s.kind==='ship'||s.title==='Coal Jetty'){
      const frameX=55,frameTop=40,frameW=1410;
      if(s.title==='Coal Jetty'){
        const unloaders=parts.filter(n=>n.kind==='ship').sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
        const auxJetty=parts.filter(n=>!unloaders.includes(n));
        decor.push(
          `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="390" rx="12" class="ps-building-frame"/>`,
          text(frameX+22,frameTop+22,'COAL JETTY · MARINE UNLOADING BERTH, 3 × 1700 TPH GRAB SHIP UNLOADERS (SUL-1..3) & JETTY CONVEYORS','ps-zone-label','start'),
          `<path d="M${frameX+14} ${frameTop+205}H${frameX+frameW-14}" class="ps-floor"/>`,
          text(frameX+24,frameTop+48,'1 · RAIL-MOUNTED 1700 TPH GRAB SHIP UNLOADERS (COAL SHIP UNLOADER-1, 2 & 3 · 31 M WATERSIDE OUTREACH)','ps-zone-label','start'),
          text(frameX+24,frameTop+228,'2 · LIMESTONE JETTY BELT CONVEYOR (LS-EAC-1) & JETTY PLAIN-WATER DUST-SUPPRESSION MAKEUP OUTLETS','ps-zone-label','start')
        );
        unloaders.forEach((n,i)=>put(n,145+i*380,frameTop+66,220,72));
        auxJetty.forEach((n,i)=>put(n,265+i*420,frameTop+248,220,72));
        const curY=drawBottomDock(frameX,frameTop+414,frameW,'CONNECTED RECEIVING JETTY BELT CONVEYORS (EAC-1A & EAC-1B) & RAW WATER SUPPLY',outside,5);
        s.width=1520;s.height=Math.max(700,curY+10);s.initialHeight=Math.min(s.height,880);
        return decor.join('')+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
      }

      // Grab Ship Unloader (SUL-1..3): Top Kinematic Flow Strip + 8 Engineering Zone Cards
      const z1Grab=parts.filter(n=>/grab|holding and closing/i.test(n.label));
      const z2BoomTrolley=parts.filter(n=>!z1Grab.includes(n)&&/trolley|boom/i.test(n.label));
      const z3HopperFeeder=parts.filter(n=>!z1Grab.includes(n)&&!z2BoomTrolley.includes(n)&&/hopper|vibro-feeder/i.test(n.label));
      const z4Shuttle=parts.filter(n=>!z1Grab.includes(n)&&!z2BoomTrolley.includes(n)&&!z3HopperFeeder.includes(n)&&/shuttle/i.test(n.label));
      const z5Gantry=parts.filter(n=>!z1Grab.includes(n)&&!z2BoomTrolley.includes(n)&&!z3HopperFeeder.includes(n)&&!z4Shuttle.includes(n)&&(/long-travel|rail-clamp|bogie|storm/i.test(n.label)||['bogie','rail-clamp'].includes(n.kind)));
      const z6Houses=parts.filter(n=>!z1Grab.includes(n)&&!z2BoomTrolley.includes(n)&&!z3HopperFeeder.includes(n)&&!z4Shuttle.includes(n)&&!z5Gantry.includes(n)&&(/cabin|machinery house|passenger lift|hoist/i.test(n.label)||['cabin','elevator','hoist'].includes(n.kind)));
      const z7Power=parts.filter(n=>!z1Grab.includes(n)&&!z2BoomTrolley.includes(n)&&!z3HopperFeeder.includes(n)&&!z4Shuttle.includes(n)&&!z5Gantry.includes(n)&&!z6Houses.includes(n)&&(/cable reel|electrical house|diesel-generator|anemometer/i.test(n.label)));
      const z8Fluid=parts.filter(n=>![...z1Grab,...z2BoomTrolley,...z3HopperFeeder,...z4Shuttle,...z5Gantry,...z6Houses,...z7Power].includes(n));

      // Top Tenova GA Elevation Cross-Section & Kinematic Coal Path Banner (Drawing 175155-ISG-TENOVA / Stability 175156-ISG)
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="218" rx="12" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+21,`${s.title.toUpperCase()} · TAKRAF TENOVA 1,700 TPH RAIL-MOUNTED GRAB SHIP UNLOADER — GA ELEVATION & KINEMATIC PROFILE (DRG 175155 / 175156)`,'ps-zone-label','start'),
        // Jetty Deck (EL 0.00 m) & Waterside Berth / 25,000 DWT Vessel Hold (left)
        `<path d="M${frameX+240} ${frameTop+188}H${frameX+742}" stroke="#5b7a6b" stroke-width="3.5"/>`,
        `<path d="M${frameX+20} ${frameTop+168}H${frameX+224}L${frameX+208} ${frameTop+204}H${frameX+20}Z" fill="#7c9a8d" stroke="#436355" stroke-width="2"/>`,
        `<path d="M${frameX+34} ${frameTop+202}L${frameX+70} ${frameTop+176}L${frameX+124} ${frameTop+172}L${frameX+184} ${frameTop+182}L${frameX+202} ${frameTop+202}Z" fill="url(#ps-coal)"/>`,
        text(frameX+116,frameTop+196,'25,000 DWT VESSEL HOLD','ps-banner-note'),
        // Portal Gantry Legs on 20.00 m CR100 Rail Span
        `<path d="M${frameX+338} ${frameTop+86}V${frameTop+184}M${frameX+352} ${frameTop+86}V${frameTop+184}M${frameX+584} ${frameTop+86}V${frameTop+184}M${frameX+598} ${frameTop+86}V${frameTop+184}" stroke="#416859" stroke-width="3"/>`,
        `<path d="M${frameX+352} ${frameTop+112}L${frameX+584} ${frameTop+112}M${frameX+352} ${frameTop+152}H${frameX+584}" stroke="#6b8a7c" stroke-width="1.8" stroke-dasharray="5 3"/>`,
        `<rect x="${frameX+324}" y="${frameTop+180}" width="42" height="7" rx="2" fill="#4a7060"/><rect x="${frameX+570}" y="${frameTop+180}" width="42" height="7" rx="2" fill="#4a7060"/>`,
        text(frameX+475,frameTop+205,'20.0 m CR100 RAIL SPAN · 40 × Ø630 mm WHEELS','ps-banner-note'),
        // Pylon Mast (EL +49.0 m at x=346) + Forestay & Backstay Boom Tie-Rods
        `<path d="M${frameX+332} ${frameTop+78}L${frameX+346} ${frameTop+36}L${frameX+364} ${frameTop+78}" fill="none" stroke="#3f6557" stroke-width="3.2"/>`,
        `<path d="M${frameX+346} ${frameTop+38}L${frameX+110} ${frameTop+78}M${frameX+346} ${frameTop+38}L${frameX+655} ${frameTop+58}" stroke="#688879" stroke-width="2"/>`,
        text(frameX+376,frameTop+43,'PYLON +49.0m','ps-banner-note','start'),
        // Waterside Hinged Luffing Boom (31.0 m Outreach, EL +31.3 m) & Landside Fixed Boom Girder
        `<rect x="${frameX+58}" y="${frameTop+78}" width="684" height="9" rx="2" fill="#d7e4da" stroke="#3f6557" stroke-width="2.2"/>`,
        text(frameX+182,frameTop+71,'31.0 m WATERSIDE BOOM (+31.3m)','ps-banner-note'),
        // Upper Machinery House (EL +41.0 m) & E-House / Trafo (EL +40.0 m)
        `<rect x="${frameX+442}" y="${frameTop+54}" width="142" height="24" rx="3" fill="#b7cbbd" stroke="#3f6557" stroke-width="2"/>`,
        text(frameX+513,frameTop+69,'MACH. HOUSE (+41m)','ps-banner-note'),
        `<rect x="${frameX+594}" y="${frameTop+56}" width="142" height="22" rx="3" fill="#d2e0d5" stroke="#3f6557" stroke-width="1.8"/>`,
        text(frameX+665,frameTop+70,'E-HOUSE (+40m)','ps-banner-note'),
        // Main Trolley + Operator Cabin + 33 m³ 4-Rope Clamshell Grab
        `<rect x="${frameX+112}" y="${frameTop+87}" width="44" height="8" rx="2" fill="#43705f"/>`,
        `<rect x="${frameX+298}" y="${frameTop+89}" width="30" height="14" rx="2" fill="#e6f2ef" stroke="#416859" stroke-width="1.6"/>`,
        `<path d="M${frameX+128} ${frameTop+95}V${frameTop+134}M${frameX+142} ${frameTop+95}V${frameTop+134}" stroke="#416859" stroke-width="2"/>`,
        `<path d="M${frameX+135} ${frameTop+132}L${frameX+112} ${frameTop+146}Q${frameX+110} ${frameTop+164} ${frameX+133} ${frameTop+162}V${frameTop+144}ZM${frameX+135} ${frameTop+132}L${frameX+158} ${frameTop+146}Q${frameX+160} ${frameTop+164} ${frameX+137} ${frameTop+162}V${frameTop+144}Z" fill="#4f6c66" stroke="#2c4540" stroke-width="2"/>`,
        text(frameX+135,frameTop+124,'33 m³ GRAB (44 t)','ps-banner-note'),
        // Curved kinematic trajectory from Grab over to 85 m³ Hopper inside portal
        `<path d="M${frameX+150} ${frameTop+118}Q${frameX+268} ${frameTop+92} ${frameX+405} ${frameTop+104}" fill="none" stroke="#b37736" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#ps-arrow)"/>`,
        // Inside Portal: 85 m³ Receiving Hopper -> Vibro-Feeder -> Reversible Shuttle Belt -> EAC-1B / EAC-1A
        `<polygon points="${frameX+382},${frameTop+104} ${frameX+472},${frameTop+104} ${frameX+450},${frameTop+132} ${frameX+404},${frameTop+132}" fill="#c7d7cb" stroke="#3f6557" stroke-width="2"/>`,
        text(frameX+427,frameTop+121,'85 m³ HOPPER','ps-banner-note'),
        `<polygon points="${frameX+398},${frameTop+134} ${frameX+462},${frameTop+137} ${frameX+458},${frameTop+146} ${frameX+398},${frameTop+143}" fill="#dfc48a" stroke="#856835" stroke-width="1.8"/>`,
        text(frameX+470,frameTop+143,'VIBRO-FEEDER (22 kW)','ps-banner-note','start'),
        `<rect x="${frameX+386}" y="${frameTop+152}" width="152" height="11" rx="4" fill="#e6efe9" stroke="#385c4e" stroke-width="1.8"/>`,
        text(frameX+462,frameTop+160,'SHUTTLE BELT (EL +7.75m)','ps-banner-note'),
        `<rect x="${frameX+376}" y="${frameTop+170}" width="44" height="11" rx="2" fill="#d7e4da" stroke="#314d42" stroke-width="1.5"/>`,
        text(frameX+398,frameTop+179,'EAC-1B','ps-banner-note'),
        `<rect x="${frameX+512}" y="${frameTop+170}" width="44" height="11" rx="2" fill="#d7e4da" stroke="#314d42" stroke-width="1.5"/>`,
        text(frameX+534,frameTop+179,'EAC-1A','ps-banner-note'),
        // Right-hand 6-Stage Kinematic Process Flow Summary Stack (widened to x=frameX+756, width=636 so zero text overflows)
        `<rect x="${frameX+756}" y="${frameTop+34}" width="636" height="172" rx="9" fill="#f8fbf8" stroke="#9ab2a4" stroke-width="1.5"/>`,
        text(frameX+774,frameTop+53,'COAL UNLOADING FLOW SEQUENCE & GA ELEVATION BENCHMARKS','ps-zone-label','start')
      );
      [
        [frameX+772,frameTop+74,'1 · Vessel Hold → 33 m³ 4-Rope Grab (17.5 t tare / 44 t gross · 2×630 kW winches @ 110/150 m/min)'],
        [frameX+772,frameTop+96,'2 · Waterside Luffing Boom (31.0 m outreach @ EL +31.3 m · 50.0 m trolley travel @ 190 m/min)'],
        [frameX+772,frameTop+118,'3 · 85 m³ Hardox-400 Hopper (EL +15.5 m · 200×200 mm grizzly · spillage flap & R&P gate)'],
        [frameX+772,frameTop+140,'4 · Spring-Mounted Vibro-Feeder (EL +10.8 m · 2400×4600 mm · 1,700 / 1,870 TPH · 22 kW)'],
        [frameX+772,frameTop+162,'5 · Reversible Shuttle Belt (EL +7.75 m · 1,800 mm belt · 30 kW drive + 2.2 kW travel · 4.0 m shift)'],
        [frameX+772,frameTop+184,'6 · Selective Jetty Discharge → EAC-1B (Waterside X=-5.25 m) or EAC-1A (Landside X=-9.25 m)']
      ].forEach(([tx,ty,lbl])=>{
        decor.push(text(tx,ty,lbl,'ps-banner-note','start'));
      });

      const colW=696,leftX=frameX,rightX=frameX+colW+18;
      let yRow1=frameTop+234;
      const h1L=drawZoneCard(leftX,yRow1,colW,3,'1','4-ROPE CLAMSHELL GRAB & HOLDING/CLOSING WINCHES','33 m³ GRAB · 2 × 630 kW VFD',z1Grab,'#f5f9f5','#8eab99');
      const h1R=drawZoneCard(rightX,yRow1,colW,4,'2','WATERSIDE HINGED LUFFING BOOM & TROLLEY TRAVERSE','31 m OUTREACH · 210 kW TRAVERSE · 75 kW HOIST',z2BoomTrolley,'#f5f9f5','#8eab99');
      let yRow2=yRow1+Math.max(h1L,h1R)+14;
      const h2L=drawZoneCard(leftX,yRow2,colW,2,'3','85 m³ RECEIVING HOPPER, 200 MM GRIZZLY & VIBRO-FEEDER','HARDOX HOPPER · R&P GATE · 2400×4600 FEEDER',z3HopperFeeder,'#faf6ee','#cbb486');
      const h2R=drawZoneCard(rightX,yRow2,colW,3,'4','REVERSIBLE SHUTTLE BELT CONVEYOR & TRAVEL DRIVE','1800 MM BELT · 30 kW DRIVE · 2.2 kW SHUTTLE',z4Shuttle,'#faf6ee','#cbb486');
      let yRow3=yRow2+Math.max(h2L,h2R)+14;
      const h3L=drawZoneCard(leftX,yRow3,colW,2,'5','GANTRY LONG-TRAVEL BOGIES, RAIL CLAMPS & BUFFERS','40 × Ø630 WHEELS · 20 × 7.5 kW · 2 × 210 kN CLAMPS',z5Gantry,'#f4f7fa','#97b0c4');
      const h3R=drawZoneCard(rightX,yRow3,colW,4,'6','OPERATOR CABIN, MACHINERY HOUSE, CRANES & LIFT','CABIN · WINCH HOUSE · 10 T EOT · AK450 LIFT',z6Houses,'#f4f7fa','#97b0c4');
      let yRow4=yRow3+Math.max(h3L,h3R)+14;
      const h4L=drawZoneCard(leftX,yRow4,colW,4,'7','3.3 kV / 415 V E-HOUSE, CABLE REEL, DG SET & WIND SAFETY','3.3 kV REEL · VVVF DRIVES · DG SET · ANEMOMETER',z7Power,'#fbf7ec','#d2be8c');
      const h4R=drawZoneCard(rightX,yRow4,colW,2,'8','ONBOARD WATER-MIST DSS & LINCOLN DUAL-LINE GREASE LUBE','10 m³ DSS (30 NOZZLES) · LUBE STATIONS I–IV',z8Fluid,'#eff5f6','#9ebec7');

      let curY=yRow4+Math.max(h4L,h4R)+18;
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED JETTY RECEIVING BELT CONVEYORS (EAC-1A & EAC-1B) & LUBRICATION REFERENCE',outside,5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(920,curY+10);s.initialHeight=Math.min(s.height,980);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:21})).join('');
    }

    // 8. Bespoke Primary Screening House (UEE-1 / PSH) Multi-Floor 4-Stream Elevation Schematic
    if(s.kind==='screenhouse'){
      const frameX=55,frameTop=40,frameW=1410,colW=696,leftX=frameX,rightX=frameX+colW+18;
      const streamAIn=parts.filter(n=>/EAC-2A|AT-1/i.test(n.label));
      const streamBIn=parts.filter(n=>/EAC-2B|AT-2/i.test(n.label));
      const rodGates=parts.filter(n=>/KB-RG-/i.test(n.label)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
      const bypassGates=parts.filter(n=>/KB-RPG-/i.test(n.label)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
      const screens=parts.filter(n=>/^EBD-[1-4]$/i.test(n.label)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
      const rejectBins=parts.filter(n=>/Oversize Reject Bins/i.test(n.label));
      const dfdsParts=parts.filter(n=>/DFDS/i.test(n.label));
      const houseServices=parts.filter(n=>![...streamAIn,...streamBIn,...rodGates,...bypassGates,...screens,...rejectBins,...dfdsParts].includes(n));

      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="52" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,'UEE-1 PRIMARY SCREENING HOUSE (PSH) · 4-STREAM INCOMING COAL SCREENING, BYPASS & TRAMP-IRON EXTRACTION ELEVATION','ps-zone-label','start'),
        text(frameX+22,frameTop+40,'INCOMING EAC-2A/2B (2 × 1750 TPH) → ILMS AT-1/AT-2 → ROD GATES KB-RG-1..4 → BYPASS GATES KB-RPG-1..4 → GRIZZLY SCREENS EBD-1..4 (-200 MM TO EAC-3A/3B · +200 MM TO REJECT BINS)','ps-Subtle','start')
      );

      let curY=frameTop+66;
      const h1L=drawZoneCard(leftX,curY,colW,4,'1A','EL +23.5 M · STREAM-A HEAD DRIVE (EAC-2A) & ILMS AT-1','EAC-2A HEAD PULLEY · AT-1 MAGNET',streamAIn,'#faf6ee','#cbb486');
      const h1R=drawZoneCard(rightX,curY,colW,4,'1B','EL +23.5 M · STREAM-B HEAD DRIVE (EAC-2B) & ILMS AT-2','EAC-2B HEAD PULLEY · AT-2 MAGNET',streamBIn,'#faf6ee','#cbb486');
      curY+=Math.max(h1L,h1R)+14;

      const h2L=drawZoneCard(leftX,curY,colW,4,'2A','EL +17.0 M · MANUAL INLET ISOLATION ROD GATES (KB-RG-1..4)','4 × STREAM ISOLATION NEEDLE GATES',rodGates,'#f5f9f5','#8eab99');
      const h2R=drawZoneCard(rightX,curY,colW,4,'2B','EL +17.0 M · MOTORIZED RACK & PINION BYPASS GATES (KB-RPG-1..4)','SCREEN vs. DIRECT BYPASS DIVERSION',bypassGates,'#f5f9f5','#8eab99');
      curY+=Math.max(h2L,h2R)+14;

      const h3L=drawZoneCard(leftX,curY,920,4,'3A','EL +11.2 M · PRIMARY VIBRATING GRIZZLY ROLLER SCREENS (EBD-1..4)','4 × 1750 TPH · -200 MM TO EAC-3A/3B',screens,'#eef5f0','#7fa38e');
      const h3R=drawZoneCard(leftX+936,curY,frameW-936,1,'3B','EL +6.5 M · OVERSIZE REJECT BINS (>200 MM)','TRUCK LOADING HOPPERS',rejectBins,'#fbf7ec','#d2be8c');
      curY+=Math.max(h3L,h3R)+14;

      const h4L=drawZoneCard(leftX,curY,460,2,'4A','EL +0.0 M · HOUSE DRY-FOG DUST SUPPRESSION','UEE-1 LOCAL DFDS & PS-03',dfdsParts,'#eff5f6','#9ebec7');
      const h4R=drawZoneCard(leftX+476,curY,frameW-476,4,'4B','EL +0.0 M · MAINTENANCE HOISTS (EH-1..4 / MH-1..4), DRAINAGE SUMP (SP-1M/N) & WATER','HOISTS · SUMP · POTABLE/SERVICE WATER',houseServices,'#f4f7fa','#97b0c4');
      curY+=Math.max(h4L,h4R)+18;

      const primaryOutside=outside.filter(n=>/^(EAC-[123][AB]|DFDS System-1|CHP Main Control Room DCS|SW1 Common|PW Common)/i.test(n.label));
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED UPSTREAM CONVEYORS (EAC-1A/B, EAC-2A/B), DOWNSTREAM SCREENED-COAL CONVEYORS (EAC-3A/B) & PLANT UTILITIES',primaryOutside.length?primaryOutside:outside.slice(0,10),5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(900,curY+10);s.initialHeight=Math.min(s.height,980);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:21})).join('');
    }

    // 9. Bespoke Primary Grizzly Roller Screen (EBD-1..4) Schematic
    if(s.kind==='screen'){
      const frameX=65,frameTop=42,frameW=1390;
      const driveItems=parts.filter(n=>/motor|transmission|cardan|exciter/i.test(n.label));
      const deckItems=parts.filter(n=>!driveItems.includes(n)&&/deck|dust-cover|spray-header/i.test(n.label));
      const chuteSpringItems=parts.filter(n=>!driveItems.includes(n)&&!deckItems.includes(n));

      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="52" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · PRIMARY VIBRATING GRIZZLY ROLLER SCREEN (1750 TPH · 200 MM APERTURE) MECHANICAL & FLOW SCHEMATIC`,'ps-zone-label','start'),
        text(frameX+22,frameTop+40,'MOTOR & V-BELT DRIVE → CARDAN SHAFT → PAIRED VIBRATION EXCITERS → BLIND FEED DECK & GRIZZLY DECK → UNDERSIZE (-200 MM) vs. OVERSIZE (+200 MM REJECT) CHUTES','ps-Subtle','start')
      );
      let curY=frameTop+66;
      curY+=drawZoneCard(frameX,curY,frameW,4,'1','VIBRATING EXCITER DRIVE TRAIN (MOTOR, V-BELT/PULLEY TRANSMISSION, CARDAN SHAFT & PAIRED EXCITERS)','EXCITATION & TORQUE TRANSMISSION',driveItems,'#f5f9f5','#8eab99')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'2','BLIND IMPACT FEED DECK, GRIZZLY SCREENING DECK, DUST ENCLOSURE & DFDS SPRAY HEADER','200 MM GRIZZLY SEPARATION ZONE',deckItems,'#faf6ee','#cbb486')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'3','UNDERSIZE (-200 MM) & OVERSIZE (+200 MM REJECT) CHUTES, ISOLATION SPRINGS & AMPLITUDE LIMITERS','DISCHARGE CHUTES & DYNAMIC ISOLATION',chuteSpringItems,'#eff5f6','#9ebec7')+18;
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED UPSTREAM BYPASS/ROD GATES, DOWNSTREAM CONVEYORS (EAC-3A/3B), REJECT BINS & UEE-1 PSH',outside,5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(760,curY+10);s.initialHeight=Math.min(s.height,920);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // 10. Bespoke Unit Boiler Bunker Bay (Unit-1 / Unit-2 Coal Bunker Bay) & Individual Mill Bunker / Reject Bin Schematic
    if(s.kind==='bunker-bay'||s.kind==='bunker'){
      const frameX=55,frameTop=40,frameW=1410;
      if(s.kind==='bunker-bay'){
        const trippers=parts.filter(n=>n.kind==='tripper'||/^TT-\d|^FG-\d/i.test(n.label)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
        const sealBelts=parts.filter(n=>!trippers.includes(n)&&(/sealing belt/i.test(n.label)||n.kind==='belt'));
        const deUnits=parts.filter(n=>!trippers.includes(n)&&!sealBelts.includes(n)&&(/DE System/i.test(n.label)||n.kind==='water'));
        const bunkers=parts.filter(n=>!trippers.includes(n)&&!sealBelts.includes(n)&&!deUnits.includes(n)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));

        decor.push(
          `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="52" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
          text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · BOILER BUNKER GALLERY (EL +49.30 M TRIPPER FLOOR & 6 × 926.25 m³ CYLINDRICAL-CONICAL MILL BUNKERS A–F)`,'ps-zone-label','start'),
          text(frameX+22,frameTop+40,'BUNKER CONVEYORS EBA-19A/19B → TRAVELLING TRIPPERS (TT-1..4) & DIVERTER GATES (FG-19..22) → TOP SLOT SEALING BELT → MILL BUNKERS A TO F (6 × 926.25 m³)', 'ps-Subtle','start')
        );

        let curY=frameTop+66;
        const c1W=490,c2W=440,c3W=frameW-c1W-c2W-28;
        const h1=drawZoneCard(frameX,curY,c1W,2,'1','EL +49.3 M · TRAVELLING BUNKER TRIPPERS','MOTORIZED TRIPPERS ON EBA-19A/19B',trippers,'#faf6ee','#cbb486');
        const h2=drawZoneCard(frameX+c1W+14,curY,c2W,1,'2','EL +49.3 M · TOP SLOT SEALING BELT','MAGNETIC SEALING STRIP OVER BUNKERS A–F',sealBelts,'#f5f9f5','#8eab99');
        const h3=drawZoneCard(frameX+c1W+c2W+28,curY,c3W,1,'3','EL +49.3 M · BUNKER HOUSE PULSE-JET DE','NEGATIVE-PRESSURE BUNKER VENTILATION',deUnits,'#eff5f6','#9ebec7');
        curY+=Math.max(h1,h2,h3)+16;

        // 6-Column Mill Bunker Array (Bunker-A through Bunker-F) with conical hopper graphic backdrop
        const bCardH=238;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${bCardH}" rx="10" fill="#f5f9f5" stroke="#8eab99" stroke-width="1.6"/>`,
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="28" rx="10" fill="#8eab99" opacity=".22"/>`,
          `<circle cx="${frameX+18}" cy="${curY+14}" r="9" fill="#8eab99"/>`,
          text(frameX+18,curY+18,'4','ps-belt-flow-arrow'),
          text(frameX+34,curY+18,'EL +36.0 M TO +19.0 M · 6 × 926.25 m³ CYLINDRICAL-CONICAL MILL BUNKERS (BUNKER-A TO F)','ps-zone-label','start'),
          text(frameX+frameW-14,curY+18,'RADAR LEVEL PROBES · Ø1150 MM OUTLET GATES TO MILL FEEDERS','ps-Subtle','end')
        );
        const stepB=Math.floor((frameW-36)/Math.max(1,bunkers.length));
        bunkers.forEach((n,i)=>{
          const bx=frameX+24+i*stepB;
          decor.push(
            `<path d="M${bx+95} ${curY+32}V${curY+50}" stroke="#b37736" stroke-width="3" marker-end="url(#ps-arrow)"/>`,
            `<path d="M${bx+12} ${curY+54}H${bx+178}V${curY+152}L${bx+132} ${curY+224}H${bx+58}L${bx+12} ${curY+152}Z" fill="#e6efe8" stroke="#7d9989" stroke-width="1.5" stroke-dasharray="4 3" opacity=".65"/>`
          );
          put(n,bx+10,curY+64,170,70);
        });
        curY+=bCardH+18;

        const cleanOut=outside.filter(n=>!/sealing-strip lifter/i.test(n.label));
        curY=drawBottomDock(frameX,curY,frameW,'CONNECTED BUNKER FEED CONVEYORS (EBA-19A/19B), DIVERTER GATES (FG-19..22) & BUNKER DE CONTROLS',cleanOut,5);
        const allClean=xrayExtraEdges(positions,[]);
        s.width=1520;s.height=Math.max(760,curY+10);s.initialHeight=Math.min(s.height,920);
        return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:21})).join('');
      }

      // Individual Mill Bunker (Bunker-A..F) or UEE-1 Oversize Reject Bins
      const topSeal=parts.filter(n=>n.kind==='belt'||/sealing belt|protective grid|Reject Bin-[12]/i.test(n.label));
      const shellAndLevel=parts.filter(n=>!topSeal.includes(n)&&(/shell|conical hopper|level|radar/i.test(n.label)||['chute','level-sensor','sensor','silo','bunker'].includes(n.kind))&&!/gate|outlet/i.test(n.label));
      const outletGates=parts.filter(n=>!topSeal.includes(n)&&!shellAndLevel.includes(n));

      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="52" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · VERTICAL VESSEL, LEVEL INSTRUMENTATION & DISCHARGE GATE CUTAWAY SCHEMATIC`,'ps-zone-label','start'),
        text(frameX+22,frameTop+40,'TOP SLOT SEALING / SURGE HOPPER → CYLINDRICAL SHELL, SS304M CONICAL HOPPER & HIGH/LOW LEVEL PROBES → BOTTOM OUTLET GATE ASSEMBLY','ps-Subtle','start')
      );
      let curY=frameTop+66;
      curY+=drawZoneCard(frameX,curY,frameW,Math.max(1,topSeal.length),'1','TIER 1 · TOP INLET SLOT SEALING BELT, PROTECTIVE GRID & SURGE HOPPER COMPARTMENTS','TOP COAL ENTRY & DUST CONTAINMENT',topSeal,'#faf6ee','#cbb486')+14;
      curY+=drawZoneCard(frameX,curY,frameW,Math.max(2,shellAndLevel.length),'2','TIER 2 · CYLINDRICAL SHELL, SS304M CONICAL HOPPER & NON-CONTACT RADAR / LEVEL SWITCHES','STORAGE VESSEL & CONTINUOUS LEVEL MONITORING',shellAndLevel,'#f5f9f5','#8eab99')+14;
      curY+=drawZoneCard(frameX,curY,frameW,Math.max(1,outletGates.length),'3','TIER 3 · BOTTOM OUTLET FLANGE & MANUAL / RACK-AND-PINION ISOLATION SLIDE GATE','GRAVITY DISCHARGE INTERFACE',outletGates,'#eff5f6','#9ebec7')+18;
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED FEEDING TRIPPERS / SCREENS & PARENT BUILDING GALLERY',outside,5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(720,curY+10);s.initialHeight=Math.min(s.height,880);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // 11. Bespoke Travelling / Fixed Tripper (TT-1..4, FTR-1..4, EAD-1..4 Travelling tripper) Kinematic S-Loop Schematic
    if(s.kind==='tripper'){
      const frameX=55,frameTop=40,frameW=1410;
      const isFixed=/^FTR-\d/i.test(s.title);
      const isStackerTrip=/^EAD-\d/i.test(s.title);
      const pulleyIdlerScraper=parts.filter(n=>['pulley','idler','scraper'].includes(n.kind)||/pulley|idler|scraper/i.test(n.label));
      const chuteGateSeal=parts.filter(n=>!pulleyIdlerScraper.includes(n)&&(['chute','gate','belt'].includes(n.kind)||/chute|diverter|skirt|sealing/i.test(n.label)));
      const travelClampCtrl=parts.filter(n=>!pulleyIdlerScraper.includes(n)&&!chuteGateSeal.includes(n));

      // Top S-Wrap Pulley Loop & Bifurcated Discharge Graphic
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="104" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · ${isFixed?'FIXED BELT TRIPPER S-WRAP PULLEY LOOP & BIFURCATED CHUTE SCHEMATIC':isStackerTrip?'STACKER TRAVELLING TRIPPER S-WRAP PULLEY LOOP & BOOM FEED SCHEMATIC':'TRAVELLING BUNKER TRIPPER S-WRAP PULLEY LOOP, ICRC-2 RAIL CLAMP & DIVERTER SCHEMATIC'}`,'ps-zone-label','start'),
        // Kinematic S-loop belt path graphic
        `<path d="M120 ${frameTop+82}H480L640 ${frameTop+44}H780" fill="none" stroke="#3d6352" stroke-width="5"/>`,
        `<path d="M780 ${frameTop+58}L690 ${frameTop+86}H1280" fill="none" stroke="#5a7d6c" stroke-width="4" stroke-dasharray="8 4"/>`,
        `<circle cx="780" cy="${frameTop+51}" r="14" class="ps-metal"/>`,
        `<circle cx="690" cy="${frameTop+82}" r="11" class="ps-metal"/>`,
        `<path d="M800 ${frameTop+51}L910 ${frameTop+84}" stroke="#b37736" stroke-width="4" marker-end="url(#ps-arrow)"/>`,
        text(310,frameTop+72,'INCOMING CARRYING BELT','ps-belt-flow-arrow'),
        text(780,frameTop+41,'HEAD DISCHARGE PULLEY','ps-Subtle'),
        text(615,frameTop+95,'LOWER S-WRAP BEND PULLEY','ps-Subtle'),
        text(1080,frameTop+74,isFixed?'BIFURCATED CHUTE TO FLOW DIVIDER & CONTINUING BELT':isStackerTrip?'TRANSFER CHUTE TO STACKER BOOM CONVEYOR':'FG-19..22 TWO-WAY CHUTE TO MILL BUNKERS A–F','ps-belt-flow-arrow')
      );

      let curY=frameTop+118;
      curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(2,pulleyIdlerScraper.length)),'1','S-WRAP HEAD DISCHARGE PULLEY, LOWER BEND PULLEY, CARRYING/IMPACT IDLERS & BELT SCRAPER','BELT S-LOOP & DISCHARGE PULLEY GROUP',pulleyIdlerScraper,'#f5f9f5','#8eab99')+14;
      curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(2,chuteGateSeal.length)),'2','BIFURCATED DISCHARGE CHUTE, DIVERTER FLAP GATE, SKIRTBOARD SEALING & BELT SEALING LIFTER','COAL DIVERSION & DUST SEALING',chuteGateSeal,'#faf6ee','#cbb486')+14;
      if(travelClampCtrl.length){
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(2,travelClampCtrl.length)),'3','LONG-TRAVEL BOGIES & GEARED MOTOR, ICRC-2 HYDRAULIC RAIL CLAMP, CABLE REEL & LOCAL CONTROL PANEL','RAIL TRAVEL, ANCHORING & INSTRUMENTATION',travelClampCtrl,'#f4f7fa','#97b0c4')+18;
      }
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED HOST CONVEYOR, SERVED BUNKERS / FLOW DIVIDERS & CONTROL INTERFACES',outside,5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(740,curY+10);s.initialHeight=Math.min(s.height,920);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // 12. Bespoke Plant Electrical SLD, MCC Building & HT/LT Switchgear Breaker Feeder Schedule Schematic
    if(s.kind==='switchboard'||/switchgear|switch board|mcc-\d/i.test(s.title)){
      const frameX=45,frameTop=36,frameW=1430;
      const mccMatch=/MCC-([1-4])/i.exec(s.title)||/#00BB([D-J])/i.exec(s.title);
      const mccNum=mccMatch?(['1','2','3','4'].includes(mccMatch[1])?mccMatch[1]:['D','E'].includes(mccMatch[1].toUpperCase())?'1':['F','G'].includes(mccMatch[1].toUpperCase())?'2':'3'):null;
      const isHtFocus=/HT Switch Board|#00BB[D-J]|3\.3 kV Bus-Coupler/i.test(s.title);
      const isLtFocus=/LT Switch Board|Switchgear & Feeder Lineup|415 V Bus Sections|415 V Incomer/i.test(s.title);
      const is11kVFocus=/^11 kV Unit Switch Board|00BBT0|00BFT/i.test(s.title);

      const getFacts=(id,pred)=>(p.outgoing.get(id)||[]).filter(a=>a.predicate===pred);
      const getComp=(id)=>{
        const comps=getFacts(id,'compartment_number').map(a=>String(a.value));
        if(!comps.length)return '';
        if(mccNum){
          const f=comps.filter(c=>new RegExp(`MCC[- ]?${mccNum}\\b`,'i').test(c));
          if(f.length)return f.join(' + ');
        }
        return comps.join(' + ');
      };
      const shortCompBadge=(raw)=>{
        if(!raw)return '';
        const b=/#(00BB[D-J])\s*(Bus-[AB])/i.exec(raw);
        let c=raw.replace(/\s*\(MCC\s*\d+,\s*p\.\d+\)/gi,'').replace(/\s*\(MCC\s*\d+\)/gi,'').replace(/\s*\(#00BB[D-J][^)]*\)/gi,'').trim();
        if(c.length>24)c=c.split(',').slice(0,2).join(',')+'…';
        return b?`${c}·#${b[1]}`:c;
      };
      const getLocTag=(id)=>{
        const ownLoc=getFacts(id,'located_at').map(a=>p.entities.get(a.canonical_object)?.label).find(Boolean);
        if(ownLoc)return ownLoc.replace(/^CHP\s+/i,'').replace(/\s+Building$/i,'');
        for(const pid of M.closestParents(p,id)){
          const pLoc=getFacts(pid,'located_at').map(a=>p.entities.get(a.canonical_object)?.label).find(Boolean);
          if(pLoc)return pLoc.replace(/^CHP\s+/i,'').replace(/\s+Building$/i,'');
          for(const gpid of M.closestParents(p,pid)){
            const gpLoc=getFacts(gpid,'located_at').map(a=>p.entities.get(a.canonical_object)?.label).find(Boolean);
            if(gpLoc)return gpLoc.replace(/^CHP\s+/i,'').replace(/\s+Building$/i,'');
          }
        }
        return '';
      };
      const formatLoadCard=(n)=>{
        const rawComp=getComp(n.id);
        const badge=shortCompBadge(rawComp);
        const brkRaw=getFacts(n.id,'breaker_rating').map(a=>String(a.value)).find(Boolean)||'';
        const cblRaw=getFacts(n.id,'power_cable_size').map(a=>String(a.value)).find(Boolean)||'';
        const pwrKw=getFacts(n.id,'rated_power').find(a=>a.unit==='kW')?.value;
        const volt=getFacts(n.id,'power_supply_voltage')[0]?.value||getFacts(n.id,'rated_voltage')[0]?.value;
        const loc=getLocTag(n.id);
        let cleanLbl=n.label
          .replace(/\s+Drive assembly\s+/i,' · ')
          .replace(/\s+main drive motor$/i,' · Main Drive Motor')
          .replace(/\s+Main motor$/i,' · Main Drive Motor')
          .replace(/\s+Main Drive Motor$/i,' · Main Drive Motor')
          .replace(/\s+screen drive motor$/i,' · Screen Drive Motor')
          .replace(/\s+Vibrating drive assembly Motor$/i,' · Vibrating Screen Motor')
          .replace(/\s+service thruster brake$/i,' · Thruster Brake')
          .replace(/\s+Thruster brake$/i,' · Thruster Brake')
          .replace(/\s+scoop fluid coupling$/i,' · Scoop Coupling')
          .replace(/\s+Scoop coupling(.*)$/i,' · Scoop Coupling$1')
          .replace(/\s+rotary actuator$/i,' · Rotary Gate Actuator')
          .replace(/\s+geared actuator assembly$/i,' · Geared Flow-Divider Drive')
          .replace(/\s+drive assembly$/i,' · Geared Actuator Drive')
          .replace(/\s+power and fibre-optic cable reel$/i,' · 3.3kV Trailing Cable Reel')
          .replace(/^UEE-3 Maintenance access and lifting Monorails and hoists\s+/i,'UEE-3 Hoist ')
          .replace(/\s+415 V Bag Filter Fan, Rotary Airlock, Hoists[^,]*, Sump Pump & Hooter/i,' · Bagfilter, Hoists & Sump')
          .replace(/\s+415 V Electric Hoists LSEH-1\.\.3, Compressor, Sump Pump & Local PDB \/ Hooter/i,' · Hoists LSEH-1..3, Sump & PDB')
          .replace(/\s+415 V Electric Hoists GEH-1\/2, Sump Pump & Warning Hooter/i,' · Hoists GEH-1/2, Sump & Hooter')
          .replace(/\s+415 V Electric Hoist LSEH-4, Compressor, Sump Pump & Warning Hooter/i,' · Hoist LSEH-4, Sump & Comp')
          .replace(/Coal Bunker Bay 415 V Electric Hoist (EH-\d), Local PDB & Warning Hooter/i,'Bunker Bay · Hoist $1, PDB & Hooter')
          .replace(/415 V Local Power Distribution Boards? \(PDB(?:-1\/2)?\) & Warning Hooter/i,'Local PDB & Hooter')
          .replace(/415 V Local Power Distribution Board \(PDB\)/i,'Local PDB')
          .replace(/415 V Electric Hoists (EH-[^,]+), Local PDB & Warning Hooter/i,'Hoists $1, PDB & Hooter')
          .replace(/415 V Electric Hoist (EH-\d), Local PDB & Warning Hooter/i,'Hoist $1, PDB & Hooter')
          .replace(/415 V Electric Hoists (EH-[^&]+)& Warning Hooter/i,'Hoists $1& Hooter')
          .replace(/(?:\s*·\s*)+/g,' · ');
        const title=badge?`[${badge}] ${cleanLbl}`:cleanLbl;
        const subParts=[];
        if(brkRaw){
          const shortBrk=brkRaw
            .replace(/3\.3 kV VCB\s*·\s*/i,'3.3kV VCB ')
            .replace(/\s*HT Motor Feeder/i,'')
            .replace(/\s*HT Crusher Feeder/i,'')
            .replace(/\s*Trailing Cable Feeder/i,'')
            .replace(/\(U-POWER OMEGA[^)]*\)/i,'EDO ACB')
            .replace(/\(([^)]+)\)/g,'$1')
            .trim();
          subParts.push(shortBrk.length>26?shortBrk.slice(0,25)+'…':shortBrk);
        }else if(pwrKw){
          subParts.push(`${pwrKw} kW${volt?' · '+volt+'V':''}`);
        }
        if(cblRaw){
          const shortCbl=cblRaw.replace(/\s*SQ\s*MM/gi,' sqmm').replace(/\s*X\s*/gi,'×');
          subParts.push(shortCbl.length>18?shortCbl.slice(0,17)+'…':shortCbl);
        }
        if(loc&&!cleanLbl.toUpperCase().startsWith(loc.toUpperCase())){
          subParts.push(`@ ${loc}`);
        }
        const sub=subParts.join(' · ')||undefined;
        return {title,sub};
      };

      // Separate upstream power sources & transformers from internal switchgear and outgoing loads
      const isUpstreamNode=n=>/11\s*kV|00BBT0[3-8]|00BFT(?:1[7-9]|2[0-7])|Auxiliary Transformer|LT Service Transformers|Switchgear Distribution Group/i.test(n.label);
      const isHtSwitchgearNode=n=>!isUpstreamNode(n)&&(/3\.3\s*kV|HT Switch Board|#00BB[D-J]|Bus-Coupler VCB/i.test(n.label));
      const isLtSwitchgearOrBldgNode=n=>!isUpstreamNode(n)&&!isHtSwitchgearNode(n)&&(/LT Switch Board|415\s*V Bus Sections|415\s*V Incomer|Switchgear & Feeder Lineup|Main Control Room DCS|Pressure Ventilation|MLDB-2|Gas Chlorination MCC/i.test(n.label));

      const allCandidates=[...parts,...outside];
      const tier1Upstream=allCandidates.filter((n,idx,arr)=>isUpstreamNode(n)&&arr.findIndex(x=>x.id===n.id)===idx&&(!isHtFocus||!/00BFT/i.test(n.label))&&(!isLtFocus||!/00BBT/i.test(n.label)));
      const tier2HtSwitchgear=allCandidates.filter((n,idx,arr)=>isHtSwitchgearNode(n)&&arr.findIndex(x=>x.id===n.id)===idx&&!isLtFocus);
      const tier2LtSwitchgear=allCandidates.filter((n,idx,arr)=>isLtSwitchgearOrBldgNode(n)&&arr.findIndex(x=>x.id===n.id)===idx&&(!isHtFocus||/Pressure Ventilation/i.test(n.label)));

      const tier12Ids=new Set([...tier1Upstream,...tier2HtSwitchgear,...tier2LtSwitchgear].map(n=>n.id));
      const rawLoads=allCandidates.filter((n,idx,arr)=>!tier12Ids.has(n.id)&&arr.findIndex(x=>x.id===n.id)===idx);

      // Deduplicate parent+child pairs in rawLoads when both share the same breaker compartment
      const loadIdSet=new Set(rawLoads.map(n=>n.id));
      const dropParentMap=new Map();
      const dropChildSet=new Set();
      for(const parent of rawLoads){
        const desc=p.assembly(parent.id).map(x=>x.id).filter(x=>x!==parent.id&&loadIdSet.has(x));
        if(!desc.length)continue;
        const pComp=getComp(parent.id);
        if(/Sump Pumps SP-|Coal Sampling System/i.test(parent.label)){
          desc.forEach(cid=>{if(getComp(cid)===pComp){dropChildSet.add(cid);dropParentMap.set(cid,parent.id);}});
        }else{
          const matchingChildren=desc.filter(cid=>getComp(cid)===pComp||!pComp);
          if(matchingChildren.length){
            dropParentMap.set(parent.id,matchingChildren[0]);
          }
        }
      }
      const dedupLoads=rawLoads.filter(n=>!dropParentMap.has(n.id)&&!dropChildSet.has(n.id));
      dedupLoads.sort((a,b)=>{
        const ca=getComp(a.id),cb=getComp(b.id);
        return (ca||a.label).localeCompare(cb||b.label,undefined,{numeric:true});
      });

      // Categorize outgoing loads into clear engineering functional sections
      const isHtLoad=n=>{
        const c=getComp(n.id);
        const v=getFacts(n.id,'power_supply_voltage')[0]?.value||getFacts(n.id,'rated_voltage')[0]?.value;
        return /^VCB-|#00BB[D-J]|3\.3\s*kV/i.test(c)||v===3300||v===3.3||/^(?:EAC-\d+[AB]?|EBA-(?:6[AB]|8|10|12|14|15[AB]|16[AB]|17[AB]|18[AB]|19[AB])|EBC-[12])\b.*motor/i.test(n.label)||/^Coal Ship Unloader|^SUL-[1-3].*cable reel|^EAD-[1-4]$|^EAF-[1-4]$/i.test(n.label);
      };
      const htOutgoingLoads=dedupLoads.filter(isHtLoad);
      const ltRemaining=dedupLoads.filter(n=>!htOutgoingLoads.includes(n));

      const ltAuxForHtDrives=ltRemaining.filter(n=>!/^KF-[1-4]\b/i.test(n.label)&&(['brake','coupling'].includes(n.kind)||/thruster brake|scoop.*coupling|Inspection door/i.test(n.label)));
      const ltMainDrives=ltRemaining.filter(n=>!ltAuxForHtDrives.includes(n)&&(['conveyor','screen','feeder','extractor','tripper','elevator','ship'].includes(n.kind)||/screen drive motor|Vibrating drive assembly Motor|^KF-[1-4]\b|SNC-2|LSPC-|GPC-|GBC-|LS-EAC|LSEAC|LSFN-|LSRPF-|Euro Silo|EBE-CES-|TT-[1-4]|GSL-1/i.test(n.label)));
      const ltGatesAndDividers=ltRemaining.filter(n=>!ltAuxForHtDrives.includes(n)&&!ltMainDrives.includes(n)&&(['gate','rack-pinion','actuator'].includes(n.kind)||/^FG-|^KB-FD-|^KB-RPG-|^LSDV-|^GDV-/i.test(n.label)));
      const ltDustWaterAir=ltRemaining.filter(n=>!ltAuxForHtDrives.includes(n)&&!ltMainDrives.includes(n)&&!ltGatesAndDividers.includes(n)&&(['pump','spray-system','de-stream','de-house','compressor','filter','fan'].includes(n.kind)||/Pump|Sump|DFDS|SPDS|DE-1|DE-2|DE System|Compressor/i.test(n.label))&&!/Electric Hoists|Local PDB/i.test(n.label));
      const ltHoistsInstPdb=ltRemaining.filter(n=>!ltAuxForHtDrives.includes(n)&&!ltMainDrives.includes(n)&&!ltGatesAndDividers.includes(n)&&!ltDustWaterAir.includes(n));

      const drawSwbZone=(x,y,w,cols,badge,title,subtitle,items,fill,stroke,customFormatter=null)=>{
        if(!items.length)return 0;
        const rows=Math.ceil(items.length/cols);
        const titleEstW=34+title.length*9.0;
        const subEstW=subtitle?subtitle.length*7.2+18:0;
        const stackSub=Boolean(subtitle&&(titleEstW+subEstW+28>w));
        const headH=stackSub?42:28;
        const rowStep=168;
        const cardH=rows*rowStep+headH+16;
        decor.push(
          `<rect x="${x}" y="${y}" width="${w}" height="${cardH}" rx="9" fill="${fill}" stroke="${stroke}" stroke-width="1.6"/>`,
          `<rect x="${x}" y="${y}" width="${w}" height="${headH}" rx="9" fill="${stroke}" opacity=".24"/>`,
          `<circle cx="${x+18}" cy="${y+14}" r="9" fill="${stroke}"/>`,
          text(x+18,y+18,badge,'ps-belt-flow-arrow'),
          text(x+34,y+18,title,'ps-zone-label','start'),
          subtitle?(stackSub?text(x+34,y+33,subtitle,'ps-Subtle','start'):text(x+w-12,y+18,subtitle,'ps-Subtle','end')):''
        );
        const padX=14,availW=w-padX*2,step=Math.floor(availW/cols),bw=cols>=5?172:cols===4?186:196,bh=64;
        items.forEach((n,i)=>{
          const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
          const sx=x+padX+Math.round((availW-rowCount*step)/2+(step-bw)/2);
          const fmt=customFormatter?customFormatter(n):{title:undefined,sub:undefined};
          put(n,sx+c*step,y+headH+10+r*rowStep,bw,bh,fmt.title,fmt.sub);
        });
        return cardH;
      };

      const formatTier12Card=(n)=>{
        const l=n.label;
        if(/^00BBT0[3-8]/i.test(l)){
          const tag=l.split(' ')[0];
          const mva=/\(([^)]+)\)/.exec(l)?.[1]||'11/3.45 kV';
          return {title:`${tag} · 11/3.45 kV HT Transformer`,sub:`${mva} · Feeds 3.3 kV HT Bus`};
        }
        if(/^00BFT/i.test(l)){
          const tag=l.split(' ')[0];
          const mva=/\(([^)]+)\)/.exec(l)?.[1]||'11/0.433 kV';
          return {title:`${tag} · 11/0.433 kV LT Transformers`,sub:`${mva} · Feeds 415 V Incomer ACBs`};
        }
        if(/^11 kV Unit Switch Board/i.test(l)){
          return {title:l,sub:'11 kV Upstream Auxiliary Source'};
        }
        if(/#00BB([D-J])/i.test(l)){
          const sec=/#(00BB[D-J])/i.exec(l)[1];
          const bus=/Bus-[AB]/i.exec(l)?.[0]||'3.3 kV Bus';
          return {title:`#${sec} · CHP MCC-${mccNum||1} 3.3 kV ${bus}`,sub:'3.3 kV 50 Hz VCB Switchboard Section'};
        }
        if(/HT Switch Board$/i.test(l)){
          return {title:l,sub:'3.3 kV Medium-Voltage VCB Switchboard'};
        }
        if(/LT Switch Board$/i.test(l)){
          return {title:l,sub:'415 V 3Ph 50kA PMCC / MCC Switchboard'};
        }
        if(/415 V Incomer & Bus-Coupler ACBs/i.test(l)){
          return {title:l,sub:'Drawout EDO Incomer & Bus-Coupler ACBs'};
        }
        if(/415 V Bus Sections/i.test(l)){
          return {title:l,sub:'415 V Segregated PMCC / MCC Busbars'};
        }
        if(/Switchgear & Feeder Lineup/i.test(l)){
          return {title:l,sub:`415 V Drawout MCC Cubicles · MCC-${mccNum||1}`};
        }
        return {title:l,sub:undefined};
      };

      // Top SLD Power Flow Header Banner
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="82" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · SINGLE-LINE POWER FLOW, BUSBAR ARCHITECTURE & BREAKER-TO-LOAD FEEDER SCHEDULE`,'ps-zone-label','start'),
        `<rect x="${frameX+20}" y="${frameTop+32}" width="435" height="38" rx="6" fill="#fbf5eb" stroke="#c89b62" stroke-width="1.3"/>`,
        text(frameX+237,frameTop+47,'1 · WHERE IT GETS POWER (UPSTREAM SOURCE)','ps-belt-flow-arrow'),
        text(frameX+237,frameTop+62,isLtFocus?`11 kV Unit Boards → 00BFT LT Step-Down Trfs (11/0.433 kV)`:isHtFocus?`11 kV Unit Boards → 00BBT HT Step-Down Trfs (11/3.45 kV)`:`11 kV Unit Boards (1BA/1BB/2BA/2BB) → 00BBT (3.3kV) & 00BFT (415V) Trfs`,'ps-Subtle'),
        `<path d="M${frameX+458} ${frameTop+51}H${frameX+492}" stroke="#8a6d3b" stroke-width="3" marker-end="url(#ps-arrow)"/>`,
        `<rect x="${frameX+498}" y="${frameTop+32}" width="435" height="38" rx="6" fill="#f3f7fa" stroke="#7d9eb5" stroke-width="1.3"/>`,
        text(frameX+715,frameTop+47,'2 · WHAT IS INSIDE (INCOMERS & BUS SECTIONS)','ps-belt-flow-arrow'),
        text(frameX+715,frameTop+62,isLtFocus?`415 V Drawout Incomer ACBs, Bus-Couplers & MCC-${mccNum||1} Busbars`:isHtFocus?`3.3 kV HT Bus-A / Bus-B Sections & Bus-Coupler VCB`:`3.3 kV HT VCB Switchboard (#00BBD–J) + 415 V LT MCC-${mccNum||'1..4'} Busbars`,'ps-Subtle'),
        `<path d="M${frameX+936} ${frameTop+51}H${frameX+970}" stroke="#366c7d" stroke-width="3" marker-end="url(#ps-water-arrow)"/>`,
        `<rect x="${frameX+976}" y="${frameTop+32}" width="434" height="38" rx="6" fill="#f2f8f3" stroke="#7fa68b" stroke-width="1.3"/>`,
        text(frameX+1193,frameTop+47,`3 · WHAT IT POWERS (${dedupLoads.length} OUTGOING BREAKER FEEDERS)`,'ps-belt-flow-arrow'),
        text(frameX+1193,frameTop+62,'[Breaker / Comp ID] + Equipment & Specific Part + Rating, Cable & Location','ps-Subtle')
      );

      let curY=frameTop+96;
      if(tier1Upstream.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(4,Math.max(2,tier1Upstream.length)),'1','SECTION 1 · WHERE IT GETS ITS POWER — UPSTREAM 11 kV SWITCHBOARDS & STEP-DOWN TRANSFORMERS (11/3.45 kV & 11/0.433 kV)','UPSTREAM POWER SUPPLY & TRANSFORMER INCOMERS',tier1Upstream,'#fbf7ec','#d2be8c',formatTier12Card)+14;
      }
      if(tier2HtSwitchgear.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(4,Math.max(2,tier2HtSwitchgear.length)),'2A',`SECTION 2A · INTERNAL 3.3 kV HT SWITCHGEAR — ${mccNum?'CHP MCC-'+mccNum+' ':''}3.3 kV HT SWITCH BOARD, BUS-A / BUS-B SECTIONS & BUS-COUPLER VCB`,'3.3 kV MEDIUM-VOLTAGE VCB SWITCHBOARD ARCHITECTURE',tier2HtSwitchgear,'#faf6ee','#cbb486',formatTier12Card)+14;
      }
      if(tier2LtSwitchgear.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(4,Math.max(2,tier2LtSwitchgear.length)),tier2HtSwitchgear.length?'2B':'2',`SECTION ${tier2HtSwitchgear.length?'2B':'2'} · INTERNAL 415 V LT SWITCHGEAR — ${mccNum?'CHP MCC-'+mccNum+' ':''}415 V LT SWITCH BOARD, INCOMER ACBs, BUS SECTIONS & FEEDER LINEUP`,'415 V LOW-VOLTAGE PMCC / MCC SWITCHBOARD ARCHITECTURE',tier2LtSwitchgear,'#f4f7fa','#97b0c4',formatTier12Card)+16;
      }

      if(htOutgoingLoads.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(5,Math.max(3,htOutgoingLoads.length)),'3A',`SECTION 3A · 3.3 kV HT VCB OUTGOING FEEDERS (${htOutgoingLoads.length} HT DRIVES) — MAIN CONVEYOR MOTORS, RING CRUSHERS, UNLOADERS & YARD MACHINES`,'[VCB COMPARTMENT · BUS] EQUIPMENT & 3.3 kV PART POWERED',htOutgoingLoads,'#fdf6ec','#c99b5b',formatLoadCard)+14;
      }
      if(ltMainDrives.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(5,Math.max(3,ltMainDrives.length)),'3B',`SECTION 3B · 415 V LT MAIN PROCESS DRIVES (${ltMainDrives.length} FEEDERS) — LT CONVEYORS, ROLLER SCREENS, BELT FEEDERS, SILO EXTRACTORS & TRIPPERS`,'[MCC COMPARTMENT] 415 V MAIN MOTOR / VFD FEEDER & LOCATION',ltMainDrives,'#f3f8f4','#7fa88c',formatLoadCard)+14;
      }
      if(ltAuxForHtDrives.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(5,Math.max(3,ltAuxForHtDrives.length)),'3C',`SECTION 3C · 415 V LT AUXILIARIES FOR 3.3 kV HT CONVEYORS & CRUSHERS (${ltAuxForHtDrives.length} FEEDERS) — THRUSTER BRAKES & SCOOP COUPLINGS`,'[MCC COMPARTMENT] 415 V BRAKE / SCOOP COUPLING ACTUATOR FOR HT DRIVE',ltAuxForHtDrives,'#f5f7fb','#88a2bd',formatLoadCard)+14;
      }
      if(ltGatesAndDividers.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(5,Math.max(3,ltGatesAndDividers.length)),'3D',`SECTION 3D · 415 V LT MOTORIZED GATES & FLOW DIVIDERS (${ltGatesAndDividers.length} FEEDERS) — FLAP GATES (FG), FLOW DIVIDERS (KB-FD) & RACK/PINION GATES`,'[MCC COMPARTMENT] REVERSING ACTUATOR FEEDER & TRANSFER HOUSE',ltGatesAndDividers,'#f8f6fb','#9f93b8',formatLoadCard)+14;
      }
      if(ltDustWaterAir.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(5,Math.max(3,ltDustWaterAir.length)),'3E',`SECTION 3E · 415 V LT DUST SUPPRESSION, DUST EXTRACTION, AIR COMPRESSORS & SUMP PUMPS (${ltDustWaterAir.length} FEEDERS)`,'[MCC COMPARTMENT] PUMP / BAGFILTER FAN / COMPRESSOR FEEDER',ltDustWaterAir,'#f1f7f8','#7aaab5',formatLoadCard)+14;
      }
      if(ltHoistsInstPdb.length){
        curY+=drawSwbZone(frameX,curY,frameW,Math.min(5,Math.max(3,ltHoistsInstPdb.length)),'3F',`SECTION 3F · 415 V LT HOISTS, SAMPLERS, ANALYZERS (CV), BELT SCALES (EAT), MAGNETS (AT), DETECTORS (QB) & LOCAL PDBs (${ltHoistsInstPdb.length} FEEDERS)`,'[MCC COMPARTMENT] HOIST / INSTRUMENT / MAGNET / PDB FEEDER',ltHoistsInstPdb,'#f7f8f2','#9cab7e',formatLoadCard)+14;
      }

      // Bind dropped parent/child IDs to their kept partner position so all edges & inspector lookups resolve
      for(const [droppedId,keptId] of dropParentMap.entries()){
        if(positions.has(keptId)&&!positions.has(droppedId))positions.set(droppedId,positions.get(keptId));
      }

      // Draw clean upstream-to-switchboard supply edges (Tier 1 -> Tier 2) without cluttering outgoing feeder grids
      const tier12Edges=s.edges.filter(a=>tier12Ids.has(a.canonical_subject)&&tier12Ids.has(a.canonical_object)&&positions.has(a.canonical_subject)&&positions.has(a.canonical_object)&&positions.get(a.canonical_subject)!==positions.get(a.canonical_object)&&Math.abs(positions.get(a.canonical_subject).y-positions.get(a.canonical_object).y)<=260);
      const allClean=[...tier12Edges,...xrayExtraEdges(positions,tier12Edges)];
      s.width=1520;s.height=Math.max(760,curY+16);s.initialHeight=Math.min(s.height,960);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,sub:d.sub,max:23})).join('');
    }

    // 13. Bespoke Water Pump Houses (DS Pump House-1/2), CHP Coal Run-off Pond & Service/Potable Water Systems P&ID Schematic
    if(/^DS Pump House-[12]$|^CHP Coal Run-off Pond|^CHP (?:Service|Potable) Water System/i.test(s.title)){
      const frameX=55,frameTop=40,frameW=1410;
      const tanksAndValves=parts.filter(n=>n.kind==='tank'||/tank|chamber|compartment|MGV-|level switch/i.test(n.label));
      const pumpsStrainersComp=parts.filter(n=>!tanksAndValves.includes(n)&&(['pump','filter','compressor'].includes(n.kind)||/pump|DUP-01|filter|compressor|DFDSP|SPDSP|LSDSP|SWP|PWP|DFDSC/i.test(n.label)));
      const headersPanelsInst=parts.filter(n=>!tanksAndValves.includes(n)&&!pumpsStrainersComp.includes(n));

      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="52" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · PUMPING STATION, SUCTION STRAINERS, STORAGE COMPARTMENTS & HEADER P&ID SCHEMATIC`,'ps-zone-label','start'),
        text(frameX+22,frameTop+40,'STAGE 1: RCC STORAGE COMPARTMENTS & LEVEL/INLET MGVs → STAGE 2: DUPLEX SUCTION STRAINERS (DUP-01), PUMPS & COMPRESSORS → STAGE 3: DISCHARGE HEADERS, PRVs & DP/PRESSURE SWITCHES','ps-Subtle','start')
      );
      let curY=frameTop+66;
      if(tanksAndValves.length){
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(2,tanksAndValves.length)),'1','STAGE 1 · RCC WATER STORAGE COMPARTMENTS, SETTLING CHAMBERS, INLET MOTORIZED VALVES (MGV) & LEVEL SWITCHES','STORAGE & MAKEUP LEVEL CONTROL',tanksAndValves,'#eff5f6','#9ebec7')+14;
      }
      if(pumpsStrainersComp.length){
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(5,Math.max(2,pumpsStrainersComp.length)),'2','STAGE 2 · DUPLEX SUCTION STRAINERS (DUP-01), DUTY/STANDBY WATER PUMPS (1W+1S) & AIR COMPRESSORS','FILTRATION, PUMPING & COMPRESSED AIR',pumpsStrainersComp,'#f5f9f5','#8eab99')+14;
      }
      if(headersPanelsInst.length){
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(5,Math.max(2,headersPanelsInst.length)),'3','STAGE 3 · COMMON SUPPLY HEADERS, RECIRCULATION PRVs, LOCAL STARTER PANELS & DP / PRESSURE SWITCHES (DPS / PS)','DISCHARGE MANIFOLDS & PROTECTION INTERLOCKS',headersPanelsInst,'#faf6ee','#cbb486')+18;
      }
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED PLANT WATER SYSTEMS (DFDS, SPDS, SWS, PWS, LSDS), RUNOFF SUMPS & CONSUMER INTERFACES',outside.slice(0,20),5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(760,curY+10);s.initialHeight=Math.min(s.height,940);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:21})).join('');
    }

    // 14. Bespoke In-Line Belt Instrumentation (AT-1..4 ILMS, QB-1..4 Metal Detectors, EAT-1..4 / Belt Weighers, CV-1..6 Coal Analyzers) & Diverter/Isolation Gates (FG, KB-FD, KB-RG, KB-RPG)
    if(['electromagnet','radiation-source','detector','weigher','gate'].includes(s.kind)){
      const frameX=55,frameTop=40,frameW=1410;
      if(s.kind==='gate'){
        const actDrive=parts.filter(n=>['drive','actuator','motor','gearbox','rack-pinion','needle-rods'].includes(n.kind)||/actuator|motor|handwheel|lever|rack|pinion|rod/i.test(n.label));
        const gateBody=parts.filter(n=>!actDrive.includes(n)&&(['gate','chute','wear-liner'].includes(n.kind)||/casing|flap|blade|liner|frame|chute|door/i.test(n.label)));
        const gateInst=parts.filter(n=>!actDrive.includes(n)&&!gateBody.includes(n));

        decor.push(
          `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="52" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
          text(frameX+22,frameTop+22,`${s.title.toUpperCase()} ·CHUTE DIVERTER / ISOLATION GATE ACTUATION, LINED CASING & LIMIT-SWITCH SCHEMATIC`,'ps-zone-label','start'),
          text(frameX+22,frameTop+40,'STAGE 1: LINEAR / ROTARY / HYDRAULIC ACTUATOR & DRIVE → STAGE 2: HARDOX-LINED CASING, FLAP BLADE / SLIDE PLATE & CHUTES → STAGE 3: PLUMMER BLOCK BEARINGS, SEALS & LIMIT SWITCHES','ps-Subtle','start')
        );
        let curY=frameTop+66;
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(1,actDrive.length)),'1','ACTUATION DRIVE, RACK & PINION / LEVER ARM & MANUAL OVERRIDE','MOTORIZED / HYDRAULIC / MANUAL ACTUATION',actDrive,'#faf6ee','#cbb486')+14;
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(1,gateBody.length)),'2','HARDOX-400 LINED GATE CASING, DIVERTER FLAP / SLIDING BLADE & INSPECTION DOORS','COAL STREAM DIVERSION & WEAR PROTECTION',gateBody,'#f5f9f5','#8eab99')+14;
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(1,gateInst.length)),'3','PLUMMER BLOCK BEARINGS (SNA 530 / SN 518), SHAFT SEALS & POSITION / THRUST LIMIT SWITCHES','SHAFT SUPPORT & PLC POSITION FEEDBACK',gateInst,'#f4f7fa','#97b0c4')+18;
        curY=drawBottomDock(frameX,curY,frameW,'CONNECTED UPSTREAM CHUTE / TRIPPER & DOWNSTREAM RECEIVING BELT CONVEYORS',outside,5);
        const allClean=xrayExtraEdges(positions,[]);
        s.width=1520;s.height=Math.max(720,curY+10);s.initialHeight=Math.min(s.height,880);
        return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
      }

      // In-Line Belt Instrumentation: AT-1..4 (ILMS), QB-1..4 (Metal Detector), EAT-1..4 / Belt Weighers, CV-1..6 (Online Coal Analyzer)
      const isIlms=s.kind==='electromagnet';
      const isMd=s.kind==='detector';
      const isBw=s.kind==='weigher';
      const activeCore=parts.filter(n=>['electromagnet','radiation-source','search-coil','weigher','trolley'].includes(n.kind)||/electromagnet|core|coil|source-holder|detector and cradle|probe|weighbridge|load cell|trolley/i.test(n.label));
      const mechAux=parts.filter(n=>!activeCore.includes(n)&&!/rectifier|integrator|electronic unit|junction box|rate meter|cabinet|reset.*panel/i.test(n.label));
      const ctrlCab=parts.filter(n=>!activeCore.includes(n)&&!mechAux.includes(n));

      const subTitle=isIlms?'CROSS-BELT OIL-COOLED INLINE MAGNETIC SEPARATOR (ILMS · 1150 GAUSS @ 450 MM · SELF-CLEANING CLEATED BELT)':isMd?'UNDER/OVER-BELT TANDEM SEARCH-COIL METAL DETECTOR (SQTA) & SANDBAG DROP MARKER':isBw?'4-IDLER STRAIN-GAUGE CONVEYOR BELT SCALE WEIGHBRIDGE, 60-12C TACHOMETER & MICRO-TECH 9101/9201 INTEGRATOR':'CROSS-BELT PROMPT-GAMMA (Cf-252) ONLINE ELEMENTAL & MOISTURE COAL ANALYZER';
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="88" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · ${subTitle}`,'ps-zone-label','start'),
        // Cross-belt / under-belt conveyor technical strip
        `<path d="M120 ${frameTop+62}H1340" stroke="#3d6352" stroke-width="6"/>`,
        `<path d="M140 ${frameTop+52}H1320" stroke="#b37736" stroke-width="3" stroke-dasharray="10 5" marker-end="url(#ps-arrow)"/>`,
        `<rect x="565" y="${frameTop+34}" width="330" height="44" rx="6" fill="#fcfdf9" stroke="#7d9989" stroke-width="2"/>`,
        text(730,frameTop+54,isIlms?'SUSPENDED 1150 G MAGNET ZONE':isMd?'TANDEM SEARCH-COIL APERTURE':isBw?'4-IDLER WEIGHBRIDGE SPAN':'Cf-252 PGNAA ANALYSIS TUNNEL','ps-zone-label'),
        text(730,frameTop+70,'ACTIVE CONVEYOR BELT SENSING / EXTRACTION ZONE','ps-Subtle')
      );

      let curY=frameTop+102;
      curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(1,activeCore.length)),'1',isIlms?'OIL-COOLED ELECTROMAGNET BODY (21.5 kW DC COIL, 1000 L OIL BATH & RTD) & OVERHEAD TROLLEYS':isMd?'TANDEM SEARCH-COIL PROBE & NON-MAGNETIC TROUGHING IDLERS':isBw?'4-IDLER WEIGHBRIDGE FRAME, CHECK RODS & 350-OHM STRAIN-GAUGE LOAD CELLS':'Cf-252 RADIATION SOURCE HOLDER & SCINTILLATION DETECTOR CRADLE ASSEMBLY','PRIMARY SENSING / EXTRACTION ASSEMBLY',activeCore,'#f5f9f5','#8eab99')+14;
      if(mechAux.length){
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(1,mechAux.length)),'2',isIlms?'SELF-CLEANING CLEATED EXTRACTOR BELT (11 kW FLAMEPROOF DRIVE, JZSS) & TRAMP-IRON CHUTE':isMd?'ELECTROMAGNETIC SANDBAG DROP MARKER & MARKER INTERLOCK SWITCH':isBw?'60-12C RETURN-BELT TACHOMETER SPEED SENSOR & CERTIFIED CALIBRATION TEST WEIGHTS':'RADIATION SHIELDING FRAME, TOP ENCLOSURE HOOD & MAINTENANCE ACCESS','MECHANICAL CARRIAGE, CALIBRATION & DISCHARGE',mechAux,'#faf6ee','#cbb486')+14;
      }
      if(ctrlCab.length){
        curY+=drawZoneCard(frameX,curY,frameW,Math.min(4,Math.max(1,ctrlCab.length)),'3',isIlms?'TRANSFORMER-RECTIFIER CUM LOCAL CONTROL PANEL':isMd?'SQTA ELECTRONIC EVALUATION UNIT, AUDIO-VISUAL HOOTER/LAMP & RESET PANEL':isBw?'LOAD-CELL SUMMING JUNCTION BOX, LOCAL TOTALIZER & MICRO-TECH 9101/9201 INTEGRATOR (IP66)':'LOCAL ANALYZER EVALUATION CABINET & PLANT DCS INTERFACE','POWER SUPPLY, SIGNAL PROCESSING & PLC/DCS INTERFACE',ctrlCab,'#f4f7fa','#97b0c4')+18;
      }
      curY=drawBottomDock(frameX,curY,frameW,'CONNECTED HOST BELT CONVEYOR, TRANSFER HOUSE & PLANT DCS INTERFACES',outside,5);
      const allClean=xrayExtraEdges(positions,[]);
      s.width=1520;s.height=Math.max(720,curY+10);s.initialHeight=Math.min(s.height,880);
      return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
    }

    // 15. Clean Structured Engineering Cards for Remaining Assemblies (Couplings, Crusher Cage/Housing/Foundation, Elevators, Fire Protection, etc.)
    const frameX=75,frameTop=44,frameW=1250;
    let curY=frameTop+56;
    decor.push(
      `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="44" rx="10" fill="#eef4ef" stroke="#8aa596" stroke-width="1.8"/>`,
      text(frameX+22,frameTop+27,`${(s.title.length>68?s.title.slice(0,66)+'…':s.title).toUpperCase()} · COMPONENT ANATOMY, ACTUATION & INSTRUMENTATION SCHEMATIC`,'ps-zone-label','start')
    );
    if(s.kind==='coupling'){
      const hydroCore=parts.filter(n=>['coupling-hub','actuator','tank'].includes(n.kind)||/impeller|scoop|sump/i.test(n.label));
      const oilCool=parts.filter(n=>!hydroCore.includes(n)&&(['pump','filter','cooler','valve'].includes(n.kind)||/pump|filter|strainer|radiator|cooler|valve/i.test(n.label)));
      const instBox=parts.filter(n=>!hydroCore.includes(n)&&!oilCool.includes(n));
      curY+=drawZoneCard(frameX,curY,frameW,4,'1','HYDRODYNAMIC IMPELLER/RUNNER, SCOOP TUBE ACTUATOR & OIL SUMP','WORKING CIRCUIT & VARIABLE SPEED CONTROL',hydroCore,'#f5f9f5','#8eab99')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'2','OIL CIRCULATION PUMP, SUCTION/RETURN FILTERS & AIR-BLAST RADIATOR','LUBRICATION & CLOSED-LOOP COOLING',oilCool,'#eff5f6','#9ebec7')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'3','TEMPERATURE / PRESSURE SWITCHES (TS1, TS2, PS, FSO, DPS), FUSIBLE PLUG & CONTROL PANEL','THERMAL & HYDRAULIC PROTECTION',instBox,'#faf6ee','#cbb486')+18;
    }else if(s.kind==='cage'||s.kind==='crusher-housing'||s.kind==='foundation'){
      const primaryCore=parts.filter(n=>['cage','screen-plate','crusher-housing','chute','spring-isolator'].includes(n.kind));
      const adjustWear=parts.filter(n=>!primaryCore.includes(n)&&['cage-adjuster','wear-liner','tramp-trap','access','cylinder','actuator'].includes(n.kind));
      const auxRest=parts.filter(n=>!primaryCore.includes(n)&&!adjustWear.includes(n));
      curY+=drawZoneCard(frameX,curY,frameW,4,'1',s.kind==='cage'?'CAGE FRAME & BREAKER / UPPER / LOWER SCREEN PLATES':s.kind==='foundation'?'HELICAL ISOLATION SPRINGS & VISCODAMPERS':'SPLIT HOUSING FRAMES & INLET HOPPER HOOD','PRIMARY STRUCTURAL ASSEMBLY',primaryCore,'#f5f9f5','#8eab99')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'2',s.kind==='cage'?'ECCENTRIC RATCHET & COMPRESSION SPRING CAGE ADJUSTER':'HARDOX WEAR LINERS, INSPECTION DOORS & TRAMP-IRON TRAP','ADJUSTMENT, WEAR PROTECTION & ACCESS',adjustWear,'#faf6ee','#cbb486')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'3','PROTECTION SWITCHES & MECHANICAL INTERFACES','MONITORING & SAFETY',auxRest,'#f4f7fa','#97b0c4')+18;
    }else if(s.kind==='elevator'){
      const driveTraction=parts.filter(n=>/traction|motor|gearbox|sheave|diverter|drive/i.test(n.label));
      const carCounter=parts.filter(n=>!driveTraction.includes(n)&&/car|cage|counterweight|rope|guide/i.test(n.label));
      const safetyCtrl=parts.filter(n=>!driveTraction.includes(n)&&!carCounter.includes(n));
      curY+=drawZoneCard(frameX,curY,frameW,4,'1','TRACTION VVVF DRIVE MOTOR, WORM GEARBOX, FAIL-SAFE BRAKE & SHEAVES','MACHINE ROOM TRACTION DRIVE',driveTraction,'#f5f9f5','#8eab99')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'2','PASSENGER / GOODS CAR, AUTOMATIC DOORS, SUSPENSION ROPES & COUNTERWEIGHT','HOISTWAY CAR & COUNTERWEIGHT LOOP',carCounter,'#faf6ee','#cbb486')+14;
      curY+=drawZoneCard(frameX,curY,frameW,4,'3','OVERSPEED GOVERNOR, AUTOMATIC RESCUE DEVICE (ARD), FIREMAN SWITCH & INTERCOM','SAFETY GEAR & EMERGENCY RESCUE',safetyCtrl,'#f4f7fa','#97b0c4')+18;
    }else{
      const driveOrAct=parts.filter(n=>['drive','motor','gearbox','coupling','pump','compressor','fan','hoist','actuator','thruster','cylinder'].includes(n.kind));
      const bodyMech=parts.filter(n=>!driveOrAct.includes(n)&&!['sensor','level-sensor','panel','switchboard','protection'].includes(n.kind));
      const instCtrl=parts.filter(n=>!driveOrAct.includes(n)&&!bodyMech.includes(n));
      if(driveOrAct.length)curY+=drawZoneCard(frameX,curY,frameW,4,'1','DRIVE, PUMPING & ACTUATION ASSEMBLIES','POWER & MOTION',driveOrAct,'#f5f9f5','#8eab99')+14;
      if(bodyMech.length)curY+=drawZoneCard(frameX,curY,frameW,4,'2','PROCESS VESSELS, MECHANICAL BODIES, PIPING & WEAR PARTS','PROCESS & STRUCTURAL CORE',bodyMech,'#faf6ee','#cbb486')+14;
      if(instCtrl.length)curY+=drawZoneCard(frameX,curY,frameW,4,'3','INSTRUMENTATION, SENSORS, LOCAL PANELS & PROTECTION INTERLOCKS','CONTROL & MONITORING',instCtrl,'#f4f7fa','#97b0c4')+18;
    }

    curY=drawBottomDock(frameX,curY,frameW,'CONNECTED PARENT EQUIPMENT, UPSTREAM/DOWNSTREAM INTERFACES & UTILITIES',outside.slice(0,20),4);
    const partIds=new Set(parts.map(n=>n.id));
    const cleanEdges=filterCleanInternalEdges(s.edges,positions,partIds);
    const allClean=[...cleanEdges,...xrayExtraEdges(positions,cleanEdges)];
    s.width=1400;s.height=Math.max(680,curY+10);s.initialHeight=Math.min(s.height,880);
    return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:22})).join('');
  }

  function classifyConveyorAnatomy(parts,self,includeSelf=false){
    const cleanName=n=>short(n).toLowerCase();
    const isDrivePart=n=>['motor','coupling','gearbox','brake','drive'].includes(n.kind)||(/pulley/i.test(n.label)&&/head|drive/i.test(cleanName(n))&&!/bearing|locking|hub|lagging/i.test(n.label));
    const isProtection=n=>!isDrivePart(n)&&(['sensor','protection','level-sensor'].includes(n.kind)||/\b(pcs|bss|zss|ubs)\b|pull-cord|belt-sway|zero-speed|switch|protection/i.test(n.label));
    const isTailLoading=n=>!isDrivePart(n)&&!isProtection(n)&&(/skirt|deck|impact idler|transition idler|receiving chute/i.test(cleanName(n)));
    const isHeadCleanerDischarge=n=>!isDrivePart(n)&&!isProtection(n)&&!isTailLoading(n)&&((n.kind==='scraper'&&!/v-plough|v-plow|internal/i.test(cleanName(n)))||(['chute','tripper','gate'].includes(n.kind)&&!/skirt|deck/i.test(cleanName(n))));
    const isCarryStrand=n=>!isDrivePart(n)&&!isProtection(n)&&!isTailLoading(n)&&!isHeadCleanerDischarge(n)&&(['belt','weigher','detector','electromagnet','radiation-source','marker'].includes(n.kind)||(/idler/i.test(cleanName(n))&&/carrying|weighing|nonmagnetic/i.test(cleanName(n))));
    const isTakeupSystem=n=>!isDrivePart(n)&&!isProtection(n)&&!isTailLoading(n)&&!isHeadCleanerDischarge(n)&&!isCarryStrand(n)&&(['takeup','counterweight','trolley','cylinder','hydraulic'].includes(n.kind)||(/take-up|counterweight|wire rope|reeving|sheave|hgtu/i.test(cleanName(n))&&!/^tail and take-up|^tail pulley/i.test(cleanName(n))));
    const isReturnIdlers=n=>!isDrivePart(n)&&!isProtection(n)&&!isTailLoading(n)&&!isHeadCleanerDischarge(n)&&!isCarryStrand(n)&&!isTakeupSystem(n)&&(/return idler|return roller|flat return|self-cleaning return/i.test(cleanName(n)));
    const isPulleyAndPlough=n=>!isDrivePart(n)&&!isProtection(n)&&!isTailLoading(n)&&!isHeadCleanerDischarge(n)&&!isCarryStrand(n)&&!isTakeupSystem(n)&&!isReturnIdlers(n);

    const driveOrder=n=>{
      const l=cleanName(n);
      if(n.kind==='drive')return 0;
      if(n.kind==='motor')return 1;
      if(n.kind==='coupling'&&!/low.speed|geared coupling/i.test(l))return 2;
      if(n.kind==='gearbox')return 3;
      if(n.kind==='coupling'&&/low.speed|geared coupling/i.test(l))return 4;
      if(n.kind==='pulley')return 5;
      if(n.kind==='brake')return 6;
      return 7;
    };
    const takeupOrder=n=>{
      const l=cleanName(n);
      if(/take-up assembly|vertical gravity|horizontal gravity|screw take-up/i.test(l))return 1;
      if(/pulley|trolley/i.test(l))return 2;
      if(/rope|sheave|reeving/i.test(l))return 3;
      if(/counterweight/i.test(l))return 4;
      return 5;
    };
    const tailOrder=n=>{
      const l=cleanName(n);
      if(/skirt|deck|receiving/i.test(l))return 1;
      if(/impact/i.test(l))return 2;
      if(/transition/i.test(l))return 3;
      return 4;
    };
    const carryOrder=n=>{
      const l=cleanName(n);
      if(n.kind==='belt')return 1;
      if(/^carrying/i.test(l))return 2;
      if(/self-aligning/i.test(l))return 3;
      return 4;
    };

    const tailZone=parts.filter(isTailLoading).sort((a,b)=>tailOrder(a)-tailOrder(b)||a.label.localeCompare(b.label));
    const carryZone=parts.filter(isCarryStrand).sort((a,b)=>carryOrder(a)-carryOrder(b)||a.label.localeCompare(b.label));
    const headZone=parts.filter(isHeadCleanerDischarge);
    const pulleyPloughZone=parts.filter(isPulleyAndPlough);
    const takeupZone=parts.filter(isTakeupSystem).sort((a,b)=>takeupOrder(a)-takeupOrder(b)||a.label.localeCompare(b.label));
    const returnIdlerZone=parts.filter(isReturnIdlers);
    const driveParts=parts.filter(isDrivePart).sort((a,b)=>driveOrder(a)-driveOrder(b)||a.label.localeCompare(b.label));
    const protParts=parts.filter(isProtection);

    if(self&&(includeSelf||!tailZone.length)){
      if(!tailZone.length)tailZone.unshift(self);
      else carryZone.unshift(self);
    }
    return {tailZone,carryZone,headZone,pulleyPloughZone,takeupZone,returnIdlerZone,driveParts,protParts};
  }

  function conveyorMatrixScene(){
    const narrow=window.matchMedia('(max-width:760px)').matches;
    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const self=s.nodes.find(n=>n.role==='self');
    const byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(n,x,y,w=136,h=72,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};

    const {tailZone,carryZone,headZone,pulleyPloughZone,takeupZone,returnIdlerZone,driveParts,protParts}=classifyConveyorAnatomy(parts,self,true);

    const ownSet=new Set([s.id,...parts.map(n=>n.id)]);
    const matEdges=s.edges.filter(a=>a.context?.network==='material');
    const isSubChuteOfVisible=n=>{
      if(n.kind!=='chute')return false;
      const parents=M.closestParents(p,n.id);
      return parents.some(pid=>byId.has(pid)&&pid!==s.id);
    };
    const inlets=[],outlets=[],services=[];
    for(const n of outside){
      const feedsUs=matEdges.some(a=>a.canonical_subject===n.id&&ownSet.has(a.canonical_object));
      const fedByUs=matEdges.some(a=>ownSet.has(a.canonical_subject)&&a.canonical_object===n.id);
      if(isSubChuteOfVisible(n)){services.push(n);continue;}
      if(feedsUs&&!fedByUs)inlets.push(n);
      else if(fedByUs)outlets.push(n);
      else services.push(n);
    }
    inlets.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    outlets.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    services.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));

    const frameX=narrow?20:185,frameW=narrow?520:840;
    const centerX=frameX+frameW/2;
    const rowH=166;

    let curY=44;
    if(inlets.length){
      decor.push(text(centerX,24,'RECEIVING FROM UPSTREAM EQUIPMENT','ps-zone-label'));
      const cols=Math.min(inlets.length,narrow?3:4),spacing=176,boxW=136;
      inlets.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,inlets.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,curY+r*154,boxW,70);
      });
      curY+=Math.ceil(inlets.length/cols)*154+34;
    }else{
      curY=55;
    }

    const frameTop=curY;
    const bands=[];
    const placeGridBand=(label,items,customCols=null)=>{
      if(!items.length)return;
      bands.push([curY,label]);
      const rowY=curY+28;
      const cols=customCols||(narrow?3:Math.min(items.length,4));
      const spacing=narrow?168:(cols>=5?146:182),boxW=cols>=5?122:138;
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,rowY+r*rowH,boxW,70);
      });
      curY=rowY+Math.ceil(items.length/cols)*rowH;
    };

    placeGridBand('1 · TAIL LOADING, CARRYING STRAND & INLINE METERING',[...tailZone,...carryZone]);
    placeGridBand('2 · HEAD DRIVE POWERTRAIN',driveParts,narrow?3:Math.min(driveParts.length,6));
    placeGridBand('3 · PULLEYS & GRAVITY TAKE-UP TENSIONING',[...pulleyPloughZone.filter(n=>n.kind!=='scraper'),...takeupZone]);
    placeGridBand('4 · RETURN STRAND IDLERS & BELT SCRAPERS',[...returnIdlerZone,...headZone.filter(n=>n.kind==='scraper'),...pulleyPloughZone.filter(n=>n.kind==='scraper')]);
    placeGridBand('5 · DISCHARGE CHUTES, TRIPPERS & BELT PROTECTION (PCS / BSS / ZSS)',[...headZone.filter(n=>n.kind!=='scraper'),...protParts]);

    const frameH=Math.max(240,curY-frameTop+12);
    decor.unshift(`<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
      text(frameX+20,frameTop+20,s.title.toUpperCase()+' · CATEGORIZED SUBSYSTEM COMPONENT MATRIX','ps-zone-label','start'));
    for(const [y,label] of bands.slice(1)){
      decor.push(`<path d="M${frameX+14} ${y}H${frameX+frameW-14}" class="ps-floor"/>`);
    }
    for(const [y,label] of bands){
      decor.push(text(frameX+22,y+18,label,'ps-zone-label','start'));
    }

    let bottomY=frameTop+frameH+54;
    if(outlets.length){
      decor.push(text(centerX,bottomY-18,'DISCHARGE TO DOWNSTREAM ROUTE','ps-zone-label'));
      const cols=Math.min(outlets.length,narrow?3:4),spacing=178,boxW=140;
      outlets.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,outlets.length-r*cols);
        const startX=centerX-(rowCount*spacing)/2+(spacing-boxW)/2;
        put(n,startX+c*spacing,bottomY+r*154,boxW,72);
      });
      bottomY+=Math.ceil(outlets.length/cols)*154+25;
    }

    const subAssyIds=(p.children.get(s.id)||[]).map(a=>a.canonical_subject).filter(cid=>p.entities.has(cid)&&(p.classes.get(cid)||[]).includes('functional_assembly'));
    const subAssyNodes=subAssyIds.map(cid=>({id:cid,label:p.entities.get(cid).label,kind:M.kind(p,cid),role:'part'}));
    const rightItems=[...subAssyNodes,...services].filter(n=>!positions.has(n.id));
    if(rightItems.length){
      if(!narrow){
        const sideX=1060,sideCols=rightItems.length>5?2:1;
        decor.push(text(sideX+(sideCols===2?145:72),frameTop+10,'SUB-ASSEMBLIES & SERVICES','ps-zone-label'));
        rightItems.forEach((n,i)=>{
          const c=i%sideCols,r=Math.floor(i/sideCols);
          put(n,sideX+c*160,frameTop+30+r*166,134,70);
        });
      }else{
        decor.push(text(centerX,bottomY+15,'SUB-ASSEMBLIES & SERVICES','ps-zone-label'));
        rightItems.forEach((n,i)=>put(n,30+(i%3)*175,bottomY+35+Math.floor(i/3)*154,145,72));
        bottomY+=45+Math.ceil(rightItems.length/3)*154;
      }
    }

    const sidebarSet=new Set(rightItems.map(n=>n.id));
    const inletSet=new Set(inlets.map(n=>n.id));
    const outletSet=new Set(outlets.map(n=>n.id));
    const dischargeParts=headZone.filter(n=>n.kind!=='scraper');
    const dischargeSet=new Set(dischargeParts.map(n=>n.id));
    const driveSet=new Set(driveParts.map(n=>n.id));

    const cleanEdges=s.edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      if(sidebarSet.has(u)||sidebarSet.has(v))return false;
      if(a.context?.network==='mechanical'){
        return (driveSet.has(u)&&driveSet.has(v)&&Math.abs(positions.get(u).y-positions.get(v).y)<30)||(Math.abs(positions.get(u).y-positions.get(v).y)<25&&Math.abs(positions.get(u).x-positions.get(v).x)<220);
      }
      if(a.context?.network==='material'){
        if(inletSet.has(u)&&v===s.id&&positions.get(v).y-positions.get(u).y<=225)return true;
        if(dischargeSet.has(u)&&outletSet.has(v)&&positions.get(v).y-positions.get(u).y<=225)return true;
        return false;
      }
      return false;
    });

    const sideBottom=rightItems.length&&!narrow?frameTop+50+Math.ceil(rightItems.length/(rightItems.length>5?2:1))*166:0;
    s.width=narrow?570:(rightItems.length>5?1410:1260);
    s.height=Math.max(780,bottomY+45,sideBottom+45);
    s.initialHeight=Math.min(s.height,940);
    const allClean=[...cleanEdges,...xrayExtraEdges(positions,cleanEdges)];
    return decor.join('')+edgeMarkup(allClean,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:d.w<=134?19:24})).join('');
  }

  /**
   * Anatomical & Subsystem-Grouped Conveyor Schematic (Default View for Conveyors & Belt Feeders)
   */
  function conveyorScene(){
    const narrow=window.matchMedia('(max-width:760px)').matches;
    if(narrow||q().get('spread')==='1')return conveyorMatrixScene();

    const positions=new Map(),routes=new Map(),drawn=[],decor=[];
    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located');
    const outside=s.nodes.filter(n=>n.role==='connected');
    const self=s.nodes.find(n=>n.role==='self');
    const byId=new Map(s.nodes.map(n=>[n.id,n]));
    const put=(n,x,y,w=122,h=64,title)=>{if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.push({n,x,y,w,h,title});};

    const {tailZone,carryZone,headZone,pulleyPloughZone,takeupZone,returnIdlerZone,driveParts,protParts}=classifyConveyorAnatomy(parts,self,false);

    const ownSet=new Set([s.id,...parts.map(n=>n.id)]);
    const matEdges=s.edges.filter(a=>a.context?.network==='material');
    const isSubChuteOfVisible=n=>{
      if(n.kind!=='chute')return false;
      const parents=M.closestParents(p,n.id);
      return parents.some(pid=>byId.has(pid)&&pid!==s.id);
    };
    const inlets=[],outlets=[],services=[];
    for(const n of outside){
      const feedsUs=matEdges.some(a=>a.canonical_subject===n.id&&ownSet.has(a.canonical_object));
      const fedByUs=matEdges.some(a=>ownSet.has(a.canonical_subject)&&a.canonical_object===n.id);
      if(isSubChuteOfVisible(n)){services.push(n);continue;}
      if(feedsUs&&!fedByUs)inlets.push(n);
      else if(fedByUs)outlets.push(n);
      else services.push(n);
    }
    inlets.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    outlets.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    services.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));

    const dischargeChutes=headZone.filter(n=>n.kind!=='scraper');
    const headScrapers=headZone.filter(n=>n.kind==='scraper');
    const z3Items=[...headScrapers,...dischargeChutes];

    // Wide 1720px canvas so Upper & Lower Subsystem Cards fit 3-4 items per row with zero halo overlap
    const frameX=178,frameY=38,frameW=1364;
    // Upper Tier Card widths: Zone 1 (Tail, 3 cols), Zone 2 (Carry & Metering, 4 cols), Zone 3 (Head, 2 cols)
    const u1X=194,u1W=426,u1Cols=3;
    const u2X=632,u2W=564,u2Cols=4;
    const u3X=1208,u3W=318,u3Cols=2;
    // Lower Tier Card widths: Zone 4 (Pulleys & V-Plough, 3 cols), Zone 5 (Take-Up System, 3 cols), Zone 6 (Return Idlers, 3 cols)
    const l1X=194,l1W=432,l1Cols=3;
    const l2X=638,l2W=436,l2Cols=3;
    const l3X=1086,l3W=440,l3Cols=3;
    const cardRowH=158,boxW=112,boxH=62;

    const placeZoneCard=(cardX,cardY,cardW,cardH,cols,badgeNum,title,subtitle,items,tint='#f6faf2',stroke='#b7c8b0')=>{
      decor.push(
        `<rect x="${cardX}" y="${cardY}" width="${cardW}" height="${cardH}" rx="10" fill="${tint}" fill-opacity=".8" stroke="${stroke}" stroke-width="1.6"/>`,
        `<rect x="${cardX+10}" y="${cardY+9}" width="20" height="18" rx="5" fill="#355d47"/>`,
        `<text x="${cardX+20}" y="${cardY+22}" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">${safe(badgeNum)}</text>`,
        text(cardX+36,cardY+21,title,'ps-zone-label','start'),
        subtitle?`<text x="${cardX+cardW-10}" y="${cardY+21}" text-anchor="end" fill="#6b7e6b" font-size="9" font-weight="600">${safe(subtitle)}</text>`:``
      );
      if(!items.length)return;
      const itemStartY=cardY+36;
      items.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,items.length-r*cols);
        const rStep=Math.min(Math.floor((cardW-20)/Math.max(1,cols)),176);
        const rowSpan=rowCount*rStep;
        const startX=Math.round(cardX+(cardW-rowSpan)/2+(rStep-boxW)/2);
        put(n,startX+c*rStep,itemStartY+r*cardRowH,boxW,boxH);
      });
    };

    // 1. Upper Tier Subsystem Cards (Tail Loading -> Carry Strand & Metering -> Head Cleaners & Discharge)
    const upperY=74;
    const upperMaxRows=Math.max(1,Math.ceil(tailZone.length/u1Cols),Math.ceil(carryZone.length/u2Cols),Math.ceil(z3Items.length/u3Cols));
    const upperCardH=upperMaxRows*cardRowH+36;

    placeZoneCard(u1X,upperY,u1W,upperCardH,u1Cols,'1','TAIL LOADING & SKIRT ZONE','TAIL END',tailZone,'#f7faf2','#b6c8af');
    placeZoneCard(u2X,upperY,u2W,upperCardH,u2Cols,'2','CARRYING STRAND & INLINE METERING','TOP CARRY RUN',carryZone,'#f3f8ef','#9eb898');
    placeZoneCard(u3X,upperY,u3W,upperCardH,u3Cols,'3','HEAD CLEANERS & DISCHARGE','HEAD END',z3Items,'#f7faf2','#b6c8af');

    // 2. Center Continuous Side-Elevation Belt Loop Corridor
    const beltBandY=upperY+upperCardH+14;
    const beltBandH=114;
    const beltTopY=beltBandY+32;
    const beltBotY=beltTopY+42;
    const takeupDropY=beltBotY+26;
    const drumCY=Math.round((beltTopY+beltBotY)/2);
    const tailX=285,headX=1430,takeupX=856;
    // Register virtual position for self on the belt loop so edges to/from s.id route cleanly
    if(self&&!positions.has(s.id))positions.set(s.id,{x:tailX,y:beltTopY,w:headX-tailX,h:beltBotY-beltTopY});

    const carryTicks=[385,500,615,730,845,960,1075,1190,1305].map(tx=>`<g stroke="#4f6f5e" stroke-width="2" fill="none"><path d="M${tx-10} ${beltTopY+4}L${tx-4} ${beltTopY+9}H${tx+4}L${tx+10} ${beltTopY+4}"/><circle cx="${tx}" cy="${beltTopY+6}" r="2.2" fill="#5e7f6d"/></g>`).join('');
    const returnTicks=[430,610,1100,1280].map(tx=>`<circle cx="${tx}" cy="${beltBotY+4}" r="3.5" fill="#769182" stroke="#425d4e" stroke-width="1.5"/>`).join('');

    decor.push(
      `<rect x="${u1X}" y="${beltBandY}" width="${u3X+u3W-u1X}" height="${beltBandH}" rx="12" fill="#e6efe0" fill-opacity=".66" stroke="#96ae92" stroke-width="1.6"/>`,
      `<path d="M${tailX-26} ${beltBandY+4}H${tailX+28}L${tailX+18} ${beltTopY-4}H${tailX-14}Z" fill="#d8c390" fill-opacity=".78" stroke="#8b7340" stroke-width="1.8"/>`,
      `<path d="M${tailX+18} ${beltTopY-4}H${tailX+66}V${beltTopY-1}H${tailX+18}Z" fill="#b7c8b2" stroke="#5b7665" stroke-width="1.4"/>`,
      text(tailX+24,beltBandY+16,'LOADING SKIRT','ps-belt-flow-arrow'),
      `<path class="ps-belt-loop-bg" d="M${tailX} ${beltTopY}H${headX}A21 21 0 0 1 ${headX} ${beltBotY}H${takeupX+82}L${takeupX+38} ${takeupDropY}H${takeupX-38}L${takeupX-82} ${beltBotY}H${tailX}A21 21 0 0 1 ${tailX} ${beltTopY}Z"/>`,
      `<path class="ps-belt-carry" d="M${tailX} ${beltTopY}H${headX}"/>`,
      `<path class="ps-belt-coal" d="M${tailX+12} ${beltTopY-4}H${headX-8}"/>`,
      `<path class="ps-belt-return" d="M${headX} ${beltBotY}H${takeupX+82}L${takeupX+38} ${takeupDropY}H${takeupX-38}L${takeupX-82} ${beltBotY}H${tailX}"/>`,
      carryTicks,
      returnTicks,
      `<circle class="ps-belt-drum" cx="${tailX}" cy="${drumCY}" r="22"/><circle class="ps-wheel" cx="${tailX}" cy="${drumCY}" r="7"/>`,
      `<circle class="ps-belt-drum" cx="${headX}" cy="${drumCY}" r="24"/><circle class="ps-wheel" cx="${headX}" cy="${drumCY}" r="8"/>`,
      `<circle class="ps-belt-drum" cx="${headX-48}" cy="${beltBotY+6}" r="8.5"/>`,
      `<circle class="ps-belt-drum" cx="${takeupX-82}" cy="${beltBotY+5}" r="8"/>`,
      `<circle class="ps-belt-drum" cx="${takeupX+82}" cy="${beltBotY+5}" r="8"/>`,
      `<circle class="ps-belt-drum" cx="${takeupX}" cy="${takeupDropY}" r="13"/><circle class="ps-wheel" cx="${takeupX}" cy="${takeupDropY}" r="4.5"/>`,
      `<path d="M${tailX+44} ${beltBotY-5}L${tailX+58} ${beltBotY-12}V${beltBotY+2}Z" fill="#c7a45e" stroke="#7d6229" stroke-width="1.4"/>`,
      `<path d="M${headX+18} ${drumCY+12}L${headX+32} ${drumCY+24}" stroke="#9e6b32" stroke-width="3.5" stroke-linecap="round"/>`,
      text(tailX+82,drumCY+4,'◀ TAIL PULLEY DRUM','ps-belt-flow-arrow'),
      text(headX-88,drumCY+4,'HEAD DRIVE DRUM ▶','ps-belt-flow-arrow'),
      text(takeupX,beltTopY+19,'CARRY RUN  ▶▶▶  COAL STREAM (TAIL TO HEAD)','ps-belt-flow-arrow'),
      text(takeupX-250,beltBotY-7,'◀◀◀  RETURN STRAND','ps-belt-flow-arrow'),
      text(takeupX+250,beltBotY-7,'◀◀◀  RETURN STRAND','ps-belt-flow-arrow')
    );

    // 3. Lower Tier Subsystem Cards (Pulleys & V-Plough <-- Take-Up System <-- Return Strand Idlers)
    const lowerY=beltBandY+beltBandH+14;
    const rawLowerRows=Math.max(1,Math.ceil(pulleyPloughZone.length/l1Cols),Math.ceil(takeupZone.length/l2Cols),Math.ceil(returnIdlerZone.length/l3Cols));
    const effL1Cols=(rawLowerRows>=2&&pulleyPloughZone.length>=3&&pulleyPloughZone.length<=4)?2:l1Cols;
    const effL2Cols=(rawLowerRows>=2&&takeupZone.length>=3&&takeupZone.length<=4)?2:l2Cols;
    const effL3Cols=(rawLowerRows>=2&&returnIdlerZone.length>=3&&returnIdlerZone.length<=4)?2:l3Cols;
    const lowerMaxRows=Math.max(1,Math.ceil(pulleyPloughZone.length/effL1Cols),Math.ceil(takeupZone.length/effL2Cols),Math.ceil(returnIdlerZone.length/effL3Cols));
    const lowerCardH=lowerMaxRows*cardRowH+36;

    placeZoneCard(l1X,lowerY,l1W,lowerCardH,effL1Cols,'4','PULLEYS, BEND ROLLERS & V-PLOUGH','TAIL & SNUB',pulleyPloughZone,'#f7faf2','#b6c8af');
    placeZoneCard(l2X,lowerY,l2W,lowerCardH,effL2Cols,'5','TAKE-UP TENSIONING SYSTEM','BELT TENSION LOOP',takeupZone,'#f2f7f4','#8fb0a1');
    placeZoneCard(l3X,lowerY,l3W,lowerCardH,effL3Cols,'6','RETURN STRAND IDLERS','BOTTOM RETURN RUN',returnIdlerZone,'#f7faf2','#b6c8af');

    decor.push(
      `<path d="M${takeupX} ${takeupDropY+13}V${lowerY+6}" stroke="#5b7f6e" stroke-width="3" stroke-dasharray="5 3" marker-end="url(#ps-drive-arrow)"/>`
    );

    // 4. Dedicated Full-Width Powertrain Card: Zone 7 (HEAD DRIVE POWERTRAIN)
    let curY=lowerY+lowerCardH+16;
    if(driveParts.length){
      const dCols=Math.min(driveParts.length,6);
      const dRows=Math.ceil(driveParts.length/dCols);
      const driveCardH=dRows*144+44;
      const driveCardW=u3X+u3W-u1X;
      const shaftY=curY+38+31;
      const dStep=Math.floor((driveCardW-36)/Math.max(1,dCols));
      const dBoxW=124,dBoxH=62;
      const startX=u1X+18+Math.round((dStep-dBoxW)/2);

      decor.push(
        `<rect x="${u1X}" y="${curY}" width="${driveCardW}" height="${driveCardH}" rx="10" fill="#f3f0f8" fill-opacity=".75" stroke="#a697c2" stroke-width="1.8"/>`,
        `<rect x="${u1X+10}" y="${curY+9}" width="20" height="18" rx="5" fill="#5e4982"/>`,
        `<text x="${u1X+20}" y="${curY+22}" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">7</text>`,
        text(u1X+36,curY+21,'HEAD DRIVE POWERTRAIN (MOTOR → COUPLING → GEARBOX → LOW-SPEED COUPLING → HEAD PULLEY → THRUSTER BRAKE)','ps-zone-label','start'),
        `<path class="ps-belt-shaft" d="M${startX+30} ${shaftY}H${startX+(dCols-1)*dStep+dBoxW-30}"/>`
      );

      driveParts.forEach((n,i)=>{
        const r=Math.floor(i/dCols),c=i%dCols;
        put(n,startX+c*dStep,curY+38+r*144,dBoxW,dBoxH);
      });

      const headPulleyNode=driveParts.find(n=>n.kind==='pulley')||driveParts.at(-1);
      const hpPos=headPulleyNode?positions.get(headPulleyNode.id):null;
      if(hpPos){
        decor.push(
          `<path d="M${hpPos.x+Math.round(hpPos.w/2)} ${curY}V${curY-8}H${headX+48}V${drumCY}H${headX+25}" fill="none" stroke="#7b639e" stroke-width="2.6" stroke-dasharray="7 4" marker-end="url(#ps-drive-arrow)"/>`
        );
      }
      curY+=driveCardH+16;
    }

    // 5. Bottom Categorized Cards: Zone 8 (Belt Protection & Safety Switches) + Zone 9 (Sub-Assemblies, Dust & Plant Services)
    const subAssyIds=(p.children.get(s.id)||[]).map(a=>a.canonical_subject).filter(cid=>p.entities.has(cid)&&(p.classes.get(cid)||[]).includes('functional_assembly'));
    const subAssyNodes=subAssyIds.map(cid=>({id:cid,label:p.entities.get(cid).label,kind:M.kind(p,cid),role:'part'}));
    const safetyItems=protParts.filter(n=>!positions.has(n.id));
    const serviceItems=[...subAssyNodes,...services].filter(n=>!positions.has(n.id));

    if(safetyItems.length||serviceItems.length){
      const z9Cols=5,z9Rows=Math.max(1,Math.ceil(serviceItems.length/z9Cols));
      const z8Cols=(z9Rows>=2&&safetyItems.length>=3&&safetyItems.length<=4)?2:Math.min(4,Math.max(2,safetyItems.length));
      const z8W=z8Cols<=2?388:540;
      const z9X=u1X+z8W+14,z9W=(u3X+u3W)-z9X;
      const z8Rows=Math.max(1,Math.ceil(safetyItems.length/z8Cols));
      const botCardH=Math.max(z8Rows,z9Rows)*cardRowH+36;

      placeZoneCard(u1X,curY,z8W,botCardH,z8Cols,'8','BELT SAFETY & TRIP SWITCHES','PCS · BSS · ZSS',safetyItems,'#fbf7ec','#d2be8c');
      placeZoneCard(z9X,curY,z9W,botCardH,z9Cols,'9','SUB-ASSEMBLIES, DUST CONTROL & PLANT SERVICES','DFDS · DE · DCS',serviceItems,'#eff5f6','#9ebec7');
      curY+=botCardH+16;
    }

    const frameH=curY-frameY;
    decor.unshift(
      `<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="14" class="ps-building-frame"/>`,
      text(frameX+20,frameY+22,`${s.title.toUpperCase()} · ANATOMICAL CONVEYOR PROFILE, SUBSYSTEM ZONES & DRIVE POWERTRAIN`,'ps-zone-label','start')
    );

    // 6. Left Column Dock: UPSTREAM FEED (x=12..164)
    let leftBottom=0;
    if(inlets.length){
      const inH=inlets.length*158+42;
      decor.push(
        `<rect x="12" y="${upperY}" width="152" height="${inH}" rx="10" fill="#fbf8f0" fill-opacity=".82" stroke="#cbb88e" stroke-width="1.6"/>`,
        text(88,upperY+21,'UPSTREAM FEED','ps-zone-label')
      );
      inlets.forEach((n,i)=>put(n,22,upperY+36+i*158,132,64));
      leftBottom=upperY+inH;
    }

    // 7. Right Column Dock: DISCHARGE & ROUTE (x=1556..1708)
    const rightCol=outlets.filter(n=>!positions.has(n.id));
    let rightBottom=0;
    if(rightCol.length){
      const outH=rightCol.length*158+42;
      decor.push(
        `<rect x="1556" y="${upperY}" width="152" height="${outH}" rx="10" fill="#fbf8f0" fill-opacity=".82" stroke="#cbb88e" stroke-width="1.6"/>`,
        text(1632,upperY+21,'DISCHARGE & ROUTE','ps-zone-label')
      );
      rightCol.forEach((n,i)=>put(n,1566,upperY+36+i*158,132,64));
      rightBottom=upperY+outH;
    }

    const inletSet=new Set(inlets.map(n=>n.id));
    const outletSet=new Set(rightCol.map(n=>n.id));
    const dischargeSet=new Set(dischargeChutes.map(n=>n.id));
    const driveSet=new Set(driveParts.map(n=>n.id));
    const takeupSet=new Set(takeupZone.map(n=>n.id));
    const dockSet=new Set([...safetyItems,...serviceItems].map(n=>n.id));

    for(const u of inlets){
      const pu=positions.get(u.id);
      if(pu){
        routes.set(u.id+'>'+s.id,`M${pu.x+pu.w+2} ${Math.round(pu.y+pu.h/2)}H170V${beltBandY+12}H${tailX-28}`);
      }
    }
    for(const v of rightCol){
      const pv=positions.get(v.id);
      if(pv){
        routes.set(s.id+'>'+v.id,`M${headX+25} ${drumCY}H1548V${Math.round(pv.y+pv.h/2)}H${pv.x-4}`);
      }
    }
    for(const u of dischargeChutes){
      const pu=positions.get(u.id);
      for(const v of rightCol){
        const pv=positions.get(v.id);
        if(pu&&pv){
          routes.set(u.id+'>'+v.id,`M${pu.x+pu.w+2} ${Math.round(pu.y+pu.h/2)}H1548V${Math.round(pv.y+pv.h/2)}H${pv.x-4}`);
        }
      }
    }

    const cleanEdges=s.edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      if(dockSet.has(u)||dockSet.has(v))return false;
      if(a.context?.network==='mechanical'){
        if(driveSet.has(u)&&driveSet.has(v)&&Math.abs(positions.get(u).y-positions.get(v).y)<35&&Math.abs(positions.get(u).x-positions.get(v).x)<=240)return true;
        if(takeupSet.has(u)&&takeupSet.has(v)&&Math.abs(positions.get(u).y-positions.get(v).y)<35)return true;
        return false;
      }
      if(a.context?.network==='material'){
        if(inletSet.has(u)&&v===s.id)return true;
        if(u===s.id&&outletSet.has(v))return true;
        if(dischargeSet.has(u)&&outletSet.has(v))return true;
        return false;
      }
      return false;
    });
    const allEdges=[...cleanEdges,...xrayExtraEdges(positions,cleanEdges)];

    s.width=1720;
    s.height=Math.max(760,frameY+frameH+22,leftBottom+28,rightBottom+28);
    s.initialHeight=Math.min(s.height,1040);
    return decor.join('')+edgeMarkup(allEdges,positions,routes)+drawn.map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:19})).join('');
  }
  function directChuteTransferColumns(){
    const located=(p.incoming.get(s.id)||[]).filter(a=>a.predicate==='located_at').map(a=>a.canonical_subject);
    const locSet=new Set(located);
    const disChutes=located.filter(id=>M.kind(p,id)==='chute'&&/discharge chute/i.test(p.entities.get(id)?.label||'')).sort((a,b)=>(p.entities.get(a)?.label||'').localeCompare(p.entities.get(b)?.label||''));
    if(!disChutes.length)return [];
    return disChutes.map(dc=>{
      const inlets=p.material.filter(a=>a.canonical_object===dc&&M.kind(p,a.canonical_subject)==='conveyor').map(a=>a.canonical_subject);
      const recChutes=p.material.filter(a=>a.canonical_subject===dc&&locSet.has(a.canonical_object)&&M.kind(p,a.canonical_object)==='chute').map(a=>a.canonical_object);
      const gates=[dc,...recChutes];
      const outlets=[...new Set(recChutes.flatMap(rc=>p.material.filter(a=>a.canonical_subject===rc&&M.kind(p,a.canonical_object)==='conveyor').map(a=>a.canonical_object)))];
      const paths=outlets.map(out=>({
        outlet:out,
        edges:p.material.filter(a=>(a.canonical_subject===dc&&recChutes.includes(a.canonical_object))||(recChutes.includes(a.canonical_subject)&&a.canonical_object===out))
      }));
      return {gate:dc,paths,gates,inlets,outlets};
    }).filter(c=>c.inlets.length&&c.outlets.length);
  }
  function getTransferColumns(){
    const std=M.transferColumns(p,s.id);
    return std.length?std:directChuteTransferColumns();
  }
  function equipmentScene(){
    if(s.kind==='transfer'&&M.fixedTripperColumns(p,s.id).length)return fixedTripperScene();
    if(s.kind==='transfer'&&getTransferColumns().length)return transferHouseScene();
    if(s.kind==='sampler-system')return samplingScene();
    if(['stacker','reclaimer'].includes(s.kind))return yardMachineScene();
    if(s.kind==='mechanical')return conveyorMechanicalScene();
    if((s.kind==='conveyor'||s.kind==='feeder')&&s.nodes.some(n=>n.role==='part'||n.role==='located'))return conveyorScene();
    if(s.kind==='crusher-house')return crusherHouseScene();
    if((s.kind==='crusher'||s.kind==='screen'&&s.nodes.some(n=>/Screen body and deck$/.test(n.label)))&&s.nodes.some(n=>n.role==='part'))return crusherMachineScene();
    if(['de-house','de-stream'].includes(s.kind))return dustExtractionScene();
    if(['silo-house','extractor'].includes(s.kind)||s.kind==='silo'&&(p.classes.get(s.id)||[]).includes('coal_silo'))return siloScene();
    if(s.kind==='spray-system'){const drawing=sprayScene();if(drawing)return drawing;}

    const parts=s.nodes.filter(n=>n.role==='part'||n.role==='located'),outside=s.nodes.filter(n=>n.role==='connected'),self=s.nodes.find(n=>n.role==='self');
    const positions=new Map(),routes=new Map(),decor=[];
    let nodes=[];
    function place(n,x,y,w=150,height=78){if(!n||positions.has(n.id))return;positions.set(n.id,{x,y,w,h:height});nodes.push({n,x,y,w,height});}

    if(s.kind==='yard'){
      const frameX=165,frameW=870;
      decor.push(
        `<rect x="${frameX}" y="48" width="${frameW}" height="520" rx="10" class="ps-building-frame"/>`,
        text(frameX+22,72,s.title.toUpperCase()+' · STACKING, STORAGE & RECLAIMING LANE','ps-zone-label','start'),
        `<path d="M${frameX+14} 230H${frameX+frameW-14}M${frameX+14} 400H${frameX+frameW-14}" class="ps-floor"/>`,
        text(frameX-14,135,'COAL STREAM','ps-zone-label','end'),
        text(frameX-14,310,'SHED & DRIVE HOUSES','ps-zone-label','end'),
        text(frameX-14,475,'DUST & RUNOFF','ps-zone-label','end')
      );
      const streamNodes=parts.filter(n=>['conveyor','stacker','pile','reclaimer'].includes(n.kind)).sort((a,b)=>{
        const sa= /^EAC-/i.test(a.label)?1:a.kind==='stacker'?2:a.kind==='pile'?3:a.kind==='reclaimer'?4:5;
        const sb= /^EAC-/i.test(b.label)?1:b.kind==='stacker'?2:b.kind==='pile'?3:b.kind==='reclaimer'?4:5;
        return sa-sb||a.label.localeCompare(b.label);
      });
      streamNodes.forEach((n,i)=>place(n,190+i*168,95,148,74));
      const bldgs=parts.filter(n=>!streamNodes.includes(n)&&['shed','building'].includes(n.kind));
      bldgs.forEach((n,i)=>place(n,220+i*220,260,165,76));
      const utils=parts.filter(n=>!streamNodes.includes(n)&&!bldgs.includes(n));
      utils.forEach((n,i)=>place(n,220+i*220,430,165,74));
      const cleanEdges=s.edges.filter(a=>a.context?.network==='material'&&positions.has(a.canonical_subject)&&positions.has(a.canonical_object)&&Math.abs(positions.get(a.canonical_subject).y-positions.get(a.canonical_object).y)<30);
      s.height=640;s.initialHeight=640;
      return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+nodes.map(({n,x,y,w,height})=>hotspot(n,x,y,w,height)).join('');
    }

    if(s.kind==='drive'){
      const order=n=>/low.speed/i.test(n.label)?3:({motor:0,coupling:1,gearbox:2,pulley:4,bearing:4,'crusher-rotor':4,brake:5}[n.kind]??6);
      const sorted=[...parts,...outside.filter(n=>['pulley','bearing','crusher-rotor'].includes(n.kind))].sort((a,b)=>order(a)-order(b));
      const mainChain=sorted.filter(n=>n.kind!=='brake');
      const brakes=sorted.filter(n=>n.kind==='brake');
      const frameX=110,frameW=980,cols=Math.min(mainChain.length,5),spacing=Math.min(185,Math.floor((frameW-40)/Math.max(1,cols))),boxW=146;
      decor.push(
        `<rect x="${frameX}" y="65" width="${frameW}" height="${brakes.length?375:215}" rx="10" class="ps-building-frame"/>`,
        text(frameX+22,90,s.title.toUpperCase()+' · MECHANICAL SHAFT TRANSMISSION','ps-zone-label','start')
      );
      mainChain.forEach((n,i)=>{
        const r=Math.floor(i/cols),c=i%cols,rowCount=Math.min(cols,mainChain.length-r*cols);
        const startX=frameX+frameW/2-(rowCount*spacing)/2+(spacing-boxW)/2;
        place(n,startX+c*spacing,115+r*165,boxW,74);
      });
      if(brakes.length){
        const cplNode=mainChain.find(n=>n.kind==='coupling')||mainChain[1]||mainChain[0];
        const anchorX=cplNode&&positions.has(cplNode.id)?positions.get(cplNode.id).x:frameX+frameW/2-boxW/2;
        decor.push(`<path d="M${frameX+14} 265H${frameX+frameW-14}" class="ps-floor"/>`);
        brakes.forEach((n,i)=>place(n,anchorX+i*185,290,boxW,74));
      }
      const partIds=new Set(sorted.map(n=>n.id));
      const cleanEdges=filterCleanInternalEdges(s.edges,positions,partIds).filter(a=>{
        const u=positions.get(a.canonical_subject),v=positions.get(a.canonical_object);
        return u&&v&&Math.abs(u.y-v.y)<=185&&Math.abs(u.x-v.x)<=spacing*1.3;
      });
      s.height=480;s.initialHeight=480;
      return decor.join('')+edgeMarkup(cleanEdges,positions,routes)+nodes.map(({n,x,y,w,height})=>hotspot(n,x,y,w,height)).join('');
    }

    if(parts.length){
      const custom=structuredEquipmentScene();
      if(custom)return custom;
    }

    if(s.kind==='pile'||s.kind==='shed'){
      const frameX=95,frameTop=44,frameW=1210;
      const machAndShed=outside.filter(n=>['stacker','reclaimer','shed','pile','assembly'].includes(n.kind));
      const waterAndRisers=outside.filter(n=>!machAndShed.includes(n));
      decor.push(
        `<rect x="${frameX}" y="${frameTop}" width="${frameW}" height="215" rx="12" class="ps-building-frame"/>`,
        text(frameX+22,frameTop+22,`${s.title.toUpperCase()} · ${s.kind==='pile'?'710×52×16 M TRAPEZOIDAL COAL STOCKPILE':'COVERED STOCKPILE STORAGE SHED'} & CONNECTED YARD SYSTEMS`,'ps-zone-label','start')
      );
      if(self)place(self,145,frameTop+52,220,90);
      machAndShed.forEach((n,i)=>place(n,435+i*205,frameTop+60,172,72));
      let curY=frameTop+240;
      if(waterAndRisers.length){
        const cols=waterAndRisers.length>8?6:4;
        const step=Math.floor((frameW-40)/cols),bw=cols===6?158:185;
        const dockH=Math.ceil(waterAndRisers.length/cols)*154+48;
        decor.push(
          `<rect x="${frameX}" y="${curY}" width="${frameW}" height="${dockH}" rx="10" class="ps-belt-dock"/>`,
          text(frameX+22,curY+22,`PERIMETER DUST SUPPRESSION (SPDS) & SPRINKLER RISERS (${waterAndRisers.length} INTERFACES)`,'ps-zone-label','start')
        );
        waterAndRisers.forEach((n,i)=>{
          const r=Math.floor(i/cols),c=i%cols;
          place(n,frameX+28+c*step,curY+38+r*154,bw,66);
        });
        curY+=dockH+20;
      }
      s.width=1400;s.height=Math.max(620,curY+20);s.initialHeight=Math.min(s.height,880);
      return decor.join('')+nodes.map(({n,x,y,w,height})=>hotspot(n,x,y,w,height,{max:21})).join('');
    }
    if(self)place(self,465,55,270,110);
    outside.forEach((n,i)=>place(n,65+(i%5)*225,280+Math.floor(i/5)*165,160,78));
    s.height=Math.max(520,320+Math.ceil(outside.length/5)*165);s.initialHeight=520;
    return decor.join('')+nodes.map(({n,x,y,w,height})=>hotspot(n,x,y,w,height)).join('');
  }
  function transferSelection(){
    const columns=getTransferColumns(),index=Math.max(0,Math.min(columns.length-1,Number(q().get('transferstream'))||0)),column=columns[index];
    return {columns,index,column,outlet:column?.outlets.includes(q().get('transferoutlet'))?q().get('transferoutlet'):column?.outlets[0]};
  }
  function transferRouteGuide(){
    const fixed=M.fixedTripperColumns(p,s.id);
    if(fixed.length&&q().get('scene')!=='connections')return `<div class="ps-crusher-guide"><nav aria-label="Fixed-tripper branch">${[['through','Same-belt continuation'],['yard','Yard diversion']].map(([key,name])=>`<a href="${safe(url({fixedmode:key,pick:null,edge:null}))}" ${(q().get('fixedmode')||'through')===key?'aria-current="true"':''}>${name}</a>`).join('')}</nav><small>Fixed trippers divert coal to the yard or pass it onward on the same continuous belt. The two views of each belt show its entry and continuation, not a return loop. Illustrative selection; partial splitting remains a documented alternative.</small>${fixed.map(c=>`<p>${safe(p.entities.get(c.inlet).label)} → ${safe(p.entities.get(c.tripper).label)} → ${safe(p.entities.get(c.gate).label)}${c.edges.filter(a=>a.canonical_subject===c.gate).map(a=>`<br>${safe(p.entities.get(a.canonical_object).label)}: ${safe(a.context?.condition||'Source-drawn branch')} ${source(a,'Route source ↗')}`).join('')}</p>`).join('')}</div>`;
    if(s.kind!=='transfer'||!getTransferColumns().length||q().get('scene')==='connections')return '';
    const v=transferSelection(),group=(title,items,key,sel)=>`<div><span>${title}</span><nav aria-label="${title}">${items.map(([id,name])=>`<a href="${safe(url({[key]:id,pick:null,edge:null}))}" ${String(id)===String(sel)?'aria-current="true"':''}>${safe(name)}</a>`).join('')}</nav></div>`;
    const selected=M.transferRoute(p,v.column,v.outlet).filter(a=>v.column?.gates.includes(a.canonical_subject));
    const locations=(p.outgoing.get(s.id)||[]).filter(a=>a.predicate==='location_description'&&typeof a.value==='string');
    return `<div class="ps-crusher-guide">${group('Follow incoming conveyor',v.columns.map((c,i)=>[i,c.inlets.map(id=>p.entities.get(id).label).join(' / ')]),'transferstream',v.index)}${group('Selected receiving conveyor',(v.column?.outlets||[]).map(id=>[id,p.entities.get(id).label]),'transferoutlet',v.outlet)}<small>${safe([...new Set(selected.map(a=>a.context?.condition||'').filter(Boolean))].join(' · '))} · illustrative selection, no live status</small>${locations.map(a=>`<p class="ps-transfer-location">${safe(a.value)} ${source(a,'Location source ↗')}</p>`).join('')}</div>`;
  }
  function transferHouseScene(){
    const v=transferSelection(),positions=new Map(),drawn=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const narrow=window.matchMedia('(max-width:760px)').matches;
    const put=(id,x,y,w=160,h=90,title)=>{const n=byId.get(id);if(n&&!drawn.has(id)){positions.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});}};
    const colCount=Math.max(2,v.columns.length);
    const colStep=colCount>2?Math.min(260,Math.floor(720/colCount)):345;
    const frameX=235,frameW=Math.max(660,colCount*colStep+40);
    const hasSecondGateTier=v.columns.some(c=>c.gates.some(id=>id!==c.gate));
    const colLocated=v.columns.map(c=>{
      const loc=s.nodes.filter(n=>n.role==='located'&&!c.gates.includes(n.id)&&M.closestParents(p,n.id).some(id=>c.inlets.includes(id)));
      return {drive:loc.find(n=>n.kind==='drive'),chutes:loc.filter(n=>n.kind==='chute')};
    });
    const hasHeadGear=!narrow&&colLocated.some(x=>x.drive||x.chutes.length);
    const headY=195;
    const gate1Y=hasHeadGear?345:235;
    const gate2Y=gate1Y+160;
    const outY=hasSecondGateTier?gate2Y+160:gate1Y+170;
    const frameH=outY-180+145;
    const decks=[
      {key:'inlet',elev:'TOP DECK',title:'INCOMING CONVEYORS',y:45,h:122,yMin:20,yMax:180},
      ...(hasHeadGear?[{key:'head',elev:'HEAD DECK',title:'DRIVES & DISCHARGE CHUTES',y:headY-12,h:125,yMin:181,yMax:headY+120}]:[]),
      {key:'divert',elev:'CHUTE DECK',title:'DIVERTER GATES / CHUTES',y:gate1Y-15,h:125,yMin:gate1Y-25,yMax:gate1Y+125},
      ...(hasSecondGateTier?[{key:'select',elev:'LOWER DECK',title:'SELECTOR GATES / CHUTES',y:gate2Y-15,h:125,yMin:gate2Y-25,yMax:gate2Y+125}]:[]),
      {key:'receive',elev:'BASE DECK',title:'RECEIVING CONVEYORS',y:outY-18,h:125,yMin:outY-30,yMax:outY+130}
    ];
    const wellXs=v.columns.map((_,i)=>frameX+120+i*colStep);
    const laneParts=new Set(),decor=[];
    if(!narrow&&isIsoStack()){
      decor.push(isoDeckSVG(decks,frameX,frameW,wellXs),text(frameX+frameW/2,24,'INCOMING CONVEYORS · 2.5D TRANSFER TOWER STACK','ps-zone-label'));
    }else{
      if(!narrow)isoDeckSVG(decks,frameX,frameW,wellXs);
      decor.push(`<rect x="${frameX}" y="180" width="${frameW}" height="${frameH}" rx="8" class="ps-building-frame"/>`,text(frameX+frameW/2,24,'INCOMING CONVEYORS · OPEN TO EXPLORE THEIR PARTS','ps-zone-label'));
    }
    v.columns.forEach((c,i)=>{
      const {drive,chutes}=colLocated[i];
      c.gates.forEach(id=>laneParts.add(id));if(drive)laneParts.add(drive.id);chutes.forEach(n=>laneParts.add(n.id));
      if(narrow&&i!==v.index)return;
      const x=narrow?50:(frameX+28+i*colStep);
      c.inlets.forEach((id,j)=>put(id,x+50+j*175,56,Math.min(180,colStep-45),80));
      if(narrow){
        put(c.gate,x+15,gate1Y,135,76);
        c.gates.filter(id=>id!==c.gate).forEach((id,j)=>put(id,x+15+j*145,gate2Y,135,76));
        if(drive)put(drive.id,325,65,125,68,'Head drive · '+c.inlets.map(id=>p.entities.get(id).label).join(' / '));
        chutes.forEach((n,j)=>put(n.id,x+155+j*140,gate1Y,125,65,'Discharge chute · '+c.inlets.map(id=>p.entities.get(id).label).join(' / ')));
      }else{
        if(drive)put(drive.id,x,headY,132,68,'Head drive · '+c.inlets.map(id=>p.entities.get(id).label).join(' / '));
        chutes.forEach((n,j)=>put(n.id,x+162+j*148,headY,132,65,'Discharge chute · '+c.inlets.map(id=>p.entities.get(id).label).join(' / ')));
        put(c.gate,x+70,gate1Y,145,76);
        c.gates.filter(id=>id!==c.gate).forEach((id,j)=>put(id,x+70+j*155,gate2Y,145,76));
      }
    });
    const outlets=narrow?[v.outlet]:[...new Set(v.columns.flatMap(c=>c.outlets))];
    const outStep=outlets.length>2?Math.floor((frameW-60)/outlets.length):345;
    outlets.forEach((id,i)=>put(id,narrow?50:(frameX+55+i*outStep),outY,Math.min(180,outStep-25),80));
    if(narrow||!isIsoStack())decor.push(`<path d="M${frameX+18} ${gate1Y-15}H${frameX+frameW-18}M${frameX+18} ${outY-20}H${frameX+frameW-18}" class="ps-floor"/>`,text(frameX-18,gate1Y+42,'DIVERT','ps-zone-label','end'),text(frameX-18,outY+42,'RECEIVE','ps-zone-label','end'));
    const services=s.nodes.filter(n=>n.role==='part'&&!drawn.has(n.id));
    const svcX=narrow?325:(frameX+frameW+40);
    services.forEach((n,i)=>{
      const applications=p.assembly(n.id).filter(e=>(p.classes.get(e.id)||[]).includes('spray_application_point')).length;
      const title=applications?`DFDS · ${applications} application points`:/Sump Pumps/.test(n.label)?'Drainage · '+short(n):/Service and drinking/.test(n.label)?'Service & drinking water':short(n);
      put(n.id,svcX,(narrow?255:70)+i*187,175,90,title);
    });
    const active=M.transferRoute(p,v.column,v.outlet),keys=new Set(active.map(a=>a.canonical_subject+'>'+a.canonical_object));
    const relevant=[...new Set(v.columns.flatMap(c=>c.outlets.flatMap(outlet=>M.transferRoute(p,c,outlet))))].filter(a=>positions.has(a.canonical_subject)&&positions.has(a.canonical_object));
    const routes=new Map();
    if(!narrow){
      v.columns.forEach(c=>{
        const pg=positions.get(c.gate);
        c.inlets.forEach(inf=>{
          const pi=positions.get(inf);
          if(pi&&pg)routes.set(inf+'>'+c.gate,chuteStep(Math.round(pi.x+pi.w/2),pi.y+pi.h+32,Math.round(pg.x+pg.w/2),pg.y-6));
        });
      });
    }
    const other=s.nodes.filter(n=>!drawn.has(n.id)&&(n.role==='connected'||n.role==='located'&&!laneParts.has(n.id)));
    const bottom=Math.max(outY+165,(narrow?280:95)+services.length*187);
    other.forEach((n,i)=>put(n.id,65+i%(narrow?2:5)*230,bottom+60+Math.floor(i/(narrow?2:5))*205,165,95));
    if(other.length)decor.push(text(600,bottom+25,'OTHER LOCATED EQUIPMENT & CONNECTIONS','ps-zone-label'));
    s.width=narrow?550:Math.max(1220,svcX+210);s.height=bottom+120+Math.ceil(other.length/(narrow?2:5))*205;s.initialHeight=Math.min(s.height,920);
    if(narrow){decor.length=0;decor.push(`<rect x="25" y="180" width="225" height="620" rx="8" class="ps-building-frame"/>`,text(140,24,'SELECTED TRANSFER ROUTE','ps-zone-label'),`<path d="M40 410H235M40 640H235" class="ps-floor"/>`,text(275,bottom+25,'OTHER LOCATED EQUIPMENT & CONNECTIONS','ps-zone-label'));}
    const activeInlets=new Set(v.column?.inlets||[]);
    const activeLocIds=new Set(colLocated[v.index]?[colLocated[v.index].drive?.id,...colLocated[v.index].chutes.map(x=>x.id)].filter(Boolean):[]);
    s._routeStreamNodes=new Set([...relevant.flatMap(a=>[a.canonical_subject,a.canonical_object]),...laneParts]);
    s._activeRouteNodes=new Set([...active.flatMap(a=>[a.canonical_subject,a.canonical_object]),...activeInlets,...activeLocIds]);
    const xEdges=xrayExtraEdges(positions,relevant);
    return decor.join('')+`<g class="ps-route-inactive">${edgeMarkup(relevant.filter(a=>!keys.has(a.canonical_subject+'>'+a.canonical_object)),positions,routes,null,relevant)}</g><g class="ps-route-active">${edgeMarkup(active,positions,routes,null,relevant)}</g>`+edgeMarkup(xEdges,positions,routes,null,relevant)+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title,max:n.w<=136?16:26})).join('');
  }
  function fixedTripperScene(){
    const columns=M.fixedTripperColumns(p,s.id),positions=new Map(),drawn=new Map(),byId=new Map(s.nodes.map(n=>[n.id,n]));
    const narrow=window.matchMedia('(max-width:760px)').matches,lanes=new Set(columns.flatMap(c=>[c.inlet,c.tripper,c.gate,...c.outlets]));
    const put=(id,x,y,w=165,h=90,title)=>{const n=byId.get(id);if(n){positions.set(id,{x,y,w,h});drawn.set(id,{n,x,y,w,h,title});}};
    const routes=new Map(),continuations=[],decor=[];
    if(!narrow){
      const decks=[
        {key:'inlet',elev:'TOP DECK',title:'CONTINUOUS BELT ENTRY',y:42,h:138,yMin:20,yMax:190},
        {key:'tripper',elev:'TRIPPER DECK',title:'FIXED TRIPPERS',y:198,h:138,yMin:191,yMax:345},
        {key:'gate',elev:'GATE DECK',title:'FLOW DIVIDERS',y:352,h:142,yMin:346,yMax:505},
        {key:'outlet',elev:'BASE DECK',title:'CONTINUATION & YARD',y:518,h:158,yMin:506,yMax:700}
      ];
      if(isIsoStack()){
        decor.push(isoDeckSVG(decks,155,970,[250,740]));
      }else{
        isoDeckSVG(decks,155,970,[250,740]);
        decor.push(`<rect x="155" y="15" width="970" height="700" rx="10" class="ps-building-frame"/>`);
      }
    }
    columns.forEach((c,i)=>{
      const x=narrow?50:180+i*480,top=narrow?i*700:0;
      put(c.inlet,x,top+55,180,90);put(c.tripper,x,top+210);put(c.gate,x,top+365);
      continuations.push(hotspot(byId.get(c.inlet),x,top+535,180,90,{label:p.entities.get(c.inlet).label+' continues'}));
      decor.push(text(x+90,top+18,'SAME CONTINUOUS BELT','ps-zone-label'),text(x+90,top+685,'ONWARD TO NEXT TRANSFER','ps-caption'));
      c.outlets.filter(id=>id!==c.inlet&&byId.has(id)).forEach((id,j)=>{put(id,x+225,top+530+j*140,180,90);continuations.push(hotspot(byId.get(id),x+225,top+530+j*140,180,90));drawn.delete(id);});
      c.edges.forEach(a=>{
        const f=positions.get(a.canonical_subject),t=a.canonical_object===c.inlet?{x,y:top+535,w:180}:positions.get(a.canonical_object);
        if(f&&t)routes.set(a.canonical_subject+'>'+a.canonical_object,`M${f.x+f.w/2} ${f.y+f.h}L${t.x+t.w/2} ${t.y}`);
      });
    });
    const base=narrow?columns.length*700:740,other=s.nodes.filter(n=>n.role!=='self'&&!lanes.has(n.id));
    other.forEach((n,i)=>put(n.id,50+i%(narrow?2:5)*225,base+85+Math.floor(i/(narrow?2:5))*185));
    decor.push(text(narrow?275:600,base+35,'LOCAL ASSEMBLIES & SHARED SERVICES','ps-zone-label'));
    s.width=narrow?550:1200;s.height=base+170+Math.ceil(other.length/(narrow?2:5))*185;s.initialHeight=narrow?740:900;
    const selected=[],inactive=[],yard=q().get('fixedmode')==='yard';
    columns.forEach(c=>c.edges.forEach(a=>(a.canonical_subject!==c.gate||(a.canonical_object!==c.inlet)===yard?selected:inactive).push(a)));
    return decor.join('')+`<g class="ps-route-inactive">${edgeMarkup(inactive,positions,routes)}</g><g class="ps-route-active">${edgeMarkup(selected,positions,routes)}</g>`+[...drawn.values()].map(n=>hotspot(n.n,n.x,n.y,n.w,n.h,{label:n.title})).join('')+continuations.join('');
  }
  function connectionsScene(){
    const positions=new Map(),self=s.nodes.find(n=>n.id===s.id),edges=s.edges,layer=q().get('layer')||'all';
    const visible=edges.filter(a=>layer==='all'||a.context.network===layer),ids=new Set(visible.flatMap(a=>[a.canonical_subject,a.canonical_object]));
    const ins=s.nodes.filter(n=>n.id!==s.id&&visible.some(a=>a.canonical_subject===n.id&&a.canonical_object===s.id));
    const outs=s.nodes.filter(n=>n.id!==s.id&&!ins.includes(n)&&visible.some(a=>a.canonical_subject===s.id&&a.canonical_object===n.id));
    const others=s.nodes.filter(n=>n.id!==s.id&&!ins.includes(n)&&!outs.includes(n)&&ids.has(n.id));
    const rows=Math.max(ins.length,outs.length,1),base=Math.max(460,rows*170+75);
    if(self)positions.set(self.id,{x:475,y:Math.min(base/2,300)-40,w:250,h:165});
    ins.forEach((n,i)=>positions.set(n.id,{x:75,y:70+i*170,w:175,h:105}));
    outs.forEach((n,i)=>positions.set(n.id,{x:950,y:70+i*170,w:175,h:105}));
    others.forEach((n,i)=>positions.set(n.id,{x:65+(i%5)*230,y:base+100+Math.floor(i/5)*210,w:170,h:108}));
    s.height=Math.max(720,base+Math.ceil(others.length/5)*210+130);s.initialHeight=Math.min(s.height,950);
    return text(165,35,'SUPPLYING / UPSTREAM','ps-zone-label')+text(1040,35,'RECEIVING / DOWNSTREAM','ps-zone-label')+edgeMarkup(visible,positions)+s.nodes.filter(n=>positions.has(n.id)).map(n=>{const a=positions.get(n.id);return hotspot(n,a.x,a.y,a.w,a.h);}).join('')+(!visible.length?text(600,550,'No documented directed connections in this layer.','ps-caption'):'');
  }
  function contextRail(){
    if(!s.id)return '';
    const inside=new Set(['silo-house','crusher-house'].includes(s.kind)?p.assembly(s.id).map(n=>n.id):[s.id]);
    const edges=p.material.filter(a=>inside.has(a.canonical_subject)!==inside.has(a.canonical_object)),other=[...new Set(edges.map(a=>inside.has(a.canonical_subject)?a.canonical_object:a.canonical_subject))];
    return `<div class="ps-route-context"><span>In the plant</span>${other.slice(0,8).map(id=>{const incoming=edges.some(a=>a.canonical_subject===id&&inside.has(a.canonical_object));return `<a href="${safe(openURL(id))}">${incoming?'← from':'to →'} <strong>${safe(p.entities.get(id)?.label)}</strong></a>`;}).join('')}<a class="ps-context-more" href="${safe(url({scene:q().get('scene')==='connections'?null:'connections',pick:null,edge:null}))}">${q().get('scene')==='connections'?'↶ Back to assembly':'View connections ↗'}</a></div>`;
  }
  function structuredAreaScene(){
    const positions=new Map(),routes=new Map(),drawn=new Map(),decor=[];
    const members=new Map(s.nodes.map(n=>[n.id,n]));
    const byLabel=new Map(s.nodes.map(n=>[n.label.toUpperCase().trim(),n]));
    const put=(n,x,y,w=150,h=76,title)=>{if(!n||drawn.has(n.id))return;positions.set(n.id,{x,y,w,h});drawn.set(n.id,{n,x,y,w,h,title});};
    const putLabel=(lbl,x,y,w=150,h=76,title)=>{const n=byLabel.get(lbl.toUpperCase());if(n)put(n,x,y,w,h,title);};

    const chuteOwner=new Map();

    if(s.area==='distribution'){
      const frameX=190,frameY=55,frameW=735,frameH=1660;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UEF-3 → UEF-7 · TWIN-STREAM STACKING & SILO-FEED CORRIDOR','ps-zone-label','start'),
        text(555,28,'FROM PRIMARY SCREENHOUSE (EAC-3A / EAC-3B)','ps-zone-label'),
        text(1055,75,'TRANSFER HOUSES & ANALYSERS','ps-zone-label'));
      const bands=[
        [95,'UEF-3 · DIVIDERS',[['KB-FD-1',285],['KB-FD-2',615]]],
        [255,'UEF-3 · SELECTORS',[['FG-1',285],['FG-2',615]]],
        [415,'CONVEYORS 4A / 4B',[['EAC-4A',285],['EAC-4B',615]]],
        [575,'UEF-4 · TRIPPERS',[['FTR-1',210],['KB-FD-3',385],['FTR-2',570],['KB-FD-4',745]]],
        [735,'UEF-5 · DIVIDERS',[['KB-FD-5',285],['KB-FD-6',615]]],
        [895,'UEF-5 · SELECTORS',[['FG-3',285],['FG-4',615]]],
        [1055,'CONVEYORS 5A / 5B',[['EAC-5A',285],['EAC-5B',615]]],
        [1215,'UEF-6 · TRIPPERS',[['FTR-3',210],['KB-FD-7',385],['FTR-4',570],['KB-FD-8',745]]],
        [1375,'UEF-7 · SELECTORS',[['FG-5',285],['FG-6',615]]],
        [1535,'SILO-FEED BELTS',[['EBA-6A',285],['EBA-6B',615]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-18}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        const w=items.length>2?132:165;
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,w,74));
      });
      ['UEF-3','UEF-4','UEF-5','UEF-6','UEF-7','CV-1','CV-2'].forEach((lbl,i)=>putLabel(lbl,965,95+i*158,160,74));
      s.width=1200;s.height=1760;s.initialHeight=980;
    }else if(s.area==='reclaim'){
      const frameX=190,frameY=65,frameW=735,frameH=675;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UEF-8 TO UEF-12 · RECLAIM COLLECTION & SILO-FEED CORRIDOR','ps-zone-label','start'),
        text(555,34,'FROM STOCKYARD RECLAIM CONVEYORS (EBA-8 / 10 / 12 / 14)','ps-zone-label'),
        text(1070,85,'TRANSFER HOUSES & WEIGHERS','ps-zone-label'));
      const bands=[
        [110,'YARD RECLAIM GATES',[['FG-7',210],['FG-8',385],['FG-9',560],['FG-10',735]]],
        [275,'COLLECTOR BELTS',[['EBA-15A',290],['EBA-15B',610]]],
        [440,'UEF-12 · SELECTORS',[['FG-11',290],['FG-12',610]]],
        [605,'SILO-FEED BELTS',[['EBA-16A',290],['EBA-16B',610]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-20}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        const w=items.length>2?135:170;
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,w,74));
      });
      ['UEF-8','UEF-9','UEF-10','UEF-11','UEF-12','AT-3','AT-4','CV-3','CV-4'].forEach((lbl,i)=>{
        putLabel(lbl,955+(i%2)*148,105+Math.floor(i/2)*152,130,72);
      });
      s.width=1250;s.height=820;s.initialHeight=820;
    }else if(s.area==='unloading'){
      const frameX=190,frameY=65,frameW=735,frameH=675;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'COAL JETTY · UNLOADING & WEIGHING CORRIDOR','ps-zone-label','start'),
        text(1070,85,'FACILITIES & DETECTORS','ps-zone-label'));
      const bands=[
        [110,'SHIP UNLOADERS',[['Coal Ship Unloader-1',220],['Coal Ship Unloader-2',470],['Coal Ship Unloader-3',720]]],
        [275,'JETTY CONVEYORS',[['EAC-1A',290],['EAC-1B',610]]],
        [440,'TRANSFER HOUSE',[['UEF-1',450]]],
        [605,'PLANT APPROACH',[['EAC-2A',290],['EAC-2B',610]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-20}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,165,74));
      });
      ['Coal Jetty','AT-1','AT-2','EAT-1','EAT-2','QB-1','QB-2'].forEach((lbl,i)=>{
        putLabel(lbl,955+(i%2)*148,105+Math.floor(i/2)*152,130,72);
      });
      s.width=1250;s.height=820;s.initialHeight=820;
    }else if(s.area==='screening'){
      const frameX=190,frameY=65,frameW=735,frameH=675;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UEE-1 · PRIMARY SCREENHOUSE','ps-zone-label','start'),
        text(1055,85,'HOUSE & SAMPLING','ps-zone-label'));
      const bands=[
        [110,'ROD GATES',[['KB-RG-1',210],['KB-RG-2',385],['KB-RG-3',560],['KB-RG-4',735]]],
        [275,'BYPASS GATES',[['KB-RPG-1',210],['KB-RPG-2',385],['KB-RPG-3',560],['KB-RPG-4',735]]],
        [440,'PRIMARY SCREENS',[['EBD-1',210],['EBD-2',385],['EBD-3',560],['EBD-4',735]]],
        [605,'ONWARD CONVEYORS',[['EAC-3A',290],['EAC-3B',610]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-20}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+42,title,'ps-zone-label','end'));
        const w=items.length>2?135:170;
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,w,74));
      });
      ['UEE-1','UEE-1 Oversize Reject Bins','EAU-1','UEF-3 Coal Sampling System'].forEach((lbl,i)=>putLabel(lbl,960,105+i*155,165,76));
      s.width=1220;s.height=820;s.initialHeight=820;
    }else if(s.area==='stockyard'){
      const gateways=s.nodes.filter(n=>n.kind==='yard');
      const bodyGateways=gateways.map((n,i)=>`<a class="ps-area-gateway" href="${safe(openURL(n.id))}"><g transform="translate(${45+i*240} 15)"><rect class="ps-halo" x="-5" y="0" width="215" height="175" rx="18"/>${symbol('yard',15,0,165,110)}${text(100,132,n.label,'ps-stage-title')}${text(100,155,'Open yard assembly →','ps-node-hint')}</g></a>`).join('');
      const frameX=150,frameY=225,frameW=1035,frameH=670;
      decor.push(bodyGateways,`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'COAL STOCKYARDS 1–4 · STACKING → STORAGE → RECLAIMING LANES','ps-zone-label','start'));
      for(let yIdx=0;yIdx<4;yIdx++){
        const n=yIdx+1,rowY=268+yIdx*156;
        if(yIdx>0)decor.push(`<path d="M${frameX+14} ${rowY-16}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,rowY+42,`YARD ${n}`,'ps-zone-label','end'));
        const rowItems=[[f=>`EAC-${5+2*f}`,175],[f=>`EAD-${f}`,380],[f=>`EAE-${f}`,585],[f=>`EAF-${f}`,790],[f=>`EBA-${6+2*f}`,995]];
        rowItems.forEach(([fn,x])=>putLabel(fn(n),x,rowY,150,74));
      }
      s.width=1220;s.height=940;s.initialHeight=940;
    }else if(s.area==='bunkers'){
      const frameX=155,frameY=55,frameW=1025,frameH=795;
      decor.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" rx="10" class="ps-building-frame"/>`,
        text(frameX+20,frameY+24,'UNIT-1 & UNIT-2 BOILER COAL BUNKER BAYS (TT-1–4 · BUNKERS A–F)','ps-zone-label','start'),
        `<path d="M668 ${frameY+40}V${frameY+frameH-15}" class="ps-floor"/>`);
      const bands=[
        [95,'TRIPPERS',[['TT-1',215],['TT-3',435],['TT-2',720],['TT-4',940]]],
        [255,'GATES',[['FG-19',215],['FG-21',435],['FG-20',720],['FG-22',940]]],
        [415,'BUNKER BAYS',[['Unit-1 Coal Bunker Bay',325],['Unit-2 Coal Bunker Bay',830]]]
      ];
      bands.forEach(([y,title,items],idx)=>{
        if(idx>0)decor.push(`<path d="M${frameX+14} ${y-18}H${frameX+frameW-14}" class="ps-floor"/>`);
        decor.push(text(frameX-14,y+40,title,'ps-zone-label','end'));
        items.forEach(([lbl,x])=>putLabel(lbl,x,y,160,74));
      });
      decor.push(`<path d="M${frameX+14} 555H${frameX+frameW-14}" class="ps-floor"/>`,text(frameX-14,620,'MILL BUNKERS','ps-zone-label','end'));
      ['A','B','C','D','E','F'].forEach((let_,i)=>{
        const r=Math.floor(i/3),c=i%3;
        putLabel(`Bunker-${let_} of Unit-1`,185+c*158,572+r*145,134,70);
        putLabel(`Bunker-${let_} of Unit-2`,695+c*158,572+r*145,134,70);
      });
      s.width=1220;s.height=890;s.initialHeight=890;
    }else{
      return null;
    }

    const findDrawnAncestor=id=>{
      const seen=new Set([id]),queue=[id];
      while(queue.length){
        const cur=queue.shift();
        for(const pid of M.closestParents(p,cur)){
          if(pid===cur||seen.has(pid))continue;
          if(drawn.has(pid))return pid;
          seen.add(pid);queue.push(pid);
        }
      }
      return null;
    };
    for(const n of s.nodes){
      if(n.kind==='chute'||(p.classes.get(n.id)||[]).includes('chute_interface')){
        const locMain=(p.outgoing.get(n.id)||[]).filter(a=>a.predicate==='located_at'&&a.canonical_object).map(a=>a.canonical_object).find(lid=>drawn.has(lid)&&(positions.get(lid)?.x??9999)<930);
        const owner=locMain||findDrawnAncestor(n.id)||M.closestParents(p,n.id).find(pid=>members.has(pid)&&pid!==n.id);
        if(owner)chuteOwner.set(n.id,owner);
      }
    }
    for(const [cid,owner] of chuteOwner){
      if(!positions.has(cid)&&positions.has(owner))positions.set(cid,positions.get(owner));
    }

    const gatewaysSet=new Set(s.nodes.filter(n=>n.kind==='yard').map(n=>n.id));
    const extra=s.nodes.filter(n=>!drawn.has(n.id)&&!chuteOwner.has(n.id)&&!gatewaysSet.has(n.id)&&!findDrawnAncestor(n.id));
    if(extra.length){
      const base=s.height+30;
      decor.push(text(190,base-12,'ADDITIONAL AREA EQUIPMENT & SERVICES','ps-zone-label','start'));
      extra.forEach((n,i)=>put(n,190+(i%5)*198,base+8+Math.floor(i/5)*152,160,74));
      s.height=base+40+Math.ceil(extra.length/5)*152;
    }

    const continuationFrom=new Map();
    for(const [beltLbl,gateLbl] of [['EAC-4A','KB-FD-3'],['EAC-4B','KB-FD-4'],['EAC-5A','KB-FD-7'],['EAC-5B','KB-FD-8']]){
      const bNode=byLabel.get(beltLbl),gNode=byLabel.get(gateLbl);
      if(bNode&&gNode&&positions.has(gNode.id))continuationFrom.set(bNode.id,positions.get(gNode.id));
    }
    function pv_from(u,v){
      const pu=positions.get(u),pv=positions.get(v);
      if(pu&&pv&&pv.y-pu.y>200&&continuationFrom.has(u))return continuationFrom.get(u);
      return pu;
    }

    const candidateEdges=s.edges.filter(a=>{
      const u=a.canonical_subject,v=a.canonical_object;
      if(!positions.has(u)||!positions.has(v)||positions.get(u)===positions.get(v))return false;
      const pu=pv_from(u,v),pv=positions.get(v);
      if(s.area!=='stockyard'&&s.area!=='bunkers'&&(pu.x>=930||pv.x>=930))return false;
      if(pv.y<pu.y-10||pv.y-pu.y>360)return false;
      return true;
    });
    const oneBandAdj=new Map();
    for(const a of candidateEdges){
      const pu=pv_from(a.canonical_subject,a.canonical_object),pv=positions.get(a.canonical_object);
      if(pv.y-pu.y<=190){
        if(!oneBandAdj.has(pu))oneBandAdj.set(pu,new Set());
        oneBandAdj.get(pu).add(pv);
      }
    }
    const activeEdges=candidateEdges.filter(a=>{
      const pu=pv_from(a.canonical_subject,a.canonical_object),pv=positions.get(a.canonical_object);
      if(pv.y-pu.y<=190)return true;
      const mids=oneBandAdj.get(pu)||new Set();
      for(const mid of mids){
        if((oneBandAdj.get(mid)||new Set()).has(pv))return false;
      }
      return true;
    });

    return decor.join('')+edgeMarkup(activeEdges,positions,routes,pv_from)+[...drawn.values()].map(d=>hotspot(d.n,d.x,d.y,d.w,d.h,{label:d.title,max:d.w<=140?18:24})).join('');
  }
  function areaScene(){
    const structured=structuredAreaScene();
    if(structured)return structured;
    const graph=PlantExplorerModel.areaGraph(p,s.area),positions=new Map();
    const members=new Map(s.nodes.map(n=>[n.id,n]));
    const gateways=s.nodes.filter(n=>n.kind==='yard');
    const shift=gateways.length?240:0;
    let body=gateways.map((n,i)=>{return `<a class="ps-area-gateway" href="${safe(openURL(n.id))}"><g transform="translate(${60+i*280} 15)"><rect class="ps-halo" x="-10" y="0" width="250" height="205" rx="20"/>${symbol('yard',20,0,185,130)}${text(110,152,n.label,'ps-stage-title')}${text(110,178,'Open yard assembly →','ps-node-hint')}</g></a>`;}).join('');
    graph.nodes.forEach(n=>positions.set(n.id,{x:n.x*1.25+35,y:n.y*1.55+shift+30,w:150,h:100}));
    const routes=new Map();for(const edge of graph.edges){if(edge.bypassLane===undefined)continue;const a=positions.get(edge.from),b=positions.get(edge.to),y=shift+30+(8+edge.bypassLane*12)*1.55,offset=20+edge.bypassLane*3;routes.set(edge.from+'>'+edge.to,`M${a.x+a.w} ${a.y+50}H${a.x+a.w+offset}V${y}H${b.x-offset}V${b.y+50}H${b.x}`);}
    body+=edgeMarkup(s.edges,positions,routes)+graph.nodes.map(n=>{const a=positions.get(n.id);return hotspot(members.get(n.id)||{id:n.id,label:p.entities.get(n.id)?.label,kind:M.kind(p,n.id),role:'equipment'},a.x,a.y,a.w,a.h);}).join('');
    const shown=new Set([...graph.nodes.map(n=>n.id),...gateways.map(n=>n.id)]),extra=s.nodes.filter(n=>!shown.has(n.id));
    const base=graph.height*1.55+shift+90;
    if(extra.length)body+=text(40,base,'OTHER EQUIPMENT IN THIS AREA','ps-zone-label','start')+extra.map((n,i)=>hotspot(n,50+(i%5)*235,base+25+Math.floor(i/5)*200,160,100)).join('');
    s.width=Math.max(1200,graph.width*1.25+120,gateways.length*280+60);s.height=Math.max(720,base+(Math.ceil(extra.length/5))*200+50);return body;
  }

  /**
   * Adaptive Equipment Information Flow Inspector
   * Dynamically structures engineering specifications, component anatomy, and process/mechanical
   * connections to fit the selected equipment or part, with 1-click source review beside every value.
   */
  function inspector(){
    const id=h(),edge=p.facts.find(a=>a.id===q().get('edge'));
    if(edge){const fs=p.networks.filter(a=>a.canonical_subject===edge.canonical_subject&&a.canonical_object===edge.canonical_object&&a.context?.network===edge.context?.network);return `<aside class="ps-inspector" aria-label="Connection details"><a class="ps-close" href="${safe(url({edge:null,pick:null}))}" aria-label="Close details">×</a><div class="ps-eyebrow">DOCUMENTED CONNECTION</div><h2>${safe(p.entities.get(edge.canonical_subject)?.label)} → ${safe(p.entities.get(edge.canonical_object)?.label)}</h2><p>Each link retains its documented operating condition and source drawing crop.</p>${(fs.length?fs:[edge]).map(a=>api.fact(a)).join('')}</aside>`;}
    if(!id||!p.entities.has(id))return '';
    const flow=PlantExplorerModel.buildEquipmentFlow(p,id);
    if(!flow)return '';
    const e=flow.entity,own=p.outgoing.get(id)||[],parents=M.closestParents(p,id),count=id===s.id?s.nodes.filter(n=>n.role==='part').length:(p.children.get(id)||[]).filter(a=>!p.refs.has(a.canonical_subject)).length;
    const modes=M.modeFacts(own,q().get('opmode'));

    // 1. Operational Lead & Role Statements
    const primaryRole=flow.roleStatements[0];
    const extraRoles=flow.roleStatements.slice(1);
    const classPills=flow.entityClasses.map((c,i)=>{
      const cf=flow.classFacts[i]||flow.classFacts[0];
      return `<span class="ps-class-badge">${safe(nice(c))} ${cf?source(cf):''}</span>`;
    }).join('');

    // 2. Adaptive Headline Metrics Ribbon
    const metricsHtml=flow.headlineMetrics.length?`<div class="ps-flow-metrics">${flow.headlineMetrics.map(m=>`<div class="ps-flow-metric"><div class="ps-flow-metric-top"><span>${safe(m.label)}</span>${source(m.fact)}</div><strong>${safe(m.value)}</strong>${m.condition?`<small>${safe(m.condition)}</small>`:''}</div>`).join('')}</div>`:'';

    // 3. Dynamic, Equipment-Tailored Specification Sections
    const sectionsHtml=flow.sections.map((sec,idx)=>`<details class="ps-flow-section" ${idx<3?'open':''}><summary><span class="ps-flow-sec-title"><i>${sec.icon}</i> ${safe(sec.title)}</span><span class="ps-flow-sec-count">${sec.rows.length}</span></summary><div class="ps-flow-table">${sec.rows.map(r=>`<div class="ps-flow-row"><div class="ps-flow-key">${safe(r.key)}${r.condition?`<small class="ps-flow-cond">${safe(r.condition)}</small>`:''}</div><div class="ps-flow-val"><strong>${safe(r.value)}${r.unit?' '+safe(r.unit):''}</strong>${source(r.fact)}</div></div>`).join('')}</div></details>`).join('');

    // 4. Sub-Assembly & Component Anatomy Cards
    const childrenHtml=flow.childrenCards.length?`<details class="ps-flow-section" open><summary><span class="ps-flow-sec-title"><i>🧩</i> Component & Sub-Assembly Anatomy</span><span class="ps-flow-sec-count">${flow.childrenCards.length}</span></summary><div class="ps-flow-parts">${flow.childrenCards.map(c=>`<div class="ps-flow-part-card"><div class="ps-flow-part-top"><a href="${safe(openURL(c.id))}" class="ps-flow-part-link">${safe(c.label)} →</a>${source(c.summaryFact||c.partEdge)}</div>${c.summary?`<p class="ps-flow-part-spec">${safe(c.summary)}</p>`:''}<div class="ps-flow-part-meta"><span>${safe(c.classes[0]||'component')}</span>${c.subCount?`<span>· ${c.subCount} sub-parts</span>`:''}</div></div>`).join('')}</div></details>`:'';

    // 5. Multi-Network Process & Mechanical Flow Wiring
    const wiringHtml=flow.wiringGroups.length?`<details class="ps-flow-section" open><summary><span class="ps-flow-sec-title"><i>⇄</i> Process, Mechanical & Control Wiring</span><span class="ps-flow-sec-count">${flow.wiringGroups.reduce((n,g)=>n+g.all.length,0)}</span></summary>${flow.wiringGroups.map(g=>`<div class="ps-flow-net-group"><div class="ps-flow-net-title">${safe(g.title)}</div>${g.all.map(a=>{const out=a.canonical_subject===id,otherId=out?a.canonical_object:a.canonical_subject;return `<div class="ps-flow-wire-row"><span class="ps-wire-dir ${out?'is-out':'is-in'}">${out?'TO →':'← FROM'}</span><div class="ps-wire-body"><a href="${safe(openURL(otherId))}">${safe(p.entities.get(otherId)?.label||otherId)}</a><small>${safe(nice(a.predicate))}${a.context?.condition?' · '+safe(a.context.condition):''}</small></div>${source(a)}</div>`;}).join('')}</div>`).join('')}</details>`:'';

    // 6. Operating Mode Reference (when mode-conditioned facts exist)
    const modeHtml=modes.modes.length?`<section class="ps-mode-reference"><div class="ps-inspector-label">OPERATING MODE REFERENCE</div><nav aria-label="Documented operating mode">${modes.modes.map(mode=>`<a href="${safe(url({opmode:mode}))}" ${mode===modes.selected?'aria-current="true"':''}>${safe(mode)}</a>`).join('')}</nav><p>Showing source conditions for this mode.</p>${modes.facts.map(a=>api.fact(a)).join('')}</section>`:'';

    // 7. Interactive Start Permissives, Trip Conditions & Interlocks Checklist
    const checklistHtml=flow.permissivesChecklist?.length?`<details class="ps-flow-section ps-checklist-section" open><summary><span class="ps-flow-sec-title"><i>✓</i> Start Permissives & Trip Interlocks</span><span class="ps-flow-sec-count">${flow.permissivesChecklist.length}</span></summary><div class="ps-checklist">${flow.permissivesChecklist.map(item=>`<label class="ps-check-row"><input type="checkbox"><span class="ps-check-badge is-${safe(item.kind)}">${safe(item.badge)}</span><span class="ps-check-body"><strong>${safe(item.text)}</strong>${item.condition?`<small>${safe(item.condition)}</small>`:''}</span>${source(item.fact)}</label>`).join('')}</div></details>`:'';

    // 8. Source Qualifications (with Severity Triage), Revision Notes & Applicable References
    const highQuals=flow.qualifications.filter(x=>x.severity==='high').length;
    const renderQual=x=>{const out=api.fact(x.fact,x.via,x.severity);return (x.severity&&!String(out).includes('ps-sev-badge'))?`<div class="ps-qual-item"><span class="ps-sev-badge is-${safe(x.severity)}">${safe(x.severity.toUpperCase())}</span>${out}</div>`:out;};
    const qualHtml=flow.qualifications.length?`<details class="ps-qualified" ${highQuals?'open':''}><summary>⚠ ${flow.qualifications.length} source qualification${flow.qualifications.length===1?'':'s'}${highQuals?` (${highQuals} HIGH)`:''}</summary>${flow.qualifications.map(renderQual).join('')}</details>`:'';
    const revHtml=flow.revisionRows.length?`<details class="ps-inspector-section"><summary>Drawing revision history <span>${flow.revisionRows.length}</span></summary><div class="ps-flow-table">${flow.revisionRows.map(r=>`<div class="ps-flow-row"><div class="ps-flow-key">${safe(r.key)}</div><div class="ps-flow-val"><span>${safe(r.value)}</span>${source(r.fact)}</div></div>`).join('')}</div></details>`:'';
    const appHtml=flow.applicableRefs.length?`<details class="ps-inspector-section"><summary>Applicable engineering schemes <span>${flow.applicableRefs.length}</span></summary>${flow.applicableRefs.map(x=>api.fact(x.fact,x.via)).join('')}</details>`:'';
    const quickActions=(!p.refs.has(id)&&e.category!=='document')?`<div class="ps-inspector-actions"><button type="button" class="ps-action-btn" data-action="plant-record" data-id="${safe(id)}">＋ Log issue / shift record</button><button type="button" class="ps-action-btn is-secondary" data-action="scene-trace" data-id="${safe(id)}">⇄ Trace connections</button></div>`:'';

    return `<aside class="ps-inspector" aria-label="Equipment details"><a class="ps-close" href="${safe(url({pick:null,edge:null}))}" aria-label="Close details">×</a><div class="ps-eyebrow">SELECTED ${safe(nice(M.kind(p,id)).toUpperCase())}</div><h2>${safe(e.label)}</h2>${flow.commonName?`<div class="ps-common-alias">${safe(flow.commonName)}</div>`:''}<div class="ps-class-row">${classPills}</div>${primaryRole?`<div class="ps-role-banner"><p>${safe(primaryRole.text)}</p>${source(primaryRole.fact)}</div>`:''}${extraRoles.map(r=>`<div class="ps-role-sub"><span>${safe(r.label)}:</span> ${safe(r.text)} ${source(r.fact)}</div>`).join('')}${id!==s.id?`<a class="ps-open" href="${safe(openURL(id))}">Open ${count?'schematic · '+count+' part'+(count===1?'':'s'):'equipment view'} <span>↗</span></a>`:''}${quickActions}${parents.length?`<div class="ps-context-line"><span>Part of</span>${parents.map(x=>{const pf=flow.parentEdges.find(a=>a.canonical_object===x);return `<a href="${safe(openURL(x))}">${safe(p.entities.get(x)?.label)}</a>${pf?' '+source(pf):''}`;}).join(' · ')}</div>`:''}${flow.locatedEdges.length?`<div class="ps-context-line"><span>Located at</span>${flow.locatedEdges.map(a=>`<a href="${safe(openURL(a.canonical_object))}">${safe(p.entities.get(a.canonical_object)?.label)}</a> ${source(a)}`).join(' · ')}</div>`:''}${metricsHtml}${qualHtml}${checklistHtml}${sectionsHtml}${childrenHtml}${wiringHtml}${modeHtml}${revHtml}${appHtml}<a class="ps-reference-link" href="${safe(url({equipment:id,view:'records',tab:'overview',pick:null,edge:null}))}">Open full equipment dossier & maintenance records →</a></aside>`;
  }
  function browse(){if(!q().has('browse'))return '';const ids=s.all||[...p.entities.keys()].filter(id=>!p.refs.has(id));return `<aside class="ps-browser" aria-label="Component navigator"><a class="ps-close" href="${safe(url({browse:null}))}" aria-label="Close component navigator">×</a><div class="ps-eyebrow">${s.id?'ASSEMBLY NAVIGATOR':'EQUIPMENT NAVIGATOR'}</div><h2>Find a part</h2><input type="search" id="ps-parts-search" aria-label="Filter components" placeholder="Tag or alias (e.g. TP-5, PSH, CRH, BCN-5A)…"><div id="ps-part-results">${ids.map(id=>{const cn=PlantExplorerModel.commonName(p,id);return `<a class="ps-part-row" href="${safe(pickURL(id))}" data-search="${safe([p.entities.get(id)?.label,...(p.entities.get(id)?.aliases||[]),...(p.searchAliases?.get(id)||[]),...(p.locationAliases?.get(id)||[]),...(p.classes.get(id)||[])].join(' ').toLowerCase())}"><span>${safe(p.entities.get(id)?.label)}</span><small>${safe(cn&&!cn.startsWith('at ')?cn+' · '+nice(M.kind(p,id)):nice(M.kind(p,id)))}</small></a>`;}).join('')}</div></aside>`;}
  function crumbs(){
    const candidates=(q().get('trail')||'').split(',').filter(id=>p.entities.has(id)),trail=[];let child=s.id;
    for(const id of candidates.reverse()){if(id===child||!p.assembly(id).some(n=>n.id===child)&&!(p.incoming.get(id)||[]).some(a=>a.predicate==='located_at'&&a.canonical_subject===child))break;trail.unshift(id);child=id;}
    const chain=trail.length?trail:s.id?M.breadcrumbs(p,s.id).slice(0,-1).filter(id=>!/Maitree Coal Handling Plant|Coal Stockpile Yard/.test(p.entities.get(id)?.label)):[];
    const area=p.stages.find(st=>st.id===q().get('area'))||p.stages.find(st=>p.memberships.get(s.id)?.has(st.id));
    return `<nav class="ps-crumbs" aria-label="Plant location"><a href="${home}">Plant</a>${area?`<span>›</span><a href="${areaURL(area.id)}">${safe(area.short)}</a>`:''}${chain.map((id,i)=>`<span>›</span><a href="${safe(url({equipment:id,trail:chain.slice(0,i).join(','),pick:null,edge:null,browse:null}))}">${safe(p.entities.get(id)?.label)}</a>`).join('')}${s.id?`<span>›</span><strong>${safe(s.title)}</strong>`:''}</nav>`;
  }
  function buildSmartToolbar(){
    const layer=q().get('layer')||'all';
    if(s.kind==='plant'){
      const curPath=q().get('path')||'';
      return `<div class="ps-toolbar"><div class="ps-path-pills" role="group" aria-label="Operating coal routes"><span class="ps-toolbar-label">Route</span><a class="ps-route-pill ${!curPath?'is-active':''}" href="${safe(url({path:null}))}" ${!curPath?'aria-current="true"':''}>Whole plant</a>${p.paths.map(path=>`<a class="ps-route-pill ${path.id===curPath?'is-active':''}" href="${safe(url({path:path.id}))}" ${path.id===curPath?'aria-current="true"':''}><strong>${safe(path.id)}</strong> ${safe(path.title.replace(/^Path\s*\d+\s*[:·-]\s*/i,''))}</a>`).join('')}<select id="ps-path" class="ps-sr-only" aria-label="Follow a route"><option value="">Whole plant</option>${p.paths.map(path=>`<option value="${safe(path.id)}" ${path.id===curPath?'selected':''}>${safe(path.title)}</option>`).join('')}</select></div><a class="ps-browse-toggle" href="${safe(url({browse:q().has('browse')?null:'1',pick:null,edge:null}))}">⌕ Find a part</a></div>`;
    }

    // 1. Spatial View Mode Switcher (2.5D Elevation Stack vs 2D Flat, or 1D Belt Strip vs Component Matrix)
    let spatialSwitch='';
    if(['conveyor','feeder'].includes(s.kind)&&q().get('scene')!=='connections'){
      const isMatrix=q().get('spread')==='1';
      spatialSwitch=`<div class="ps-view-seg" role="group" aria-label="Conveyor layout mode"><a class="ps-seg-btn ${!isMatrix?'is-active':''}" href="${safe(url({spread:null}))}" ${!isMatrix?'aria-current="true"':''}>⇄ 1D Belt Strip</a><a class="ps-seg-btn ${isMatrix?'is-active':''}" href="${safe(url({spread:'1'}))}" ${isMatrix?'aria-current="true"':''}>⊞ Component Matrix</a></div>`;
    }else if(['crusher-house','silo-house','sampler-system','transfer','screenhouse'].includes(s.kind)&&q().get('scene')!=='connections'&&(!s._sceneDecks||s._sceneDecks.length>1)){
      const iso=isIsoStack();
      spatialSwitch=`<div class="ps-view-seg" role="group" aria-label="Building projection mode"><a class="ps-seg-btn ${iso?'is-active':''}" href="${safe(url({iso:null}))}" ${iso?'aria-current="true"':''}>◫ 2.5D Stack</a><a class="ps-seg-btn ${!iso?'is-active':''}" href="${safe(url({iso:'0',floor:null}))}" ${!iso?'aria-current="true"':''}>▭ 2D Flat</a></div>`;
    }else if(['stacker','reclaimer'].includes(s.kind)&&q().get('scene')!=='connections'&&q().get('view')!=='3d'){
      const isMatrix=q().get('spread')==='1';
      spatialSwitch=`<div class="ps-view-seg" role="group" aria-label="Yard machine layout mode"><a class="ps-seg-btn ${!isMatrix?'is-active':''}" href="${safe(url({spread:null}))}" ${!isMatrix?'aria-current="true"':''}>⇄ Assembled Machine</a><a class="ps-seg-btn ${isMatrix?'is-active':''}" href="${safe(url({spread:'1'}))}" ${isMatrix?'aria-current="true"':''}>⊞ Component Matrix</a></div>`;
    }else if(s.kind==='yard'&&q().get('scene')!=='connections'){
      const isSpread=q().get('spread')==='1';
      spatialSwitch=`<div class="ps-view-seg" role="group" aria-label="Yard layout mode"><a class="ps-seg-btn ${!isSpread?'is-active':''}" href="${safe(url({spread:null}))}">Assembled</a><a class="ps-seg-btn ${isSpread?'is-active':''}" href="${safe(url({spread:'1'}))}">Spread parts</a></div>`;
    }

    // 2. Interactive Floor Slicer Pills (for multi-elevation buildings)
    let floorSlicer='';
    if(s._sceneDecks&&s._sceneDecks.length>1&&q().get('scene')!=='connections'){
      const curFloor=q().get('floor')||'all';
      floorSlicer=`<div class="ps-floor-slicer" role="group" aria-label="Building elevation floor slicer"><span class="ps-slicer-label">Floor</span><a class="ps-floor-pill ${curFloor==='all'?'is-active':''}" href="${safe(url({floor:null}))}" ${curFloor==='all'?'aria-current="true"':''}>All Levels</a>${s._sceneDecks.map(d=>`<a class="ps-floor-pill ${curFloor===d.key?'is-active':''}" href="${safe(url({floor:curFloor===d.key?null:d.key}))}" ${curFloor===d.key?'aria-current="true"':''}><span>${safe(d.elev.replace(/^EL\s*/i,''))}</span>${safe(d.title)}</a>`).join('')}</div>`;
    }

    // 3. Context-Aware Subsystem X-Ray Lenses (only disciplines actually present in the current scene)
    const netMeta=[
      ['material','Coal flow'],
      ['mechanical','Drive & mech'],
      ['utility','Water, air & lube'],
      ['electrical','Power'],
      ['control','Control & trips']
    ];
    const activeNets=netMeta.map(([k,lbl])=>{
      const edgeCount=s.edges.filter(a=>a.context?.network===k).length;
      const nodeCount=s.nodes.filter(n=>n.role!=='self'&&nodeMatchesLayer(n,k)).length;
      const count=edgeCount||nodeCount;
      return {k,lbl,count,edgeCount};
    }).filter(x=>x.count>0);

    const xrayPills=activeNets.length>1?`<div class="ps-layers" role="group" aria-label="Subsystem X-Ray lens"><a href="${safe(url({layer:null}))}" ${layer==='all'?'aria-current="true"':''}>All systems</a>${activeNets.map(x=>`<a href="${safe(url({layer:layer===x.k?null:x.k}))}" ${layer===x.k?'aria-current="true"':''}>${x.lbl} <small>${x.count}</small></a>`).join('')}</div>`:'';

    return `<div class="ps-toolbar">${spatialSwitch}${floorSlicer}${xrayPills}<a class="ps-browse-toggle" href="${safe(url({browse:q().has('browse')?null:'1',pick:null,edge:null}))}">⌕ Find a part (${(s.all||s.nodes).length})</a></div>`;
  }
  function view(projection,helpers){
    p=projection;api=helpers;activeFloorBounds=null;
    const entry=q().get('equipment')||M.areaEntry(p,q().get('area'));
    s=M.scene(p,entry,q().get('area'));
    s._sceneDecks=null;s._routeStreamNodes=null;s._activeRouteNodes=null;
    const layer=q().get('layer')||'all';
    s._activeLayerEndpoints=layer==='all'?null:new Set(s.edges.filter(a=>a.context?.network===layer).flatMap(a=>[a.canonical_subject,a.canonical_object]));
    const has3DCapability=s.kind==='stacker'||s.kind==='reclaimer';
    const is3DView=has3DCapability&&q().get('view')==='3d';
    const body=is3DView?'':(s.kind==='plant'?plant():s.kind==='area'?areaScene():q().get('scene')==='connections'?connectionsScene():equipmentScene()),panel=inspector()||browse();
    const toolbarHtml=buildSmartToolbar();
    const hasTopbar=typeof document!=='undefined'&&!!document.querySelector('.topbar');
    const canvasStageHtml=is3DView&&typeof window!=='undefined'&&window.PlantYard3D
      ?window.PlantYard3D.renderStageMarkup(s)
      :`<div class="ps-canvas-wrap"><svg id="ps-canvas" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${s.width||1200} ${s.height||720}" role="group" tabindex="0" aria-label="${safe(s.title)} interactive plant schematic" data-width="${s.width||1200}" data-height="${s.height||720}" data-initial-height="${s.initialHeight||s.height||720}">${defs()}<rect x="-10000" y="-10000" width="25000" height="25000" fill="url(#ps-grid)" opacity=".38"/>${body}</svg><div class="ps-canvas-controls"><button data-action="scene-zoom" data-delta="in" aria-label="Zoom in" title="Zoom in (+)">+</button><button data-action="scene-zoom" data-delta="out" aria-label="Zoom out" title="Zoom out (-)">−</button><button data-action="scene-zoom" data-delta="fit" title="Reset view (0)">Fit</button>${s.height>760?`<button data-action="scene-zoom" data-delta="all">All parts</button>`:''}<button data-action="scene-wheel-mode" aria-pressed="${wheelZoomMode?'true':'false'}" title="Toggle mouse wheel between panning and zooming">${wheelZoomMode?'Wheel: Zoom 🔍':'Wheel: Pan ⇅'}</button><button data-action="scene-motion" aria-pressed="false">▷ Explain flow</button></div><div class="ps-canvas-hint">Click to inspect · Double-click (or Open ↗) to enter assembly · Wheel to pan · Ctrl+Wheel to zoom</div></div>`;
    return `<div class="ps-root ps-scene-${safe(s.kind)} ${['silo-house','extractor','silo','spray-system','crusher-house','crusher','screen','de-house','de-stream','transfer','conveyor','weigher','detector','drive','coupling','pump','sampler-system','stacker','reclaimer','mechanical','ship','tripper','bunker-bay','bunker'].includes(s.kind)?'ps-detail-scene':''}">${hasTopbar?'':`<header class="ps-top"><a href="#overview" class="ps-brand"><span>CHP</span><div>MAITREE<small>Plant explorer</small></div></a><nav class="ps-app-links" aria-label="Workspace"><a href="#desk">Operations desk ↗</a><a href="#documents">Documents</a></nav></header>`}<div class="ps-navigation">${crumbs()}<div class="ps-nav-right"><div class="ps-search"><label class="ps-sr-only" for="ps-search">Find any equipment</label><input id="ps-search" type="search" placeholder="Search tag or alias (TP-5, PSH, CBSH, CRH, BCN-5A…)" autocomplete="off"><div id="ps-search-results" hidden></div></div><span class="ps-model">Documented model · v${p.version}</span></div></div><section class="ps-workspace ${panel?'has-inspector':''}"><div class="ps-main"><header class="ps-heading"><div><div class="ps-eyebrow">${s.kind==='plant'?'THE COAL JOURNEY':s.kind==='area'?'PROCESS AREA':'INSIDE THE PLANT'}</div><h1>${safe(s.title)}</h1><p>${safe(s.description)}</p></div><div class="ps-heading-actions">${s.id?`<div class="ps-view-seg" role="group" aria-label="Equipment view mode"><a class="ps-seg-btn ${!is3DView?'is-active':''}" href="${safe(url({view:null,tab:null}))}" ${!is3DView?'aria-current="page"':''}>📐 Schematic</a>${has3DCapability?`<a class="ps-seg-btn ${is3DView?'is-active':''}" href="${safe(url({view:'3d',tab:null,scene:null,spread:null}))}" ${is3DView?'aria-current="page"':''}>🧊 3D Model</a>`:''}<a class="ps-seg-btn" href="${safe(url({equipment:s.id,view:'records',tab:'overview',pick:null,edge:null}))}">📋 Full Dossier</a></div><a class="ps-details-button" href="${safe(pickURL(s.id))}">About ${safe(s.title)} ⓘ</a>`:''}</div></header>${contextRail()}${crusherRouteGuide()}${toolbarHtml}${routeSummaryBanner()}${canvasStageHtml}<div class="ps-legend"><span><i class="ps-key material"></i>Coal</span><span><i class="ps-key mechanical"></i>Mechanical drive</span><span><i class="ps-key utility"></i>Air / water / oil</span><span><i class="ps-key electrical"></i>Electrical supply</span><span><i class="ps-key control"></i>Control</span><span class="ps-basis">${is3DView?'1:1 True-Scale 3D Kinematic Model · WebGL On-Demand':'Illustrative arrangement · no live status'}</span></div>${s.kind!=='plant'?`<nav class="ps-plant-strip" aria-label="Plant context">${p.stages.map(st=>`<a href="${areaURL(st.id)}" ${p.memberships.get(s.id)?.has(st.id)||s.area===st.id?'aria-current="true"':''}><span>${String(st.number).padStart(2,'0')}</span>${safe(st.short)}</a>`).join('')}</nav>`:''}</div>${panel}</section></div>`;
  }
  function bind(){
    cleanup?.();
    if(typeof window!=='undefined'&&window.PlantYard3D&&(!(s&&(s.kind==='stacker'||s.kind==='reclaimer'))||q().get('view')!=='3d')){
      window.PlantYard3D.unmount();
    }
    const root=document.querySelector('.ps-root');document.body.classList.toggle('ps-mode',!!root);if(!root)return;
    const svg=document.getElementById('ps-canvas'),input=document.getElementById('ps-search'),results=document.getElementById('ps-search-results');
    if(input){
      input.oninput=()=>{const qStr=input.value.trim();results.hidden=!qStr.length;const rows=PlantExplorerModel.searchEntities(p,qStr);results.innerHTML=rows.slice(0,30).map(e=>{const cn=PlantExplorerModel.commonName(p,e.id);const kindTxt=PlantExplorerModel.isPrimaryEquipment(p,e.id)?'★ '+nice(M.kind(p,e.id)):nice(M.kind(p,e.id));return `<a href="${safe(openURL(e.id))}"><strong>${safe(e.label)}</strong><small>${safe(cn?cn+' · '+kindTxt:kindTxt)}</small></a>`;}).join('')||'<p>No matching equipment.</p>';};
      input.onkeydown=e=>{if(e.key==='Escape')results.hidden=true;};
    }
    const filter=document.getElementById('ps-parts-search');if(filter)filter.oninput=()=>{const raw=filter.value.trim().toLowerCase(),norm=PlantExplorerModel.normalizeUserQuery(raw);document.querySelectorAll('.ps-part-row').forEach(el=>{el.hidden=!!raw&&!el.dataset.search.includes(raw)&&!el.dataset.search.includes(norm);});};
    if(s&&(s.kind==='stacker'||s.kind==='reclaimer')&&q().get('view')==='3d'&&typeof window!=='undefined'&&window.PlantYard3D){
      window.PlantYard3D.mount(s,{
        selectedId:h(),
        layer:q().get('layer')||'all',
        onSelect:id=>{if(id){location.hash=pickURL(id);}}
      });
      const close3d=e=>{if(e.key==='Escape'&&!document.getElementById('dialog')?.open){if(h()||q().has('edge')||q().has('browse'))location.hash=url({pick:null,edge:null,browse:null});}};
      window.addEventListener('keydown',close3d);
      cleanup=()=>{window.removeEventListener('keydown',close3d);};
      return;
    }
    if(!svg)return;
    const key=[s.id,s.area,s.kind,q().get('scene'),q().get('spread'),q().get('iso')].join('|');
    const apply=()=>svg.setAttribute('viewBox',`${viewport.x} ${viewport.y} ${viewport.w} ${viewport.h}`);
    const fit=(all=false)=>{
      if(!all&&activeFloorBounds){
        const padY=55,bandH=Math.max(340,(activeFloorBounds.yMax-activeFloorBounds.yMin)+padY*2);
        viewport={x:0,y:Math.max(0,activeFloorBounds.yMin-padY),w:Number(svg.dataset.width),h:Math.min(Number(svg.dataset.height),bandH)};
      }else{
        viewport={x:0,y:0,w:Number(svg.dataset.width),h:Number(all?svg.dataset.height:svg.dataset.initialHeight)};
      }
      apply();
    };
    const floorKey=q().get('floor')||'all';
    if(key!==viewKey||root.dataset.lastFloor!==floorKey){
      viewKey=key;
      root.dataset.lastFloor=floorKey;
      fit();
    }else{
      apply();
    }
    root._zoom=direction=>{if(direction==='fit'||direction==='all'){fit(direction==='all');return;}const scale=direction==='in'?.8:1.25;if(viewport.w*scale<220||viewport.w*scale>12000)return;viewport.x+=viewport.w*(1-scale)/2;viewport.y+=viewport.h*(1-scale)/2;viewport.w*=scale;viewport.h*=scale;apply();};
    // Ergonomic Wheel / Trackpad Navigation:
    // - By default, 2-finger trackpad scroll or mouse wheel pans smoothly across tall/wide schematics
    // - Holding Ctrl/Cmd (or trackpad pinch-to-zoom, or toggling Wheel: Zoom mode) zooms centered on cursor
    svg.addEventListener('wheel',e=>{
      e.preventDefault();
      const r=svg.getBoundingClientRect();
      if(!r.width||!r.height)return;
      const isHorizSwipe=!e.ctrlKey&&!e.metaKey&&Math.abs(e.deltaX)>Math.abs(e.deltaY)*1.35;
      if(e.ctrlKey||e.metaKey||(wheelZoomMode&&!e.shiftKey&&!isHorizSwipe)){
        const fx=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width));
        const fy=Math.max(0,Math.min(1,(e.clientY-r.top)/r.height));
        const rawDelta=e.deltaMode===1?e.deltaY*18:e.deltaY;
        const scale=Math.exp(rawDelta*(e.ctrlKey?0.0022:0.0014));
        const nextW=Math.min(12000,Math.max(220,viewport.w*scale));
        const nextH=viewport.h*(nextW/viewport.w);
        viewport.x+=(viewport.w-nextW)*fx;
        viewport.y+=(viewport.h-nextH)*fy;
        viewport.w=nextW;
        viewport.h=nextH;
      }else{
        const dx=(e.deltaMode===1?e.deltaX*22:e.deltaX)*(viewport.w/r.width);
        const dy=(e.deltaMode===1?e.deltaY*22:e.deltaY)*(viewport.h/r.height);
        const maxW=Number(svg.dataset.width)||1200,maxH=Number(svg.dataset.height)||720;
        viewport.x=Math.max(-240,Math.min(maxW-180,viewport.x+dx));
        viewport.y=Math.max(-180,Math.min(maxH-160,viewport.y+dy));
      }
      apply();
    },{passive:false});
    // Double-click on any hotspot opens its assembly directly without moving to the right-hand inspector
    svg.addEventListener('dblclick',e=>{
      const hs=e.target.closest('.ps-hotspot[data-id]');
      if(!hs)return;
      const id=hs.dataset.id;
      if(id&&id!==s.id){
        e.preventDefault();
        location.hash=openURL(id);
      }
    });
    let drag=null,moved=false;
    svg.onpointerdown=e=>{if(e.button!==0||e.target.closest('[data-action],a'))return;drag={x:e.clientX,y:e.clientY,v:{...viewport}};moved=false;svg.setPointerCapture(e.pointerId);};
    svg.onpointermove=e=>{if(!drag)return;const r=svg.getBoundingClientRect(),scale=Math.max(viewport.w/r.width,viewport.h/r.height);viewport.x=drag.v.x-(e.clientX-drag.x)*scale;viewport.y=drag.v.y-(e.clientY-drag.y)*scale;moved=true;apply();};
    svg.onpointerup=()=>drag=null;svg.onpointercancel=()=>drag=null;
    svg.onpointerover=e=>{
      const hs=e.target.closest('.ps-hotspot'),ed=e.target.closest('.ps-edge');
      const activeId=hs?.dataset.id||h();
      if(ed){
        svg.classList.add('has-hover-focus');
        svg.querySelectorAll('.ps-edge').forEach(el=>el.classList.toggle('is-active',el===ed));
      }else if(activeId){
        const hasAny=[...svg.querySelectorAll('.ps-edge')].some(el=>el.dataset.from===activeId||el.dataset.to===activeId);
        svg.classList.toggle('has-hover-focus',hasAny);
        svg.querySelectorAll('.ps-edge').forEach(el=>el.classList.toggle('is-active',el.dataset.from===activeId||el.dataset.to===activeId));
      }else{
        svg.classList.remove('has-hover-focus');
        svg.querySelectorAll('.ps-edge.is-active').forEach(el=>el.classList.remove('is-active'));
      }
    };
    svg.onpointerleave=()=>{
      const pickId=h();
      const hasAny=pickId&&[...svg.querySelectorAll('.ps-edge')].some(el=>el.dataset.from===pickId||el.dataset.to===pickId);
      svg.classList.toggle('has-hover-focus',!!hasAny);
      svg.querySelectorAll('.ps-edge').forEach(el=>el.classList.toggle('is-active',!!pickId&&(el.dataset.from===pickId||el.dataset.to===pickId)));
    };
    svg.onkeydown=e=>{if(e.target!==svg)return;if(['+','=','-','0','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();if(['+','=','-','0'].includes(e.key))root._zoom(e.key==='0'?'fit':e.key==='-'?'out':'in');else{viewport.x+=e.key==='ArrowLeft'?-50:e.key==='ArrowRight'?50:0;viewport.y+=e.key==='ArrowUp'?-50:e.key==='ArrowDown'?50:0;apply();}}};
    const pathSelect=document.getElementById('ps-path');if(pathSelect)pathSelect.onchange=()=>location.hash=url({path:pathSelect.value||null});
    const close=e=>{if(e.key==='Escape'&&!document.getElementById('dialog')?.open){if(h()||q().has('edge')||q().has('browse'))location.hash=url({pick:null,edge:null,browse:null});}};document.addEventListener('keydown',close);cleanup=()=>document.removeEventListener('keydown',close);
    const selected=h()||q().get('edge')||(q().has('browse')?'browse':'');
    if(selected!==lastPick){
      lastPick=selected;
      if(selected){
        // If the selected node sits under the right-hand floating inspector drawer, gently nudge viewport.x so it stays visible
        const pickedEl=h()?svg.querySelector(`.ps-hotspot[data-id="${CSS.escape(h())}"]`):null;
        if(pickedEl&&!window.matchMedia('(max-width:760px)').matches){
          const nx=Number(pickedEl.dataset.x)||0,nw=Number(pickedEl.dataset.w)||150;
          const visibleRight=viewport.x+viewport.w*0.66;
          if(nx+nw>visibleRight){
            viewport.x=Math.min(Number(svg.dataset.width)-viewport.w*0.4,(nx+nw)-viewport.w*0.62);
            apply();
          }
        }
        requestAnimationFrame(()=>{const panel=document.querySelector('.ps-inspector,.ps-browser'),heading=panel?.querySelector('h2');heading?.setAttribute('tabindex','-1');heading?.focus({preventScroll:true});if(window.matchMedia('(max-width:760px)').matches)panel?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});});
      }
    }
  }
  async function action(name,el){
    if(!name.startsWith('scene-'))return false;
    if(name==='scene-open'){
      if(el.dataset.id&&el.dataset.id!==s.id)location.hash=openURL(el.dataset.id);
      return true;
    }
    if(name==='scene-floor'){
      const fl=el.dataset.floor;
      location.hash=url({floor:(!fl||fl==='all'||q().get('floor')===fl)?null:fl});
      return true;
    }
    if(name==='scene-wheel-mode'){
      wheelZoomMode=!wheelZoomMode;
      el.setAttribute('aria-pressed',String(wheelZoomMode));
      el.textContent=wheelZoomMode?'Wheel: Zoom 🔍':'Wheel: Pan ⇅';
      return true;
    }
    if(name==='scene-pick'){
      // Clicking an already-selected node opens its schematic directly!
      if(h()===el.dataset.id&&el.dataset.id!==s.id){
        location.hash=openURL(el.dataset.id);
      }else{
        location.hash=pickURL(el.dataset.id);
      }
      return true;
    }
    if(name==='scene-path-source'){const path=p.paths.find(x=>x.id===q().get('path'));if(path)modal('Documented route',path.facts.map(a=>api.fact(a)).join(''));}
    if(name==='scene-edge')location.hash=url({edge:el.dataset.id,pick:null,browse:null});
    if(name==='scene-zoom')document.querySelector('.ps-root')?._zoom(el.dataset.delta);
    if(name==='scene-motion'){const active=document.getElementById('ps-canvas')?.classList.toggle('ps-explain');el.setAttribute('aria-pressed',String(!!active));el.textContent=active?'Ⅱ Stop illustration':'▷ Explain flow';const hint=document.querySelector('.ps-canvas-hint');if(hint)hint.textContent=active?'Illustrating documented directions · alternatives may not run together':'Click to inspect · Double-click (or Open ↗) to enter assembly · Wheel to pan · Ctrl+Wheel to zoom';}
    return true;
  }
  return {view,bind,action};
})();
if(typeof window!=="undefined")window.PlantScene=PlantScene;
if(typeof globalThis!=="undefined")globalThis.PlantScene=PlantScene;
