import folder_paths
import hashlib
import requests
import json

def load_json_from_file(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return {}

def save_dict_to_json(data_dict, file_path):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
            print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON to file: {e}")

def get_model_version_info(hash_value):
    api_url = f"https://civitai.com/api/v1/model-versions/by-hash/{hash_value}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

class LoraInfo:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        LORA_LIST = sorted(folder_paths.get_filename_list("loras"), key=str.lower)

        return {
            "required": {
                "lora_name": (LORA_LIST, )
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "lora_info"
    OUTPUT_NODE = True
    CATEGORY = "jitcoder"

    def lora_info(self, lora_name):
        lora_tags = load_json_from_file('./custom_nodes/lora-info/db.json')
        output = lora_tags.get(lora_name, None) if lora_tags is not None else None

        if output is None:
            output = ""
            lora_path = folder_paths.get_full_path("loras", lora_name)
            LORAsha256 = calculate_sha256(lora_path)
            model_info = get_model_version_info(LORAsha256)
            trainedWords = model_info.get("trainedWords")
            baseModel = model_info.get("baseModel")
            images = model_info.get('images')

            if trainedWords:
                output += "Triggers: " + ",".join(trainedWords)
                output += "\n"
            
            if baseModel:
                output += f"Base Model: {baseModel}\n"
            if images:
                output += "\nExamples:\n"
                for image in images:
                    output += f"\nOutput: {image.get('url')}\n"
                    meta = image.get("meta")
                    if meta:
                        for key, value in meta.items():
                            output += f"{key}: {value}\n"
                    output += '\n'
            lora_tags[lora_name] = output
            save_dict_to_json(lora_tags, './custom_nodes/lora-info/db.json')
        return {"ui": {"text": (output,)}}


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LoraInfo": LoraInfo
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraInfo": "Lora Info"
}

WEB_DIRECTORY = "./js"