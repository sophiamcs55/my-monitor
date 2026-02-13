import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

# 1. API 引擎设置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.error("❌ 未检测到 API Key，请检查 Secrets 配置")

# 2. 增强型数据解析函数
def analyze_text(text):
    prompt = f"分析该文本的风险，必须只返回一个 JSON 格式。格式如下: {{'score': 0-10, 'values': [5个数字], 'summary': '一句话总结'}}。待分析内容: {text}"
    try:
        response = model.generate_content(prompt)
        res_text = response.text.strip()
        # 核心修复：强力抓取 JSON 块，无视 Markdown 干扰
        if "```" in res_text:
            res_text = res_text.split("```")[1]
            if res_text.startswith("json"):
                res_text = res_text[4:]
        return json.loads(res_text.strip())
    except Exception as e:
        return None

# 3. 界面布局
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📝 情报输入")
    user_input = st.text_area("在此粘贴需要扫描的文本：", height=250, placeholder="输入文本后点击启动扫描...")
    if st.button("🚀 启动扫描") and user_input:
        with st.spinner("AI 正在深度解析中..."):
            result = analyze_text(user_input)
            if result:
                st.session_state['result'] = result
                st.session_state['history'].insert(0, {
                    "时间": datetime.now().strftime("%H:%M:%S"), 
                    "评分": result.get('score', 0)
                })
            else:
                st.error("⚠️ AI 返回数据异常，请重试。")

with col2:
    st.subheader("📊 分析看板")
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.metric("风险评分", f"{res.get('score', 0)} / 10")
        
        # 雷达图绘制
        df = pd.DataFrame(dict(
            r=res.get('values', [0,0,0,0,0]), 
            theta=['宗教','技术','政治','经济','媒体']
        ))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"**分析总结：** {res.get('summary', '解析完成')}")
    else:
        st.info("💡 终端已就绪。请在左侧输入文本并点击扫描。")

with st.sidebar:
    st.write("### 📜 历史扫描")
    if st.session_state['history']:
        # 保持你需要的历史记录表格
        st.table(pd.DataFrame(st.session_state['history']))
