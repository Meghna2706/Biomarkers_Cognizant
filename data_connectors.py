import fitbit, json, xml.etree.ElementTree as ET

class FitbitConnector:
    def __init__(self, access_token: str):
        self.client = fitbit.Fitbit(access_token=access_token)

    def get_today(self) -> dict:
        hrv   = self.client.intraday_time_series('activities/heart', detail_level='1min')
        sleep = self.client.get_sleep(date='today')
        steps = self.client.activities()['summary']['steps']
        return {"hrv": hrv, "sleep": sleep["summary"]["totalTimeInBed"]/60, "steps": steps}

class AppleHealthConnector:
    def parse_export(self, xml_path: str) -> list:
        tree = ET.parse(xml_path)
        records = tree.getroot().findall("Record")
        hrv_records = [r for r in records
                       if r.get("type") == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN"]
        return [{"value": float(r.get("value")),
                  "date": r.get("startDate")} for r in hrv_records]

# Option 3: WESAD academic dataset (free, validated)
# archive.ics.uci.edu/dataset/465/wesad
def load_wesad(subject_id: int) -> list:
    import pickle
    with open(f"WESAD/S{subject_id}/S{subject_id}.pkl", "rb") as f:
        data = pickle.load(f, encoding="latin1")
    return data["signal"]["wrist"]