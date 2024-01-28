from .lora_info import LoraInfo
from .image_from_url import ImageFromURL

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LoraInfo": LoraInfo,
    "ImageFromURL": ImageFromURL
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraInfo": "Lora Info",
    "ImageFromURL": "Image From URL"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]