import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json
import re
import hashlib
import io
from datetime import datetime
from fpdf import FPDF
from docx import Document

# 1. 引擎核心配置
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        sys_msg = "You are a master academic logician. Output MUST be in JSON format with keys: v_a, v_b, context, logic_chain, paradox, critique, conclusion."
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings, system_instruction=sys_msg)
        st.sidebar.success("✅ 逻辑导出系统已就绪")
    except Exception:
        st.sidebar.error("❌ 引擎连接异常")

# 2. 导出功能函数
def generate_docx(res):
    doc = Document()
    doc.add_heading('SharpShield 学术逻辑分析报告', 0)
    doc.add_paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    doc.add_heading('1. 背景与战略穿透', level=1)
    doc.add_paragraph(res.get('context', ''))
    
    doc.add_heading('2. 符号逻辑链', level=1)
    doc.add_paragraph(res.get('logic_chain', ''))
    
    doc.add_heading('3. 逻辑悖论识别', level=1)
    doc.add_paragraph(res.get('paradox', ''))
    
    doc.add_heading('4. 终局学术定性', level=1)
    doc.add_paragraph(res.get('conclusion', ''))
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def generate_pdf(res):
    pdf = FPDF()
    pdf.add_page()
    # 注意：标准FPDF对中文字符支持较复杂，此处使用常用字体替代，建议报告以Word为主
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SharpShield Academic Logic Report", ln=1, align='C')
    pdf.multi_cell(0, 10, txt=f"Context: {res.get('context', '')}")
    pdf.multi_cell(0, 10, txt=f"Logic Chain: {res.get('logic_chain', '')}")
    pdf.multi_cell(0, 10, txt=f"Conclusion: {res.get('conclusion', '')}")
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# 3. 深度分析逻辑 (略作优化以支持更稳定的 JSON)
def perform_deep_scan(text_a, text_b):
    try:
        prompt = f"Compare A: [{text_a}] and B: [{text_b}]. Perform a formal logic duel and cycle critique."
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match: return json.loads(match.group().replace("'", '"'))
    except: pass
    return {"v_a":[0.5]*5, "v_b":[0.7]*5, "context":"系统自动进入影子模式...", "logic_chain":"P->Q", "paradox":"无", "critique":"略", "conclusion":"解析超时，建议缩短样本。"}

# 4. 界面布局
st.set_page_config(page_title="Logic Export Lab", layout="wide")
st.title("🛡️ SharpShield Pro：学术穿透分析与一键导出实验室")

c1, c2 = st.columns(2)
with c1: input_a = st.text_area("🧪 样本 A (基准)", height=200)
with c2: input_b = st.text_area("🧪 样本 B (穿透组)", height=200)

if st.button("🚀 启动全周期逻辑扫描"):
    if input_a and input_b:
        with st.spinner("深度推理中..."):
            res = perform_deep_scan(input_a, input_b)
            st.session_state['last_res'] = res
            
            # 显示图表
            dims = ['认知框架', '分发韧性', '协同矩阵', '经济杠杆', '符号资本']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=res.get('v_a'), theta=dims, fill='toself', name='基准 A'))
            fig.add_trace(go.Scatterpolar(r=res.get('v_b'), theta=dims, fill='toself', name='观察 B'))
            st.plotly_chart(fig, use_container_width=True)

            # 显示结论
            st.markdown("### 🏛️ 逻辑分析概览")
            st.info(f"**背景穿透：** {res.get('context')}")
            st.success(f"**最终结论：** {res.get('conclusion')}")
            
            # 导出区域
            st.write("---")
            st.subheader("📂 导出研究报告")
            col_ex1, col_ex2 = st.columns(2)
            
            with col_ex1:
                docx_data = generate_docx(res)
                st.download_button(
                    label="📥 下载 Word 格式报告 (.docx)",
                    data=docx_data,
                    file_name=f"SharpShield_Report_{datetime.now().strftime('%m%d')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            with col_ex2:
                # PDF 导出暂作基础实现
                pdf_data = generate_pdf(res)
                st.download_button(
                    label="📥 下载 PDF 格式报告 (基础版)",
                    data=pdf_data,
                    file_name=f"SharpShield_Report_{datetime.now().strftime('%m%d')}.pdf",
                    mime="application/pdf"
                )
    else:
        st.error("请先输入比对样本。")
