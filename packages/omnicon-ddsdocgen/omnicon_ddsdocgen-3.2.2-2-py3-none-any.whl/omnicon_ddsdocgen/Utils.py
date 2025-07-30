import os


def is_output_file_open(output_file_name: str, output_folder_name: str, file_type: str) -> bool:
    """
    This function checks if the output file is open
    """
    # TODO compatibility to linux
    output_file_name = f'{output_file_name}.{file_type}'
    full_output_path = os.path.join(output_folder_name, output_file_name)

    # Already checked if the folder exists. Checking if the file exists
    if os.path.exists(full_output_path):
        try:
            os.rename(full_output_path, full_output_path)
            return False
        except OSError:
            return True
    return False
