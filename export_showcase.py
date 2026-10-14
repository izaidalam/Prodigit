import base64
import os
import shutil

def get_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

b64_emerald = get_b64('icon_emerald_chrono.png')
b64_swiss = get_b64('icon_swiss_mono.png')
b64_cyber = get_b64('icon_cyber_cyan.png')

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Prodigit - Desktop Icon Design Suite</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: #090B10;
      color: #E2E8F0;
    }}
    .font-mono-code {{
      font-family: monospace;
    }}
    #deviceFrame {{
      transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1), max-width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .active-concept-btn {{
      background: #2563EB !important;
      color: #FFFFFF !important;
      border-color: #3B82F6 !important;
      box-shadow: 0 0 15px rgba(37, 99, 235, 0.4) !important;
    }}
    .active-vp-btn {{
      background: #10B981 !important;
      color: #FFFFFF !important;
      border-color: #059669 !important;
    }}
    .glow-emerald {{
      box-shadow: 0 0 35px rgba(16, 185, 129, 0.3);
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- HEADER -->
  <header class="sticky top-0 z-50 bg-[#0F131D]/95 backdrop-blur-xl border-b border-slate-800 px-6 py-3 shadow-2xl">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
      
      <!-- Brand -->
      <div class="flex items-center gap-3 shrink-0">
        <img src="{b64_emerald}" class="w-9 h-9 rounded-xl shadow-lg border border-emerald-500/30" alt="Prodigit Icon">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-black text-white text-base tracking-wider">PRODIGIT</span>
            <span class="text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Desktop Icon Suite</span>
          </div>
          <p class="text-xs text-slate-400">Applied on Windows Desktop &middot; C:\\Users\\Zaid alam\\Desktop\\Prodigit.lnk</p>
        </div>
      </div>

      <!-- Concepts Switcher -->
      <div class="flex items-center gap-2 overflow-x-auto p-1 bg-slate-900/90 rounded-xl border border-slate-800 shadow-inner">
        <button onclick="switchConcept(1)" id="btn-c1" class="active-concept-btn px-3 py-1.5 rounded-lg text-xs font-semibold border border-transparent transition-all flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>1. Emerald Chrono (Active)</span>
        </button>
        <button onclick="switchConcept(2)" id="btn-c2" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 border border-transparent transition-all flex items-center gap-1.5">
          <span>2. Swiss Monochrome</span>
        </button>
        <button onclick="switchConcept(3)" id="btn-c3" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 border border-transparent transition-all flex items-center gap-1.5">
          <span>3. Cyber Cyan</span>
        </button>
        <button onclick="switchConcept('all')" id="btn-all" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 border border-transparent transition-all flex items-center gap-1.5">
          <span>Side-by-Side</span>
        </button>
      </div>

      <!-- Viewport Switcher -->
      <div class="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 shrink-0">
        <button onclick="setViewport('desktop')" id="vp-desktop" class="active-vp-btn px-3 py-1.5 rounded-lg text-xs font-semibold border border-transparent transition-all">
          💻 Desktop (1280px)
        </button>
        <button onclick="setViewport('tablet')" id="vp-tablet" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 border border-transparent transition-all">
          📱 Tablet (768px)
        </button>
        <button onclick="setViewport('mobile')" id="vp-mobile" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 border border-transparent transition-all">
          📱 Mobile (390px)
        </button>
      </div>

    </div>
  </header>

  <!-- WORKSPACE FRAME -->
  <main class="flex-1 flex flex-col items-center p-6 md:p-10">
    <div id="deviceFrame" class="w-full max-w-[1280px] bg-[#0E121B] rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col">
      
      <!-- Simulated Window Bar -->
      <div class="bg-[#161B26] px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full bg-rose-500/80"></div>
          <div class="w-3 h-3 rounded-full bg-amber-500/80"></div>
          <div class="w-3 h-3 rounded-full bg-emerald-500/80"></div>
          <span class="text-xs text-slate-400 font-mono-code ml-2">Windows Desktop &middot; Icon Simulation Frame</span>
        </div>
        <div id="resolutionTag" class="text-[11px] font-mono-code px-2 py-0.5 rounded bg-slate-800 text-slate-300">
          1280 &times; Desktop
        </div>
      </div>

      <!-- INNER CONTENT -->
      <div class="p-8 md:p-12 flex-1 flex flex-col gap-10">

        <!-- CONCEPT 1 VIEW -->
        <div id="concept-1" class="flex flex-col gap-8">
          <div class="flex flex-col md:flex-row items-center gap-8 justify-between bg-slate-900/60 p-6 md:p-8 rounded-2xl border border-emerald-500/20">
            <div class="flex items-center gap-6">
              <div class="relative group">
                <img src="{b64_emerald}" class="w-36 h-36 rounded-3xl shadow-2xl glow-emerald border border-emerald-500/40 transition-transform group-hover:scale-105 duration-300" alt="Concept 1">
                <span class="absolute -top-2 -right-2 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500 text-slate-950 uppercase shadow-md">Active Icon</span>
              </div>
              <div class="space-y-2">
                <h2 class="text-2xl font-bold text-white">Concept 1: Emerald Chrono</h2>
                <p class="text-sm text-slate-400 max-w-md">Dark glass obsidian squircle with vibrant emerald chronometer ring, precision tick hashmarks, and a bold geometric 'P' monogram featuring a central pulse dot.</p>
                <div class="flex flex-wrap gap-2 pt-2">
                  <span class="text-xs font-mono-code px-2.5 py-1 rounded-md bg-slate-800 text-emerald-400 border border-emerald-500/20">Multi-res ICO (256 - 16px)</span>
                  <span class="text-xs font-mono-code px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">Applied on Desktop</span>
                </div>
              </div>
            </div>

            <!-- Windows Desktop Simulated Shortcut Preview -->
            <div class="p-6 rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/60 border border-slate-800 flex flex-col items-center justify-center w-56 h-48 shadow-inner">
              <span class="text-[11px] text-slate-400 font-medium mb-3 uppercase tracking-wider">Desktop Shortcut Preview</span>
              <div class="flex flex-col items-center p-2 rounded-lg bg-blue-500/10 border border-blue-500/30 w-24 hover:bg-blue-500/20 transition-all cursor-pointer">
                <img src="{b64_emerald}" class="w-12 h-12 rounded-xl shadow-md" alt="Prodigit Desktop Icon">
                <span class="text-xs font-medium text-white mt-1.5 drop-shadow">Prodigit</span>
              </div>
            </div>
          </div>

          <!-- Mipmap Grid -->
          <div class="bg-slate-900/40 p-6 rounded-2xl border border-slate-800">
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Multi-Resolution Mipmap Rendering</h3>
            <div class="flex items-end gap-6 flex-wrap">
              <div class="flex flex-col items-center gap-2">
                <img src="{b64_emerald}" class="w-24 h-24 rounded-2xl shadow border border-slate-800" alt="96px">
                <span class="text-[11px] text-slate-400 font-mono-code">96px (Large)</span>
              </div>
              <div class="flex flex-col items-center gap-2">
                <img src="{b64_emerald}" class="w-16 h-16 rounded-xl shadow border border-slate-800" alt="64px">
                <span class="text-[11px] text-slate-400 font-mono-code">64px (Medium)</span>
              </div>
              <div class="flex flex-col items-center gap-2">
                <img src="{b64_emerald}" class="w-12 h-12 rounded-lg shadow border border-slate-800" alt="48px">
                <span class="text-[11px] text-slate-400 font-mono-code">48px (Desktop Default)</span>
              </div>
              <div class="flex flex-col items-center gap-2">
                <img src="{b64_emerald}" class="w-8 h-8 rounded-md shadow border border-slate-800" alt="32px">
                <span class="text-[11px] text-slate-400 font-mono-code">32px (Taskbar)</span>
              </div>
              <div class="flex flex-col items-center gap-2">
                <img src="{b64_emerald}" class="w-5 h-5 rounded-sm shadow border border-slate-800" alt="16px">
                <span class="text-[11px] text-slate-400 font-mono-code">16px (Small)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- CONCEPT 2 VIEW -->
        <div id="concept-2" class="hidden flex-col gap-8">
          <div class="flex flex-col md:flex-row items-center gap-8 justify-between bg-slate-900/60 p-6 md:p-8 rounded-2xl border border-white/20">
            <div class="flex items-center gap-6">
              <img src="{b64_swiss}" class="w-36 h-36 rounded-3xl shadow-2xl border border-white/40 transition-transform hover:scale-105 duration-300" alt="Concept 2">
              <div class="space-y-2">
                <h2 class="text-2xl font-bold text-white">Concept 2: Swiss Monochrome</h2>
                <p class="text-sm text-slate-400 max-w-md">Pure obsidian jet black with high-contrast crisp white hairline chamfer. Matches Prodigit's minimalist Swiss Monochrome dark UI theme.</p>
                <div class="flex flex-wrap gap-2 pt-2">
                  <span class="text-xs font-mono-code px-2.5 py-1 rounded-md bg-slate-800 text-slate-200 border border-slate-700">Multi-res ICO (256 - 16px)</span>
                  <span class="text-xs font-mono-code px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-800">Available in project</span>
                </div>
              </div>
            </div>

            <div class="p-6 rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/60 border border-slate-800 flex flex-col items-center justify-center w-56 h-48 shadow-inner">
              <span class="text-[11px] text-slate-400 font-medium mb-3 uppercase tracking-wider">Desktop Shortcut Preview</span>
              <div class="flex flex-col items-center p-2 rounded-lg bg-blue-500/10 border border-blue-500/30 w-24 hover:bg-blue-500/20 transition-all cursor-pointer">
                <img src="{b64_swiss}" class="w-12 h-12 rounded-xl shadow-md" alt="Swiss Icon">
                <span class="text-xs font-medium text-white mt-1.5 drop-shadow">Prodigit</span>
              </div>
            </div>
          </div>
        </div>

        <!-- CONCEPT 3 VIEW -->
        <div id="concept-3" class="hidden flex-col gap-8">
          <div class="flex flex-col md:flex-row items-center gap-8 justify-between bg-slate-900/60 p-6 md:p-8 rounded-2xl border border-cyan-500/20">
            <div class="flex items-center gap-6">
              <img src="{b64_cyber}" class="w-36 h-36 rounded-3xl shadow-2xl border border-cyan-500/40 transition-transform hover:scale-105 duration-300" alt="Concept 3">
              <div class="space-y-2">
                <h2 class="text-2xl font-bold text-white">Concept 3: Cyber Cyan Pulse</h2>
                <p class="text-sm text-slate-400 max-w-md">Deep midnight navy canvas with high-energy electric cyan ring and purple pulse accent dot. Futuristic, neon cyberpunk productivity vibe.</p>
                <div class="flex flex-wrap gap-2 pt-2">
                  <span class="text-xs font-mono-code px-2.5 py-1 rounded-md bg-slate-800 text-cyan-400 border border-cyan-500/20">Multi-res ICO (256 - 16px)</span>
                  <span class="text-xs font-mono-code px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-800">Available in project</span>
                </div>
              </div>
            </div>

            <div class="p-6 rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/60 border border-slate-800 flex flex-col items-center justify-center w-56 h-48 shadow-inner">
              <span class="text-[11px] text-slate-400 font-medium mb-3 uppercase tracking-wider">Desktop Shortcut Preview</span>
              <div class="flex flex-col items-center p-2 rounded-lg bg-blue-500/10 border border-blue-500/30 w-24 hover:bg-blue-500/20 transition-all cursor-pointer">
                <img src="{b64_cyber}" class="w-12 h-12 rounded-xl shadow-md" alt="Cyber Cyan Icon">
                <span class="text-xs font-medium text-white mt-1.5 drop-shadow">Prodigit</span>
              </div>
            </div>
          </div>
        </div>

        <!-- SIDE-BY-SIDE VIEW -->
        <div id="concept-all" class="hidden grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="p-6 rounded-2xl bg-slate-900/60 border border-emerald-500/30 flex flex-col items-center text-center gap-4">
            <span class="text-[11px] font-bold text-emerald-400 uppercase tracking-widest">Concept 1 (Active)</span>
            <img src="{b64_emerald}" class="w-24 h-24 rounded-2xl shadow-lg border border-emerald-500/40" alt="C1">
            <h4 class="text-base font-bold text-white">Emerald Chrono</h4>
            <p class="text-xs text-slate-400">Currently set on Desktop Shortcut &amp; Window</p>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/60 border border-white/20 flex flex-col items-center text-center gap-4">
            <span class="text-[11px] font-bold text-slate-300 uppercase tracking-widest">Concept 2</span>
            <img src="{b64_swiss}" class="w-24 h-24 rounded-2xl shadow-lg border border-white/40" alt="C2">
            <h4 class="text-base font-bold text-white">Swiss Monochrome</h4>
            <p class="text-xs text-slate-400">Pure black &amp; white high-contrast aesthetic</p>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/60 border border-cyan-500/30 flex flex-col items-center text-center gap-4">
            <span class="text-[11px] font-bold text-cyan-400 uppercase tracking-widest">Concept 3</span>
            <img src="{b64_cyber}" class="w-24 h-24 rounded-2xl shadow-lg border border-cyan-500/40" alt="C3">
            <h4 class="text-base font-bold text-white">Cyber Cyan Pulse</h4>
            <p class="text-xs text-slate-400">Electric cyan and neon violet glow</p>
          </div>
        </div>

      </div>
    </div>
  </main>

  <script>
    function switchConcept(id) {{
      const c1 = document.getElementById('concept-1');
      const c2 = document.getElementById('concept-2');
      const c3 = document.getElementById('concept-3');
      const call = document.getElementById('concept-all');

      const b1 = document.getElementById('btn-c1');
      const b2 = document.getElementById('btn-c2');
      const b3 = document.getElementById('btn-c3');
      const ball = document.getElementById('btn-all');

      [c1, c2, c3, call].forEach(el => {{ el.classList.add('hidden'); el.classList.remove('flex', 'grid'); }});
      [b1, b2, b3, ball].forEach(btn => btn.classList.remove('active-concept-btn'));

      if (id === 1) {{
        c1.classList.remove('hidden');
        c1.classList.add('flex');
        b1.classList.add('active-concept-btn');
      }} else if (id === 2) {{
        c2.classList.remove('hidden');
        c2.classList.add('flex');
        b2.classList.add('active-concept-btn');
      }} else if (id === 3) {{
        c3.classList.remove('hidden');
        c3.classList.add('flex');
        b3.classList.add('active-concept-btn');
      }} else {{
        call.classList.remove('hidden');
        call.classList.add('grid');
        ball.classList.add('active-concept-btn');
      }}
    }}

    function setViewport(mode) {{
      const frame = document.getElementById('deviceFrame');
      const tag = document.getElementById('resolutionTag');
      const vpDesk = document.getElementById('vp-desktop');
      const vpTab = document.getElementById('vp-tablet');
      const vpMob = document.getElementById('vp-mobile');

      [vpDesk, vpTab, vpMob].forEach(b => b.classList.remove('active-vp-btn'));

      if (mode === 'desktop') {{
        frame.style.maxWidth = '1280px';
        frame.style.width = '100%';
        tag.innerText = '1280 × Desktop';
        vpDesk.classList.add('active-vp-btn');
      }} else if (mode === 'tablet') {{
        frame.style.maxWidth = '768px';
        frame.style.width = '100%';
        tag.innerText = '768 × Tablet';
        vpTab.classList.add('active-vp-btn');
      }} else if (mode === 'mobile') {{
        frame.style.maxWidth = '390px';
        frame.style.width = '100%';
        tag.innerText = '390 × Mobile';
        vpMob.classList.add('active-vp-btn');
      }}
    }}
  </script>
</body>
</html>'''

with open('prodigit_desktop_icon_showcase.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

downloads_path = r'C:\Users\Zaid alam\Downloads\prodigit_desktop_icon_showcase.html'
shutil.copy('prodigit_desktop_icon_showcase.html', downloads_path)
print('Exported to Downloads folder successfully:', downloads_path)
