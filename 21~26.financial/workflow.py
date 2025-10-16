import os
import yaml
from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from llm import DeepSeek, DeepSeek_R1, Tongyi
from prompts import get_competitor_and_industry_data_prompt, get_competitor_info_prompt, get_business_info_prompt, analyze_financial_data_user_prompt, compare_company_report_user_prompt, generate_valuation_model_user_prompt, outline_prompt, background, generate_section_prompt
from deepresearch.graph import DeepResearchAgent
from financial_data_collection.graph import DataCollectionAgent
from finnancial_caculate.graph import FinancialCaculateAgent
from analyze_agent.graph import AnalyzeAgent
from shareholder_collection_agent.graph import ShareholderCollectionAgent
from stock_info_collection.graph import StockInfoCollectionAgent
from states import OverallState
from utils import save_markdown, get_financial_caculates_file_map, read_csv, get_financial_statements_file_map, get_industry_info_file, get_business_info_file,get_report_file,get_analyze_file,extract_images_from_markdown,format_markdown,convert_to_docx
from schemas import CompetitorInfoList, CompetitorInfo
from datetime import datetime

#获取竞争对手与行业均值数据
def get_competitor_and_industry_data(state: OverallState):
    agent = DeepResearchAgent()
    ret=agent.run(get_competitor_and_industry_data_prompt.format(stock_name=state["stock_name"], stock_code=state["stock_code"], market=state["market"]))
    last_message_content = ""
    if ret["messages"]:
        last_message = ret["messages"][-1]
        last_message_content = last_message.content
    
    #长期记忆
    save_markdown(last_message_content, "竞争对手与行业均值数据.md")

    #短期记忆
    return {"competitor_and_industry_data": last_message_content}

#获取竞争对手信息
def get_competitor_info(state: OverallState):
    formatted_prompt = get_competitor_info_prompt.format(context=state["competitor_and_industry_data"])
    llm=DeepSeek()
    llm_with_structured_output=llm.with_structured_output(CompetitorInfoList)
    ret=llm_with_structured_output.invoke(formatted_prompt)
    print(ret)

    return {"competitor_info": ret}

#获取本公司与竞争对手公司的财务数据
def get_financial_data(state: OverallState):
    #测试数据
    state["competitor_info"] = CompetitorInfoList(competitors=[CompetitorInfo(stock_code='000858', stock_name='五粮液', market='A股'), 
                               CompetitorInfo(stock_code='000568', stock_name='泸州老窖', market='A股'), 
                               CompetitorInfo(stock_code='600809', stock_name='山西汾酒', market='A股'), 
                               CompetitorInfo(stock_code='002304', stock_name='洋河股份', market='A股'), 
                               CompetitorInfo(stock_code='000596', stock_name='古井贡酒', market='A股')])
    agent = DataCollectionAgent()
    #取本公司的
    for year in state["year"]:
        agent.run(state["stock_code"], state["stock_name"], state["market"], year)

    #取竞争对手公司的财务数据
    for competitor in state["competitor_info"].competitors:
        for year in state["year"]:
            agent.run(competitor.stock_code, competitor.stock_name, competitor.market, year)

#计算财务指标
def financial_caculate(state: OverallState):
    #测试数据
    state["competitor_info"] = CompetitorInfoList(competitors=[CompetitorInfo(stock_code='000858', stock_name='五粮液', market='A股'), 
                               CompetitorInfo(stock_code='000568', stock_name='泸州老窖', market='A股'), 
                               CompetitorInfo(stock_code='600809', stock_name='山西汾酒', market='A股'), 
                               CompetitorInfo(stock_code='002304', stock_name='洋河股份', market='A股'), 
                               CompetitorInfo(stock_code='000596', stock_name='古井贡酒', market='A股')])
    agent = FinancialCaculateAgent()
    for year in state["year"]:
        agent.run(state["stock_code"], state["stock_name"], state["market"], year)
    
    for competitor in state["competitor_info"].competitors:
        for year in state["year"]:
            agent.run(competitor.stock_code, competitor.stock_name, competitor.market, year)

#分析单个公司的财务数据
def analyze_financial_data(state: OverallState):
    #测试数据
    state["competitor_info"] = CompetitorInfoList(competitors=[CompetitorInfo(stock_code='000858', stock_name='五粮液', market='A股'), 
                               CompetitorInfo(stock_code='000568', stock_name='泸州老窖', market='A股'), 
                               CompetitorInfo(stock_code='600809', stock_name='山西汾酒', market='A股'), 
                               CompetitorInfo(stock_code='002304', stock_name='洋河股份', market='A股'), 
                               CompetitorInfo(stock_code='000596', stock_name='古井贡酒', market='A股')])
    
    file_map = get_financial_caculates_file_map()
    files = []
    
    if state["stock_code"] in file_map:
        files = file_map[state["stock_code"]]
    
    report0=read_csv(files[0])
    report1=read_csv(files[1])
    report2=read_csv(files[2])

    formatted_user_prompt = analyze_financial_data_user_prompt.format(company_name=state["stock_name"],files0=files[0],report0=report0,files1=files[1],report1=report1,files2=files[2],report2=report2)

    agent = AnalyzeAgent(base_output_dir="analyze_agent_outputs", absolute_path=True)
    ret=agent.run(state["stock_code"], state["stock_name"], state["market"], formatted_user_prompt)
    
    # 确保 company_report 字典已初始化
    if "company_report" not in state or state["company_report"] is None:
        state["company_report"] = {}
    
    state["company_report"][state["stock_code"]] = ret

    for competitor in state["competitor_info"].competitors:
        if competitor.stock_code in file_map:
            files = file_map[competitor.stock_code]
        
        report0=read_csv(files[0])
        report1=read_csv(files[1])
        report2=read_csv(files[2])

        formatted_user_prompt = analyze_financial_data_user_prompt.format(company_name=competitor.stock_name,files0=files[0],report0=report0,files1=files[1],report1=report1,files2=files[2],report2=report2)
        agent = AnalyzeAgent(base_output_dir="analyze_agent_outputs", absolute_path=True)
        ret=agent.run(competitor.stock_code, competitor.stock_name, competitor.market, formatted_user_prompt)
        
        # 确保 company_report 字典已初始化
        if "company_report" not in state or state["company_report"] is None:
            state["company_report"] = {}
            
        state["company_report"][competitor.stock_code] = ret

    return state

#生成对比分析报告
def generate_compare_company_report(state: OverallState):
    #测试数据
    state["competitor_info"] = CompetitorInfoList(competitors=[CompetitorInfo(stock_code='000858', stock_name='五粮液', market='A股'), 
                               CompetitorInfo(stock_code='000568', stock_name='泸州老窖', market='A股'), 
                               CompetitorInfo(stock_code='600809', stock_name='山西汾酒', market='A股'), 
                               CompetitorInfo(stock_code='002304', stock_name='洋河股份', market='A股'), 
                               CompetitorInfo(stock_code='000596', stock_name='古井贡酒', market='A股')])
    state["compare_company_report"] = {}

    file_map = get_financial_caculates_file_map()
    source_files = []
    target_files = []

    if state["stock_code"] in file_map:
        source_files = file_map[state["stock_code"]]
    
    source_report0=read_csv(source_files[0])
    source_report1=read_csv(source_files[1])
    source_report2=read_csv(source_files[2])

    for competitor in state["competitor_info"].competitors:
        if competitor.stock_code in file_map:
            target_files = file_map[competitor.stock_code]
            target_report0=read_csv(target_files[0])
            target_report1=read_csv(target_files[1])
            target_report2=read_csv(target_files[2])

            formatted_user_prompt = compare_company_report_user_prompt.format(source_name=state["stock_name"], source_files0=source_files[0], source_report0=source_report0, source_files1=source_files[1], source_report1=source_report1, source_files2=source_files[2], source_report2=source_report2, target_name=competitor.stock_name, target_files0=target_files[0], target_report0=target_report0, target_files1=target_files[1], target_report1=target_report1, target_files2=target_files[2], target_report2=target_report2)

            agent = AnalyzeAgent(base_output_dir="compare_company_report_outputs", absolute_path=True)
            ret=agent.run(competitor.stock_code, competitor.stock_name, competitor.market, formatted_user_prompt)
            state["compare_company_report"][competitor.stock_code] = ret

    return state

#汇总分析报告
def merger_reports(state: OverallState):
    formatted_output = []
    
    # 遍历analyze_agent_outputs下所有session开头的文件夹
    import os
    analyze_outputs_dir = "./analyze_agent_outputs"

    compare_outputs_dir = "./compare_company_report_outputs"

    if os.path.exists(analyze_outputs_dir):
        for item in os.listdir(analyze_outputs_dir):
            if item.startswith("session_"):
                session_path = os.path.join(analyze_outputs_dir, item)
                if os.path.isdir(session_path):
                    # 使用get_analyze_file函数取出最终分析报告.md的内容
                    report_content = get_analyze_file("最终分析报告.md", "analyze_agent_outputs", item)
                    if report_content:
                        formatted_output.append(f"【财务数据分析结果开始】")
                        formatted_output.append(report_content)
                        formatted_output.append(f"【财务数据分析结果结束】")
                        formatted_output.append("")

    if os.path.exists(compare_outputs_dir):
        for item in os.listdir(compare_outputs_dir):
            if item.startswith("session_"):
                session_path = os.path.join(compare_outputs_dir, item)
                if os.path.isdir(session_path):
                    # 使用get_analyze_file函数取出最终分析报告.md的内容
                    report_content = get_analyze_file("最终分析报告.md", "compare_outputs_dir", item)
                    if report_content:
                        formatted_output.append(f"【财务数据分析结果开始】")
                        formatted_output.append(report_content)
                        formatted_output.append(f"【财务数据分析结果结束】")
                        formatted_output.append("")

    return {"formatted_output": formatted_output}

#获取主营业务与核心竞争力
def get_business_info(state: OverallState):
    agent = DeepResearchAgent()
    ret=agent.run(get_business_info_prompt.format(stock_name=state["stock_name"], stock_code=state["stock_code"], market=state["market"]))
    last_message_content = ""
    if ret["messages"]:
        last_message = ret["messages"][-1]
        last_message_content = last_message.content
    
    #长期记忆
    save_markdown(last_message_content, "主营业务与核心竞争力.md")

    #短期记忆
    return {"business_info": last_message_content}

#生成估值与预测模型
def generate_valuation_model(state: OverallState):
    file_map = get_financial_statements_file_map()
    stock_code = state["stock_code"]
    
    # 初始化年份数据字典
    year_data = {}
    
    # 遍历年份，分别获取每年的数据
    for year in state["year"]:
        if stock_code in file_map:
            year_map = file_map[stock_code]
            if year in year_map:
                files = year_map[year]
                
                # 读取该年份的四个报表文件
                report0 = read_csv(files[0])  # 利润表
                report1 = read_csv(files[1])  # 现金流量表
                report2 = read_csv(files[2])  # 财务指标
                report3 = read_csv(files[3])  # 资产负债表
                
                # 存储该年份的数据
                year_data[year] = {
                    'files': files,
                    'reports': [report0, report1, report2, report3]
                }
    
    # 构建prompt参数字典
    prompt_params = {
        'company_name': state["stock_name"],
        'competitor_and_industry_data': get_industry_info_file(),
        'business_info': get_business_info_file()
    }
    
    # 为每个年份添加数据到prompt参数
    for year in state["year"]:
        if year in year_data:
            data = year_data[year]
            files = data['files']
            reports = data['reports']
            
            # 添加该年份的文件名和报告内容
            prompt_params[f'files0_{year}'] = files[0]
            prompt_params[f'report0_{year}'] = reports[0]
            prompt_params[f'files1_{year}'] = files[1]
            prompt_params[f'report1_{year}'] = reports[1]
            prompt_params[f'files2_{year}'] = files[2]
            prompt_params[f'report2_{year}'] = reports[2]
            prompt_params[f'files3_{year}'] = files[3]
            prompt_params[f'report3_{year}'] = reports[3]

    formatted_prompt = generate_valuation_model_user_prompt.format(**prompt_params)

    llm=DeepSeek()
    ret=llm.invoke(formatted_prompt)
    
    #长期记忆
    save_markdown(ret.content, "估值与预测模型.md")

    #短期记忆
    return {"valuation_model": ret.content}

#获取股东信息
def get_shareholder_info(state: OverallState):
    agent = ShareholderCollectionAgent()
    ret=agent.run(state["stock_code"], state["stock_name"], state["market"])

    #长期记忆
    save_markdown(ret, "股东信息数据.md")

    return {"shareholder_info": ret}

#获取公司信息
def get_company_info(state: OverallState):
    agent = StockInfoCollectionAgent()
    ret=agent.run(state["stock_code"], state["stock_name"], state["market"])

    #长期记忆
    save_markdown(ret, "公司信息数据.md")

    return {"company_info": ret}

#汇总第一阶段所有数据
def summarize_first_stage_data(state: OverallState):
    formatted_report = state["formatted_output"]
    # 统一保存为markdown
    md_output_file = f"./final_output/财务研报汇总_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(md_output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 公司基础信息\n\n## 整理后公司信息\n\n{get_report_file("公司信息数据.md")}\n\n")
        f.write(f"# 股权信息分析\n\n{get_report_file("股东信息数据.md")}\n\n")
        f.write(f"# 行业信息搜索结果\n\n{get_report_file("主营业务与核心竞争力.md")}\n\n")
        f.write(f"# 财务数据分析与两两对比\n\n{formatted_report}\n\n")
        f.write(f"# 商汤科技估值与预测分析\n\n{get_report_file("估值与预测模型.md")}\n\n")

def generate_outline(stock_name: str, report_content: str, background: str):
    formatted_prompt = outline_prompt.format(company_name=stock_name,background=background, report_content=report_content)
    llm=DeepSeek()
    ret=llm.invoke([
                SystemMessage(content="你是一位顶级金融分析师和研报撰写专家，善于结构化、分段规划输出，分段大纲必须用```yaml包裹，便于后续自动分割。"),
                HumanMessage(content=formatted_prompt)
            ])
    try:
        if '```yaml' in ret.content:
            yaml_block = ret.content.split('```yaml')[1].split('```')[0]
        else:
            yaml_block = ret.content
        parts = yaml.safe_load(yaml_block)
        if isinstance(parts, dict):
            parts = list(parts.values())
    except Exception as e:
        print(f"[大纲yaml解析失败] {e}")
        parts = []

    return parts

def generate_section(part_title, prev_content, background, report_content):
    """生成章节"""
    section_prompt = generate_section_prompt.format(part_title=part_title, prev_content=prev_content, background=background, report_content=report_content)
    llm=DeepSeek()
    ret=llm.invoke([
                SystemMessage(content="你是顶级金融分析师，专门生成完整可用的研报内容。输出必须是完整的研报正文，无需用户修改。严格禁止输出分隔符、建议性语言或虚构内容。只允许引用真实存在于【财务研报汇总内容】中的图片地址，严禁虚构、猜测、改编图片路径。如引用了不存在的图片，将被判为错误输出。"),
                HumanMessage(content=section_prompt)
            ])
    return ret.content

#深度研报生成
def generate_deep_report(state: OverallState):
    md_file_path = "./final_output/财务研报汇总_20250926_210018.md"

    # 处理图片路径
    print("🖼️ 处理图片路径...")
    new_md_path = md_file_path.replace('.md', '_images.md')
    images_dir = os.path.join(os.path.dirname(md_file_path), 'images')
    extract_images_from_markdown(md_file_path, images_dir, new_md_path)

    with open(new_md_path, "r", encoding="utf-8") as f:
        report_content = f.read()
    
    # 生成大纲
    print("\n📋 生成报告大纲...")
    parts=generate_outline(state["stock_name"], report_content, background)

    # 分段生成深度研报
    print("\n✍️ 开始分段生成深度研报...")
    full_report = ['# {stock_name}公司研报\n'.format(stock_name=state["stock_name"])]
    prev_content = ''

    for idx, part in enumerate(parts):
        part_title = part.get('part_title', f'部分{idx+1}')
        print(f"\n  正在生成：{part_title}")
        section_text = generate_section(part_title, prev_content, background, report_content)
        full_report.append(section_text)
        print(f"  ✅ 已完成：{part_title}")
        prev_content = '\n'.join(full_report)

    # 保存最终报告
    final_report = '\n\n'.join(full_report)
    output_file = f"深度财务研报分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    save_markdown(final_report, output_file, "final_output")
    
    # 格式化和转换
    print("\n🎨 格式化报告...")
    format_markdown(output_file, "./final_output")

    print("\n📄 转换为Word文档...")
    convert_to_docx(output_file, "./final_output")

    print(f"\n✅ 第二阶段完成！深度研报已保存到: {output_file}")

    return {"final_report": output_file}

builder=StateGraph(OverallState)

builder.add_node("get_competitor_and_industry_data", get_competitor_and_industry_data)
builder.add_node("get_competitor_info", get_competitor_info)
builder.add_node("get_financial_data", get_financial_data)
builder.add_node("financial_caculate", financial_caculate)
builder.add_node("analyze_financial_data", analyze_financial_data)
builder.add_node("generate_compare_company_report", generate_compare_company_report)
builder.add_node("merger_reports", merger_reports)
builder.add_node("get_business_info", get_business_info)
builder.add_node("generate_valuation_model", generate_valuation_model)
builder.add_node("get_shareholder_info", get_shareholder_info)
builder.add_node("get_company_info", get_company_info)
builder.add_node("summarize_first_stage_data", summarize_first_stage_data)
builder.add_node("generate_deep_report", generate_deep_report)

#builder.add_edge(START, "get_competitor_and_industry_data")
#builder.add_edge("get_competitor_and_industry_data", "get_competitor_info")
#builder.add_edge("get_competitor_info", "get_financial_data")
#builder.add_edge("get_financial_data", "financial_caculate")
#builder.add_edge("financial_caculate", "analyze_financial_data")
#builder.add_edge("analyze_financial_data", "generate_compare_company_report")
#builder.add_edge("generate_compare_company_report", "merger_reports")
#builder.add_edge("merger_reports", "get_business_info")
#builder.add_edge("get_business_info", "generate_valuation_model")
#builder.add_edge("generate_valuation_model", "get_shareholder_info")
#builder.add_edge("get_shareholder_info", "get_company_info")
#builder.add_edge("get_company_info", "summarize_first_stage_data")
#builder.add_edge("summarize_first_stage_data", "generate_deep_report")
#builder.add_edge("generate_deep_report", END)

builder.add_edge(START, "generate_deep_report")
builder.add_edge("generate_deep_report", END)

workflow = builder.compile()

ret=workflow.invoke({"stock_code": "600519", "stock_name": "贵州茅台", "market": "A股", "year": ["2022", "2023", "2024"]})
