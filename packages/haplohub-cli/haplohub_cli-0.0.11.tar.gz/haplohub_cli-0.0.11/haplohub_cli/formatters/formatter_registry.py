from rich.console import Console


class FormatterRegistry:
    def __init__(self):
        self.formatters = {}
        self.console = Console()

    def register_formatter(self, model_type, formatter):
        self.formatters[model_type] = formatter

    def has_formatter(self, model_type):
        return model_type in self.formatters

    def format(self, model):
        formatter = self.formatters[type(model)]
        output = formatter(model)
        self.console.print(output)


formatter_registry = FormatterRegistry()
