import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

--- 1. 核心配置：连接 AI 大脑 ---
从 Streamlit Secrets 自动读取 API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if api_key and api_key.startswith("AIza"):
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
else:
st.sidebar.error("❌ 未检测到有效的 API Key，请检查 Secrets 配置。")

--- 2. 深度分析函数 ---
def analyze_text(text):
prompt = f"""
你是一个顶级情报分析专家。请对以下文本进行分析，并严格以 JSON 格式返回结果（不要包含任何额外文字）：
{{
"score": 0-10之间的风险分,
"label": "叙事类型标签",
"indicator": "命中指标简述",
"values": [5个0-10的数值，分别对应：宗教渗透、技术锁定、政治俘获、经济依赖、媒体操纵],
"summary": "100字以内的专业分析结论"
}}
待测文本："{text}"
"""
try:
response = model.generate_content(prompt)
# 清洗结果，确保是纯 JSON
clean_text = response.text.strip().replace('json', '').replace('', '')
return json.loads(clean_text)
except Exception as e:
return f"Error: {str(e)}"

--- 3. 界面布局设计 ---
st.set_page_config(page_title="SharpShield Pro v2.1", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
st.session_state['history'] = []

col1, col2 = st.columns([1, 1.2])

with col1:
st.subheader("📝 情报输入终端")
user_input = st.text_area("在此粘贴待测文本...", height=250, placeholder="AI 将扫描文本中的叙事陷阱...")

with col2:
st.subheader("📊 实时分析看板")
if 'result' in st.session_state:
res = st.session_state['result']
c1, c2, c3 = st.columns(3)
c1.metric("风险评分", f"{res['score']} / 10")
c2.info(f"核心叙事：{res['label']}")
c3.warning(f"命中指标：{res['indicator']}")

with st.sidebar:
st.markdown("### 🗄️ 历史趋势库")
if st.session_state['history']:
st.table(pd.DataFrame(st.session_state['history']))
st.caption
