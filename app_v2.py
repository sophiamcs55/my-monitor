import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎配置：修复 404 错误
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 显式指定模型，确保兼容性
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.sidebar.success("✅ API 连接已建立")
    except Exception as e:
        st.sidebar.error(f"❌ 初始化失败: {str(e)}")
else:
    st.sidebar.error("❌ 未检测到 API Key，请检查 Secrets 配置")

# 2. 强效数据提取逻辑
def analyze_text(text):
    prompt = f"分析该文本的风险，只返回一个 JSON。格式: {{\"score\": 0, \"values\": [0,0,0,0,0], \"summary\": \"\"}}。内容: {text}"
    try:
        response = model.generate_content(prompt)
        # 检查 AI 是否因安全原因拒绝回答
        if not response.candidates or not response.candidates[0].content.parts:
            return {"score": 0, "values": [0,0,0,0,0], "summary": "AI 无法分析此内容（可能涉及安全过滤）。"}
            
        res_text = response.text.strip()
        # 强力抓取 JSON 块
        match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if match:
            clean_json = match.group().replace("'", '"')
            return json.loads(clean_json)
        return None
    except Exception as e:
        st.sidebar.error(f"❌ 运行错误: {str(e)}")
        return None

# 3. 界面布局与汉化
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 情报输入")
    u = st.text_area("在此粘贴需要扫描的文本：", height=250, placeholder="请输入文字...")
    if st.button("🚀 启动扫描") and u:
        with st.spinner("AI 正在深度解析中..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {
                    "时间": datetime.now().strftime("%H:%M:%S"), 
                    "评分": res.get('score', 0)
                })
            else:
                st.error("⚠️ 解析引擎未响应，请检查左侧错误诊断。")

with c2:
    st.subheader("📊 分析看板")
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.metric("风险评分", f"{res.get('score', 0)} / 10")
        
        # 绘制雷达图
        df = pd.DataFrame(dict(
            r=res.get('values', [0,0,0,0,0]), 
            theta=['宗教','技术','政治','经济','媒体']
        ))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"**分析总结：** {res.get('summary', '解析完成')}")
    else:
        st.info("💡 终端就绪。请在左侧输入文本后点击扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
