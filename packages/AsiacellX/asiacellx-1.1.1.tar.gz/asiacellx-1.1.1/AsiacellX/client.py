import requests
import json
import re
from .utils.headers import *
from .utils.helpers import ExractPID, token


class Client:
	def __init__(self, PhoneNumber: str, language: str = "ar"):
		self.api = "https://odpapp.asiacell.com/api/"
		self.PhoneNumber = PhoneNumber
		self.DeviceId = GeneratorDeviceId("App")
		self.token = token
		self.access_token = None
		self.lang = language
		self.handshake_token = None
		self.userId = None
		self.refresh_token = None
     
	def headers(self, data: str = None):
		return Headers(data,self.access_token,self.DeviceId).headers

	def GetCapatcha(self):
		response = requests.post(url=f"{self.api}captcha?lang={self.lang}", headers=self.headers())
		return response.json()

	def login(self, CapatchaCode: str = None):
		data = json.dumps({
		"captchaCode": CapatchaCode,
		"username": self.PhoneNumber
		})
		
		response = requests.post(url=f"{self.api}v1/login?lang={self.lang}", data=data, headers =self.headers(data)).json()
		pid = ExractPID(response["nextUrl"])
		VerificationCode = input("Enter the verification code: ")
		data = json.dumps({
		"PID": pid,
		"passcode": VerificationCode,
		"token": self.token 
		})
		response = requests.post(url=f"{self.api}v1/smsvalidation?lang={self.lang}",data = data, headers = self.headers(data)).json()
		self.access_token = response["access_token"]
		self.refresh_token = response["refresh_token"]
		self.handshake_token = response["handshake_token"]
		self.userId = response["userId"]
		return response
			

	def login_token(self, access_token: str):
		"""login with Access Token AsiaCell"""
		self.access_token = access_token

	def get_info_profile(self):
		headers=self.headers()
		print(headers)
		response = requests.get(url=f"{self.api}v1/profile/view?lang={self.lang}", headers=headers)
		return response.text

	def recharge(self, PhoneNumber: str = "", voucherNumber: str = None, rechargeType: int = 1):
		"""
		Recharge mobile balance or internet using a voucher number.
		Args:
			voucherNumber (str): The voucher/card number to be used for recharge .
			rechargeType (int, optional):
				1 for normal balance recharge,
				2 for internet recharge. Defaults to 1.
		"""
		
		data = json.dumps({
		"msisdn": PhoneNumber,
		"rechargeType": rechargeType,
		"voucher": voucherNumber
		})
		response = requests.post(url=f"{self.api}v1/top-up?lang={self.lang}", data = data, headers = self.headers(data))
		return response.json()
	
	def check_spinwheel(self):
		response = requests.post(url=f"{self.api}v2/spinwheel/check?lang={self.lang}", headers = self.headers())
		return response.json()

	def confirm_spinwheel(self):
		"""Free data received"""
		response = requests.post(url=f"{self.api}v2/spinwheel/confirm?lang={self.lang}", headers = self.headers())
		return response.json()

	def get_info_spinwheel(self):
		"""desc"""
		response = requests.get(url=f"{self.api}v2/spinwheel/ui?lang={self.lang}", headers = self.headers())
		return response.json()