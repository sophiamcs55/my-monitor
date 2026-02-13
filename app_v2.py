import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎配置：修复 404 模型找不到的问题
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 显式初始化模型
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.sidebar.success("✅ API 系统连接已建立")
    except Exception as e:
        st.sidebar.error(f"❌ 引擎初始化失败: {str(e)}")
else:
    st.sidebar.error("❌ 未检测到 API Key，请检查 Secrets 配置")

# 2. 强效数据抓取与解析逻辑
def analyze_text(text):
    # 强制 AI 只返回 JSON 格式，不废话
    prompt = f"请分析以下文本的风险，只返回一个 JSON 格式，严禁包含任何说明文字。格式必须为: {{\"score\": 0, \"values\": [0,0,0,0,0], \"summary\": \"\"}}。待分析文本: {text}"
    try:
        response = model.generate_content(prompt)
        # 检查 AI 是否因为安全策略拒绝回答
        if not response.candidates or not response.candidates[0].content.parts:
            return {"score": 0, "values": [0,0,0,0,0], "summary": "AI 无法分析此内容（可能涉及安全过滤机制）。"}
            
        res_text = response.text.strip()
        # 使用正则表达式强力抓取最外层的 { ... } 块，忽略所有 Markdown 干扰
        match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if match:
            clean_json = match.group().replace("'", '"')
            return json.loads(clean_json)
        return None
    except Exception as e:
        st.sidebar.error(f"❌ 运行中错误: {str(e)}")
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
                st.error("⚠️ 扫描引擎解析失败，请检查左侧边栏诊断信息。")

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
        st.info("💡 系统就绪。请在左侧输入文本后点击扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
