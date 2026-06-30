# Codex Autoteach Video Skill 🎬

> AI教学文本 → 精美视频原生PPT → 教学视频 全自动生成 | AI Teaching Text → Video-Native Slides → Teaching Video Auto Pipeline

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-orange.svg)](https://ffmpeg.org/)

---

## 🌟 简介 | Introduction

将AI教学Markdown文本**一键自动生成**为**精美视频原生HTML教学PPT**，并录制为**带AI语音旁白的MP4教学视频**。

Transform AI teaching Markdown text into **beautiful video-native HTML slides** and record them as **MP4 teaching videos with AI voice narration**.

### 核心特性 | Key Features

- 🎯 **视频原生设计** — 无PPT痕迹（无页码、无页眉、无进度点），每页一个核心概念，步进式揭示
- 🎨 **4种专业主题** — Slate（深色专业）、Ocean（海洋蓝）、Warm（暖色调）、Forest（森林绿）
- 🖼️ **SVG图标系统** — 替代emoji，专业矢量风格
- 🎬 **Canvas粒子动画** — 封面页动态粒子效果
- 🔊 **AI语音旁白** — 基于 edge-tts，高质量中文女声
- 🎞️ **自动视频合成** — FFmpeg 合成 1920×1080 MP4
- 🔄 **全自动流水线** — 从文本到成品视频，一键完成

### Design Philosophy

- **Video-Native First**: No PPT chrome (no page numbers, headers, footers, progress dots). Every slide is a full-screen 1920×1080 canvas focused on one core concept.
- **Content-Driven Layout**: Each content type (code, steps, architecture, summary) has its own visual layout designed for maximum clarity.
- **No AI Fingerprints**: No emoji-as-icons, no colored-left-border cards, no purple-blue diagonal gradients, no pill buttons. Clean, professional vector SVG icons and geometric design.
- **Progressive Reveal**: Content appears step by step, keeping viewer attention focused on one idea at a time.

---

## 📦 安装 | Installation

### 前置依赖 | Prerequisites

1. **Python 3.8+** — 核心脚本运行
2. **Microsoft Edge** — Playwright 截图
3. **FFmpeg** — 视频合成
4. **Python 包依赖**:
```bash
pip install edge-tts playwright
playwright install msedge
```

### 安装 Skill | Install the Skill

```bash
# 通过 GitHub 安装
codex skills add https://github.com/pephupephu/Codex_autoteach-video-skill

# 或手动克隆
git clone https://github.com/pephupephu/Codex_autoteach-video-skill.git
cd Codex_autoteach-video-skill
```

---

## 🚀 使用方法 | Usage

### 一键式完整流水线 | One-Click Full Pipeline

```powershell
# 进入插件目录
cd Codex_autoteach-video-skill

# 一键生成教学视频（带TTS语音）
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.md"

# 指定主题和时长
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.md" -Theme ocean -DurationPerSlide 10
```

### 分步执行 | Step by Step

```powershell
# Step 1: 生成HTML PPT
python scripts/generate_ppt.py "你的教学文本.md" --theme slate -o ./output

# Step 2: 截图 + 渲染视频（带TTS）
python scripts/screenshot_slides.py ./output/课程名
.\scripts\render_video.ps1 -DeckDir "./output/课程名" -DurationPerSlide 12 -WithTTS
```

### 参数说明 | Parameters

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-InputFile` | 输入Markdown教学文本路径 | 必填 |
| `-DurationPerSlide` | 每页幻灯片展示秒数 | 12 |
| `-Theme` | PPT主题风格 | `slate` |
| `-OutputDir` | 输出目录 | `D:\codex\teach-output` |
| `-NoTTS` | 跳过语音旁白 | 未设置（默认生成语音） |
| `-Voice` | TTS语音角色 | `zh-CN-XiaoxiaoNeural` |

---

## 🎨 主题风格 | Themes

| 主题 | 预览色 | 特点 |
|------|--------|------|
| `slate` 🔵 | 深色专业 | 紫色点缀，最适合技术内容 |
| `ocean` 🌊 | 深海蓝 | 蓝色系，适合企业级内容 |
| `warm` 🟠 | 暖棕色 | 温暖舒适，适合教育内容 |
| `forest` 🌿 | 森林绿 | 自然清新，适合入门教程 |

---

## 📝 输入文本格式 | Input Format

支持标准Markdown，以 `==` 分隔符或 `##` 分页：

```markdown
============================================================
  课程标题
============================================================
  版本: v1.0
  简介文字

============================================================
一、章节标题
============================================================

【说明】
  要点1
  要点2

- 项目1
- 项目2

============================================================
二、代码示例
============================================================

```python
def hello():
    print("Hello World")
```

============================================================
三、总结
============================================================

- 知识点1
- 知识点2
```

**幻灯片类型自动识别：**
- 封面 → 带 Canvas 粒子特效
- 环境/配置 → Setup 布局
- 代码/示例 → 代码窗口布局
- 步骤/流程 → 步骤时间线
- 总结/回顾 → 检查清单布局
- 架构/设计 → 网格卡片布局
- 目标/大纲 → 目标卡片布局
- 注意/警告 → 强调卡片布局

---

## 📂 输出产物 | Output

```
D:\codex\teach-output\
  └── <课程名>\
      ├── index.html          ← 可交互HTML PPT
      ├── slides.json         ← 幻灯片数据
      ├── steps.json          ← 步进配置
      └── teaching-video.mp4  ← 成品教学视频（1920×1080, H.264）
```

---

## 🧠 设计理念详解 | Design Details

### 视频原生设计（Video-Native Design）

与传统PPT不同，本工具生成的每张幻灯片都是**全屏1920×1080画布**，没有任何PPT界面元素：

- ❌ 无页码
- ❌ 无页眉/页脚
- ❌ 无进度点
- ❌ 无标题栏
- ✅ 每个内容项独立呈现
- ✅ 充足留白，大标题排版（52px+）
- ✅ 步进式揭示（step-by-step reveal）

### 内容驱动布局（Content-Driven Layout）

不同类型的内容有专属视觉方案：
- **代码页** → 仿终端窗口，带红黄绿圆点
- **步骤页** → 编号时间线，彩色圆点标记
- **总结页** → 绿色对勾清单
- **架构页** → 双列网格卡片
- **目标页** → 编号目标卡片
- **注意事项** → 红色强调卡片

---

## 🔧 开发 | Development

```bash
git clone https://github.com/pephupephu/Codex_autoteach-video-skill.git
cd Codex_autoteach-video-skill

# 修改 generate_ppt.py 改进设计
# 修改 text_extract.py 改进旁白
# 修改 screenshot_slides.py 改进截图流程

# 提交贡献
git add .
git commit -m "feat: your improvement"
git push
```

---

## 📄 许可 | License

MIT License © 2024 pephupephu

## 🙏 致谢 | Acknowledgments

- [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills/) — 设计理念参考
- [edge-tts](https://github.com/rany2/edge-tts) — 免费中文TTS
- [Playwright](https://playwright.dev/) — 浏览器截图
- [FFmpeg](https://ffmpeg.org/) — 视频合成
