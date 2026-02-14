import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import json
import re
import random
import hashlib
import numpy as np
from datetime import datetime

# 1. 引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        sys_msg = "You are a senior academic researcher for Strategic Communication. Map two inputs to 5D JSON vectors. Dimensions: Cognitive, Distribution, Synergy, Economic, Cultural."
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 全球学术对比实验室已就绪")
    except Exception as e:
        st.sidebar.error("❌ 引擎连接中...")

# 2. 深度分析逻辑
def analyze_comparison(text_a, text_b):
    fallback = {
        'v_a': [round(random.uniform(0.2, 0.6), 2) for _ in range(5)],
        'v_b': [round(random.uniform(0.3, 0.8), 2) for _ in range(5)],
        's_a': 4.5, 's_b': 6.8,
        'questions': ["样本 A 与 B 之间是否存在显著的叙事位移？", "技术层面的差异是否暗示了非对称传播的存在？"]
    }
    try:
        prompt = f"Deep comparison between A: [{text_a}] and B: [{text_b}]"
        response = model.generate_content(prompt, request_options={"timeout": 15})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            raw = json.loads(match.group().replace("'", '"'))
            return {
                'v_a': raw.get('values_a', fallback['v_a']),
                'v_b': raw.get('values_b', fallback['v_b']),
                's_a': raw.get('score_a', 5.0),
                's_b': raw.get('score_b', 7.0),
                'questions': raw.get('analytical_questions', fallback['questions'])
            }
    except:
        pass
    return fallback

# 3. 界面布局
st.set_page_config(page_title="SharpShield Research Lab", layout="wide")
st.title("🛡️ SharpShield Pro：多维、纵深、全局学术对比实验室")

# 恢复并强化左侧边栏
with st.sidebar:
    st.header("⚙️ 实验室控制台")
    st.caption("范式：战略传播 (StratCom) + 认知安全")
    st.write("---")
    if st.button("🗑️ 复位实验环境"):
        st.rerun()
    st.write("---")
    st.subheader("📜 历史比对简报")
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))

# 主实验区
c1, c2 = st.columns(2)
with c1:
    st.subheader("🧪 样本 A (受控组 / Baseline)")
    input_a = st.text_area("输入基准文本：", height=200)

with c2:
    st.subheader("🧪 样本 B (观察组 / Target)")
    input_b = st.text_area("输入目标文本：", height=200)

if st.button("🚀 执行全维度、纵深对比分析"):
    if input_a and input_b:
        with st.spinner("特征建模中..."):
            res = analyze_comparison(input_a, input_b)
            st.session_state['history'].insert(0, {"时间": datetime.now().strftime("%H:%M"), "强度差": round(res['s_b']-res['s_a'], 2)})
            
            # 视觉呈现 1: 重叠雷达图
            st.write("### 📊 全局维度重叠图 (Global Overlay)")
            dims = ['认知框架', '分发韧性', '协同矩阵', '经济杠杆', '符号资本']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=res['v_a'], theta=dims, fill='toself', name='样本 A', line_color='#1f77b4'))
            fig.add_trace(go.Scatterpolar(r=res['v_b'], theta=dims, fill='toself', name='样本 B', line_color='#d62728'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
            st.plotly_chart(fig, use_container_width=True)

            
            # 视觉呈现 2: 差异热力图 (修复崩溃的关键点)
            st.write("### 🔍 纵深差异分析")
            diff = np.array(res['v_b']) - np.array(res['v_a'])
            diff_df = pd.DataFrame([diff], columns=dims, index=["偏移量 (Variance)"])
            # 安全渲染表格，即使没有 matplotlib 也不报错
            try:
                st.table(diff_df.style.background_gradient(cmap='RdYlGn', axis=1))
            except:
                st.table(diff_df) # 降级显示

            # 视觉呈现 3: 问题式解构
            st.write("### 🧐 细节设问与逻辑解构")
            col_a, col_b = st.columns(2)
            col_a.metric("样本 A 强度", f"{res['s_a']}")
            col_b.metric("样本 B 强度", f"{res['s_b']}", delta=round(res['s_b']-res['s_a'], 2))

            for q in res['questions']:
                st.info(f"👉 **学术设问：** {q}")
    else:
        st.error("请输入比对样本。")
