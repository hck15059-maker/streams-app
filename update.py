import requests
import json

BASE = "https://telegratuita.net"

# canales telegratuita
channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 gen": BASE + "/en-vivo/gentv.php",
    "📺 ae": BASE + "/en-vivo/ae.php",
    "📺 axn": BASE + "/en-vivo/axn.php",
}

session = requests.Session()

result = {"channels": []}

# 🔥 ejecutar separado
result["channels"] += scrape_telegratuita(session, BASE, channels)
result["channels"] += scrape_tvlibr3()

# guardar JSON
with open("streams.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("🔥 TOTAL:", len(result["channels"]))
    

