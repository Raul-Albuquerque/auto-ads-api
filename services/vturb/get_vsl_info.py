from playwright.sync_api import sync_playwright
import requests

def login_and_get_token(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        token = None

        def handle_response(response):
            nonlocal token
            if "auth/login.json" in response.url and response.status == 200:
                try:
                    data = response.json()
                    token = data.get("token") or data.get("access_token")
                except:
                    pass

        page.on("response", handle_response)

        page.goto("https://app.vturb.com")
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_timeout(5000)

        browser.close()
        return token

def call_vturb_stats():
    email = "thaleslopesmkt@gmail.com"
    password = "k@7B7ayPkPHbBi6"
    token = login_and_get_token(email=email, password=password)
    url = "https://api.vturb.com.br/vturb/v2/players/67f07dac5f4ceec86cc3fe04/analytics_stream/player_stats"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://app.vturb.com",
        "Referer": "https://app.vturb.com/",
    }

    payload = {
    "player_stats": {
        "player_id": "67f07dac5f4ceec86cc3fe04",
        "start_date": "2025-04-11 00:00:00",
        "end_date": "2025-04-11 23:59:59",
        "timezone": "America/Sao_Paulo"
    }
  }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
