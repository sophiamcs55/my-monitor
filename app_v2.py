import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json
import re
import io
from datetime import datetime
from docx import Document
from docx.shared import Pt

# 1. 顶级研究引擎配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        
        # 终极学术指令：要求大跨度分析与双轨证明
        sys_msg = """You are a Universal Academic Intelligence.
        Analyze the input through 4 Lenses:
        1. Literary/Aesthetic (Imagery, style, emotional resonance)
        2. Philosophical/Metaphysical (Ontology, ethics, core beliefs)
        3. Semantic/Linguistic (Etymology, word play, context shifts)
        4. Logical Duel: Provide BOTH Symbolic Logic (P->Q) and Informal Logic (fallacies, rhetoric).
        REQUIRED: For each point, provide a Similar, Opposite, and Identical case from history/literature.
        Output MUST be structured JSON."""
        
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 全学科分析隧道已激活")
    except Exception:
        st.sidebar.error("❌ 引擎连接受限")

# 2. 深度学术报告生成器 (Word)
def generate_mega_report(res):
    doc = Document()
    doc.add_heading('SharpShield Pro：全学科纵深分析与互证报告', 0)
    doc.add_paragraph(f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    sections = [
        ('1. 文学与意境审美 (Aesthetic Analysis)', 'aesthetic'),
        ('2. 哲学与形而上学解构 (Metaphysical Analysis)', 'philosophy'),
        ('3. 语义多重解构 (Semantic Analysis)', 'semantic'),
        ('4. 形式逻辑证明 [Symbolic]', 'symbolic_logic'),
        ('5. 非形式逻辑分析 [Informal]', 'informal_logic'),
        ('6. 万量级案例对标 (Comparative Cases)', 'comparative'),
        ('7. 终局批判性结论 (Final Assessment)', 'conclusion')
    ]
    
    for title, key in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(res.get(key, "数据在穿透过程中丢失"))
        
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 核心穿透逻辑
def perform_mega_scan(t_a, t_b):
    prompt = f"Perform deep vertical and horizontal comparison. A: [{t_a}] B: [{t_b}]. Provide cross-referenced logic and extensive case citations."
    try:
        response = model.generate_content(prompt, request_options={"timeout": 90})
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group().replace("'", '"'))
    except:
        pass
    return None

# 4. 用户界面布局
st.set_page_config(page_title="SharpShield Mega Lab", layout="wide")
st.title("🛡️ SharpShield Pro：全球多维学术与逻辑比对实验室")

with st.sidebar:
    st.header("⚙️ 实验室配置")
    st.info("💡 终极功能已上线：系统现已支持双轨逻辑证明与历史案例自动对标。")
    if st.button("🗑️ 复位"): st.rerun()

c1, c2 = st.columns(2)
with c1: in_a = st.text_area("🧪 基准样本 (A)", height=200, placeholder="输入对比基准...")
with c2: in_b = st.text_area("🧪 目标样本 (B)", height=200, placeholder="输入需要纵深扫描的文本...")

if st.button("🚀 启动全维度、万量级对比扫描"):
    if in_a and in_b:
        with st.spinner("正在进行跨学科穿透建模，请稍候（任务强度：高）..."):
            res = perform_mega_scan(in_a, in_b)
            
            if res:
                # 展示雷达矩阵
                st.subheader("📊 跨学科量化矩阵")
                dims = ['意境/审美', '哲学/本体', '语义/语用', '形式逻辑', '批判性思维']
                v_a = res.get('v_a', [0.5]*5)
                v_b = res.get('v_b', [0.8]*5)
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=v_a, theta=dims, fill='toself', name='样本 A'))
                fig.add_trace(go.Scatterpolar(r=v_b, theta=dims, fill='toself', name='样本 B'))
                st.plotly_chart(fig, use_container_width=True)

                
                # 双轨逻辑展示
                st.markdown("### 🧮 逻辑互证实验室")
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.info("**符号逻辑 (Symbolic)**")
                    st.code(res.get('symbolic_logic', ''), language='latex')
                with lc2:
                    st.warning("**非形式逻辑 (Informal)**")
                    st.write(res.get('informal_logic', ''))

                # 展示深度内容
                st.write("---")
                st.markdown(f"#### 🏛️ 终局批判报告")
                st.success(res.get('conclusion', ''))
                
                # 导出 Word
                docx_data = generate_mega_report(res)
                st.download_button("📥 导出全维纵深分析报告 (.docx)", data=docx_data, file_name="SharpShield_Mega_Report.docx")
            else:
                st.error("⚠️ 扫描强度过大导致解析受阻，建议分段进行。")
