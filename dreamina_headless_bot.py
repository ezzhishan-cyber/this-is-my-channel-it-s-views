#!/usr/bin/env python3
"""
DREAMINA HEADLESS PLAYWRIGHT BOT (ZERO HUMAN PRESENCE)
Automates Dreamina Canvas / Nodes in a headless Chromium browser.
Supports direct session cookie injection (sessionid) to bypass Cloudflare and cloud IP login blocks.
"""

import os
import sys
import time
import json
import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright

DREAMINA_URL = "https://dreamina.capcut.com"
CANVAS_URL = "https://dreamina.capcut.com/ai-tool/canvas"
SESSION_DIR = Path("./dreamina_session_profile")
OUTPUT_DIR = Path("./generated_reels")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Credentials
DREAMINA_EMAIL = os.getenv("DREAMINA_EMAIL", "ezzhisham585@gmail.com")
DREAMINA_PASSWORD = os.getenv("DREAMINA_PASSWORD", "lolmanjoker556")
DREAMINA_SESSION_ID = os.getenv("DREAMINA_SESSION_ID", "")


async def setup_authenticated_context(p, session_id: str = None):
    """Creates a browser context with persistent storage or injected session cookies."""
    context = await p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ]
    )

    if session_id:
        print(f"[BOT] Injecting sessionid cookie into browser context...")
        cookies = [
            {
                "name": "sessionid",
                "value": session_id,
                "domain": ".capcut.com",
                "path": "/"
            },
            {
                "name": "sessionid",
                "value": session_id,
                "domain": "dreamina.capcut.com",
                "path": "/"
            }
        ]
        await context.add_cookies(cookies)

    return context


async def attempt_direct_login(page):
    """Attempts direct email/password login on Dreamina embed page."""
    print("[BOT] Attempting direct login with provided credentials...")
    embed_url = "https://dreamina.capcut.com/ai-tool/login-embed?aid=513641&current_page=dreamina_landing_page_pc&lang=en&title_key=DrmnUG_web_welcome_login&source=dreamina_landing_page&page=dreamina_landing_page_pc&col=1"
    await page.goto(embed_url, wait_until="domcontentloaded")
    await asyncio.sleep(2)

    # Click continue with email
    email_btn = page.locator("text=/continue with email/i").first
    if await email_btn.is_visible():
        await email_btn.click()
        await asyncio.sleep(1)

    email_inp = page.locator('input[type="email"], input[placeholder*="email"]').first
    pass_inp = page.locator('input[type="password"]').first

    if await email_inp.is_visible() and await pass_inp.is_visible():
        print(f"[BOT] Filling email: {DREAMINA_EMAIL}")
        await email_inp.click()
        await email_inp.press_sequentially(DREAMINA_EMAIL, delay=40)
        await pass_inp.click()
        await pass_inp.press_sequentially(DREAMINA_PASSWORD, delay=40)

        continue_btn = page.locator('button:has-text("Continue"), div[role="button"]:has-text("Continue")').first
        await continue_btn.click()
        await asyncio.sleep(4)

        # Inspect if error occurred
        errors = await page.locator('.error, [role="alert"], span:has-text("Couldn’t sign in"), div:has-text("Couldn’t sign in")').all_text_contents()
        if any("Couldn’t sign in" in e for e in errors):
            print("\n[SECURITY BLOCK DETECTED]")
            print("ByteDance risk control blocked direct password submission from datacenter IP:")
            print("  -> 'Couldn’t sign in. Try again later.'")
            print("Solution: Provide your active browser 'sessionid' cookie or run locally.\n")
            return False

        return True

    return False


async def dismiss_modals(page):
    """Dismisses welcome modals, tutorial overlays, and announcement dialogs."""
    print("[BOT] Checking for modal overlays or announcements...")
    await page.keyboard.press("Escape")
    await asyncio.sleep(0.5)

    selectors = [
        ".lv-modal-close",
        "[aria-label='Close']",
        "button:has-text('Got it')",
        "button:has-text('OK')",
        "button:has-text('I know')",
        "button:has-text('Dismiss')",
        "button:has-text('Close')",
        "button:has-text('Skip')",
        "button:has-text('Next')",
        ".arco-modal-close-icon",
        "[class*='close-icon']",
        "[class*='closeBtn']",
        "[class*='modal-close']"
    ]

    for sel in selectors:
        try:
            elements = await page.locator(sel).all()
            for el in elements:
                if await el.is_visible():
                    print(f"[BOT] Closing modal overlay via '{sel}'...")
                    await el.click(force=True)
                    await asyncio.sleep(0.5)
        except Exception:
            pass


async def execute_canvas_generation(page, prompt_img: str, prompt_video: str):
    """Automates the Dreamina Canvas interface with zero-credit settings."""
    print(f"[BOT] Navigating to Canvas: {CANVAS_URL}...")
    await page.goto(CANVAS_URL, wait_until="domcontentloaded")
    await asyncio.sleep(5)

    # 1. Verify Authentication
    if "login" in page.url:
        print("[BOT ERROR] Redirected to login. Session is unauthenticated.")
        return False

    print("[BOT SUCCESS] Authenticated Canvas access verified!")

    # Dismiss any welcome / update modals
    await dismiss_modals(page)
    await page.screenshot(path="canvas_loaded.png")

    # 2. Toggle Standard / Unlimited Mode (Zero Credits)
    try:
        std_btn = page.locator("button:has-text('Standard'), span:has-text('Unlimited')").first
        if await std_btn.is_visible():
            await std_btn.click(force=True)
            print("[BOT] Zero-credit Unlimited Mode engaged.")
    except Exception as e:
        print(f"[BOT NOTICE] Standard mode toggle: {e}")

    # 3. Ratio 9:16
    try:
        ratio_btn = page.locator("button:has-text('9:16')").first
        if await ratio_btn.is_visible():
            await ratio_btn.click(force=True)
            print("[BOT] Ratio 9:16 selected.")
    except Exception as e:
        print(f"[BOT NOTICE] Ratio 9:16 select: {e}")

    # 4. Inject prompt
    prompt_area = page.locator("textarea, [contenteditable='true']").first
    if await prompt_area.is_visible():
        await prompt_area.fill(prompt_img)
        print("[BOT] Injected Seedream prompt.")
    else:
        print("[BOT NOTICE] Searching for alternative prompt input fields...")
        prompt_fallback = page.locator("input[placeholder*='prompt' i], [placeholder*='describe' i]").first
        if await prompt_fallback.is_visible():
            await prompt_fallback.fill(prompt_img)
            print("[BOT] Injected Seedream prompt via fallback input.")

    # 5. Generate
    gen_btn = page.locator("button:has-text('Generate')").first
    if await gen_btn.is_visible():
        await gen_btn.click(force=True)
        print("[BOT] Generation command sent to Seedream!")
        await asyncio.sleep(15)
        await page.screenshot(path="canvas_generating.png")

    return True


async def main():
    parser = argparse.ArgumentParser(description="Dreamina Headless Bot")
    parser.add_argument("--sessionid", type=str, default=DREAMINA_SESSION_ID, help="Active Dreamina sessionid cookie")
    parser.add_argument("--test-login", action="store_true", help="Test login and report exact state")
    args = parser.parse_args()

    session_id = args.sessionid or os.getenv("DREAMINA_SESSION_ID")

    async with async_playwright() as p:
        context = await setup_authenticated_context(p, session_id=session_id)
        page = await context.new_page()

        # Check if already authenticated via persistent context
        print("[BOT] Checking session status on Canvas...")
        await page.goto(CANVAS_URL, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        if "login" in page.url or await page.locator("text=/sign in/i").first.is_visible():
            print("[BOT] Session not logged in. Attempting login...")
            if not session_id:
                success = await attempt_direct_login(page)
                if not success:
                    await context.close()
                    return
        else:
            print("[BOT SUCCESS] Session is already authenticated from persistent profile!")

        # Execute Canvas automation
        prompt_image = (
            "Cinematic extreme macro eye close-up of James Mercer (#MERCER_CORE_V1), "
            "hyper-detailed dilated hazel iris reflecting a flickering cyan neon sign reading 'VAULT 73'. "
            "Half of face illuminated by high-contrast volumetric frost vapor and radioactive amber emergency strobe, "
            "ultra-realistic 8k, sub-surface skin scattering, Arri Alexa 65 anamorphic."
        )
        prompt_video = (
            "[Camera: Dynamic high-speed backward pull out from extreme close-up of hazel eye pupil, "
            "pulling back into medium over-the-shoulder tracking shot] James Mercer steps forward into "
            "abandoned cryogenic bunker chamber Vault 73."
        )

        await execute_canvas_generation(page, prompt_image, prompt_video)
        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
