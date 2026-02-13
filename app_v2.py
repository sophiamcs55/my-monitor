import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.error("❌ 未检测到 API Key")

# 2. 强力解析逻辑
def analyze_text(text):
    prompt = f"分析风险并只返回JSON: {{'score':0-10,'values':[5个数字],'summary':'总结'}}。内容: {text}"
    try:
        response = model.generate_content(prompt)
        res_text = response.text.strip()
        # 使用正则提取最外层的 { ... } 块
        match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
        return None
    except:
        return None

# 3. 界面显示
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 情报输入")
    u = st.text_area("在此粘贴文本：", height=250)
    if st.button("🚀 启动扫描") and u:
        with st.spinner("AI 正在扫描..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M"), "得分": res.get('score', 0)})
            else:
                st.error("⚠️ 扫描引擎响应异常，请重试。")

with c2:
    st.subheader("📊 分析看板")
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.metric("风险评分", f"{res.get('score', 0)} / 10")
        df = pd.DataFrame(dict(
            r=res.get('values', [0,0,0,0,0]), 
            theta=['宗教','技术','政治','经济','媒体']
        ))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"**总结：** {res.get('summary', '')}")
    else:
        st.info("💡 请输入文本后启动扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
