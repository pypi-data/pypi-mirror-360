import os
from tqdm import tqdm


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
