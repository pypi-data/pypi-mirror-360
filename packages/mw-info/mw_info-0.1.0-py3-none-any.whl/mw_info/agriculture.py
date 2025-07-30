import os
import yaml

class AgriInfoMW: 
    def __init__(self, file_path=None): 
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "data/agriculture_data.yml")
        with open(file_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)
        self.crops = self.data.get("crops", []) 
        self.fish = self.data.get("fish", [])

    def get_all_crops(self):
        return self.crops

    def get_all_fish(self):
        return self.fish

    def find_crop(self, name):
        return self._find_item(name, self.crops)

    def find_fish(self, name):
        return self._find_item(name, self.fish)

    def _find_item(self, name, items):
        name_lower = name.lower()
        for item in items:
            if (
                item["chichewa"].lower() == name_lower
                or item["english"].lower() == name_lower
                or item["scientific"].lower() == name_lower
            ):
                return item
        return None
  