from uuid import uuid4
import random
import platform
import re



token = "ersrsDcnSmeDyGflUeMnwN:APA91bHneFTyD2RLqLK-JU1kUXQM9q0xJAFkGetsnfEFyI0Nn-fbRWxee9oWTn8SKFjUMqBhIVcjsLMr47c3y0Q2HXZUae9fWwHWG2tUR4LoMnOGhg2yQMQ"


def DeviceType() -> str:
	os = "Android"
	brands = ["INFINIX", "TECNO", "SAMSUNG", "XIAOMI", "REALME"]
	models = ["Infinix X6871 15", "Tecno KG5n", "Samsung A32", "Redmi Note 10", "Realme C55"]
	versions = ["VANILLA_ICE_CREAM", "RED_BEAN", "OXYGEN_OS", "MIUI14", "REALME_UI"]
	frameworks = ["HMS", "GMS", "FIREBASE"]
	appVersions = ["4.2.5:90000256", "4.2.5:10000111", "4.2.5:80000888"]
	DeviceType = f"[{os}][{random.choice(brands)}][{random.choice(models)}][{random.choice(versions)}][{random.choice(frameworks)}][{random.choice(appVersions)}]"
	return DeviceType


def GeneratorDeviceId(Type="App"):
	if Type=="App":
		return str(uuid4())
	else:
		return uuid4().hex


def ExractPID(response):
	pid = re.search(r'PID=([a-f0-9\-]+)', response)
	return pid.group(1)

def GetApiKey():
	return "1ccbc4c913bc4ce785a0a2de444aa0d6"
def VersionPlatform():
	return platform.release()

def UserAgent():
	return "okhttp/5.0.0-alpha.2"
