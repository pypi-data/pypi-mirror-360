from mcp.server.fastmcp import FastMCP
import os
import pandas as pd
from typing import List, Dict, Any

# 1. 创建MCP服务器实例（修改名称为更贴合需求的标识）
mcp = FastMCP("StudentErrorQueryServer")


# 2. 新增：根据学生姓名查询错题信息的工具（核心功能）
@mcp.tool()
def get_student_errors(name: str) -> List[Dict[str, Any]]:
    """
    根据学生姓名从Excel表格中获取其错题详情（支持大模型调用）。
    
    参数说明:
        name (str): 学生姓名（需与表格中的“学生姓名”字段完全匹配）
    
    返回结果:
        List[Dict[str, Any]]: 该学生的所有错题记录，每个元素包含以下字段：
            - 题目内容: 错题的完整题目
            - 知识点: 错题对应的生物知识点（如“细胞呼吸-有氧呼吸”）
            - 题目类型: 题目类型（如“选择题”“简答题”）
            - 错误原因: 学生错误的根源（如“概念混淆”“计算错误”）
            - 难度等级: 题目难度（如“易”“中”“难”）
            - 正确答案: 题目的标准正确答案
            - 学生答案: 学生实际填写的错误答案
    
    异常处理:
        - 文件不存在: 返回明确的路径错误提示
        - 学生未找到: 返回“未找到该学生信息”的提示
        - 表格读取失败: 返回读取错误原因
    """
    # 2.1 定义表格文件路径（与main.py同目录下的StudentErrorQuestion/Table.xlsx）
    #table_dir = os.path.join(os.path.dirname(__file__), "StudentErrorQuestion")
    #table_path = os.path.join(table_dir, "Table.xlsx")
    table_path = r"C:\StudentErrorQuestion\Table.xlsx"  # 直接写死完整路径

    # 2.2 检查表格文件是否存在
    if not os.path.exists(table_path):
        raise FileNotFoundError(
            f"错误：未找到错题表格文件，请检查路径是否正确。路径：{table_path}"
        )
    
    # 2.3 读取Excel表格数据（使用openpyxl引擎处理.xlsx文件）
    try:
        df = pd.read_excel(table_path, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"错误：读取表格失败，原因：{str(e)}")
    
    # 2.4 筛选指定学生的错题记录（精确匹配姓名）
    student_errors = df[df["学生姓名"].str.strip() == name.strip()]  # 去除首尾空格，避免输入误差
    
    # 2.5 检查是否有匹配的学生记录
    if student_errors.empty:
        raise ValueError(f"错误：未找到姓名为「{name}」的学生错题信息，请确认姓名是否正确。")
    
    # 2.6 转换为字典列表（保留需要的字段，排除无关字段如“错题ID”）
    result = student_errors[
        [
            "题目内容",
            "知识点",
            "题目类型",
            "错误原因",
            "难度等级",
            "正确答案",
            "学生答案",
        ]
    ].to_dict(orient="records")  # orient="records"表示按行转换为字典列表
    
    # 2.7 返回结构化结果（大模型可直接解析）
    return result


# # 3. 保留原有的工具/资源（可选，可根据需求删除）
# @mcp.tool()
# def sum(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# 4. 运行MCP服务器（使用stdio协议，与原模板一致）

def main() -> None:
    mcp.run(transport="stdio")
