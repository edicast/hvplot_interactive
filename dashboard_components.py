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
            pn.pane.Markdown(f"### {self.dashboard.name} Chart"),
            self.plot_type,
            *self.filter_widgets,
            self.yaxis,
            self.plot_pane,
            width=1000
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

        if plot_type in ["stacked_line", "stacked_bar"]:
            # Validate that grouping_config exists and is not empty
            if not hasattr(self.dashboard, 'grouping_config') or not self.dashboard.grouping_config:
                return pn.pane.Markdown("⚠️ Stacked plot: `grouping_config` is missing or empty in dashboard configuration.", height=100)

            # Use the first configuration entry for stacked plot parameters
            group_config = self.dashboard.grouping_config[0]
            
            stack_by_col = group_config.get("measure")
            operation_name = group_config.get("operation")  # e.g., "mean", "sum", "count"
            x_axis_col = self.dashboard.xaxis_col   # Default to "mpg" if "xaxis" is not in config

            # --- Validate configuration and DataFrame columns ---
            if not stack_by_col:
                return pn.pane.Markdown("⚠️ Stacked plot: `measure` (for stacking) is missing in `grouping_config`.", height=100)
            if not operation_name:
                return pn.pane.Markdown("⚠️ Stacked plot: `operation` (e.g., 'mean') is missing in `grouping_config`.", height=100)

            if yaxis not in df.columns: # yaxis is a parameter to _generate_plot
                return pn.pane.Markdown(f"⚠️ Y-axis column '{yaxis}' not found in DataFrame.", height=100)
            if stack_by_col not in df.columns:
                return pn.pane.Markdown(f"⚠️ Stacked plot: Grouping column '{stack_by_col}' (from `measure`) not found in DataFrame.", height=100)
            if x_axis_col not in df.columns:
                return pn.pane.Markdown(f"⚠️ Stacked plot: X-axis column '{x_axis_col}' not found in DataFrame.", height=100)

            # For this type of stacked plot, the stacking dimension and x-axis should ideally be different.
            if stack_by_col == x_axis_col:
                return pn.pane.Markdown(
                    f"⚠️ Stacked plot: `measure` ('{stack_by_col}') and `xaxis` ('{x_axis_col}') "
                    f"should be different columns for this plot type.", height=100
                )

            # --- Perform dynamic grouping and aggregation ---
            try:
                # Group by the stacking column and the x-axis column, then aggregate the y-axis.
                # `as_index=False` makes the grouped keys into columns in the resulting DataFrame.
                df_grouped = df.groupby([stack_by_col, x_axis_col], as_index=False)[yaxis].agg(operation_name)
                
                # Pandas `agg` with a string function on a SeriesGroupBy typically names the result column
                # after the original Series (which is `yaxis` here). So, df_grouped should have `yaxis` as the aggregated value column.
            except Exception as e:
                # Catch errors from invalid operation_name or other Pandas grouping/aggregation issues
                return pn.pane.Markdown(f"⚠️ Error during data aggregation for stacked plot: {e}", height=100)
            
            if df_grouped.empty:
                return pn.pane.Markdown("⚠️ Stacked plot: No data available after grouping.", height=100)

            # --- Generate plots for each group ---
            plots = []
            # Sort unique values from the stack_by_col for consistent legend order
            unique_stack_values = sorted(df_grouped[stack_by_col].unique())

            for group_value in unique_stack_values:
                # Filter data for the current group value
                dfo = df_grouped[df_grouped[stack_by_col] == group_value]
                
                if not dfo.empty:
                    plot_label = str(group_value)  # Ensure the label is a string for hvplot
                    
                    # Determine plot function based on plot_type
                    plot_func = dfo.hvplot.area if plot_type == "stacked_line" else dfo.hvplot.bar
                    
                    # Create the plot for the current group
                    # Uses the dynamically determined x_axis_col and the aggregated yaxis column
                    plot = plot_func(x=x_axis_col, y=yaxis, label=plot_label)
                    plots.append(plot)

            if not plots:
                # This message means that even if df_grouped had data, no individual group yielded a plot.
                return pn.pane.Markdown("⚠️ Stacked plot: No data to display in any group after processing.", height=100)

            # Combine the individual plots into an Overlay
            return hv.Overlay(plots).opts(
                legend_position="right", 
                responsive=True, 
                height=300, 
                width=1000  # As per your addition in the prompt
            )
        # Gráficos normales
        return df.hvplot(
            x=self.dashboard.xaxis_col,
            y=yaxis,
            by=self.dashboard.xaxis_col,
            cmap="Category10",
            #color="Category10",
            kind=plot_type,# if plot_type == "line" else "bar",
            #legend_position="top_right",
            responsive=True,
            height=300,
            legend_position="right" 
        )

