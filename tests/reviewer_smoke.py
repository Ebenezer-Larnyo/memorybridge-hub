"""Reviewer interface regression (not a human-accessibility or clinical audit)."""
import json
import os
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright,expect
base=os.environ.get("TEST_URL","http://127.0.0.1:8000/")
with sync_playwright() as p:
 browser=p.chromium.launch()
 page=browser.new_page(viewport={"width":390,"height":844})
 errors=[];page.on("pageerror",lambda e: errors.append(str(e)))
 page.add_init_script("window.open = (url) => { window.__reviewIssueTarget = url; };")
 page.goto(base+"review.html")
 expect(page).to_have_title("Reviewer workspace | Naviboa Hub")
 expect(page.locator("#stat-total")).not_to_have_text("—",timeout=15000)
 expect(page.locator("#resource-list .item")).not_to_have_count(0)
 assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"),"reviewer mobile overflow"
 page.locator(".item").first.click()
 expect(page.locator("#selected-title")).not_to_be_empty()
 expect(page.locator("#evidence")).to_have_value("https://"+page.locator("#evidence").input_value().split("https://",1)[1])
 page.locator("#decision").select_option("approved")
 page.locator("#notes").fill("I inspected the original page and verified the listed source against each criterion.")
 page.locator("#ack").check()
 page.locator("#submit-github").click()
 assert page.evaluate("window.__reviewIssueTarget === undefined"), "Invalid review must not open GitHub"
 for s in page.locator("[data-criterion]").all():s.select_option("pass")
 page.locator("[data-criterion=medical_safety_screen]").select_option("concern")
 page.locator("#submit-github").click()
 expect(page.locator("#form-status")).to_contain_text("Approval requires")
 page.locator("[data-criterion=medical_safety_screen]").select_option("pass")
 page.locator("#submit-github").click()
 expect(page.locator("#form-status")).to_contain_text("GitHub has been opened")
 target=page.evaluate("window.__reviewIssueTarget")
 parsed=urlparse(target)
 assert parsed.scheme=="https" and parsed.netloc=="github.com",target
 assert parsed.path.endswith("/issues/new"),target
 payload=parse_qs(parsed.query)["body"][0]
 assert payload.startswith("NAVIBOA_REVIEW_V1\n"),payload
 fence=chr(96)*3
 data=json.loads(payload.split(fence+"json\n",1)[1].rsplit("\n"+fence,1)[0])
 assert data["decision"]=="approved" and len(data["criteria"])==8 and data["replace_existing"] is False
 assert "reviewer_id" not in data and "token" not in data
 expect(page.locator("#scope")).to_have_value("queue")
 page.locator("#scope").select_option("all")
 page.locator("#search").fill("WHO")
 expect(page.locator("#resource-list .item")).not_to_have_count(0)
 page.set_viewport_size({"width":1280,"height":900})
 assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"),"reviewer desktop overflow"
 assert not errors,errors
 browser.close()
print("Reviewer dashboard browser checks passed")
