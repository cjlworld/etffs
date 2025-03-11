import streamlit as st
from datetime import datetime
import json
from streamlit_local_storage import LocalStorage
import tools

# 初始化本地存储
local_storage = LocalStorage()

# 从本地存储加载历史记录
def load_history():
    history_str = local_storage.getItem("etf_history")
    return json.loads(history_str) if history_str else {}

# 保存历史记录到本地存储
def save_history(history):
    local_storage.setItem("etf_history", json.dumps(history))

# 网页布局
st.title("ETF估值分析工具")
st.write("本工具用于计算ETF的加权调和平均市盈率(PE)")

# 输入区域
col1, col2 = st.columns([3,1])
with col1:
    etf_code = st.text_input("请输入ETF代码（如517180）:", 
                            placeholder="6位数字代码").strip().upper()

with col2:
    st.write("")
    st.write("")
    query_btn = st.button("开始计算")

# 处理单个查询请求
if query_btn and etf_code:
    history = load_history()
    
    with st.spinner(f"正在处理 {etf_code}..."):
        try:
            etf_name, holdings = tools.get_etf_info(etf_code)
            harmonic_pe = tools.calculate_harmonic_pe(holdings)
            
            # 更新历史记录
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history[etf_code] = {
                "code": etf_code,
                "name": etf_name,
                "pe": harmonic_pe,
                "time": current_time
            }
            save_history(history)
            
            st.success(f"{etf_name} 更新成功！")
            st.markdown(f"""
                - ETF名称: **{etf_name}**
                - 加权调和PE: **{harmonic_pe if harmonic_pe else 'N/A'}**
                - 计算时间: {current_time}
                """)
        except Exception as e:
            st.error(f"处理失败: {str(e)}")

# 显示历史记录和刷新功能
history = load_history()
if history:
    st.divider()
    
    # 显示历史记录表格
    st.subheader("历史估值记录")
        
    # 刷新全部按钮和进度显示
    col_a, col_b = st.columns([2, 5])
    with col_a:
        refresh_all_btn = st.button("🔄 刷新全部历史记录")
    with col_b:
        status = st.empty()
    
    # 处理批量刷新
    if refresh_all_btn:
        # 先加载全部历史记录
        all_history = load_history()
        etf_list = list(all_history.keys())
        total = len(etf_list)
        progress = st.progress(0)
        
        for i, code in enumerate(etf_list):
            status.text(f"正在刷新 {code} ({i+1}/{total})")
            
            try:
                # 获取最新数据
                etf_name, holdings = tools.get_etf_info(code)
                harmonic_pe = tools.calculate_harmonic_pe(holdings)
                
                # 更新当前记录（基于初始加载的all_history）
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                all_history[code] = {
                    "code": code,
                    "name": etf_name,
                    "pe": harmonic_pe,
                    "time": current_time
                }
                
            except Exception as e:
                status.warning(f"⚠️ {code} 刷新失败: {str(e)}")
            
            progress.progress((i+1)/total)
        
        # 所有处理完成后统一保存
        save_history(all_history)
        status.success("所有记录刷新完成！")
        progress.empty()

    history = load_history()
    sorted_records = sorted(history.values(), 
                           key=lambda x: x['time'], reverse=True)
    
    table_data = [
        {
            "ETF代码": rec['code'],
            "ETF名称": rec['name'],
            "加权调和PE": rec['pe'] if rec['pe'] else 'N/A',
            "最后查询时间": rec['time']
        } for rec in sorted_records
    ]
    
    st.table(table_data)

# 侧边栏说明
with st.sidebar:
    st.markdown("""
    **使用说明**
    1. 输入6位ETF数字代码（如：510300）
    2. 点击"开始计算"获取最新估值
    3. 使用"刷新全部"批量更新历史记录

    **注意事项**
    - 数据来源：天天基金网、雪球
    - 港股PE数据可能获取不全
    - 刷新全部功能会按顺序重新计算所有历史记录
    """)