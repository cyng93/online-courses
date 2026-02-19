#!/usr/bin/env python3
"""Generate HTML one-pager from transcripts.json + course.json.

Usage: python3 generate_pages.py /path/to/course-dir
  Reads course.json for metadata, YouTube IDs, summaries, chapters.
  Reads step4-input/transcripts.json for transcript data.
  Writes HTML to step4-output/{course_id}.html
"""

import json
import sys
from datetime import date
from pathlib import Path


def load_config(course_dir: Path) -> tuple[dict, dict]:
    """Load course config and transcript data."""
    config_path = course_dir / "course.json"
    if not config_path.exists():
        print(f"ERROR: course.json not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))

    transcripts_path = course_dir / "step4-input" / "transcripts.json"
    if not transcripts_path.exists():
        print(f"ERROR: transcripts.json not found at {transcripts_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(transcripts_path.read_text(encoding="utf-8"))
    return config, data


def build_yt_id_map(config: dict) -> dict[str, str]:
    """Build video_id -> youtube_id mapping from config."""
    return {v["id"]: v.get("youtube_id", "") for v in config["videos"]}


def yt_url(video_id: str, yt_ids: dict, playlist_id: str) -> str:
    """Build YouTube URL with playlist context."""
    yt_id = yt_ids.get(video_id, "")
    if not yt_id:
        return ""
    return f"https://www.youtube.com/watch?v={yt_id}&list={playlist_id}"


def generate_html(config: dict, data: dict) -> str:
    playlist_id = config["playlist_id"]
    yt_ids = build_yt_id_map(config)
    summaries = config.get("summaries", {})
    chapters = config.get("chapters", {})

    videos_html = []
    toc_html = []
    sidebar_toc_html = []
    current_chapter = None

    for v in data["videos"]:
        vid = v["id"]
        anchor = f"video-{vid}"
        toc_html.append(f'<li><a href="#{anchor}">{v["full_title"]}</a></li>')

        # Build sidebar TOC with chapter grouping
        chapter = vid.split("-")[0]
        if chapter != current_chapter:
            if current_chapter is not None:
                sidebar_toc_html.append('</ul>')
            chapter_name = chapters.get(chapter, f"第 {chapter} 章")
            sidebar_toc_html.append(f'<div class="sidebar-chapter">{chapter_name}</div>')
            sidebar_toc_html.append('<ul>')
            current_chapter = chapter
        sidebar_toc_html.append(
            f'<li><a href="#{anchor}" data-target="{anchor}">{v["full_title"]}</a></li>'
        )

        summary = summaries.get(vid, "")
        transcript_paras = "\n".join(f"<p>{line}</p>" for line in v["lines"])
        yt_id = yt_ids.get(vid, "")
        yt_embed = ""
        if yt_id:
            yt_embed = f"""<div class="yt-thumb" onclick="loadVideo(this, '{yt_id}')" data-yt="{yt_id}">
        <img src="https://img.youtube.com/vi/{yt_id}/hqdefault.jpg" alt="{v['full_title']}" loading="lazy">
        <span class="yt-play">▶</span>
      </div>"""

        videos_html.append(f"""
    <section class="video-section" id="{anchor}">
      <h2>{v["full_title"]}</h2>
      <p class="summary">{summary}</p>
      <p class="meta">字幕數：{v["entry_count"]}</p>
      {yt_embed}
      <details>
        <summary>展開完整逐字稿</summary>
        <div class="transcript">{transcript_paras}</div>
      </details>
    </section>""")

    if current_chapter is not None:
        sidebar_toc_html.append('</ul>')

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data["course_title"]} — 完整逐字稿</title>
<style>
:root {{
  --bg: #fafafa;
  --fg: #1a1a1a;
  --bg-card: #ffffff;
  --border: #e0e0e0;
  --accent: #2563eb;
  --accent-light: #dbeafe;
  --summary-bg: #f0f7ff;
  --summary-border: #93c5fd;
  --meta: #6b7280;
  --search-highlight: #fef08a;
  --font-size: 1rem;
  --line-height: 1.8;
  --letter-spacing: 0;
}}
[data-theme="dark"] {{
  --bg: #111827;
  --fg: #f3f4f6;
  --bg-card: #1f2937;
  --border: #374151;
  --accent: #60a5fa;
  --accent-light: #1e3a5f;
  --summary-bg: #1e293b;
  --summary-border: #3b82f6;
  --meta: #9ca3af;
  --search-highlight: #854d0e;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", "Microsoft JhengHei", sans-serif;
  background: var(--bg);
  color: var(--fg);
  font-size: var(--font-size);
  line-height: var(--line-height);
  letter-spacing: var(--letter-spacing);
  transition: background 0.3s, color 0.3s, font-size 0.2s, line-height 0.2s;
}}
.container {{
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}}
header {{
  text-align: center;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--border);
}}
header h1 {{
  font-size: 2rem;
  margin-bottom: 0.5rem;
}}
header .meta-info {{
  color: var(--meta);
  font-size: inherit;
}}
.toolbar {{
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}}
.toolbar input {{
  flex: 1;
  min-width: 200px;
  padding: 0.6rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1rem;
  background: var(--bg-card);
  color: var(--fg);
  outline: none;
}}
.toolbar input:focus {{
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}}
.toolbar button {{
  padding: 0.6rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--fg);
  cursor: pointer;
  font-size: 0.95rem;
  white-space: nowrap;
}}
.toolbar button:hover {{
  border-color: var(--accent);
}}
nav.toc {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}}
nav.toc h3 {{
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}}
nav.toc ol {{
  padding-left: 1.5rem;
}}
nav.toc li {{
  margin-bottom: 0.3rem;
}}
nav.toc a {{
  color: var(--accent);
  text-decoration: none;
}}
nav.toc a:hover {{
  text-decoration: underline;
}}
.video-section {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}}
.video-section h2 {{
  font-size: 1.35rem;
  margin-bottom: 0.75rem;
  color: var(--accent);
}}
.summary {{
  background: var(--summary-bg);
  border-left: 4px solid var(--summary-border);
  padding: 0.75rem 1rem;
  border-radius: 0 8px 8px 0;
  margin-bottom: 0.75rem;
  font-size: inherit;
}}
.meta {{
  color: var(--meta);
  font-size: inherit;
  margin-bottom: 0.5rem;
}}
.yt-thumb {{
  display: block;
  position: relative;
  max-width: 640px;
  margin: 0.75rem 0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}}
.yt-thumb:hover {{
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
}}
.yt-thumb img {{
  display: block;
  width: 100%;
  height: auto;
}}
.yt-play {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 68px;
  height: 48px;
  background: rgba(255, 0, 0, 0.85);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  color: #fff;
  pointer-events: none;
  transition: background 0.2s;
}}
.yt-thumb:hover .yt-play {{
  background: rgba(255, 0, 0, 1);
}}
.video-container {{
  position: relative;
  max-width: 640px;
  margin: 0.75rem 0;
  padding-bottom: min(360px, 56.25%);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}}
.video-container iframe {{
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  border: 0;
}}
details {{
  margin-top: 0.5rem;
}}
details summary {{
  cursor: pointer;
  color: var(--accent);
  font-weight: 500;
  padding: 0.4rem 0;
  user-select: none;
}}
details summary:hover {{
  text-decoration: underline;
}}
.transcript {{
  margin-top: 0.75rem;
  padding: 1rem;
  background: var(--bg);
  border-radius: 8px;
  font-size: inherit;
  line-height: inherit;
}}
.transcript.scrollable {{
  max-height: 60vh;
  overflow-y: auto;
  scroll-behavior: smooth;
}}
.hidden {{
  display: none !important;
}}
mark {{
  background: var(--search-highlight);
  color: inherit;
  padding: 0 2px;
  border-radius: 2px;
}}
footer {{
  text-align: center;
  padding: 2rem 0 1rem;
  color: var(--meta);
  font-size: 0.85rem;
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}}
.expand-controls {{
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}}
.expand-controls button {{
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--fg);
  cursor: pointer;
  font-size: 0.85rem;
}}
.expand-controls button:hover {{
  border-color: var(--accent);
}}
.font-controls {{
  display: flex;
  gap: 0.4rem;
  align-items: center;
  flex-wrap: wrap;
}}
.font-controls button {{
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--fg);
  cursor: pointer;
  font-size: 0.95rem;
  white-space: nowrap;
}}
.font-controls button:hover {{
  border-color: var(--accent);
}}
.font-controls button.active {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}
.font-controls .size-label {{
  font-size: 0.85rem;
  color: var(--meta);
  min-width: 2.5rem;
  text-align: center;
}}
@media (max-width: 600px) {{
  .container {{ padding: 1rem; }}
  header h1 {{ font-size: 1.5rem; }}
  .toolbar {{ flex-direction: column; }}
  .toolbar input {{ min-width: 100%; }}
  .font-controls {{ justify-content: center; }}
}}

/* Floating TOC Sidebar */
#floating-toc {{
  position: fixed;
  top: 0;
  left: 0;
  width: 260px;
  height: 100vh;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 1.25rem 1rem;
  z-index: 1000;
  transition: transform 0.3s ease, background 0.3s;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}}
#floating-toc::-webkit-scrollbar {{
  width: 4px;
}}
#floating-toc::-webkit-scrollbar-track {{
  background: transparent;
}}
#floating-toc::-webkit-scrollbar-thumb {{
  background: var(--border);
  border-radius: 2px;
}}
#floating-toc .sidebar-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
}}
#floating-toc .sidebar-header h3 {{
  font-size: 1rem;
  margin: 0;
}}
#floating-toc .sidebar-close {{
  background: none;
  border: none;
  color: var(--meta);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.2rem;
  line-height: 1;
}}
#floating-toc .sidebar-close:hover {{
  color: var(--fg);
}}
.sidebar-chapter {{
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--meta);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.75rem;
  margin-bottom: 0.25rem;
  padding-left: 0.5rem;
}}
#floating-toc ul {{
  list-style: none;
  padding: 0;
  margin: 0 0 0.25rem 0;
}}
#floating-toc li a {{
  display: block;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  color: var(--fg);
  text-decoration: none;
  font-size: 0.82rem;
  line-height: 1.4;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
#floating-toc li a:hover {{
  background: var(--accent-light);
  color: var(--accent);
}}
#floating-toc li a.active {{
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 600;
}}

/* Toggle button */
#toc-toggle {{
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 1001;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--fg);
  cursor: pointer;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: background 0.3s, transform 0.3s;
}}
#toc-toggle:hover {{
  border-color: var(--accent);
}}

/* Body shift when sidebar is open */
body.sidebar-open {{
  margin-left: 260px;
  transition: margin-left 0.3s ease;
}}
body {{
  transition: margin-left 0.3s ease;
}}

/* Hide sidebar when closed */
#floating-toc.closed {{
  transform: translateX(-100%);
}}
body.sidebar-open #toc-toggle {{
  left: 268px;
}}

/* Responsive: hide sidebar on narrow screens */
@media (max-width: 1200px) {{
  #floating-toc {{
    transform: translateX(-100%);
    box-shadow: 2px 0 16px rgba(0,0,0,0.15);
  }}
  #floating-toc.mobile-open {{
    transform: translateX(0);
  }}
  body.sidebar-open {{
    margin-left: 0;
  }}
  body.sidebar-open #toc-toggle {{
    left: 1rem;
  }}
  #toc-toggle {{
    display: flex;
  }}
}}
@media (min-width: 1201px) {{
  /* On wide screens, sidebar is open by default */
  #floating-toc {{
    transform: translateX(0);
  }}
  #floating-toc.closed {{
    transform: translateX(-100%);
  }}
}}
</style>
</head>
<body>
<button id="toc-toggle" onclick="toggleSidebar()" title="目錄">☰</button>
<aside id="floating-toc">
  <div class="sidebar-header">
    <h3>目錄</h3>
    <button class="sidebar-close" onclick="toggleSidebar()" title="關閉目錄">✕</button>
  </div>
  {"".join(sidebar_toc_html)}
</aside>
<div class="container">
  <header>
    <h1>{data["course_title"]}</h1>
    <div class="meta-info">
      講師：{data["author"]} ・ 共 {data["total_videos"]} 支影片 ・ 生成日期：{date.today().isoformat()}
    </div>
  </header>

  <div class="toolbar">
    <input type="text" id="search" placeholder="搜尋逐字稿內容..." autocomplete="off">
    <button onclick="clearSearch()">清除</button>
    <button onclick="toggleTheme()" id="theme-btn">🌙 深色模式</button>
  </div>

  <div class="expand-controls">
    <button onclick="expandAll()">全部展開</button>
    <button onclick="collapseAll()">全部收合</button>
    <span style="margin-left: auto;"></span>
    <div class="font-controls">
      <button onclick="changeFontSize(-1)" title="縮小字體">A-</button>
      <span class="size-label" id="size-label">M</span>
      <button onclick="changeFontSize(1)" title="放大字體">A+</button>
      <button onclick="toggleEyeFriendly()" id="eye-btn">👁 護眼模式</button>
    </div>
  </div>

  <nav class="toc">
    <h3>目錄</h3>
    <ol>
      {"".join(toc_html)}
    </ol>
  </nav>

  {"".join(videos_html)}

  <footer>
    {data["course_title"]} — {data["author"]} ・ 逐字稿由 AI 視覺辨識燒入字幕提取
  </footer>
</div>

<script>
// Click-to-load YouTube player (replaces thumbnail with iframe)
function loadVideo(el, ytId) {{
  const container = document.createElement('div');
  container.className = 'video-container';
  container.innerHTML = '<iframe width="560" height="315"'
    + ' src="https://www.youtube.com/embed/' + ytId + '?autoplay=1"'
    + ' title="YouTube video player" frameborder="0"'
    + ' allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"'
    + ' referrerpolicy="strict-origin-when-cross-origin"'
    + ' allowfullscreen></iframe>';
  el.replaceWith(container);
  // Auto-expand transcript and make it scrollable
  const section = container.closest('.video-section');
  if (section) {{
    const details = section.querySelector('details');
    const transcript = section.querySelector('.transcript');
    if (details) details.open = true;
    if (transcript) transcript.classList.add('scrollable');
  }}
}}

// Dark mode toggle
function toggleTheme() {{
  const body = document.documentElement;
  const current = body.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  body.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  document.getElementById('theme-btn').textContent =
    next === 'dark' ? '☀️ 淺色模式' : '🌙 深色模式';
}}

// Restore theme
(function() {{
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {{
    document.documentElement.setAttribute('data-theme', 'dark');
    document.addEventListener('DOMContentLoaded', () => {{
      document.getElementById('theme-btn').textContent = '☀️ 淺色模式';
    }});
  }}
}})();

// Search
const searchInput = document.getElementById('search');
let searchTimeout;
searchInput.addEventListener('input', () => {{
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(doSearch, 300);
}});

function doSearch() {{
  const query = searchInput.value.trim().toLowerCase();
  const sections = document.querySelectorAll('.video-section');

  // Clear previous highlights
  document.querySelectorAll('mark').forEach(m => {{
    m.replaceWith(m.textContent);
  }});

  if (!query) {{
    sections.forEach(s => s.classList.remove('hidden'));
    return;
  }}

  sections.forEach(section => {{
    const text = section.textContent.toLowerCase();
    if (text.includes(query)) {{
      section.classList.remove('hidden');
      // Open details if match is in transcript
      const details = section.querySelector('details');
      const transcript = section.querySelector('.transcript');
      if (transcript && transcript.textContent.toLowerCase().includes(query)) {{
        details.open = true;
        highlightText(transcript, query);
      }}
      // Also highlight in summary
      const summary = section.querySelector('.summary');
      if (summary && summary.textContent.toLowerCase().includes(query)) {{
        highlightText(summary, query);
      }}
    }} else {{
      section.classList.add('hidden');
    }}
  }});
}}

function highlightText(el, query) {{
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(node => {{
    const idx = node.textContent.toLowerCase().indexOf(query);
    if (idx >= 0) {{
      const span = document.createElement('span');
      span.innerHTML = node.textContent.substring(0, idx)
        + '<mark>' + node.textContent.substring(idx, idx + query.length) + '</mark>'
        + node.textContent.substring(idx + query.length);
      node.replaceWith(span);
    }}
  }});
}}

function clearSearch() {{
  searchInput.value = '';
  doSearch();
}}

function expandAll() {{
  document.querySelectorAll('details').forEach(d => d.open = true);
}}

function collapseAll() {{
  document.querySelectorAll('details').forEach(d => d.open = false);
}}

// Font size control
const SIZES = [
  {{ label: 'XS', size: '0.85rem', line: '1.6', spacing: '0' }},
  {{ label: 'S',  size: '0.95rem', line: '1.8', spacing: '0' }},
  {{ label: 'M',  size: '1rem',    line: '1.8', spacing: '0' }},
  {{ label: 'L',  size: '1.15rem', line: '2.0', spacing: '0.02em' }},
  {{ label: 'XL', size: '1.3rem',  line: '2.2', spacing: '0.03em' }},
  {{ label: '2XL', size: '1.5rem', line: '2.4', spacing: '0.04em' }},
];
let currentSizeIdx = parseInt(localStorage.getItem('fontSizeIdx') || '2');
let eyeFriendly = localStorage.getItem('eyeFriendly') === 'true';
let preEyeTheme = localStorage.getItem('preEyeTheme') || 'light';
let preEyeSizeIdx = parseInt(localStorage.getItem('preEyeSizeIdx') || '2');

function applyFontSize() {{
  const s = SIZES[currentSizeIdx];
  const root = document.documentElement;
  root.style.setProperty('--font-size', s.size);
  root.style.setProperty('--line-height', s.line);
  root.style.setProperty('--letter-spacing', s.spacing);
  document.getElementById('size-label').textContent = s.label;
  localStorage.setItem('fontSizeIdx', currentSizeIdx);
}}

function changeFontSize(delta) {{
  currentSizeIdx = Math.max(0, Math.min(SIZES.length - 1, currentSizeIdx + delta));
  applyFontSize();
}}

function toggleEyeFriendly() {{
  eyeFriendly = !eyeFriendly;
  applyEyeFriendly();
}}

function applyEyeFriendly() {{
  const btn = document.getElementById('eye-btn');
  if (eyeFriendly) {{
    // Save current state before switching
    preEyeTheme = document.documentElement.getAttribute('data-theme') || 'light';
    preEyeSizeIdx = currentSizeIdx;
    localStorage.setItem('preEyeTheme', preEyeTheme);
    localStorage.setItem('preEyeSizeIdx', preEyeSizeIdx);
    // Jump to at least L size
    if (currentSizeIdx < 3) currentSizeIdx = 3;
    applyFontSize();
    document.documentElement.setAttribute('data-theme', 'dark');
    document.getElementById('theme-btn').textContent = '☀️ 淺色模式';
    localStorage.setItem('theme', 'dark');
    btn.textContent = '👁 護眼開啟';
    btn.classList.add('active');
  }} else {{
    // Restore previous theme
    const restoreTheme = preEyeTheme || 'light';
    document.documentElement.setAttribute('data-theme', restoreTheme);
    document.getElementById('theme-btn').textContent =
      restoreTheme === 'dark' ? '☀️ 淺色模式' : '🌙 深色模式';
    localStorage.setItem('theme', restoreTheme);
    // Restore previous font size
    currentSizeIdx = preEyeSizeIdx;
    applyFontSize();
    btn.textContent = '👁 護眼模式';
    btn.classList.remove('active');
  }}
  localStorage.setItem('eyeFriendly', eyeFriendly);
}}

// Floating TOC Sidebar
function toggleSidebar() {{
  const sidebar = document.getElementById('floating-toc');
  const isWide = window.innerWidth > 1200;

  if (isWide) {{
    sidebar.classList.toggle('closed');
    document.body.classList.toggle('sidebar-open');
    localStorage.setItem('sidebarOpen', !sidebar.classList.contains('closed'));
  }} else {{
    sidebar.classList.toggle('mobile-open');
  }}
}}

// Active section tracking with IntersectionObserver
function initSidebarObserver() {{
  const sidebarLinks = document.querySelectorAll('#floating-toc a[data-target]');
  const sections = document.querySelectorAll('.video-section');

  if (!sections.length) return;

  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        // Remove active from all links
        sidebarLinks.forEach(link => link.classList.remove('active'));
        // Add active to matching link
        const target = entry.target.id;
        const activeLink = document.querySelector(
          `#floating-toc a[data-target="${{target}}"]`
        );
        if (activeLink) {{
          activeLink.classList.add('active');
          // Auto-scroll sidebar to keep active link visible
          activeLink.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
        }}
      }}
    }});
  }}, {{
    rootMargin: '-10% 0px -80% 0px',
    threshold: 0
  }});

  sections.forEach(section => observer.observe(section));
}}

// Sidebar click handler: smooth scroll + close on mobile
document.getElementById('floating-toc').addEventListener('click', (e) => {{
  const link = e.target.closest('a[data-target]');
  if (!link) return;
  e.preventDefault();
  const target = document.getElementById(link.dataset.target);
  if (target) {{
    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
  // Close sidebar on mobile after click
  if (window.innerWidth <= 1200) {{
    document.getElementById('floating-toc').classList.remove('mobile-open');
  }}
}});

// Restore on load
document.addEventListener('DOMContentLoaded', () => {{
  applyFontSize();
  if (eyeFriendly) applyEyeFriendly();

  // Restore sidebar state (desktop only)
  const isWide = window.innerWidth > 1200;
  const sidebarPref = localStorage.getItem('sidebarOpen');
  const sidebar = document.getElementById('floating-toc');
  if (isWide) {{
    if (sidebarPref === 'false') {{
      sidebar.classList.add('closed');
    }} else {{
      document.body.classList.add('sidebar-open');
    }}
  }}

  // Init observer
  initSidebarObserver();
}});
</script>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_pages.py /path/to/course-dir", file=sys.stderr)
        sys.exit(1)

    course_dir = Path(sys.argv[1]).resolve()
    config, data = load_config(course_dir)

    course_id = config["course_id"]
    out_dir = course_dir / "step4-output"
    out_dir.mkdir(parents=True, exist_ok=True)

    html = generate_html(config, data)
    html_path = out_dir / f"{course_id}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"Wrote {html_path} ({len(html):,} chars)")


if __name__ == "__main__":
    main()
