from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """您的目标是生成复杂多样的 Web 搜索查询。这些查询适用于高级自动化 Web 研究工具，该工具能够分析复杂的结果、跟踪链接和综合信息。

要求:
- 总是优先生成单个搜索查询，只有在原始问题要求多个方面或元素且单个查询不足以回答时才添加另一个查询。
- 每个查询应专注于原始问题的一个特定方面。
- 不要生成超过 {number_queries} 个查询。
- 查询应多样化，如果主题广泛，则生成多个查询。
- 不要生成多个类似的查询，1 个就足够了。
- 查询应确保收集最新信息。当前日期是 {current_date}。

格式: 
- 将您的响应格式化为包含以下两个字段的 JSON 对象：
   - "rationale": 简要说明为什么这些查询与研究主题相关。
   - "query": 一个搜索查询列表

Example:

Topic: 去年苹果股票和iPhone销量哪个增长更多？
```json
{{
    "rationale": "为了准确回答这个问题，我们需要具体的苹果股票表现和iPhone销量数据。这些查询针对所需的具体财务信息：公司收入趋势、产品特定单位销售数据以及同一财政年度的股票价格变动，用于直接比较。",
    "query": ["Apple 2024 财年总收入增长", "2024 财年 iPhone 销量增长", "2024 财年苹果股价增长"],
}}
```

上下文: {research_topic}"""


web_searcher_instructions = """进行有针对性的Web搜索，以收集有关“{research_topic}”的最新可靠信息，并将其合成为可验证的文本工件。

要求:
- 查询应确保收集最新信息。当前日期是 {current_date}。
- 进行多次、多样化的搜索，以收集全面信息。
- 仔细跟踪每个特定信息的来源，并总结关键发现。
- 输出应基于您的搜索发现，写成一篇高质量的总结或报告。 
- 只能包含在搜索结果中找到的信息，不要编造任何信息。

研究主题:
{research_topic}
"""

reflection_instructions = """您是分析有关 “{research_topic}” 的摘要的专家研究助理.

指令:
- 识别知识缺口或需要深入探索的领域，并生成一个后续查询。（1个或多个）
- 如果提供的摘要足以回答用户的问题，则不要生成后续查询。
- 如果存在知识缺口，请生成一个后续查询，以帮助扩展您的理解。
- 专注于技术细节、实施细节或未完全涵盖的最新趋势。

要求:
- 确保后续查询是自包含的，并包含web搜索所需的相关上下文。

输出格式:
- 将您的响应格式化为包含以下两个字段的 JSON 对象：
   - "is_sufficient": true 或 false
   - "knowledge_gap": 描述缺失或需要澄清的信息
   - "follow_up_queries": 写一个具体的问题来解决这个缺口

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "摘要缺少有关性能指标和基准的信息", // "" if is_sufficient is true
    "follow_up_queries": ["用于评估 [特定技术] 的典型性能基准和指标有哪些？"] // [] if is_sufficient is true
}}
```

仔细分析摘要，识别知识缺口并生成一个后续查询。然后，按照以下JSON格式输出您的响应：

摘要:
{summaries}
"""

answer_instructions = """根据提供的摘要为用户的问题生成高质量的答案.

指令:
- 当前日期是 {current_date}。
- 您是多步骤研究过程的最后一步，不要提及您是最后一步。
- 您可以访问从先前步骤收集的所有信息。
- 您可以访问用户的问题。
- 根据提供的摘要和用户的问题生成用户问题的高质量答案.
- 在答案中正确包含您在摘要中使用的来源，使用 markdown 格式（例如 [apnews]（https://vertexaisearch.cloud.google.com/id/1-0））。这是必须的.

用户上下文:
- {research_topic}

摘要:
{summaries}"""
