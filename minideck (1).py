#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINI STREAM DECK
----------------
1) Bu dosyayi PC'de ac (cift tikla veya:  python minideck.py)
2) Ekranda yazan adresi telefonun tarayicisina yaz (ayni Wi-Fi'de olmali)
3) Telefondan butonlara bas -> PC'de uygulama/kisayol calisir.
Ek kurulum yok, sadece Python gerekli.
"""
import os, sys, json, socket, subprocess, secrets, threading, platform, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

START_PORT = 8080
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "deck_ayar.json")
SYS = platform.system()
IS_WIN = SYS == "Windows"
LOCK = threading.Lock()

DEFAULT_ITEMS = [
    {"id": "m1", "name": "Oynat/Durdur", "icon": "⏯", "color": "#7c3aed", "type": "media", "value": "playpause"},
    {"id": "m2", "name": "Sonraki", "icon": "⏭", "color": "#2563eb", "type": "media", "value": "next"},
    {"id": "m3", "name": "Önceki", "icon": "⏮", "color": "#2563eb", "type": "media", "value": "prev"},
    {"id": "m4", "name": "Ses +", "icon": "🔊", "color": "#059669", "type": "media", "value": "volup"},
    {"id": "m5", "name": "Ses -", "icon": "🔉", "color": "#059669", "type": "media", "value": "voldown"},
    {"id": "m6", "name": "Sessiz", "icon": "🔇", "color": "#dc2626", "type": "media", "value": "mute"},
]


def load_cfg():
    try:
        with open(CFG, "r", encoding="utf-8") as f:
            d = json.load(f)
        if "token" in d and "items" in d:
            return d
    except Exception:
        pass
    d = {"token": secrets.token_hex(3), "items": DEFAULT_ITEMS}
    save_cfg(d)
    return d


def save_cfg(d):
    with LOCK:
        with open(CFG, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)


CONFIG = load_cfg()

# ---------------- Calistirma ----------------
VK = {
    "ctrl": 0x11, "control": 0x11, "shift": 0x10, "alt": 0x12, "win": 0x5B, "windows": 0x5B,
    "enter": 0x0D, "esc": 0x1B, "escape": 0x1B, "tab": 0x09, "space": 0x20, "backspace": 0x08,
    "delete": 0x2E, "del": 0x2E, "insert": 0x2D, "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22, "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "printscreen": 0x2C,
}
for i in range(1, 13):
    VK["f%d" % i] = 0x6F + i
MEDIA = {"playpause": 0xB3, "next": 0xB0, "prev": 0xB1, "stop": 0xB2,
         "volup": 0xAF, "voldown": 0xAE, "mute": 0xAD}
EXTENDED = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E}


def press(vks):
    import ctypes
    u = ctypes.windll.user32
    for vk in vks:
        u.keybd_event(vk, 0, 1 if vk in EXTENDED else 0, 0)
    for vk in reversed(vks):
        u.keybd_event(vk, 0, (1 if vk in EXTENDED else 0) | 2, 0)


def send_keys(combo):
    if not IS_WIN:
        raise RuntimeError("Tuş kısayolları sadece Windows'ta çalışır")
    import ctypes
    u = ctypes.windll.user32
    vks = []
    for n in [p.strip().lower() for p in combo.split("+") if p.strip()]:
        vk = VK.get(n)
        if vk is None and len(n) == 1:
            r = u.VkKeyScanW(ord(n))
            vk = r & 0xFF if r != -1 else None
        if vk is None:
            raise ValueError("Bilinmeyen tuş: " + n)
        vks.append(vk)
    if not vks:
        raise ValueError("Tuş boş")
    press(vks)


def open_target(v):
    v = v.strip()
    if not v:
        raise ValueError("Boş")
    if IS_WIN:
        try:
            os.startfile(v)  # yol, exe, spotify:, steam:// vs.
            return
        except Exception:
            subprocess.Popen('start "" "%s"' % v.strip('"'), shell=True)
    elif SYS == "Darwin":
        subprocess.Popen(["open", v])
    else:
        subprocess.Popen(["xdg-open", v])


def run_item(it):
    t, v = it.get("type"), it.get("value", "")
    if t == "app":
        open_target(v)
    elif t == "link":
        webbrowser.open(v if "://" in v else "https://" + v)
    elif t == "keys":
        send_keys(v)
    elif t == "media":
        if not IS_WIN:
            raise RuntimeError("Medya tuşları sadece Windows'ta çalışır")
        if v not in MEDIA:
            raise ValueError("Bilinmeyen medya tuşu")
        press([MEDIA[v]])
    else:
        raise ValueError("Bilinmeyen tür")


# ---------------- Sunucu ----------------
class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _ok(self):
        q = parse_qs(urlparse(self.path).query)
        return q.get("k", [""])[0] == CONFIG["token"]

    def do_GET(self):
        p = urlparse(self.path).path
        if not self._ok():
            return self._send(403, "<meta name=viewport content='width=device-width'><body style='background:#000;color:#fff;font:20px sans-serif;padding:20px'>Adres eksik. PC'deki pencerede yazan tam adresi gir (sonunda ?k=... olmalı).", "text/html; charset=utf-8")
        if p == "/":
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if p == "/api/items":
            return self._send(200, CONFIG["items"])
        self._send(404, {"error": "yok"})

    def do_POST(self):
        if not self._ok():
            return self._send(403, {"error": "yetkisiz"})
        p = urlparse(self.path).path
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send(400, {"error": "bozuk veri"})
        if p == "/api/items":
            if not isinstance(data, list):
                return self._send(400, {"error": "liste olmalı"})
            CONFIG["items"] = data
            save_cfg(CONFIG)
            return self._send(200, {"ok": True})
        if p == "/api/run":
            it = next((x for x in CONFIG["items"] if x.get("id") == data.get("id")), None)
            if not it:
                return self._send(404, {"error": "buton bulunamadı"})
            try:
                run_item(it)
                return self._send(200, {"ok": True})
            except Exception as e:
                return self._send(200, {"ok": False, "error": str(e)})
        self._send(404, {"error": "yok"})


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


PAGE = r"""<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Mini Deck</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;user-select:none}
html,body{margin:0;height:100%;background:#000;color:#fff;font-family:system-ui,sans-serif;overflow:hidden}
#wrap{position:absolute;background:#0b0b10;display:flex;flex-direction:column;overflow:hidden;border:1px solid #222}
#bar{display:flex;gap:6px;padding:6px;align-items:center;background:#15151d;flex:none}
#bar button{flex:1;min-height:42px;border:0;border-radius:10px;background:#262634;color:#fff;font-size:20px}
#bar button.on{background:#f59e0b;color:#000}
#dot{width:12px;height:12px;border-radius:50%;background:#dc2626;flex:none;margin:0 4px}
#dot.ok{background:#22c55e}
#grid{flex:1;overflow-y:auto;padding:8px;display:grid;grid-template-columns:repeat(auto-fill,minmax(84px,1fr));gap:8px;align-content:start}
.b{border:0;border-radius:16px;color:#fff;padding:6px 2px;min-height:88px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-size:12px;line-height:1.1;text-align:center;word-break:break-word}
.b .i{font-size:30px;line-height:1}
.b:active,.b.flash{filter:brightness(1.5);transform:scale(.95)}
.edit .b{outline:2px dashed #f59e0b}
#empty{grid-column:1/-1;text-align:center;opacity:.6;padding:20px;font-size:14px}
#modal{position:absolute;top:0;left:0;right:0;bottom:0;background:#0b0b10;overflow-y:auto;padding:10px;display:none;z-index:5}
#modal h3{margin:4px 0 10px;font-size:16px}
#modal label{display:block;font-size:12px;opacity:.7;margin:10px 0 4px}
#modal input,#modal select{width:100%;padding:12px;border-radius:10px;border:1px solid #333;background:#1a1a24;color:#fff;font-size:16px}
.row{display:flex;gap:6px;flex-wrap:wrap}
.chip{padding:8px 10px;border-radius:999px;background:#262634;font-size:12px;border:0;color:#fff}
.sw{width:34px;height:34px;border-radius:50%;border:3px solid transparent}
.sw.sel{border-color:#fff}
.act{display:flex;gap:8px;margin:14px 0 30px}
.act button{flex:1;padding:14px;border:0;border-radius:12px;font-size:15px;color:#fff;background:#262634}
.act .go{background:#22c55e;color:#000;font-weight:700}
.act .del{background:#dc2626}
#toast{position:absolute;left:8px;right:8px;bottom:8px;background:#dc2626;padding:10px;border-radius:10px;font-size:13px;display:none;z-index:9}
.area{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.area button{padding:12px 4px;border:0;border-radius:10px;background:#262634;color:#fff;font-size:14px}
.area button.sel{background:#7c3aed}
</style></head><body>
<div id="wrap">
  <div id="bar">
    <span id="dot"></span>
    <button id="bEdit" title="Düzenle">✏️</button>
    <button id="bAdd" title="Ekle">＋</button>
    <button id="bSet" title="Ekran alanı">⚙️</button>
    <button id="bFull" title="Tam ekran">⛶</button>
  </div>
  <div id="grid"></div>
  <div id="modal"></div>
  <div id="toast"></div>
</div>
<script>
window.onerror = function(m, s, l){
  document.body.insertAdjacentHTML('beforeend', '<div style="position:fixed;top:0;left:0;right:0;background:#c00;color:#fff;padding:8px;font-size:12px;z-index:99">Hata: ' + m + ' (satir ' + l + ')</div>');
};
const K =new URLSearchParams(location.search).get('k') || '';
const $ = s => document.querySelector(s);
let items = [], editMode = false;
let view = {area:'bottom', size:60};
try { Object.assign(view, JSON.parse(localStorage.getItem('deck_view')||'{}')); } catch(e){}

const COLORS = ['#7c3aed','#2563eb','#0891b2','#059669','#65a30d','#d97706','#dc2626','#db2777','#475569'];
const APP_CHIPS = [
  ['Chrome','chrome','🌐'],['Not Defteri','notepad','📝'],['Hesap Mak.','calc','🧮'],
  ['Spotify','spotify:','🎵'],['Discord','discord://','💬'],['Steam','steam://open/main','🎮'],
  ['Görev Yön.','taskmgr','📊'],['Dosyalar','explorer','📁'],['Paint','mspaint','🎨']
];
const LINK_CHIPS = [['YouTube','youtube.com','▶️'],['Twitch','twitch.tv','🟣'],['Gmail','mail.google.com','✉️'],['WhatsApp','web.whatsapp.com','🟢']];
const KEY_CHIPS = [['Masaüstü','win+d','🖥'],['Pencere değiş','alt+tab','🔁'],['Ekran görüntüsü','win+shift+s','✂️'],['Görev Yön.','ctrl+shift+esc','📊'],['Kopyala','ctrl+c','📋'],['Yapıştır','ctrl+v','📌'],['Tam ekran','f11','⛶']];
const MEDIA_OPTS = [['playpause','⏯ Oynat/Durdur'],['next','⏭ Sonraki'],['prev','⏮ Önceki'],['volup','🔊 Ses +'],['voldown','🔉 Ses -'],['mute','🔇 Sessiz'],['stop','⏹ Durdur']];

function api(path, body){
  return fetch(path + (path.includes('?')?'&':'?') + 'k=' + encodeURIComponent(K),
    body===undefined ? {} : {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)})
    .then(r => r.json());
}
function toast(msg){
  const t = $('#toast'); t.textContent = msg; t.style.display='block';
  clearTimeout(toast.t); toast.t = setTimeout(()=>t.style.display='none', 2500);
}
function applyView(){
  const w = $('#wrap'), s = view.size + '%';
  w.style.cssText = '';
  const a = view.area;
  if (a==='full') { w.style.cssText = 'top:0;left:0;right:0;bottom:0'; }
  else if (a==='top') { w.style.cssText = `top:0;left:0;right:0;height:${s}`; }
  else if (a==='bottom') { w.style.cssText = `bottom:0;left:0;right:0;height:${s}`; }
  else if (a==='left') { w.style.cssText = `top:0;bottom:0;left:0;width:${s}`; }
  else if (a==='right') { w.style.cssText = `top:0;bottom:0;right:0;width:${s}`; }
}
function render(){
  const g = $('#grid'); g.innerHTML=''; g.className = editMode ? 'edit' : '';
  $('#bEdit').className = editMode ? 'on' : '';
  if (!items.length){ const e=document.createElement('div'); e.id='empty'; e.textContent='Boş. ＋ ile buton ekle.'; g.appendChild(e); }
  items.forEach((it, idx) => {
    const b = document.createElement('button'); b.className='b'; b.style.background = it.color || '#475569';
    const i = document.createElement('span'); i.className='i'; i.textContent = it.icon || '⭐';
    const n = document.createElement('span'); n.textContent = it.name || '';
    b.append(i, n);
    b.onclick = () => editMode ? openEdit(idx) : press(it, b);
    g.appendChild(b);
  });
}
async function press(it, el){
  if (navigator.vibrate) navigator.vibrate(25);
  el.classList.add('flash'); setTimeout(()=>el.classList.remove('flash'), 150);
  try {
    const r = await api('/api/run', {id: it.id});
    if (!r.ok) toast('Hata: ' + (r.error||'?'));
  } catch(e){ toast('PC\'ye ulaşılamadı'); }
}
function save(){ return api('/api/items', items).catch(()=>toast('Kaydedilemedi')); }

function openEdit(idx){
  const isNew = idx < 0;
  const it = isNew ? {id:'i'+Date.now(), name:'', icon:'⭐', color:COLORS[0], type:'app', value:''} : Object.assign({}, items[idx]);
  const m = $('#modal'); m.style.display='block'; m.scrollTop = 0;
  m.innerHTML = `<h3>${isNew?'Yeni buton':'Butonu düzenle'}</h3>
    <label>Tür</label>
    <select id="fT"><option value="app">Uygulama / dosya</option><option value="link">Web sitesi</option><option value="keys">Tuş kısayolu</option><option value="media">Medya / ses</option></select>
    <div id="chips" class="row" style="margin-top:8px"></div>
    <label id="fVL">Değer</label><div id="fVW"></div>
    <label>Ad</label><input id="fN" maxlength="20">
    <label>İkon (emoji)</label><input id="fI" maxlength="4">
    <label>Renk</label><div class="row" id="fC"></div>
    <div class="act">
      <button id="aC">İptal</button>
      ${isNew?'':'<button id="aL">◀</button><button id="aR">▶</button><button class="del" id="aD">Sil</button>'}
      <button class="go" id="aS">Kaydet</button>
    </div>`;
  $('#fT').value = it.type; $('#fN').value = it.name; $('#fI').value = it.icon;
  const sw = $('#fC');
  COLORS.forEach(c => { const s=document.createElement('button'); s.className='sw'+(c===it.color?' sel':''); s.style.background=c;
    s.onclick=()=>{ it.color=c; [...sw.children].forEach(x=>x.classList.remove('sel')); s.classList.add('sel'); }; sw.appendChild(s); });

  function drawValue(){
    const t = $('#fT').value, w = $('#fVW'), ch = $('#chips'); ch.innerHTML='';
    const L = $('#fVL');
    if (t==='media'){
      L.textContent='Hangisi';
      w.innerHTML = '<select id="fV">' + MEDIA_OPTS.map(o=>`<option value="${o[0]}">${o[1]}</option>`).join('') + '</select>';
      $('#fV').value = MEDIA_OPTS.some(o=>o[0]===it.value) ? it.value : 'playpause';
      return;
    }
    L.textContent = t==='app' ? 'Uygulama adı veya tam yol (örn. C:\\Program Files\\...\\x.exe)' : t==='link' ? 'Site adresi' : 'Kısayol (örn. ctrl+shift+m)';
    w.innerHTML = '<input id="fV" autocapitalize="off" autocomplete="off" spellcheck="false">';
    $('#fV').value = it.value;
    const list = t==='app'?APP_CHIPS : t==='link'?LINK_CHIPS : KEY_CHIPS;
    list.forEach(c => { const b=document.createElement('button'); b.className='chip'; b.textContent=c[2]+' '+c[0];
      b.onclick=()=>{ $('#fV').value=c[1]; if(!$('#fN').value) $('#fN').value=c[0]; if($('#fI').value==='⭐') $('#fI').value=c[2]; };
      ch.appendChild(b); });
  }
  $('#fT').onchange = () => { it.value=''; drawValue(); };
  drawValue();

  const close = () => { m.style.display='none'; };
  $('#aC').onclick = close;
  $('#aS').onclick = () => {
    it.type = $('#fT').value; it.value = $('#fV').value.trim(); it.name = $('#fN').value.trim(); it.icon = $('#fI').value.trim() || '⭐';
    if (!it.value){ toast('Değer boş'); return; }
    if (!it.name) it.name = it.value.slice(0,14);
    if (isNew) items.push(it); else items[idx] = it;
    save(); render(); close();
  };
  if (!isNew){
    $('#aD').onclick = () => { if (confirm('Silinsin mi?')){ items.splice(idx,1); save(); render(); close(); } };
    $('#aL').onclick = () => { if(idx>0){ [items[idx-1],items[idx]]=[items[idx],items[idx-1]]; save(); render(); close(); } };
    $('#aR').onclick = () => { if(idx<items.length-1){ [items[idx+1],items[idx]]=[items[idx],items[idx+1]]; save(); render(); close(); } };
  }
}

function openSettings(){
  const m = $('#modal'); m.style.display='block'; m.scrollTop=0;
  m.innerHTML = `<h3>Telefonun çalışan kısmı</h3>
    <div style="font-size:12px;opacity:.7;margin-bottom:8px">Ekranın hangi tarafı çalışıyorsa onu seç. Deck sadece orada görünür.</div>
    <div class="area" id="aA"></div>
    <label>Boyut: <b id="sz"></b>%</label>
    <input type="range" id="fS" min="30" max="100" step="5" style="width:100%;padding:0">
    <div class="act"><button class="go" id="aOK">Tamam</button></div>`;
  const names = [['top','⬆ Üst'],['bottom','⬇ Alt'],['full','⛶ Tam'],['left','⬅ Sol'],['right','➡ Sağ']];
  const A = $('#aA');
  names.forEach(n => { const b=document.createElement('button'); b.textContent=n[1]; if(view.area===n[0]) b.className='sel';
    b.onclick=()=>{ view.area=n[0]; [...A.children].forEach(x=>x.classList.remove('sel')); b.classList.add('sel'); applyView(); }; A.appendChild(b); });
  const S = $('#fS'); S.value = view.size; $('#sz').textContent = view.size;
  S.oninput = () => { view.size = +S.value; $('#sz').textContent = view.size; applyView(); };
  $('#aOK').onclick = () => { localStorage.setItem('deck_view', JSON.stringify(view)); m.style.display='none'; };
}

$('#bEdit').onclick = () => { editMode = !editMode; render(); };
$('#bAdd').onclick = () => openEdit(-1);
$('#bSet').onclick = openSettings;
$('#bFull').onclick = () => { const d=document.documentElement; (document.fullscreenElement ? document.exitFullscreen() : (d.requestFullscreen && d.requestFullscreen())); };

async function ping(){
  try { items = await api('/api/items'); $('#dot').className='ok'; if(!editMode && $('#modal').style.display!=='block') render(); }
  catch(e){ $('#dot').className=''; }
}
applyView(); ping(); setInterval(ping, 5000);
</script></body></html>
"""


def main():
    srv = None
    port = START_PORT
    for port in range(START_PORT, START_PORT + 20):
        try:
            srv = ThreadingHTTPServer(("0.0.0.0", port), H)
            break
        except OSError:
            continue
    if not srv:
        print("Boş port bulunamadı.")
        input("Kapatmak için Enter...")
        return
    url = "http://%s:%d/?k=%s" % (local_ip(), port, CONFIG["token"])
    print("=" * 60)
    print("  MINI STREAM DECK çalışıyor")
    print()
    print("  Telefonun tarayıcısına bunu yaz (aynı Wi-Fi'de olmalı):")
    print()
    print("      " + url)
    print()
    print("  Kapatmak için bu pencereyi kapat.")
    print("  Butonların ayarı: " + CFG)
    print("=" * 60)
    if IS_WIN:
        print("  Not: Windows güvenlik duvarı sorarsa 'Özel ağ'a izin ver.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
