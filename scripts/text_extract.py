#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI教学PPT -> 讲解稿生成器
为每页PPT生成自然、生动的口播讲解文案，而非直接念文本。
"""
import json, sys, re, math

def generate_narration(slide_title, slide_type, body_items, slide_index, total_slides):
    """为单页PPT生成自然口播讲解稿"""
    title = slide_title
    items = body_items
    
    # 提取关键内容和数量
    bullets = [it["text"] for it in items if it["type"]=="bullet"]
    texts = [it["text"] for it in items if it["type"]=="text"]
    codes = [it["content"] for it in items if it["type"]=="code"]
    
    has_bullets = len(bullets) > 0
    has_texts = len(texts) > 0
    has_codes = len(codes) > 0
    
    # 构建自然口播
    parts = []
    
    # 判断是否是第一节正文
    is_first_content = slide_index == 1
    
    # 过渡语
    if slide_index == 0:
        parts.append(f"大家好，欢迎来到今天的课程：{title}")
    elif is_first_content:
        parts.append(f"好，我们正式开始。首先来看第一个部分：{title}")
    else:
        transitions = [
            f"接下来，我们来看下一个部分：{title}",
            f"说完了这些，我们进入：{title}",
            f"好了，接下来是：{title}",
            f"继续往下看，{title}",
            f"下面我们来了解一下{title}",
        ]
        parts.append(transitions[slide_index % len(transitions)])
    
    # 根据幻灯片类型生成讲解
    if slide_type in ("cover",):
        if has_texts:
            parts.append("今天这堂课，我们会系统地学习相关内容。")
            parts.append("在正式开始之前，先给大家介绍一下整体的课程安排。")
    
    elif slide_type in ("setup", "requirements"):
        parts.append(f"在开始之前，我们需要先了解一下{title}方面的要求。")
        if has_bullets:
            main_pts = []
            for b in bullets[:3]:
                # Remove leading numbers like "CPU:"
                clean = re.sub(r'^[^:：]*[:：]\s*', '', b)
                if not clean: clean = b
                main_pts.append(clean)
            
            if len(bullets) > 3:
                parts.append(f"主要包括这几个方面：{'、'.join(main_pts[:2])}等等，一共{len(bullets)}个要点。")
            else:
                parts.append(f"主要包括：{'；'.join(main_pts)}。")
            
            parts.append("大家可以根据自己的情况提前准备好相应的条件。")
    
    elif slide_type in ("steps", "content"):
        parts.append(f"这里面有{len(bullets) + len(texts)}个关键信息需要我们了解。")
        
        if has_bullets:
            # Group into meaningful chunks for narration
            if len(bullets) <= 3:
                parts.append(f"首先是：{'；'.join(bullets)}。")
            elif len(bullets) <= 6:
                mid = (len(bullets)+1)//2
                parts.append(f"前几个要点包括：{'；'.join(bullets[:mid])}。")
                parts.append(f"此外还有：{'；'.join(bullets[mid:])}。")
            else:
                parts.append(f"这里一共有{len(bullets)}个要点，内容比较多，我们逐一来看。")
                parts.append(f"主要包括：{'；'.join(bullets[:3])}等等。")
        
        if has_texts:
            for t in texts[:2]:
                clean = re.sub(r'^■\s*', '', t)
                parts.append(f"这里需要说明的是：{clean}。")
    
    elif slide_type == "code":
        parts.append(f"现在我们来看一个{'代码示例' if has_codes else '具体的实现步骤'}。")
        if has_texts:
            parts.append(f"{texts[0]}。")
        if has_bullets:
            parts.append(f"这里的关键步骤包括：{'；'.join(bullets[:3])}。")
        if has_codes:
            parts.append("注意代码中的关键逻辑，我们会在后面详细解释。")
    
    elif slide_type == "summary":
        parts.append(f"好了，我们来快速总结一下刚才讲到的{title}。")
        if has_bullets:
            parts.append(f"归纳起来主要有{len(bullets)}个要点：{'；'.join(bullets[:5])}。")
        if has_texts:
            parts.append(f"{texts[0] if texts else '这些内容希望大家都能掌握。'}")
    
    elif slide_type == "callout":
        parts.append(f"这里有一个非常重要的提醒：")
        if has_texts:
            parts.append(f"{texts[0]}")
        if has_bullets:
            for b in bullets:
                parts.append(f"{b}。")
    
    elif slide_type == "objectives":
        parts.append(f"在学习这节内容之前，我们先明确一下学习目标。")
        if has_bullets:
            parts.append(f"通过本节学习，你将掌握：{'；'.join(bullets[:4])}。")
    
    elif slide_type == "architecture":
        parts.append(f"现在我们来看一下整体的{title}。")
        if has_bullets:
            parts.append(f"整个架构包含{len(bullets)}个核心模块：{'；'.join(bullets[:4])}。")
    
    else:
        parts.append(f"在{title}这部分内容中，")
        if has_bullets:
            parts.append(f"主要涉及{len(bullets)}个方面：{'；'.join(bullets[:3])}。")
        if has_texts:
            parts.append(texts[0] if texts else "")
    
    # 结束语
    if slide_index == total_slides - 1:
        endings = [
            "以上就是今天课程的全部内容，感谢大家的观看！",
            "好了，本次课程到这里就结束了，希望对你有帮助！",
            "以上就是本课的完整内容，如果觉得有用，别忘了收藏分享哦！",
            "课程到此结束，祝你学习愉快，我们下次再见！",
        ]
        parts.append(endings[slide_index % len(endings)])
    elif slide_type == "summary":
        parts.append("好的，这部分总结就到这里。")
    
    return " ".join(p for p in parts if p)


def main():
    if len(sys.argv) < 2:
        print("Usage: text_extract.py <slides.json>")
        sys.exit(1)
    
    data = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    total = len(data["slides"])
    
    for i, s in enumerate(data["slides"]):
        narration = generate_narration(
            slide_title=s["title"],
            slide_type=s.get("type", "content"),
            body_items=s.get("body", []),
            slide_index=i,
            total_slides=total
        )
        print(narration)
    
    # Also print slide titles for reference (pipe-separated, for debugging)
    if len(sys.argv) > 2 and sys.argv[2] == "--titles":
        print("---SLIDE_TITLES---", file=sys.stderr)
        for s in data["slides"]:
            print(s["title"], file=sys.stderr)

if __name__ == "__main__":
    main()
