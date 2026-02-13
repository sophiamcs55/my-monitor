import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎核心配置（增加自动备选机制）
api_key = st.secrets.get("GOOGLE_API_KEY")
model = None

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 尝试使用最快的 Flash 模型，如果失败则自动切换
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # 简单测试一下
            model.generate_content("test")
            st.sidebar.success("✅ Flash 引擎就绪")
        except:
            model = genai.GenerativeModel('gemini-pro')
            st.sidebar.warning("⚠️ Flash 不可用，已降级至 Pro 引擎")
    except Exception as e:
        st.sidebar.error(f"❌ 引擎初始化失败: {str(e)}")
else:
    st.sidebar.error("❌ 未检测到 API Key")

# 2. 强力数据提取（无视 AI 的废话）
def analyze_text(text):
    prompt = f"分析风险并只返回JSON: {{'score':0-10,'values':[5个数字],'summary':'总结'}}。内容: {text}"
    try:
        if not model: return None
        response = model.generate_content(prompt)
        # 提取括号内的 JSON
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
        return None
    except:
        return None

# 3. 界面布局
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 情报输入")
    u = st.text_area("在此粘贴文本：", height=250, placeholder="请输入内容...")
    if st.button("🚀 启动扫描") and u:
        with st.spinner("AI 正在深度扫描..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M"), "评分": res.get('score', 0)})
            else:
                st.error("⚠️ 扫描失败：模型响应异常或内容被拦截。")

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
        st.success(f"**分析总结：** {res.get('summary', '')}")
    else:
        st.info("💡 终端就绪。请输入文本后点击扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
