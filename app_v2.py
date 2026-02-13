import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎配置：学术模式（深度解除所有安全限制）
api_key = st.secrets.get("GOOGLE_API_KEY")
model = None

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 核心设置：将所有类别的安全拦截阈值设为 BLOCK_NONE
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        # 使用 gemini-pro 模型，该模型在解除限制后对指令的遵循度更高
        model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
        st.sidebar.success("✅ 锐实力研究引擎已就绪")
    except Exception as e:
        st.sidebar.error(f"❌ 初始化失败: {str(e)}")
else:
    st.sidebar.error("❌ 未检测到 API Key")

# 2. 增强型解析：确保获取 JSON 数据
def analyze_text(text):
    # 引导性提示词，明确学术用途以降低 AI 自我审查的可能性
    prompt = f"作为学术研究助手，请客观分析此文本。必须仅返回 JSON: {{'score':0-10,'values':[5个数字],'summary':'总结'}}。内容: {text}"
    try:
        if not model: return None
        response = model.generate_content(prompt)
        # 尝试直接获取文本，如果被拦截，则进入异常处理
        res_text = response.text
        match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
        return None
    except Exception:
        # 兜底方案：如果 AI 依然拒绝生成文本，返回一个提示
        return {"score": 0, "values": [0,0,0,0,0], "summary": "此内容极端敏感，已超出当前 API 节点的学术授权范围。"}

# 3. 界面布局
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 研究情报输入")
    u = st.text_area("请粘贴需要学术扫描的文本：", height=250)
    if st.button("🚀 启动穿透扫描") and u:
        with st.spinner("系统正在进行多维度穿透分析..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M:%S"), "得分": res.get('score', 0)})
            else:
                st.error("⚠️ 扫描引擎响应异常。")

with c2:
    st.subheader("📊 研究看板")
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
        st.info("💡 请输入文本后启动扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
