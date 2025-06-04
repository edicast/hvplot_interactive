class Dashboard:
    def __init__(self, name, xaxis_col, yaxis_options, filter_config, grouping_config, initial_plot_type):
        self.name = name 
        self.yaxis_options = yaxis_options
        self.filter_config = filter_config
        self.grouping_config = grouping_config 
        self.initial_plot_type = initial_plot_type
        self.xaxis_col = xaxis_col
        

    @staticmethod
    def from_dict(data):
        return Dashboard(
            name = data['name'],
            xaxis_col=data['xaxis_col'],
            yaxis_options=data['yaxis_options'],
            filter_config=data['filter_config'],
            grouping_config=data['grouping_config'],
            initial_plot_type=data['initial_plot_type']
        )

    def to_dict(self):
        return {
            'name': self.name,
            'xaxis_col': self.xaxis_col,
            'yaxis_options': self.yaxis_options,
            'filter_config': self.filter_config,
            'grouping_config': self.grouping_config,
            'initial_plot_type': self.initial_plot_type
        }
