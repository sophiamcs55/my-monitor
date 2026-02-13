import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime

# 1. Setup API
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.error("API Key Missing")

# 2. Logic to Get AI Data
def analyze_text(text):
    prompt = f"Analyze risk: {text}. Return ONLY JSON: {{'score':0-10, 'values':[5 numbers], 'summary':'...'}}"
    try:
        response = model.generate_content(prompt)
        t = response.text.strip()
        # Clean Markdown characters
        if "```json" in t:
            t = t.split("```json")[1].split("```")[0]
        elif "```" in t:
            t = t.split("```")[1].split("```")[0]
        return json.loads(t.strip())
    except:
        return None

# 3. UI Interface
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    u = st.text_area("Input Text", height=250)
    if st.button("Scan") and u:
        with st.spinner("Analyzing..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {"Time": datetime.now().strftime("%H:%M"), "Score": res.get('score', 0)})
            else:
                st.error("AI Error: Failed to parse data.")

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
        st.success(res.get('summary', 'Scan Complete'))
    else:
        st.info("Awaiting scan results...")

with st.sidebar:
    st.write("### History")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
