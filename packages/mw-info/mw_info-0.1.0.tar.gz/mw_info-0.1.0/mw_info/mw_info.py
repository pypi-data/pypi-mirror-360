import os
import yaml

class DistrictInfo:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "data/district_data.yml")
        with open(path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get_all_districts(self):
        return [d["district"] for d in self.data.get("districts", [])]  

    def get_district_info(self, name, fields=None):
        name = name.strip().lower()
        for district in self.data.get("districts", []):
            if district["district"].lower() == name:
                if fields is None:
                    return district
                return {field: district.get(field) for field in fields}
        return None

    def filter_by_region(self, region):
        region = region.strip().lower()
        return [
            d for d in self.data.get("districts", [])
            if d.get("region", "").lower() == region
        ]

    def get_all_district_data(self):
        return self.data.get("districts", [])  
