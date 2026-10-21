import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Virtual Lab AAS 7000", page_icon="🔬", layout="wide")

THREE_LIBS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
"""

# =====================================================================
# 1) MODEL 3D AAS (skala seragam 1 unit = 1 cm, proporsi 1:1 ke ukuran nyata)
# =====================================================================
AAS_HTML = THREE_LIBS + """
<style>
 body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#f0f9ff;color:#1e293b}
 #wrap{display:flex;flex-wrap:wrap;height:660px}
 #c{flex:1 1 480px;position:relative;min-height:420px}
 #panel{flex:0 0 330px;padding:14px;overflow:auto;background:#ffffff;font-size:14px;line-height:1.55;max-height:660px;box-sizing:border-box}
 #panel h3{margin:0 0 6px;color:#db2777}
 .chip{display:inline-block;margin:2px;padding:4px 9px;border-radius:14px;background:#e0e7ff;color:#3730a3;cursor:pointer;font-size:12px;border:1px solid #a5b4fc}
 .chip:hover,.chip.on{background:#ec4899;color:#fff;border-color:#ec4899}
 #hint{position:absolute;left:10px;top:8px;font-size:12px;color:#334155;pointer-events:none}
 #tools{position:absolute;right:10px;top:8px;font-size:12px}
 #tools label{color:#334155;margin-left:8px;cursor:pointer}
</style>
<div id="wrap">
 <div id="c"><div id="hint">Putar: seret • Zoom: scroll • Klik komponen untuk penjelasan • 1 unit = 1 cm</div>
  <div id="tools"><label><input type="checkbox" id="rot"> Putar otomatis</label>
  <label><input type="checkbox" id="trans" checked> Bodi transparan</label>
  <label>💥 Uraikan <input type="range" id="exp" min="0" max="100" value="0" style="vertical-align:middle;width:90px"></label></div></div>
 <div id="panel"><div id="chips"></div><hr style="border-color:#e2e8f0"><div id="info">
 <h3>Klik komponen AAS</h3>Klik bagian 3D atau tombol di atas untuk menampilkan fungsi dan prinsip kerjanya.</div></div>
</div>
<script>
const el=document.getElementById('c');
const scene=new THREE.Scene(); scene.background=new THREE.Color(0xe0f2fe);
const camera=new THREE.PerspectiveCamera(45,el.clientWidth/el.clientHeight,0.1,2000);
camera.position.set(75,55,100);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setPixelRatio(devicePixelRatio);
renderer.setSize(el.clientWidth,el.clientHeight); el.appendChild(renderer.domElement);
const controls=new THREE.OrbitControls(camera,renderer.domElement); controls.target.set(0,15,0); controls.update();
scene.add(new THREE.AmbientLight(0xffffff,0.7));
const dl=new THREE.DirectionalLight(0xffffff,0.8); dl.position.set(60,100,80); scene.add(dl);
scene.add(new THREE.GridHelper(160,16,0x93c5fd,0xbfdbfe));

const parts={}, pick=[];
function M(c,o){return new THREE.MeshStandardMaterial({color:c,transparent:o<1,opacity:o,metalness:.25,roughness:.55,emissive:0x000000});}
function reg(key,m,pickable=true){m.userData.key=key;(parts[key]=parts[key]||[]).push(m);scene.add(m);if(pickable)pick.push(m);return m;}
function box(k,w,h,d,x,y,z,c,o=1,p=true){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),M(c,o));m.position.set(x,y,z);return reg(k,m,p);}
function cyl(k,rt,rb,h,ax,x,y,z,c,o=1){const m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,32),M(c,o));
 if(ax=='x')m.rotation.z=Math.PI/2; if(ax=='z')m.rotation.x=Math.PI/2; m.position.set(x,y,z);return reg(k,m);}

// ---- Bodi (ukuran perkiraan, ganti sesuai manual jika perlu): 46 x 34 x 57 cm
const body=box('body',46,34,57,0,17,0,0xc7d2fe,0.22,false);
const edges=new THREE.LineSegments(new THREE.EdgesGeometry(body.geometry),new THREE.LineBasicMaterial({color:0x4f46e5}));
edges.position.copy(body.position);scene.add(edges);
box('body',48,2,59,0,-1,0,0x818cf8,1,false);

// ---- Jalur optik (sumbu x, tinggi y=14)
cyl('beam',0.3,0.3,28,'x',-1,14,0,0xfde047,0.7);
// Lampu katoda berongga + turret
cyl('hcl',2.3,2.3,9,'x',-15,14,0,0xf59e0b);
cyl('turret',6,6,2,'x',-21,14,0,0xec4899);
// Lampu D2 (koreksi latar)
cyl('d2',1.6,1.6,7,'z',-8,14,-9,0x818cf8);
// Atomizer nyala
cyl('chamber',3.2,3.2,9,'y',0,4.5,0,0x06b6d4);
cyl('nebulizer',0.9,0.9,6,'x',-6,5,0,0xf97316);
box('burner',11,1.2,0.7,0,10,0,0xfbbf24);
const fl=new THREE.Mesh(new THREE.ConeGeometry(1.8,6,24),M(0xfb923c,0.6)); fl.position.set(0,13.6,0);reg('flame',fl);
box('drain',0.8,5,0.8,3.5,-0.5,0,0x0ea5e9);
// Monokromator + detektor
box('mono',10,10,12,10.5,14,0,0x22c55e,0.85);
cyl('pmt',2.5,2.5,5,'x',18,14,0,0xef4444);
// Kontrol gas (belakang)
box('gas',12,6,2,10,22,-27.5,0xf43f5e);
cyl('gasport',0.7,0.7,3,'z',7,22,-29.5,0xfacc15);
cyl('gasport',0.7,0.7,3,'z',13,22,-29.5,0x60a5fa);
// Tungku grafit GFA-7000 (opsional, di sisi kiri)
box('gfa',22,20,25,-38,10,0,0xa78bfa,0.9);
// Autosampler ASC-7000 (sisi kanan)
box('asc',20,14,25,38,7,0,0x14b8a6,0.9);
cyl('asc',8,8,2,'y',38,15,0,0x2dd4bf);
// Komputer + monitor
box('pc',30,20,2,0,26,44,0x4f46e5);
box('pc',26,16,0.4,0,26,45.1,0x38bdf8);
cyl('pc',1.5,1.5,10,'y',0,8,44,0xa855f7);

const INFO={
 body:['Rangka / Bodi Utama','Rumah instrumen yang melindungi sistem optik dan atomizer, menjaga stabilitas suhu dan keselamatan operator (interlock, ventilasi). Ukuran model ±46 × 57 × 34 cm (perkiraan).'],
 beam:['Jalur Berkas Cahaya','Radiasi dari lampu melewati uap atom di nyala/tungku lalu menuju monokromator. Absorbansi mengikuti Hukum Lambert–Beer: A = ε·b·c.'],
 hcl:['Hollow Cathode Lamp (HCL)','Sumber radiasi garis spesifik unsur (mis. lampu Ca, λ 422,7 nm). Katoda dari logam analit; gas isian Ne/Ar tereksitasi sehingga atom katoda memancarkan garis yang sama dengan garis serapan analit. Setiap unsur butuh lampu sendiri.'],
 turret:['Turret Lampu Otomatis','AA-7000 memiliki turret multi-lampu (hingga 6). Lampu berikutnya dapat dipanaskan lebih dulu sehingga ganti unsur cepat dan stabil.'],
 d2:['Lampu Deuterium (D₂) – Koreksi Latar','Memancarkan spektrum kontinu (UV) untuk mengoreksi serapan latar (absorpsi molekul, hamburan) pada koreksi D₂. Latar diukur dengan D₂, lalu dikurangi dari serapan total. Shimadzu juga menyediakan koreksi SR (self-reversal).'],
 chamber:['Ruang Pengabut (Spray Chamber)','Mengubah aerosol menjadi tetesan halus dan seragam; tetesan besar dibuang ke drain. Terdapat impact bead untuk memecah tetesan.'],
 nebulizer:['Nebulizer','Menyedot larutan sampel (efek Venturi akibat aliran oksidan) dan mengubahnya menjadi aerosol. Laju hisap tipikal 4–6 mL/menit.'],
 burner:['Kepala Pembakar (Burner Head)','Slot panjang memberi lintasan optik panjang (b besar) sehingga sensitivitas tinggi. Udara–asetilena (±2300 °C) untuk Ca; N₂O–asetilena (±2700 °C) bila gangguan fosfat/Al sangat kuat dan dipakai burner khusus.'],
 flame:['Nyala (Atomizer)','Zona tempat desolvasi → penguapan → disosiasi sehingga terbentuk atom bebas Ca⁰ yang menyerap 422,7 nm. Senyawa tahan panas (Ca₃(PO₄)₂) menurunkan jumlah atom bebas.'],
 drain:['Saluran Drain','Membuang kelebihan cairan dari spray chamber melalui water-seal/liquid trap agar tidak ada gas balik (flashback). Wajib selalu terisi cairan.'],
 mono:['Monokromator','Memilih satu garis panjang gelombang (celah + kisi difraksi tipe Czerny–Turner) dan menyingkirkan emisi nyala serta garis lain. Lebar celah mempengaruhi resolusi dan intensitas.'],
 pmt:['Detektor – Photomultiplier Tube (PMT)','Mengubah foton menjadi arus listrik dan memperkuatnya. Sinyal intensitas (I dan I₀) dikonversi menjadi absorbansi oleh prosesor.'],
 gas:['Unit Kontrol Gas','Mengatur dan memantau aliran asetilena, udara, dan N₂O secara otomatis, dilengkapi sensor tekanan dan sistem keamanan (pemadaman otomatis jika kebocoran/tekanan abnormal).'],
 gasport:['Inlet Gas','Kuning: asetilena (C₂H₂, bahan bakar). Biru: udara/oksidan. Selang harus bebas kebocoran; periksa dengan larutan sabun, jangan memakai api.'],
 gfa:['Tungku Grafit GFA-7000 (opsional)','Atomisasi elektrotermal: tahap pengeringan → pengabuan → atomisasi → pembersihan. Sensitivitas ppb (µg/L) karena atom tertahan lama di jalur optik, volume sampel hanya 5–50 µL.'],
 asc:['Autosampler ASC-7000','Menyampaikan sampel, standar, dan blanko ke atomizer secara otomatis; mendukung pengenceran otomatis sehingga analisis banyak sampel lebih cepat dan presisi.'],
 pc:['Komputer & Perangkat Lunak WizAArd','Mengontrol instrumen, membuat kurva kalibrasi, menampilkan sinyal real-time, mengolah data, dan membuat laporan.']
};
const ORDER=['body','hcl','turret','d2','beam','nebulizer','chamber','burner','flame','drain','mono','pmt','gas','gasport','gfa','asc','pc'];
const chips=document.getElementById('chips'), info=document.getElementById('info');
ORDER.forEach(k=>{const s=document.createElement('span');s.className='chip';s.textContent=INFO[k][0].split(' (')[0].split(' –')[0];s.dataset.k=k;s.onclick=()=>sel(k);chips.appendChild(s);});
function sel(k){
 Object.values(parts).flat().forEach(m=>m.material.emissive.setHex(0));
 (parts[k]||[]).forEach(m=>m.material.emissive.setHex(0x2563eb));
 document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('on',c.dataset.k==k));
 info.innerHTML='<h3>'+INFO[k][0]+'</h3>'+INFO[k][1];
 if(k!='body'&&parts[k]){goal.copy(parts[k][0].position);} else goal.set(0,15,0);
}
const goal=new THREE.Vector3(0,15,0);
const ray=new THREE.Raycaster(), mouse=new THREE.Vector2(); let down=null;
renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
renderer.domElement.addEventListener('pointerup',e=>{
 if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;
 const r=renderer.domElement.getBoundingClientRect();
 mouse.set(((e.clientX-r.left)/r.width)*2-1,-((e.clientY-r.top)/r.height)*2+1);
 ray.setFromCamera(mouse,camera); const h=ray.intersectObjects(pick);
 if(h.length)sel(h[0].object.userData.key);
});
document.getElementById('rot').onchange=e=>controls.autoRotate=e.target.checked;
document.getElementById('trans').onchange=e=>{body.visible=e.target.checked;};
addEventListener('resize',()=>{camera.aspect=el.clientWidth/el.clientHeight;camera.updateProjectionMatrix();renderer.setSize(el.clientWidth,el.clientHeight);});
// foton bergerak sepanjang jalur optik
const ph=[];for(let i=0;i<9;i++){const p=new THREE.Mesh(new THREE.SphereGeometry(0.55,12,12),new THREE.MeshBasicMaterial({color:0xfef08a}));p.userData.o=i/9;scene.add(p);ph.push(p);}
// uraikan komponen (exploded view)
Object.values(parts).flat().forEach(m=>m.userData.p0=m.position.clone());
const C0=new THREE.Vector3(0,14,0);
document.getElementById('exp').oninput=e=>{const k=e.target.value/100*0.9;
 Object.entries(parts).forEach(([key,arr])=>{if(key=='body'||key=='beam')return;arr.forEach(m=>{m.position.copy(m.userData.p0).add(m.userData.p0.clone().sub(C0).multiplyScalar(k));});});
 beamVis(k);};
function beamVis(k){(parts.beam||[]).forEach(m=>m.scale.y=1+k*1.4);}
let t=0;(function loop(){requestAnimationFrame(loop);t+=0.05;
 fl.scale.set(1,1+0.12*Math.sin(t*4),1+0.08*Math.sin(t*5));fl.material.opacity=0.5+0.15*Math.sin(t*6);
 ph.forEach(p=>{const u=(p.userData.o+t*0.05)%1;p.position.set(-15+u*33,14,0);p.scale.setScalar(u>0.55&&u<0.62?0.5:1);p.material.color.setHex(u>0.6?0xfb7185:0xfef08a);});
 controls.target.lerp(goal,0.06);controls.update();renderer.render(scene,camera);})();
</script>
"""

# =====================================================================
# 2) VIDEO SIMULASI 3D: PENETAPAN KADAR Cu DALAM AIR LIMBAH
# =====================================================================
CU_HTML = THREE_LIBS + """
<style>
 body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(135deg,#fff7ed,#fdf2f8,#eef2ff);color:#1e293b}
 #chips{padding:8px 8px 2px}
 .ch{display:inline-block;margin:3px;padding:6px 12px;border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;color:#fff;opacity:.55;transition:.2s}
 .ch.on{opacity:1;transform:scale(1.07);box-shadow:0 4px 14px #0003}
 #c{height:460px;position:relative;margin:4px 8px;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px #6366f155}
 #hud{position:absolute;right:12px;top:78px;background:#fff;border-radius:12px;padding:8px 12px;font-size:13px;font-weight:700;display:none;box-shadow:0 4px 14px #0002}
 #bar{display:flex;align-items:center;gap:8px;padding:8px 12px;flex-wrap:wrap;font-size:13px}
 .btn{border:0;border-radius:10px;padding:8px 14px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(120deg,#f97316,#ec4899)}
 .btn.alt{background:linear-gradient(120deg,#06b6d4,#6366f1)}
 #seek{flex:1;min-width:160px;accent-color:#ec4899}
 #cap{margin:0 8px 8px;padding:12px 16px;border-radius:14px;background:#fff;font-size:14px;line-height:1.6;border-left:6px solid #ec4899}
 #vid video{width:100%;border-radius:12px;margin-top:6px}
</style>
<div id="chips"></div>
<div id="c"><div id="hud"></div></div>
<div id="bar"><button class="btn" id="play">⏸️ Jeda</button><input id="seek" type="range" min="0" max="1000" value="0"><span id="tm">0:00 / 1:12</span>
<select id="spd"><option value="1">1×</option><option value="0.5">0,5×</option><option value="2">2×</option></select>
<label><input type="checkbox" id="fol" checked> 🎥 Kamera otomatis</label>
<button class="btn alt" id="rec">⏺️ Rekam & unduh video</button></div>
<div id="cap"></div><div id="vid" style="margin:0 8px"></div>
<script>
const el=document.getElementById('c');
const scene=new THREE.Scene();scene.background=new THREE.Color(0xdbeafe);scene.fog=new THREE.Fog(0xdbeafe,70,150);
const camera=new THREE.PerspectiveCamera(45,el.clientWidth/el.clientHeight,0.1,300);camera.position.set(0,12,30);scene.add(camera);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(el.clientWidth,el.clientHeight);el.appendChild(renderer.domElement);
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.target.set(0,5,0);
let follow=true;controls.addEventListener('start',()=>{follow=false;document.getElementById('fol').checked=false;});
scene.add(new THREE.AmbientLight(0xffffff,0.85));const dl=new THREE.DirectionalLight(0xffffff,0.7);dl.position.set(20,40,25);scene.add(dl);
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),sm=x=>{x=cl(x);return x*x*(3-2*x);};
const fm=(v,d)=>v.toFixed(d).replace('.',',');
function mat(c,o=1){return new THREE.MeshStandardMaterial({color:c,transparent:o<1,opacity:o,roughness:.45,metalness:.1});}
function mesh(geo,c,o,x,y,z,g){const q=new THREE.Mesh(geo,mat(c,o));q.position.set(x,y,z);g.add(q);return q;}
function cyl(r,h,c,o,x,y,z,g,ax){const q=mesh(new THREE.CylinderGeometry(r,r,h,32),c,o,x,y,z,g);if(ax=='x')q.rotation.z=Math.PI/2;return q;}
function liq(r,c,x,y,z,g){const q=new THREE.Mesh(new THREE.CylinderGeometry(r,r,1,32).translate(0,0.5,0),mat(c,0.92));q.position.set(x,y,z);q.scale.y=0.001;g.add(q);return q;}
function ball(r,c,g){const q=new THREE.Mesh(new THREE.SphereGeometry(r,14,14),mat(c));g.add(q);return q;}
function label(txt,col,s,x,y,z,g){const c=document.createElement('canvas');c.width=512;c.height=72;const q=c.getContext('2d');
 q.globalAlpha=.93;q.fillStyle=col;q.fillRect(4,6,504,60);q.globalAlpha=1;q.font='bold 30px sans-serif';q.fillStyle='#fff';q.textAlign='center';q.fillText(txt,256,47);
 const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(c),transparent:true,depthTest:false}));
 sp.scale.set(14*s,14*s*72/512,1);sp.position.set(x,y,z);sp.renderOrder=5;g.add(sp);return sp;}
// lantai warna-warni
mesh(new THREE.CylinderGeometry(26,26,0.6,64),0xfde68a,1,0,-0.3,0,scene);
const rg=mesh(new THREE.TorusGeometry(26,0.4,8,80),0xf472b6,1,0,0,0,scene);rg.rotation.x=Math.PI/2;

// ---- data standar & regresi (contoh)
const Cs=[0,0.5,1,2,3,4,5],As=[0.002,0.023,0.045,0.087,0.130,0.172,0.214],AS=0.098;
const nn=Cs.length,mx=Cs.reduce((a,b)=>a+b)/nn,my=As.reduce((a,b)=>a+b)/nn;let sxy=0,sxx=0,syy=0;
Cs.forEach((c,i)=>{sxy+=(c-mx)(As[i]-my);sxx+=(c-mx)(c-mx);syy+=(As[i]-my)*(As[i]-my);});
const sl=sxy/sxx,ic=my-sl*mx,R2=sxy*sxy/(sxx*syy),CS=(AS-ic)/sl;
const EQ='y = '+fm(sl,4)+'x + '+fm(ic,4);

const CH=[
{t:'1 · Pengambilan Sampel',s:'Air limbah masuk botol PE, diawetkan HNO₃',col:'#0891b2',cam:V(0,10,27),tg:V(0,5,0),
 cap:'<b>Pengambilan & pengawetan.</b> Ambil air limbah representatif (sesaat/komposit) di titik outlet IPAL memakai botol polietilen yang sudah dicuci asam dan dibilas aquabidest. Segera awetkan dengan HNO₃ pekat hingga <b>pH &lt; 2</b> agar Cu²⁺ tidak mengendap atau menempel pada dinding botol.'},
{t:'2 · Destruksi Asam',s:'HNO₃ pekat + pemanasan hingga larutan jernih',col:'#f97316',cam:V(0,11,26),tg:V(0,6,0),
 cap:'<b>Destruksi.</b> Sampel dikocok, diambil volume tertentu (mis. 50–100 mL), ditambah HNO₃ pekat ±5 mL lalu dipanaskan pada hot plate (±95 °C). Bahan organik teroksidasi dan Cu terikat partikulat terlarut; larutan berubah dari keruh kecokelatan menjadi <b>jernih</b>. Kerjakan di <b>lemari asam</b> (uap NO₂ beracun) dengan APD lengkap.'},
{t:'3 · Penyaringan & Pengenceran',s:'Disaring ke labu ukur, ditera dengan aquabidest',col:'#8b5cf6',cam:V(0,12,27),tg:V(0,7,0),
 cap:'<b>Penyiapan larutan uji.</b> Setelah dingin, larutan disaring (kertas saring bebas logam) ke labu ukur, lalu ditera dengan aquabidest sampai tanda batas dan dikocok. Catat <b>faktor pengenceran (FP)</b> = volume akhir ÷ volume sampel awal.'},
{t:'4 · Deret Larutan Standar',s:'Larutan induk Cu 1000 mg/L → 0,5–5,0 mg/L',col:'#ec4899',cam:V(0,10,33),tg:V(0,3,0),
 cap:'<b>Deret standar.</b> Dari larutan induk Cu 1000 mg/L dibuat larutan baku kerja, lalu deret 0,5 – 5,0 mg/L dan <b>blanko</b>. Warna biru menggambarkan konsentrasi Cu²⁺ yang makin pekat. Matriks asam (HNO₃) dibuat sama dengan sampel. Pilih deret yang mengapit konsentrasi sampel.'},
{t:'5 · Pengukuran dengan AAS',s:'HCL Cu 324,7 nm • nyala udara–asetilena',col:'#22c55e',cam:V(2,12,34),tg:V(2,5,0),
 cap:'<b>Pengukuran.</b> Lampu katoda berongga Cu memancarkan garis <b>324,7 nm</b>. Sampel diaspirasi → aerosol → desolvasi → penguapan → atomisasi Cu²⁺ menjadi Cu⁰ di nyala <b>udara–asetilena</b>. Atom Cu menyerap sebagian foton (bola ungu yang hilang) sehingga absorbansi naik: A = ε·b·c. Urutan: blanko (auto-zero) → standar → sampel, dibilas aquabidest di antaranya.'},
{t:'6 · Kurva Kalibrasi & Hasil',s:EQ+'  |  Cu sampel = '+fm(CS,2)+' mg/L',col:'#eab308',cam:V(0,10,30),tg:V(-1,6,0),
 cap:'<b>Perhitungan.</b> Absorbansi standar diplot terhadap konsentrasi: <b>'+EQ+'</b>, R² = '+fm(R2,4)+' (r ≥ 0,995 umumnya disyaratkan). Absorbansi sampel '+fm(AS,3)+' → C = (A − b)/m = <b>'+fm(CS,2)+' mg/L</b>; kadar asli = C × FP. Bandingkan dengan baku mutu air limbah sesuai jenis industri (mis. Permen LH No. 5/2014 – mohon verifikasi). Gunakan tab <i>Kurva Kalibrasi</i> untuk data Anda.'}
];
const G=CH.map(()=>{const g=new THREE.Group();g.visible=false;scene.add(g);return g;}),UP=[];

// ===== Bab 1
{const g=G[0];cyl(1.2,15,0xf97316,1,-4.75,11,0,g,'x');const t=mesh(new THREE.TorusGeometry(1.3,0.25,8,24),0xea580c,1,2.5,11,0,g);t.rotation.y=Math.PI/2;
 cyl(3,8,0xe0f2fe,0.25,2,4,0,g);const L=liq(2.8,0x2dd4bf,2,0.1,0,g);cyl(1.6,1.2,0xec4899,1,9,0.6,0,g);
 label('Outlet air limbah','#f97316',1,-6,13.3,0,g);label('Botol sampel (PE)','#0891b2',1,9,3.2,0,g);label('+ HNO₃ → pH < 2','#ec4899',0.9,2,9.6,0,g);
 const P=[];for(let i=0;i<16;i++)P.push(ball(0.3,0x14b8a6,g));
 UP[0]=(u,T)=>{const top=0.1+7.4*u;L.scale.y=Math.max(top,0.001);P.forEach((p,i)=>{const k=(T*1.6+i/16)%1;p.position.set(2+Math.sin(i)0.3,10.4-k(10.4-top),Math.cos(i)*0.3);p.visible=u<0.97;});};}
// ===== Bab 2
{const g=G[1];mesh(new THREE.BoxGeometry(10,1.2,10),0x7c3aed,1,0,0.6,0,g);const co=mesh(new THREE.TorusGeometry(3.6,0.3,8,40),0xff5a1f,1,0,1.25,0,g);co.rotation.x=Math.PI/2;
 cyl(3.2,8,0xe0f2fe,0.25,0,5.2,0,g);const L=liq(3.0,0x8b5a2b,0,1.3,0,g);L.scale.y=4.5;
 mesh(new THREE.ConeGeometry(0.5,2,16),0xf43f5e,1,2,13,0,g).rotation.x=Math.PI;cyl(0.6,3,0xf43f5e,1,2,15,0,g);
 label('HNO₃ pekat (±5 mL)','#f43f5e',0.95,6.5,15,0,g);label('Pemanas ±95 °C','#7c3aed',0.9,-7.5,2.5,0,g);const ok=label('Larutan jernih ✔️ destruksi selesai','#16a34a',1.15,0,12.3,0,g);
 const B=[],F=[];for(let i=0;i<14;i++)B.push(ball(0.22,0xffffff,g));
 for(let i=0;i<6;i++){const q=new THREE.Mesh(new THREE.SphereGeometry(0.8,12,12),mat(0xe2e8f0,0.4));g.add(q);F.push(q);}
 const D=ball(0.28,0xfacc15,g),c0=new THREE.Color(0x8b5a2b),c1=new THREE.Color(0x7dd3fc);
 UP[1]=(u,T)=>{L.material.color.copy(c0).lerp(c1,sm((u-0.2)/0.7));co.material.emissive.setHex(0xff3300);co.material.emissiveIntensity=0.35+0.3*Math.sin(T*5);
  D.visible=u<0.4;D.position.set(2,11.5-((T*1.8)%1)*(11.5-5.8),0);ok.visible=u>0.85;
  B.forEach((b,i)=>{const k=(T*1.1+i/14)%1;b.visible=u>0.12;b.position.set(Math.cos(i*2.1)2.2(0.4+0.6*((i*7)%5)/5),1.5+k*4.2,Math.sin(i*2.1)2.2(0.4+0.6*((i*3)%5)/5));});
  F.forEach((q,i)=>{const k=(T*0.5+i/6)%1;q.visible=u>0.1;q.position.set(Math.sin(i*2)1.3,9.5+k*4.5,Math.cos(i*2)*1.3);q.scale.setScalar(0.6+k*1.2);q.material.opacity=0.45(1-k);});};}
// ===== Bab 3
{const g=G[2];cyl(2.6,6,0xe0f2fe,0.25,0,3,0,g);cyl(0.8,4,0xe0f2fe,0.25,0,8,0,g);const L=liq(2.5,0x0ea5e9,0,0.05,0,g),N=liq(0.75,0x0ea5e9,0,6,0,g);
 const mk=mesh(new THREE.TorusGeometry(0.85,0.07,8,24),0xef4444,1,0,8.6,0,g);mk.rotation.x=Math.PI/2;
 const fu=mesh(new THREE.ConeGeometry(3.4,3.5,32,1,true),0xfde68a,0.85,0,13,0,g);fu.rotation.x=Math.PI;fu.material.side=THREE.DoubleSide;
 const fp=mesh(new THREE.ConeGeometry(3,3.2,32,1,true),0xffffff,1,0,13.1,0,g);fp.rotation.x=Math.PI;fp.material.side=THREE.DoubleSide;cyl(0.35,2,0xfde68a,0.9,0,11,0,g);
 for(let i=0;i<7;i++){const s=ball(0.18,0x78350f,g);s.position.set(Math.cos(i*1.7)*0.9,12.1+(i%3)*0.35,Math.sin(i*1.7)*0.9);}
 label('Penyaringan (kertas saring)','#8b5cf6',1.1,7.5,13.8,0,g);label('Labu ukur 50 mL','#0ea5e9',0.9,7,3,0,g);const tr=label('Tera dengan aquabidest','#ec4899',1,-6.5,9.5,0,g);
 const D=ball(0.26,0x0ea5e9,g),c0=new THREE.Color(0x0ea5e9),c1=new THREE.Color(0x93c5fd);
 UP[2]=(u,T)=>{const a=cl(u/0.7);L.scale.y=Math.max(5.8*a,0.001);N.scale.y=Math.max(2.6*cl((u-0.7)/0.3),0.001);tr.visible=u>0.68;
  L.material.color.copy(c0).lerp(c1,sm((u-0.7)/0.3));N.material.color.copy(L.material.color);
  const top=u<0.7?0.05+5.8*a:6+2.6*cl((u-0.7)/0.3);D.material.color.setHex(u<0.7?0x0ea5e9:0xffffff);D.visible=u<0.98;D.position.set(0,10-((T*1.6)%1)*(10-top),0);};}
// ===== Bab 4
{const g=G[3],names=['Blanko','0,5 mg/L','1,0 mg/L','2,0 mg/L','3,0 mg/L','4,0 mg/L','5,0 mg/L'],pal=['#94a3b8','#ef4444','#f97316','#eab308','#22c55e','#06b6d4','#8b5cf6'];
 const FL=[],ca=new THREE.Color(0xbfdbfe),cb=new THREE.Color(0x1e40af);
 for(let i=0;i<7;i++){const x=-13.2+4.4*i;cyl(1.6,3.2,0xe0f2fe,0.25,x,1.6,0,g);cyl(0.5,2.2,0xe0f2fe,0.25,x,4.3,0,g);
  const L=liq(1.5,0xe0f2fe,x,0.05,0,g);if(i)L.material.color.copy(ca).lerp(cb,(i-1)/5);FL.push(L);label(names[i],pal[i],0.62,x,6.9,0,g);}
 const pp=new THREE.Group();g.add(pp);cyl(0.2,7,0xfcd34d,1,0,10,0,pp);const bu=ball(0.7,0xf43f5e,pp);bu.position.y=14;
 const D=ball(0.22,0x2563eb,g);label('Larutan induk Cu 1000 mg/L → diencerkan','#ec4899',1.35,0,13.5,0,g);
 UP[3]=(u,T)=>{const a=Math.min(6,Math.floor(u*7)),lo=u*7-a;FL.forEach((L,i)=>{L.scale.y=i<a?2.8:(i==a?Math.max(2.8*cl(lo*1.6),0.001):0.001);});
  const tx=-13.2+4.4*a;pp.position.x+=(tx-pp.position.x)*0.15;const top=0.05+FL[a].scale.y;
  D.visible=u<0.99&&lo<0.65;D.position.set(pp.position.x,6.5-((T*2)%1)*(6.5-top),0);};}
// ===== Bab 5
{const g=G[4],Y=5.8;cyl(1.4,5,0xf97316,1,-12,Y,0,g,'x');cyl(3,1.5,0xec4899,1,-15.5,Y,0,g,'x');label('HCL Cu • 324,7 nm','#f97316',0.95,-12,9.4,0,g);
 cyl(2,3,0x06b6d4,1,0,1.5,0,g);mesh(new THREE.BoxGeometry(7,0.8,0.7),0xfbbf24,1,0,3.4,0,g);const fl=mesh(new THREE.ConeGeometry(1.4,4,24),0xfb923c,0.65,0,5.8,0,g);
 mesh(new THREE.BoxGeometry(6,6,7),0x22c55e,0.9,11,Y,0,g);label('Monokromator','#16a34a',0.85,11,9.6,0,g);cyl(2.2,4,0xef4444,1,16,Y,0,g,'x');label('Detektor PMT','#dc2626',0.85,16,2.2,0,g);
 label('Nyala udara–C₂H₂','#ea580c',0.9,0,9.6,0,g);cyl(1.5,4,0xbae6fd,0.3,-4,2,8,g);liq(1.4,0x38bdf8,-4,0.05,8,g).scale.y=3;label('Sampel Cu²⁺','#0284c7',0.8,-4,5.4,8,g);
 const cv=new THREE.CatmullRomCurve3([V(-4,3.5,8),V(-4,5,5.5),V(-2.5,3.2,2.5),V(-1,1.8,1)]);mesh(new THREE.TubeGeometry(cv,24,0.12,8,false),0xf1f5f9,1,0,0,0,g);
 const DR=[],AT=[],PH=[];for(let i=0;i<8;i++)DR.push(ball(0.22,0x7dd3fc,g));for(let i=0;i<30;i++)AT.push(ball(0.16,0xff6a00,g));for(let i=0;i<24;i++)PH.push(ball(0.28,0xa78bfa,g));
 const hud=document.getElementById('hud');
 UP[4]=(u,T)=>{const s=sm(u);fl.scale.set(1,1+0.1*Math.sin(T*8),1);DR.forEach((d,i)=>d.position.copy(cv.getPoint((T*0.6+i/8)%1)));
  AT.forEach((q,i)=>{q.visible=i<30*s;const a=i*2.4+T*1.6,r=0.25+0.6*((i*7)%5)/5;q.position.set(Math.cos(a)*r,4.4+((i*13)%10)*0.25,Math.sin(a)*r);});
  const fr=0.2*s;PH.forEach((p,i)=>{const k=(T*0.45+i/24)%1,x=-9.3+k*17.3;p.position.set(x,Y,Math.sin(i)*0.4);p.visible=!(x>-1.4&&i/24<fr);});
  hud.style.display='block';hud.innerHTML='Absorbansi: <span style="color:#16a34a">'+fm(AS*s,3)+'</span><br>Transmitans: '+fm(Math.pow(10,-AS*s)*100,1)+' %';};}
// ===== Bab 6
{const g=G[5],X=c=>-9+c*3.4,SC=48,pal=[0x94a3b8,0xef4444,0xf97316,0xeab308,0x22c55e,0x06b6d4,0x8b5cf6],BR=[];
 mesh(new THREE.BoxGeometry(26,0.4,6),0xfef3c7,1,3,-0.2,0,g);cyl(0.1,13,0x334155,1,-10.8,6.5,0,g);mesh(new THREE.BoxGeometry(24,0.15,0.15),0x334155,1,2.5,0,0,g);
 for(let i=0;i<7;i++){const q=new THREE.Mesh(new THREE.BoxGeometry(1.3,1,1.3).translate(0,0.5,0),mat(pal[i]));q.position.set(X(Cs[i]),0,0);q.scale.y=0.001;g.add(q);BR.push(q);
  label(fm(Cs[i],1),'#64748b',0.38,X(Cs[i]),-1,2.2,g);}
 label('Absorbansi','#334155',0.7,-10.8,13.8,0,g);label('Konsentrasi (mg/L)','#334155',0.8,5,-2.6,2.2,g);
 const p0=V(X(0),ic*SC,0.9),p1=V(X(5.4),(sl*5.4+ic)*SC,0.9),dir=p1.clone().sub(p0),LN=dir.length();
 const ln=new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.13,LN,8).translate(0,LN/2,0),mat(0xf43f5e));ln.position.copy(p0);ln.quaternion.setFromUnitVectors(V(0,1,0),dir.clone().normalize());ln.scale.y=0.001;g.add(ln);
 const eq=label(EQ+'   R² = '+fm(R2,4),'#6366f1',1.45,2,14.2,0,g);
 const xs=X(CS),ys=AS*SC,sg=new THREE.Group();g.add(sg);const sp=ball(0.65,0xf43f5e,sg);sp.position.set(xs,ys,0.9);
 [[V(-10.8,ys,0.9),V(xs,ys,0.9)],[V(xs,ys,0.9),V(xs,0,0.9)]].forEach(a=>{const l=new THREE.Line(new THREE.BufferGeometry().setFromPoints(a),new THREE.LineDashedMaterial({color:0xf43f5e,dashSize:.4,gapSize:.25}));l.computeLineDistances();sg.add(l);});
 const rs=label('Cu sampel = '+fm(CS,2)+' mg/L','#f43f5e',1.2,xs+1,ys+3.2,0.9,sg);
 UP[5]=(u,T)=>{BR.forEach((q,i)=>{q.scale.y=Math.max(As[i]*SC*cl(u*2.2-i*0.15),0.001);});ln.scale.y=Math.max(cl((u-0.5)/0.2),0.001);eq.visible=u>0.55;
  sg.visible=u>0.75;sp.scale.setScalar(1+0.18*Math.sin(T*6));rs.visible=u>0.85;};}

// ---- judul di dalam kanvas (ikut terekam di video)
const tc=document.createElement('canvas');tc.width=1024;tc.height=160;const tx=tc.getContext('2d'),tex=new THREE.CanvasTexture(tc);
const ts=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false}));ts.position.set(0,5.7,-19);ts.renderOrder=999;camera.add(ts);
function fit(){const w=Math.min(24,15.7*camera.aspect*0.96);ts.scale.set(w,w*160/1024,1);}fit();
const chips=document.getElementById('chips'),cap=document.getElementById('cap');
CH.forEach((c,i)=>{const s=document.createElement('span');s.className='ch';s.style.background=c.col;s.textContent=c.t;s.onclick=()=>{tt=i*12+0.01;};chips.appendChild(s);});
let cur=-1;
function show(c){cur=c;G.forEach((g,i)=>g.visible=i==c);document.querySelectorAll('.ch').forEach((s,i)=>s.classList.toggle('on',i==c));
 cap.innerHTML=CH[c].cap;cap.style.borderLeftColor=CH[c].col;if(c!=4)document.getElementById('hud').style.display='none';
 tx.clearRect(0,0,1024,160);tx.fillStyle=CH[c].col;tx.globalAlpha=.93;tx.fillRect(0,0,1024,160);tx.globalAlpha=1;tx.fillStyle='#fff';tx.textAlign='left';
 tx.font='bold 54px sans-serif';tx.fillText(CH[c].t,30,72);tx.font='34px sans-serif';tx.fillText(CH[c].s,30,126);tex.needsUpdate=true;}
// ---- pemutar
const D=72;let tt=0,playing=true,spd=1,last=performance.now(),rec=null;
const pb=document.getElementById('play'),rb=document.getElementById('rec'),sk=document.getElementById('seek'),tm=document.getElementById('tm');
const mmss=s=>Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0');
pb.onclick=()=>{if(tt>=D)tt=0;playing=!playing;pb.textContent=playing?'⏸️ Jeda':'▶️ Putar';};
sk.oninput=e=>{tt=e.target.value/1000*D;};
document.getElementById('spd').onchange=e=>{spd=+e.target.value;};
document.getElementById('fol').onchange=e=>{follow=e.target.checked;};
rb.onclick=()=>{if(rec)return;if(!window.MediaRecorder||!renderer.domElement.captureStream){alert('Browser tidak mendukung perekaman video.');return;}
 const ch=[],st=renderer.domElement.captureStream(30),mt=MediaRecorder.isTypeSupported('video/webm;codecs=vp9')?'video/webm;codecs=vp9':'video/webm';
 rec=new MediaRecorder(st,{mimeType:mt,videoBitsPerSecond:4000000});rec.ondataavailable=e=>{if(e.data.size)ch.push(e.data);};
 rec.onstop=()=>{const url=URL.createObjectURL(new Blob(ch,{type:'video/webm'}));
  document.getElementById('vid').innerHTML='<b>🎬 Video siap:</b> <a download="simulasi_Cu_air_limbah.webm" href="'+url+'">⬇️ Unduh .webm</a><video controls src="'+url+'"></video>';
  rec=null;rb.textContent='⏺️ Rekam & unduh video';};
 tt=0;playing=true;pb.textContent='⏸️ Jeda';rec.start();rb.textContent='⏺️ Merekam… (berhenti otomatis)';};
addEventListener('resize',()=>{camera.aspect=el.clientWidth/el.clientHeight;camera.updateProjectionMatrix();renderer.setSize(el.clientWidth,el.clientHeight);fit();});
(function frame(now){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,0.1);last=now;
 if(playing){tt+=dt*spd;if(tt>=D){tt=D;playing=false;pb.textContent='▶️ Ulangi';if(rec&&rec.state!='inactive')rec.stop();}}
 const c=Math.min(5,Math.floor(tt/12));if(c!=cur)show(c);const u=cl((tt-c*12)/12);UP[c](u,now/1000);
 if(follow){camera.position.lerp(CH[c].cam,0.04);controls.target.lerp(CH[c].tg,0.06);}
 sk.value=Math.round(tt/D*1000);tm.textContent=mmss(tt)+' / '+mmss(D);controls.update();renderer.render(scene,camera);})(performance.now());
</script>
"""

# =====================================================================
# UI STREAMLIT
# =====================================================================
st.markdown("""
<style>
 .stApp{background:linear-gradient(135deg,#fff7ed 0%,#fdf2f8 35%,#eef2ff 70%,#ecfeff 100%);}
 .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp li,.stApp label,.stApp td,.stApp th,.stApp span{color:#1e293b}
 .hero h1,.hero p,.hero span{color:#fff !important}
 .hero{padding:26px 30px;border-radius:20px;margin-bottom:14px;color:#fff;
  background:linear-gradient(120deg,#f97316 0%,#ec4899 35%,#8b5cf6 68%,#06b6d4 100%);box-shadow:0 10px 40px #ec489955;}
 .hero h1{margin:0;font-size:2rem;line-height:1.2;color:#fff}
 .hero p{margin:6px 0 0;opacity:.92;font-size:1.02rem}
 .pill{display:inline-block;margin:10px 6px 0 0;padding:4px 12px;border-radius:20px;background:#ffffff26;font-size:.82rem;backdrop-filter:blur(4px)}
 div[data-testid="stMetric"]{background:#fff;border:2px solid #fbcfe8;box-shadow:0 4px 14px #ec489922;border-radius:14px;padding:12px 16px}
 button[data-baseweb="tab"]{font-weight:600;font-size:1rem}
 iframe{border-radius:16px;border:2px solid #f9a8d4}
</style>
<div class="hero"><h1>🔬 Virtual Lab AAS – Shimadzu AA-7000</h1>
<p>Jelajahi instrumen secara 3D, bangun kurva kalibrasi, dan tonton video simulasi 3D penetapan kadar Cu pada air limbah.</p>
<span class="pill">🧩 Model 3D interaktif</span><span class="pill">📈 Regresi + LOD/LOQ</span>
<span class="pill">🎬 Video 3D kadar Cu air limbah</span><span class="pill">🏆 Kuis</span></div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🧩 Model 3D AAS 7000", "📈 Kurva Kalibrasi & Sampel", "🎬 Video 3D: Kadar Cu Air Limbah", "🏆 Kuis"])

# ---------------------- TAB 1 ----------------------
with tab1:
    st.markdown("Klik komponen pada model 3D (atau tombol di panel kanan) untuk melihat penjelasannya. "
                "Model dibuat dengan *skala seragam 1:1 (1 unit = 1 cm)* tanpa distorsi sumbu. "
                "Dimensi adalah perkiraan; sesuaikan dengan manual resmi bila diperlukan.")
    components.html(AAS_HTML, height=680, scrolling=False)

# ---------------------- TAB 2 ----------------------
with tab2:
    st.subheader("Data Deret Standar")
    c1, c2 = st.columns([1, 1.4])
    with c1:
        satuan = st.selectbox("Satuan konsentrasi", ["mg/L (ppm)", "µg/L (ppb)", "mol/L"], index=0)
        unit = satuan.split(" ")[0]
        origin = st.checkbox("Paksa garis melalui titik nol (intercept = 0)", value=False)
        default = pd.DataFrame({"Konsentrasi": [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0],
                                "Absorbansi": [0.002, 0.023, 0.045, 0.087, 0.130, 0.172, 0.214]})
        df = st.data_editor(default, num_rows="dynamic", use_container_width=True, key="std",
                            column_config={"Konsentrasi": st.column_config.NumberColumn(f"Konsentrasi ({unit})", format="%.4f"),
                                           "Absorbansi": st.column_config.NumberColumn("Absorbansi", format="%.4f")})
    d = df.dropna()
    ok = len(d) >= 2 and d["Konsentrasi"].nunique() >= 2
    with c2:
        if not ok:
            st.info("Masukkan minimal 2 titik data dengan konsentrasi berbeda.")
        else:
            x = d["Konsentrasi"].to_numpy(float); y = d["Absorbansi"].to_numpy(float)
            if origin:
                m = float((x * y).sum() / (x * x).sum()); b = 0.0
            else:
                m, b = np.polyfit(x, y, 1)
            yhat = m * x + b
            ss_res = float(((y - yhat) * 2).sum()); ss_tot = float(((y - y.mean()) * 2).sum())
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
            r = np.corrcoef(x, y)[0, 1] if len(x) > 2 or not origin else float(np.sqrt(max(r2, 0)))
            sign = "+" if b >= 0 else "−"
            st.success(f"*Persamaan regresi:* y = {m:.5f}x {sign} {abs(b):.5f}")
            k1, k2, k3 = st.columns(3)
            k1.metric("Slope (m)", f"{m:.5f}"); k2.metric("Koefisien korelasi (r)", f"{r:.5f}"); k3.metric("R²", f"{r2:.5f}")
            n = len(x); dof = n - (1 if origin else 2)
            if dof > 0 and m != 0:
                sy = float(np.sqrt(ss_res / dof)); lod = 3.3 * sy / abs(m); loq = 10 * sy / abs(m); conc_k = 0.0044 / abs(m)
                q1, q2, q3 = st.columns(3)
                q1.metric(f"LOD ({unit})", f"{lod:.4f}", help="3,3 × Sy/x ÷ slope"); q2.metric(f"LOQ ({unit})", f"{loq:.4f}", help="10 × Sy/x ÷ slope")
                q3.metric(f"Konsentrasi karakteristik ({unit})", f"{conc_k:.4f}", help="Konsentrasi yang memberi A = 0,0044 (1 % serapan)")
            if r2 < 0.995:
                st.warning("R² < 0,995 – periksa deret standar (pengenceran, kontaminasi, atau titik pencilan).")
            xs = np.linspace(min(x.min(), 0), x.max() * 1.05, 50)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="Standar", marker=dict(size=13, color="#ec4899", line=dict(width=2, color="#fff"))))
            fig.add_trace(go.Scatter(x=xs, y=m * xs + b, mode="lines", name="Regresi", line=dict(color="#06b6d4", width=4)))
            fig.update_layout(template="plotly_white", xaxis_title=f"Konsentrasi ({unit})", yaxis_title="Absorbansi", height=360,
                              margin=dict(l=10, r=10, t=30, b=10), title=f"y = {m:.5f}x {sign} {abs(b):.5f} | R² = {r2:.5f}")
            st.plotly_chart(fig, use_container_width=True)

    if ok:
        st.subheader("Hitung Konsentrasi Sampel")
        s_def = pd.DataFrame({"Nama sampel": ["Sampel 1", "Sampel 2"], "Absorbansi": [0.098, 0.150], "Faktor pengenceran": [1.0, 1.0]})
        smp = st.data_editor(s_def, num_rows="dynamic", use_container_width=True, key="smp")
        res = smp.dropna(subset=["Absorbansi"]).copy()
        if m == 0:
            st.error("Slope = 0, konsentrasi tidak dapat dihitung.")
        else:
            fp = res["Faktor pengenceran"].fillna(1.0)
            res[f"Konsentrasi terukur ({unit})"] = (res["Absorbansi"] - b) / m
            res[f"Konsentrasi sampel asli ({unit})"] = res[f"Konsentrasi terukur ({unit})"] * fp
            amin, amax = y.min(), y.max()
            res["Status"] = np.where((res["Absorbansi"] >= amin) & (res["Absorbansi"] <= amax), "Dalam rentang",
                                     "⚠️ Di luar rentang kalibrasi")
            st.dataframe(res.style.format({"Absorbansi": "{:.4f}", f"Konsentrasi terukur ({unit})": "{:.4f}",
                                           f"Konsentrasi sampel asli ({unit})": "{:.4f}"}), use_container_width=True)
            st.caption("Rumus: x = (y − b) / m, lalu dikalikan faktor pengenceran. "
                       "Hasil di luar rentang standar sebaiknya diencerkan/diukur ulang.")
            st.download_button("⬇️ Unduh hasil (CSV)", res.to_csv(index=False).encode("utf-8"), "hasil_aas.csv", "text/csv")

# ---------------------- TAB 3 ----------------------
with tab3:
    st.markdown("### 🧪 Penetapan Kadar Cu dalam Sampel Air Limbah (AAS Nyala)")
    st.markdown("Tonton *video simulasi 3D* 6 tahap (±72 detik): ▶️ putar/jeda, geser timeline, ubah kecepatan, atau klik tahap di atas. "
                "Tekan *⏺️ Rekam & unduh video* untuk menyimpan simulasi sebagai file video .webm.")
    components.html(CU_HTML, height=960, scrolling=True)
    with st.expander("📋 Ringkasan prosedur & parameter"):
        st.markdown("""
| Tahap | Ringkasan | Catatan penting |
|---|---|---|
| 1. Sampling | Botol PE, diawetkan HNO₃ hingga pH < 2 | Botol dicuci asam, bilas aquabidest |
| 2. Destruksi | Sampel + HNO₃ pekat, panaskan di hot plate | Lemari asam, APD |
| 3. Penyiapan | Saring → labu ukur → tera | Catat faktor pengenceran |
| 4. Standar | Deret 0,5–5,0 mg/L + blanko | Matriks asam sama dengan sampel |
| 5. Pengukuran | HCL Cu, λ 324,7 nm, nyala udara–C₂H₂ | Auto-zero dengan blanko |
| 6. Hitung | C = (A − b)/m × FP | r ≥ 0,995; bandingkan baku mutu |

Rujukan metode: SNI 6989.6:2009 (Cu secara SSA-nyala) dan baku mutu air limbah sesuai Permen LH No. 5/2014 – mohon verifikasi versi terbaru.
Parameter instrumen (lebar celah, arus lampu, tinggi burner) mengikuti manual Shimadzu AA-7000.
""")
        st.info("Data contoh pada video sama dengan data awal di tab *Kurva Kalibrasi*, jadi hasilnya dapat Anda cocokkan.")


# ---------------------- TAB 4: KUIS ----------------------
with tab4:
    st.subheader("🏆 Uji Pemahaman Anda")
    QZ = [
        ("Garis resonansi Cu yang umum dipakai pada AAS adalah …", ["248,3 nm", "324,7 nm", "422,7 nm", "589,0 nm"], 1,
         "Cu diukur pada 324,7 nm dengan lampu katoda berongga Cu."),
        ("Fungsi utama lampu deuterium (D₂) pada AA-7000 adalah …", ["Sumber garis Cu", "Pembakar nyala", "Koreksi serapan latar", "Menguatkan sinyal"], 2,
         "D₂ memberi spektrum kontinu untuk mengukur dan mengurangi serapan latar."),
        ("Mengapa sampel air limbah didestruksi dengan HNO₃ sebelum diukur?", ["Agar larutan berwarna", "Menghilangkan bahan organik dan melarutkan Cu terikat partikulat", "Menaikkan pH", "Menambah volume"], 1,
         "Destruksi asam mengoksidasi organik dan melepaskan logam sehingga seluruh Cu terukur."),
        ("Absorbansi sampel lebih tinggi dari standar tertinggi. Tindakan tepat?", ["Ekstrapolasi kurva", "Encerkan sampel lalu ukur ulang", "Abaikan saja", "Naikkan lebar celah"], 1,
         "Di luar rentang linear hasil tidak valid; encerkan agar masuk rentang kalibrasi."),
        ("Campuran gas nyala yang umum untuk analisis Cu adalah …", ["Udara–asetilena", "N₂O–asetilena", "H₂–O₂", "LPG–N₂"], 0,
         "Cu mudah teratomisasi sehingga nyala udara–asetilena sudah memadai."),
        ("Jika y = 0,0427x + 0,0005 dan A sampel = 0,098, konsentrasi sampel ≈ …", ["≈ 0,23 mg/L", "≈ 1,2 mg/L", "≈ 2,3 mg/L", "≈ 4,6 mg/L"], 2,
         "x = (0,098 − 0,0005) / 0,0427 ≈ 2,28 mg/L."),
        ("Sampel diencerkan 10× dan terbaca 1,8 mg/L. Kadar Cu sampel asli …", ["0,18 mg/L", "1,8 mg/L", "18 mg/L", "180 mg/L"], 2,
         "Kadar asli = 1,8 × FP 10 = 18 mg/L."),
    ]
    with st.form("kuis"):
        jawab = [st.radio(f"*{i+1}. {q}*", opts, index=None, key=f"q{i}") for i, (q, opts, _, _) in enumerate(QZ)]
        kirim = st.form_submit_button("✅ Periksa jawaban", type="primary")
    if kirim:
        skor = sum(1 for (q, opts, k, _), a in zip(QZ, jawab) if a == opts[k])
        st.metric("Skor Anda", f"{skor} / {len(QZ)}", f"{skor / len(QZ) * 100:.0f} %")
        st.progress(skor / len(QZ))
        for i, ((q, opts, k, why), a) in enumerate(zip(QZ, jawab)):
            (st.success if a == opts[k] else st.error)(f"*{i+1}.* {'Benar' if a == opts[k] else 'Belum tepat'} – jawaban: *{opts[k]}*. {why}")
        if skor >= 6:
            st.balloons(
