#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI教学文本 -> 精美HTML教学PPT 生成器（v5 - 稳定版）
修复：正确处理TOC和重复section headings
"""
import json, os, re, sys
from datetime import datetime
from pathlib import Path

def find_htmlppt_assets():
    candidates = [
        Path.home() / ".codex" / "skills" / "html-ppt" / "assets",
        Path(os.environ.get("CODEX_HOME", "")) / "skills" / "html-ppt" / "assets",
 
    ]
    for p in candidates:
        if (p / "themes").is_dir() and (p / "runtime.js").exists():
            return p.resolve()
    raise FileNotFoundError("html-ppt assets not found")

SKILL_ASSETS = find_htmlppt_assets()
ALL_THEMES = ["academic-paper","aurora","bauhaus","blueprint","catppuccin-mocha",
    "corporate-clean","cyberpunk-neon","dracula","editorial-serif","glassmorphism",
    "japanese-minimal","magazine-bold","memphis-pop","midcentury","minimal-white",
    "neo-brutalism","news-broadcast","nord","pitch-deck-vc","rainbow-gradient",
    "retro-tv","rose-pine","sharp-mono","soft-pastel","solarized-light","sunset-warm",
    "swiss-grid","terminal-green","tokyo-night","vaporwave","xiaohongshu-white",
    "y2k-chrome","engineering-whiteprint","gruvbox-dark","catppuccin-latte"]
DEFAULT_THEME = "tokyo-night"

def escape_html(text):
    return text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def is_decorative(s):
    return bool(re.match(r'^[=\-*]{3,}$', s.strip()))

def parse_md(text):
    lines = text.strip().split("\n")
    deck_title = "AI教学课程"
    
    # Find deck title (first non-decorative line)
    for raw in lines:
        s = raw.strip()
        if s and not is_decorative(s) and not s.startswith("目录") and not s.startswith("END"):
            deck_title = s.strip("*# \t")
            break
    
    # ---- Build list of REAL section headings ----
    # Strategy: find lines that are between === markers OR start with ##
    # Skip the table of contents section
    
    in_toc = False
    real_sections = []  # (line_idx, heading_text)
    seen_headings = set()
    
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        
        if not stripped:
            i += 1
            continue
        
        # Detect TOC
        if stripped == "目录：" or stripped.startswith("目录"):
            in_toc = True
            i += 1
            continue
        if is_decorative(stripped):
            in_toc = False
            i += 1
            continue
        
        # ## format heading
        if raw.startswith("## "):
            h = raw[3:].strip()
            if h and h not in seen_headings:
                real_sections.append((i, h))
                seen_headings.add(h)
            i += 1
            continue
        
        # === format: section headings between === markers
        # Find if this line is a Chinese numbered heading immediately after === or blank
        if re.match(r'^[一二三四五六七八九十]+[、\.\)]\s*\S', stripped):
            prev_dec = False
            for j in range(i-1, -1, -1):
                p = lines[j].strip()
                if is_decorative(p):
                    prev_dec = True
                    break
                if p:
                    break
            if prev_dec and not in_toc:
                if stripped not in seen_headings:
                    real_sections.append((i, stripped))
                    seen_headings.add(stripped)
                i += 1
                continue
        
        i += 1
    
    # If no sections by ===, try consecutive blank-line-separated headings
    if not real_sections:
        for i, raw in enumerate(lines):
            s = raw.strip()
            if raw.startswith("## "):
                real_sections.append((i, raw[3:].strip()))
            elif re.match(r'^[一二三四五六七八九十]+[、\.\)]\s*\S', s) and i > 0 and lines[i-1].strip() == "":
                real_sections.append((i, s))
    
    # If STILL no sections, make one slide
    if not real_sections:
        body = [{"type":"text","text":l.strip()} for l in lines if l.strip() and not is_decorative(l)]
        return {"title":deck_title, "slides":[{"title":deck_title,"type":"cover","body":body[:10]}]}
    
    # ---- Build slides from sections ----
    slides = []
    
    # Add cover slide from pre-section lines
    cover_body = []
    first_section_idx = real_sections[0][0]
    for raw in lines[:first_section_idx]:
        s = raw.strip()
        if s and not is_decorative(s) and not s.startswith("目录") and not s.startswith("END"):
            cover_body.append({"type":"text","text":s})
    if cover_body:
        slides.append({"title":deck_title,"type":"cover","body":cover_body})
    
    # Build content slides
    for si, (start_line, heading) in enumerate(real_sections):
        end_line = real_sections[si+1][0] if si+1 < len(real_sections) else len(lines)
        
        tl = heading.lower()
        tp = "content"
        if any(k in tl for k in ["目标","大纲","学习目标","objectives"]): tp = "objectives"
        elif any(k in tl for k in ["总结","小结","回顾","收尾","summary","conclusion","end","常见问题","faq"]): tp = "summary"
        elif any(k in tl for k in ["环境","配置","设置","requirements"]): tp = "setup"
        elif any(k in tl for k in ["注意","警告","提示","tip","note","重要"]): tp = "callout"
        
        body = []
        in_code = False
        code_buf = None
        has_content = False
        
        for j in range(start_line+1, end_line):
            raw = lines[j]
            s = raw.strip()
            if not s or is_decorative(s):
                continue
            if s.startswith("```"):
                if in_code and code_buf:
                    body.append({"type":"code","lang":"text","content":"\n".join(code_buf)})
                    code_buf=None
                    has_content = True
                in_code = not in_code
                if in_code: code_buf=[]
                continue
            if in_code and code_buf is not None:
                code_buf.append(raw.rstrip())
                continue
            if s.startswith(("- ","* ","+ ")):
                body.append({"type":"bullet","text":s[2:].strip()})
                has_content = True
                continue
            if re.match(r'^\d+[\.\)]\s', s):
                body.append({"type":"bullet","text":s})
                has_content = True
                continue
            if s.startswith("【") and "】" in s:
                body.append({"type":"text","text":"■ "+s.strip("【】")})
                has_content = True
                continue
            if s.startswith("|") and s.endswith("|"):
                cols = [c.strip() for c in s.strip("|").split("|")]
                if len(cols) >= 2:
                    body.append({"type":"table_row","cols":cols})
                    has_content = True
                continue
            body.append({"type":"text","text":s})
            has_content = True
        
        if has_content or si == len(real_sections)-1:
            slides.append({"title":heading,"type":tp,"body":body})
    
    return {"title":deck_title,"slides":slides}


def generate_cover_slide(s, i, n, deck_title):
    body = s.get("body",[])
    parts = [f'  <section class="slide" data-title="{escape_html(s["title"])}">']
    parts.append('    <div class="cover-bg"></div><div class="cover-content">')
    parts.append(f'      <span class="cover-badge">{escape_html(deck_title)}</span>')
    parts.append(f'      <h1 class="cover-title">{escape_html(s["title"])}</h1>')
    for it in body:
        if it["type"]=="text":
            parts.append(f'      <p class="cover-sub">{escape_html(it["text"])}</p>')
    if not body:
        parts.append('      <p class="cover-sub">AI 教学课程</p>')
    parts.append(f'      <div class="cover-footer"><span>{datetime.now().strftime("%Y-%m-%d")}</span><span class="slide-number">{i+1}/{n}</span></div>')
    parts.append('    </div></section>')
    return "\n".join(parts)

def generate_content_slide(s, i, n, deck_title):
    body = s.get("body",[])
    tp = s["type"]
    parts = [f'  <section class="slide" data-title="{escape_html(s["title"])}">']
    parts.append('    <div class="slide-header">')
    parts.append(f'      <span class="slide-decor"></span><span class="slide-kicker">{escape_html(deck_title)}</span><span class="slide-num">{i+1}/{n}</span>')
    parts.append('    </div>')
    if tp=="code":
        parts.append('    <div class="code-layout">')
        parts.append(f'      <h2 class="slide-title code-title">⟨ {escape_html(s["title"])} ⟩</h2>')
        for it in body:
            if it["type"]=="code": parts.append(f'      <pre class="code-block"><code>{escape_html(it["content"])}</code></pre>')
            elif it["type"]=="text": parts.append(f'      <p class="code-desc">{escape_html(it["text"])}</p>')
        parts.append('    </div>')
    elif tp=="summary":
        parts.append('    <div class="summary-layout">')
        parts.append(f'      <div class="summary-icon">🎯</div><h2 class="slide-title">{escape_html(s["title"])}</h2>')
        parts.append('      <div class="summary-items">')
        for it in body:
            if it["type"] in ("text","bullet"):
                parts.append(f'        <div class="summary-item"><span class="check">✅</span><span>{escape_html(it["text"])}</span></div>')
        parts.append('      </div></div>')
    elif tp=="objectives":
        parts.append('    <div class="obj-layout">')
        parts.append(f'      <h2 class="slide-title">{escape_html(s["title"])}</h2><div class="obj-grid">')
        for it in body:
            if it["type"] in ("text","bullet"):
                parts.append(f'        <div class="obj-card"><span class="obj-icon">📌</span><span>{escape_html(it["text"])}</span></div>')
        parts.append('      </div></div>')
    else:
        parts.append('    <div class="content-layout">')
        parts.append(f'      <h2 class="slide-title">{escape_html(s["title"])}</h2>')
        bullets = [it for it in body if it["type"]=="bullet"]
        texts = [it for it in body if it["type"]=="text"]
        if len(bullets)>6:
            mid = (len(bullets)+1)//2
            parts.append('      <div class="two-col"><ul class="bullet-list">')
            for it in bullets[:mid]: parts.append(f'          <li><span class="bullet-marker">▸</span>{escape_html(it["text"])}</li>')
            parts.append('        </ul><ul class="bullet-list">')
            for it in bullets[mid:]: parts.append(f'          <li><span class="bullet-marker">▸</span>{escape_html(it["text"])}</li>')
            parts.append('        </ul></div>')
        elif bullets:
            parts.append('      <ul class="bullet-list">')
            for it in bullets: parts.append(f'        <li><span class="bullet-marker">▸</span>{escape_html(it["text"])}</li>')
            parts.append('      </ul>')
        for it in texts: parts.append(f'      <p class="content-text">{escape_html(it["text"])}</p>')
        for it in body:
            if it["type"]=="table_row": parts.append(f'      <div class="mini-table"><div class="mini-row">{"".join(f"<span>{escape_html(c)}</span>" for c in it["cols"])}</div></div>')
            elif it["type"]=="code": parts.append(f'      <pre class="inline-code"><code>{escape_html(it["content"])}</code></pre>')
        parts.append('    </div>')
    parts.append('  </section>')
    return "\n".join(parts)

CSS = """.slide{position:absolute;top:0;left:0;width:1920px;height:1080px;display:none;overflow:hidden;box-sizing:border-box;padding:60px 80px;background:var(--surface)}.slide.is-active{display:flex;opacity:1;z-index:10}.slide-header{position:absolute;top:0;left:0;right:0;height:48px;display:flex;align-items:center;padding:0 60px;gap:16px;font-size:13px;color:var(--text-3);border-bottom:1px solid var(--border)}.slide-decor{width:4px;height:24px;background:var(--accent);border-radius:2px}.slide-kicker{font-weight:600;letter-spacing:.08em;text-transform:uppercase}.slide-num{margin-left:auto;font-family:"JetBrains Mono",monospace;font-size:13px}.slide-title{font-size:42px;font-weight:700;letter-spacing:-.02em;margin:0 0 28px;color:var(--text-1);line-height:1.2}.content-layout,.code-layout,.obj-layout,.summary-layout{width:100%;padding-top:56px}.bullet-list{list-style:none;padding:0;margin:0}.bullet-list li{padding:10px 0;font-size:22px;line-height:1.6;color:var(--text-1);border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:12px}.bullet-list li:last-child{border-bottom:none}.bullet-marker{color:var(--accent);font-size:18px;flex-shrink:0;margin-top:4px}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:40px}.content-text{font-size:20px;line-height:1.7;color:var(--text-2);margin:8px 0}.code-block{background:#1a1a2e;border-radius:12px;padding:24px;font-family:"JetBrains Mono",monospace;font-size:15px;line-height:1.7;overflow-x:auto;color:#e4e4e7;border:1px solid rgba(255,255,255,.1);box-shadow:0 4px 20px rgba(0,0,0,.3)}.code-title{color:var(--accent);font-family:"JetBrains Mono",monospace;font-size:28px}.code-desc{font-size:18px;color:var(--text-2);margin:16px 0}.inline-code{background:#1a1a2e;border-radius:8px;padding:16px;margin:12px 0;font-family:"JetBrains Mono",monospace;font-size:14px;overflow-x:auto;color:#e4e4e7;border:1px solid rgba(255,255,255,.08)}.cover-bg{position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 30% 50%,rgba(255,255,255,.08) 0%,transparent 60%)}.cover-content{position:relative;z-index:2;text-align:center;margin:auto;max-width:1400px}.cover-badge{display:inline-block;padding:8px 24px;border:1px solid rgba(255,255,255,.3);border-radius:20px;font-size:14px;color:rgba(255,255,255,.6);margin-bottom:24px;letter-spacing:.1em;text-transform:uppercase}.cover-title{font-size:72px;font-weight:800;letter-spacing:-.03em;color:#fff;margin:0 0 20px;line-height:1.1;text-shadow:0 2px 40px rgba(0,0,0,.3)}.cover-sub{font-size:24px;color:rgba(255,255,255,.7);margin:16px 0}.cover-footer{margin-top:60px;display:flex;justify-content:space-between;color:rgba(255,255,255,.4);font-size:14px}.summary-layout{text-align:center}.summary-icon{font-size:60px;margin-bottom:16px}.summary-items{display:flex;flex-direction:column;gap:16px;max-width:900px;margin:0 auto}.summary-item{display:flex;align-items:center;gap:16px;padding:18px 24px;background:var(--surface-2);border-radius:12px;font-size:20px;line-height:1.5;text-align:left;border:1px solid var(--border)}.check{font-size:20px;flex-shrink:0}.obj-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.obj-card{display:flex;align-items:center;gap:12px;padding:20px 24px;background:var(--surface-2);border-radius:12px;font-size:19px;line-height:1.5;border:1px solid var(--border);box-shadow:var(--shadow)}.obj-icon{font-size:20px;flex-shrink:0}.mini-table{margin:12px 0}.mini-row{display:flex;gap:8px;flex-wrap:wrap}.mini-row span{padding:6px 12px;background:var(--surface-2);border-radius:6px;font-size:14px;color:var(--text-2);border:1px solid var(--border)}.is-active .slide-title{animation:fadeInUp .6s ease both}.is-active .bullet-list li{animation:fadeInUp .5s ease both}.is-active .cover-title{animation:fadeInScale .8s ease both}.is-active .cover-sub{animation:fadeInUp .6s ease .3s both}.is-active .cover-badge{animation:fadeInUp .5s ease .1s both}.is-active .summary-item{animation:slideInRight .5s ease both}.is-active .obj-card{animation:fadeInUp .5s ease both}.is-active .code-block{animation:fadeInScale .6s ease both}@keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}@keyframes fadeInScale{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:scale(1)}}@keyframes slideInRight{from{opacity:0;transform:translateX(60px)}to{opacity:1;transform:translateX(0)}}"""

def build(deck, deck_dir=None):
    slides = deck["slides"]
    n = len(slides)
    title = deck["title"]
    ar = "assets"
    h = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{title}</title>',
         f'<link rel="stylesheet" href="{ar}/fonts.css">',
         f'<link rel="stylesheet" href="{ar}/base.css">',
         f'<link rel="stylesheet" href="{ar}/animations/animations.css">',
         '<link rel="stylesheet" href="style.css">',
         f'<link rel="stylesheet" id="theme-link" href="{ar}/themes/{DEFAULT_THEME}.css">',
         f'</head><body class="tpl-course-module" data-themes="{",".join(ALL_THEMES)}" data-theme-base="{ar}/themes/"><div class="deck">']
    for i,s in enumerate(slides):
        sl = generate_cover_slide(s,i,n,title) if s["type"]=="cover" or i==0 else generate_content_slide(s,i,n,title)
        if i==0: sl=sl.replace('class="slide"','class="slide is-active"',1)
        h.append(sl)
    h.append('</div><script src="'+ar+'/runtime.js"></script></body></html>')
    return "\n".join(h)

def copy_assets(deck_dir):
    import shutil
    try:
        src=find_htmlppt_assets(); dst=deck_dir/"assets"
        if dst.exists(): return
        dst.mkdir(parents=True)
        for f in ["fonts.css","base.css","runtime.js"]: shutil.copy2(src/f,dst/f)
        shutil.copytree(src/"themes",dst/"themes",dirs_exist_ok=True)
        shutil.copytree(src/"animations",dst/"animations",dirs_exist_ok=True)
    except Exception as e: print(f"Warning: could not copy assets: {e}")

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("input"); ap.add_argument("--theme",default=DEFAULT_THEME); ap.add_argument("-o","--output",default=None)
    a=ap.parse_args()
    with open(a.input,"r",encoding="utf-8-sig") as f: deck=parse_md(f.read())
    slug=re.sub(r'[^\w\u4e00-\u9fff]+','-',deck["title"]).strip("-")[:40] or "teaching-deck"
    dd=(Path(a.output) if a.output else Path("D:/codex/teach-output"))/slug
    dd.mkdir(parents=True,exist_ok=True)
    (dd/"index.html").write_text(build(deck,dd),encoding="utf-8")
    (dd/"style.css").write_text(CSS,encoding="utf-8")
    (dd/"slides.json").write_text(json.dumps(deck,ensure_ascii=False,indent=2),encoding="utf-8")
    copy_assets(dd)
    print(f"\n=== PPT Generation Complete ===")
    print(f"Directory: {dd}"); print(f"Slides: {len(deck['slides'])}")

if __name__=="__main__": main()
