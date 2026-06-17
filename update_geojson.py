import requests
import json
import sys

# URL จริงจากที่คุณให้มา
API_URL = "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/thaiwater/temperature"
OUTPUT_FILE = "temperature_data.geojson"

def fetch_and_transform():
    print(f"DEBUG: Fetching data from {API_URL}")
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        # สำหรับ API ThaiWater โครงสร้างข้อมูลจะอยู่ที่ data -> data
        items = data.get("data", {}).get("data", [])
        
        if not items:
            print("ERROR: No data found in API response.")
            sys.exit(1)

        features = []
        for item in items:
            # ดึงตำแหน่งสถานี
            station = item.get("station", {})
            lat = station.get("tele_station_lat")
            lon = station.get("tele_station_long")

            # ข้ามสถานีที่ไม่มีพิกัด
            if lat is None or lon is None:
                continue

            # สร้าง Feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)]
                },
                "properties": {
                    "station_name": station.get("tele_station_name", {}).get("th", "N/A"),
                    "temperature": item.get("temperature"),
                    "datetime": item.get("temperature_datetime"),
                    "province": item.get("geocode", {}).get("province_name", {}).get("th", "N/A"),
                    "amphoe": item.get("geocode", {}).get("amphoe_name", {}).get("th", "N/A")
                }
            }
            features.append(feature)

        # บันทึกไฟล์
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False, indent=2)
        
        print(f"SUCCESS: {len(features)} stations processed.")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_transform()
