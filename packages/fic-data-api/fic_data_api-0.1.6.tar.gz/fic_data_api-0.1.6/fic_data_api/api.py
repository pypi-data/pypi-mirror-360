"""
 * @Author：cyg
 * @Package：api
 * @Project：Default (Template) Project
 * @name：api
 * @Date：2025/5/8 09:52
 * @Filename：api
"""

import requests


class FicDataApi:
	def __init__(self, token):
		self.api_url = "http://10.8.23.90:5001"
		self.token = token
	
	def get_data(self, dataName, where="", columns="", page=1):
		"""
		
		:param dataName: 接口get_data_info中的name
		:param where: 查询条件
		:param columns: 需要查询的字段,默认为所有,多个有,隔开如:trade_date,ts_code
		:param page :分页如果是最后一页将返回空数据
		:return:[]
		"""
		if not self.token:
			raise ValueError("Token has not been set")
		
		url = f"{self.api_url}/fic_data/get_data"
		headers = {"token": f"{self.token}"}
		params = {
			"dataName": dataName,
			"where": where,
			"columns": columns,
			"page": page
		}
		response = requests.get(url, headers=headers, params=params)
		
		if response.status_code == 200:
			data = response.json()
			return data["data"]
		else:
			print(f"Failed : {response.status_code}")
			return None
	
	def get_data_info(self):
		"""
		获取所有数据信息
		:return:[
			{
				"desc":["数据表数据说明"],
				"columns":[{"columns_info":"表字段说明","columns_name":"字段名字"}],
				"name":"数据名字"
			}
			]
		"""
		url = f"{self.api_url}/fic_data/data_info"
		headers = {"token": f"{self.token}"}
		response = requests.get(url, headers=headers)
		
		if response.status_code == 200:
			data = response.json()
			return data["data"]
		else:
			print(f"Failed : {response.status_code}")
			return None
