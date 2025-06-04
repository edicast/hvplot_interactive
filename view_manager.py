import json
import os
from typing import List
from dashboard_components import InteractiveDashboard
import pandas as pd
import panel as pn
from dashboard_loader import DashboardLoader, ViewDefinitionLoader
from dashboard import Dashboard
from view_definition import ViewDefinition

PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

print("[DEBUG] Cargando dashboards y datos...")

class ViewManager:
    def __init__(self, df, shared_cylinder_widget, dashboards, view_definitions):
        self.df = df
        self.shared_cylinder_widget = shared_cylinder_widget
        self.dashboards_dict = {d.name: d for d in dashboards}
        self.view_definitions = view_definitions

        self.template = pn.template.MaterialTemplate(title="Dashboard Viewer")

        self.view_selector = pn.widgets.Select(
            name="View",
            options=[v.name for v in self.view_definitions],
            value=self.view_definitions[0].name if self.view_definitions else None
        )

        self.template.sidebar.append(pn.pane.Markdown("## Filtros Globales"))
        self.template.sidebar.append(pn.pane.Markdown("### Selección de Vista"))
        self.template.sidebar.append(self.view_selector)
        self.template.sidebar.append(pn.pane.Markdown("### Cilindros"))
        self.template.sidebar.append(self.shared_cylinder_widget)

        # Llama al renderizado enlazado con el selector
        self.template.main[:] = [pn.bind(self._update_view, self.view_selector)]

    def _update_view(self, selected_name):
        print(f"[TRACE] _update_view triggered with selected_name: {selected_name}")
        print(f"[TRACE] View definitions disponibles: {[v.name for v in self.view_definitions]}")

        selected_view = next((v for v in self.view_definitions if v.name == selected_name), None)
        if not selected_view:
            print(f"[ERROR] Vista '{selected_name}' no encontrada.")
            return pn.pane.Markdown("### Error: Vista no encontrada")

        dashboards = [self.dashboards_dict.get(name) for name in selected_view.dashboard_names if name in self.dashboards_dict]
        print(f"[DEBUG] Renderizando vista '{selected_view.name}' con {len(dashboards)} dashboards...")

        dashboard_views = [InteractiveDashboard(self.df, self.shared_cylinder_widget, db).view() for db in dashboards if db]

        col1 = pn.Column(*dashboard_views[:2])
        col2 = pn.Column(*dashboard_views[2:])
        n = len(dashboard_views)
        if n <= 2:
            layout = pn.Row(*dashboard_views)  # Una fila con 1 o 2 dashboards
        else:
            col1 = pn.Column(*dashboard_views[:n // 2])
            col2 = pn.Column(*dashboard_views[n // 2:])
            layout = pn.Row(col1, col2)
        return layout

    def serve(self):
        self.template.servable()
