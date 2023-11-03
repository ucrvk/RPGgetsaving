from json import dump, load
from filehandle import dafaultDirectory
from typing import Union

defaultJson = {
    "user": {"token": "", "id": ""},
    "gameDirectory": {
        "saving": dafaultDirectory[0],
        "game": dafaultDirectory[1],
    },
}


def settingLoad() -> Union[dict, Exception]:
    """
    Loads the settings.json file and returns a dictionary
    """
    try:
        with open("settings.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        with open("settings.json", "w") as f:
            dump(defaultJson, f, indent=4)
        return defaultJson
    except Exception as e:
        return e


def settingSave(settings: dict) -> Union[bool, Exception]:
    """
    Saves the settings.json file
    """
    try:
        with open("settings.json", "w") as f:
            dump(settings, f, indent=4)
        return True
    except Exception as e:
        return e
    
def emptyDirectoryDectec(dectetJson:dict)->bool:
    """
    Checks if the directory is empty
    """
    if dectetJson["gameDirectory"]["saving"] == "" or dectetJson["gameDirectory"]["game"] == "":
        return True
    else:
        return False

