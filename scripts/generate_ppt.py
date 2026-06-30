#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI教学文本 -> 视频原生精美HTML幻灯片（专业设计版v8）

设计理念：
  - 视频优先：无PPT界面元素（页码、页眉、页脚、进度点）
  - 每页一个核心概念，逐步呈现（步进式揭示）
  - 内容驱动布局：代码/步骤/架构/总结各有专属视觉设计
  - 无AI痕迹：不使用emoji图标、有色左边框卡片、紫蓝渐变
  - 大标题排版（80px+），充足留白，SVG/Canvas视觉演示
"""
import json, os, re, sys, random, math
from datetime import datetime
from pathlib import Path
random.seed(42)

# ============================================================
# 设计令牌系统
# ============================================================
THEMES = {
    "slate": {
        "bg": "#0f1117", "bg2": "#161822", "card": "#1c1f2e",
        "card2": "#232738", "border": "#2a2e42", "text": "#e8eaed",
        "text2": "#9ba0b0", "text3": "#5f6577", "accent": "#7c8aff",
        "accent2": "#ff7a7a", "accent3": "#5ae0c0", "accent4": "#fabc4a",
        "grad1": "#7c8aff", "grad2": "#a78bfa"
    },
    "ocean": {
        "bg": "#0b1929", "bg2": "#0f2440", "card": "#132a4a",
        "card2": "#1a3660", "border": "#1e4080", "text": "#e0f0ff",
        "text2": "#8ab8e0", "text3": "#4a7aaa", "accent": "#4fc3ff",
        "accent2": "#ff8a80", "accent3": "#69f0ae", "accent4": "#ffd740",
        "grad1": "#4fc3ff", "grad2": "#7c4dff"
    },
    "warm": {
        "bg": "#1a1410", "bg2": "#221c16", "card": "#2d241c",
        "card2": "#3a2e24", "border": "#4a3c30", "text": "#efe8e0",
        "text2": "#c4b8a8", "text3": "#8a7a68", "accent": "#f5a97f",
        "accent2": "#ed8796", "accent3": "#a6da95", "accent4": "#eed49f",
        "grad1": "#f5a97f", "grad2": "#c6a0f6"
    },
    "forest": {
        "bg": "#0e1914", "bg2": "#14241c", "card": "#1a3024",
        "card2": "#224030", "border": "#28503c", "text": "#d8f0e0",
        "text2": "#8abc9a", "text3": "#4a7a60", "accent": "#7dda58",
        "accent2": "#ff7a7a", "accent3": "#5ae0c0", "accent4": "#fabc4a",
        "grad1": "#7dda58", "grad2": "#4fc3ff"
    }
}
DEFAULT_THEME = "slate"

def get_theme(name):
    return THEMES.get(name, THEMES[DEFAULT_THEME])

def esc(t):
    if t is None: return ""
    return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace(chr(34),"&quot;")

def deco(s):
    return bool(re.match(r"^[=\-*]{3,}$", s.strip()))

# SVG icons
SVG_ICONS = {
    "activity": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
    "alert": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "book": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>""",
    "box": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>""",
    "check": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>""",
    "checkcircle": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "code": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>""",
    "cube": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="21 16 8 22 3 14 16 8 21 16"/><line x1="3" y1="14" x2="21" y2="16"/><polyline points="8 22 8 8"/><line x1="16" y1="8" x2="16" y2="22"/></svg>""",
    "database": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "download": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>""",
    "git": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><line x1="6" y1="9" x2="6" y2="21"/></svg>""",
    "gitbranch": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>""",
    "help": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "layers": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>""",
    "lightbulb": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg>""",
    "list": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>""",
    "node": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>""",
    "server": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>""",
    "settings": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",
    "star": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>""",
    "target": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "terminal": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>""",
    "zap": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
}

def get_icon(title, stype):
    kw_map = [
        (["环境","配置","设置","安装","部署","setup","install","requirements"], "settings"),
        (["代码","示例","实现","函数","code","example","api","编译","构建"], "code"),
        (["目标","大纲","学习","objectives","goal","目的"], "target"),
        (["总结","小结","回顾","summary","conclusion"], "check"),
        (["步骤","流程","工作流","step","workflow"], "layers"),
        (["架构","设计","结构","architecture","design"], "cube"),
        (["注意","警告","提示","tip","important"], "alert"),
        (["常见问题","faq","qanda","帮助"], "help"),
        (["验证","测试","检查","test","verify"], "checkcircle"),
        (["维护","运维","更新","升级","update"], "activity"),
        (["启动","访问","run","start","server","端口"], "node"),
        (["数据","数据库","database"], "database"),
        (["硬件","内存","磁盘","cpu","性能"], "cpu"),
        (["卸载","清理","remove","clear"], "box"),
        (["集成","integration","skill","插件"], "gitbranch"),
        (["git","github","clone"], "git"),
        (["下载","安装包","download"], "download"),
        (["版本","version","兼容"], "book"),
        (["文件","目录","结构","folder"], "list"),
        (["技巧","提示","tip","小贴士"], "lightbulb"),
    ]
    for keywords, icon_name in kw_map:
        if any(k in title.lower() or k in stype.lower() for k in keywords):
            return SVG_ICONS[icon_name]
    return SVG_ICONS["node"]

# ============================================================
# Markdown 解析 (2-pass: 先找section分隔, 再分组)
# ============================================================
def parse_md(text):
    lines = text.strip().split("\n")
    course_title = "AI教学课程"
    for r in lines:
        s = r.strip()
        if s and not deco(s) and not s.startswith("目录") and not s.startswith("END"):
            course_title = s.strip("*#\t ")
            break

    sections = []
    seen = set()
    in_toc = False
    i = 0
    while i < len(lines):
        r = lines[i]; s = r.strip()
        if not s: i += 1; continue
        if s == "目录：" or s.startswith("目录"):
            in_toc = True; i += 1; continue
        if deco(s):
            if in_toc: in_toc = False
            i += 1; continue
        if r.startswith("## "):
            h = r[3:].strip()
            if h and h not in seen:
                sections.append((i, h))
                seen.add(h)
            i += 1; continue
        if re.match(r"^[一二三四五六七八九十]+[、\.\)]\s*\S", s):
            prev_deco = False
            for j in range(i-1, -1, -1):
                p = lines[j].strip()
                if deco(p): prev_deco = True; break
                if p: break
            if prev_deco and not in_toc and s not in seen:
                sections.append((i, s))
                seen.add(s)
            i += 1; continue
        i += 1

    if not sections:
        body = [{"type":"text","text": l.strip()} for l in lines if l.strip() and not deco(l)]
        return {"title": course_title, "slides": [{"title": course_title, "type": "cover", "body": body[:8]}]}

    cover_body = []
    for r in lines[:sections[0][0]]:
        s = r.strip()
        if s and not deco(s) and not s.startswith("目录") and not s.startswith("END"):
            cover_body.append({"type": "text", "text": s})

    slides = []
    if cover_body:
        slides.append({"title": course_title, "type": "cover", "body": cover_body})

    for si, (line_num, heading) in enumerate(sections):
        end_line = sections[si+1][0] if si+1 < len(sections) else len(lines)
        tl = heading.lower()
        stype = "content"
        if any(k in tl for k in ["环境","配置","设置","requirements"]): stype = "setup"
        elif any(k in tl for k in ["代码","示例","实现","安装","code"]): stype = "code"
        elif any(k in tl for k in ["总结","小结","回顾","收尾","summary","conclusion","常见问题","faq"]): stype = "summary"
        elif any(k in tl for k in ["目标","大纲","学习目标","objectives"]): stype = "objectives"
        elif any(k in tl for k in ["注意","警告","提示","tip","重要"]): stype = "callout"
        elif any(k in tl for k in ["步骤","流程","工作流"]): stype = "steps"
        elif any(k in tl for k in ["架构","设计","结构"]): stype = "architecture"
        elif any(k in tl for k in ["更新","支持","许可","license"]): stype = "summary"

        body = []
        in_code = False
        code_lines = None
        has_content = False

        for j in range(line_num+1, end_line):
            r = lines[j]; s = r.strip()
            if not s or deco(s): continue
            if s.startswith("```"):
                if in_code and code_lines is not None:
                    body.append({"type": "code", "lang": "text", "content": "\n".join(code_lines)})
                    code_lines = None; has_content = True
                in_code = not in_code
                if in_code: code_lines = []
                continue
            if in_code and code_lines is not None:
                code_lines.append(r.rstrip()); continue
            if s.startswith(("- ","* ","+ ")):
                body.append({"type": "bullet", "text": s[2:].strip()}); has_content = True; continue
            if re.match(r"^\d+[\.\)]\s", s):
                body.append({"type": "bullet", "text": s}); has_content = True; continue
            if s.startswith("【") and "】" in s:
                body.append({"type": "text", "text": "■ " + s.strip("【】")}); has_content = True; continue
            if s.startswith("|") and s.endswith("|"):
                cols = [c.strip() for c in s.strip("|").split("|")]
                if len(cols) >= 2: body.append({"type": "table_row", "cols": cols}); has_content = True
                continue
            body.append({"type": "text", "text": s}); has_content = True

        if has_content or si == len(sections)-1:
            slides.append({"title": heading, "type": stype, "body": body})

    return {"title": course_title, "slides": slides}

def build_steps_config(data):
    configs = []
    for s in data["slides"]:
        bullets = [it for it in s.get("body",[]) if it["type"]=="bullet"]
        codes = [it for it in s.get("body",[]) if it["type"]=="code"]
        texts = [it for it in s.get("body",[]) if it["type"]=="text"]
        total = len(bullets) + len(codes) + len(texts)
        configs.append({"steps": max(1, total), "title": s["title"], "type": s["type"]})
    return configs

def build_cover(slide, idx, total, course_title, theme):
    t = THEMES.get(theme, THEMES[DEFAULT_THEME])
    body = slide.get("body", [])
    icon_svg = get_icon(course_title, "cover")
    meta_lines = []
    for b in body:
        txt = b.get("text","")
        if "\u7248\u672c" in txt or ("v" in txt and re.search(r"\d", txt)):
            meta_lines.append(txt.strip("#*\t "))
        if "\u9002\u7528" in txt:
            meta_lines.append(txt.strip("#*\t "))
    meta_str = " | ".join(meta_lines[:2])

    subtitles = [b.get("text","") for b in body if len(b.get("text","")) > 5 and b.get("text","") != course_title]
    subtitle = subtitles[0] if subtitles else ""

    dots_html = "".join('<span class="cdot' + (' active"' if i==0 else '"') + '></span>' for i in range(min(total,12)))

    html = '''  <section class="slide cover-slide" data-title="''' + esc(course_title) + '''" data-type="cover">
    <canvas class="cover-canvas" id="cover-canvas-''' + str(idx) + '''"></canvas>
    <div class="cover-overlay"></div>
    <div class="cover-content">
      <div class="cover-icon-svg">''' + icon_svg + '''</div>
      <div class="cover-label">AI\u6559\u5b66\u8bfe\u7a0b</div>
      <h1 class="cover-title">''' + esc(course_title) + '''</h1>
      <div class="cover-title-underline"></div>
'''
    if subtitle:
        html += '''      <p class="cover-subtitle">''' + esc(subtitle) + '''</p>
'''
    html += '''      <div class="cover-meta">''' + esc(meta_str) + '''</div>
      <div class="cover-dots">''' + dots_html + '''</div>
    </div>
    <div class="cover-edge top-edge"></div>
    <div class="cover-edge bottom-edge"></div>
  </section>'''
    return html
# build_content_slide
def build_content_slide(slide, idx, total, course_title, theme):
    t = THEMES.get(theme, THEMES[DEFAULT_THEME])
    title = slide["title"]
    stype = slide["type"]
    body = slide.get("body", [])
    icon_svg = get_icon(title, stype)

    bullets = [it for it in body if it["type"] == "bullet"]
    texts = [it for it in body if it["type"] == "text"]
    codes = [it for it in body if it["type"] == "code"]
    tables = [it for it in body if it["type"] == "table_row"]

    labels = {'setup':'环境配置','code':'代码示例','steps':'操作步骤','summary':'要点总结','callout':'注意事项','objectives':'学习目标','architecture':'架构分析','content':'正文内容'}
    label = labels.get(stype, "正文内容")

    lines = []
    lines.append('  <section class="slide content-slide" data-title="' + esc(title) + '" data-type="' + stype + '">')
    lines.append('    <div class="slide-bg"></div>')
    lines.append('    <div class="slide-category"><span class="cat-icon">' + icon_svg + '</span><span class="cat-label">' + esc(label) + '</span></div>')
    lines.append('    <h2 class="slide-title">' + esc(title) + '</h2>')
    lines.append('    <div class="slide-title-bar"><span class="bar-fill" style="width:0%%"></span></div>')

    if stype == "code":
        lines.append('    <div class="code-container">')
        for tx in texts[:1]:
            lines.append('      <div class="code-desc step-item">' + esc(tx['text']) + '</div>')
        for c in codes:
            lines.append('      <div class="code-block step-item"><div class="code-bar"><span class="cb-dot r"></span><span class="cb-dot y"></span><span class="cb-dot g"></span></div><pre class="code-pre"><code>' + esc(c['content']) + '</code></pre></div>')
        for b in bullets:
            lines.append('      <div class="code-annotation step-item"><span class="ca-arrow">\u2192</span> ' + esc(b['text']) + '</div>')
        lines.append('    </div>')

    elif stype in ("setup", "steps"):
        lines.append('    <div class="steps-container">')
        cs = ['#7c8aff','#5ae0c0','#fabc4a','#ff7a7a','#a78bfa','#4fc3ff']
        for ib, b in enumerate(bullets):
            cc = cs[ib % 6]
            lines.append('      <div class="step-item step-row" style="border-color:' + cc + '40"><div class="step-num" style="background:' + cc + '">' + str(ib+1) + '</div><div class="step-text">' + esc(b['text']) + '</div></div>')
        for tx in texts:
            lines.append('      <div class="step-item step-note"><span class="sn-icon">\u2192</span> ' + esc(tx['text']) + '</div>')
        lines.append('    </div>')

    elif stype == "summary":
        lines.append('    <div class="summary-container">')
        for b in bullets:
            lines.append('      <div class="summary-item step-item"><span class="si-check"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"20 6 9 17 4 12\"/></svg></span><span class="si-text">' + esc(b['text']) + '</span></div>')
        for tx in texts:
            lines.append('      <div class="summary-item step-item info"><span class="si-icon">\u24D8</span><span class="si-text">' + esc(tx['text']) + '</span></div>')
        lines.append('    </div>')

    elif stype == "callout":
        lines.append('    <div class="callout-container">')
        lines.append('      <div class="callout-card step-item"><div class="callout-header"><span class="callout-icon">' + SVG_ICONS['alert'] + '</span><span class="callout-title">' + esc(title) + '</span></div><div class="callout-body">')
        for tx in texts:
            lines.append('        <p>' + esc(tx['text']) + '</p>')
        for b in bullets:
            lines.append('        <div class="callout-point"><span class="cp-dot"></span> ' + esc(b['text']) + '</div>')
        lines.append('      </div></div></div>')

    elif stype == "architecture":
        lines.append('    <div class="arch-container">')
        all_items = bullets + [{'type':'bullet','text':tx['text']} for tx in texts]
        for ib in range(0, len(all_items), 2):
            pair = all_items[ib:ib+2]
            lines.append('      <div class="arch-row step-item">')
            for item in pair:
                txt = item['text']
                for ch in '\u2514\u251c\u2500\u2502': txt = txt.replace(ch, '')
                lines.append('        <div class="arch-card"><div class="arch-icon">' + SVG_ICONS['box'] + '</div><div class="arch-text">' + esc(txt.strip()) + '</div></div>')
            lines.append('      </div>')
        lines.append('    </div>')

    elif stype == "objectives":
        lines.append('    <div class="obj-container">')
        cs2 = ['#7c8aff','#5ae0c0','#fabc4a','#ff7a7a']
        for ib, b in enumerate(bullets):
            cc = cs2[ib % 4]
            lines.append('      <div class="obj-card step-item"><div class="obj-num" style="background:' + cc + '20;color:' + cc + '">' + str(ib+1) + '</div><div class="obj-text">' + esc(b['text']) + '</div></div>')
        lines.append('    </div>')

    else:
        lines.append('    <div class="content-container">')
        for tx in texts:
            if '\u25a0' in tx['text']:
                lines.append('      <div class="content-section-header step-item">' + esc(tx['text'].replace('\u25a0 ', '')) + '</div>')
            else:
                lines.append('      <div class="content-text step-item">' + esc(tx['text']) + '</div>')
        cs3 = ['#7c8aff','#5ae0c0','#fabc4a','#ff7a7a']
        for ib, b in enumerate(bullets):
            lines.append('      <div class="content-bullet step-item"><span class="bullet-dot" style="background:' + cs3[ib%4] + '"></span><span>' + esc(b['text']) + '</span></div>')
        if tables:
            lines.append('      <div class="content-table-wrap step-item"><table class="content-table">')
            for tr in tables:
                lines.append('        <tr>' + ''.join('<td>' + esc(c) + '</td>' for c in tr['cols']) + '</tr>')
            lines.append('      </table></div>')
        for c in codes:
            lines.append('      <div class="inline-code step-item"><pre>' + esc(c['content']) + '</pre></div>')
        lines.append('    </div>')

    lines.append('  </section>')
    return '\n'.join(lines)

def generate_css(theme_name):
    t = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    BG = t['bg']; BG2 = t['bg2']; CARD = t['card']; CARD2 = t['card2']
    BORDER = t['border']; TXT = t['text']; TXT2 = t['text2']; TXT3 = t['text3']
    ACC = t['accent']; ACC2 = t['accent2']; ACC3 = t['accent3']; ACC4 = t['accent4']
    G1 = t['grad1']; G2 = t['grad2']
    
    return f'''/* === Video-Native Slide Design v8 === */
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:{BG};font-family:"Noto Sans SC",-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:{TXT};}}
.deck{{position:relative;width:1920px;height:1080px;}}
.slide{{position:absolute;top:0;left:0;width:1920px;height:1080px;overflow:hidden;opacity:0;pointer-events:none;transition:opacity 0.4s ease;}}
.slide.is-active{{opacity:1;pointer-events:auto;z-index:10;}}
.slide-bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 30% 20%,{BG2} 0%,{BG} 70%);}}
.cover-slide{{display:flex;align-items:center;justify-content:center;}}
.cover-canvas{{position:absolute;inset:0;z-index:1;}}
.cover-overlay{{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 40%,{BG}a0 100%);z-index:2;}}
.cover-content{{position:relative;z-index:3;text-align:center;max-width:1400px;padding:60px;}}
.cover-icon-svg{{width:72px;height:72px;margin:0 auto 24px;color:{ACC};opacity:0;animation:fadeScale 0.6s 0.2s ease forwards;}}
.cover-icon-svg svg{{width:100%;height:100%;}}
.cover-label{{display:inline-block;font-size:14px;letter-spacing:4px;color:{ACC};border:1px solid {ACC}40;padding:6px 20px;margin-bottom:28px;opacity:0;animation:fadeSlideU 0.5s 0.4s ease forwards;}}
.cover-title{{font-size:82px;font-weight:700;line-height:1.15;letter-spacing:-1px;margin-bottom:16px;opacity:0;animation:fadeSlideU 0.6s 0.6s ease forwards;}}
.cover-title-underline{{width:0;height:3px;margin:0 auto 20px;background:linear-gradient(90deg,{G1},{G2});animation:expandW 0.8s 1.0s ease forwards;}}
.cover-subtitle{{font-size:28px;color:{TXT2};line-height:1.6;margin-bottom:20px;opacity:0;animation:fadeSlideU 0.5s 0.9s ease forwards;}}
.cover-meta{{font-size:16px;color:{TXT3};margin-top:36px;opacity:0;animation:fadeSlideU 0.4s 1.2s ease forwards;}}
.cover-dots{{margin-top:40px;display:flex;justify-content:center;gap:8px;opacity:0;animation:fadeSlideU 0.4s 1.4s ease forwards;}}
.cdot{{width:8px;height:8px;border-radius:50%;background:{TXT3};}}
.cdot.active{{background:{ACC};}}
.cover-edge{{position:absolute;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,{ACC}40,transparent);z-index:2;}}
.top-edge{{top:0;}}.bottom-edge{{bottom:0;}}
.slide-category{{position:absolute;top:32px;left:48px;z-index:5;display:flex;align-items:center;gap:10px;opacity:0;animation:fadeSlideU 0.4s 0.1s ease forwards;}}
.cat-icon{{width:22px;height:22px;color:{ACC};}}
.cat-icon svg{{width:100%;height:100%;}}
.cat-label{{font-size:13px;letter-spacing:3px;color:{ACC};}}
.slide-title{{position:absolute;top:28px;left:48px;right:48px;font-size:52px;font-weight:700;letter-spacing:-0.5px;line-height:1.2;padding-left:34px;z-index:4;opacity:0;animation:fadeSlideU 0.5s 0.15s ease forwards;}}
.slide-title-bar{{position:absolute;top:92px;left:82px;right:48px;height:2px;background:{BORDER};z-index:4;}}
.slide-title-bar .bar-fill{{display:block;height:100%;background:linear-gradient(90deg,{G1},{G2});}}
.content-container,.code-container,.steps-container,.summary-container,.callout-container,.arch-container,.obj-container{{position:absolute;top:120px;left:80px;right:80px;bottom:60px;overflow-y:auto;}}
.content-container{{padding-top:16px;}}
.step-item{{opacity:0;transform:translateY(16px);}}
.step-item.visible{{opacity:1;transform:translateY(0);transition:opacity 0.4s ease,transform 0.4s ease;}}
.content-text{{font-size:22px;color:{TXT2};line-height:1.7;margin-bottom:14px;}}
.content-section-header{{font-size:26px;font-weight:600;color:{ACC};margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid {BORDER};}}
.content-bullet{{display:flex;align-items:flex-start;gap:14px;font-size:24px;line-height:1.6;color:{TXT};margin-bottom:12px;}}
.bullet-dot{{min-width:10px;min-height:10px;width:10px;height:10px;border-radius:50%;margin-top:10px;}}
.content-table-wrap{{margin:16px 0;overflow-x:auto;}}
.content-table{{width:100%;border-collapse:collapse;font-size:18px;}}
.content-table td{{padding:10px 16px;border-bottom:1px solid {BORDER};color:{TXT2};}}
.content-table tr:first-child td{{border-top:2px solid {ACC};font-weight:600;color:{TXT};}}
.inline-code{{background:{CARD};border-radius:6px;padding:16px 20px;margin:10px 0;font-family:'JetBrains Mono',monospace;font-size:15px;overflow-x:auto;color:{ACC3};border:1px solid {BORDER};}}
.code-container{{display:flex;flex-direction:column;gap:10px;padding-top:12px;}}
.code-desc{{font-size:22px;color:{TXT2};line-height:1.6;padding-bottom:6px;}}
.code-block{{border-radius:8px;overflow:hidden;border:1px solid {BORDER};background:{CARD};}}
.code-bar{{display:flex;align-items:center;gap:8px;padding:10px 16px;background:{CARD2};}}
.cb-dot{{width:10px;height:10px;border-radius:50%;}}
.cb-dot.r{{background:#ff5f57;}}.cb-dot.y{{background:#ffbd2e;}}.cb-dot.g{{background:#28c840;}}
.code-pre{{padding:20px 24px;margin:0;font-family:'JetBrains Mono',monospace;font-size:16px;line-height:1.7;overflow-x:auto;color:{ACC3};}}
.code-annotation{{font-size:18px;color:{TXT2};display:flex;align-items:center;gap:8px;background:{CARD};padding:10px 16px;border-radius:6px;border:1px solid {BORDER};}}
.ca-arrow{{color:{ACC};font-size:16px;}}
.steps-container{{display:flex;flex-direction:column;gap:10px;padding-top:8px;}}
.step-row{{display:flex;align-items:center;gap:18px;padding:16px 20px;background:{CARD};border-radius:8px;border:1px solid {BORDER};}}
.step-num{{min-width:36px;min-height:36px;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:#fff;}}
.step-text{{font-size:22px;line-height:1.5;}}
.step-note{{display:flex;align-items:center;gap:10px;font-size:20px;color:{TXT2};padding:10px 16px;}}
.sn-icon{{color:{ACC};}}
.summary-container{{display:flex;flex-direction:column;gap:12px;padding-top:16px;}}
.summary-item{{display:flex;align-items:center;gap:16px;padding:14px 20px;border-radius:6px;background:{CARD};border:1px solid {BORDER};}}
.summary-item.info{{border-color:{ACC}30;}}
.si-check{{width:26px;min-width:26px;}}
.si-check svg{{width:26px;height:26px;}}
.si-icon{{width:26px;height:26px;border-radius:50%;background:{ACC}20;color:{ACC};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;min-width:26px;}}
.si-text{{font-size:22px;line-height:1.5;}}
.callout-container{{display:flex;align-items:center;justify-content:center;height:100%;}}
.callout-card{{max-width:1100px;width:90%;padding:48px 56px;background:linear-gradient(135deg,{CARD},{CARD2});border-radius:12px;border:1px solid {ACC2}40;}}
.callout-header{{display:flex;align-items:center;gap:14px;margin-bottom:20px;}}
.callout-icon{{width:32px;height:32px;color:{ACC2};}}
.callout-icon svg{{width:100%;height:100%;}}
.callout-title{{font-size:28px;font-weight:600;}}
.callout-body p{{font-size:22px;color:{TXT2};line-height:1.7;margin-bottom:12px;}}
.callout-point{{display:flex;align-items:flex-start;gap:10px;font-size:20px;color:{TXT};padding:6px 0;}}
.cp-dot{{min-width:6px;min-height:6px;width:6px;height:6px;border-radius:50%;background:{ACC2};margin-top:12px;}}
.arch-container{{display:flex;flex-direction:column;gap:16px;padding-top:16px;}}
.arch-row{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
.arch-card{{padding:24px;background:{CARD};border-radius:8px;border:1px solid {BORDER};display:flex;align-items:center;gap:16px;}}
.arch-icon{{width:28px;height:28px;min-width:28px;color:{ACC};}}
.arch-icon svg{{width:100%;height:100%;}}
.arch-text{{font-size:20px;line-height:1.5;color:{TXT2};}}
.obj-container{{display:flex;flex-direction:column;gap:14px;padding-top:24px;}}
.obj-card{{display:flex;align-items:center;gap:20px;padding:18px 24px;background:{CARD};border-radius:8px;border:1px solid {BORDER};}}
.obj-num{{width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;min-width:40px;}}
.obj-text{{font-size:24px;line-height:1.5;}}
@keyframes fadeSlideU{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes fadeScale{{from{{opacity:0;transform:scale(0.8);}}to{{opacity:1;transform:scale(1);}}}}
@keyframes expandW{{from{{width:0;}}to{{width:180px;}}}}
'''


# ============================================================
# Canvas粒子动画 + 步进揭示脚本
# ============================================================
CANVAS_SCRIPT = """
(function() {
  var canvases = document.querySelectorAll('.cover-canvas');
  canvases.forEach(function(canvas) {
    var ctx = canvas.getContext('2d');
    canvas.width = 1920; canvas.height = 1080;
    var particles = [];
    var count = 80;
    for (var i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * 1920, y: Math.random() * 1080,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        r: Math.random() * 2.5 + 1,
        a: Math.random() * 0.4 + 0.1
      });
    }
    function draw() {
      ctx.clearRect(0, 0, 1920, 1080);
      for (var i = 0; i < count; i++) {
        var p = particles[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = 1920; if (p.x > 1920) p.x = 0;
        if (p.y < 0) p.y = 1080; if (p.y > 1080) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(124, 138, 255, ' + p.a + ')';
        ctx.fill();
        for (var j = i + 1; j < count; j++) {
          var p2 = particles[j];
          var dx = p.x - p2.x, dy = p.y - p2.y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 180) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = 'rgba(124, 138, 255, ' + (0.06 * (1 - dist / 180)) + ')';
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    }
    draw();
  });
})();
"""

STEP_REVEAL_SCRIPT = """
window._maxSteps = {};
window._currentStep = 0;

function resetSteps(slide) {
  slide.querySelectorAll('.step-item').forEach(function(el) {
    el.classList.remove('visible');
  });
}

function revealAll(slide) {
  slide.querySelectorAll('.step-item').forEach(function(el) {
    el.classList.add('visible');
  });
}

function advance() {
  var active = document.querySelector('.is-active');
  if (!active) return false;
  var items = active.querySelectorAll('.step-item');
  if (items.length === 0) return false;
  var maxVis = -1;
  items.forEach(function(el, i) {
    if (el.classList.contains('visible')) maxVis = i;
  });
  var next = maxVis + 1;
  if (next < items.length) {
    items[next].classList.add('visible');
    return true;
  }
  return false;
}

// Override go() to reset steps
if (typeof go === 'function') {
  var _origGo = go;
  go = function(n) {
    var current = document.querySelector('.is-active');
    if (current) current.classList.remove('is-active');
    var slides = document.querySelectorAll('.slide');
    if (n >= 0 && n < slides.length) {
      slides[n].classList.add('is-active');
      resetSteps(slides[n]);
      revealAll(slides[n]);
    }
  };
}

// Show all by default
document.querySelectorAll('.slide').forEach(function(sl) {
  revealAll(sl);
});
// Activate first slide
var firstSlide = document.querySelector('.slide');
if (firstSlide) { firstSlide.classList.add('is-active'); }
"""

# ============================================================
# Main build function
# ============================================================
def build(data, theme=DEFAULT_THEME):
    slides = data["slides"]
    total = len(slides)
    course_title = data["title"]
    css = generate_css(theme)

    html_parts = []
    html_parts.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(course_title) + '</title><style>' + css + '</style></head><body><div class="deck">')

    for i, s in enumerate(slides):
        if s["type"] == "cover" or i == 0:
            slide_html = build_cover(s, i, total, course_title, theme)
            if i == 0:
                slide_html = slide_html.replace('class="slide cover-slide"', 'class="slide cover-slide is-active"', 1)
        else:
            slide_html = build_content_slide(s, i, total, course_title, theme)
        html_parts.append(slide_html)

    html_parts.append('</div><script>' + STEP_REVEAL_SCRIPT + CANVAS_SCRIPT + '</script></body></html>')
    return '\n'.join(html_parts)

# ============================================================
# CLI entry
# ============================================================
def main():
    import argparse
    ap = argparse.ArgumentParser(description="AI教学文本 -> 视频原生精美HTML幻灯片 (v8)")
    ap.add_argument("input", help="输入Markdown教学文本路径")
    ap.add_argument("--theme", default=DEFAULT_THEME, choices=list(THEMES.keys()), help="主题风格")
    ap.add_argument("-o", "--output", default=None, help="输出目录")
    a = ap.parse_args()

    with open(a.input, "r", encoding="utf-8-sig") as f_in:
        data = parse_md(f_in.read())

    slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', data['title']).strip('-')[:40] or 'teaching-deck'
    base_dir = Path(a.output) if a.output else Path("D:/codex/teach-output")
    out_dir = base_dir / slug
    html = build(data, a.theme)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    slides_json = json.dumps(data, ensure_ascii=False, indent=2)
    (out_dir / "slides.json").write_text(slides_json, encoding="utf-8")

    steps_config = build_steps_config(data)
    (out_dir / "steps.json").write_text(json.dumps(steps_config, ensure_ascii=False), encoding="utf-8")

    slide_count = len(data.get("slides", []))
    print(f"[DONE] {slide_count} slides generated")
    out_path = str(out_dir)
    print(f"  Output: {out_path}")
    course_name = data.get("title", "")
    print(f"  Course: {course_name}")
    print(f"  Theme: {a.theme}")

if __name__ == '__main__':
    main()
