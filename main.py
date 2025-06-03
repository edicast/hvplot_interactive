from view_manager import ViewManager
import pandas as pd

df = pd.read_csv("data.csv")

filter_config = [
    {'type': 'multiselect', 'column': 'mfr', 'label': 'Fabricantes', 'options': sorted(df['mfr'].unique()), 'default_value': sorted(df['mfr'].unique())},
    {'type': 'text_filter', 'column': 'origin', 'label': 'Buscar Nombre origen'}
]

yaxis_options = ['hp', 'weight']

vm = ViewManager(df, yaxis_options, filter_config)
for plot_type in ['line', 'stacked_line', 'bar', 'stacked_bar']:
    vm.add_dashboard(plot_type)
vm.serve()
