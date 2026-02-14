import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json, re, io, hashlib
from datetime import datetime
from docx import Document
from docx.shared import Pt

# 1. 顶级学术引擎：注入形式逻辑与万量级知识库
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        # 终极学术指令：要求显性推理与广泛互证
        sys_msg = """You are a Senior Academic Logician and Philologist. 
        DECONSTRUCTION PROTOCOL:
        1. Aesthetic-Semantic: Map imagery to standard philosophical categories.
        2. Formal Symbolic Proof: Show STEP-BY-STEP deduction from Premises to Conclusion.
        3. Informal Rhetoric: Identify fallacies and persuasive structures.
        4. Global Intertextuality: Cite specific Similar, Opposite, and Identical cases from world literature/philosophy.
        Output MUST be structured JSON. Be extremely verbose and rigorous."""
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 全球学术纵深分析引擎已就绪")
    except Exception:
        st.sidebar.error("❌ 引擎同步异常")

# 2. 纵深学术研究报告引擎 (Word)
def generate_mega_report(res):
    doc = Document()
    doc.add_heading('SharpShield Pro: 全球学术纵深与逻辑互证报告', 0)
    doc.add_paragraph(f"生成日期: {datetime.now()} | 唯一指纹: {hashlib.md5(str(res).encode()).hexdigest().upper()}")
    
    sections = [
        ('I. 文学意境与符号鉴赏 (Imagery & Semiotics)', 'aesthetic'),
        ('II. 哲学本体与逻辑证明过程 [Symbolic Proof]', 'symbolic_logic'),
        ('III. 修辞解构与非形式批判 [Informal Analysis]', 'informal_logic'),
        ('IV. 全球史料旁征博引 (Global Intertextuality)', 'comparative'),
        ('V. 终局批判性综述 (Scholarly Assessment)', 'conclusion')
    ]
    for title, key in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(res.get(key, "该维度扫描密度受阻。"))
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 核心穿透分析
def perform_mega_scan(t_a, t_b):
    # 强制增加上下文密度，引导 AI 进行长程推理
    prompt = f"Perform high-intensity scholarly deconstruction. Base: [{t_a[:1200]}] Target: [{t_b[:1200]}]. Provide explicit formal proofs and historical case references."
    try:
        response = model.generate_content(prompt, request_options={"timeout": 120})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
    except Exception:
        pass
    return None

# 4. 界面布局
st.set_page_config(page_title="Academic Logic Lab", layout="wide")
st.title("🛡️ SharpShield Pro: 全球学术逻辑解构实验室")

with st.sidebar:
    st.header("⚙️ 终端控制台")
    st.info("💡 提示：本版本已锁定【形式逻辑证明】与【全球案例对垒】模式。")
    if st.button("🗑️ 复位实验室"): st.rerun()

c1, c2 = st.columns(2)
with c1: in_a = st.text_area("🧪 基准样本 (Baseline)", height=250)
with c2: in_b = st.text_area("🧪 目标样本 (Target)", height=250)

if st.button("🚀 启动全球多维、逻辑穿透比对分析"):
    if in_a and in_b:
        with st.spinner("分布式推理启动中，正在执行形式化证明与史料检索..."):
            res = perform_mega_scan(in_a, in_b)
            if res:
                # 展示特征矩阵
                dims = ['意境/审美', '哲学/本体', '符号/语义', '符号证明', '非形式逻辑']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=res.get('v_a'), theta=dims, fill='toself', name='A'))
                fig.add_trace(go.Scatterpolar(r=res.get('v_b'), theta=dims, fill='toself', name='B'))
                st.plotly_chart(fig, use_container_width=True)

                # 展示双轨逻辑互证实验室
                st.markdown("### 🧮 逻辑互证实验室 (Formal vs Informal)")
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.info("**形式化符号逻辑证明过程**")
                    st.code(res.get('symbolic_logic'), language='latex')
                with lc2:
                    st.warning("**非形式修辞批判与解构**")
                    st.write(res.get('informal_logic'))

                # 最终定性展示
                st.write("---")
                st.success(f"**终局学术综述：** {res.get('conclusion', '')}")
                
                # 下载 Word
                doc_bytes = generate_mega_report(res)
                st.download_button("📥 导出全周期、纵深学术研究报告 (.docx)", data=doc_bytes, file_name="Global_Analysis.docx")
            else:
                st.error("⚠️ 云端协议熔断。建议分段进行扫描，以换取更高的推理深度。")
    else: st.error("请输入样本。")
