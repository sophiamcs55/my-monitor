import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re
from datetime import datetime

# 1. 引擎配置与自检
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # 测试 API 是否可用
        st.sidebar.success("✅ API 连接正常")
    except Exception as e:
        st.sidebar.error(f"❌ API 配置失败: {str(e)}")
else:
    st.sidebar.error("❌ 未检测到 API Key，请检查 Secrets")

# 2. 强力数据抓取逻辑
def analyze_text(text):
    prompt = f"分析该文本的风险，只返回一个纯 JSON 格式。格式: {{\"score\": 0, \"values\": [0,0,0,0,0], \"summary\": \"\"}}。内容: {text}"
    try:
        response = model.generate_content(prompt)
        # 检查是否被安全拦截
        if not response.parts:
            st.sidebar.warning("⚠️ AI 拒绝回答：内容可能触发了安全过滤")
            return None
        
        res_text = response.text.strip()
        match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if match:
            # 自动修复 AI 返回的单引号问题
            clean_json = match.group().replace("'", '"')
            return json.loads(clean_json)
        return None
    except Exception as e:
        st.sidebar.error(f"❌ 解析错误: {str(e)}")
        return None

# 3. 界面布局
st.set_page_config(page_title="SharpShield Pro", layout="wide")
st.title("🛡️ SharpShield Pro 锐实力防御系统")

if 'history' not in st.session_state:
    st.session_state['history'] = []

c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("📝 情报输入")
    u = st.text_area("在此粘贴文本：", height=250, placeholder="请输入需要分析的文字...")
    if st.button("🚀 启动扫描") and u:
        with st.spinner("AI 正在解析多维度情报..."):
            res = analyze_text(u)
            if res:
                st.session_state['result'] = res
                st.session_state['history'].insert(0, {
                    "时间": datetime.now().strftime("%H:%M:%S"), 
                    "评分": res.get('score', 0)
                })
            else:
                st.error("⚠️ 扫描引擎响应异常。请查看左侧边栏的错误诊断。")

with c2:
    st.subheader("📊 分析看板")
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.metric("风险评分", f"{res.get('score', 0)} / 10")
        
        df = pd.DataFrame(dict(
            r=res.get('values', [0,0,0,0,0]), 
            theta=['宗教','技术','政治','经济','媒体']
        ))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"**分析总结：** {res.get('summary', '解析完成')}")
    else:
        st.info("💡 终端就绪。请输入文本后开始扫描。")

with st.sidebar:
    st.write("### 📜 历史记录")
    if st.session_state['history']:
        st.table(pd.DataFrame(st.session_state['history']))
