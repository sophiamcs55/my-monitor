import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

api_key = st.secrets.get("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_text(text):
p = f"Analyze: {text}. Return JSON: {{'score':0, 'values':[0,0,0,0,0], 'summary':''}}"
    try:
response = model.generate_content(p)
t = response.text.strip()
    if "`json" in t: t = t.split("`json")[1].split("`")[0] elif "`" in t:
t = t.split("`")[1].split("`")[0]
return json.loads(t.strip())
except:
return None

st.set_page_config(page_title="SharpShield", layout="wide")
st.title("SharpShield Pro")

    if 'history' not in st.session_state:
st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

    with c1:
u = st.text_area("Input Text", height=250)
    if st.button("Scan") and u:
    with st.spinner("Scanning..."):
res = analyze_text(u)
    if res:
st.session_state['result'] = res
st.session_state['history'].insert(0, {"Time": datetime.now().strftime("%H:%M"), "Score": res.get('score', 0)})

    with c2:
    if 'result' in st.session_state:
res = st.session_state['result']
st.metric("Risk Score", res.get('score', 0))
df = pd.DataFrame(dict(
r=res.get('values', [0,0,0,0,0]),
theta=['Religion','Tech','Politics','Economy','Media']
))
fig = px.line_polar(df, r='r', theta='theta', line_close=True)
st.plotly_chart(fig, use_container_width=True)
st.success(res.get('summary', ''))
    else:
st.info("Awaiting scan results...")

    with st.sidebar:
st.write("### History")
    if st.session_state['history']:
st.table(pd.DataFrame(st.session_state['history']))


