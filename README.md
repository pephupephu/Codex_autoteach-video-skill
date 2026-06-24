# Autoteach Video Skill

**AI教学文本 → 精美PPT → 教学视频 全自动流水线**  
**AI Teaching Text → Beautiful PPT → Teaching Video — Fully Automated Pipeline**

---

## 📖 简介 | Introduction

**中文**：只需提供教学文本（Markdown或带`===`分隔线的纯文本），一键生成带语音旁白的精美教学视频，全程无需人工干预。

**English**: Just provide your teaching text (Markdown or plain text with `===` section dividers) and get a polished teaching video with TTS narration in one command — fully automated from start to finish.

---

## ✨ 功能特点 | Features

| 中文 | English |
|------|---------|
| 📊 **智能解析**：自动识别 `## Markdown` 和 `===` 分隔线两种格式 | 📊 **Smart parsing**: Auto-detects `## Markdown` and `===` section formats |
| 🎨 **36种主题**：Tokyo Night、Cyberpunk、学术论文等一键切换 | 🎨 **36 themes**: Tokyo Night, Cyberpunk, Academic, and more |
| 🎬 **丰富动画**：卡片逐条滑入、封面弹入、悬停上浮等12种动效 | 🎬 **Rich animations**: Stagger card entry, cover bounce, hover lift |
| 🗣️ **智能口播**：自动生成自然教学讲解稿，而非直接读文本 | 🗣️ **Smart narration**: Auto-generates natural teaching scripts |
| 🎥 **高清视频**：1920×1080 H.264 + AAC，完美适配教学场景 | 🎥 **HD video**: 1920×1080 H.264 + AAC, perfect for teaching |
| 🌐 **交互式HTML**：附带可交互HTML版本，支持键盘快捷键 | 🌐 **Interactive HTML**: Bonus HTML deck with keyboard shortcuts |

---

## 📋 前置依赖 | Prerequisites

| 工具 | 说明 | 安装 |
|------|------|------|
| **Python 3.8+** | 运行PPT生成和工具脚本 | [python.org](https://python.org) |
| **Microsoft Edge** | Headless网页截图 | 系统内置 |
| **FFmpeg** | 视频合成 | `winget install ffmpeg` |
| **edge-tts** | 文本转语音（免费离线） | `pip install edge-tts` |
| **Playwright** | 网页截图引擎 | `pip install playwright && playwright install msedge` |
| **html-ppt skill** | PPT视觉框架 | `npx skills add https://github.com/lewislulu/html-ppt-skill` |

---

## 🚀 快速使用 | Quick Start

### 一键生成 | One-click Pipeline

```powershell
# 中文: 指定教学文本即可
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.txt"

# English: Just point to your teaching file
.\scripts\teach-pipeline.ps1 -InputFile "course-material.txt"
```

### 分步执行 | Step-by-Step

```powershell
# 1. 生成HTML PPT
python scripts\generate_ppt.py "教学文本.txt" --theme tokyo-night -o D:\codex\teach-output

# 2. 渲染视频（含TTS）
.\scripts\render_video.ps1 -DeckDir "D:\codex\teach-output\<course-name>" -DurationPerSlide 15 -WithTTS
```

### 参数说明 | Parameters

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-InputFile` | 输入教学文本路径 (Input teaching text) | 必填 |
| `-DurationPerSlide` | 每页展示秒数 (Seconds per slide) | 12 |
| `-Theme` | PPT主题风格 (Theme name) | `tokyo-night` |
| `-OutputDir` | 输出目录 (Output directory) | `D:\codex\teach-output` |
| `-NoTTS` | 跳过语音生成 (Skip TTS) | 未设置 |
| `-Voice` | TTS语音角色 (TTS voice) | `zh-CN-XiaoxiaoNeural` |

---

## 🎨 主题预览 | Theme Gallery

| 风格 | 中文 | English |
|------|------|---------|
| 🌙 暗色炫酷 | `tokyo-night`, `cyberpunk-neon`, `dracula` | Dark/Neon |
| 🎓 学术报告 | `academic-paper`, `editorial-serif`, `minimal-white` | Academic |
| 💼 商务投资 | `pitch-deck-vc`, `corporate-clean`, `swiss-grid` | Business |
| 🔧 技术分享 | `blueprint`, `terminal-green`, `catppuccin-mocha` | Tech |
| 🌸 社交分享 | `xiaohongshu-white`, `soft-pastel`, `magazine-bold` | Social |
| 🏔 自然温暖 | `sunset-warm`, `arctic-cool`, `aurora` | Nature/Warm |
| 🎨 设计创意 | `bauhaus`, `glassmorphism`, `memphis-pop` | Creative |

---

## 📂 输出产物 | Output

```
输出目录/Output Dir/
  └── <课程名/Course Name>/
      ├── index.html          ← 可交互HTML PPT（按T切换主题）
      │                         Interactive HTML (press T for themes)
      ├── style.css           ← PPT样式 / PPT styles
      ├── slides.json         ← 幻灯片数据 / Slide data
      └── teaching-video.mp4  ← 成品教学视频（1920×1080）
                                Final teaching video (1920×1080)
```

---

## 📝 支持的输入格式 | Supported Input Formats

### Markdown格式（用 `##` 分页）

```markdown
# 课程标题 / Course Title

## 第一节 / Section 1
- 要点1 / Point 1
- 要点2 / Point 2

## 代码示例 / Code Example
\`\`\`python
print("Hello World")
\`\`\`
```

### 文本格式（用 `===` 分隔章节）

```
============================================
课程标题 / Course Title
============================================

============================================
一、章节标题 / Section Title
============================================
内容... / Content...
```

---

## ⌨️ 键盘快捷键 | Keyboard Shortcuts

| 按键 | 功能 | Function |
|------|------|----------|
| `←` `→` | 上一页 / 下一页 | Previous / Next |
| `T` | 循环切换主题 | Cycle themes |
| `S` | 演讲者模式 | Presenter mode |
| `F` | 全屏 | Fullscreen |
| `A` | 循环动画效果 | Cycle animations |
| `O` | 缩略图总览 | Overview |

---

## 📜 许可 | License

MIT License © 2026 [pephupephu](https://github.com/pephupephu)
