import os
from tqdm import tqdm
import shutil
import os


def find_file(directory: str, filename: str, ignore_extension: bool = True, verbose: bool = True):
    if ignore_extension and '.' in filename:
        filename, _ = os.path.splitext(filename)
    find_result = []
    for root, dirs, files in tqdm(os.walk(directory)):
        if ignore_extension:
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                if file_name == filename:
                    find_result.append(os.path.join(root, file))
                    if verbose:
                        print(os.path.join(root, file))
        else:
            if filename in files:
                find_result.append(os.path.join(root, filename))
                if verbose:
                    print(os.path.join(root, filename))

    return find_result

def move(source_image_path, destination_folder_path, verbose: bool = False):

    os.makedirs(destination_folder_path, exist_ok=True)

    destination_path = os.path.join(destination_folder_path, os.path.basename(source_image_path))

    try:
        shutil.move(source_image_path, destination_path)
        if verbose:
            print(f"Success move '{source_image_path}' to '{destination_path}'")
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Cannot find '{source_image_path}'")
    except Exception as e:
        raise Exception(f"Error when moving '{source_image_path}' to '{destination_path}'")

def copy(source_image_path, destination_folder_path, verbose: bool = False):

    os.makedirs(destination_folder_path, exist_ok=True)

    destination_path = os.path.join(destination_folder_path, os.path.basename(source_image_path))

    try:
        shutil.copy(source_image_path, destination_path)
        if verbose:
            print(f'Success copying {source_image_path} to {destination_path}')
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Cannot find '{source_image_path}'")
    except Exception as e:
        raise Exception(f"Error when moving '{source_image_path}' to '{destination_path}'")

def move_list(source_image_list, destination_folder_path, verbose: bool = False):
    os.makedirs(destination_folder_path, exist_ok=True)
    for source_image_path in tqdm(source_image_list):
        move(source_image_path, destination_folder_path, verbose=verbose)

def copy_list(source_image_list, destination_folder_path, verbose: bool = False):
    os.makedirs(destination_folder_path, exist_ok=True)
    for source_image_path in tqdm(source_image_list):
        copy(source_image_path, destination_folder_path, verbose=verbose)

def find_files_by_extension(directory_path, extension):
    png_files_list = []
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.lower().endswith(f'.{extension}'):
                full_path = os.path.join(dirpath, filename)
                png_files_list.append(full_path)
    return png_files_list

def copy_rename(source_file_path, destination_folder_path, new_name, verbose: bool = False):
    os.makedirs(destination_folder_path, exist_ok=True)
    destination_path = os.path.join(destination_folder_path, os.path.basename(source_file_path))
    destination_file_path_with_new_name = os.path.join(destination_folder_path, new_name)

    try:
        shutil.copy2(source_file_path, destination_file_path_with_new_name)
        if verbose:
            print(f'Success copying {source_file_path} to {destination_path}')
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Cannot find '{source_file_path}'")
    except Exception as e:
        raise Exception(f"Error when moving '{source_file_path}' to '{destination_path}'")