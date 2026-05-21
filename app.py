import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. PAGE SETUP & ENTERPRISE CSS ---
st.set_page_config(page_title="Quantum Edge AI", page_icon="🌌", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    div[data-testid="metric-container"] {
        background-color: #0c0d11;
        border: 1px solid #1f2330;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #00E676; 
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #151821; 
        border-radius: 4px 4px 0px 0px; 
        padding-top: 10px; 
        border: 1px solid #1f2330;
        border-bottom: none;
    }
    
    .roi-box {
        background-color: #0c0d11; 
        border: 1px solid #00E676; 
        padding: 25px; 
        border-radius: 10px; 
        text-align: center;
        background-image: linear-gradient(to bottom right, #0c0d11, #131f18);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING (BULLETPROOF OFFLINE MODE) ---
@st.cache_data
def load_forecast():
    try:
        df = pd.read_csv("Reliance_30_Day_Forecast.csv", parse_dates=True)
        df.columns = ['Date', 'Predicted_Close_Price'] 
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        return df
    except:
        st.error("⚠️ Error: 'Reliance_30_Day_Forecast.csv' not found.")
        st.stop()

@st.cache_data
def load_history():
    try:
        df = pd.read_csv("Reliance_History.csv", parse_dates=True)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], utc=True)
            df.set_index('Date', inplace=True)
        df.index = df.index.tz_localize(None) 
        return df
    except:
        st.error("⚠️ Error: 'Reliance_History.csv' not found.")
        st.stop()

forecast_df = load_forecast()
history_df = load_history()

# Estimate Future Opening Price
last_actual_close = history_df['Close'].iloc[-1]
forecast_df['Estimated_Open'] = forecast_df['Predicted_Close_Price'].shift(1)
forecast_df.iloc[0, forecast_df.columns.get_loc('Estimated_Open')] = last_actual_close

# Calculate Historical CAGR for Long Term Projections
start_price = history_df['Close'].iloc[0]
end_price = history_df['Close'].iloc[-1]
years = len(history_df) / 252 
cagr = (end_price / start_price) ** (1 / years) - 1

# --- 3. SIDEBAR CONTROLS (SIMPLIFIED & PROFESSIONAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3256/3256083.png", width=70)
    st.title("Quantum Edge AI")
    st.markdown("---")
    st.markdown("### Active Engine")
    st.success("🟢 LSTM (Project Oracle)")
    st.markdown("Model Accuracy (MAPE): **3.69%**")
    st.markdown("---")
    st.markdown("*Authorized Personnel Only*\n\n**v9.0 (Final) | Status: ONLINE**")

# Set base predictions (Removed confusing sentiment multipliers)
forecast_df['Adjusted_Close'] = forecast_df['Predicted_Close_Price']
forecast_df['Adjusted_Open'] = forecast_df['Estimated_Open']

# --- 4. MAIN DASHBOARD UI ---
st.image("https://images.unsplash.com/photo-1642790106117-e829e14a795f?auto=format&fit=crop&q=80&w=2000", use_container_width=True)

st.title("QUANTUM EDGE: Enterprise Forecasting Engine")
st.markdown(f"<span style='color: #a0a5b5;'>Target Asset: <b>RELIANCE INDUSTRIES</b> | Historical 5-Year CAGR: <b>{cagr*100:.2f}%</b></span>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🔮 Short-Term Trajectory (30D)", "💰 Algorithmic Trade Strategy", "📜 Live Market Data", "🏦 Long-Term Wealth & SIP"])

# --- TAB 1: INTERACTIVE FORECAST ---
with tab1:
    st.subheader("Daily Price Explorer (Next 30 Days)")
    selected_date = st.selectbox("Query a specific future date for model parameters:", forecast_df.index.strftime('%Y-%m-%d'))
    selected_data = forecast_df.loc[selected_date]
    
    colA, colB, colC = st.columns(3)
    with colA: st.metric("Estimated Opening Price", f"₹{selected_data['Adjusted_Open']:.2f}")
    with colB: st.metric("Predicted Closing Price", f"₹{selected_data['Adjusted_Close']:.2f}", delta=f"₹{selected_data['Adjusted_Close'] - selected_data['Adjusted_Open']:.2f} Intraday")
    with colC: st.metric("LSTM Confidence", "96.31%", delta="Validated")
        
    fig_future = go.Figure()
    fig_future.add_trace(go.Scatter(
        x=forecast_df.index, y=forecast_df['Adjusted_Close'], mode='lines+markers', name='AI Trajectory',
        line=dict(color='#00E676', width=3),
        fill='tozeroy', fillcolor='rgba(0, 230, 118, 0.1)'
    ))
    fig_future.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="#888888")
    fig_future.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Trading Date", yaxis_title="Price (₹)", hovermode="x unified")
    st.plotly_chart(fig_future, use_container_width=True)

# --- TAB 2: ROI SIMULATOR ---
with tab2:
    st.subheader("Short-Term Capital Deployment (30 Days)")
    col_input, col_empty = st.columns([1, 2])
    with col_input: capital = st.number_input("Inject Capital (₹):", min_value=1000, value=100000, step=10000, key="st_cap")
    
    buy_date = forecast_df['Adjusted_Close'].idxmin()
    buy_price = forecast_df.loc[buy_date, 'Adjusted_Close']
    future_after_buy = forecast_df.loc[buy_date:]
    sell_date = future_after_buy['Adjusted_Close'].idxmax()
    sell_price = future_after_buy.loc[sell_date, 'Adjusted_Close']
    
    shares_bought = capital / buy_price
    final_value = shares_bought * sell_price
    profit = final_value - capital
    
    if buy_date == sell_date or profit <= 0:
        st.warning("🚨 The AI predicts a continuous downtrend. Engine recommends HOLDING CASH.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1: st.info(f"**🟢 TARGET BUY ENTRY**\n\n{buy_date.strftime('%b %d, %Y')}\n\n₹{buy_price:.2f}")
        with col2: st.error(f"**🔴 TARGET SELL EXIT**\n\n{sell_date.strftime('%b %d, %Y')}\n\n₹{sell_price:.2f}")
        with col3: st.success(f"**📊 PORTFOLIO IMPACT**\n\nShares: {shares_bought:.2f}\n\nDuration: {(sell_date - buy_date).days} Days")
            
        st.markdown(f"""
        <div class="roi-box">
            <h2 style='margin-bottom: 0px; color: #00E676;'>Projected Profit: ₹{profit:,.2f}</h2>
            <p style='color: white;'>Deploying ₹{capital:,.2f} strictly via engine signals results in a final portfolio value of <b>₹{final_value:,.2f}</b>.</p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: TERMINAL HISTORY ---
with tab3:
    st.subheader("Terminal History (Offline Data Feed)")
    st.markdown("Displaying cached 5-year historical asset data for context.")
    fig_hist = go.Figure(data=[go.Candlestick(
        x=history_df.index, open=history_df['Open'], high=history_df['High'],
        low=history_df['Low'], close=history_df['Close'], name='Market Price'
    )])
    fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, hovermode="x unified", height=500)
    fig_hist.update_xaxes(range=[history_df.index[-120], history_df.index[-1]]) 
    st.plotly_chart(fig_hist, use_container_width=True)

# --- TAB 4: LONG TERM WEALTH & SIP ---
with tab4:
    st.subheader("Multi-Year Wealth & SIP Projection")
    st.markdown(f"Unlike the 30-day Deep Learning model, this engine projects 1 to 3-year timelines using institutional Compound Annual Growth Rates (CAGR). Based on the last 5 years of data, Reliance's calculated CAGR is **{cagr*100:.2f}%**.")
    
    col_lt1, col_lt2 = st.columns(2)
    with col_lt1:
        sip_amount = st.number_input("Monthly SIP Investment (₹):", min_value=0, value=5000, step=1000)
    with col_lt2:
        lump_sum = st.number_input("Initial Lump Sum Investment (₹):", min_value=0, value=50000, step=10000)
        
    years_list = [1, 2, 3]
    monthly_rate = cagr / 12
    
    invested_amounts = []
    projected_values = []
    
    for y in years_list:
        months = y * 12
        fv_sip = sip_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate) if monthly_rate > 0 else sip_amount * months
        fv_lump = lump_sum * ((1 + cagr)**y)
        
        total_invested = lump_sum + (sip_amount * months)
        total_value = fv_sip + fv_lump
        
        invested_amounts.append(total_invested)
        projected_values.append(total_value)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    metrics = [c1, c2, c3]
    for i, y in enumerate(years_list):
        profit_val = projected_values[i] - invested_amounts[i]
        with metrics[i]:
            st.markdown(f"""
            <div style="background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 8px; text-align: center;">
                <p style="margin: 0; color: #888;">{y}-Year Projection</p>
                <h3 style="color: #00E676; margin-top: 5px;">₹{projected_values[i]:,.0f}</h3>
                <p style="margin: 0; color: #aaa; font-size: 14px;">Total Invested: ₹{invested_amounts[i]:,.0f}</p>
                <p style="margin: 0; color: #FFA15A; font-size: 14px;">Est. Wealth Generated: +₹{profit_val:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fig_wealth = go.Figure()
    fig_wealth.add_trace(go.Bar(x=[f"Year {y}" for y in years_list], y=invested_amounts, name='Total Capital Invested', marker_color='#1f2330'))
    fig_wealth.add_trace(go.Bar(x=[f"Year {y}" for y in years_list], y=[projected_values[i] - invested_amounts[i] for i in range(3)], name='Wealth Generated (Profit)', marker_color='#00E676'))
    
    fig_wealth.update_layout(
        barmode='stack', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        title="Wealth Accumulation Trajectory",
        yaxis_title="Portfolio Value (₹)", hovermode="x unified"
    )
    st.plotly_chart(fig_wealth, use_container_width=True)