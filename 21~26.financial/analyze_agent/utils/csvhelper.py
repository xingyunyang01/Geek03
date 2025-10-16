import os
import pandas as pd

def get_financial_caculates_file_map():
    """
    遍历项目根目录下financial_caculates目录下所有md文件，
    返回形如 {股票代码: 文件路径列表} 的字典。
    """
    file_map = {}
    # 获取当前文件的绝对路径，再定位到项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../.."))
    caculates_dir = os.path.join(project_root, "data", "financial_caculates")
    if not os.path.exists(caculates_dir):
        return file_map

    for filename in os.listdir(caculates_dir):
        if filename.endswith(".csv"):
            # 文件名格式：股票代码_年份_财务计算结果.md
            # 例如: 600519_2023年度财务计算结果.md
            parts = filename.split("_")
            if len(parts) < 2:
                continue  # 文件名格式不符，跳过

            code = parts[0]  # 股票代码

            abs_path = os.path.abspath(os.path.join(caculates_dir, filename))

            if code not in file_map:
                file_map[code] = []
            file_map[code].append(abs_path)

    return file_map

def read_csv(filepath:str):
    """
    读取CSV文件
    """
    # 读取CSV文件
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    return format_df(df)

def format_df(df, decimal_places=2):
    if df.empty:
        return "没有找到相关股票的数据"
    formatted_lines = []
    for _, row in df.iterrows():
        line_parts = []
        for col in df.columns:
            value = row[col]
            # 处理缺失值
            formatted_value = value if pd.notna(value)  else ''
            # 根据数据类型调整格式
            if isinstance(formatted_value, (int, float)):
                formatted_value = f"{formatted_value:.{decimal_places}f}"
            line_parts.append(f"{col}:{formatted_value}")
        # 合并当前行的字符串
        formatted_line = "\n".join(line_parts)
        formatted_lines.append(formatted_line)
    # 行间保留空行
    return "\n\n".join(formatted_lines)

def read_md_file(filepath: str) -> str:
    """
    读取指定路径的md文件，并以字符串形式返回内容。
    """
    if not os.path.exists(filepath):
        return "文件不存在"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return content

def save_string_to_md_file(content: str, filename: str):
    """
    将字符串content保存到项目根目录下data/finalcial_caculates目录下的指定md文件中。
    :param content: 要保存的字符串内容
    :param filename: 文件名（应以.md结尾）
    """

    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = os.path.dirname(current_dir)
    report_dir = os.path.join(project_root, "data", "single_analyze")
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    file_map = get_financial_caculates_file_map()
    print(file_map)
