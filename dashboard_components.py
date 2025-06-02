# dashboard_components.py
import panel as pn
import hvplot.pandas
import pandas as pd

PALETTE = ["#ff6f69", "#ffcc5c", "#88d8b0"]

class InteractiveDashboard:
    def __init__(self, interactive_dataframe, cylinders_widget_from_notebook, 
                 yaxis_options_list, filter_config_list): # Nuevo parámetro filter_config_list
        self.idf = interactive_dataframe
        self.cylinders_widget = cylinders_widget_from_notebook
        self.passed_yaxis_options = yaxis_options_list
        self.filter_configs = filter_config_list # Guardar la configuración de filtros

        # Crear dinámicamente los widgets de filtro personalizados
        self.custom_filter_widgets = []
        # Guardaremos especificaciones de los filtros para usarlas en el pipeline
        self._active_filter_specs = [] 

        for config in self.filter_configs:
            label = config.get('label', config['column'].replace('_', ' ').capitalize()) # Etiqueta por defecto
            widget = None
            if config['type'] == 'multiselect':
                options = config.get('options', [])
                # Por defecto, seleccionamos todas las opciones como en el ToggleGroup original
                default_value = config.get('default_value', options) 
                widget = pn.widgets.MultiSelect(name=label, options=options, value=default_value, sizing_mode='stretch_width')
            elif config['type'] == 'text_filter':
                widget = pn.widgets.TextInput(name=label, placeholder=f"Filtrar {config['column']}...", sizing_mode='stretch_width')
            
            if widget:
                self.custom_filter_widgets.append(widget)
                self._active_filter_specs.append({'column': config['column'], 'type': config['type'], 'widget': widget})

        # Widget del eje Y (sin cambios en su creación)
        initial_yaxis_value = self.passed_yaxis_options[0] if self.passed_yaxis_options else None
        self.yaxis_widget = pn.widgets.RadioButtonGroup(
            name='Y axis',
            options=self.passed_yaxis_options,
            value=initial_yaxis_value,
            button_type='success'
        )

        self._create_pipeline()
        self._create_plot_pane()
        self._create_table_pane()

    def _create_pipeline(self):
        """Crea el pipeline de datos interactivo."""
        # Condición base (cilindros)
        current_pipeline_conditions = (self.idf.cyl == self.cylinders_widget)

        # Añadir condiciones de los filtros personalizados
        for spec in self._active_filter_specs:
            widget_instance = spec['widget'] # Este es el objeto widget en sí
            column_name = spec['column']
            filter_type = spec['type']

            if filter_type == 'multiselect':
                # Usar el widget_instance directamente con .isin()
                # .isin() es inteligente y usará widget_instance.value reactivamente
                current_pipeline_conditions &= (self.idf[column_name].isin(widget_instance))
            elif filter_type == 'text_filter':
                # Usar el widget_instance directamente con .str.contains()
                # .str.contains() también debería manejar el widget y usar su .value reactivamente.
                # Si el widget.value está vacío (''), .str.contains('') devuelve True para todo lo que no es NaN,
                # lo cual significa que no filtra si el campo de texto está vacío (comportamiento deseado).
                current_pipeline_conditions &= (
                    self.idf[column_name].astype(str).str.contains(widget_instance, case=False, na=False)
                )
        
        self.ipipeline = (
            self.idf[current_pipeline_conditions]
            .groupby(['origin', 'mpg'])[self.yaxis_widget].mean() # yaxis_widget ya se usa directamente, lo cual es correcto
            .to_frame().reset_index().sort_values(by='mpg').reset_index(drop=True)
        )

    def _create_plot_pane(self):
        self.ihvplot_pane = self.ipipeline.hvplot(
            x='mpg', y=self.yaxis_widget, by='origin',
            color=PALETTE, line_width=6, height=300,
            responsive=True,
            datashade=True, # <--- Esto activa datashader
            dynspread=True  # (Opcional) para mejorar la visualización de puntos dispersos con datashade
        )

    def _create_table_pane(self):
        self.itable_pane = self.ipipeline.pipe(
            pn.widgets.Tabulator, pagination='remote', page_size=5,
            sizing_mode='stretch_width'
        )

    def get_view(self):
        # Columna de controles internos: los filtros personalizados primero, luego el eje Y
        instance_internal_controls = pn.Column(*(self.custom_filter_widgets + [self.yaxis_widget]))
        
        main_elements = [self.ihvplot_pane.panel()]
        if hasattr(self, 'itable_pane') and self.itable_pane is not None:
             main_elements.append(self.itable_pane.panel())
        
        instance_plot_and_table_area = pn.Column(*main_elements, sizing_mode='stretch_width')
        
        instance_layout_block = pn.Column(
            instance_internal_controls, 
            instance_plot_and_table_area,
            sizing_mode='stretch_width'
        )
        return instance_layout_block