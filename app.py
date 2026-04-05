# 加入一個滑動條，讓你隨意調整計算天數
lookback_days = st.sidebar.slider("LEGO 計算週期 (天)", min_value=5, max_value=20, value=10)

def calculate_lego_auto(ticker, days):
    # 【註】目前因休市與爬蟲限制，這裡先模擬歷史最高/最低
    # 實戰中應對接歷史數據 API 獲取真實 High/Low
    current_p, _ = fetch_safe_data(ticker)
    if current_p:
        # 模擬過去 N 天的方塊：最高價為現價 + 5%，最低價為現價 - 5%
        # 這裡你可以手動在畫面上的 Number Input 進行微調
        auto_top = current_p * (1 + 0.005 * days)
        auto_base = current_p * (1 - 0.005 * days)
        return auto_base, auto_top
    return 0, 0
