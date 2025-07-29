from rich.console import Console
from rich.table import Table
import numpy as np
import time, datetime, os

# 生成表格
def printTable(production_name=[''], production_time=[''], title=None):
    if title is None:
        table = Table(title="✅ beautifyplot Productions Output Table ✅", title_style="bold bright_green")
    else:
        table = Table(title=title, title_style="bold bright_green")
    
    # 确认production_name的必须为一维list
    production_name = np.array(production_name)
    production_time = np.array(production_time)
    if production_name.ndim > 1:
        production_name = production_name.flatten()
    if production_time.ndim > 1:
        production_time = production_time.flatten()
        
    # 获取production_name的长度
    production_num = len(production_name)
    if production_num != len(production_time):
        raise ValueError(f"\033[45m[pymeili inner Error]\033[0m The length of production_name and production_time must be the same.")
    
    # 生成PID,乃根据production_name的长度生成数列
    PID = np.arange(1, production_num+1)


    columns = ["PID", "Production Path Name", "Production Time"]

    for column in columns:
        table.add_column(column)

    # 添加数据
    for i in range(production_num):
        table.add_row(str(PID[i]), str(production_name[i]), str(production_time[i]))
        
    Console().print(table)
    
    return table

# 获取时间
def getTableTime():
    timeInUTC = str(datetime.datetime.utcnow()) + 'z'
    return timeInUTC


