# dashboard_components.py
import panel as pn
import hvplot.pandas
import pandas as pd

PALETTE = ["#ff6f69", "#ffcc5c", "#88d8b0"]

class InteractiveDashboard:
    def __init__(self, interactive_dataframe, cylinders_widget_from_notebook, yaxis_options_list):
        self.idf = interactive_dataframe
        self.cylinders_widget = cylinders_widget_from_notebook
        self.passed_yaxis_options = yaxis_options_list

        # Widgets internos de esta instancia de dashboard
        self.mfr_widget = pn.widgets.ToggleGroup(
            name='MFR',
            options=['ford', 'chevrolet', 'honda', 'toyota', 'audi'],
            value=['ford', 'chevrolet', 'honda', 'toyota', 'audi'],
            button_type='success'
        )
        initial_yaxis_value = self.passed_yaxis_options[0] if self.passed_yaxis_options else None
        self.yaxis_widget = pn.widgets.RadioButtonGroup(
            name='Y axis',
            options=self.passed_yaxis_options,
            value=initial_yaxis_value,
            button_type='success'
        )

        # Creación de pipeline y panes (gráfica, tabla)
        self._create_pipeline()
        self._create_plot_pane()
        # Si quieres la tabla, descomenta la siguiente línea y asegúrate que _create_table_pane existe y se usa
        # self._create_table_pane() 

    def _create_pipeline(self):
        self.ipipeline = (
            self.idf[
                (self.idf.cyl == self.cylinders_widget) &
                (self.idf.mfr.isin(self.mfr_widget))
            ]
            .groupby(['origin', 'mpg'])[self.yaxis_widget].mean()
            .to_frame().reset_index().sort_values(by='mpg').reset_index(drop=True)
        )

    def _create_plot_pane(self):
        self.ihvplot_pane = self.ipipeline.hvplot(
            x='mpg', y=self.yaxis_widget, by='origin',
            color=PALETTE, line_width=6, height=400
        )

    def _create_table_pane(self): # Descomentaste esto en tu código
        self.itable_pane = self.ipipeline.pipe(
            pn.widgets.Tabulator, pagination='remote', page_size=10
        )

    # ... (el __init__ y los métodos _create_pipeline, _create_plot_pane, _create_table_pane 
    #      permanecen como estaban, asegurándote que cylinders_widget se recibe 
    #      pero NO se añade al layout que devuelve get_view()) ...

    def get_dashboard_view(self): 
        """
        Construye y devuelve el layout del contenido principal de este dashboard
        (controles mfr/yaxis, gráfica, y tabla opcional).
        NO incluye el widget 'cylinders' aquí, ya que estará en una sidebar global.
        """
        # Controles superiores específicos para esta instancia (mfr, yaxis)
        instance_top_controls = pn.Column(self.mfr_widget, self.yaxis_widget)
        
        # Elementos principales (gráfica y tabla si está habilitada)
        main_elements = [self.ihvplot_pane.panel()]
        if hasattr(self, 'itable_pane') and self.itable_pane is not None: # Verifica que itable_pane exista y no sea None
             main_elements.append(self.itable_pane.panel())
        
        # Este es el contenido que se mostrará para UNA instancia de dashboard
        # (controles superiores + gráfica/tabla)
        instance_main_content_area = pn.Column(instance_top_controls, *main_elements)
        
        return instance_main_content_area # <--- MUY IMPORTANTE: Solo devuelve esta área.