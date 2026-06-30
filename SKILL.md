---
name: autoteach-video
description: "AI教学文本 → 视频原生精美PPT → 教学视频 全自动生成。只需提供教学文本，即可生成带语音旁白的教学视频。"
---

# Autoteach Video Skill 🎬

将AI教学Markdown文本**一键自动生成**为**精美视频原生HTML教学PPT**，并录制为**带AI语音旁白的MP4教学视频**。

## 工作流程

```
用户提供Markdown教学文本
       ↓
Step 1: 解析文本 → 生成视频原生HTML PPT（4种主题 + SVG图标 + Canvas粒子）
       ↓
Step 2: 截图每页幻灯片 (1920×1080)
       ↓
Step 3: edge-tts 生成每页语音旁白
       ↓
Step 4: FFmpeg 合成 PNG + 音频 → MP4教学视频
       ↓
输出：成品MP4视频 + 可交互HTML PPT
```

## 设计理念

- **视频原生设计**：无PPT痕迹（无页码、无页眉、无进度点）
- **内容驱动布局**：代码、步骤、架构、总结各有专属视觉方案
- **无AI痕迹**：不使用emoji图标、有色左边框卡片、紫蓝渐变
- **步进式揭示**：内容逐步呈现，聚焦当前讲解点

## 前置依赖

1. **Python 3.8+**
2. **Microsoft Edge**
3. **FFmpeg**
4. **Python包**：`pip install edge-tts playwright`

## 使用方法

```powershell
# 一键生成
.\scripts\teach-pipeline.ps1 -InputFile "你的教学文本.md"

# 分步执行
python scripts/generate_ppt.py "输入.md" --theme slate -o ./output
python scripts/screenshot_slides.py ./output/课程名
.\scripts\render_video.ps1 -DeckDir ./output/课程名 -WithTTS
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--theme` | `slate` | 主题：slate, ocean, warm, forest |
| `DurationPerSlide` | 12 | 每页秒数 |
| `-Voice` | zh-CN-XiaoxiaoNeural | TTS语音 |

## 输出

```
D:\codex\teach-output\<课程名>\
  ├── index.html          ← 可交互HTML PPT
  ├── slides.json         ← 幻灯片数据
  └── teaching-video.mp4  ← 成品教学视频
```
