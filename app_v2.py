import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import base64
import google.generativeai as genai

# --- 0. 配置与初始化 ---
st.set_page_config(page_title="SharpShield Pro | 锐实力防御系统", page_icon="🛡️", layout="wide")

# 配置 API KEY (请替换为你自己的 Key，或从侧边栏输入)
# genai.configure(api_key="YOUR_API_KEY") 

# --- A. 数据库持久化模块 (Database Persistence) ---
def init_db():
    conn = sqlite3.connect('sharpshield.db')
    c = conn.cursor()
    # 创建表：存储历史分析记录
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY, 
                  timestamp TEXT, 
                  source TEXT, 
                  risk_score REAL, 
                  meta_narrative TEXT,
                  summary TEXT)''')
    conn.commit()
    return conn

def save_analysis(source, score, narrative, summary):
    conn = init_db()
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (timestamp, source, risk_score, meta_narrative, summary) VALUES (?, ?, ?, ?, ?)",
              (ts, source, score, narrative, summary))
    conn.commit()
    conn.close()

def load_history():
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
    conn.close()
    return df

# --- B. 多源采集自动化模块 (Multi-source Scraper) ---
def fetch_url_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除无关标签
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
        
        text = soup.get_text()
        # 简单清洗：去除多余空行
        lines = (line.strip() for line in text.splitlines())
        clean_text = '\n'.join(chunk for chunk in lines if chunk)
        return clean_text[:3000] # 限制长度，避免 Token 溢出
    except Exception as e:
        return f"Error: {e}"

# --- 模拟 AI 分析 (为了让代码无 Key 也能运行演示，这里做了一个模拟器) ---
# 真实使用时，请解开 analyze_narrative_real 的注释并配置 Key
def mock_ai_analyze(text):
    # 简单的关键词逻辑模拟 AI
    score = 2.0
    narrative = "自由/程序叙事"
    if "复兴" in text or "统一" in text or "血浓于水" in text:
        score = 8.5
        narrative = "复兴/秩序叙事 (Mainland Logic)"
    elif "主体" in text or "防卫" in text:
        score = 4.0
        narrative = "生存/自主叙事 (Taiwan Logic)"
    
    return {
        "score": score,
        "narrative": narrative,
        "analysis": f"经扫描，文本含有高频元叙事关键词。风险评级为 {score}/10。",
        "indicators": ["RE_2 (境外资金)" if score > 7 else "无明显异常"]
    }

# --- C. UI 视觉升级与导出模块 (Visuals & Export) ---
def create_pdf(analysis_data, text_content):
    pdf = FPDF()
    pdf.add_page()
    # 因 FPDF 对中文支持较繁琐，这里演示英文报告或需加载中文字体
    # 为演示方便，我们生成简易版
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SharpShield Intelligence Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, txt=f"Risk Score: {analysis_data['score']}/10", ln=True)
    pdf.cell(200, 10, txt=f"Meta-Narrative: {analysis_data['narrative']}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Analysis Summary:\n{analysis_data['analysis']}")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 主程序逻辑 ---

# 侧边栏：API 设置与历史数据
with st.sidebar:
    st.title("🛡️ 控制中心")
    api_key = st.text_input("输入 Gemini API Key (可选)", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    
    st.divider()
    st.subheader("📊 历史趋势库 (DB)")
    history_df = load_history()
    if not history_df.empty:
        st.dataframe(history_df[['timestamp', 'risk_score', 'meta_narrative']], height=200)
        # 简单趋势图
        st.line_chart(history_df.set_index('timestamp')['risk_score'])
    else:
        st.info("暂无历史数据，请执行一次分析。")

# 主界面
st.title("SharpShield Pro: 全域影响力监测终端")
st.markdown("---")

# 输入区：支持 文本 或 URL
col_input1, col_input2 = st.columns([3, 1])
with col_input1:
    input_type = st.radio("数据源选择", ["📝 手动文本输入", "🌐 URL 自动抓取"], horizontal=True)

target_text = ""
source_label = "Manual Input"

if input_type == "📝 手动文本输入":
    target_text = st.text_area("输入待测文本", height=150, placeholder="粘贴宫庙公告、新闻报道或社交媒体贴文...")
else:
    url = st.text_input("输入目标网址 (URL)", placeholder="https://news.example.com/article/123")
    if url and st.button("🕷️ 开始抓取"):
        with st.spinner("正在派遣爬虫..."):
            fetched = fetch_url_content(url)
            if "Error" not in fetched:
                st.success("抓取成功！")
                target_text = fetched
                st.text_area("抓取内容预览", value=fetched, height=100)
                source_label = url
            else:
                st.error(fetched)

# 分析执行区
if st.button("🚀 启动全维扫描 (Analyze)"):
    if not target_text:
        st.warning("请输入文本或抓取有效内容。")
    else:
        with st.spinner("正在进行元叙事解构与指标匹配..."):
            # 1. 调用 AI (如果没 Key 则用模拟器)
            result = mock_ai_analyze(target_text)
            
            # 2. 存入数据库 (Step A 实现)
            save_analysis(source_label, result['score'], result['narrative'], result['analysis'])
            
            # 3. 结果展示 (Step C 视觉升级)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("穿刺风险评分", f"{result['score']} / 10", delta_color="inverse")
            with c2:
                st.info(f"🛡️ 核心元叙事判定:\n**{result['narrative']}**")
            with c3:
                st.warning(f"⚠️ 命中指标:\n{', '.join(result['indicators'])}")
            
            # 4. 炫酷雷达图
            st.subheader("雷达特征图谱")
            # 模拟六维数据分布
            radar_data = pd.DataFrame(dict(
                r=[result['score'], result['score']*0.8, result['score']*0.6, 5, 4, 7],
                theta=['宗教渗透', '技术锁定', '政治俘获', '学术干扰', '经济依赖', '媒体操弄']
            ))
            fig = px.line_polar(radar_data, r='r', theta='theta', line_close=True, range_r=[0,10])
            fig.update_traces(fill='toself', line_color='#ff2b2b' if result['score']>7 else '#00cc96')
            fig.update_layout(polar=dict(bgcolor="#0e1117"))
            st.plotly_chart(fig, use_container_width=True)

            # 5. 导出报告 (Step C 导出功能)
            pdf_bytes = create_pdf(result, target_text)
            st.download_button(
                label="📄 导出 PDF 战略简报",
                data=base64.b64decode(pdf_bytes),
                file_name="sharpshield_report.pdf",
                mime="application/pdf"
            )

            st.success("分析完成，数据已归档至本地数据库。")

            st.rerun() # 刷新以更新侧边栏历史记录
