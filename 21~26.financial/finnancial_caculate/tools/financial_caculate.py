from langchain_core.tools import tool

@tool
def calculate_gross_profit_margin(operating_income: float, operating_cost: float) -> float:
    """
    计算毛利率
    公式: (营业收入 - 营业成本) / 营业收入 × 100%

    参数:
        operating_income: float, 营业收入
        operating_cost: float, 营业成本

    返回:
        float, 毛利率（百分比）
    """
    if operating_income == 0:
        raise ZeroDivisionError("营业收入为0，无法计算毛利率。")
    gross_profit_margin = (operating_income - operating_cost) / operating_income
    return gross_profit_margin

@tool
def calculate_net_profit_margin(net_profit: float, operating_income: float) -> float:
    """
    计算净利率
    公式: 净利润 / 营业收入 × 100%

    参数:
        net_profit: float, 净利润
        operating_income: float, 营业收入

    返回:
        float, 净利率（百分比）
    """
    if operating_income == 0:
        raise ZeroDivisionError("营业收入为0，无法计算净利率。")
    net_profit_margin = net_profit / operating_income
    return net_profit_margin

@tool
def calculate_debt_to_asset_ratio(total_liabilities: float, total_assets: float) -> float:
    """
    计算资产负债率
    公式: 总负债 / 总资产 × 100%

    参数:
        total_liabilities: float, 总负债
        total_assets: float, 总资产

    返回:
        float, 资产负债率（百分比）
    """
    if total_assets == 0:
        raise ZeroDivisionError("总资产为0，无法计算资产负债率。")
    debt_to_asset_ratio = total_liabilities / total_assets
    return debt_to_asset_ratio

@tool
def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    计算流动比率
    公式: 流动资产 / 流动负债

    参数:
        current_assets: float, 流动资产
        current_liabilities: float, 流动负债

    返回:
        float, 流动比率
    """
    if current_liabilities == 0:
        raise ZeroDivisionError("流动负债为0，无法计算流动比率。")
    current_ratio = current_assets / current_liabilities
    return current_ratio


@tool
def calculate_quick_ratio(current_assets: float, inventories: float, prepayments: float, current_liabilities: float) -> float:
    """
    计算速动比率
    公式: (流动资产 - 存货 - 预付账款) / 流动负债

    参数:
        current_assets: float, 流动资产
        inventories: float, 存货
        prepayments: float, 预付账款
        current_liabilities: float, 流动负债

    返回:
        float, 速动比率
    """
    if current_liabilities == 0:
        raise ZeroDivisionError("流动负债为0，无法计算速动比率。")
    quick_assets = current_assets - inventories - prepayments
    quick_ratio = quick_assets / current_liabilities
    return quick_ratio

@tool
def calculate_total_asset_turnover(operating_income: float, average_total_assets: float) -> float:
    """
    计算总资产周转率
    公式: 总资产周转率 = 营业收入 / 平均总资产

    参数:
        operating_income: float, 营业收入
        average_total_assets: float, 平均总资产

    返回:
        float, 总资产周转率
    """
    if average_total_assets == 0:
        raise ZeroDivisionError("平均总资产为0，无法计算总资产周转率。")
    return operating_income / average_total_assets

@tool
def calculate_receivables_turnover_days(operating_income: float, average_net_receivables: float) -> float:
    """
    计算应收账款周转天数
    公式: 365天 / (营业收入 / 平均应收账款净额)

    参数:
        operating_income: float, 营业收入
        average_net_receivables: float, 平均应收账款净额

    返回:
        float, 应收账款周转天数
    """
    if average_net_receivables == 0:
        raise ZeroDivisionError("平均应收账款净额为0，无法计算应收账款周转天数。")
    turnover_ratio = operating_income / average_net_receivables
    if turnover_ratio == 0:
        raise ZeroDivisionError("营业收入为0，无法计算应收账款周转天数。")
    return 365 / turnover_ratio

@tool
def calculate_inventory_turnover_days(cost_of_goods_sold: float, average_inventory: float) -> float:
    """
    计算存货周转天数
    公式: 365天 / (营业成本 / 平均存货余额)

    参数:
        cost_of_goods_sold: float, 营业成本
        average_inventory: float, 平均存货余额

    返回:
        float, 存货周转天数
    """
    if average_inventory == 0:
        raise ZeroDivisionError("平均存货余额为0，无法计算存货周转天数。")
    turnover_ratio = cost_of_goods_sold / average_inventory
    if turnover_ratio == 0:
        raise ZeroDivisionError("营业成本为0，无法计算存货周转天数。")
    return 365 / turnover_ratio

@tool
def calculate_cash_flow_matching_ratio(net_cash_flow_from_operating_activities: float, net_profit: float) -> float:
    """
    计算现金流匹配度
    公式: 经营活动产生的现金流量净额 / 净利润

    参数:
        net_cash_flow_from_operating_activities: float, 经营活动产生的现金流量净额
        net_profit: float, 净利润

    返回:
        float, 现金流匹配度
    """
    if net_profit == 0:
        raise ZeroDivisionError("净利润为0，无法计算现金流匹配度。")
    return net_cash_flow_from_operating_activities / net_profit

@tool
def calculate_sales_cash_ratio(net_cash_flow_from_operating_activities: float, operating_income: float) -> float:
    """
    计算销售现金比率
    公式: 经营活动产生的现金流量净额 / 营业收入

    参数:
        net_cash_flow_from_operating_activities: float, 经营活动产生的现金流量净额
        operating_income: float, 营业收入

    返回:
        float, 销售现金比率
    """
    if operating_income == 0:
        raise ZeroDivisionError("营业收入为0，无法计算销售现金比率。")
    return net_cash_flow_from_operating_activities / operating_income

@tool
def calculate_equity_multiplier(asset_liability_ratio: float) -> float:
    """
    计算权益乘数
    公式: 权益乘数 = 1 / (1 - 资产负债率)

    参数:
        asset_liability_ratio: float, 资产负债率（如0.6表示60%）

    返回:
        float, 权益乘数
    """
    if asset_liability_ratio >= 1:
        raise ValueError("资产负债率不能大于或等于1。")
    if asset_liability_ratio < 0:
        raise ValueError("资产负债率不能为负数。")
    denominator = 1 - asset_liability_ratio
    if denominator == 0:
        raise ZeroDivisionError("资产负债率为1，无法计算权益乘数。")
    return 1 / denominator




