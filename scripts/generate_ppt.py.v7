#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI教学文本 -> 精美HTML教学PPT 生成器（v7 - 专业设计版）"""
import json, os, re, sys, random
from datetime import datetime
from pathlib import Path
random.seed(42)

def fa():
    c=[Path.home()/".codex"/"skills"/"html-ppt"/"assets",Path(os.environ.get("CODEX_HOME",""))/"skills"/"html-ppt"/"assets"]
    for p in c:
        if(p/"themes").is_dir()and(p/"runtime.js").exists():return p.resolve()
    raise FileNotFoundError("html-ppt assets not found")
SKILL_A=fa()
ALL_T=["academic-paper","aurora","bauhaus","blueprint","catppuccin-mocha","corporate-clean","cyberpunk-neon","dracula","editorial-serif","glassmorphism","japanese-minimal","magazine-bold","memphis-pop","midcentury","minimal-white","neo-brutalism","news-broadcast","nord","pitch-deck-vc","rainbow-gradient","retro-tv","rose-pine","sharp-mono","soft-pastel","solarized-light","sunset-warm","swiss-grid","terminal-green","tokyo-night","vaporwave","xiaohongshu-white","y2k-chrome","engineering-whiteprint","gruvbox-dark","catppuccin-latte"]
DT="tokyo-night"
def esc(t):return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def deco(s):return bool(re.match(r"^[=\-*]{3,}$",s.strip()))
def icon(k):
    m={"环境|配置|设置|安装|部署|setup|install":"⚙️","代码|示例|实现|函数|code|example|api":"💻","目标|大纲|学习|objectives|goal":"🎯","总结|小结|回顾|summary":"📝","注意|警告|提示|tip|note":"⚠️","数据|架构|设计|structure":"🏗️","步骤|流程|工作流|step|workflow":"🔄","常见问题|faq|q&a":"❓","验证|测试|检查|test|verify":"✅","维护|运维|日常":"🔧","卸载|清理|remove":"🗑️","启动|访问|run|start":"🚀","集成|integration|skill":"🧩","算法|聚类|affinity":"🧮","更新|升级|update":"🔄","备份|backup":"💾","硬件|内存|磁盘|cpu":"🖥️"}
    for p,i in m.items():
        if re.search(p,k,re.I):return i
    return "📌"
def col(i):
    cs=["#6366f1","#ec4899","#14b8a6","#f59e0b","#8b5cf6","#06b6d4","#84cc16","#f97316","#e11d48","#0ea5e9"]
    return cs[i%len(cs)]
def pmd(t):
    ls=t.strip().split("\n")
    dt="AI教学课程"
    for r in ls:
        s=r.strip()
        if s and not deco(s)and not s.startswith("目录")and not s.startswith("END"):
            dt=s.strip("*#\t ");break
    it=False;rs=[];se=set()
    i=0
    while i<len(ls):
        r=ls[i];s=r.strip()
        if not s:i+=1;continue
        if s=="目录："or s.startswith("目录"):it=True;i+=1;continue
        if deco(s):it=False;i+=1;continue
        if r.startswith("## "):
            h=r[3:].strip()
            if h and h not in se:rs.append((i,h));se.add(h)
            i+=1;continue
        if re.match(r"^[一二三四五六七八九十]+[、\.\)]\s*\S",s):
            pd=False
            for j in range(i-1,-1,-1):
                p=ls[j].strip()
                if deco(p):pd=True;break
                if p:break
            if pd and not it and s not in se:rs.append((i,s));se.add(s)
            i+=1;continue
        i+=1
    if not rs:
        b=[{"type":"text","text":l.strip()}for l in ls if l.strip()and not deco(l)]
        return{"title":dt,"slides":[{"title":dt,"type":"cover","body":b[:8]}]}
    sl=[]
    cb=[]
    for r in ls[:rs[0][0]]:
        s=r.strip()
        if s and not deco(s)and not s.startswith("目录")and not s.startswith("END"):
            cb.append({"type":"text","text":s})
    if cb:sl.append({"title":dt,"type":"cover","body":cb})
    for si,(sl_,h)in enumerate(rs):
        el=rs[si+1][0] if si+1<len(rs)else len(ls)
        tl=h.lower()
        tp="content"
        if any(k in tl for k in["环境","配置","设置","requirements"]):tp="setup"
        elif any(k in tl for k in["代码","示例","实现","安装","code"]):tp="code"
        elif any(k in tl for k in["总结","小结","回顾","收尾","summary","conclusion","常见问题","faq"]):tp="summary"
        elif any(k in tl for k in["目标","大纲","学习目标","objectives"]):tp="objectives"
        elif any(k in tl for k in["注意","警告","提示","tip","重要"]):tp="callout"
        elif any(k in tl for k in["步骤","流程","工作流"]):tp="steps"
        elif any(k in tl for k in["架构","设计","结构"]):tp="architecture"
        bd=[];ic=False;cb_=None;hc=False
        for j in range(sl_+1,el):
            r=ls[j];s=r.strip()
            if not s or deco(s):continue
            if s.startswith("```"):
                if ic and cb_:bd.append({"type":"code","lang":"text","content":"\n".join(cb_)});cb_=None;hc=True
                ic=not ic
                if ic:cb_=[]
                continue
            if ic and cb_ is not None:cb_.append(r.rstrip());continue
            if s.startswith(("- ","* ","+ ")):bd.append({"type":"bullet","text":s[2:].strip()});hc=True;continue
            if re.match(r"^\d+[\.\)]\s",s):bd.append({"type":"bullet","text":s});hc=True;continue
            if s.startswith("【")and"】"in s:bd.append({"type":"text","text":"■ "+s.strip("【】")});hc=True;continue
            if s.startswith("|")and s.endswith("|"):
                cl=[c.strip()for c in s.strip("|").split("|")]
                if len(cl)>=2:bd.append({"type":"table_row","cols":cl});hc=True
                continue
            bd.append({"type":"text","text":s});hc=True
        if hc or si==len(rs)-1:sl.append({"title":h,"type":tp,"body":bd})
    return{"title":dt,"slides":sl}
def bcover(s,i,n,t):
    bd=s.get("body",[]);ic=icon(t)
    mt=[it["text"]for it in bd[:4]]
    sb=mt[1]if len(mt)>=2 else""
    ln=[f'  <section class="slide cover-slide" data-title="{esc(t)}">']
    ln.append('    <div class="cover-gradient"></div>')
    ln.append("""    <div class="cover-pattern">""" + "".join(f'<div class="deco-shape" style="left:{random.randint(3,94)}%;top:{random.randint(5,90)}%;width:{random.choice([40,60,80,120])}px;height:{random.choice([40,60,80,120])}px;animation-delay:{random.uniform(0,2):.1f}s;border-radius:{random.choice(["50%","30%","10%","40% 60%"])}"></div>' for _ in range(5)) + """</div>""")
    ln.append('    <div class="cover-content">')
    ln.append(f'      <div class="cover-icon-wrap"><span class="cover-icon">{ic}</span></div>')
    ln.append('      <div class="cover-badge">AI教学课程</div>')
    ln.append(f'      <h1 class="cover-title">{esc(t)}</h1>')
    if sb:ln.append(f'      <p class="cover-subtitle">{esc(sb)}</p>')
    ln.append('      <div class="cover-divider"></div>')
    ln.append(f'      <div class="cover-meta"><span class="meta-item">📅 {datetime.now().strftime("%Y-%m-%d")}</span><span class="meta-item">📄 {n}页</span></div>')
    ln.append('    </div><div class="cover-bar"></div></section>')
    return"\n".join(ln)
def bdivider(s,i,n,t):
    ic=icon(s["title"])
    return f'  <section class="slide divider-slide" data-title="{esc(s["title"])}"><div class="divider-bg"></div><div class="divider-content"><span class="divider-num">{i}</span><span class="divider-icon">{ic}</span><h2 class="divider-title">{esc(s["title"])}</h2><div class="divider-line"></div></div></section>'
def bcontent(s,i,n,t):
    bd=s.get("body",[]);tp=s["type"];st=s["title"]
    ic=icon(st)
    ln=[f'  <section class="slide" data-title="{esc(st)}">']
    ln.append('    <div class="slide-ambient"><div class="ambient-1"></div><div class="ambient-2"></div></div>')
    ln.append(f'    <div class="slide-header-bar"><span class="header-icon">{ic}</span><span class="header-title">{esc(st)}</span><span class="header-dots">{"".join(["●"if _==i else"○"for _ in range(n)])}</span><span class="header-num">{i}/{n}</span></div>')
    bu=[it for it in bd if it["type"]=="bullet"];tx=[it for it in bd if it["type"]=="text"]
    cd=[it for it in bd if it["type"]=="code"];tb=[it for it in bd if it["type"]=="table_row"]
    if tp=="code":
        ln.append('    <div class="code-window"><div class="code-titlebar"><span class="win-dot r"></span><span class="win-dot y"></span><span class="win-dot g"></span><span class="win-label">'+esc(st)+'</span></div>')
        if tx:ln.append(f'      <div class="code-intro">{esc(tx[0]["text"])}</div>')
        for c in cd:ln.append(f'      <pre class="code-content"><code>{esc(c["content"])}</code></pre>')
        for b in bu:ln.append(f'      <div class="code-note"><span class="note-arrow">➜</span>{esc(b["text"])}</div>')
        ln.append('    </div>')
    elif tp=="summary":
        ln.append(f'    <div class="summary-section"><h2 class="section-title-anim"><span class="title-icon">📋</span> {esc(st)}</h2><div class="check-grid">')
        for b in bu:ln.append(f'        <div class="check-item"><span class="check-mark">✓</span><span>{esc(b["text"])}</span></div>')
        for t in tx:ln.append(f'        <div class="check-item info"><span class="check-mark info">i</span><span>{esc(t["text"])}</span></div>')
        ln.append('      </div></div>')
    elif tp in("setup","steps"):
        ln.append(f'    <div class="steps-section"><h2 class="section-title-anim"><span class="title-icon">{ic}</span> {esc(st)}</h2><div class="steps-flow">')
        for idx,b in enumerate(bu):
            cc=col(idx);ln.append(f'        <div class="step-unit" style="--sc:{cc}"><div class="step-badge" style="background:{cc}">{idx+1}</div><div class="step-content">{esc(b["text"])}</div></div>')
        for t in tx:ln.append(f'        <div class="step-unit info"><div class="step-badge info">i</div><div class="step-content">{esc(t["text"])}</div></div>')
        ln.append('      </div></div>')
    elif tp=="callout":
        ln.append('    <div class="callout-section"><div class="callout-box-big"><div class="callout-ico">⚠️</div><h3>'+esc(st)+'</h3>')
        for t in tx:ln.append(f'        <p>{esc(t["text"])}</p>')
        for b in bu:ln.append(f'        <div class="callout-bullet">• {esc(b["text"])}</div>')
        ln.append('      </div></div>')
    elif tp=="architecture":
        ln.append(f'    <div class="archi-section"><h2 class="section-title-anim"><span class="title-icon">{ic}</span> {esc(st)}</h2><div class="archi-grid">')
        for idx,b in enumerate(bu):
            cc=col(idx);ln.append(f'        <div class="archi-module" style="--mc:{cc};border-color:{cc}40"><div class="archi-hd" style="background:{cc}15;color:{cc}">{esc(b["text"])}</div></div>')
        for t in tx:ln.append(f'        <div class="archi-module"><div class="archi-hd">{esc(t["text"])}</div></div>')
        ln.append('      </div></div>')
    elif tp=="objectives":
        ln.append(f'    <div class="obj-section"><h2 class="section-title-anim"><span class="title-icon">🎯</span> {esc(st)}</h2><div class="obj-grid-prof">')
        ai=bu+[{"text":t["text"]}for t in tx]
        for idx,it in enumerate(ai):
            em=["🎯","💡","⭐","🔑","📌","🏆"][idx%6];cc=col(idx)
            ln.append(f'        <div class="obj-card-prof" style="border-left-color:{cc}"><span class="obj-emoji-prof">{em}</span><span>{esc(it.get("text",""))}</span></div>')
        ln.append('      </div></div>')
    else:
        ln.append(f'    <div class="content-section"><h2 class="section-title-anim"><span class="title-icon">{ic}</span> {esc(st)}</h2>')
        if tb:
            ln.append('      <div class="table-deck"><table class="pro-table">')
            for it in tb:
                cl=" thr"if it==tb[0]else""
                ln.append(f'        <tr class="{cl}">{"".join(f"<td>{esc(c)}</td>"for c in it["cols"])}</tr>')
            ln.append('      </table></div>')
        if len(bu)>6:
            md=(len(bu)+1)//2
            ln.append('      <div class="two-col-cards"><div class="col-cards">')
            for idx,b in enumerate(bu[:md]):
                cc=col(idx);em=["🚀","💡","🎯","🔧","📊","🛡️","⚡","🎨"][idx%8]
                ln.append(f'          <div class="content-card" style="--cc:{cc}"><span class="card-emoji">{em}</span><span>{esc(b["text"])}</span></div>')
            ln.append('        </div><div class="col-cards">')
            for idx,b in enumerate(bu[md:]):
                cc=col(idx+md);em=["🚀","💡","🎯","🔧","📊","🛡️","⚡","🎨"][(idx+md)%8]
                ln.append(f'          <div class="content-card" style="--cc:{cc}"><span class="card-emoji">{em}</span><span>{esc(b["text"])}</span></div>')
            ln.append('        </div></div>')
        elif bu:
            ln.append('      <div class="cards-stack">')
            for idx,b in enumerate(bu):
                cc=col(idx);em=["🚀","💡","🎯","🔧","📊","🛡️","⚡","🎨"][idx%8]
                ln.append(f'        <div class="content-card" style="--cc:{cc}"><span class="card-emoji">{em}</span><span>{esc(b["text"])}</span></div>')
            ln.append('      </div>')
        for t in tx:
            if t["text"].startswith("■"):ln.append(f'      <div class="tag-badge">{esc(t["text"][2:])}</div>')
            else:ln.append(f'      <p class="body-text">{esc(t["text"])}</p>')
        for c in cd:ln.append(f'      <pre class="inline-code-block"><code>{esc(c["content"])}</code></pre>')
        ln.append('    </div>')
    ln.append('  </section>')
    return"\n".join(ln)
CSS=r"""
.slide{position:absolute;top:0;left:0;width:1920px;height:1080px;display:none;overflow:hidden;box-sizing:border-box;background:var(--surface);color:var(--text-1)}
.slide.is-active{display:flex;flex-direction:column;z-index:10}
.slide-ambient{position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;overflow:hidden}
.ambient-1{position:absolute;top:-15%;right:-10%;width:70%;height:70%;border-radius:50%;background:radial-gradient(circle,var(--accent)0%,transparent 70%);opacity:0.05}
.ambient-2{position:absolute;bottom:-10%;left:-10%;width:50%;height:50%;border-radius:50%;background:radial-gradient(circle,color-mix(in srgb,var(--accent)60%,#fff)0%,transparent 70%);opacity:0.03}
.slide-header-bar{position:absolute;top:0;left:0;right:0;height:48px;display:flex;align-items:center;padding:0 48px;gap:12px;z-index:20;background:linear-gradient(180deg,var(--surface-2)0%,transparent 100%);border-bottom:1px solid var(--border);animation:headerSlide 0.5s ease both}
.header-icon{font-size:18px}
.header-title{font-size:14px;font-weight:600;color:var(--text-2);letter-spacing:0.5px}
.header-dots{margin-left:auto;font-size:10px;color:var(--text-3);letter-spacing:4px}
.header-num{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--text-3);opacity:0.6}
.deco-shape{position:absolute;border:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.02);animation:floatShape 8s ease-in-out infinite;pointer-events:none}
.cover-slide{background:var(--accent)!important;position:relative}
.cover-gradient{position:absolute;top:0;left:0;right:0;bottom:0;background:linear-gradient(135deg,var(--accent)0%,color-mix(in srgb,var(--accent)25%,#0d0d1a)100%)}
.cover-pattern{position:absolute;top:0;left:0;right:0;bottom:0;overflow:hidden}
.cover-content{position:relative;z-index:5;margin:auto;text-align:center;padding:60px 100px}
.cover-icon-wrap{display:inline-flex;width:80px;height:80px;border-radius:50%;align-items:center;justify-content:center;background:rgba(255,255,255,0.12);backdrop-filter:blur(10px);margin-bottom:16px;animation:iconBounce 1s cubic-bezier(0.34,1.56,0.64,1) both}
.cover-icon{font-size:38px}
.cover-badge{display:inline-block;padding:6px 24px;border:1px solid rgba(255,255,255,0.2);border-radius:20px;font-size:12px;color:rgba(255,255,255,0.5);letter-spacing:3px;text-transform:uppercase;margin-bottom:20px;animation:fadeSlideUp 0.6s ease 0.2s both}
.cover-title{font-size:64px;font-weight:800;letter-spacing:-2.5px;color:#fff;margin:0 0 12px;line-height:1.08;text-shadow:0 4px 40px rgba(0,0,0,0.15);animation:fadeSlideUp 0.7s ease 0.3s both}
.cover-subtitle{font-size:22px;color:rgba(255,255,255,0.6);margin:0 auto 20px;max-width:800px;line-height:1.6;animation:fadeSlideUp 0.6s ease 0.4s both}
.cover-divider{width:60px;height:3px;background:rgba(255,255,255,0.2);margin:24px auto;border-radius:2px;animation:scaleW 0.6s ease 0.5s both}
.cover-meta{display:flex;justify-content:center;gap:32px;font-size:13px;color:rgba(255,255,255,0.35);animation:fadeSlideUp 0.6s ease 0.6s both}
.meta-item{display:flex;align-items:center;gap:6px}
.cover-bar{position:absolute;bottom:0;left:0;right:0;height:3px;background:linear-gradient(90deg,rgba(255,255,255,0.4),transparent)}
.divider-slide{position:relative}
.divider-bg{position:absolute;top:0;left:0;right:0;bottom:0;background:var(--surface-2)}
.divider-content{margin:auto;text-align:center;position:relative;z-index:2;padding:40px}
.divider-num{display:block;font-size:80px;font-weight:900;color:var(--accent);opacity:0.12;font-family:"JetBrains Mono",monospace;line-height:1;margin-bottom:8px}
.divider-icon{font-size:48px;display:block;margin-bottom:12px}
.divider-title{font-size:52px;font-weight:700;color:var(--text-1);margin:0;letter-spacing:-1px}
.divider-line{width:100px;height:3px;background:var(--accent);margin:20px auto 0;border-radius:2px}
.content-section,.steps-section,.summary-section,.obj-section,.archi-section,.code-window,.callout-section{padding-top:52px;flex:1;overflow-y:auto;padding-left:48px;padding-right:40px}
.section-title-anim{font-size:32px;font-weight:700;letter-spacing:-0.5px;color:var(--text-1);margin:8px 0 20px;padding-bottom:12px;display:flex;align-items:center;gap:10px;border-bottom:2px solid var(--accent);width:fit-content;min-width:30%;animation:titleSlide 0.5s ease both}
.title-icon{font-size:28px}
.cards-stack{display:flex;flex-direction:column;gap:10px;max-width:95%}
.content-card{display:flex;align-items:center;gap:16px;padding:14px 22px;background:var(--surface-2);border-radius:10px;font-size:20px;line-height:1.5;border:1px solid var(--border);border-left:4px solid var(--cc,#6366f1);box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:all 0.3s;animation:cardSlideUp 0.5s ease both}
.content-card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,0.08)}
.card-emoji{font-size:22px;flex-shrink:0}
.two-col-cards{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.col-cards{display:flex;flex-direction:column;gap:10px}
.body-text{font-size:18px;line-height:1.7;color:var(--text-2);margin:6px 0}
.tag-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 16px;background:var(--surface-2);border-radius:6px;margin:4px 0;font-size:14px;font-weight:600;color:var(--accent);border:1px solid var(--border)}
.steps-flow{display:flex;flex-direction:column;gap:8px;max-width:90%}
.step-unit{display:flex;align-items:center;gap:16px;padding:14px 20px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);border-left:3px solid var(--sc,#6366f1);animation:cardSlideUp 0.4s ease both}
.step-badge{flex-shrink:0;width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:"JetBrains Mono",monospace;font-size:14px;font-weight:800;color:#fff}
.step-badge.info{background:var(--text-3)}
.step-content{font-size:18px;color:var(--text-1);line-height:1.5}
.step-unit.info{border-left-color:var(--text-3)}
.check-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:95%}
.check-item{display:flex;align-items:center;gap:14px;padding:14px 18px;background:var(--surface-2);border-radius:8px;font-size:17px;line-height:1.5;border:1px solid var(--border);animation:cardSlideUp 0.4s ease both}
.check-mark{flex-shrink:0;width:24px;height:24px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700}
.check-mark.info{background:var(--text-3);font-style:italic}
.obj-grid-prof{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:95%}
.obj-card-prof{display:flex;align-items:center;gap:14px;padding:16px 20px;background:var(--surface-2);border-radius:10px;font-size:17px;line-height:1.5;border:1px solid var(--border);border-left:4px solid var(--clr,#6366f1);box-shadow:0 2px 6px rgba(0,0,0,0.04);animation:cardSlideUp 0.4s ease both}
.obj-emoji-prof{font-size:24px;flex-shrink:0}
.callout-section{display:flex;align-items:center;justify-content:center}
.callout-box-big{max-width:880px;width:100%;padding:36px 44px;background:var(--surface-2);border-radius:16px;border:2px solid var(--accent);box-shadow:0 8px 32px rgba(0,0,0,0.06);animation:popIn 0.5s ease both}
.callout-ico{font-size:48px;margin-bottom:8px}
.callout-box-big h3{font-size:28px;color:var(--accent);margin:0 0 16px}
.callout-box-big p{font-size:19px;line-height:1.7;color:var(--text-1);margin:8px 0}
.callout-bullet{font-size:18px;color:var(--text-2);margin:6px 0;padding-left:16px}
.code-window{padding-top:52px;max-width:92%}
.code-titlebar{display:flex;align-items:center;gap:8px;padding:10px 18px;background:#1a1a2e;border-radius:10px 10px 0 0;border-bottom:1px solid rgba(255,255,255,0.05)}
.win-dot{width:12px;height:12px;border-radius:50%}
.win-dot.r{background:#ff5f57}
.win-dot.y{background:#febc2e}
.win-dot.g{background:#28c840}
.win-label{margin-left:auto;font-size:12px;color:rgba(255,255,255,0.25);font-family:"JetBrains Mono",monospace}
.code-content{background:#1a1a2e;color:#e4e4e7;padding:20px 24px;margin:0;font-family:"JetBrains Mono","Fira Code",monospace;font-size:13.5px;line-height:1.7;overflow-x:auto;border-radius:0 0 10px 10px;border:1px solid rgba(255,255,255,0.03)}
.code-intro{font-size:17px;color:var(--text-2);margin:8px 0}
.code-note{font-size:15px;color:var(--text-3);margin:6px 0;font-family:"JetBrains Mono",monospace}
.note-arrow{color:var(--accent);margin-right:6px}
.archi-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;max-width:95%}
.archi-module{border:2px solid var(--border);border-radius:10px;overflow:hidden;background:var(--surface-2);animation:cardSlideUp 0.4s ease both}
.archi-hd{padding:14px 16px;font-size:17px;font-weight:600}
.table-deck{margin:12px 0;max-width:95%;overflow-x:auto}
.pro-table{width:100%;border-collapse:separate;border-spacing:0;font-size:15px}
.pro-table td{padding:10px 16px;border-bottom:1px solid var(--border);color:var(--text-2)}
.pro-table .thr td{background:var(--surface-2);font-weight:600;color:var(--text-1);border-top:2px solid var(--accent)}
.inline-code-block{background:#1a1a2e;border-radius:8px;padding:14px 18px;margin:8px 0;font-family:"JetBrains Mono",monospace;font-size:13px;overflow-x:auto;color:#e4e4e7}
@keyframes floatShape{0%,100%{transform:translate(0,0)rotate(0deg)}33%{transform:translate(15px,-15px)rotate(5deg)}66%{transform:translate(-10px,10px)rotate(-3deg)}}
@keyframes iconBounce{0%{opacity:0;transform:scale(0.3)rotate(-10deg)}50%{transform:scale(1.1)rotate(3deg)}70%{transform:scale(0.9)}100%{opacity:1;transform:scale(1)rotate(0)}}
@keyframes fadeSlideUp{from{opacity:0;transform:translateY(25px)}to{opacity:1;transform:translateY(0)}}
@keyframes scaleW{from{transform:scaleX(0);opacity:0}to{transform:scaleX(1);opacity:1}}
@keyframes headerSlide{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:translateY(0)}}
@keyframes titleSlide{from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}}
@keyframes cardSlideUp{from{opacity:0;transform:translateY(20px)scale(0.98)}to{opacity:1;transform:translateY(0)scale(1)}}
@keyframes popIn{from{opacity:0;transform:scale(0.95)}to{opacity:1;transform:scale(1)}}
.is-active .content-card{animation:cardSlideUp 0.45s ease both}
.is-active .step-unit{animation:cardSlideUp 0.4s ease both}
.is-active .check-item{animation:cardSlideUp 0.4s ease both}
.is-active .obj-card-prof{animation:cardSlideUp 0.4s ease both}
.is-active .archi-module{animation:cardSlideUp 0.4s ease both}
"""

def build(d,dd=None):
    sl=d["slides"];n=len(sl);t=d["title"];ar="assets"
    h=['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
       '<meta name="viewport" content="width=device-width,initial-scale=1">',
       f'<title>{t}</title>',
       f'<link rel="stylesheet" href="{ar}/fonts.css">',
       f'<link rel="stylesheet" href="{ar}/base.css">',
       '<link rel="stylesheet" href="style.css">',
       f'<link rel="stylesheet" id="theme-link" href="{ar}/themes/{DT}.css">',
       f'</head><body class="" data-themes="{",".join(ALL_T)}" data-theme-base="{ar}/themes/"><div class="deck">']
    for i,s in enumerate(sl):
        if s["type"]=="cover"or i==0:sl_=bcover(s,i,n,t)
        elif(i>1 and i%5==0 or s["type"]=="divider")and len(s.get("body",[]))<3:sl_=bdivider(s,i,n,t)
        else:sl_=bcontent(s,i,n,t)
        if i==0:sl_=sl_.replace('class="slide"','class="slide is-active"',1)
        h.append(sl_)
    h.append('</div><script src="'+ar+'/runtime.js"></script></body></html>')
    return"\n".join(h)

def ca(dd):
    import shutil
    try:
        s=fa();d=dd/"assets"
        if d.exists():return
        d.mkdir(parents=True)
        for f in["fonts.css","base.css","runtime.js"]:shutil.copy2(s/f,d/f)
        shutil.copytree(s/"themes",d/"themes",dirs_exist_ok=True)
    except Exception as e:print(f"Warning: could not copy assets: {e}")

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("input");ap.add_argument("--theme",default=DT);ap.add_argument("-o","--output",default=None)
    a=ap.parse_args()
    with open(a.input,"r",encoding="utf-8-sig")as f:d=pmd(f.read())
    sl=re.sub(r'[^\w\u4e00-\u9fff]+','-',d["title"]).strip("-")[:40]or"teaching-deck"
    dd=(Path(a.output)if a.output else Path("D:/codex/teach-output"))/sl
    dd.mkdir(parents=True,exist_ok=True)
    (dd/"index.html").write_text(build(d,dd),encoding="utf-8")
    (dd/"style.css").write_text(CSS,encoding="utf-8")
    (dd/"slides.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    ca(dd)
    print(f"\n=== PPT Generation Complete ===");print(f"Directory: {dd}");print(f"Slides: {len(d['slides'])}")

if __name__=="__main__":main()
