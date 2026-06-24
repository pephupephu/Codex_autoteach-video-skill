#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI教学PPT -> 专业讲解稿生成器 v2
为每页PPT生成更自然、更专业的教学口播文案。
"""
import json, sys, re

PROFESSIONAL_OPENINGS = {
    "cover": [
        "大家好，欢迎来到今天的课程。《{title}》是一套系统性的教学材料，我会带领大家从零开始，一步步掌握所有核心知识点。",
        "欢迎收看本次课程：{title}。这套内容涵盖了从基础到进阶的完整知识体系，建议大家跟随节奏循序渐进地学习。",
    ],
    "setup": [
        "在正式开始之前，我们首先来了解{title}。这部分是后续所有操作的基础，建议大家提前做好准备。",
        "工欲善其事，必先利其器。接下来我们看一看{title}，把基础打牢再往下走。",
    ],
    "code": [
        "现在我们来看一个具体的代码示例。这部分我会带着大家一步步拆解实现逻辑。",
        "光说不练假把式，接下来我们看一个实战示例。代码中包含了关键的技术要点。",
    ],
    "steps": [
        "接下来我们进入实操环节，{title}。这部分我会按步骤逐一演示，大家跟着操作就行。",
        "好的，现在来看具体的{title}。我把每一个步骤都拆解清楚了。",
    ],
    "summary": [
        "好了，我们来做个快速总结。{title}这部分我们涵盖了多个关键知识点，归纳如下。",
        "到这里，{title}这部分的内容就讲完了。我们来回顾一下重点。",
    ],
    "callout": [
        "这里有一个非常重要的提醒，大家一定要留意。{title}这个点如果处理不当，后续会遇到麻烦。",
        "注意了，这个地方是很多初学者容易踩坑的——{title}。",
    ],
    "objectives": [
        "在学习具体内容之前，我们先明确一下{title}。带着目标去学习，效率会更高。",
        "这一节我们要达成什么目标？来看一下{title}。",
    ],
    "architecture": [
        "现在我们从宏观角度来看一下整体的架构设计。{title}展示了各个模块之间的关系。",
        "理解了整体架构，再学具体内容就会豁然开朗。来看一下{title}。",
    ],
    "default": [
        "接下来我们进入一个新的部分：{title}。这部分内容我会详细展开讲解。",
        "好的，现在我们来看{title}。这里面包含了不少实用的知识点。",
    ],
}

TRANSITIONS = [
    "好，第一部分到这里就结束了。接下来我们进入下一个环节。",
    "说完了这些，我们继续往下走。",
    "掌握了前面的内容，现在来看下一个知识点。",
    "好的，接下来是更有意思的部分。",
    "继续深入，我们来看一看{title}。",
]

def generate_narration(title, stype, items, idx, total):
    """Generate professional narration for a slide."""
    stype = stype if stype in PROFESSIONAL_OPENINGS else "default"
    bullets = [it["text"] for it in items if it["type"]=="bullet"]
    texts = [it["text"] for it in items if it["type"]=="text"]
    
    parts = []
    
    # Opening
    if idx == 0:
        parts.append(f"大家好，欢迎来到今天的课程：{title}。今天这堂课，我会带大家系统地学习相关知识。在正式开始之前，先来看一下整体的课程安排。")
        return " ".join(parts)
    
    # Slide opening
    openings = PROFESSIONAL_OPENINGS[stype]
    opening = openings[idx % len(openings)]
    opening = opening.replace("{title}", title)
    parts.append(opening)
    
    # Content-specific narration
    if stype in ("setup", "steps"):
        if bullets:
            if len(bullets) <= 3:
                items_text = "；".join(bullets)
                parts.append(f"主要包括这几个方面：{items_text}。")
            else:
                items_text = "；".join(bullets[:3])
                parts.append(f"涉及的面比较多，包括{items_text}等{len(bullets)}个要点。")
        if texts:
            for t in texts[:2]:
                clean = t.replace("■ ", "")
                parts.append(clean + "。")
    
    elif stype == "summary":
        if bullets:
            parts.append(f"总结起来主要有{len(bullets)}个要点：{'；'.join(bullets[:4])}。")
        if texts:
            parts.append(texts[0] + "。")
        parts.append("这些都是关键知识点，希望大家能够熟练掌握。")
    
    elif stype == "callout":
        if texts:
            parts.append(texts[0] + "。")
        if bullets:
            for b in bullets[:3]:
                parts.append(b + "。")
    
    elif stype == "code":
        if texts:
            parts.append(texts[0] + "。")
        if bullets:
            main_bullets = "；".join(bullets[:3])
            parts.append(f"关键步骤包括：{main_bullets}。")
        parts.append("大家可以对照代码仔细理解其中的逻辑。")
    
    else:
        if bullets:
            if len(bullets) <= 4:
                parts.append(f"这里列出了{len(bullets)}个要点：{'；'.join(bullets)}。")
            else:
                parts.append(f"这里一共有{len(bullets)}个要点。主要包括：{'；'.join(bullets[:3])}等等。")
        if texts:
            for t in texts[:3]:
                clean = t.replace("■ ", "")
                if len(clean) > 5:
                    parts.append(clean + "。")
    
    # Ending
    if idx == total - 1:
        endings = [
            "以上就是今天课程的全部内容，感谢大家的观看，希望对你有所帮助！",
            "好的，本次课程到这里就圆满结束了。如果觉得有收获，欢迎点赞收藏！",
            "课程到此结束，祝你学习愉快，我们下次再见！",
        ]
        parts.append(endings[idx % len(endings)])
    elif stype == "summary":
        parts.append("这部分总结就到这里。")
    
    return " ".join(parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: text_extract.py <slides.json>")
        sys.exit(1)
    
    data = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    total = len(data["slides"])
    
    for i, s in enumerate(data["slides"]):
        narration = generate_narration(
            title=s["title"],
            stype=s.get("type", "content"),
            items=s.get("body", []),
            idx=i,
            total=total
        )
        print(narration)

if __name__ == "__main__":
    main()
