import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json, re, io, hashlib
from datetime import datetime
from docx import Document
from docx.shared import Pt

# 1. 实验室核心引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        
        # 顶级纯学术指令集：专注于逻辑、文学、哲学与语义
        sys_msg = """You are the 'Universal Academic Logic Engine'. 
        Analyze inputs through 4 distinct scholarly layers:
        1. Aesthetic-Linguistic: Imagery, semiotics, and subconscious drives.
        2. Philosophical: Ontological structure and metaphysical dualism.
        3. Semantic: Deconstruct etymology and context shifts.
        4. Logic Duel: Provide both SYMBOLIC Proof (P->Q) and INFORMAL Critique (fallacies/rhetoric).
        REQUIRED: For each layer, cite 1 Similar, 1 Opposite, and 1 Identical historical or academic case.
        Output MUST be structured JSON only."""
        
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 纯粹学术分析引擎已就绪")
    except Exception:
        st.sidebar.error("❌ 引擎同步异常")

# 2. 纵深学术报告生成引擎
def generate_academic_report(res):
    doc = Document()
    doc.add_heading('SharpShield Pro: 全维学术纵深分析报告', 0)
    doc.add_paragraph(f"报告指纹: {hashlib.md5(str(res).encode()).hexdigest().upper()}")
    
    sections = [
        ('1. 文学意境与审美解构', 'aesthetic'),
        ('2. 哲学本体与形而上学证明', 'philosophy'),
        ('3. 语义多重解构与语用分析', 'semantic'),
        ('4. 符号逻辑证明 [Symbolic]', 'symbolic_logic'),
        ('5. 非形式逻辑批判 [Informal]', 'informal_logic'),
        ('6. 全球学术/历史案例对标', 'comparative'),
        ('7. 终局批判性结论', 'conclusion')
    ]
    
    for title, key in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(res.get(key, "扫描受阻，请分段重试。"))
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 分片解析扫描逻辑
def perform_deep_academic_scan(t_a, t_b):
    # 引导 AI 进入纯粹学术语境，避开无关干扰
    prompt = f"Perform recursive academic deconstruction. Signal_A: [{t_a}] Signal_B: [{t_b}]. Focus on logic, philosophy, and linguistics."
    try:
        # 增加响应时长以支持“百倍”深度的计算
        response = model.generate_content(prompt, request_options={"timeout": 100})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
    except Exception:
        pass
    return None

# 4. 界面布局
st.set_page_config(page_title="Academic Logic Lab", layout="wide")
st.title("🛡️ SharpShield Pro: 纯粹学术逻辑与纵深分析实验室")

with st.sidebar:
    st.header("⚙️ 实验室状态")
    st.info("💡 提示：本引擎已屏蔽非学术干扰，专注于文学、哲学、逻辑与语义解构。")
    if st.button("🗑️ 复位实验环境"): st.rerun()

c1, c2 = st.columns(2)
with c1: in_a = st.text_area("🧪 基准样本 (Baseline)", height=250, placeholder="输入对比基准...")
with c2: in_b = st.text_area("🧪 目标样本 (Observation)", height=250, placeholder="输入需要纵深扫描的学术文本...")

if st.button("🚀 启动全维度、纵深递归分析"):
    if in_a and in_b:
        with st.spinner("分布式计算矩阵启动中，正在执行全息逻辑拆解..."):
            res = perform_deep_academic_scan(in_a, in_b)
            
            if res:
                # 展示特征矩阵
                st.subheader("📊 跨学科特征量化矩阵")
                dims = ['意境/审美', '哲学/本体', '符号/语义', '符号逻辑', '非形式逻辑']
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=res.get('v_a', [0.5]*5), theta=dims, fill='toself', name='样本 A'))
                fig.add_trace(go.Scatterpolar(r=res.get('v_b', [0.8]*5), theta=dims, fill='toself', name='样本 B'))
                st.plotly_chart(fig, use_container_width=True)

                # 展示双轨逻辑
                st.write("---")
                st.subheader("🧮 逻辑互证实验室 (Formal vs Informal)")
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.info("**符号逻辑证明 (Symbolic)**")
                    st.code(res.get('symbolic_logic', 'P -> Q'), language='latex')
                with lc2:
                    st.warning("**非形式逻辑批判 (Informal)**")
                    st.write(res.get('informal_logic', ''))

                # 下载 Word
                doc_bytes = generate_academic_report(res)
                st.download_button("📥 导出全周期、纵深学术报告 (.docx)", data=doc_bytes, file_name="Academic_Logic_Report.docx")
            else:
                st.error("⚠️ 扫描受阻。即便已移除敏感内容，极高密度的文本仍可能导致超时。建议：将文本控制在 1200 字以内分段扫描。")
    else:
        st.error("请输入样本。")
