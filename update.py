import requests
from bs4 import BeautifulSoup
import base64
import re
import json
import time
from urllib.parse import urljoin
import cloudscraper

# =========================
# 🔹 CONFIGURACIÓN
# =========================

BASE = "https://telegratuita.net"

telegratuita_channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 GEN": BASE + "/en-vivo/gentv.php",
    "📺 AE": BASE + "/en-vivo/ae.php",
    "📺 AXN": BASE + "/en-vivo/axn.php",
}

tvlibr3_channels = {
    "📺 SNT": "https://tvlibr3.com/en-vivo/snt/",
    "📺 Telefuturo": "https://tvlibr3.com/en-vivo/telefuturo/",
    "📺 Trece": "https://tvlibr3.com/en-vivo/trece/",
    "📺 C9N": "https://tvlibr3.com/en-vivo/c9n/",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": BASE
}

# sesión anti-bloqueo
session = cloudscraper.create_scraper()
session.headers.update(headers)

# =========================
# 🔹 TELEGRATUITA
# =========================

def scrape_telegratuita(session, BASE, channels):
    result = []

    for name, url in channels.items():
        try:
            print(f"\n📺 TELEGRATUITA: {name}")

            res = session.get(url, timeout=15)
            html = res.text

            # 🔥 buscar repro directo
            match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)
            if match:
                final_url = match.group(0)

                result.append({
                    "name": name,
                    "url": final_url,
                    "source": "telegratuita"
                })

                print("✅ REPRO:", final_url)
                continue

            # 🔹 fallback iframe
            iframe = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)

            if iframe:
                iframe_url = iframe[0]
                full_iframe = iframe_url if iframe_url.startswith("http") else urljoin(BASE, iframe_url)

                res2 = session.get(full_iframe, timeout=15)
                html2 = res2.text

                match2 = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html2)
                if match2:
                    final_url = match2.group(0)

                    result.append({
                        "name": name,
                        "url": final_url,
                        "source": "telegratuita_iframe"
                    })

                    print("✅ REPRO iframe:", final_url)
                    continue

                # fallback final
                result.append({
                    "name": name,
                    "url": full_iframe,
                    "source": "iframe"
                })

                print("⚠️ usando iframe:", full_iframe)

        except Exception as e:
            print("❌ ERROR TELEGRATUITA:", e)

        time.sleep(1)

    return result


# =========================
# 🔹 TVLIBR3
# =========================

def scrape_tvlibr3(channels):
    result = []

    for name, url in channels.items():
        try:
            print(f"\n📺 TVLIBR3: {name}")

            response = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            iframe = soup.find('iframe', {'id': 'iframe'})
            if not iframe:
                print("❌ No iframe")
                continue

            src = iframe.get('src')

            if '?get=' in src:
                encoded = src.split('?get=')[1]

                final_url = f"https://tvlibr3.com/html/fl/?get={encoded}"

                result.append({
                    "name": f"{name} (TVLIBR3)",
                    "url": final_url,
                    "source": "tvlibr3"
                })

                print("✅ OK:", final_url)

            else:
                result.append({
                    "name": f"{name} (TVLIBR3)",
                    "url": src,
                    "source": "direct"
                })

        except Exception as e:
            print(f"❌ ERROR TVLIBR3 {name}:", e)

        time.sleep(1)

    return result


# =========================
# 🔹 EJECUCIÓN
# =========================

result = {"channels": []}

result["channels"] += scrape_telegratuita(session, BASE, telegratuita_channels)
result["channels"] += scrape_tvlibr3(tvlibr3_channels)

# =========================
# 🔹 GUARDAR JSON
# =========================

with open("streams.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n🔥 TOTAL CANALES:", len(result["channels"]))
