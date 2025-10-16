import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

# 创建测试数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 创建图形
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('中文标题测试: 正弦函数曲线', fontsize=16)
plt.xlabel('X轴标签 - 时间', fontsize=14)
plt.ylabel('Y轴标签 - 振幅', fontsize=14)
plt.grid(True, alpha=0.3)

# 添加图例和注释
plt.legend(['正弦波'], loc='upper right')
plt.text(2, 0.5, '中文注释: 最大值区域', fontsize=12, 
         bbox=dict(facecolor='yellow', alpha=0.5))

# 显示图形
plt.savefig("./", dpi=150, bbox_inches='tight', facecolor='white')

# 打印当前使用字体信息
current_font = plt.rcParams['font.sans-serif'][0]
print(f"当前使用字体: {current_font}")