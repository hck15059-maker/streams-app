import requests
from bs4 import BeautifulSoup
import base64
import re
import json
import time
from urllib.parse import urljoin

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://telegratuita.net/",
    "Connection": "keep-alive"
}

import cloudscraper

session = cloudscraper.create_scraper()
session.headers.update(headers)


def scrape_telegratuita(session, BASE, channels, max_retries=3):
    result = []
    
    for name, url in channels.items():
        retries = 0
        success = False
        
        while retries < max_retries and not success:
            try:
                print(f"\n📺 TELEGRATUITA: {name} (Intento {retries + 1})")

                res = session.get(url, timeout=15)
                res.raise_for_status()  # Lanza excepción para códigos de error HTTP
                html = res.text

                # 🔥 1. BUSCAR repro DIRECTO (CLAVE)
                match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)
                if match:
                    final_url = match.group(0)

                    result.append({
                        "name": name,
                        "url": final_url,
                        "source": "telegratuita_direct"
                    })

                    print("✅ REPRO DIRECTO:", final_url)
                    success = True
                    continue

                # 🔥 2. SI NO, intentar iframe
                iframe = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)

                if iframe:
                    iframe_url = iframe[0]
                    full_iframe = iframe_url if iframe_url.startswith("http") else urljoin(BASE, iframe_url)

                    res2 = session.get(full_iframe, timeout=15)
                    res2.raise_for_status()
                    html2 = res2.text

                    match2 = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html2)
                    if match2:
                        final_url = match2.group(0)

                        result.append({
                            "name": name,
                            "url": final_url,
                            "source": "telegratuita_iframe"
                        })

                        print("✅ REPRO DESDE IFRAME:", final_url)
                        success = True
                        continue

                    # fallback
                    result.append({
                        "name": name,
                        "url": full_iframe,
                        "source": "telegratuita_iframe_fallback"
                    })

                    print("⚠️ usando iframe:", full_iframe)
                    success = True
                    continue

                else:
                    print("❌ No se encontró nada útil")
                    success = True  # Para no reintentar si no hay contenido

            except requests.exceptions.RequestException as e:
                print(f"❌ TELEGRATUITA ERROR (Intento {retries + 1}):", e)
                retries += 1
                time.sleep(2)  # Esperar antes de reintentar
            except Exception as e:
                print(f"❌ TELEGRATUITA ERROR INESPERADO (Intento {retries + 1}):", e)
                retries += 1
                time.sleep(2)
    
    return result


# =========================
# 🔹 TVLIBR3
# =========================

def scrape_tvlibr3(max_retries=3):
    url = "https://tvlibr3.com/en-vivo/snt/"
    url = "https://tvlibr3.com/en-vivo/latele/"
    result = []
    retries = 0
    
    while retries < max_retries:
        try:
            print(f"\n📺 TVLIBR3: SNT (Intento {retries + 1})")

            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            iframe = soup.find('iframe', {'id': 'iframe'})
            if not iframe:
                print("❌ No se encontró el iframe")
                break

            src = iframe.get('src')

            if '?get=' in src:
                encoded_param = src.split('?get=')[1]
                
                # 🔥 Decodificamos para ver qué contiene
                try:
                    decoded_param = base64.b64decode(encoded_param).decode('utf-8')
                    print(f"🔍 Parámetro decodificado: {decoded_param}")
                except:
                    print("🔍 No se pudo decodificar el parámetro")

                final_url = f"https://tvlibr3.com/html/fl/?get={encoded_param}"

                result.append({
                    "name": "📺 SNT ",
                    "url": final_url,
                    "source": "tvlibr3",
                    "decoded_param": decoded_param if 'decoded_param' in locals() else None
                })
                break

            else:
                result.append({
                    "name": "📺 SNT (TVLIBR3)",
                    "url": src,
                    "source": "tvlibr3_direct"
                })
                break

        except requests.exceptions.RequestException as e:
            print(f"❌ TVLIBR3 ERROR (Intento {retries + 1}):", e)
            retries += 1
            time.sleep(2)
        except Exception as e:
            print(f"❌ TVLIBR3 ERROR INESPERADO (Intento {retries + 1}):", e)
            retries += 1
            time.sleep(2)
    
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
