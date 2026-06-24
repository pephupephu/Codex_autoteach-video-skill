#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI教学文本 -> 精美HTML教学PPT 生成器（v6 - 精美视觉版）
彻底重写幻灯片模板系统，每页都像专业PPT。
"""
import json, os, re, sys, random
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
    raise FileNotFoundError("html-ppt assets not found. Run: npx skills add https://github.com/lewislulu/html-ppt-skill")

SKILL_ASSETS = find_htmlppt_assets()
ALL_THEMES = ["academic-paper","aurora","bauhaus","blueprint","catppuccin-mocha",
    "corporate-clean","cyberpunk-neon","dracula","editorial-serif","glassmorphism",
    "japanese-minimal","magazine-bold","memphis-pop","midcentury","minimal-white",
    "neo-brutalism","news-broadcast","nord","pitch-deck-vc","rainbow-gradient",
    "retro-tv","rose-pine","sharp-mono","soft-pastel","solarized-light","sunset-warm",
    "swiss-grid","terminal-green","tokyo-night","vaporwave","xiaohongshu-white",
    "y2k-chrome","engineering-whiteprint","gruvbox-dark","catppuccin-latte"]
DEFAULT_THEME = "tokyo-night"

def escape(text): return text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def is_deco(s): return bool(re.match(r'^[=\-*]{3,}$', s.strip()))

def pick_icon(keyword):
    """Pick an emoji icon based on keywords"""
    emoji_map = {
        "环境|配置|设置|安装|部署|setup|install": "⚙️",
        "代码|示例|实现|函数|code|example|api": "💻",
        "目标|大纲|学习|objectives|goal": "🎯",
        "总结|小结|回顾|summary|conclusion": "📝",
        "注意|警告|提示|tip|note": "⚠️",
        "数据|架构|设计|架构|structure": "🏗️",
        "步骤|流程|工作流|step|workflow": "🔄",
        "常见问题|faq|q&a": "❓",
        "验证|测试|检查|test|verify": "✅",
        "维护|运维|日常": "🔧",
        "卸载|清理|remove": "🗑️",
        "启动|访问|run|start": "🚀",
        "企业|商业|enterprise": "🏢",
        "安全|权限|security": "🔒",
        "优化|性能|performance": "⚡",
        "集成|integration|skill": "🧩",
        "算法|聚类|affinity": "🧮",
        "更新|升级|update": "🔄",
        "备份|backup": "💾",
    }
    for pattern, icon in emoji_map.items():
        if re.search(pattern, keyword, re.I):
            return icon
    return "📌"

def pick_color(keyword, idx=0):
    """Pick an accent color based on keywords"""
    colors = ["#6366f1","#ec4899","#14b8a6","#f59e0b","#8b5cf6","#06b6d4","#84cc16","#f97316"]
    return colors[idx % len(colors)]


def parse_md(text):
    lines = text.strip().split("\n")
    deck_title = "AI教学课程"
    for raw in lines:
        s = raw.strip()
        if s and not is_deco(s) and not s.startswith("目录") and not s.startswith("END"):
            deck_title = s.strip("*#\t ")
            break
    
    # Find real section headings (between === markers or ## headings, skip TOC)
    in_toc = False
    real_sections = []
    seen_headings = set()
    
    i = 0
    while i < len(lines):
        raw = lines[i]; stripped = raw.strip()
        if not stripped: i+=1; continue
        if stripped == "目录：" or stripped.startswith("目录"): in_toc = True; i+=1; continue
        if is_deco(stripped): in_toc = False; i+=1; continue
        if raw.startswith("## "):
            h = raw[3:].strip()
            if h and h not in seen_headings: real_sections.append((i,h)); seen_headings.add(h)
            i+=1; continue
        if re.match(r'^[一二三四五六七八九十]+[、\.\)]\s*\S', stripped):
            prev_dec = False
            for j in range(i-1,-1,-1):
                p = lines[j].strip()
                if is_deco(p): prev_dec=True; break
                if p: break
            if prev_dec and not in_toc and stripped not in seen_headings:
                real_sections.append((i,stripped)); seen_headings.add(stripped)
            i+=1; continue
        i+=1
    
    if not real_sections:
        body=[{"type":"text","text":l.strip()} for l in lines if l.strip() and not is_deco(l)]
        return {"title":deck_title,"slides":[{"title":deck_title,"type":"cover","body":body[:8]}]}
    
    slides = []
    # Cover slide
    cover_body = []
    for raw in lines[:real_sections[0][0]]:
        s=raw.strip()
        if s and not is_deco(s) and not s.startswith("目录") and not s.startswith("END"):
            cover_body.append({"type":"text","text":s})
    if cover_body:
        slides.append({"title":deck_title,"type":"cover","body":cover_body})
    
    # Content slides
    for si,(start_line,heading) in enumerate(real_sections):
        end_line = real_sections[si+1][0] if si+1<len(real_sections) else len(lines)
        tl=heading.lower()
        # Auto-detect slide type
        tp="content"
        if any(k in tl for k in ["环境","配置","设置","requirements"]): tp="setup"
        elif any(k in tl for k in ["代码","示例","实现","安装","code"]): tp="code"
        elif any(k in tl for k in ["总结","小结","回顾","收尾","summary","conclusion","常见问题","faq"]): tp="summary"
        elif any(k in tl for k in ["目标","大纲","学习目标","objectives"]): tp="objectives"
        elif any(k in tl for k in ["注意","警告","提示","tip","重要"]): tp="callout"
        elif any(k in tl for k in ["步骤","流程","工作流"]): tp="steps"
        elif any(k in tl for k in ["架构","设计","结构"]): tp="architecture"
        elif any(k in tl for k in ["数据","对比","比较"]): tp="data"
        
        body=[]; in_code=False; code_buf=None
        has_content=False
        for j in range(start_line+1,end_line):
            raw=lines[j]; s=raw.strip()
            if not s or is_deco(s): continue
            if s.startswith("```"):
                if in_code and code_buf:
                    body.append({"type":"code","lang":"text","content":"\n".join(code_buf)})
                    code_buf=None; has_content=True
                in_code=not in_code
                if in_code: code_buf=[]
                continue
            if in_code and code_buf is not None:
                code_buf.append(raw.rstrip()); continue
            if s.startswith(("- ","* ","+ ")):
                body.append({"type":"bullet","text":s[2:].strip()}); has_content=True; continue
            if re.match(r'^\d+[\.\)]\s',s):
                body.append({"type":"bullet","text":s}); has_content=True; continue
            if s.startswith("【") and "】" in s:
                body.append({"type":"text","text":"■ "+s.strip("【】")}); has_content=True; continue
            if s.startswith("|") and s.endswith("|"):
                cols=[c.strip() for c in s.strip("|").split("|")]
                if len(cols)>=2: body.append({"type":"table_row","cols":cols}); has_content=True
                continue
            body.append({"type":"text","text":s}); has_content=True
        if has_content or si==len(real_sections)-1:
            slides.append({"title":heading,"type":tp,"body":body})
    
    return {"title":deck_title,"slides":slides}


# ============ RICH SLIDE BUILDERS ============

def build_cover(s, i, n, title):
    """Beautiful cover with gradient, pattern overlay, and floating decorations"""
    body = s.get("body",[])
    icon = pick_icon(title)
    lines = [f'  <section class="slide" data-title="{escape(s["title"])}">']
    # Decorative floating shapes
    shapes = ""
    for k in range(6):
        x=random.randint(5,92); y=random.randint(5,92); sz=random.randint(60,180)
        shapes += f'<div class="cover-shape" style="left:{x}%;top:{y}%;width:{sz}px;height:{sz}px;animation-delay:{k*0.15}s"></div>'
    lines.append(f'    <div class="cover-pattern">{shapes}</div>')
    lines.append(f'    <div class="cover-content">')
    lines.append(f'      <div class="cover-icon">{icon}</div>')
    lines.append(f'      <div class="cover-badge">AI 教学课程</div>')
    lines.append(f'      <h1 class="cover-title">{escape(s["title"])}</h1>')
    for it in body[:5]:
        if it["type"]=="text":
            lines.append(f'      <p class="cover-sub">{escape(it["text"])}</p>')
    lines.append(f'      <div class="cover-divider"></div>')
    lines.append(f'      <div class="cover-meta">')
    lines.append(f'        <span>📅 {datetime.now().strftime("%Y-%m-%d")}</span>')
    lines.append(f'        <span>📄 {n} 页幻灯片</span>')
    lines.append(f'      </div>')
    lines.append(f'    </div>')
    lines.append(f'    <div class="cover-footer-bar"></div>')
    lines.append(f'  </section>')
    return "\n".join(lines)

def build_section_divider(s, i, n, title):
    """Full-bleed section divider slide"""
    lines = [f'  <section class="slide" data-title="{escape(s["title"])}">']
    lines.append(f'    <div class="section-divider">')
    lines.append(f'      <div class="section-number">{(i):02d}</div>')
    lines.append(f'      <h2 class="section-title">{escape(s["title"])}</h2>')
    lines.append(f'      <div class="section-line"></div>')
    lines.append(f'    </div>')
    lines.append(f'  </section>')
    return "\n".join(lines)

def build_content_rich(s, i, n, title):
    """Rich content slide with cards, badges, icons"""
    body = s.get("body",[])
    tp = s["type"]
    
    lines = [f'  <section class="slide" data-title="{escape(s["title"])}">']
    # Top bar
    lines.append(f'    <div class="topbar"><span class="topbar-icon">{pick_icon(s["title"])}</span><span class="topbar-title">{escape(s["title"])}</span><span class="topbar-num">{i}/{n}</span></div>')
    
    # Background decorations
    lines.append(f'    <div class="slide-bg-deco"><div class="bg-circle-1"></div><div class="bg-circle-2"></div></div>')
    
    bullets = [it for it in body if it["type"]=="bullet"]
    texts = [it for it in body if it["type"]=="text"]
    codes = [it for it in body if it["type"]=="code"]
    tables = [it for it in body if it["type"]=="table_row"]
    
    if tp == "code":
        lines.append('    <div class="code-container">')
        lines.append(f'      <div class="code-header"><span class="code-dot red"></span><span class="code-dot yellow"></span><span class="code-dot green"></span><span class="code-lang">{escape(s["title"])}</span></div>')
        if texts:
            for it in texts: lines.append(f'      <p class="code-desc">{escape(it["text"])}</p>')
        for it in codes:
            lines.append(f'      <pre class="code-body"><code>{escape(it["content"])}</code></pre>')
        for it in bullets:
            lines.append(f'      <div class="code-info"><span class="bullet-dot">▸</span>{escape(it["text"])}</div>')
        lines.append('    </div>')
    
    elif tp == "summary":
        lines.append('    <div class="summary-container">')
        lines.append(f'      <h2 class="section-heading">📋 {escape(s["title"])}</h2>')
        lines.append('      <div class="check-grid">')
        for it in bullets:
            lines.append(f'        <div class="check-card"><span class="check-icon">✅</span><span>{escape(it["text"])}</span></div>')
        for it in texts:
            lines.append(f'        <div class="check-card"><span class="check-icon">📌</span><span>{escape(it["text"])}</span></div>')
        lines.append('      </div></div>')
    
    elif tp == "setup" or tp == "steps":
        lines.append('    <div class="steps-container">')
        lines.append(f'      <h2 class="section-heading">🛠️ {escape(s["title"])}</h2>')
        lines.append('      <div class="steps-list">')
        for idx, it in enumerate(bullets):
            c = pick_color("", idx)
            lines.append(f'        <div class="step-card" style="--step-color:{c}"><div class="step-num">{idx+1}</div><div class="step-text">{escape(it["text"])}</div></div>')
        for it in texts:
            lines.append(f'        <div class="step-card"><div class="step-num">✦</div><div class="step-text">{escape(it["text"])}</div></div>')
        lines.append('      </div></div>')
    
    elif tp == "callout":
        lines.append('    <div class="callout-wrap">')
        lines.append(f'      <div class="callout-card"><div class="callout-icon">⚠️</div><h3>{escape(s["title"])}</h3>')
        for it in body:
            if it["type"]=="text": lines.append(f'        <p>{escape(it["text"])}</p>')
            elif it["type"]=="bullet": lines.append(f'        <div class="callout-item">• {escape(it["text"])}</div>')
        lines.append('      </div></div>')
    
    elif tp == "objectives":
        lines.append('    <div class="obj-container">')
        lines.append(f'      <h2 class="section-heading">🎯 {escape(s["title"])}</h2>')
        lines.append('      <div class="obj-grid">')
        all_items = bullets + [{"type":"text","text":it["text"]} for it in texts]
        for idx, it in enumerate(all_items):
            t = it.get("text","")
            icon = ["🎯","💡","⭐","🔑","📌","🏆"][idx % 6]
            lines.append(f'        <div class="obj-card-r"><span class="obj-emoji">{icon}</span><span>{escape(t)}</span></div>')
        lines.append('      </div></div>')
    
    elif tp == "architecture":
        lines.append('    <div class="arch-container">')
        lines.append(f'      <h2 class="section-heading">🏗️ {escape(s["title"])}</h2>')
        lines.append('      <div class="arch-grid">')
        for idx, it in enumerate(bullets):
            c = pick_color("", idx)
            lines.append(f'        <div class="arch-card" style="border-color:{c}"><div class="arch-card-head" style="background:{c}20;color:{c}">{escape(it["text"])}</div></div>')
        for it in texts:
            lines.append(f'        <div class="arch-card"><div class="arch-card-head">{escape(it["text"])}</div></div>')
        lines.append('      </div></div>')
    
    else:
        # Rich content layout
        lines.append('    <div class="content-rich">')
        lines.append(f'      <h2 class="section-heading">{pick_icon(s["title"])} {escape(s["title"])}</h2>')
        
        if tables:
            lines.append('      <div class="table-wrap"><table class="rich-table">')
            for it in tables:
                row_class = "table-header" if it == tables[0] else ""
                lines.append(f'        <tr class="{row_class}">{"".join(f"<td>{escape(c)}</td>" for c in it["cols"])}</tr>')
            lines.append('      </table></div>')
        
        if len(bullets) > 6:
            mid = (len(bullets)+1)//2
            lines.append('      <div class="two-col">')
            lines.append('        <div class="bullet-cards">')
            for idx, it in enumerate(bullets[:mid]):
                c = pick_color("", idx)
                lines.append(f'          <div class="bullet-card" style="--card-color:{c}"><span class="bullet-badge" style="background:{c}">{idx+1}</span><span>{escape(it["text"])}</span></div>')
            lines.append('        </div>')
            lines.append('        <div class="bullet-cards">')
            for idx, it in enumerate(bullets[mid:]):
                c = pick_color("", idx+mid)
                lines.append(f'          <div class="bullet-card" style="--card-color:{c}"><span class="bullet-badge" style="background:{c}">{idx+mid+1}</span><span>{escape(it["text"])}</span></div>')
            lines.append('        </div></div>')
        elif bullets:
            lines.append('      <div class="bullet-cards single-col">')
            for idx, it in enumerate(bullets):
                c = pick_color("", idx)
                icon = ["🚀","💡","🎯","🔧","📊","🛡️","⚡","🎨"][idx % 8]
                lines.append(f'        <div class="bullet-card" style="--card-color:{c}"><span class="bullet-badge" style="background:{c}">{icon}</span><span>{escape(it["text"])}</span></div>')
            lines.append('      </div>')
        
        for it in texts:
            if it["text"].startswith("■"):
                lines.append(f'      <div class="section-tag">{escape(it["text"][1:].strip())} {pick_icon(it["text"])}</div>')
            else:
                lines.append(f'      <p class="content-para">{escape(it["text"])}</p>')
        
        for it in codes:
            lines.append(f'      <pre class="inline-code-r"><code>{escape(it["content"])}</code></pre>')
        
        lines.append('    </div>')
    
    lines.append(f'  </section>')
    return "\n".join(lines)


# ============ RICH CSS ============
CSS = """
/* ==== Rich Teaching PPT Styles ==== */

/* Base slide */
.slide { position:absolute; top:0; left:0; width:1920px; height:1080px; display:none; overflow:hidden; box-sizing:border-box; background:var(--surface); }
.slide.is-active { display:flex; flex-direction:column; z-index:10; }

/* ---- Top Bar ---- */
.topbar {
  position:absolute; top:0; left:0; right:0; height:52px; display:flex; align-items:center;
  padding:0 50px; gap:14px; z-index:20;
  background:linear-gradient(180deg, rgba(0,0,0,0.08) 0%, transparent 100%);
  border-bottom:1px solid var(--border);
}
.topbar-icon { font-size:22px; }
.topbar-title { font-size:15px; font-weight:600; color:var(--text-2); letter-spacing:0.3px; }
.topbar-num { margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:13px; color:var(--text-3); }

/* ---- Background decorations ---- */
.slide-bg-deco { position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none; overflow:hidden; }
.bg-circle-1 {
  position:absolute; top:-200px; right:-100px; width:600px; height:600px; border-radius:50%;
  background:radial-gradient(circle, var(--accent) 0%, transparent 70%); opacity:0.06;
}
.bg-circle-2 {
  position:absolute; bottom:-150px; left:-80px; width:400px; height:400px; border-radius:50%;
  background:radial-gradient(circle, var(--accent-2,var(--accent)) 0%, transparent 70%); opacity:0.04;
}

/* ---- Section Heading ---- */
.section-heading {
  font-size:36px; font-weight:700; letter-spacing:-0.5px; color:var(--text-1);
  margin:0 0 24px 0; padding-bottom:14px;
  border-bottom:3px solid var(--accent); display:inline-block;
}

/* ---- Cover (refined) ---- */
.cover-pattern {
  position:absolute; top:0; left:0; right:0; bottom:0; overflow:hidden;
  background:linear-gradient(135deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 30%, #1a1a2e) 100%);
}
.cover-shape {
  position:absolute; border-radius:50%; background:rgba(255,255,255,0.04);
  animation:floatShape 6s ease-in-out infinite; border:1px solid rgba(255,255,255,0.06);
}
.cover-content { position:relative; z-index:2; margin:auto; text-align:center; max-width:1200px; padding:60px; }
.cover-icon { font-size:64px; margin-bottom:8px; animation:coverBounce 1s ease both; }
.cover-badge {
  display:inline-block; padding:6px 20px; border:1px solid rgba(255,255,255,0.25);
  border-radius:20px; font-size:12px; color:rgba(255,255,255,0.6);
  letter-spacing:3px; text-transform:uppercase; margin-bottom:20px;
}
.cover-title {
  font-size:68px; font-weight:800; letter-spacing:-2px; color:#fff;
  margin:0 0 16px; line-height:1.1; text-shadow:0 4px 30px rgba(0,0,0,0.2);
}
.cover-sub { font-size:22px; color:rgba(255,255,255,0.7); margin:8px 0; line-height:1.6; max-width:800px; margin-left:auto; margin-right:auto; }
.cover-divider { width:80px; height:3px; background:rgba(255,255,255,0.3); margin:28px auto; border-radius:2px; }
.cover-meta { display:flex; justify-content:center; gap:40px; font-size:14px; color:rgba(255,255,255,0.4); }
.cover-footer-bar { position:absolute; bottom:0; left:0; right:0; height:4px; background:linear-gradient(90deg, var(--accent), transparent); }

/* ---- Section Divider ---- */
.section-divider {
  margin:auto; text-align:center; position:relative; z-index:2;
  background:linear-gradient(135deg, var(--surface-2), var(--surface)); width:100%; height:100%;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.section-number {
  font-size:100px; font-weight:900; color:var(--accent); opacity:0.15; letter-spacing:-5px;
  font-family:"JetBrains Mono",monospace; line-height:1; margin-bottom:10px;
}
.section-title { font-size:56px; font-weight:700; color:var(--text-1); margin:0; }
.section-line { width:120px; height:3px; background:var(--accent); margin-top:24px; border-radius:2px; }

/* ---- Bullet Cards ---- */
.bullet-cards { display:flex; flex-direction:column; gap:10px; padding-right:20px; }
.bullet-cards.single-col { max-width:95%; }
.bullet-card {
  display:flex; align-items:center; gap:16px; padding:14px 20px;
  background:var(--surface-2); border-radius:10px; font-size:20px; line-height:1.5;
  border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.04);
  transition:transform 0.2s, box-shadow 0.2s;
}
.bullet-badge {
  flex-shrink:0; width:28px; height:28px; border-radius:8px;
  display:flex; align-items:center; justify-content:center;
  font-family:"JetBrains Mono",monospace; font-size:12px; font-weight:700; color:#fff;
}
.bullet-dot { color:var(--accent); margin-right:8px; }
.content-para { font-size:19px; line-height:1.7; color:var(--text-2); margin:6px 0; }
.section-tag {
  display:inline-flex; align-items:center; gap:10px;
  padding:8px 18px; background:var(--surface-2); border-radius:8px; margin:6px 0;
  font-size:16px; font-weight:600; color:var(--accent); border:1px solid var(--border);
}
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:24px; }
.content-rich { padding-top:56px; flex:1; padding-right:40px; overflow:auto; }

/* ---- Step Cards ---- */
.steps-container { padding-top:56px; flex:1; }
.steps-list { display:flex; flex-direction:column; gap:10px; max-width:90%; }
.step-card {
  display:flex; align-items:center; gap:18px; padding:16px 22px;
  background:var(--surface-2); border-radius:12px;
  border:1px solid var(--border); border-left:4px solid var(--step-color,#6366f1);
  box-shadow:0 2px 8px rgba(0,0,0,0.04);
}
.step-num {
  flex-shrink:0; width:36px; height:36px; border-radius:10px;
  background:var(--step-color,#6366f1); color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-family:"JetBrains Mono",monospace; font-size:16px; font-weight:800;
}
.step-text { font-size:19px; color:var(--text-1); line-height:1.5; }

/* ---- Check Grid (Summary) ---- */
.summary-container { padding-top:56px; flex:1; }
.check-grid {
  display:grid; grid-template-columns:1fr 1fr; gap:12px; max-width:95%;
}
.check-card {
  display:flex; align-items:center; gap:14px; padding:16px 20px;
  background:var(--surface-2); border-radius:10px; font-size:18px; line-height:1.5;
  border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.04);
}
.check-icon { font-size:20px; flex-shrink:0; }

/* ---- Objective Grid ---- */
.obj-container { padding-top:56px; flex:1; }
.obj-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; max-width:95%; }
.obj-card-r {
  display:flex; align-items:center; gap:14px; padding:18px 22px;
  background:var(--surface-2); border-radius:12px; font-size:18px; line-height:1.5;
  border:1px solid var(--border); box-shadow:0 2px 8px rgba(0,0,0,0.04);
}
.obj-emoji { font-size:24px; flex-shrink:0; }

/* ---- Callout ---- */
.callout-wrap { padding-top:56px; flex:1; display:flex; align-items:center; justify-content:center; }
.callout-card {
  max-width:900px; padding:36px 44px; background:var(--surface-2);
  border-radius:16px; border:2px solid var(--accent); box-shadow:0 4px 20px rgba(0,0,0,0.06);
}
.callout-icon { font-size:48px; margin-bottom:12px; }
.callout-card h3 { font-size:28px; color:var(--accent); margin:0 0 16px; }
.callout-card p { font-size:19px; line-height:1.7; color:var(--text-1); margin:8px 0; }
.callout-item { font-size:18px; color:var(--text-2); margin:6px 0; padding-left:20px; }

/* ---- Code ---- */
.code-container { padding-top:56px; flex:1; max-width:95%; }
.code-header {
  display:flex; align-items:center; gap:8px; padding:10px 16px;
  background:#1e1e2e; border-radius:10px 10px 0 0; border-bottom:1px solid rgba(255,255,255,0.06);
}
.code-dot { width:12px; height:12px; border-radius:50%; }
.red { background:#ff5f57; }
.yellow { background:#febc2e; }
.green { background:#28c840; }
.code-lang { margin-left:auto; font-size:12px; color:rgba(255,255,255,0.3); font-family:"JetBrains Mono",monospace; }
.code-body {
  background:#1e1e2e; color:#e4e4e7; padding:20px 24px; margin:0;
  font-family:"JetBrains Mono","Fira Code",monospace; font-size:14px; line-height:1.7;
  overflow-x:auto; border-radius:0 0 10px 10px;
}
.code-desc { font-size:18px; color:var(--text-2); margin:12px 0; }
.code-info { font-size:16px; color:var(--text-3); margin:8px 0; }

/* ---- Architecture ---- */
.arch-container { padding-top:56px; flex:1; }
.arch-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; max-width:95%; }
.arch-card {
  border:2px solid var(--border); border-radius:12px; overflow:hidden; background:var(--surface-2);
}
.arch-card-head { padding:14px 18px; font-size:17px; font-weight:600; }

/* ---- Table ---- */
.table-wrap { margin:16px 0; max-width:95%; overflow-x:auto; }
.rich-table { width:100%; border-collapse:separate; border-spacing:0; font-size:16px; }
.rich-table td { padding:10px 16px; border-bottom:1px solid var(--border); color:var(--text-2); }
.table-header td { background:var(--surface-2); font-weight:600; color:var(--text-1); }

/* ---- Inline Code ---- */
.inline-code-r {
  background:#1e1e2e; border-radius:8px; padding:16px; margin:10px 0;
  font-family:"JetBrains Mono",monospace; font-size:13px; overflow-x:auto; color:#e4e4e7;
}

/* ---- Animations ---- */
@keyframes floatShape {
  0%,100% { transform:translate(0,0) scale(1); }
  50% { transform:translate(20px,-20px) scale(1.05); }
}
@keyframes coverBounce {
  0% { opacity:0; transform:scale(0.5) translateY(-20px); }
  60% { transform:scale(1.05) translateY(5px); }
  100% { opacity:1; transform:scale(1) translateY(0); }
}

/* Stagger animations */
.is-active .content-rich { animation:slideUp 0.5s ease both; }
.is-active .bullet-card { animation:cardIn 0.4s ease both; }
.is-active .step-card { animation:cardIn 0.4s ease both; }
.is-active .check-card { animation:cardIn 0.4s ease both; }
.is-active .obj-card-r { animation:cardIn 0.4s ease both; }
.is-active .code-container { animation:slideUp 0.5s ease both; }
.is-active .callout-card { animation:popIn 0.5s ease both; }
.is-active .section-heading { animation:fadeSlide 0.4s ease both; }
.is-active .cover-title { animation:zoomIn 0.7s ease both; }
.is-active .cover-badge { animation:fadeSlide 0.5s ease 0.15s both; }
.is-active .cover-sub { animation:fadeSlide 0.5s ease 0.25s both; }
.is-active .cover-divider { animation:scaleW 0.5s ease 0.35s both; }
.is-active .cover-meta { animation:fadeSlide 0.5s ease 0.45s both; }
.is-active .section-divider { animation:zoomIn 0.6s ease both; }

/* Stagger delays */
.is-active .bullet-card:nth-child(1) { animation-delay:0.05s; }
.is-active .bullet-card:nth-child(2) { animation-delay:0.1s; }
.is-active .bullet-card:nth-child(3) { animation-delay:0.15s; }
.is-active .bullet-card:nth-child(4) { animation-delay:0.2s; }
.is-active .bullet-card:nth-child(5) { animation-delay:0.25s; }
.is-active .bullet-card:nth-child(6) { animation-delay:0.3s; }
.is-active .bullet-card:nth-child(7) { animation-delay:0.35s; }
.is-active .bullet-card:nth-child(8) { animation-delay:0.4s; }
.is-active .step-card:nth-child(1) { animation-delay:0.05s; }
.is-active .step-card:nth-child(2) { animation-delay:0.1s; }
.is-active .step-card:nth-child(3) { animation-delay:0.15s; }
.is-active .step-card:nth-child(4) { animation-delay:0.2s; }
.is-active .obj-card-r:nth-child(1) { animation-delay:0.05s; }
.is-active .obj-card-r:nth-child(2) { animation-delay:0.1s; }
.is-active .obj-card-r:nth-child(3) { animation-delay:0.15s; }
.is-active .check-card:nth-child(1) { animation-delay:0.05s; }
.is-active .check-card:nth-child(2) { animation-delay:0.1s; }

@keyframes slideUp { from{opacity:0;transform:translateY(30px)} to{opacity:1;transform:translateY(0)} }
@keyframes cardIn { from{opacity:0;transform:translateX(-20px) scale(0.97)} to{opacity:1;transform:translateX(0) scale(1)} }
@keyframes fadeSlide { from{opacity:0;transform:translateY(15px)} to{opacity:1;transform:translateY(0)} }
@keyframes zoomIn { from{opacity:0;transform:scale(0.9)} to{opacity:1;transform:scale(1)} }
@keyframes popIn { from{opacity:0;transform:scale(0.95)} to{opacity:1;transform:scale(1)} }
@keyframes scaleW { from{transform:scaleX(0)} to{transform:scaleX(1)} }
"""


def build(deck, deck_dir=None):
    slides = deck["slides"]; n = len(slides); title = deck["title"]; ar = "assets"
    h = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{title}</title>',
         f'<link rel="stylesheet" href="{ar}/fonts.css">',
         f'<link rel="stylesheet" href="{ar}/base.css">',
         '<link rel="stylesheet" href="style.css">',
         f'<link rel="stylesheet" id="theme-link" href="{ar}/themes/{DEFAULT_THEME}.css">',
         f'</head><body class="" data-themes="{",".join(ALL_THEMES)}" data-theme-base="{ar}/themes/"><div class="deck">']
    for i,s in enumerate(slides):
        if s["type"]=="cover" or i==0:
            sl = build_cover(s,i,n,title)
        else:
            # Check if it can be a section divider (every ~5 slides)
            if i>0 and i%5==0 and len(s.get("body",[]))<3:
                sl = build_section_divider(s,i,n,title)
            else:
                sl = build_content_rich(s,i,n,title)
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
