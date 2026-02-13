import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

核心引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key and api_key.startswith("AIza"):
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
else:
st.sidebar.error("Key Error: Please check Secrets")

AI 分析核心逻辑
def analyze_text(text):
prompt = f"分析该文本的风险，以JSON返回: {{'score':0-10, 'label':'标签', 'indicator':'指标', 'values':[5个数值], 'summary':'结论'}}。文本内容: {text}"
try:
response = model.generate_content(prompt)
t = response.text.strip().replace('json', '').replace('', '').strip()
return json.loads(t)
except:
return None

网页界面布局
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
st.session_state['history'] = []

col1, col2 = st.columns([1, 1.2])

with col1:
st.subheader("📝 情报输入")
user_input = st.text_area("在此粘贴文本", height=250)
if st.button("🚀 启动扫描") and user_input:
with st.spinner("AI 正在深度解析..."):
res = analyze_text(user_input)
if res:
st.session_state['result'] = res
st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M:%S"), "得分": res['score']})

with col2:
st.subheader("📊 分析看板")
if 'result' in st.session_state:
res = st.session_state['result']
st.metric("风险评分", f"{res['score']} / 10")
df = pd.DataFrame(dict(r=res['values'], theta=['宗教','技术','政治','经济','媒体']))
fig = px.line_polar(df, r='r', theta='theta', line_close=True)
st.plotly_chart(fig, use_container_width=True)
st.success(res['summary'])
else:
st.info("💡 终端已就绪。请在左侧输入数据后开启扫描。")

with st.sidebar:
st.write("### 📜 历史记录")
if st.session_state['history']:
st.table(pd.DataFrame(st.session_state['history']))
