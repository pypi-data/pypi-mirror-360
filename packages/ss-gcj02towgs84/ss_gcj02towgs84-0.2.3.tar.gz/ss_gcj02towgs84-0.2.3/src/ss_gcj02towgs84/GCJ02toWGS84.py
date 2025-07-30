'''
Author: WQ
Date: 2025-07-02 15:24:00
LastEditTime: 2025-07-02 15:51:23
LastEditors: WQ
Description: 
FilePath: \mcp_server\GCJ02toWGS84.py
'''

#mymcp.py
from mcp.server.fastmcp import FastMCP
import math

mcp = FastMCP("StatelessServer", stateless_http=True, port=8000)
 
@mcp.tool()
def GCJ02toWGS84(lng: float, lat: float) -> dict:
    """
        GCJ02 转换为 WGS84
        :param lng: 经度
        :param lat: 纬度
        :return: 转换后的经纬度
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
        return [lng, lat]
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
        # 这里的经纬度是WGS84坐标系的
        print(f"mglng: {lng * 2 - mglng}, mglat: {lat * 2 - mglat}")
        return [lng * 2 - mglng, lat * 2 - mglat]
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport='stdio')

