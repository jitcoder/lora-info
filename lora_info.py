import folder_paths
import hashlib
import requests
import json
import server
from aiohttp import web
import os


db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.json')

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
        return {}
    
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def get_lora_info(lora_name):
    db = load_json_from_file(db_path)
    output = None
    examplePrompt = None
    trainedWords = None
    baseModel = None

    loraInfo = db.get(lora_name, {})

    if isinstance(loraInfo, str):
        loraInfo = {}
    
    output = loraInfo.get('output', None)
    examplePrompt = loraInfo.get('examplePrompt', None)
    trainedWords = loraInfo.get('trainedWords', None)
    baseModel = loraInfo.get('baseModel', None)

    if output is None or baseModel is None:
        output = ""
        lora_path = folder_paths.get_full_path("loras", lora_name)
        LORAsha256 = calculate_sha256(lora_path)
        model_info = get_model_version_info(LORAsha256)
        if model_info.get("trainedWords", None) is None:
            trainedWords = ""
        else:
            trainedWords = ",".join(model_info.get("trainedWords"))
        baseModel = model_info.get("baseModel", "")
        images = model_info.get('images')
        examplePrompt = None

        if trainedWords:
            output += "Triggers: " + trainedWords
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
                        if examplePrompt is None and key == "prompt":
                            examplePrompt = value
                        output += f"{key}: {value}\n"
                output += '\n'

        db[lora_name] = {
            "output": output,
            "trainedWords": trainedWords,
            "examplePrompt": examplePrompt,
            "baseModel": baseModel
            }
        save_dict_to_json(db, db_path)
    
    return (output, trainedWords, examplePrompt, baseModel)

LORA_LIST = sorted(folder_paths.get_filename_list("loras"), key=str.lower)

@server.PromptServer.instance.routes.post('/lora_info')
async def fetch_lora_info(request):
    post = await request.post()
    lora_name = post.get("lora_name")
    (output, triggerWords, examplePrompt, baseModel) = get_lora_info(lora_name)

    return web.json_response({"output": output, "triggerWords": triggerWords, "examplePrompt": examplePrompt, "baseModel": baseModel})

class LoraInfo:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lora_name": (LORA_LIST, )
            },
        }

    RETURN_NAMES = ("trigger_words", "example_prompt")
    RETURN_TYPES = ("STRING", "STRING")
    FUNCTION = "lora_info"
    OUTPUT_NODE = True
    CATEGORY = "jitcoder"

    def lora_info(self, lora_name):
        (output, triggerWords, examplePrompt, baseModel) = get_lora_info(lora_name)
        return {"ui": {"text": (output,), "model": (baseModel,)}, "result": (triggerWords, examplePrompt)}


