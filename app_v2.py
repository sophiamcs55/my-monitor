import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json, re, io, hashlib
from datetime import datetime
from docx import Document

# 1. 顶级学术引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        # 强制性学术重定义：将 AI 设定为纯逻辑符号计算器
        sys_msg = """You are the 'Universal Scholarly Logic & Symbolic Prover'. 
        Mandatory Protocol: 
        1. Deconstruct input for Aesthetic, Philosophical, and Semantic layers.
        2. Provide BOTH Symbolic Logic (Formal proof) and Informal Logic (Rhetorical analysis).
        3. Cross-reference with Similar/Opposite/Identical historical cases.
        Output ONLY valid JSON. Be verbose and detailed."""
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 纯粹学术分析引擎已就绪")
    except Exception:
        st.sidebar.error("❌ 引擎连接受阻")

# 2. 纵深学术报告引擎 (Word)
def generate_robust_report(res):
    doc = Document()
    doc.add_heading('SharpShield Pro 全维学术纵深分析报告', 0)
    doc.add_paragraph(f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    sections = [
        ('I. 文学意境与审美解构', 'aesthetic'),
        ('II. 哲学与形而上学证明', 'philosophy'),
        ('III. 符号逻辑证明 [Symbolic]', 'symbolic_logic'),
        ('IV. 非形式逻辑批判 [Informal]', 'informal_logic'),
        ('V. 万量级案例横向对标', 'comparative'),
        ('VI. 终局批判性结论', 'conclusion')
    ]
    
    for title, key in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(res.get(key, "扫描受阻，请尝试缩短样本。"))
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 核心穿透分析 (递归降压模式)
def perform_robust_scan(t_a, t_b):
    # 引导 AI 避免过度递归，直接给出关键数据
    prompt = f"Perform deep vertical analysis between Baseline: [{t_a}] and Target: [{t_b}]. Focus on symbolic logic proofs and historical cross-referencing."
    try:
        # 提升超时限额至 120 秒，支持“百倍”深度运算
        response = model.generate_content(prompt, request_options={"timeout": 120})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
    except Exception:
        pass
    return None

# 4. 界面布局
st.set_page_config(page_title="Scholarly Logic Lab", layout="wide")
st.title("🛡️ SharpShield Pro: 纯粹学术逻辑与纵深分析实验室")

with st.sidebar:
    st.header("⚙️ 实验室状态控制")
    st.info("💡 提示：本版本已锁定纯学术模式。若扫描受阻，请将文本控制在 1000 字左右。")
    if st.button("🗑️ 复位"): st.rerun()

c1, c2 = st.columns(2)
with c1: in_a = st.text_area("🧪 基准样本 (Baseline)", height=220, placeholder="输入对比基准...")
with c2: in_b = st.text_area("🧪 目标样本 (Observation)", height=220, placeholder="输入目标学术文本...")

if st.button("🚀 启动全维度、纵深递归分析"):
    if in_a and in_b:
        with st.spinner("系统正在启动分布式计算隧道，执行全息逻辑解构..."):
            res = perform_robust_scan(in_a, in_b)
            
            if res:
                # 仪表盘展示
                dims = ['意境/审美', '哲学/本体', '符号/语义', '符号逻辑', '非形式逻辑']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=res.get('v_a', [0.5]*5), theta=dims, fill='toself', name='基准 A'))
                fig.add_trace(go.Scatterpolar(r=res.get('v_b', [0.8]*5), theta=dims, fill='toself', name='观察 B'))
                st.plotly_chart(fig, use_container_width=True)

                # 展示双轨逻辑互证 (重点保留功能)
                st.markdown("### 🧮 逻辑互证实验室 (Formal vs Informal)")
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.info("**符号逻辑证明 (Symbolic)**")
                    st.code(res.get('symbolic_logic', 'P -> Q'), language='latex')
                with lc2:
                    st.warning("**非形式逻辑批判 (Informal)**")
                    st.write(res.get('informal_logic', ''))

                # 导出 Word
                doc_bytes = generate_robust_report(res)
                st.download_button("📥 导出全周期、纵深学术研究报告 (.docx)", data=doc_bytes, file_name="Academic_Analysis_Report.docx")
            else:
                st.error("⚠️ 扫描再次受限。请分段扫描，或者在此次运行成功后，再尝试增加文本复杂度。")
    else:
        st.error("请输入样本。")
