# '''
# Author: WQ
# Date: 2025-07-03 14:17:56
# LastEditTime: 2025-07-03 14:41:17
# LastEditors: WQ
# Description: 
# FilePath: \SS_GCJ02toWGS84\src\ss_gcj02towgs84\server.py
# '''
# '''
# Author: WQ
# Date: 2025-07-02 16:22:15
# LastEditTime: 2025-07-02 17:51:44
# LastEditors: WQ
# Description: 
# FilePath: \mcp_server\mcpServer\server.py
# '''
from fastmcp import FastMCP
import math
import requests
# 初始化mcp服务
mcp = FastMCP(name='GCJ02 转换为 WGS84')

# @mcp.tool()
async def GCJ02toWGS84(lng: float, lat: float) -> dict:
    """
        GCJ02 转换为 WGS84
        :param lng: 经度
        :param lat: 纬度
        :return: 转换后的经纬度，格式为 {"longitude": float, "latitude": float}
    """

    # 定义一些常量
    PI = 3.1415926535897932384626
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 扁率

    def transformlat(lng, lat):
        lat = float(lat)
        lng = float(lng)
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
        return ret
    
    def transformlng(lng, lat):
        lat = float(lat)
        lng = float(lng)
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
        return ret
    
    def out_of_china(lng, lat):
        """
        判断是否在国内，不在国内则不做偏移
        :param lng: 经度
        :param lat: 纬度
        :return: 是否在国内
        """
        lat = float(lat)
        lng = float(lng)
        # 纬度3.86~53.55, 经度73.66~135.05
        return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)
        
    if out_of_china(lng, lat):
        return {"longitude": lng, "latitude": lat}
    else:
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * PI
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
        mglat = lat + dlat
        mglng = lng + dlng
        # 返回转换后的经纬度
        print(f"mglng: {lng * 2 - mglng}, mglat: {lat * 2 - mglat}")
        return {"longitude": lng * 2 - mglng, "latitude": lat * 2 - mglat}

@mcp.tool()
def getPOIposition(keywords: str, city: str) -> dict:
    """
        获取 位置、地点、名称、地址等信息
        :param keywords: 名称或地址
        :param city: 城市名称
        :return: POI 的经纬度，格式为 {"longitude": float, "latitude": float}
    """
    if not keywords or not city:
        return {"longitude": 0, "latitude": 0}

    # 目标 URL
    url = 'https://restapi.amap.com/v3/place/text'
    # 查询参数
    params = {
        'key': '58e1e50b1e55a0915da5eeb6dbc26714',
        'keywords': keywords,
        'city': city,
        'offset': 1,
    }
    # 发送 GET 请求
    response = requests.get(url, params=params)
    data = None
    # 检查响应状态码
    if response.status_code == 200:
        # 请求成功，获取响应内容（假设是 JSON 格式）
        data = response.json()
        # print(data)
    else:
        print(f"请求失败，状态码: {response.status_code}")

    # 这里可以调用实际的 POI 服务来获取经纬度
    if data and 'pois' in data and len(data['pois']) > 0:
        poi = data['pois'][0]
        print(f"名称: {poi['name']}, 坐标: {poi['location']}")
        print(f"经度: {poi['location'].split(',')[0]}, 纬度: {poi['location'].split(',')[1]}")
        return GCJ02toWGS84(float(poi['location'].split(',')[0]), float(poi['location'].split(',')[1]))
    else:
        print("未找到相关 POI 信息")
        return {"longitude": 0, "latitude": 0}
    # 目前仅返回一个示例值
    # return {"longitude": 116.404, "latitude": 39.915}
def run():
    # 启动 MCP 服务
    import asyncio
    asyncio.run(mcp.run(transport="stdio"))

if __name__ == "__main__":
    run()