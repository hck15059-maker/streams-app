import requests
from bs4 import BeautifulSoup
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
    "📺 A&E": BASE + "/en-vivo/ae.php",
    "📺 AXN": BASE + "/en-vivo/axn.php",
    "📺 TNT": BASE + "/en-vivo/tnt.php",
    "📺 HBO": BASE + "/en-vivo/hbo.php",
    "📺 De Pelicula": BASE + "/live/depelicula.php",
    "📺 Space": BASE + "/en-vivo/space.php",
    "📺 Cine Max": BASE + "/en-vivo/cinemax.php",
    "📺 Cinecanal": BASE + "/en-vivo/cinecanal.php",
    "📺 TNT Series": BASE + "/en-vivo/tntseries.php",
    "📺 Discovery Channel": BASE + "/en-vivo/discovery-channel.php",
    "📺 Discovery Home": BASE + "/en-vivo/discovery-home-and-health.php",
    "📺 Discovery ID": BASE + "/en-vivo/investigacion-discovery.php",
    "📺 Discovery Science": BASE + "/en-vivo/discovery-science.php",
    "📺 Animal Planet": BASE + "/en-vivo/animalplanet.php",
}

tvlibr3_channels = {
    "📺 SNT": "https://tvlibr3.com/en-vivo/snt/",
    "📺 Telefuturo": "https://tvlibr3.com/en-vivo/telefuturo/",
    "📺 Trece": "https://tvlibr3.com/en-vivo/trecepy/",
    "📺 C9N": "https://tvlibr3.com/en-vivo/c9n/",
    "📺 NPY": "https://tvlibr3.com/en-vivo/noticiaspy/",
    "📺 LaTele": "https://tvlibr3.com/en-vivo/latele/",
    "📺 ESPN1": "https://tvlibr3.com/en-vivo/espn/",
    "📺 ESPN2": "https://tvlibr3.com/en-vivo/espn-2/",
    "📺 ESPN3": "https://tvlibr3.com/en-vivo/espn-3/",
    "📺 Fox Sports": "https://tvlibr3.com/en-vivo/fox-sports/",
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "es-ES,es;q=0.9"
}

session = cloudscraper.create_scraper()
session.headers.update(headers)

# =========================
# 🔥 LIMPIAR NOMBRE
# =========================

def clean_channel_name(name):
    return name.lower() \
        .replace("📺", "") \
        .replace(" ", "") \
        .replace(".", "") \
        .strip()

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

            match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)

            if match:
                final_url = match.group(0)

                result.append({
                    "name": name.strip(),
                    "id": clean_channel_name(name),
                    "url": final_url,
                    "source": "telegratuita"
                })

                print("✅ REPRO:", final_url)
                continue

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
                        "name": name.strip(),
                        "id": clean_channel_name(name),
                        "url": final_url,
                        "source": "telegratuita"
                    })

                    print("✅ REPRO iframe:", final_url)
                    continue

                result.append({
                    "name": name.strip(),
                    "id": clean_channel_name(name),
                    "url": full_iframe,
                    "source": "iframe"
                })

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
                    "name": name.strip(),
                    "id": clean_channel_name(name),
                    "url": final_url,
                    "source": "tvlibr3"
                })

                print("✅ OK:", final_url)

            else:
                result.append({
                    "name": name.strip(),
                    "id": clean_channel_name(name),
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
