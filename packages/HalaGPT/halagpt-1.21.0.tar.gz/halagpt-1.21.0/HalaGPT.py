import requests
from user_agent import generate_user_agent
from hashlib import md5
import random
from bs4 import BeautifulSoup
import pycountry
import time
from datetime import datetime
from secrets import token_hex
from uuid import uuid4
from mnemonic import Mnemonic

API_HalaGPT = "http://sii3.moayman.top"

MODELS_DEEP_INFRA = [ … ]
MODELS_31 = [ … ]
MODELS_BLACKBOX = [ … ]

class VoiceAi:
    @staticmethod
    def openai(text: str) -> dict:
        resp = requests.get(f"{API_HalaGPT}/DARK/voice.php", params={"text": text})
        body = resp.text
        status = "ok" if "audio_url" in body else "Bad"
        return {"status": status, "result": body, "Dark": "@Sii_3"}

class TextAi:
    @staticmethod
    def DeepInfra(text: str, model: str) -> dict:
        try:
            resp = requests.get(f"{API_HalaGPT}/api/DeepInfra.php", params={model: text})
            res = resp.json()
            return {"status": "OK", "result": res.get("response"), "Dark": "@sii_3"} if "response" in res else {"status": "Bad", "result": res, "Dark": "@sii_3"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Dark": "@sii_3"}

def ModelDeepInfra() -> list:
    return MODELS_DEEP_INFRA

class WormGpt:
    @staticmethod
    def DarkGPT(text: str) -> dict:
        res = requests.get(f"{API_HalaGPT}/DARK/api2/darkgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response"), "Dark": "@Sii_3"}

    @staticmethod
    def Worm(text: str) -> dict:
        res = requests.get(f"{API_HalaGPT}/DARK/api/wormgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response"), "Dark": "@Sii_3"}

class Model31:
    @staticmethod
    def Modl(text: str, model: str) -> dict:
        resp = requests.get(f"{API_HalaGPT}/api/gpt.php", params={model: text})
        return resp.json()

    @staticmethod
    def ModelsAi() -> list:
        return MODELS_31

class BlackBox:
    @staticmethod
    def Models(text: str, model: str) -> dict:
        resp = requests.get(f"{API_HalaGPT}/api/black.php", params={model: text})
        data = resp.json()
        return {"status": "OK", "result": data.get("response"), "Dark": "@Sii_3"}

    @staticmethod
    def ReturnModel() -> list:
        return MODELS_BLACKBOX

class Developers:
    @staticmethod
    def Dark() -> str:
        return (
            "Name ➝ ➞ #Dark\n\n"
            "My user = @sii_3\n\n"
            "ʀᴀɴᴅᴏᴍ ǫᴜᴏᴛᴇ ➛ ➜ ➝\n"
            "    ˛ I have you, that's all I need 𓍲 ."
        )

class ImageAi:
    SUPPORTED_MODELS = [
        "fluex-pro", "flux", "schnell", "imger-12", "deepseek",
        "gemini-2-5-pro", "blackbox", "redux", "halagpt-7-i",
        "r1", "gpt-4-1"
    ]

    @staticmethod
    def generate(prompt: str, model: str = "halagpt-7-i") -> dict:
        if model not in ImageAi.SUPPORTED_MODELS:
            return {"status": "Error", "error": f"Model '{model}' not supported"}
        resp = requests.get(f"{API_HalaGPT}/api/img.php", params={model: prompt})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

class ChatAi:
    @staticmethod
    def ask(prompt: str) -> dict:
        resp = requests.get(f"{API_HalaGPT}/api/chat/gpt-3.5.php", params={"ai": prompt})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

class AzkarApi:
    @staticmethod
    def today() -> dict:
        resp = requests.get(f"{API_HalaGPT}/api/azkar.php")
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

class DeepSeekT1:
    @staticmethod
    def codeify(text: str) -> dict:
        resp = requests.get(f"{API_HalaGPT}/api/DeepSeek/DeepSeek.php", params={"text": text})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

class GeminiApi:
    @staticmethod
    def ask(prompt: str) -> dict:
        resp = requests.get(f"{API_HalaGPT}/DARK/gemini.php", params={"text": prompt})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}