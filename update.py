import cloudscraper
import re
import json
import time

BASE = "https://telegratuita.net"

channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 gen": BASE + "/en-vivo/gentv.php",
    "📺 ae": BASE + "/en-vivo/ae.php",
    "📺 axn": BASE + "/en-vivo/axn.php",
    "📺 Discovery ID": BASE + "/en-vivo/investigacion-discovery.php",
    "📺 NatGeo": BASE + "/en-vivo/natgeo.php",
    "📺 History": BASE + "/en-vivo/history-2.php",
    "📺 Space": BASE + "/en-vivo/space.php",
    "📺 TNT Series": BASE + "/en-vivo/tntseries.php",
    "📺 History Channel": BASE + "/en-vivo/history-channel.php",
    "📺 FOX": BASE + "/en-vivo/fox.php",
    "📺 TNT": BASE + "/en-vivo/tnt.php",
    "📺 Space": BASE + "/en-vivo/space.php",
    "📺 TNT Series": BASE + "/en-vivo/tntseries.php",
    "📺 History Channel": BASE + "/en-vivo/history-channel.php",
    "📺 FOX": BASE + "/en-vivo/fox.php",
    "📺 TNT": BASE + "/en-vivo/tnt.php",
    "📺 Space": BASE + "/en-vivo/space.php",
    "📺 TNT Series": BASE + "/en-vivo/tntseries.php",
    "📺 History Channel": BASE + "/en-vivo/history-channel.php",
    "📺 FOX": BASE + "/en-vivo/fox.php",
    "📺 TNT": BASE + "/en-vivo/tnt.php",
    "📺 Space": BASE + "/en-vivo/space.php",
    "📺 TNT Series": BASE + "/en-vivo/tntseries.php",
    "📺 History Channel": BASE + "/en-vivo/history-channel.php",
    "📺 FOX": BASE + "/en-vivo/fox.php",
    "📺 TNT": BASE + "/en-vivo/tnt.php",
 }   
    
  result = {"channels": []}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://telegratuita.net/",
    "Connection": "keep-alive"
}

session = cloudscraper.create_scraper()
session.headers.update(headers)

def extract_iframe(html):
    matches = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)
    return matches[0] if matches else None

def extract_m3u8(html):
    matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
    return matches[0] if matches else None

for name, url in channels.items():
    try:
        print("\n" + "="*50)
        print(f"📺 Canal: {name}")
        print("👉 URL:", url)

        # 🔹 Paso 1
        res = session.get(url, timeout=15)
        html = res.text

        print("📊 STATUS:", res.status_code)
        print(html[:500])

        iframe = extract_iframe(html)

        if not iframe:
            print("❌ iframe no encontrado (HTML estático)")
            continue

        # 🔥 FIX URL absoluta/relativa
        if iframe.startswith("http"):
            full_iframe = iframe
        else:
            full_iframe = BASE + iframe

        print("🎬 IFRAME:", full_iframe)

        time.sleep(1)  # anti-bloqueo simple

        # 🔹 Paso 2
        res2 = session.get(full_iframe, timeout=15)
        html2 = res2.text

        print("📊 PLAYER SIZE:", len(html2))

        # 🔹 Paso 3
        m3u8 = extract_m3u8(html2)

        if m3u8:
            final_url = m3u8
            print("🔥 M3U8 ENCONTRADO")
        else:
            final_url = full_iframe
            print("⚠️ No m3u8, usando iframe")

        result["channels"].append({
            "name": name,
            "url": final_url
        })

        print("✅ FINAL:", final_url)

    except Exception as e:
        print("❌ ERROR:", str(e))

# guardar JSON
if result["channels"]:
    with open("streams.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("JSON actualizado")
else:
    print("No se encontraron canales")

print("\n🔥 JSON actualizado:", len(result["channels"]))
  


    
    

