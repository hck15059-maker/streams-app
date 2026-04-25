import requests
from bs4 import BeautifulSoup
import base64
import re
import json

# =========================
# 🔹 TELEGRATUITA
# =========================

BASE = "https://telegratuita.net"

channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 GEN": BASE + "/en-vivo/gentv.php",
    "📺 AE": BASE + "/en-vivo/ae.php",
    "📺 AXN": BASE + "/en-vivo/axn.php",
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(headers)


def scrape_telegratuita(session, BASE, channels):

    result = []

    def extract_iframe(html):
        matches = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)
        return matches[0] if matches else None

    def extract_m3u8(html):
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
        return matches[0] if matches else None

    for name, url in channels.items():
        try:
            print("\n📺 TELEGRATUITA:", name)

            res = session.get(url, timeout=15)
            html = res.text

            iframe = extract_iframe(html)

            # 🔥 si no hay iframe
            if not iframe:
                m3u8 = extract_m3u8(html)
                if m3u8:
                    result.append({"name": name, "url": m3u8})
                continue

            full_iframe = iframe if iframe.startswith("http") else BASE + iframe

            res2 = session.get(full_iframe, timeout=15)
            html2 = res2.text

            m3u8 = extract_m3u8(html2)

            final_url = m3u8 if m3u8 else full_iframe

            result.append({
                "name": name,
                "url": final_url
            })

        except Exception as e:
            print("❌ TELEGRATUITA ERROR:", e)

    return result


# =========================
# 🔹 TVLIBR3
# =========================

def scrape_tvlibr3():

    url = "https://tvlibr3.com/en-vivo/snt/"
    result = []

    try:
        print("\n📺 TVLIBR3: SNT")

        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        iframe = soup.find('iframe', {'id': 'iframe'})
        if not iframe:
            return result

        src = iframe.get('src')

        if '?get=' in src:
            encoded_param = src.split('?get=')[1]

            # 🔥 NO decodificamos, solo construimos URL correcta
            final_url = f"https://tvlibr3.com/html/fl/?get={encoded_param}"

            result.append({
                "name": "📺 SNT (TVLIBR3)",
                "url": final_url
            })

        else:
            result.append({
                "name": "📺 SNT (TVLIBR3)",
                "url": src
            })

    except Exception as e:
        print("❌ TVLIBR3 ERROR:", e)

    return result


# =========================
# 🔹 EJECUCIÓN PRINCIPAL
# =========================

result = {"channels": []}

# ejecutar por separado (tu idea)
result["channels"] += scrape_telegratuita(session, BASE, channels)
result["channels"] += scrape_tvlibr3()

# =========================
# 🔹 GUARDAR JSON
# =========================

with open("streams.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n🔥 TOTAL CANALES:", len(result["channels"]))
