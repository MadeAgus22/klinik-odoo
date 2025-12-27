/* =========================================
   LOGIKA JS BARU (VERSI STRICT)
   Pastikan kode ini yang berjalan di browser!
   ========================================= */

console.log(">>> MEMUAT LOGIKA ODONTOGRAM V3 (STRICT MODE) <<<");

/* --- 1. SETUP --- */
const COLORS = { "CAR":"#6e6e6e", "FILL-LOG":"#9b59b6", "FILL-NON":"#2e86c1", "CROWN-METAL":"#ff4d4d", "CROWN-NON":"#04cfd6" };
const topPermanent    = [18,17,16,15,14,13,12,11,21,22,23,24,25,26,27,28];
const childUpper      = [55,54,53,52,51,61,62,63,64,65];
const childLower      = [85,84,83,82,81,71,72,73,74,75];
const bottomPermanent = [48,47,46,45,44,43,42,41,31,32,33,34,35,36,37,38];
const anteriorSet = new Set([13,12,11,21,22,23, 33,32,31,41,42,43, 53,52,51,61,62,63, 83,82,81,71,72,73]);
const shapeOf = n => (anteriorSet.has(n) ? 'anterior' : 'posterior');

/* --- 2. RENDER GIGI --- */
function toothSVG(type='posterior'){
  const w=58, h=58, pad=2.2;
  const cx=w/2, cy=h/2;
  const rw=w*0.45, rh=h*0.45;
  const x1=cx-rw/2, x2=cx+rw/2, y1=cy-rh/2, y2=cy+rh/2;
  let partsSVG='', frameInnerSVG='', frameCenterSVG='';

  if(type==='anterior'){
    const tw=rw*0.50, bw=rw*0.50;
    const yTop=cy-rh*0, yBot=cy+rh*0;
    const xLt=cx-tw/2, xRt=cx+tw/2;
    const xLb=cx-bw/2, xRb=cx+bw/2;
    frameInnerSVG = `<path class="frame-inner" d="M ${pad} ${pad} L ${xLt} ${yTop}" /><path class="frame-inner" d="M ${w-pad} ${pad} L ${xRt} ${yTop}" /><path class="frame-inner" d="M ${pad} ${h-pad} L ${xLb} ${yBot}" /><path class="frame-inner" d="M ${w-pad} ${h-pad} L ${xRb} ${yBot}" />`;
    frameCenterSVG = `<polygon class="frame-center" points="${xLt},${yTop} ${xRt},${yTop} ${xRb},${yBot} ${xLb},${yBot}" />`;
    partsSVG = `<polygon class="part" data-part="top" points="${xLt},${yTop} ${xRt},${yTop} ${w-pad},${pad} ${pad},${pad}"/><polygon class="part" data-part="right" points="${xRt},${yTop} ${xRb},${yBot} ${w-pad},${h-pad} ${w-pad},${pad}"/><polygon class="part" data-part="bottom" points="${xLb},${yBot} ${xRb},${yBot} ${w-pad},${h-pad} ${pad},${h-pad}"/><polygon class="part" data-part="left" points="${xLt},${yTop} ${xLb},${yBot} ${pad},${h-pad} ${pad},${pad}"/><polygon class="part" data-part="center" points="${xLt},${yTop} ${xRt},${yTop} ${xRb},${yBot} ${xLb},${yBot}"/>`;
  }else{
    frameInnerSVG = `<path class="frame-inner" d="M ${pad} ${pad} L ${x1} ${y1} M ${w-pad} ${pad} L ${x2} ${y1} M ${pad} ${h-pad} L ${x1} ${y2} M ${w-pad} ${h-pad} L ${x2} ${y2}"/>`;
    frameCenterSVG = `<rect class="frame-center" x="${x1}" y="${y1}" width="${rw}" height="${rh}"/>`;
    partsSVG = `<polygon class="part" data-part="top" points="${x1},${y1} ${x2},${y1} ${w-pad},${pad} ${pad},${pad}"/><polygon class="part" data-part="right" points="${x2},${y1} ${x2},${y2} ${w-pad},${h-pad} ${w-pad},${pad}"/><polygon class="part" data-part="bottom" points="${x1},${y2} ${x2},${y2} ${w-pad},${h-pad} ${pad},${h-pad}"/><polygon class="part" data-part="left" points="${x1},${y1} ${x1},${y2} ${pad},${h-pad} ${pad},${pad}"/><rect class="part" data-part="center" x="${x1}" y="${y1}" width="${rw}" height="${rh}"/>`;
  }
  return `<svg viewBox="0 0 ${w} ${h}" aria-hidden="true"><rect class="frame-outer" x="1" y="1" width="${w-2}" height="${h-2}"/>${frameInnerSVG}${frameCenterSVG}${partsSVG}</svg>`;
}

function makeTooth(n, labelPos){
  const wrap = document.createElement('div'); wrap.className='tooth'; wrap.dataset.tooth=n;
  wrap.innerHTML = toothSVG(shapeOf(n));

  const lb = document.createElement('div');
  lb.className = 'idx ' + (labelPos==='top'?'label-top':'label-bottom');
  lb.textContent = n;
  wrap.appendChild(lb);

  const topTag = document.createElement('div'); topTag.className='top-tag'; wrap.appendChild(topTag);
  
  const missing = document.createElement('div'); missing.className='missing';
  missing.innerHTML = '<div class="line l1"></div><div class="line l2"></div>';
  wrap.appendChild(missing);

  const bridge  = document.createElement('div'); bridge.className='bridge';  wrap.appendChild(bridge);
  
  const checkLayer = document.createElement('div'); checkLayer.className = 'check-layer';
  checkLayer.innerHTML = `<svg viewBox="0 0 58 58"><path d="M 14 6 L 28 50 L 46 -6"></path></svg>`;
  wrap.appendChild(checkLayer);
  const checkSVG = checkLayer.querySelector('svg');

  // EVENT LISTENER
  wrap.addEventListener('click', e=>{
    if (COLORS[currentTool] && e.target.classList.contains('part')) return;
    pushHistory();
    if (['UNE','PRE','ANO','NVT'].includes(currentTool)){
      topTag.textContent = currentTool;
      topTag.style.display = 'block';
      wrap.classList.add('flag');
    }else if(currentTool==='SISA'){
      checkSVG.style.display = (checkSVG.style.display==='block') ? 'none' : 'block';
    }else if(currentTool==='BRIDGE'){
      bridge.style.display = (bridge.style.display==='block') ? 'none' : 'block';
    }else if(currentTool==='MISSING'){
      missing.style.display = (missing.style.display==='block') ? 'none' : 'block';
    }
  });

  wrap.querySelectorAll('.part').forEach(p=>{
    p.addEventListener('click', e=>{
      const tool=currentTool, el=e.target;
      if(COLORS[tool]){
        pushHistory();
        el.style.fill = COLORS[tool];
        el.dataset.cat = tool;
      }
    });
  });
  return wrap;
}

function makeRow(arr, labelPos){
  const row=document.createElement('div'); row.className='row';
  arr.forEach(n=>row.appendChild(makeTooth(n,labelPos)));
  return row;
}

const root = document.getElementById('odontogram');
if(root) {
    root.innerHTML = ''; // Bersihkan container dulu
    root.appendChild(makeRow(topPermanent,'top'));
    const mid=document.createElement('div'); mid.className='child-block';
    mid.appendChild(makeRow(childUpper,'top'));
    mid.appendChild(makeRow(childLower,'bottom'));
    root.appendChild(mid);
    root.appendChild(makeRow(bottomPermanent,'bottom'));
}

/* --- 3. TOOLBAR --- */
let currentTool=null;
const btns=document.querySelectorAll('#controls button');
btns.forEach(b=>{
  b.addEventListener('click',()=>{
    btns.forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    currentTool=b.dataset.tool||null;
  });
});

document.getElementById('clear-all').addEventListener('click', ()=>{
  if(confirm("Hapus semua?")) {
      pushHistory();
      applySnapshot([]); // Reset total
  }
});

/* --- 4. CORE LOGIC (BAGIAN INI YANG MEMPERBAIKI BUG) --- */

function snapshot() {
  return Array.from(document.querySelectorAll('.tooth')).map(t => {
    // 1. Warna
    const parts = Array.from(t.querySelectorAll('.part')).map(p => ({
        fill: p.style.fill || 'transparent',
        cat: p.dataset.cat || ''
    }));

    // 2. Status Tanda (DIPERBAIKI)
    // Hanya simpan True jika style BENAR-BENAR 'block'
    // Jangan pakai (!== 'none') karena elemen kosong akan terhitung True!
    const isMissing = (t.querySelector('.missing').style.display === 'block');
    const isBridge  = (t.querySelector('.bridge').style.display === 'block');
    const isSisa    = (t.querySelector('.check-layer svg').style.display === 'block');
    const isTagShown = (t.querySelector('.top-tag').style.display === 'block');

    return {
      toothNr: t.dataset.tooth, // Kunci pakai Nomor Gigi
      parts: parts,
      tag: (t.querySelector('.top-tag').textContent||''),
      tagShown: isTagShown,
      flag: t.classList.contains('flag'),
      missing: isMissing,
      bridge:  isBridge,
      sisa:    isSisa,
    };
  });
}

function applySnapshot(state) {
  // A. Reset Total Dulu
  document.querySelectorAll('.tooth').forEach(t => {
      t.querySelectorAll('.part').forEach(p => { p.style.fill='transparent'; p.dataset.cat=''; });
      const tag=t.querySelector('.top-tag'); tag.textContent=''; tag.style.display='none';
      t.classList.remove('flag');
      t.querySelector('.missing').style.display='none';
      t.querySelector('.bridge').style.display='none';
      t.querySelector('.check-layer svg').style.display='none';
  });

  if (!state || !Array.isArray(state)) return;

  // B. Apply Data (Anti-Nyasar & Strict)
  state.forEach(s => {
    if(!s.toothNr) return; 
    const t = document.querySelector(`.tooth[data-tooth="${s.toothNr}"]`);
    if(t) {
        // Apply Warna
        const parts = t.querySelectorAll('.part');
        if (s.parts && s.parts.length === parts.length) {
            s.parts.forEach((p, idx)=>{ parts[idx].style.fill=p.fill; parts[idx].dataset.cat=p.cat; });
        }
        // Apply Tanda
        const tag=t.querySelector('.top-tag'); 
        tag.textContent=s.tag; 
        tag.style.display = s.tagShown ? 'block':'none';
        
        t.classList.toggle('flag', s.flag);
        t.querySelector('.missing').style.display = s.missing ? 'block':'none';
        t.querySelector('.bridge').style.display  = s.bridge  ? 'block':'none';
        t.querySelector('.check-layer svg').style.display = s.sisa ? 'block':'none';
    }
  });
}

/* --- 5. HISTORY SYSTEM --- */
const undoBtn=document.getElementById('undo');
const redoBtn=document.getElementById('redo');
const undoStack=[]; const redoStack=[];
function pushHistory(){ undoStack.push(snapshot()); redoStack.length=0; }
undoBtn.addEventListener('click', ()=>{
  if(undoStack.length){ redoStack.push(snapshot()); applySnapshot(undoStack.pop()); }
});
redoBtn.addEventListener('click', ()=>{
  if(redoStack.length){ undoStack.push(snapshot()); applySnapshot(redoStack.pop()); }
});

/* --- 6. KONEKSI ODOO --- */
const params = new URLSearchParams(window.location.search);
const emrId = params.get('emr_id');

// LOAD DATA
window.addEventListener('DOMContentLoaded', () => {
    if (!emrId) return;
    fetch('/clinic_odoo/get_odontogram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: { emr_id: emrId }
        })
    })
    .then(r => r.json())
    .then(res => {
        if (res.result && res.result.data) {
            const serverData = JSON.parse(res.result.data);
            console.log("Data dimuat dari server:", serverData);
            applySnapshot(serverData);
            undoStack.push(serverData);
        }
    });
});

// SIMPAN DATA
document.getElementById('save-odontogram').addEventListener('click', function () {
    const btn = this;
    const originalText = btn.textContent;
    btn.textContent = "Menyimpan...";
    btn.disabled = true;

    // Ambil state terbaru
    const currentState = snapshot();
    console.log("Data yang akan disimpan (Cek di sini jika ada true semua):", currentState);

    const payload = {
        jsonrpc: "2.0",
        method: "call",
        params: { 
            emr_id: parseInt(emrId), 
            odontogram_data: JSON.stringify(currentState) 
        }
    };

    fetch('/clinic_odoo/save_odontogram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
    .then(r => r.json())
    .then(res => {
        if (res.result && res.result.success) {
            alert('Berhasil disimpan!');
        } else {
            alert('Gagal: ' + (res.error ? res.error.data.message : 'Unknown'));
        }
    })
    .catch(e => alert("Koneksi Error: " + e))
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
});