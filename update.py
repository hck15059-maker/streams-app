import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin
import cloudscraper

# ==============================================================================
# 🔹 CONFIGURACIÓN Y DICCIONARIOS
# ==============================================================================

BASE_TELEGRATUITA = "https://telegratuita.net"

telegratuita_channels = {
    " Telefuturo": f"{BASE_TELEGRATUITA}/en-vivo/telefuturo.php",
    " Paravision": f"{BASE_TELEGRATUITA}/en-vivo/paravision.php",
    " GEN": f"{BASE_TELEGRATUITA}/en-vivo/gentv.php",
    " A&E": f"{BASE_TELEGRATUITA}/en-vivo/ae.php",
    " AXN": f"{BASE_TELEGRATUITA}/en-vivo/axn.php",
    " TNT": f"{BASE_TELEGRATUITA}/en-vivo/tnt.php",
    " HBO": f"{BASE_TELEGRATUITA}/en-vivo/hbo.php",
    " De Pelicula": f"{BASE_TELEGRATUITA}/live/depelicula.php",
    " Space": f"{BASE_TELEGRATUITA}/en-vivo/space.php",
    " Cine Max": f"{BASE_TELEGRATUITA}/en-vivo/cinemax.php",
    " Cinecanal": f"{BASE_TELEGRATUITA}/en-vivo/cinecanal.php",
    " TNT Serie": f"{BASE_TELEGRATUITA}/en-vivo/tntseries.php",
    " Discovery Chanel": f"{BASE_TELEGRATUITA}/en-vivo/discovery-channel.php",
    " Discovery Home": f"{BASE_TELEGRATUITA}/en-vivo/discovery-home-and-health.php",
    " Discovery ID": f"{BASE_TELEGRATUITA}/en-vivo/investigacion-discovery.php",
    " Discovery Science": f"{BASE_TELEGRATUITA}/en-vivo/discovery-science.php",
    " Animal Planet": f"{BASE_TELEGRATUITA}/en-vivo/animalplanet.php",
}

tvlibr3_channels = {
    " SNT": "https://tvlibr3.com/en-vivo/snt/",
    " Telefuturo": "https://tvlibr3.com/en-vivo/telefuturo/",
    " Trece": "https://tvlibr3.com/en-vivo/trecepy/",
    " C9N": "https://tvlibr3.com/en-vivo/c9n/",
    " NPY": "https://tvlibr3.com/en-vivo/noticiaspy/",
    " LaTele": "https://tvlibr3.com/en-vivo/latele/",
    " ESPN Premium": "https://tvlibr3.com/en-vivo/espn-premium/",
    " ESPN1": "https://tvlibr3.com/en-vivo/espn/",
    " ESPN2": "https://tvlibr3.com/en-vivo/espn-2/",
    " ESPN3": "https://tvlibr3.com/en-vivo/espn-3/",
    " ESPN4": "https://tvlibr3.com/en-vivo/espn-4/",
    " ESPN5": "https://tvlibr3.com/en-vivo/espn-5/",
    " ESPN6": "https://tvlibr3.com/en-vivo/espn-6/",
    " Fox Sport": "https://tvlibr3.com/en-vivo/fox-sports/",
    " Fox Sport2": "https://tvlibr3.com/en-vivo/fox-sports-2/",
    " Fox Sport3": "https://tvlibr3.com/en-vivo/fox-sports-3/",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": BASE_TELEGRATUITA
}

# Crear sesión anti-bloqueo
scraper = cloudscraper.create_scraper()
scraper.headers.update(headers)

# ==============================================================================
# 🔹 FUNCIONES DE SCRAPING
# ==============================================================================

def scrape_telegratuita(session, base_url, channels):
    results = []
    print(f"\n--- INICIANDO TELEGRATUITA ({len(channels)} canales) ---")
    
    for name, url in channels.items():
        try:
            print(f"Buscando: {name}...", end=" ", flush=True)
            res = session.get(url, timeout=15)
            html = res.text

            # Buscar reproductor directo
            match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)
            if match:
                final_url = match.group(0)
                results.append({"name": name, "url": final_url, "source": "telegratuita"})
                print("✅")
                continue

            # Fallback iframe
            iframes = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)
            if iframes:
                iframe_url = iframes[0]
                full_iframe = urljoin(base_url, iframe_url)

                res2 = session.get(full_iframe, timeout=15)
                match2 = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', res2.text)
                
                if match2:
                    final_url = match2.group(0)
                    results.append({"name": name, "url": final_url, "source": "telegratuita_iframe"})
                else:
                    results.append({"name": name, "url": full_iframe, "source": "iframe_direct"})
                print("✅ (iframe)")
            else:
                print("❌ No encontrado")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(0.5)
    return results


def scrape_tvlibr3(channels):
    results = []
    print(f"\n--- INICIANDO TVLIBR3 ({len(channels)} canales) ---")
    
    for name, url in channels.items():
        try:
            print(f"Buscando: {name}...", end=" ", flush=True)
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
                results.append({"name": name, "url": final_url, "source": "tvlibr3"})
                print("✅")
            else:
                results.append({"name": name, "url": src, "source": "direct"})
                print("✅ (src)")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(0.5)
    return results

# ==============================================================================
# 🔹 EJECUCIÓN Y GUARDADO
# ==============================================================================

if __name__ == "__main__":
    final_data = {"channels": []}

    # Ejecutar Scrapers
    final_data["channels"] += scrape_telegratuita(scraper, BASE_TELEGRATUITA, telegratuita_channels)
    final_data["channels"] += scrape_tvlibr3(tvlibr3_channels)

    # Guardar en archivo JSON
    output_file = "streams.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"\n🚀 PROCESO COMPLETADO")
    print(f"📦 Total canales capturados: {len(final_data['channels'])}")
    print(f"💾 Archivo guardado como: {output_file}")
