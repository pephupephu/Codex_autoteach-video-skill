# Autoteach Video Skill

**AI教学文本 → 精美PPT → 教学视频 全自动流水线**

只需提供教学文本（Markdown或带`===`分隔线的纯文本），一键生成带语音旁白的精美教学视频。

## 功能特点

- 📊 **智能解析**：自动识别教学文档的章节结构，支持 `## Markdown` 和 `===` 分隔线两种格式
- 🎨 **36种主题风格**：Tokyo Night、Cyberpunk、学术论文、商务演示等，可在线切换
- 🎬 **PPT动效**：逐条淡入、缩放、滑入等入场动画
- 🗣️ **TTS语音旁白**：使用 edge-tts 生成中文女声旁白（离线、免费）
- 🎥 **1920×1080高清视频**：H.264编码，搭配AAC音频
- 🌐 **交互式HTML PPT**：附带可交互的HTML版本，支持键盘快捷键

## 前置依赖

| 工具 | 说明 | 安装 |
|------|------|------|
| **Python 3.8+** | 运行PPT生成和工具脚本 | [python.org](https://python.org) |
| **Microsoft Edge** | Headless网页截图 | 内置 |
| **FFmpeg** | 视频合成 | `winget install ffmpeg` |
| **edge-tts** | 文本转语音（免费） | `pip install edge-tts` |
| **Playwright** | 网页截图引擎 | `pip install playwright` |
| **html-ppt skill** | PPT视觉框架 | `npx skills add https://github.com/lewislulu/html-ppt-skill` |

## 快速使用

### 一键生成

```powershell
# 进入插件目录后
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.txt"
```

### 分步执行

```powershell
# 1. 生成HTML PPT
python scripts\generate_ppt.py "教学文本.txt" --theme tokyo-night -o D:\codex\teach-output

# 2. 渲染视频（含TTS）
.\scripts\render_video.ps1 -DeckDir "D:\codex\teach-output\<课程名>" -DurationPerSlide 15 -WithTTS
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-InputFile` | 输入教学文本路径 | 必填 |
| `-DurationPerSlide` | 每页展示秒数 | 12 |
| `-Theme` | PPT主题风格 | `tokyo-night` |
| `-OutputDir` | 输出目录 | `D:\codex\teach-output` |
| `-NoTTS` | 跳过语音生成 | 未设置 |
| `-Voice` | TTS语音角色 | `zh-CN-XiaoxiaoNeural` |

## 主题预览

| 风格 | 主题 |
|------|------|
| 🌙 暗色炫酷 | `tokyo-night`, `cyberpunk-neon`, `dracula`, `vaporwave` |
| 🎓 学术报告 | `academic-paper`, `editorial-serif`, `minimal-white` |
| 💼 商务投资 | `pitch-deck-vc`, `corporate-clean`, `swiss-grid` |
| 🔧 技术分享 | `blueprint`, `terminal-green`, `catppuccin-mocha` |
| 🏔 自然温暖 | `sunset-warm`, `arctic-cool`, `aurora` |
| 🎨 设计创意 | `bauhaus`, `glassmorphism`, `memphis-pop` |

## 输出产物

```
输出目录/
  └── <课程名>/
      ├── index.html          ← 可交互HTML PPT（按T切换主题）
      ├── style.css           ← PPT样式
      ├── slides.json         ← 幻灯片数据
      └── teaching-video.mp4  ← 成品教学视频（1920×1080）
```

## 支持的输入格式

### Markdown格式（用 ## 分页）

```markdown
# 课程标题

## 第一节标题
- 要点1
- 要点2

## 代码示例
\`\`\`python
print("Hello")
\`\`\`
```

### 文本格式（用 === 分隔章节）

```
============================================
课程标题
============================================

============================================
一、章节标题
============================================
内容...

============================================
二、下一个章节
============================================
```

## 开源协议

MIT
