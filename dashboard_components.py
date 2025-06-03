import panel as pn
import hvplot.pandas  # noqa: F401
import holoviews as hv

pn.extension()

class InteractiveDashboard:
    def __init__(self, df, shared_cylinder_widget, dashboard):
        self.df = df
        print(f"[DEBUG] dataframe en dashboard: {len(df)}")
        self.shared_cylinder_widget = shared_cylinder_widget
        self.dashboard = dashboard

        self.plot_type = pn.widgets.Select(
            name="Tipo de Gráfica",
            options=["line", "bar", "stacked_line", "stacked_bar"],
            value=dashboard.initial_plot_type
        )
        self.yaxis = pn.widgets.Select(
            name="Y axis",
            options=dashboard.yaxis_options,
            value=dashboard.yaxis_options[0]
        )

        self.filter_widgets = []
        for i, f in enumerate(dashboard.filter_config):
            if f["type"] == "multiselect":
                w = pn.widgets.MultiSelect(
                    name=f["label"],
                    options=f["options"],
                    value=f.get("default_value", f["options"])
                )
            elif f["type"] == "text_filter":
                w = pn.widgets.TextInput(name=f["label"], placeholder="...")
            else:
                continue
            self.filter_widgets.append(w)

        self.plot_pane = pn.bind(self._generate_plot, self.plot_type, self.yaxis, self.shared_cylinder_widget, *self.filter_widgets)

    def view(self):
        return pn.Column(
            pn.pane.Markdown(f"### {self.dashboard.initial_plot_type.title()} Chart"),
            self.plot_type,
            *self.filter_widgets,
            self.yaxis,
            self.plot_pane
        )

    def _generate_plot(self, plot_type, yaxis, cylinders, *filter_values):
        df = self.df.copy()
        df = df[df['cyl'] == cylinders]

        # Aplicar filtros definidos
        for i, val in enumerate(filter_values):
            f = self.dashboard.filter_config[i]
            col = f["column"]
            if f["type"] == "multiselect" and val:
                df = df[df[col].isin(val)]
            elif f["type"] == "text_filter" and val:
                df = df[df[col].str.contains(val, case=False, na=False)]

        if df.empty:
            return pn.pane.Markdown("⚠️ No hay datos después de aplicar los filtros.", height=100)

        # Verificación de columnas necesarias
        required_cols = {"mpg", yaxis, "origin"}
        if not required_cols.issubset(df.columns):
            return pn.pane.Markdown("⚠️ Columnas necesarias ausentes en los datos.", height=100)

        # Gráficos stacked
        if plot_type in ["stacked_line", "stacked_bar"]:
            df = df.groupby(["origin", "mpg"])[yaxis].mean().reset_index()
            plots = []
            for origin in df["origin"].unique():
                dfo = df[df["origin"] == origin]
                if not dfo.empty:
                    plot = (
                        dfo.hvplot.area(x="mpg", y=yaxis, label=origin)
                        if plot_type == "stacked_line"
                        else dfo.hvplot.bar(x="mpg", y=yaxis, label=origin)
                    )
                    plots.append(plot)

            if not plots:
                return pn.pane.Markdown("⚠️ No hay datos para representar en ningún grupo.", height=100)

            return hv.Overlay(plots).opts(
                legend_position="top_right", responsive=True, height=300
            )

        # Gráficos normales
        return df.hvplot(
            x="mpg",
            y=yaxis,
            by="origin",
            color="Category10",
            kind="line" if plot_type == "line" else "bar",
            legend_position="top_right",
            responsive=True,
            height=300
        )
