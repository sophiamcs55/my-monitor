import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

Setup
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key and api_key.startswith("AIza"):
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
else:
st.sidebar.error("API Key Error")

Logic
def analyze_text(text):
prompt = f"Analyze risk, return JSON: {{'score':0-10, 'label':'type', 'indicator':'index', 'values':[5 numbers], 'summary':'text'}}. Content: {text}"
try:
response = model.generate_content(prompt)
t = response.text.strip().replace('json', '').replace('', '').strip()
return json.loads(t)
except:
return None

UI
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro")

if 'history' not in st.session_state:
st.session_state['history'] = []

col1, col2 = st.columns([1, 1.2])

with col1:
user_input = st.text_area("Input Text", height=250)
if st.button("Scan") and user_input:
with st.spinner("Analyzing..."):
res = analyze_text(user_input)
if res:
st.session_state['result'] = res
st.session_state['history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Score": res['score']})

with col2:
if 'result' in st.session_state:
res = st.session_state['result']
st.metric("Risk Score", f"{res['score']} / 10")
df = pd.DataFrame(dict(r=res['values'], theta=['Religion','Tech','Politics','Econ','Media']))
fig = px.line_polar(df, r='r', theta='theta', line_close=True)
st.plotly_chart(fig, use_container_width=True)
st.success(res['summary'])
else:
st.info("Awaiting scan...")

with st.sidebar:
st.write("### History")
if st.session_state['history']:
st.table(pd.DataFrame(st.session_state['history']))
