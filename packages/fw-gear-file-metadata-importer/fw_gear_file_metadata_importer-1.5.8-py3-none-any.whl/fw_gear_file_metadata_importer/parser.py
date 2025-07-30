"""Parser module."""


def parse_config(context):
    """Parses config.json."""
    file_type = context.get_input("input-file")["object"]["type"]
    file_path = context.get_input("input-file")["location"]["path"]
    config = context.config
    return file_path, file_type, config
