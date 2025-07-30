import os
import yaml

class DemographicsInfoMW:
    def __init__(self, yaml_path=None):
        if yaml_path is None:
            yaml_path = os.path.join(os.path.dirname(__file__), "data/demographics_data.yml")
        with open(yaml_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f).get("demographics", [])

    def get_all_districts(self):
        return [d["district"] for d in self.data]

    def get_district_data(self, name, fields=None):
        d = self._find_district(name)
        if not d:
            return None
        if fields is None:
            return d
        return {field: d.get(field, "N/A") for field in fields}

    def get_population_total(self, name):
        d = self._find_district(name)
        return d.get("population") if d else None

    def get_age_distribution(self, name):
        d = self._find_district(name)
        return d.get("age_distribution") if d else None

    def get_gender_ratio(self, name):
        d = self._find_district(name)
        return d.get("gender_ratio") if d else None

    def get_urban_rural_split(self, name):
        d = self._find_district(name)
        if not d:
            return None
        urban = d.get("urban_percent", 0)
        rural = 100 - urban
        return {"urban": urban, "rural": rural}

    def filter_by_urbanization(self, min_percent):
        return [
            d for d in self.data
            if d.get("urban_percent", 0) >= min_percent
        ]

    def population_over(self, threshold):
        return [
            d for d in self.data
            if d.get("population", 0) > threshold
        ]

    def _find_district(self, name):
        name = name.strip().lower()
        return next((d for d in self.data if d["district"].lower() == name), None)
