import json
import os
from typing import List

from dashboard import Dashboard

class DashboardLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def load_dashboards(self) -> List[Dashboard]:
        dashboards = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    dashboards.append(Dashboard.from_dict(data))
        print(f"[DEBUG] Dashboards cargados: {len(dashboards)}")
        return dashboards
