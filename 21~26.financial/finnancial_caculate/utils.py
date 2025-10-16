import pandas as pd
import os

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

def get_financial_statements_file_map():
    """
    遍历项目根目录下financial_statements目录下所有csv文件，
    返回形如 {股票代码: {年份: [文件路径列表]}} 的两层嵌套字典。
    支持同一只股票同一年份的多个文件类型，将文件路径存储在列表中。
    """
    file_map = {}
    # 获取当前文件的绝对路径，再定位到项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    statements_dir = os.path.join(project_root, "data","financial_statements")
    if not os.path.exists(statements_dir):
        return file_map
    
    for filename in os.listdir(statements_dir):
        if filename.endswith(".csv"):
            # 文件名格式：股票代码_年份_文件类型.csv
            parts = filename.split("_")
            if len(parts) < 3:
                continue  # 文件名格式不符，跳过
            
            code = parts[0]  # 股票代码
            year = parts[1]  # 年份
            
            abs_path = os.path.abspath(os.path.join(statements_dir, filename))
            
            # 初始化嵌套字典结构
            if code not in file_map:
                file_map[code] = {}
            if year not in file_map[code]:
                file_map[code][year] = []
            
            file_map[code][year].append(abs_path)
    
    return file_map

def save_dataframe_to_csv_file(df, filename: str):
    """
    将DataFrame保存到项目根目录下data/finalcial_caculates目录下的指定csv文件中。
    :param df: 要保存的pandas DataFrame对象
    :param filename: 文件名（应以.csv结尾）
    """

    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = os.path.dirname(current_dir)
    report_dir = os.path.join(project_root, "data", "financial_caculates")
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    #print(get_financial_statements_file_map())
    save_dataframe_to_csv_file(pd.DataFrame([{"a": 1, "b": 2}]), "test.csv")