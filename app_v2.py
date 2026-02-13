import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

api_key = st.secrets.get("GOOGLE_API_KEY")

if api_key and api_key.startswith("AIza"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.error("API Key Error")

def analyze_text(text):
    p = f"Analyze: {text}. Return JSON: {{'score':0, 'values':[0,0,0,0,0], 'summary':''}}"
    try:
        response = model.generate_content(p)
        t = response.text.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(t)
    except:
        return None

st.set_page_config(page_title="SharpShield", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 情报输入")
    u = st.text_area("在此粘贴文本", height=250)
    if st.button("🚀 启动扫描") and u:
        with st.spinner("AI 解析中..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M:%S"), "得分": res.get('score', 0)})

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
        st.success(res.get('summary', '解析完成'))
    else:
        st.info("💡 终端已就绪。请在左侧输入数据后开启扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
