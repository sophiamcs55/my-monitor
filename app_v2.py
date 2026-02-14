import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json, re, io, hashlib
from datetime import datetime
from docx import Document

# 1. 实验室顶级研究引擎配置 - 释放智能自主性
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        
        # 释放智能的顶级指令：要求 AI 像独立学者一样进行深度发现
        sys_msg = """You are a self-directed Global Academic Researcher. 
        Your task is NOT to fill templates, but to DISCOVER deep logical conflicts.
        STEP-BY-STEP REASONING REQUIRED:
        1. Contextualize the hidden paradigms.
        2. Execute complex symbolic proofs using Predicate/Modal logic.
        3. Identify 3 specific historical cases (Similar, Opposite, Identical) with detailed explanations of 'Why'.
        Output strictly detailed JSON. Be critical and intellectual."""
        
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 智能自主分析引擎已激活")
    except Exception:
        st.sidebar.error("❌ 引擎连接异常")

# 2. 纵深学术报告引擎 (增加智能动态内容)
def generate_intellectual_report(res):
    doc = Document()
    doc.add_heading('SharpShield Pro: 全球智能学术自主研究报告', 0)
    doc.add_paragraph(f"生成日期: {datetime.now()} | 研究指纹: {hashlib.md5(str(res).encode()).hexdigest().upper()}")
    
    sections = [
        ('I. 动态语境与范式解构 (Paradigm Analysis)', 'aesthetic'),
        ('II. 复杂形式逻辑证明 (Advanced Symbolic Proof)', 'symbolic_logic'),
        ('III. 全球史料深度互证 (Intellectual Intertextuality)', 'comparative'),
        ('IV. 逻辑漏洞与修辞陷阱批判 (Rhetorical Critique)', 'informal_logic'),
        ('V. 终局批判性综述 (Final Scholarly Assessment)', 'conclusion')
    ]
    for title, key in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(res.get(key, "该维度扫描由于逻辑复杂度过高，建议分段进行。"))
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 核心穿透分析 (解除字数限制压力)
def perform_autonomous_scan(t_a, t_b):
    prompt = f"Perform deep autonomous scholarly comparison. A: [{t_a[:1500]}] B: [{t_b[:1500]}]. Focus on revealing hidden logical contradictions and citing unique historical precedents."
    try:
        # 给 AI 足够的时间去“思考”
        response = model.generate_content(prompt, request_options={"timeout": 140})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
    except Exception:
        pass
    return None

# 4. 界面布局
st.set_page_config(page_title="Autonomous Scholar Lab", layout="wide")
st.title("🛡️ SharpShield Pro: 全球学术智能自主实验室")

with st.sidebar:
    st.header("⚙️ 终端控制")
    st.info("💡 终极功能：思维链递归 + 全球史料自主互证。")
    if st.button("🗑️ 复位实验"): st.rerun()

c1, c2 = st.columns(2)
with c1: in_a = st.text_area("🧪 基准样本 (Baseline)", height=250, placeholder="输入文本...")
with c2: in_b = st.text_area("🧪 目标样本 (Target)", height=250, placeholder="输入文本...")

if st.button("🚀 启动全球多维智能自主分析"):
    if in_a and in_b:
        with st.spinner("系统正在进行思维链建模与全球史料对垒..."):
            res = perform_autonomous_scan(in_a, in_b)
            
            if res:
                # 仪表盘展示
                dims = ['意境/审美', '哲学/本体', '符号/语义', '形式逻辑', '批判性思维']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=res.get('v_a', [0.5]*5), theta=dims, fill='toself', name='A'))
                fig.add_trace(go.Scatterpolar(r=res.get('v_b', [0.8]*5), theta=dims, fill='toself', name='B'))
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 🧮 智能逻辑互证专栏 (Symbolic vs Informal)")
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.info("**高级符号逻辑证明链**")
                    st.code(res.get('symbolic_logic'), language='latex')
                with lc2:
                    st.warning("**自主史料旁征博引**")
                    st.write(res.get('comparative'))

                st.success(f"**终局深度学术综述：** {res.get('conclusion', '')}")
                
                # 导出按钮
                doc_bytes = generate_intellectual_report(res)
                st.download_button("📥 导出全球智能研究报告 (.docx)", data=doc_bytes, file_name="Autonomous_Analysis.docx")
            else:
                st.error("⚠️ 协议拦截。检测到高危语义或超时，请分段进行扫描。")
    else:
        st.error("请输入比对样本。")
