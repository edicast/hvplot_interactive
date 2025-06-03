
import panel as pn
import pandas as pd
import holoviews as hv
import hvplot.pandas

PALETTE = ["#ff6f69", "#ffcc5c", "#88d8b0"]
PLOT_TYPE_OPTIONS = ['line', 'stacked_line', 'bar', 'stacked_bar']

class InteractiveDashboard:
    def __init__(self, df, shared_cylinder_widget, yaxis_options, filter_config, initial_plot_type='line'):
        self.df = df
        self.shared_cylinders = shared_cylinder_widget
        self.yaxis_options = yaxis_options
        self.filter_config = filter_config

        # Widgets internos exclusivos de este dashboard
        self.plot_type_widget = pn.widgets.RadioButtonGroup(
            name='Tipo de Gráfica',
            options=PLOT_TYPE_OPTIONS,
            value=initial_plot_type,
            button_type='default'
        )

        self.yaxis_widget = pn.widgets.RadioButtonGroup(
            name='Y axis',
            options=self.yaxis_options,
            value=self.yaxis_options[0],
            button_type='success'
        )

        self.custom_filter_widgets = self._create_filter_widgets()

        self._plot_pane = pn.bind(self._generate_plot,
                                  plot_type=self.plot_type_widget,
                                  yaxis=self.yaxis_widget,
                                  **{f"f_{i}": w for i, w in enumerate(self.custom_filter_widgets)},
                                  cylinders=self.shared_cylinders)

    def _create_filter_widgets(self):
        widgets = []
        for config in self.filter_config:
            if config['type'] == 'multiselect':
                widget = pn.widgets.MultiSelect(
                    name=config.get('label', config['column']),
                    options=config.get('options', []),
                    value=config.get('default_value', []),
                    sizing_mode='stretch_width'
                )
            elif config['type'] == 'text_filter':
                widget = pn.widgets.TextInput(
                    name=config.get('label', config['column']),
                    placeholder=f"Filtrar {config['column']}...",
                    sizing_mode='stretch_width'
                )
            else:
                continue
            widgets.append(widget)
        return widgets

    def _generate_plot(self, plot_type, yaxis, cylinders, **filters):
        df = self.df.copy()

        df = df[df['cyl'] == cylinders]

        for i, config in enumerate(self.filter_config):
            widget_value = filters.get(f"f_{i}")
            col = config['column']
            if config['type'] == 'multiselect' and widget_value:
                df = df[df[col].isin(widget_value)]
            elif config['type'] == 'text_filter' and widget_value:
                df = df[df[col].str.contains(widget_value, case=False, na=False)]

        if plot_type in ['stacked_line', 'stacked_bar']:
            df = df.groupby(['origin', 'mpg'])[yaxis].mean().reset_index()
            overlays = []
            for origin in df['origin'].unique():
                dfo = df[df['origin'] == origin]
                if plot_type == 'stacked_line':
                    plot = dfo.hvplot.area(x='mpg', y=yaxis, label=origin, stacked=True)
                else:
                    plot = dfo.hvplot.bar(x='mpg', y=yaxis, label=origin, stacked=True)
                overlays.append(plot)
            return hv.Overlay(overlays).opts(
                legend_position='right',
                show_legend=True,
                responsive=True,
                height=300,
                width=700
            )

        # No apilados
        hvplot_args = {
            'x': 'mpg',
            'y': yaxis,
            'by': 'origin',
            'color': PALETTE,
            'height': 300,
            'responsive': True,
            'legend_position': 'right',
            'kind': 'line' if plot_type == 'line' else 'bar'
        }

        return df.hvplot(**hvplot_args)


    def view(self):
        return pn.Column(
            self.plot_type_widget,
            *self.custom_filter_widgets,
            self.yaxis_widget,
            self._plot_pane,
            sizing_mode='stretch_width'
        )
