import requests
import json
import os

# --- ตั้งค่าเริ่มต้น ---
# หาก API ต้องใช้ Key ให้ตั้งค่าใน GitHub Secrets แล้วดึงมาใช้ด้วย os.getenv('API_KEY')
API_URL = "ใส่_URL_API_ของคุณที่นี่"
OUTPUT_FILE = "temperature_data.geojson"

def fetch_and_transform():
    try:
        # ดึงข้อมูลจาก API
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()  # ตรวจสอบว่า API ตอบกลับมาปกติ (200)
        data = response.json()

        # สร้าง FeatureCollection ของ GeoJSON
        features = []
        
        # เข้าถึงรายการข้อมูลใน JSON (ตามโครงสร้างที่ส่งมาให้)
        items = data.get("data", {}).get("data", [])

        for item in items:
            # ดึงพิกัด (ต้องระบุให้ถูกว่าอยู่ใน station หรือส่วนไหน)
            lat = item.get("station", {}).get("tele_station_lat")
            lon = item.get("station", {}).get("tele_station_long")

            # ข้ามถ้าไม่มีพิกัด
            if lat is None or lon is None:
                continue

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)]
                },
                "properties": {
                    "station_name": item.get("station", {}).get("tele_station_name", {}).get("th"),
                    "temperature": item.get("temperature"),
                    "datetime": item.get("temperature_datetime"),
                    "province": item.get("geocode", {}).get("province_name", {}).get("th"),
                    "amphoe": item.get("geocode", {}).get("amphoe_name", {}).get("th"),
                    "area": item.get("geocode", {}).get("area_name", {}).get("th")
                }
            }
            features.append(feature)

        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }

        # เขียนไฟล์ GeoJSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=2)
        
        print(f"Success: {len(features)} stations updated in {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_transform()
