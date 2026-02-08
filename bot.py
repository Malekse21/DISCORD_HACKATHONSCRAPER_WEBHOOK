import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURATION ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "seen_events.txt"

# Broadened keywords for Tunisian events
KEYWORDS = [
    "hackathon", "hack", "challenge", "competition", 
    "compétition", "ideathon", "codeweek", "startup", 
    "innovation", "bootcamp", "data"
]

def get_seen_events():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_event(event_id):
    with open(DB_FILE, "a") as f:
        f.write(event_id + "\n")

def send_to_discord(event_name, date, link, source):
    payload = {
        "content": "🚀 **New Event Found in Tunisia!**",
        "embeds": [{
            "title": event_name,
            "description": f"📅 **Date:** {date}\n🔌 **Source:** {source}",
            "url": link,
            "color": 3447003 
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)

def is_match(title):
    return any(k in title.lower() for k in KEYWORDS)

def scrape_10times():
    print("Checking 10times...")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get("https://10times.com/tunisia/technology", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        seen = get_seen_events()
        for row in soup.select("tr.box"):
            name = row.select_one("h2").text.strip()
            link = row.select_one("a")['href']
            date = row.select_one("span.text-muted").text.strip()
            if is_match(name) and link not in seen:
                send_to_discord(name, date, link, "10times")
                save_event(link)
    except Exception as e: print(f"10times error: {e}")

def scrape_eventbrite():
    print("Checking Eventbrite...")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get("https://www.eventbrite.com/d/tunisia/events/", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        seen = get_seen_events()
        for link_tag in soup.find_all('a', href=True):
            title = link_tag.get_text().strip()
            href = link_tag['href']
            if "eventbrite.com/e/" in href and is_match(title):
                clean_url = href.split('?')[0]
                if clean_url not in seen:
                    send_to_discord(title, "Click link for info", clean_url, "Eventbrite")
                    save_event(clean_url)
    except Exception as e: print(f"Eventbrite error: {e}")

if __name__ == "__main__":
    if WEBHOOK_URL:
        # Check all sources
        scrape_10times()
        scrape_eventbrite()
        print("Scrape complete.")
    else:
        print("Missing Webhook URL.")
