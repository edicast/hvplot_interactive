
import panel as pn
from dashboard_components import InteractiveDashboard

class ViewManager:
    def __init__(self, df, yaxis_options, filter_config):
        self.df = df
        self.yaxis_options = yaxis_options
        self.filter_config = filter_config

        self.shared_cylinders_widget = pn.widgets.IntSlider(
            name='Cylinders (Shared)', start=4, end=8, step=2, value=4
        )

        self.template = pn.template.FastListTemplate(
            title='Multi-Dashboard con Sidebar Global',
            sidebar=[self.shared_cylinders_widget],
            main=[],
            accent_base_color="#88d8b0",
            header_background="#88d8b0"
        )

        self._dashboards = []

    def add_dashboard(self, initial_plot_type='line'):
        dashboard = InteractiveDashboard(
            df=self.df,
            shared_cylinder_widget=self.shared_cylinders_widget,
            yaxis_options=self.yaxis_options,
            filter_config=self.filter_config,
            initial_plot_type=initial_plot_type
        )
        self._dashboards.append(dashboard)

    def build_layout(self):
        col1 = pn.Column(sizing_mode='stretch_width')
        col2 = pn.Column(sizing_mode='stretch_width')
        for i, dashboard in enumerate(self._dashboards):
            (col1 if i % 2 == 0 else col2).append(dashboard.view())
        self.template.main[:] = [pn.Row(col1, col2, sizing_mode='stretch_width')]

    def serve(self):
        self.build_layout()
        self.template.servable()
