import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. 時空握手 - 設定介面
st.set_page_config(page_title="AI 算力中心 - 勢位態監控", layout="wide")
st.title("🚀 Sky Sir 風格：AI 新貴實時監控系統")
st.write(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (AEST/HKT 同步)")

# 2. 核心數據模擬 (實際運行時可對接 aastock 爬蟲)
def get_live_data():
    # 這裡預填你提到的 2513 與 100 數據
    data = {
        '代碼': ['02513', '00100', '09988', '00700'],
        '名稱': ['智譜 AI', 'MiniMax-W', '阿里巴巴', '騰訊控股'],
        '現價': [779.0, 949.5, 92.4, 385.2],
        '資金流向(億)': [-13.6, 6.8, 5.1, -1.8],
        'LEGO狀態': ['疊磚中', '向上突破', '方塊底', '整固中']
    }
    return pd.DataFrame(data)

# 3. LEGO 形態繪圖引擎
def draw_lego_chart(stock_name, price):
    # 模擬 K 線數據
    df_k = pd.DataFrame({
        'Date': pd.date_range(start='2026-03-20', periods=15),
        'Open': [price-10]*15,
        'High': [price+5]*15,
        'Low': [price-15]*15,
        'Close': [price]*15
    })
    
    fig = go.Figure(data=[go.Candlestick(x=df_k['Date'],
                open=df_k['Open'], high=df_k['High'],
                low=df_k['Low'], close=df_k['Close'], name='K線')])

    # 注入 LEGO 方塊 (Sky Sir 邏輯：窄幅橫盤區)
    fig.add_shape(type="rect",
        x0=df_k['Date'].iloc[5], y0=price-20, x1=df_k['Date'].iloc[14], y1=price+20,
        line=dict(color="Gold", width=2),
        fillcolor="LightYellow", opacity=0.2, name="LEGO 方塊"
    )
    
    fig.update_layout(title=f"{stock_name} - LEGO 形態偵測", template="plotly_dark")
    return fig

# 4. APP 佈局
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 板塊資金實時監控")
    df = get_live_data()
    st.dataframe(df.style.map(lambda x: 'color: #ff4d4d' if isinstance(x, float) and x > 0 else 'color: #2ecc71', subset=['資金流向(億)']))
    
    selected_stock = st.selectbox("選擇個股查看穿透數據", df['名稱'])

with col2:
    current_price = df[df['名稱'] == selected_stock]['現價'].values[0]
    st.plotly_chart(draw_lego_chart(selected_stock, current_price), use_container_width=True)

# 5. 玄學提示
st.info("💡 算力備註：目前甲辰年，AI 板塊屬『火金』互煉。智譜 (2513) 方塊底部在 760 附近，守住則勢強。")
