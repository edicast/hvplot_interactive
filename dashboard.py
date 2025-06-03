class Dashboard:
    def __init__(self, yaxis_options, filter_config, initial_plot_type):
        self.yaxis_options = yaxis_options
        self.filter_config = filter_config
        self.initial_plot_type = initial_plot_type

    @staticmethod
    def from_dict(data):
        return Dashboard(
            yaxis_options=data['yaxis_options'],
            filter_config=data['filter_config'],
            initial_plot_type=data['initial_plot_type']
        )

    def to_dict(self):
        return {
            'yaxis_options': self.yaxis_options,
            'filter_config': self.filter_config,
            'initial_plot_type': self.initial_plot_type
        }
