
from .helpers import *



AppVersion = "4.2.5"


class Headers:
	def __init__(self, data = None, access_token: str = None, DeviceId: str = None):
		AppHeaders = {
		"X-ODP-API-KEY": GetApiKey(),
		"DeviceID": DeviceId,
		"X-OS-Version": "15",
		"X-ODP-APP-VERSION": AppVersion,
		"X-Device-Type":"[Android][INFINIX][Infinix X6871 15][VANILLA_ICE_CREAM][HMS][4.2.5:90000256]",
		"X-FROM-APP": "odp",
		"X-ODP-CHANNEL": "mobile",
		"X-SCREEN-TYPE": "MOBILE",
		"Content-Type": "application/json; charset=UTF-8",
		"Host": "odpapp.asiacell.com",
		"Connection": "Keep-Alive",
		"Accept-Encoding": "gzip",
		"User-Agent": UserAgent()
		}
		if access_token:
			AppHeaders["Authorization"] = f"Bearer {access_token}"
		if data:
			AppHeaders["Content-Length"] = str(len(data))
		
		self.headers = AppHeaders
