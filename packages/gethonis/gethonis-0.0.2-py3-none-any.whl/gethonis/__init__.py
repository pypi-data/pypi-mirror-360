import codecs
import requests
from random import randint

class Gethonis:
	token: str
	type: str
	auth = False
	dataMessages: dict
	dataPosts = {
		"headers": "",
		"type": "",
		"prompt": [
			{"role": "system", "content": "You are a helpful assistant"}
		],
	}
	model: str
	stream: bool
	base_url: str

	def __init__(self, token, base_url):
		test = {"token": token}
		self.base_url = base_url
		rs = requests.post(f"{base_url}/api/authorisation", json=test)
		resp = rs.json()
		print(resp['Status'])
		if resp['Status'] == "Positive":
			self.auth = True
		else: 
			self.auth = False

		if self.auth == True:
			self.token = token

	def set_message(self, model, stream):
		self.model = model
		self.stream = stream
		self.dataMessages = {
			"headers": self.token,
			"messages": [
				{"role": "system", "content": "You are a helpful assistant"}
		    ],
		    "stream": stream
		}

	def set_post(self, type):
		self.type = type
		self.dataPosts = {
			"headers": self.token,
			"type": "type",
			"prompt": [
				{"role": "system", "content": "You are a helpful assistant"}
			],
		}

	def get_message(self, message):
		if self.stream:
			self.dataMessages["messages"].append({"role": "user", "content": message})
			decoder = codecs.getincrementaldecoder('utf-8')()
			response = requests.post(f"{self.base_url}/api/{self.model}", json=self.dataMessages, stream=True)
			return response
		self.dataMessages["messages"].append({"role": "user", "content": message})
		response = requests.post(f"{self.base_url}/api/{self.model}", json=self.dataMessages)
		rs = response.json()
		return rs[0]

	def get_post(self, prompt):
		self.dataPosts["prompt"].append({"role": "user", "content": prompt})
		response = requests.post(f"{self.base_url}/api/post", json=self.dataPosts)
		rs = response.json()
		return rs