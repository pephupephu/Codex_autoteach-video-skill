#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshot HTML slides via Playwright - v2: uses go() function directly"""
import asyncio, pathlib, os, sys, json, re
from playwright.async_api import async_playwright

async def main():
    deck_dir = sys.argv[1]
    html_path = str(pathlib.Path(deck_dir) / "index.html")
    png_dir = str(pathlib.Path(deck_dir) / "png")
    os.makedirs(png_dir, exist_ok=True)
    
    html_content = open(html_path, "r", encoding="utf-8").read()
    slide_count = html_content.count('<section class="slide')
    print(f"[INFO] Total slides found: {slide_count}", flush=True)
    
    if slide_count == 0:
        print("[ERROR] No slides found in HTML!", flush=True)
        sys.exit(1)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge", headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-software-rasterizer"]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        url = "file:///" + html_path.replace("\\", "/")
        
        print("[INFO] Loading deck...", flush=True)
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        try:
            await page.wait_for_selector(".deck", timeout=5000)
            print("[INFO] Deck loaded", flush=True)
        except:
            print("[WARN] .deck selector not found", flush=True)
        
        await asyncio.sleep(1)
        
        for i in range(slide_count):
            # Navigate using the runtime's go() function
            nav_result = await page.evaluate(f"""() => {{
                if (typeof go === 'function') {{
                    go({i});
                    return 'go()';
                }}
                location.hash = '#/{i+1}';
                return 'hash';
            }}""")
            
            await asyncio.sleep(0.8)
            
            active_title = await page.evaluate(f"""() => {{
                const active = document.querySelector('.is-active');
                if (active) {{
                    const t = active.getAttribute('data-title') || '';
                    return t.substring(0, 40);
                }}
                return 'no active slide';
            }}""")
            
            # Force content visible
            await page.evaluate("""() => {
                document.querySelectorAll('.slide *').forEach(el => {
                    el.style.animation = 'none';
                    el.style.animationDelay = '0s';
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
            }""")
            await asyncio.sleep(0.2)
            
            png_path = os.path.join(png_dir, f"slide_{i+1:03d}.png")
            await page.screenshot(path=png_path, full_page=False)
            
            file_size = os.path.getsize(png_path)
            print(f"[{i+1}/{slide_count}] {nav_result} | {active_title} | {file_size} bytes", flush=True)
            
            if file_size < 5000:
                print(f"  ⚠️  WARNING: Very small screenshot!", flush=True)
        
        await browser.close()
    
    total = len([f for f in os.listdir(png_dir) if f.startswith("slide_")])
    print(f"\n[DONE] {total} slides captured to {png_dir}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
