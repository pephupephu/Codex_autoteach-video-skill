---
name: autoteach-video
description: "AI教学文本 → 精美PPT → 教学视频 全自动生成流水线。只需提供Markdown教学文本，一键生成带语音旁白的教学视频。"
---

# Autoteach Video Skill

将AI教学Markdown文本，一键自动生成为**精美HTML教学PPT**，并录制为**带语音旁白的MP4教学视频**。

## 工作流程

```
用户提供Markdown教学文本
       ↓
Step 1: 解析文本 → 生成HTML精美PPT（36种主题 + CSS动效 + Canvas粒子特效）
       ↓
Step 2: Headless Edge截图每页幻灯片 (1920×1080)
       ↓
Step 3: edge-tts 生成每页语音旁白（中文女声）
       ↓
Step 4: FFmpeg 合成 PNG + 音频 → MP4教学视频
       ↓
输出：成品MP4视频 + 可交互HTML PPT
```

## 前置依赖

该插件依赖以下工具，需要先在系统中安装：

1. **Python 3.8+** — 用于PPT生成和TTS
2. **Microsoft Edge** — 用于Headless截图
3. **FFmpeg** — 用于视频合成
4. **edge-tts** — 文本转语音 (`pip install edge-tts`)
5. **html-ppt skill** — 提供36个主题和动效框架 (`npx skills add https://github.com/lewislulu/html-ppt-skill`)

## 使用方法

### 方式一：一键式完整流水线

```powershell
# 进入插件目录
cd path\to\autoteach-video-skill

# 一键生成教学视频（带TTS语音）
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.md" -DurationPerSlide 12

# 不带语音（快速生成）
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.md" -DurationPerSlide 10 -NoTTS
```

### 方式二：分步执行

```powershell
# Step 1: 生成HTML PPT
python scripts/generate_ppt.py "你的教学文本.md" --theme academic-paper -o ./output

# Step 2: 渲染视频
.\scripts\render_video.ps1 -DeckDir "./output/AI教学课程" -DurationPerSlide 12 -WithTTS
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-InputFile` | 输入Markdown教学文本路径 | 必填 |
| `-DurationPerSlide` | 每页幻灯片展示秒数 | 12 |
| `-Theme` | PPT主题风格 | `academic-paper` |
| `-OutputDir` | 输出目录 | `D:\codex\teach-output` |
| `-NoTTS` | 跳过语音旁白生成 | 未设置（默认生成语音） |
| `-Voice` | TTS语音角色 | `zh-CN-XiaoxiaoNeural` |

## 36种主题风格

| 风格类型 | 主题名 |
|---------|--------|
| 🎓 学术/报告 | `academic-paper` `editorial-serif` `minimal-white` |
| 💼 商务/投资 | `pitch-deck-vc` `corporate-clean` `swiss-grid` |
| 🔧 技术分享 | `tokyo-night` `dracula` `catppuccin-mocha` `terminal-green` `blueprint` |
| 🌸 小红书/社交 | `xiaohongshu-white` `soft-pastel` `rainbow-gradient` `magazine-bold` |
| 🌙 暗色/炫酷 | `cyberpunk-neon` `vaporwave` `y2k-chrome` `neo-brutalism` `retro-tv` |
| 🏔 自然/温暖 | `sunset-warm` `arctic-cool` `aurora` `midcentury` |
| 🎨 设计/创意 | `bauhaus` `glassmorphism` `memphis-pop` `japanese-minimal` |
| 📊 数据/工程 | `engineering-whiteprint` `news-broadcast` `sharp-mono` |
| 🌈 多彩/渐变 | `catppuccin-latte` `nord` `rose-pine` `gruvbox-dark` `solarized-light` `corporate-clean` |

## 输入文本格式

支持标准Markdown，以 `##` 分页：

```markdown
# 课程标题（可选）

## 封面标题
课程副标题或简介文字

## 第一节标题
- 要点1
- 要点2
- 要点3

## 代码示例：函数实现
\`\`\`python
def hello():
    print("Hello World")
\`\`\`

## 总结
恭喜你完成了本课程的学习！
```

**幻灯片类型自动识别：**
- `## 封面 / 标题` → 封面页（带 Canvas 粒子特效）
- `## 目标 / 大纲 / 学习目标` → 目标页
- `## 代码 / 示例 / 实现` → 代码页
- `## 练习 / 习题 / 思考` → 练习页
- `## 总结 / 小结 / 回顾` → 总结页（带 Canvas 星空特效）
- 其他 `## 标题` → 内容页

## 输出产物

```
D:\codex\teach-output\
  └── <课程名>\
      ├── index.html          ← 可交互HTML PPT（在浏览器打开，按 T 切换主题，S 演讲者模式）
      ├── style.css           ← PPT样式
      ├── slides.json         ← 幻灯片数据结构
      └── teaching-video.mp4  ← 成品教学视频（1920×1080, MP4 H.264）
```

## 键盘快捷键（在浏览器中打开HTML后）

| 按键 | 功能 |
|------|------|
| `←` `→` | 上一页 / 下一页 |
| `T` | 循环切换主题风格 |
| `A` | 循环切换动画效果 |
| `S` | 打开演讲者模式（单独窗口，显示当前页/下一页/逐字稿/计时器） |
| `F` | 全屏 |
| `O` | 缩略图总览 |
| `N` | 笔记抽屉 |

## 许可

MIT License
