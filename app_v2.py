import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎配置（解除安全限制）
api_key = st.secrets.get("GOOGLE_API_KEY")
model = None

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 解除所有安全过滤，防止 AI 拒绝回答敏感话题
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        # 优先使用 Pro 模型，因为它在处理复杂指令和绕过过滤上更稳
        model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
        st.sidebar.success("✅ 锐实力引擎已就绪")
    except Exception as e:
        st.sidebar.error(f"❌ 引擎初始化失败: {str(e)}")
else:
    st.sidebar.error("❌ 未检测到 API Key")

# 2. 暴力数据提取（即使 AI 拒绝也能尝试解析）
def analyze_text(text):
    prompt = f"分析该文本风险，只需返回 JSON: {{'score':0-10,'values':[5个数字],'summary':'总结'}}。内容: {text}"
    try:
        if not model: return None
        response = model.generate_content(prompt)
        # 强行提取最外层的 { } 块
        text_response = response.text
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            # 自动修复 AI 习惯使用的单引号和非标准 JSON 格式
            json_data = match.group().replace("'", '"')
            return json.loads(json_data)
        return None
    except:
        # 如果 AI 彻底拦截了（没产生 text），返回一个基础提示数据
        return {"score": 0, "values": [0,0,0,0,0], "summary": "AI 触发安全审核，无法深入分析此敏感话题。"}

# 3. 界面布局
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 情报输入")
    u = st.text_area("在此粘贴需要扫描的文本：", height=250, placeholder="请输入文字...")
    if st.button("🚀 启动扫描") and u:
        with st.spinner("系统正在进行多维度穿透分析..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M:%S"), "得分": res.get('score', 0)})
            else:
                st.error("⚠️ 扫描引擎解析失败。")

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
        st.info("💡 终端已就绪。请输入文本后启动扫描。")

with st.sidebar:
    st.write("### 📜 历史扫描记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
