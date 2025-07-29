from pathlib import Path
from appdirs import user_data_dir
import json
from typing import List

import sys
sys.path.append(Path(__file__).parent.parent.absolute().as_posix())

import importlib_resources as resources
from perfect_cmaps import lab_control_points
from perfect_cmaps import test_images


app_name = "perfect_cmaps"
data_dir = Path(user_data_dir(app_name))
data_dir.mkdir(parents=True, exist_ok=True)


def save_data(data: dict, name: str):
    new_name = name
    i = 2
    while True:
        new_json_file = data_dir / f"{new_name}.json"
        if new_json_file.exists():
            new_name = f"{name}_{i}"
            i += 1
        else:
            break
    
    json_file = (data_dir / new_name).with_suffix(".json")
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)
    
    print("Saved colormap data as", new_name)


def load_data(filename: str) -> dict:
    """
    Load data from the internal package folder first.
    If not found, try the custom app data folder.
    """
    filename = Path(filename).with_suffix(".json")  # Ensure the file has a .json suffix

    # Try loading from the internal package data folder
    try:
        with resources.open_text(lab_control_points, filename.name) as f:
            return json.load(f)
    except (FileNotFoundError, ModuleNotFoundError):
        pass  # File not found internally, fallback to the custom app folder

    # Try loading from the custom app folder
    custom_path = data_dir / filename
    if custom_path.exists():
        with open(custom_path, "r") as f:
            return json.load(f)

    # If not found in either location, raise an exception
    raise FileNotFoundError(f"{filename} not found in internal or app data folders.")


def get_test_img_path() -> Path:
    """
    Return the path to the 'test_images' folder inside the package.
    """
    folder_path = resources.files(test_images)
    return Path(folder_path)


def list_cmaps(print_console: bool = False) -> List[str]:
    """
    Print the list of available colormap files from both the internal package folder
    and the local app data folder.
    """

    output = "----- Available colormaps -----\n"

    # List internal data files
    output += "\nAlgorithmic colormaps:\n  - ectotherm / cold_blooded\n  - ectotherm_l / cold_blooded_l\n"
    output += "\nInternal colormaps:\n"
    cmap_names = ["ectotherm", "ectotherm_l"]

    try:
        internal_files = list(resources.contents(lab_control_points))
        json_internal_files = [file for file in internal_files if file.endswith(".json")]
        if json_internal_files:
            for file in json_internal_files:
                output += f"  - {file}\n"
                cmap_names.append(file.split(".json")[0])
        else:
            output += "  (No JSON files found in the internal data folder.)\n"
    except Exception as e:
        output += f"  (Error reading internal data files: {e})\n"

    # List local data files
    output += "\nLocal colormaps:\n"
    local_files = list(data_dir.glob("*.json"))
    if local_files:
        for file in local_files:
            output += f"  - {file.name}\n"
            cmap_names.append(file.stem)
    else:
        output += "  (No JSON files found in the local app data folder.)\n"

    if print_console:
        print(output)
    
    return cmap_names


if __name__ == "__main__":
    list_cmaps(True)
