import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURATION ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "seen_events.txt"

# Keywords that indicate a hackathon
HACKATHON_KEYWORDS = ["hackathon", "hack", "challenge", "competition", "compétition", "ideathon"]

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
        "embeds": [{
            "title": f"🏆 New Hackathon Found: {event_name}",
            "description": f"📅 **Date:** {date}\n🔌 **Source:** {source}",
            "url": link,
            "color": 15418782  # Bright Orange/Gold
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)

def is_hackathon(title):
    """Checks if the event title contains hackathon-related words."""
    return any(keyword in title.lower() for keyword in HACKATHON_KEYWORDS)

def scrape_10times():
    print("Checking 10times.com...")
    url = "https://10times.com/tunisia/technology"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        seen = get_seen_events()

        for row in soup.select("tr.box"):
            name = row.select_one("h2").text.strip()
            link = row.select_one("a")['href']
            date = row.select_one("span.text-muted").text.strip()

            # FILTER: Only send if it matches our keywords
            if is_hackathon(name) and link not in seen:
                send_to_discord(name, date, link, "10times")
                save_event(link)
    except Exception as e:
        print(f"Error scraping 10times: {e}")

def scrape_eventbrite():
    print("Checking Eventbrite Tunisia...")
    # This URL searches specifically for 'hackathon' in Tunisia on Eventbrite
    url = "https://www.eventbrite.com/d/tunisia/hackathon/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        seen = get_seen_events()

        # Eventbrite structure changes often, this targets their common card title
        links = soup.find_all('a', href=True)
        for link in links:
            title = link.get_text().strip()
            href = link['href']
            
            if "eventbrite.com/e/" in href and is_hackathon(title):
                clean_url = href.split('?')[0] # Remove tracking parameters
                if clean_url not in seen:
                    send_to_discord(title, "Click link for date", clean_url, "Eventbrite")
                    save_event(clean_url)
    except Exception as e:
        print(f"Error scraping Eventbrite: {e}")

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK not set.")
        send_to_discord("Test Event", "Today", "https://google.com", "Test System did not work")
    else:
        send_to_discord("Test Event", "Today", "https://google.com", "Test System")
        scrape_10times()
        scrape_eventbrite()
