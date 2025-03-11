import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import akshare as ak
import traceback

def get_etf_info(etf_code):
    """获取ETF持仓数据和名称"""
    print(f"获取ETF {etf_code} 数据...")
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={etf_code}&month=3,6,9,12"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 获取ETF名称
        name_tag = soup.find("a", href=re.compile(f".*{etf_code}.*"))
        etf_name = name_tag.text.strip() if name_tag else "未知ETF"
        
        # 查找所有季度持仓报告
        reports = []
        for box in soup.find_all("div", class_="box"):
            date_tag = box.find("font", class_="px12")
            if date_tag:
                date_str = date_tag.text.strip()
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                table = box.find("table", class_="comm")
                if table:
                    reports.append((date, table))
        
        if not reports:
            return None, None
        
        # 获取最新报告
        latest_report = max(reports, key=lambda x: x[0])[1]
        
        # 解析持仓数据
        holdings = []
        for row in latest_report.tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 8:
                continue
                
            stock_code = cols[1].text.strip()
            weight = cols[6].text.replace("%", "").strip()
            
            holdings.append({
                "symbol": stock_code,
                "weight": float(weight)/100
            })

        print(f"获取ETF {etf_code} 数据成功: {holdings}")
        return etf_name, holdings
    
    except Exception:
        traceback.print_exc()
        return None, None

def code_to_xq_symbol(code):
    # 五位数 港股
    if len(code) == 5:
        return code
    
    assert len(code) == 6
    if code.startswith("6") or code.startswith("9"):
        return f"SH{code}"
    else:
        return f"SZ{code}"

def get_pe_ratio(symbol):
    """获取市盈率数据"""
    try:
        df = ak.stock_individual_spot_xq(symbol=symbol)
        pe_row = df[df["item"] == "市盈率(TTM)"]
        if not pe_row.empty:
            pe = pe_row["value"].values[0]
            return float(pe) if pe not in [None, "None"] else 1e9
    except Exception:
        return 1e9

def calculate_harmonic_pe(holdings):
    """计算加权调和平均PE"""
    total_weight = 0.0
    weighted_sum = 0.0
    
    for holding in holdings:
        pe = get_pe_ratio(code_to_xq_symbol(holding["symbol"]))
        print(f"{holding['symbol']} PE: {pe}")
        
        if pe and pe > 0:
            total_weight += holding["weight"]
            weighted_sum += holding["weight"] / pe
            
    if weighted_sum == 0:
        return None
    
    return total_weight / weighted_sum