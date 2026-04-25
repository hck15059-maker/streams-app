import cloudscraper
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import base64

BASE = "https://telegratuita.net"

channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 GEN": BASE + "/en-vivo/gentv.php",
    "📺 SNT (TVLIBRE)": "https://tvlibr3.com/en-vivo/snt/",  # 👈 agregado
}

result = {"channels": []}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE
}

session = cloudscraper.create_scraper()
session.headers.update(headers)

def extract_iframe(html):
    matches = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)
    return matches[0] if matches else None

def extract_m3u8(html):
    matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
    return matches[0] if matches else None

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

            print("🔓 Decodificado:", decoded)

            # 🔥 SI NO ES URL, hay que construirla
            if not decoded.startswith("http"):
                # Probá armar URL manual
                return f"https://tvlibr3.com/player/{decoded}"

            return decoded

        return src

    except Exception as e:
        print("❌ TVLIBRE ERROR:", e)

    return None


for name, url in channels.items():
    try:
        print("\n" + "="*50)
        print(f"📺 Canal: {name}")

        # 🔥 CASO ESPECIAL TVLIBRE
        if "tvlibr3" in url:
            final_url = extract_tvlibr3(url)

            if final_url:
                print("🔥 TVLIBRE EXTRAÍDO:", final_url)
                result["channels"].append({
                    "name": name,
                    "url": final_url
                })
            continue

        # 🔹 Método normal (primer script)
        res = session.get(url, timeout=15)
        html = res.text

        iframe = extract_iframe(html)
        if not iframe:
            print("❌ iframe no encontrado")
            continue

        full_iframe = iframe if iframe.startswith("http") else BASE + iframe
        print("🎬 IFRAME:", full_iframe)

        time.sleep(1)

        res2 = session.get(full_iframe, timeout=15)
        html2 = res2.text

        m3u8 = extract_m3u8(html2)

        final_url = m3u8 if m3u8 else full_iframe

        result["channels"].append({
            "name": name,
            "url": final_url
        })

        print("✅ FINAL:", final_url)

    except Exception as e:
        print("❌ ERROR:", str(e))


# Guardar JSON
with open("streams.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n🔥 JSON actualizado:", len(result["channels"]))

    
    

