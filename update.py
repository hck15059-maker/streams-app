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

    for name, url in channels.items():
        try:
            print("\n📺 TELEGRATUITA:", name)

            res = session.get(url, timeout=15)
            html = res.text

            # 🔥 1. BUSCAR repro DIRECTO (CLAVE)
            match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)
            if match:
                final_url = match.group(0)

                result.append({
                    "name": name,
                    "url": final_url
                })

                print("✅ REPRO DIRECTO:", final_url)
                continue

            # 🔥 2. SI NO, intentar iframe
            iframe = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)

            if iframe:
                iframe_url = iframe[0]
                full_iframe = iframe_url if iframe_url.startswith("http") else BASE + iframe_url

                res2 = session.get(full_iframe, timeout=15)
                html2 = res2.text

                match2 = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html2)
                if match2:
                    final_url = match2.group(0)

                    result.append({
                        "name": name,
                        "url": final_url
                    })

                    print("✅ REPRO DESDE IFRAME:", final_url)
                    continue

                # fallback
                result.append({
                    "name": name,
                    "url": full_iframe
                })

                print("⚠️ usando iframe:", full_iframe)

            else:
                print("❌ No se encontró nada útil")

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
