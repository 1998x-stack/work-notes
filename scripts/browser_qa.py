"""Real Chromium checks for the homepage, demo and approved visual articles."""
from __future__ import annotations

from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

from build_site import OUT


def run() -> int:
    if not (OUT / "index.html").is_file():
        print("Build _site first.", file=sys.stderr)
        return 1
    report = []
    captures = OUT.parent / "_qa"
    captures.mkdir(exist_ok=True)
    urls = [OUT / "index.html", OUT / "demo.html", *sorted((OUT / "posts").glob("**/index.html"))]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for width, height, device in ((1440, 900, "desktop"), (390, 844, "mobile")):
                page = browser.new_page(viewport={"width": width, "height": height},
                                        device_scale_factor=1)
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                for path in urls:
                    page.goto(path.resolve().as_uri(), wait_until="load")
                    if page.locator("h1").count() != 1:
                        report.append(f"{device} {path.name}: one h1 required")
                    x_overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > window.innerWidth + 2"
                    )
                    if x_overflow:
                        report.append(f"{device} {path.name}: horizontal overflow")
                    if path.name == "index.html" and path.parent == OUT:
                        if page.locator("#topic-grid button").count() < 6:
                            report.append(f"{device}: topic selection missing")
                        page.locator("#search").fill("no-such-public-note-zz")
                        page.locator("#month").select_option("")
                        if page.locator("#visible-count").inner_text() != "0":
                            report.append(f"{device}: search filter failed")
                        page.locator("#reset-filters").click()
                    if path.name == "demo.html":
                        if page.get_by_text("合成演示 · 非真实工作记录").count() != 1:
                            report.append(f"{device}: demo disclosure missing")
                        page.locator("details").last.locator("summary").click()
                        if not page.locator("details").last.get_attribute("open") == "":
                            report.append(f"{device}: accessible details interaction failed")
                    if errors:
                        report.extend(f"{device} {path.name}: JS error {err}" for err in errors)
                        errors.clear()
                page.goto((OUT / "index.html").resolve().as_uri())
                page.screenshot(path=str(captures / ("home-" + device + ".png")), full_page=True)
                page.close()
        finally:
            browser.close()
    if report:
        print("\n".join(report), file=sys.stderr)
        return 1
    print(f"Browser QA passed: {len(urls)} page(s), desktop/mobile, filters, demo, overflow.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
