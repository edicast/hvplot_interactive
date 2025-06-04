import os
import sys
import panel as pn
import pandas as pd
from dashboard_loader import DashboardLoader, ViewDefinitionLoader

from view_manager import ViewManager

pn.extension()

# Asegurar que el path del proyecto esté en sys.path
sys.path.append(os.path.dirname(__file__))

# Ruta absoluta relativa a main.py
base_path = os.path.dirname(__file__)
csv_path = os.path.join(os.path.dirname(__file__), "data", "data.csv")

# Cargar datos
df = pd.read_csv(csv_path)

# Crear widget compartido
cylinder_selector = pn.widgets.Select(name='Cylinders', options=sorted(df['cyl'].unique()))

# Cargar configuración de dashboards
dashboard_loader = DashboardLoader('dashboards')
dashboards = dashboard_loader.load_dashboards()

# Cargar view definitions
view_loader = ViewDefinitionLoader("views")
views = view_loader.load_view_definitions()
print(f"[DEBUG] Views cargadas: {[v.name for v in views]}")

# Crear y servir la aplicación
vm = ViewManager(df, cylinder_selector, dashboards, views)
#vm.serve()

pn.panel(vm.template).servable()