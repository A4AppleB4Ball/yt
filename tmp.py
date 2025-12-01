import jinja2
from playwright.sync_api import sync_playwright
import os

def generate_fake_tweet(username, handle, text, filename="tweet.png"):
    # 1. HTML Template (Simplified Twitter UI)
    html_template = """
    <html>
    <style>
        body { background-color: black; font-family: sans-serif; color: white; width: 500px; padding: 20px;}
        .handle { color: gray; }
        .text { font-size: 24px; margin-top: 10px;}
    </style>
    <body>
        <b>{{ username }}</b> <span class="handle">@{{ handle }}</span>
        <div class="text">{{ text }}</div>
    </body>
    </html>
    """
    
    # 2. Render HTML
    template = jinja2.Template(html_template)
    rendered_html = template.render(username=username, handle=handle, text=text)
    
    with open("temp_tweet.html", "w") as f:
        f.write(rendered_html)
        
    # 3. Screenshot the HTML
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{os.getcwd()}/temp_tweet.html")
        
        # Take element screenshot only
        element = page.locator("body")
        element.screenshot(path=filename)
        browser.close()

# Usage
generate_fake_tweet("Elon Musk", "elonmusk", "I am buying the stickman video generator.")