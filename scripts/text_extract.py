#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract slide text for TTS from slides.json"""
import json, sys

def main():
    data = json.load(open(sys.argv[1], "r", encoding="utf-8"))
    for i, s in enumerate(data["slides"]):
        parts = ["page " + str(i + 1) + ": ", s["title"]]
        for x in s.get("body", []):
            t = x.get("text", "")
            if t and x.get("type") in ("text", "bullet"):
                parts.append(t)
        print(" - ".join(parts))

if __name__ == "__main__":
    main()
