import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin
import cloudscraper

# ==============================================================================
# 🔹 CONFIGURACIÓN
# ==============================================================================

BASE = "https://telegratuita.net"

telegratuita_channels = {
    "📺 Telefuturo": f"{BASE}/en-vivo/telefuturo.php",
    "📺 Paravision": f"{BASE}/en-vivo/paravision.php",
    "📺 GEN": f"{BASE}/en-vivo/gentv.php",
    "📺 A&E": f"{BASE}/en-vivo/ae.php",
    "📺 AXN": f"{BASE}/en-vivo/axn.php",
    "📺 TNT": f"{BASE}/en-vivo/tnt.php",
    "📺 HBO": f"{BASE}/en-vivo/hbo.php",
    "📺 De Pelicula": f"{BASE}/live/depelicula.php",
    "📺 Space": f"{BASE}/en-vivo/space.php",
    "📺 Cine Max": f"{BASE}/en-vivo/cinemax.php",
    "📺 Cinecanal": f"{BASE}/en-vivo/cinecanal.php",
    "📺 TNT Series": f"{BASE}/en-vivo/tntseries.php",
    "📺 Discovery Channel": f"{BASE}/en-vivo/discovery-channel.php",
    "📺 Discovery Home": f"{BASE}/en-vivo/discovery-home-and-health.php",
    "📺 Discovery ID": f"{BASE}/en-vivo/investigacion-discovery.php",
    "📺 Discovery Science": f"{BASE}/en-vivo/discovery-science.php",
    "📺 Animal Planet": f"{BASE}/en-vivo/animalplanet.php",
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
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": BASE
}

scraper = cloudscraper.create_scraper()
scraper.headers.update(headers)

# ==============================================================================
# 🔹 UTILIDADES
# ==============================================================================

def clean_channel_id(name: str) -> str:
    return name.lower().replace("📺", "").replace(" ", "").strip()

# ==============================================================================
# 🔹 TELEGRATUITA
# ==============================================================================

def scrape_telegratuita(session, base_url, channels):
    results = []

    print(f"\n--- TELEGRATUITA ({len(channels)} canales) ---")

    for name, url in channels.items():
        try:
            print(f"Buscando: {name}...", end=" ")

            res = session.get(url, timeout=15)
            html = res.text

            # 🔥 intento directo
            match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)
            if match:
                final_url = match.group(0)

                results.append({
                    "name": name,
                    "id": clean_channel_id(name),
                    "url": final_url,
                    "source": "telegratuita"
                })

                print("✅")
                continue

            # 🔹 fallback iframe
            iframes = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)

            if iframes:
                iframe_url = iframes[0]
                full_iframe = urljoin(base_url, iframe_url)

                res2 = session.get(full_iframe, timeout=15)
                html2 = res2.text

                match2 = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html2)

                if match2:
                    final_url = match2.group(0)

                    results.append({
                        "name": name,
                        "id": clean_channel_id(name),
                        "url": final_url,
                        "source": "telegratuita_iframe"
                    })
                else:
                    results.append({
                        "name": name,
                        "id": clean_channel_id(name),
                        "url": full_iframe,
                        "source": "iframe"
                    })

                print("✅ iframe")
            else:
                print("❌")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(0.5)

    return results

# ==============================================================================
# 🔹 TVLIBR3
# ==============================================================================

def scrape_tvlibr3(channels):
    results = []

    print(f"\n--- TVLIBR3 ({len(channels)} canales) ---")

    for name, url in channels.items():
        try:
            print(f"Buscando: {name}...", end=" ")

            response = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            iframe = soup.find('iframe', {'id': 'iframe'})

            if not iframe:
                print("❌ No iframe")
                continue

            src = iframe.get('src', '')

            if '?get=' in src:
                encoded = src.split('?get=')[1]
                final_url = f"https://tvlibr3.com/html/fl/?get={encoded}"

                results.append({
                    "name": name,
                    "id": clean_channel_id(name),
                    "url": final_url,
                    "source": "tvlibr3"
                })

                print("✅")
            else:
                results.append({
                    "name": name,
                    "id": clean_channel_id(name),
                    "url": src,
                    "source": "direct"
                })

                print("✅ src")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(0.5)

    return results

# ==============================================================================
# 🔹 MAIN
# ==============================================================================

if __name__ == "__main__":

    data = {"channels": []}

    data["channels"] += scrape_telegratuita(scraper, BASE, telegratuita_channels)
    data["channels"] += scrape_tvlibr3(tvlibr3_channels)

    with open("streams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n🚀 COMPLETADO")
    print(f"📺 Total canales: {len(data['channels'])}")
