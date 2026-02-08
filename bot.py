import requests
import os

# --- CONFIGURATION ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

def test_connection():
    if not WEBHOOK_URL:
        print("❌ ERROR: DISCORD_WEBHOOK is not found in GitHub Secrets!")
        return

    print(f"📡 Attempting to send message to Discord...")
    payload = {"content": "Hello! This is a test from the Python script to see if the connection works."}
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("✅ SUCCESS: The message was sent to Discord!")
        else:
            print(f"❌ FAILED: Discord returned status code {response.status_code}")
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_connection()
