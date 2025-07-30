from haplohub_cli.formatters.formatter_registry import formatter_registry


def register(model_type):
    def decorator(func):
        formatter_registry.register_formatter(model_type, func)
        return func

    return decorator
