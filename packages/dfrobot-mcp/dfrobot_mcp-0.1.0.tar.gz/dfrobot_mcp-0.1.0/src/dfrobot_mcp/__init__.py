from mcp.server.fastmcp import FastMCP
import requests
import json
import re
from typing import List

# 创建MCP服务器
mcp = FastMCP("DFRobotProductSearch")

# 提取产品ID或名称的关键词
def extract_keyword(text: str) -> str:
    """从用户查询中提取商品关键词"""
    # 尝试匹配产品ID (如DFR0100)
    product_id = re.search(r'dfr\d{4}', text, re.IGNORECASE)
    if product_id:
        return product_id.group().lower()
    
    # 尝试提取产品名称关键词
    keywords = re.findall(r'\b\w{3,}\b', text)
    if keywords:
        return max(keywords, key=len)
    
    return 'dfr0100'  # 默认关键词

# 优化产品URL格式
def format_product_url(goods_id: str) -> str:
    """创建友好的产品详情链接"""
    return f"https://www.dfrobot.com.cn/goods-{goods_id}.html"

# 新添加的DFRobot商品搜索工具
@mcp.tool()
def search(query: str) -> str:
    """
    根据查询文本自动提取关键词搜索DFRobot商品
    例如: "搜索DFR0100" -> 提取关键词"dfr0100"
    """
    keyword = extract_keyword(query)
    url = f"https://www.dfrobot.com.cn/app/route.php?r=goods.search&keywords={keyword}"
    
    try:
        # 发送HTTP请求
        response = requests.get(url)
        response.raise_for_status()
        
        # 解析JSON数据
        data = response.json()
        
        # 验证响应结构
        if data.get("error") != 0:
            return f"搜索失败: API返回错误代码 {data.get('error')}"
            
        products: List[dict] = data.get("list", [])
        
        if not products:
            return f"没有找到匹配关键词 '{keyword}' 的商品"
        
        # 构建格式化的商品信息
        result = [f"DFRobot商品搜索结果 (关键词: {keyword}):"]
        for i, product in enumerate(products, 1):
            product_url = format_product_url(product['goods_id'])
            
            result.append(
                f"{i}. 【{product['goods_name']}】\n"
                f"   价格: {product['shop_price']}\n"
                f"   库存: {'现货' if product['is_online'] == '1' else '缺货'}\n"
                f"   sku: {product['goods_sn']}\n"
                f"   链接: {product_url}\n"
                f"   图片: {product['goods_thumb']}"
            )
        
        return "\n\n".join(result)
        
    except requests.exceptions.RequestException as e:
        return f"网络请求失败: {str(e)}"
    except json.JSONDecodeError:
        return "API返回了无效的JSON数据"
    except Exception as e:
        return f"处理请求时出错: {str(e)}"

# 添加一个动态问候资源
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """获取个性化问候语"""
    return f"你好, {name}!"

    
def main() -> None:
    mcp.run(transport="stdio")
