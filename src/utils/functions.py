from io import BytesIO
from PIL import Image
import configparser
import base64
import yaml

def getConfig(configFilePath: str) -> configparser.ConfigParser:
    """
    Get the config from the config file
    Args:
        configFilePath: path to the config file
    Returns:
        config: config parser object
    """
    config = configparser.ConfigParser()
    config.read(configFilePath)
    return config

def convertImageToBase64(image: Image.Image) -> str:
    """
    Convert an image to a base64 string
    Args:
        image: image object
    Returns:
        imageString: base64 uri of the image
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG", optimize=True, quality=85)
    imageBytes = buffered.getvalue()
    imageBase64 = base64.b64encode(imageBytes).decode("utf-8")
    dataUri = f"data:image/jpeg;base64,{imageBase64}"
    return dataUri

def getYaml(yamlFilePath: str) -> dict:
    """
    Get the yaml from the yaml file
    Args:
        yamlFilePath: path to the yaml file
    Returns:
        yamlData: yaml data
    """
    with open(yamlFilePath, "r") as file:
        yamlData = yaml.safe_load(file)
    return yamlData