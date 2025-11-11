import webbrowser
import time
import requests

def open_react():
    url = "http://localhost:5173"
    for _ in range(20):
        try:
            requests.get(url)
            webbrowser.open(url)
            print(f"✅ Opened React app at {url}")
            return
        except:
            time.sleep(1)
    print("⚠️ React dev server not detected. Start it with `npm run dev`.")
