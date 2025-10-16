import os
import re
import shutil
import requests
from urllib.parse import urlparse
import pandas as pd

def get_financial_caculates_file_map():
    """
    遍历项目根目录下financial_caculates目录下所有md文件，
    返回形如 {股票代码: 文件路径列表} 的字典。
    """
    file_map = {}
    # 获取当前文件的绝对路径，再定位到项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
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

def get_financial_statements_file_map():
    """
    遍历项目根目录下financial_statements目录下所有csv文件，
    返回形如 {股票代码: {年份: [文件路径列表]}} 的两层嵌套字典。
    支持同一只股票同一年份的多个文件类型，将文件路径存储在列表中。
    """
    file_map = {}
    # 获取当前文件的绝对路径，再定位到项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
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

def get_industry_info_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
    statements_dir = os.path.join(project_root, "data","report")

    md_file_path = os.path.join(statements_dir, "竞争对手与行业均值数据.md")
    if not os.path.exists(md_file_path):
        return ""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content

def get_business_info_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
    statements_dir = os.path.join(project_root, "data","report")

    md_file_path = os.path.join(statements_dir, "主营业务与核心竞争力.md")
    if not os.path.exists(md_file_path):
        return ""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return content

def get_company_info_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
    statements_dir = os.path.join(project_root, "data","report")

    md_file_path = os.path.join(statements_dir, "公司信息数据.md")
    if not os.path.exists(md_file_path):
        return ""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return content

def get_report_file(filename:str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
    statements_dir = os.path.join(project_root, "data","report")

    md_file_path = os.path.join(statements_dir, filename)
    if not os.path.exists(md_file_path):
        return ""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return content

def get_report_file(filename:str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
    statements_dir = os.path.join(project_root, "data","report")

    md_file_path = os.path.join(statements_dir, filename)
    if not os.path.exists(md_file_path):
        return ""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return content

def get_analyze_file(filename:str, path:str, subpath:str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "./"))
    statements_dir = os.path.join(project_root, path, subpath)

    md_file_path = os.path.join(statements_dir, filename)
    if not os.path.exists(md_file_path):
        return ""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return content

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

def save_markdown(content: str, filename: str, path: str = "data/report"):
    """
    将字符串content保存到项目根目录下data/report目录下的指定md文件中。
    :param content: 要保存的字符串内容
    :param filename: 文件名（应以.md结尾）
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(project_root, path)
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def ensure_dir(path):
        """确保目录存在"""
        if not os.path.exists(path):
            os.makedirs(path)
    
def is_url(path):
    """判断是否为URL"""
    return path.startswith('http://') or path.startswith('https://')

def download_image(url, save_path):
    """下载图片"""
    try:
        resp = requests.get(url, stream=True, timeout=10)
        resp.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[下载失败] {url}: {e}")
        return False

def copy_image(src, dst):
    """复制图片"""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"[复制失败] {src}: {e}")
        return False

def extract_images_from_markdown(md_path, images_dir, new_md_path):
    """从markdown中提取图片"""
    ensure_dir(images_dir)
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 ![alt](path) 形式的图片
    pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
    matches = pattern.findall(content)
    used_names = set()
    replace_map = {}
    not_exist_set = set()

    for img_path in matches:
        img_path = img_path.strip()
        # 取文件名
        if is_url(img_path):
            filename = os.path.basename(urlparse(img_path).path)
        else:
            filename = os.path.basename(img_path)
        # 防止重名
        base, ext = os.path.splitext(filename)
        i = 1
        new_filename = filename
        while new_filename in used_names:
            new_filename = f"{base}_{i}{ext}"
            i += 1
        used_names.add(new_filename)
        new_img_path = os.path.join(images_dir, new_filename)
        # 下载或复制
        img_exists = True
        if is_url(img_path):
            success = download_image(img_path, new_img_path)
            if not success:
                img_exists = False
        else:
            # 支持绝对和相对路径
            abs_img_path = img_path
            if not os.path.isabs(img_path):
                abs_img_path = os.path.join(os.path.dirname(md_path), img_path)
            if not os.path.exists(abs_img_path):
                print(f"[警告] 本地图片不存在: {abs_img_path}")
                img_exists = False
            else:
                copy_image(abs_img_path, new_img_path)
        # 记录替换
        if img_exists:
            replace_map[img_path] = f'./images/{new_filename}'
        else:
            not_exist_set.add(img_path)

    # 替换 markdown 内容，不存在的图片直接删除整个图片语法
    def replace_func(match):
        orig = match.group(1).strip()
        if orig in not_exist_set:
            return ''  # 删除不存在的图片语法
        return match.group(0).replace(orig, replace_map.get(orig, orig))

    new_content = pattern.sub(replace_func, content)
    with open(new_md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"图片处理完成！新文件: {new_md_path}")

def format_markdown(output_file, path):
    """格式化markdown文件"""
    file = path + "/" + output_file
    try:
        import subprocess
        format_cmd = ["mdformat", file]
        subprocess.run(format_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print(f"✅ 已用 mdformat 格式化 Markdown 文件: {output_file}")
    except Exception as e:
        print(f"[提示] mdformat 格式化失败: {e}\n请确保已安装 mdformat (pip install mdformat)")

def convert_to_docx(output_file, path, docx_output=None):
    file = path + "/" + output_file
    """转换为Word文档"""
    if docx_output is None:
        docx_output = file.replace('.md', '.docx')
    try:
        import subprocess
        import os
        pandoc_cmd = [
            "pandoc",
            file,
            "-o",
            docx_output,
            "--standalone",
            "--resource-path=/root/python/financial/final_output",
            "--extract-media=/root/python/financial/final_output"
        ]
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        subprocess.run(pandoc_cmd, check=True, capture_output=True, text=True, encoding='utf-8', env=env)
        print(f"\n📄 Word版报告已生成: {docx_output}")
    except subprocess.CalledProcessError as e:
        print(f"[提示] pandoc转换失败。错误信息: {e.stderr}")
        print("[建议] 检查图片路径是否正确，或使用 --extract-media 选项")
    except Exception as e:
        print(f"[提示] 若需生成Word文档，请确保已安装pandoc。当前转换失败: {e}")