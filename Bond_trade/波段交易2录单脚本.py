import pandas as pd
import re
from datetime import datetime

def parse_line(line):
    # 获取今天的日期
    today_date = datetime.today().strftime('%Y/%m/%d')
    parsed = {
        "组合类型": "【输入你想设定的组合类型】",
        "组合名称": "",
        "内部证券账户代码": "【输入你想设定的组合代码】",
        "交易对手": "",
        "对手交易员": "",
        "执行市场": "银行间场内",
        "交易日期": today_date,
        "交易方向": "",
        "债券代码": "",
        "交易面额(万元)": "",
        "清算速度": "T+0",
        "首期净价(元)": "",
        "到期收益率": "",
        "行权收益率": "",
        "执行员": "张三"
    }

    line = line.strip()
    if not line:
        parsed["内部证券账户代码"] = "【输入你想设定的组合代码】"
        return parsed

    # 使用正则分割，空格和逗号都作为分隔符
    tokens = re.split(r'[ ,]+', line)  # 用正则表达式将空格和逗号作为分隔符
    tokens = [token.strip() for token in tokens]  # 移除每个部分的前后空格和逗号
    line_lower = line.lower()

    # ------------------------------
    # 1) 内部证券账户代码判断(暂时不需要)
    # ------------------------------
    # if "bd2" in line_lower:
    #     account_code = "【输入你想设定的组合代码】"
    # elif "zj3" in line_lower or "中间3" in line_lower:
    #     account_code = "【输入你想设定的组合代码2】"
    # else:
    #     account_code = "【输入你想设定的组合代码3】"
    #
    # parsed["内部证券账户代码"] = account_code

    # ------------------------------
    # 2) 交易方向、对手方解析
    # ------------------------------
    sell_pattern = re.search(r"(?:北京证券|北京)\s+(?:to|出给)\s+(\S+)", line, re.IGNORECASE)
    buy_pattern = re.search(r"(\S+)\s+(?:to|出给)\s+(?:北京证券|北京)", line, re.IGNORECASE)

    if sell_pattern:
        parsed["交易对手"] = sell_pattern.group(1)
        parsed["交易方向"] = "现券卖出"
    elif buy_pattern:
        parsed["交易对手"] = buy_pattern.group(1)
        parsed["交易方向"] = "现券买入"

    # ------------------------------
    # 3) 发后解析对手方和对手交易员
    # ------------------------------
    institution_keywords = ["银行", "证券", "基金", "农", "资产", "信托", "公司", "理财", "农信", "资管"]
    abbreviation_map = {
        "招行": "招商银行"
    }
    def normalize_institution_name(name):
        for abbr, full_name in abbreviation_map.items():
            if abbr in name:
                return full_name
        return name

    filler_words = {"对方", "请求", "请求你", "你"}

    if "发" in line:
        parts = line.split("发", 1)
        if len(parts) > 1:
            after_fa = parts[-1].strip()
            # 如果"发"后面有 "北京证券", "张三", "北京", "李四"，则跳过覆盖
            if any(keyword in after_fa for keyword in ["北京证券", "张三", "北京", "李四"]):
                pass  # 不进行任何覆盖处理，保持原始数据
            else:
                # 否则，继续处理"发"后面的内容，覆盖交易对手和交易员
                cn_matches = re.findall(r"[\u4e00-\u9fa5]+", after_fa)
                final_institution = ""
                final_trader = ""
                i = 0
                length = len(cn_matches)
                while i < length:
                    w = cn_matches[i]
                    w = normalize_institution_name(w)
                    if any(kw in w for kw in institution_keywords):
                        final_institution = w
                        final_trader = ""
                        j = i + 1
                        trader_found = False
                        while j < length and not trader_found:
                            w2 = cn_matches[j]
                            if 2 <= len(w2) <= 4 and w2 not in filler_words:
                                final_trader = w2
                                trader_found = True
                            j += 1
                    i += 1

                if final_institution:
                    parsed["交易对手"] = final_institution
                    if final_trader:
                        parsed["对手交易员"] = final_trader
                else:
                    if parsed["交易对手"]:
                        for w in cn_matches:
                            if 2 <= len(w) <= 4 and w not in filler_words:
                                parsed["对手交易员"] = w
                                break

    # ------------------------------
    # 4) 若仍无对手方，fallback
    # ------------------------------
    if not parsed["交易对手"]:
        cn_all = re.findall(r"[\u4e00-\u9fa5]+", line)
        for w in cn_all:
            w = normalize_institution_name(w)
            if any(kw in w for kw in institution_keywords):
                parsed["交易对手"] = w
                break

    # ------------------------------
    # 5) 债券代码处理(去除.IB后缀)
    # ------------------------------
    bond_code = ""
    for tk in tokens:
        if re.match(r"^\d+(\.IB)?$", tk, re.IGNORECASE):
            bond_code = tk.replace(".IB", "")
            break
    parsed["债券代码"] = bond_code

    # ------------------------------
    # 6) 到期收益率 & 交易面额 & 清算速度
    #
    # 在这条要素中，如果出现 <10 的数值视为到期收益率，
    # 再看后面紧跟若干 token，直到找到 "+0"或"+1"为结算速度。
    # “到期收益率”和“+0或+1”之间的那个 token 即是交易面额(万)。
    # ------------------------------
    float_pattern = re.compile(r"^\d+(\.\d+)?$")
    all_nums_idx = [ (i, tk) for i, tk in enumerate(tokens) if float_pattern.match(tk)]

    # 首先获取到期收益率( <10 )
    # 然后往后搜寻 +0 / +1
    # 中间那一个 token 就是交易面额(万元)
    # 如果找不到 +0 / +1，就保持原逻辑(如有)
    found_ytm = False
    for (idx, tk) in all_nums_idx:
        val = float(tk)
        if val < 10:
            # 这是到期收益率
            parsed["到期收益率"] = f"{val:.4f}%"
            found_ytm = True

            # 从 idx+1 开始往后找 +0 或 +1
            # 需要 tokens[idx+2] == +0/+1 => tokens[idx+1] 即交易面额
            if idx+2 < len(tokens):
                # tokens[idx+1] => transaction amount
                # tokens[idx+2] => +0 / +1
                if tokens[idx+2].lower() in ["+0", "+1"]:
                    # 交易面额
                    parsed["交易面额(万元)"] = tokens[idx+1]
                    # 结算速度
                    if tokens[idx+2].lower() == "+1":
                        parsed["清算速度"] = "T+1"
                # 若没有匹配到 +0 / +1，就不做额外处理
            break
    # ------------------------------
    # 7) 如果还没有“到期收益率”，则按原逻辑(净价 / <10)  [已有相关处理]
    # ------------------------------
    net_price_pattern = re.search(r"净价\s*(\d+(\.\d+)?)", line)
    if net_price_pattern:
        val = float(net_price_pattern.group(1))
        parsed["首期净价(元)"] = f"{val:.4f}"
    else:
        if not found_ytm:
            # 没有按上面新的方式找到到期收益率，就走原逻辑
            float_pattern_2 = re.compile(r"\d+(\.\d+)?")
            all_values = [float(tk) for tk in tokens if float_pattern_2.match(tk)]
            ytm_candidates = [v for v in all_values if v < 10]
            if ytm_candidates:
                parsed["到期收益率"] = f"{ytm_candidates[0]:.4f}%"

    return parsed

def process_input_to_excel(input_text, output_excel="output.xlsx"):
    lines = input_text.strip().split("\n")
    results = []
    for line in lines:
        if not line.strip():
            continue
        parsed = parse_line(line)
        results.append(parsed)

    df = pd.DataFrame(results, columns=[
        "组合类型","组合名称","内部证券账户代码","交易对手","对手交易员","执行市场","交易日期",
        "交易方向","债券代码","交易面额(万元)","清算速度","首期净价(元)","到期收益率","行权收益率","执行员"
    ])
    # 获取今天的日期
    today_date = datetime.today().strftime('%Y-%m-%d')  # 获取今天的日期，格式化为 "YYYY-MM-DD"

    # 根据日期和固定名称生成文件名
    output_excel = f"【{today_date}】波段交易2_张三.xlsx"

    # 输出结果到Excel文件
    df.to_excel(output_excel, index=False)
    print(f"解析完成，结果已写入 {output_excel}")



if __name__ == "__main__":
    input_text = """

"""
    process_input_to_excel(input_text, "output.xlsx")


