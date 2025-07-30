import json
import traceback
from datetime import datetime

import requests

from solax_py_library.utils.time_util import trans_str_time_to_index


class CloudClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_token(self, ems_sn, sn_secret):
        token_url = self.base_url + "/device/token/getByRegistrationSn"
        try:
            response = requests.post(
                token_url,
                json={
                    "registrationSn": ems_sn,
                    "snSecret": sn_secret,
                },
                timeout=5,
            )
            if response.content:
                response_data = json.loads(response.content)
                print(f"获取token结果 {response_data}")
                if response_data.get("code") == 0 and response_data.get("result"):
                    token = response_data["result"]
                    return token
        except Exception as e:
            print(f"访问token接口失败: {str(e)}")

    def get_weather_data_from_cloud(self, ems_sn, token):
        """获取未来24小时天气数据"""
        try:
            weather_url = self.base_url + "/ess/web/v1/powerStation/station/solcast/get"
            headers = {"token": token, "Content-Type": "application/json"}
            post_dict = {"registerNo": ems_sn, "day": 1}
            response = requests.post(
                url=weather_url, data=json.dumps(post_dict), headers=headers, timeout=5
            )
            # 访问失败或获取数据失败，则重复插入最后一条数据
            if response.status_code != 200:
                print(f"获取天气数据失败 状态码 {response.status_code}")
                return False
            response_data = response.json()
            if response_data.get("result") is None:
                print(f"获取天气数据失败 返回数据 {response_data}")
                return False
            weather_info = {
                "timeList": [],
                "irradiance": {"valueList": []},
                "temperature": {"valueList": []},
                "humidity": {"valueList": []},
                "wind": {"valueList": []},
                "barometricPressure": {"valueList": []},
                "rain": {"valueList": []},
            }
            for info in response_data["result"]:
                weather_info["timeList"].append(info["localTime"])
                weather_info["irradiance"]["valueList"].append(float(info["ghi"]))
                weather_info["temperature"]["valueList"].append(float(info["air_temp"]))
                weather_info["humidity"]["valueList"].append(
                    float(info["relative_humidity"])
                )
                weather_info["wind"]["valueList"].append(float(info["wind_speed_10m"]))
                weather_info["barometricPressure"]["valueList"].append(
                    float(info.get("surface_pressure", 0))
                )
                rain = 1 if float(info["precipitation_rate"]) > 2.5 else 0
                weather_info["rain"]["valueList"].append(rain)
            data_length = len(weather_info["irradiance"]["valueList"])
            if weather_info["timeList"] == []:
                weather_info = {}
            else:
                weather_info["irradiance"]["maxValue"] = max(
                    weather_info["irradiance"]["valueList"]
                )
                weather_info["irradiance"]["avgValue"] = round(
                    sum(weather_info["irradiance"]["valueList"]) / data_length, 3
                )
                weather_info["irradiance"]["minValue"] = min(
                    weather_info["irradiance"]["valueList"]
                )

                weather_info["temperature"]["maxValue"] = max(
                    weather_info["temperature"]["valueList"]
                )
                weather_info["temperature"]["avgValue"] = round(
                    sum(weather_info["temperature"]["valueList"]) / data_length, 3
                )
                weather_info["temperature"]["minValue"] = min(
                    weather_info["temperature"]["valueList"]
                )

                weather_info["humidity"]["maxValue"] = max(
                    weather_info["humidity"]["valueList"]
                )
                weather_info["humidity"]["avgValue"] = round(
                    sum(weather_info["humidity"]["valueList"]) / data_length, 3
                )
                weather_info["humidity"]["minValue"] = min(
                    weather_info["humidity"]["valueList"]
                )

                weather_info["wind"]["maxValue"] = max(
                    weather_info["wind"]["valueList"]
                )
                weather_info["wind"]["avgValue"] = round(
                    sum(weather_info["wind"]["valueList"]) / data_length, 3
                )
                weather_info["wind"]["minValue"] = min(
                    weather_info["wind"]["valueList"]
                )

                weather_info["barometricPressure"]["maxValue"] = max(
                    weather_info["barometricPressure"]["valueList"]
                )
                weather_info["barometricPressure"]["avgValue"] = round(
                    sum(weather_info["barometricPressure"]["valueList"]) / data_length,
                    3,
                )
                weather_info["barometricPressure"]["minValue"] = min(
                    weather_info["barometricPressure"]["valueList"]
                )

                weather_info["rain"]["maxValue"] = max(
                    weather_info["rain"]["valueList"]
                )
                weather_info["rain"]["minValue"] = min(
                    weather_info["rain"]["valueList"]
                )
            return weather_info
            print("获取天气数据成功")
        except Exception:
            print(f"获取天气数据失败 异常 {traceback.format_exc()}")
            return False

    def get_electrovalence_data_from_cloud(self, ems_sn, token):
        try:
            price_url = self.base_url + "/powerStation/station/getCurrentElectrovalence"
            response = requests.post(
                url=price_url,
                headers={"token": token, "Content-Type": "application/json"},
                json={"registerNo": ems_sn},
                timeout=5,
            )
            # 访问失败或获取数据失败，则重复插入最后一条数据
            if response.status_code != 200:
                print(f"获取电价数据失败 状态码 {response.status_code}")
                return False
            response_data = response.json()
            if response_data.get("result") is None:
                print(f"获取电价数据失败 返回数据 {response_data}")
                return False
            today = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            ele_price_info = {
                "buy": [None] * 192,
                "sell": [None] * 192,
                "date": today,
            }
            ele_price_info["ele_unit"] = response_data["result"]["unit"]
            if ele_price_info["ele_unit"] == "¥":
                rate = 1
                ele_price_info["ele_unit"] = "¥/kWh"
            else:
                rate = 100
                ele_price_info["ele_unit"] = "Cents €/kWh"
            for detail_info in response_data["result"]["list"]:
                start_index = trans_str_time_to_index(detail_info["startTime"])
                end_index = trans_str_time_to_index(detail_info["endTime"])
                # 处理欧分的情况
                if detail_info["buyPrice"] is not None:
                    buy_price = round(detail_info["buyPrice"] * rate, 5)
                else:
                    buy_price = detail_info["buyPrice"]
                if detail_info["salePrice"] is not None:
                    sale_price = round(detail_info["salePrice"] * rate, 5)
                else:
                    sale_price = detail_info["salePrice"]
                ele_price_info["buy"][start_index:end_index] = [buy_price] * (
                    end_index - start_index
                )
                ele_price_info["sell"][start_index:end_index] = [sale_price] * (
                    end_index - start_index
                )
            if response_data["result"].get("tomorrow") is not None:
                for detail_info in response_data["result"]["tomorrow"]:
                    start_index = trans_str_time_to_index(detail_info["startTime"]) + 96
                    end_index = trans_str_time_to_index(detail_info["endTime"]) + 96
                    if detail_info["buyPrice"] is not None:
                        buy_price = round(detail_info["buyPrice"] * rate, 5)
                    else:
                        buy_price = detail_info["buyPrice"]
                    if detail_info["salePrice"] is not None:
                        sale_price = round(detail_info["salePrice"] * rate, 5)
                    else:
                        sale_price = detail_info["salePrice"]
                    ele_price_info["buy"][start_index:end_index] = [buy_price] * (
                        end_index - start_index
                    )
                    ele_price_info["sell"][start_index:end_index] = [sale_price] * (
                        end_index - start_index
                    )
            print("获取电价数据成功")
            return ele_price_info
        except Exception:
            print(f"获取电价数据失败 异常 {traceback.format_exc()}")
            return False
