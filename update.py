import cloudscraper
import requests
from bs4 import BeautifulSoup
import re
import json
import time

BASE = "https://telegratuita.net"

channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 GEN": BASE + "/en-vivo/gentv.php",
    "📺 SNT (TVLIBRE)": "https://tvlibr3.com/en-vivo/snt/",
}

result = {"channels": []}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE
}

session = cloudscraper.create_scraper()
session.headers.update(headers)

# =========================
# 🔹 UTILIDADES GENERALES
# =========================

def extract_iframe(html):
    matches = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)
    return matches[0] if matches else None


def extract_m3u8(html):
    matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
    return matches[0] if matches else None


# =========================
# 🔹 TELEGRATUITA SCRAPER
# =========================

def extract_telegratuita(url):
    try:
        res = session.get(url, timeout=15)
        html = res.text

        iframe = extract_iframe(html)
        if not iframe:
            print("❌ No iframe")
            return extract_m3u8(html)

        full_iframe = iframe if iframe.startswith("http") else BASE + iframe

        res2 = session.get(full_iframe, timeout=15)
        html2 = res2.text

        return extract_m3u8(html2) or full_iframe

    except Exception as e:
        print("❌ TELEGRATUITA ERROR:", e)
        return None


# =========================
# 🔹 TVLIBR3 SCRAPER
# =========================

def extract_tvlibr3(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        iframe = soup.find('iframe', {'id': 'iframe'})
        if not iframe:
            return None

        src = iframe.get('src')

        if '?get=' in src:
            encoded = src.split('?get=')[1]
            return f"https://tvlibr3.com/html/fl/?get={encoded}"

        return src

    except Exception as e:
        print("❌ TVLIBR3 ERROR:", e)
        return None


# =========================
# 🔹 ROUTER PRINCIPAL
# =========================

for name, url in channels.items():
    try:
        print("\n" + "=" * 50)
        print(f"📺 Canal: {name}")

        # 🔥 TVLIBR3
        if "tvlibr3.com" in url:
            final_url = extract_tvlibr3(url)

        # 🔥 TELEGRATUITA
        else:
            final_url = extract_telegratuita(url)

        if not final_url:
            print("❌ No se pudo obtener stream")
            continue

        result["channels"].append({
            "name": name,
            "url": final_url
        })

        print("✅ FINAL:", final_url)

        time.sleep(1)

    except Exception as e:
        print("❌ ERROR GENERAL:", str(e))


# =========================
# 🔹 GUARDAR JSON
# =========================

with open("streams.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n🔥 JSON actualizado:", len(result["channels"]))
    

