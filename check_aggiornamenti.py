import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://www.liceoariostospallanzani-re.edu.it/index.php/notizie/la-vita-della-scuola/circolari-e-comunicazioni"
BASE_DOMAIN = "https://www.liceoariostospallanzani-re.edu.it"
CACHE_FILE = "last_circolare.txt"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Token o Chat ID mancanti.")
        return
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Errore nell'invio a Telegram: {e}")

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Cerca il link della circolare più recente
    link_elem = soup.find("a", href=lambda h: h and "circolari-e-comunicazioni" in h and "id=" in h.lower())
    
    if not link_elem:
        table = soup.find("table")
        if table:
            link_elem = table.find("a")

    if not link_elem:
        print("Nessuna circolare individuata.")
        return

    title = link_elem.get_text(strip=True)
    full_url = urljoin(BASE_DOMAIN, link_elem["href"])

    last_title = ""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title and title != last_title:
        msg = f"🔔 <b>Nuova Circolare Pubblicata!</b>\n\n📄 {title}\n\n🔗 <a href='{full_url}'>Apri la pagina</a>"
        send_telegram(msg)
        
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print(f"Nuova circolare notificata: {title}")
    else:
        print("Nessun aggiornamento rispetto all'ultimo controllo.")

if __name__ == "__main__":
    main()
