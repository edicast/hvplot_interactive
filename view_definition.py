from typing import List

class ViewDefinition:
    def __init__(self, name: str, dashboard_names: List[str]):
        self.name = name
        self.dashboard_names = dashboard_names

    @staticmethod
    def from_dict(data):
        return ViewDefinition(
            name=data['name'],
            dashboard_names=data['dashboard_names']
        )

    def to_dict(self):
        return {
            'name': self.name,
            'dashboard_names': self.dashboard_names
        }