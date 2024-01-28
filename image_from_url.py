from PIL import Image, ImageOps
import requests
import torch
import numpy

class ImageFromURL:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {"multiline": False})
            },
        }

    RETURN_NAMES = ("image",)
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "fetch_image"
    OUTPUT_NODE = True
    CATEGORY = "jitcoder"

    def fetch_image(self, url):
        image = Image.open(requests.get(url, stream=True).raw)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = numpy.array(image).astype(numpy.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        return (image,)
