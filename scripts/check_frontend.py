#!/usr/bin/env python3
"""Check frontend for errors using Playwright."""

from playwright.sync_api import sync_playwright
import json

def check_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        # Capture page errors
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))

        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Take screenshot
        page.screenshot(path="/tmp/frontend_home.png", full_page=True)
        print("Screenshot saved to /tmp/frontend_home.png")

        # Check for errors
        errors = [msg for msg in console_messages if msg["type"] in ["error", "warning"]]
        if errors:
            print("\n=== Console Errors/Warnings ===")
            for err in errors:
                print(f"[{err['type'].upper()}] {err['text']}")

        if page_errors:
            print("\n=== Page Errors ===")
            for err in page_errors:
                print(f"ERROR: {err}")

        if not errors and not page_errors:
            print("\nNo errors found!")

        # Get page title and content
        print(f"\n=== Page Info ===")
        print(f"Title: {page.title()}")
        print(f"URL: {page.url}")

        # Check if main content is loaded
        content = page.content()
        if "DeepWiki" in content or "wiki" in content.lower():
            print("Main content loaded successfully")

        browser.close()

if __name__ == "__main__":
    check_frontend()