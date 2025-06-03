import os
import sys
import panel as pn
import pandas as pd
from dashboard_loader import DashboardLoader

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

print(f"[DEBUG] data.csv: {len(df)}")
print(f"[DEBUG] dashboards: {len(dashboards)}")

# Crear y construir el visor de dashboards
vm = ViewManager(df, cylinder_selector, dashboards)
vm.serve()

#app = vm.template

