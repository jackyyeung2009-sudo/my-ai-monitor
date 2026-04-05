import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go

# 1. 初始化頁面
st.set_page_config(page_title="AI 算力中心-全功能版", layout="wide")
st.title("📊 智譜 & MiniMax：LEGO 形態視覺化分析")

# 2. 定義格局數據 (收市分析用)
STOCK_DB = {
    '02513': {'name': '智譜 AI', 'base': 760, 'top': 850, 'support': 764, 'last_close': 779.0},
    '00100': {'name': 'MiniMax-W', 'base': 920, 'top': 980, 'support': 935, 'last_close': 949.5}
}

def fetch_data(ticker):
    """抓取現價，失敗則用最後收盤價"""
    try:
        url = f"http://www.aastocks.com/tc/stocks/analysis/stock-quote-details.aspx?stock={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        price = float(soup.find('div', {'class': 'lastPrice'}).text.strip().replace(',', ''))
        return price, "實時/延遲數據"
    except:
        return STOCK_DB[ticker]['last_close'], "收市封存數據"

# 3. 核心功能：繪製 LEGO 圖表
def draw_lego_plot(ticker, current_price):
    conf = STOCK_DB[ticker]
    # 模擬過去 10 天的走勢數據 (讓你有「看過去」的感覺)
    dates = pd.date_range(end=datetime.now(), periods=10)
    # 假設一些波动，最後一天對齊現價
    prices = [conf['last_close'] * (1 + (i-5)*0.01) for i in range(10)]
    prices[-1] = current_price
    
    fig = go.Figure()
    # 畫出走勢線
    fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines+markers', name='價格走勢', line=dict(color='#00ffcc')))
    
    # 畫出核心 LEGO 方塊 (態)
    fig.add_shape(type="rect",
        x0=dates[0], y0=conf['base'], x1=dates[-1], y1=conf['top'],
        line=dict(color="Gold", width=2),
        fillcolor="Yellow", opacity=0.1, name="LEGO 方塊"
    )
    
    fig.update_layout(
        title=f"{conf['name']} - LEGO 格局分析 (${conf['base']} - ${conf['top']})",
        template="plotly_dark",
        yaxis=dict(range=[conf['base']-50, conf['top']+50])
    )
    return fig

# 4. 佈局呈現
selected_ticker = st.sidebar.selectbox("選擇監控個股", list(STOCK_DB.keys()))
price, source = fetch_data(selected_ticker)

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label=f"{STOCK_DB[selected_ticker]['name']} 現價", value=f"${price}", delta=source)
    st.write(f"🧱 **LEGO 底部防禦：** ${STOCK_DB[selected_ticker]['base']}")
    st.write(f"🛡️ **明日部署：** 守住 ${STOCK_DB[selected_ticker]['support']} 則陽氣尚存。")
    
    # 方塊進度條
    progress = (price - STOCK_DB[selected_ticker]['base']) / (STOCK_DB[selected_ticker]['top'] - STOCK_DB[selected_ticker]['base'])
    st.progress(min(max(progress, 0.0), 1.0), text="當前在方塊內的位置")

with col2:
    # 重新注入圖表！
    st.plotly_chart(draw_lego_plot(selected_ticker, price), use_container_width=True)

st.info("💡 **提示：** 圖表中的黃色陰影區就是 Sky Sir 的 LEGO 方塊。只要線條在陰影內，就是『疊磚』；衝出頂部就是『突破』。")
