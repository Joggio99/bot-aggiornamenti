import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Token o Chat ID mancanti.")
        return
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Errore nell'invio a Telegram: {e}")

def check_spallanzani():
    url = "https://www.liceoariostospallanzani-re.edu.it/index.php/notizie/la-vita-della-scuola/circolari-e-comunicazioni"
    base_domain = "https://www.liceoariostospallanzani-re.edu.it"
    cache_file = "last_spallanzani.txt"

    print("Controllo Liceo Spallanzani...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        link_elem = soup.find("a", href=lambda h: h and "circolari-e-comunicazioni" in h and "id=" in h.lower())
        if not link_elem:
            table = soup.find("table")
            if table:
                link_elem = table.find("a")

        if not link_elem:
            print("Spallanzani: nessun elemento trovato.")
            return

        title = link_elem.get_text(strip=True)
        full_url = urljoin(base_domain, link_elem["href"])

        last_title = ""
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                last_title = f.read().strip()
        elif os.path.exists("last_circolare.txt"):
            # Migrazione automatica dalla vecchia versione
            with open("last_circolare.txt", "r", encoding="utf-8") as f:
                last_title = f.read().strip()

        if title and title != last_title:
            msg = (
                f"🏫 <b>Liceo Spallanzani - Nuova Circolare</b>\n\n"
                f"📄 {title}\n\n"
                f"🔗 <a href='{full_url}'>Leggi la circolare</a>"
            )
            send_telegram(msg)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(title)
            print(f"Spallanzani: inviata notifica per '{title}'")
        else:
            print("Spallanzani: nessun aggiornamento.")
    except Exception as e:
        print(f"Errore durante il controllo Spallanzani: {e}")

def check_usp_reggio():
    url = "https://re.istruzioneer.gov.it/tutte-le-notizie/"
    base_domain = "https://re.istruzioneer.gov.it"
    cache_file = "last_usp_re.txt"

    print("Controllo USP Reggio Emilia...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Cerca il titolo del primo articolo nella lista notizie
        article = soup.find("article")
        link_elem = None
        if article:
            link_elem = article.find(["h2", "h3", "h1"]).find("a") if article.find(["h2", "h3", "h1"]) else article.find("a")

        if not link_elem:
            # Fallback generico per la prima intestazione contenente un link
            for h in soup.find_all(["h2", "h3"]):
                a = h.find("a")
                if a and a.get("href"):
                    link_elem = a
                    break

        if not link_elem:
            print("USP Reggio Emilia: nessun elemento trovato.")
            return

        title = link_elem.get_text(strip=True)
        full_url = urljoin(base_domain, link_elem["href"])

        last_title = ""
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                last_title = f.read().strip()

        if title and title != last_title:
            msg = (
                f"🏛️ <b>USP Reggio Emilia - Nuova Notizia</b>\n\n"
                f"📄 {title}\n\n"
                f"🔗 <a href='{full_url}'>Leggi l'avviso</a>"
            )
            send_telegram(msg)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(title)
            print(f"USP Reggio Emilia: inviata notifica per '{title}'")
        else:
            print("USP Reggio Emilia: nessun aggiornamento.")
    except Exception as e:
        print(f"Errore durante il controllo USP Reggio Emilia: {e}")

def main():
    check_spallanzani()
    check_usp_reggio()

if __name__ == "__main__":
    main()
