import cloudscraper
import re
import json
import time

BASE = "https://telegratuita.net"

channels = {
    "📺 Telefuturo": BASE + "/en-vivo/telefuturo.php",
    "📺 Paravision": BASE + "/en-vivo/paravision.php",
    "📺 GEN": BASE + "/en-vivo/gentv.php",
    "📺 AE": BASE + "/en-vivo/ae.php",
    "📺 AXN": BASE + "/en-vivo/axn.php",
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE
}

# 🔥 cloudscraper (anti-bot)
session = cloudscraper.create_scraper()
session.headers.update(headers)


def find_repro(html):
    match = re.search(r'https://telegratuita\.net/repro/\?r=[^"\']+', html)
    return match.group(0) if match else None


def find_iframes(html):
    return re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)


def scrape_telegratuita():
    results = []

    for name, url in channels.items():
        try:
            print("\n" + "="*50)
            print(f"📺 Canal: {name}")

            # 🔹 PASO 1
            res = session.get(url, timeout=15)
            html = res.text

            print("📊 HTML SIZE:", len(html))

            # 🔥 intento directo
            repro = find_repro(html)
            if repro:
                print("✅ REPRO DIRECTO")
                results.append({"name": name, "url": repro})
                continue

            # 🔹 PASO 2 (iframe 1)
            iframes = find_iframes(html)

            if not iframes:
                print("❌ Sin iframe")
                continue

            for iframe in iframes:
                full_iframe = iframe if iframe.startswith("http") else BASE + iframe
                print("👉 IFRAME 1:", full_iframe)

                res2 = session.get(full_iframe, timeout=15)
                html2 = res2.text

                repro = find_repro(html2)
                if repro:
                    print("✅ REPRO EN IFRAME 1")
                    results.append({"name": name, "url": repro})
                    break

                # 🔹 PASO 3 (iframe dentro de iframe)
                iframes2 = find_iframes(html2)

                for iframe2 in iframes2:
                    full_iframe2 = iframe2 if iframe2.startswith("http") else BASE + iframe2
                    print("👉 IFRAME 2:", full_iframe2)

                    res3 = session.get(full_iframe2, timeout=15)
                    html3 = res3.text

                    repro = find_repro(html3)
                    if repro:
                        print("✅ REPRO EN IFRAME 2")
                        results.append({"name": name, "url": repro})
                        break

                else:
                    continue
                break

            time.sleep(1)  # anti-bloqueo

        except Exception as e:
            print("❌ ERROR:", e)

    return results


# =========================
# 🔹 EJECUCIÓN
# =========================

result = {"channels": []}

result["channels"] += scrape_telegratuita()

# guardar JSON
with open("streams.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\n🔥 TOTAL:", len(result["channels"]))
