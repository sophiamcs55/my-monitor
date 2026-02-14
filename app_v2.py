import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json, re, io, hashlib
import numpy as np
from datetime import datetime
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer

# 1. 实验室顶级研究引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        # 终极学术指令：强制 AI 成为一个具备自主发现能力的专家
        sys_msg = """You are a Universal Scholarly Analyzer. Your core mission is to DISCOVER hidden logical paradoxes between Input A and B. 
        MANDATORY PROTOCOL:
        1. NO generic templates. Analyze the SPECIFIC words provided.
        2. Perform Formal Symbolic Logic deduction and identify Rhetorical Fallacies.
        3. Cite EXACT historical cases (Similar, Opposite, Identical) that relate to the text's specific ontology.
        Output MUST be a dense, academic JSON."""
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 逻辑破壁引擎已激活")
    except Exception:
        st.sidebar.error("❌ 引擎同步受限")

# 2. 深度学术报告生成 (增加史料对垒密度)
def generate_advanced_report(res):
    doc = Document()
    doc.add_heading('SharpShield Pro: 全球智能学术破壁分析报告', 0)
    sections = [
        ('I. 深度意境与审美穿透 (Aesthetic Deconstruction)', 'aesthetic'),
        ('II. 形式化逻辑证明与演算 (Formal Logic Proof)', 'symbolic_logic'),
        ('III. 动态史料互证与案例库对比 (Intertextual Matrix)', 'comparative'),
        ('IV. 话语陷阱与逻辑谬误批判 (Fallacy Detection)', 'informal_logic'),
        ('V. 终局学术定性综述 (Final Scholarly Conclusion)', 'conclusion')
    ]
    for title, key in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(res.get(key, "检测到高维解析阻塞。"))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 核心算法：差值敏感化分析
def perform_breakthrough_scan(t_a, t_b):
    # 本地先算一遍差异，强迫 AI 面对现实
    tfidf = TfidfVectorizer().fit_transform([t_a, t_b])
    sim = (tfidf * tfidf.T).toarray()[0,1]
    
    prompt = f"Detect differences between Signal_A and Signal_B. Current Similarity Score: {sim:.2f}. If score is low, explain the conflict deeply. If high, explain the resonance. Focus on Symbolic Logic and Global Cases."
    try:
        response = model.generate_content(prompt, request_options={"timeout": 140})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match: return json.loads(match.group().replace("'", '"'))
    except: pass
    return None

# 4. 界面
st.set_page_config(page_title="Logic Breakthrough Lab", layout="wide")
st.title("🛡️ SharpShield Pro: 全球学术智能破壁实验室")

with st.sidebar:
    st.header("⚙️ 实验室状态")
    st.info("💡 终极功能：本地语义敏感化 + 史料动态互证。")
    if st.button("🗑️ 复位实验室"): st.rerun()

c1, c2 = st.columns(2)
with c1: in_a = st.text_area("🧪 基准样本 (A)", height=250)
with c2: in_b = st.text_area("🧪 目标样本 (B)", height=250)

if st.button("🚀 启动全维度、破壁式、智能自主分析"):
    if in_a and in_b:
        with st.spinner("系统正在递归解构语义并执行史料库对垒..."):
            res = perform_breakthrough_scan(in_a, in_b)
            if res:
                # 仪表盘
                dims = ['意境审美', '哲学本体', '符号语义', '符号证明', '批判思维']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=res.get('v_a', [0.5]*5), theta=dims, fill='toself', name='A'))
                fig.add_trace(go.Scatterpolar(r=res.get('v_b', [0.8]*5), theta=dims, fill='toself', name='B'))
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 🧮 全息逻辑互证 (Symbolic vs Informal)")
                l1, l2 = st.columns(2)
                with l1:
                    st.info("**三段式/谓词逻辑证明**")
                    st.code(res.get('symbolic_logic'), language='latex')
                with l2:
                    st.warning("**自主史料旁征博引**")
                    st.write(res.get('comparative'))

                st.success(f"**终局深度学术结论：** {res.get('conclusion')}")
                
                doc_bytes = generate_advanced_report(res)
                st.download_button("📥 导出全周期、破壁学术分析报告 (.docx)", data=doc_bytes, file_name="Academic_Breakthrough_Report.docx")
            else:
                st.error("⚠️ 云端熔断。建议分段（每段 600 字）输入以突破限制。")
    else: st.error("请输入样本。")
