
import panel as pn
from dashboard_components import InteractiveDashboard
from dashboard import Dashboard
from typing import List
import pandas as pd

import json
import os
from typing import List
from dashboard_components import InteractiveDashboard  # Importar la nueva clase
import pandas as pd
import panel as pn
from dashboard_loader import DashboardLoader

PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

class ViewManager:
    def __init__(self, df: pd.DataFrame, shared_cylinder_widget: pn.widgets.Widget, dashboards: List[Dashboard]):
        self.df = df
        self.shared_cylinder_widget = shared_cylinder_widget
        self.dashboards = dashboards
        #self.template = pn.template.MaterialTemplate(title="Dashboard Viewer")
        self.template = pn.template.FastListTemplate(
            title="Multi-Dashboard con Sidebar Global",
            sidebar=[pn.pane.Markdown("## Filtros Globales"), self.shared_cylinder_widget],
            main=[],
            theme="default"
        )
        pn.extension("tabulator", sizing_mode="stretch_width", theme="default")

    def serve(self):
        dashboards = [self.dashboards[0]] * 4
        dashboard_views = [InteractiveDashboard(self.df, self.shared_cylinder_widget, db).view() for db in dashboards]

        col1 = pn.Column(*dashboard_views[:2])
        col2 = pn.Column(*dashboard_views[2:])

        self.template.sidebar.append(pn.pane.Markdown("### Filtros Globales"))
        self.template.sidebar.append(self.shared_cylinder_widget)

        self.template.main.append(pn.Row(col1, col2))
        self.template.servable()
