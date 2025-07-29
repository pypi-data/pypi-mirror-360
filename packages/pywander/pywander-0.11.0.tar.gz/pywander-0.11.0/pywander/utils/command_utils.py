import shutil
from pywander.config import load_all_config



def get_command_path(command_name):
    """
    略微智能一点的查找命令支持
    """
    command_path = command_name
    config = load_all_config()
    command_search_path = config.get(command_name.upper() + '_COMMAND_PATH', '.')

    if shutil.which(command_name):
        pass
    elif shutil.which(command_name, path=command_search_path):
        command_path = shutil.which(command_name, path=command_search_path)
    else:
        raise Exception(f"{command_name} not found.")

    return command_path