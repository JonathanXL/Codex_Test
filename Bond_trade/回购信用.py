import re
import pandas as pd
from datetime import  datetime,timedelta
from openpyxl import Workbook

# 输入的原始文本
input_text = """

"""

# 以“abc证券”分割文本得到不同的组
groups = input_text.split("abc证券")[1:]

# 创建两个新的 Excel 工作簿
wb1= Workbook()
ws1 = wb1.active
wb2= Workbook()
ws2 = wb2.active

# # 写入表头
base_headers1 = ["内部证券账户代码","外部证券账户代码","对手内部证券账户代码",
"外部成交编号","交易员",
"内部账户交易员",
"交易对手",
"对手交易员",
"对手方银行账号",
"交易市场",
"执行市场",
"交易日期",
"交易方向",
"债券代码",
"交易面额(万元)",
"清算速度",
"首期结算方式",
"意向天数",
"到期结算日期",
"到期结算方式",
"计息基准",
"借贷/拆借/回购利率",
"到期结算金额(元)",
"备注",
"交易费用(元)",
"结算费用(元)",
"合并约定号",
"中介机构",
"中介费用"]
bond_headers1 = []
base_headers2=["复核人","执行员","报价来源","对手方交易员代码","对手方席位号","大宗交易约定号","提前购回利率(%)","报价方式"]
# 假设每组最多有 10 个债券，可根据实际情况调整
max_bonds = 15
for i in range(1, max_bonds + 1):
    bond_headers1.extend([f"质押券{i}代码", f"质押券{i}券面总额(万元)", f"质押券{i}折价率"])

headers1 = base_headers1 + bond_headers1+base_headers2

ws1.append(headers1)

headers2 = ["本方方向*","本方*","对手方*","对手方交易员*","回购方式*","回购期限(天)*","回购利率(%)*","交易金额（元）","债券代码","债券简称","券面总额(万)","折算比例(%)","清算速度*","清算类型*","首次结算方式*","到期结算方式*","债券币种","结算币种","汇率","本方状态","回购利息","到期结算金额","报价类型","报价编号","最后更新时间","备注","补充条款"]
ws2.append(headers2)

# 获取当前日期
today_date = datetime.today().date()

# 创建工作日历
bday = pd.tseries.offsets.BusinessDay()

for group in groups:
    # 去除首尾空白字符
    group = group.strip()
    if not group:
        continue

     # 提取天数
    intend_day=int(re.search(r'(\d+)d', group).group(1))
    
    # 计算到期日期
    maturity_date = datetime.today()+timedelta(days=intend_day)
    maturity_date_pd = pd.Timestamp(maturity_date)
    while not pd.tseries.offsets.BusinessDay().is_on_offset(maturity_date_pd):
        maturity_date_pd = maturity_date_pd + bday
    maturity_date = maturity_date_pd.to_pydatetime().date()
        
    # 提取利率
    interest_rate = float(re.search(r'(\d+\.\d+)', group).group(1))
    interest_rate1=f"{interest_rate:.2f}%"
    interest_rate2=f"{interest_rate:.4f}"
    
    # 提取交易面额
    # transaction_face_value = int(re.search(r'折后(\d+)', group).group(1))
    # transaction_face_value2=f"{transaction_face_value*10000:.2f}"

    # 提取折扣率
    discount_start = group.find("折")
    if discount_start > 0:
        discount_str = ""
        i = discount_start - 1
        while i >= 0 and group[i].isdigit():
            discount_str = group[i] + discount_str
            i -= 1
        if discount_str:
            overall_discount = int(discount_str)
        else:
            overall_discount = None
    else:
        overall_discount = None

    # 提取交易面额
    face_value_start = group.find("折后") + 2
    face_value_str = ""
    for char in group[face_value_start:]:
        if char.isdigit():
            face_value_str += char
        else:
            break
    transaction_face_value = float(face_value_str)
    transaction_face_value2=f"{transaction_face_value*10000:.2f}"

# 提取交易对手和对手交易员
    send_index = group.find("发")
    if send_index != -1:
        parts = group[send_index + 1:].strip().split()
        if len(parts) >= 1:
            trading_counterparty = parts[0]
        if len(parts) >= 2:
            counterparty_trader = parts[1]
            
    # 处理债券信息
    lines = group.split("\n")[1:-1]
    first_row = True
    bond_data=[]
    for line in lines:
        if ".IB" not in line:
            continue

        # 提取债券代码
        ib_index = line.find(".IB")
        bond_code = line[:ib_index]

         # 提取债券名称
        bond_name = line[ib_index + 3:].split()[0]

        # 提取债券面值
        parts = line.split()
        rating_index = -1
        for i, part in enumerate(parts):
            if part in ["AA+", "AAA", "AAA+","AA"]:
                rating_index = i
                break
        bond_face_value = int(parts[rating_index - 1])

        # 提取评级
        rating = ""
        for r in ["AA+", "AAA", "AAA+","AA"]:
            if r in line:
                rating = r
                break

        # 确定最终折扣率
        if overall_discount is not None:
            discount = overall_discount
        else:
            rating_index = line.find(rating)
            if rating_index + len(rating) < len(line):
                next_part = line[rating_index + len(rating):].strip().split()[0]
                if next_part.isdigit():
                    discount = int(next_part)
                else:
                    discount = None
            else:
                discount = None
        discount1=f"{discount:.2f}%"
        discount2=f"{discount:.2f}"
        bond_data.extend([bond_code, bond_face_value, discount1])

#         result = [days, rate, discount, transaction_face_value, bond_code, bond_name, bond_face_value, rating,
# trading_counterparty, counterparty_trader,maturity_date]
#         result = [str(x) for x in result if x is not None]
#         print(" ".join(result))

        if first_row:        
            result2 = ["正回购","abc证券",trading_counterparty, counterparty_trader,"双边回购",intend_day,interest_rate2,transaction_face_value2,bond_code, bond_name,bond_face_value, discount2, "+0","全额清算","券款对付","券款对付"]
            first_row = False
        else:        
            result2 = ["","","", "","","","","",bond_code, bond_name,bond_face_value, discount2, "","","",""]
        ws2.append(result2)
        # 补齐债券数据到最大长度
    while len(bond_data) < max_bonds * 3:
        bond_data.append("")
        
    result1 = ["SECU_JY_RZZH","B0002917","","","","", trading_counterparty, counterparty_trader,"","","银行间场内",today_date,"质押式正回购","",transaction_face_value, "T+0","DVP",intend_day, maturity_date,"DVP","",interest_rate1,"","","","","","",""]+bond_data
    ws1.append(result1)
        
today_date = datetime.today().strftime('%m%d')
        
# 生成文件名
filename1 = f"{today_date}-信用.xlsx"
filename2 = f"{today_date}-回购前台信用.xlsx"

# 保存 Excel 文件
wb1.save(filename1)
wb2.save(filename2)

print(f"解析完成，结果已写入 {filename1}")
print(f"解析完成，结果已写入 {filename2}")

        
