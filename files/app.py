import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #e2e8f0;
    }

    .stApp {
        background: #0f0f13;
    }

    /* Insight card */
    .insight-card {
        background: linear-gradient(135deg, #1a1a24 0%, #1e1e2e 100%);
        border: 1px solid rgba(110, 231, 183, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }

    .insight-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        color: #6ee7b7;
        margin-bottom: 8px;
        font-weight: 700;
    }

    .insight-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #6ee7b7;
        margin: 8px 0;
    }

    .insight-text {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0;
        margin-left: 20%;
        color: white;
    }

    .chat-ai {
        background: linear-gradient(135deg, #1e1e2e 0%, #1a1a24 100%);
        border: 1px solid rgba(110, 231, 183, 0.2);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        margin-right: 20%;
        line-height: 1.6;
    }

    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #6ee7b7;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(110, 231, 183, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6ee7b7 0%, #34d399 100%) !important;
        color: #0f0f13 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
    }

    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state:
    # Try to get from secrets, then environment
    st.session_state.api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))


# ── Helper functions ──────────────────────────────────────────────────────────
def load_data(uploaded_file):
    """Load CSV or Excel file."""
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Faylni o'qishda xato: {e}")
        return None


def analyze_data(df: pd.DataFrame):
    """Automatically analyze the dataset and return insights."""
    insights = []
    
    # Numeric columns
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Try to detect revenue/profit/quantity columns
    revenue_col = next((c for c in df.columns if any(k in c.lower() for k in ["revenue", "sales", "amount", "daromad", "summa", "total"])), None)
    qty_col = next((c for c in df.columns if any(k in c.lower() for k in ["qty", "quantity", "count", "miqdor", "soni"])), None)
    profit_col = next((c for c in df.columns if any(k in c.lower() for k in ["profit", "margin", "foyda"])), None)
    
    # 1. Overall stats
    insights.append({
        "title": "📊 UMUMIY MA'LUMOTLAR",
        "value": f"{df.shape[0]:,} qator × {df.shape[1]} ustun",
        "text": f"Ma'lumotlar bazasi: {df.shape[0]:,} ta yozuv"
    })
    
    # 2. Revenue analysis
    if revenue_col:
        total_rev = df[revenue_col].sum()
        avg_rev = df[revenue_col].mean()
        max_rev = df[revenue_col].max()
        min_rev = df[revenue_col].min()
        
        insights.append({
            "title": f"💰 DAROMAD ({revenue_col})",
            "value": f"{total_rev:,.0f}",
            "text": f"O'rtacha: {avg_rev:,.0f} | Eng ko'p: {max_rev:,.0f} | Eng kam: {min_rev:,.0f}"
        })
    
    # 3. Quantity analysis  
    if qty_col:
        total_qty = df[qty_col].sum()
        avg_qty = df[qty_col].mean()
        
        insights.append({
            "title": f"📦 MIQDOR ({qty_col})",
            "value": f"{total_qty:,.0f}",
            "text": f"O'rtacha buyurtma: {avg_qty:,.1f} dona"
        })
    
    # 4. Profit analysis
    if profit_col:
        total_profit = df[profit_col].sum()
        avg_profit = df[profit_col].mean()
        
        insights.append({
            "title": f"📈 FOYDA ({profit_col})",
            "value": f"{total_profit:,.0f}",
            "text": f"O'rtacha foyda: {avg_profit:,.0f}"
        })
    
    # 5. Top performer (by revenue or first numeric col)
    if cat_cols and num_cols:
        group_col = cat_cols[0]
        value_col = revenue_col or num_cols[0]
        
        top = df.groupby(group_col)[value_col].sum().nlargest(3)
        top_text = " | ".join([f"{k}: {v:,.0f}" for k, v in top.items()])
        
        insights.append({
            "title": f"🏆 TOP 3 ({group_col})",
            "value": top.index[0],
            "text": top_text
        })
    
    # 6. Bottom performer
    if cat_cols and num_cols:
        group_col = cat_cols[0]
        value_col = revenue_col or num_cols[0]
        
        bottom = df.groupby(group_col)[value_col].sum().nsmallest(3)
        bottom_text = " | ".join([f"{k}: {v:,.0f}" for k, v in bottom.items()])
        
        insights.append({
            "title": f"⚠️ PAST 3 ({group_col})",
            "value": bottom.index[0],
            "text": bottom_text
        })
    
    return insights


def ask_claude(question: str, df: pd.DataFrame, api_key: str):
    """Ask Claude about the data using API directly."""
    if not api_key:
        return "❌ API key topilmadi. Iltimos .streamlit/secrets.toml faylida ANTHROPIC_API_KEY ni sozlang."
    
    try:
        # Create data summary
        summary = f"""Dataset: {df.shape[0]} rows × {df.shape[1]} columns
Columns: {list(df.columns)}

Numeric summary:
{df.describe().to_string()}

Sample data (first 10 rows):
{df.head(10).to_string()}
"""
        
        # Call Claude API
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=f"""You are a data analyst. Answer questions about this dataset in Uzbek language.
Use emojis and be concise. Provide specific numbers from the data.

{summary}""",
            messages=[{"role": "user", "content": question}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"❌ Xato: {str(e)}"



# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">📂 Ma\'lumot yuklash</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "CSV yoki Excel fayl tanlang",
        type=["csv", "xlsx", "xls"],
        help="Satish ma'lumotlari bo'lgan CSV yoki Excel fayl yuklang",
    )

    if uploaded:
        df = load_data(uploaded)
        if df is not None:
            st.session_state.df = df
            st.session_state.chat_history = []  # Reset chat
            st.success(f"✅ {df.shape[0]:,} qator yuklandi")

    st.markdown("---")
    st.markdown('<div class="section-title">🔑 API sozlamalari</div>', unsafe_allow_html=True)
    
    api_input = st.text_input(
        "Anthropic API Key", 
        value=st.session_state.api_key,
        type="password",
        help="Claude bilan suhbat uchun API key kerak"
    )
    if api_input:
        st.session_state.api_key = api_input
    
    if st.session_state.api_key:
        st.success("✅ API key sozlangan")
    else:
        st.warning("⚠️ API key kiritilmagan")

    st.markdown("---")
    st.markdown('<div class="section-title">💡 Namuna savollar</div>', unsafe_allow_html=True)

    sample_questions = [
        "Eng ko'p daromad keltirgan mahsulot?",
        "Qaysi region eng yaxshi?",
        "O'rtacha buyurtma qiymati?",
        "Eng past ko'rsatkichlar qayerda?",
    ]

    for q in sample_questions:
        if st.button(q, key=f"sq_{q}", use_container_width=True):
            st.session_state["pending_question"] = q

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-family: Space Mono, monospace; font-size: 2rem; color: #6ee7b7; margin-bottom: 4px;'>
    📊 Sales Data Analyzer
</h1>
<p style='color: #64748b; font-size: 0.95rem; margin-top: 0;'>
    Avtomatik tahlil + AI chat · Har qanday CSV/Excel fayl
</p>
""", unsafe_allow_html=True)

# ── No data state ─────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.markdown("""
    <div style='text-align: center; padding: 60px; border: 2px dashed rgba(110, 231, 183, 0.3); border-radius: 16px;'>
        <div style='font-size: 3rem; margin-bottom: 12px;'>📁</div>
        <div style='font-size: 1.1rem; font-weight: 600; color: #94a3b8;'>Chap paneldan fayl yuklang</div>
        <div style='font-size: 0.85rem; margin-top: 8px; color: #475569;'>CSV yoki Excel formatdagi ma'lumotlar</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = st.session_state.df

# ── AUTO ANALYSIS ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Avtomatik tahlil</div>', unsafe_allow_html=True)

insights = analyze_data(df)

cols = st.columns(3)
for i, insight in enumerate(insights):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{insight['title']}</div>
            <div class="insight-value">{insight['value']}</div>
            <div class="insight-text">{insight['text']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Jadval", "📊 Grafik", "🤖 AI Chat"])

# Tab 1: Data table
with tab1:
    st.markdown('<div class="section-title">Ma\'lumotlar jadvali</div>', unsafe_allow_html=True)
    
    n_rows = st.selectbox("Ko'rsatish", [10, 25, 50, 100], index=1)
    st.dataframe(df.head(n_rows), use_container_width=True, height=400)
    st.caption(f"Jami: {len(df):,} qator")

# Tab 2: Charts
with tab2:
    st.markdown('<div class="section-title">Vizualizatsiya</div>', unsafe_allow_html=True)
    
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    if cat_cols and num_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            x_col = st.selectbox("Kategoriya", cat_cols)
            y_col = st.selectbox("Qiymat", num_cols)
            top_n = st.slider("Top N", 5, 20, 10)
            
            agg = df.groupby(x_col)[y_col].sum().nlargest(top_n).reset_index()
            fig = px.bar(agg, x=y_col, y=x_col, orientation="h",
                        color=y_col, color_continuous_scale=["#1e1e2e", "#6ee7b7"],
                        title=f"Top {top_n}: {x_col}")
            fig.update_layout(
                plot_bgcolor="#1a1a24", paper_bgcolor="#0f0f13",
                font=dict(color="#e2e8f0"), showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            pie_data = df.groupby(x_col)[y_col].sum().nlargest(8).reset_index()
            fig2 = px.pie(pie_data, values=y_col, names=x_col, hole=0.4,
                         title=f"{x_col} taqsimoti",
                         color_discrete_sequence=px.colors.sequential.Teal)
            fig2.update_layout(
                plot_bgcolor="#1a1a24", paper_bgcolor="#0f0f13",
                font=dict(color="#e2e8f0")
            )
            st.plotly_chart(fig2, use_container_width=True)

# Tab 3: AI Chat
with tab3:
    st.markdown('<div class="section-title">🤖 Claude bilan suhbat</div>', unsafe_allow_html=True)
    
    if not st.session_state.api_key:
        st.warning("⚠️ Chat ishlatish uchun chap panelda API key kiriting")
    else:
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        
        # Input
        question = st.text_input(
            "Savol bering",
            value=st.session_state.pop("pending_question", ""),
            placeholder="Masalan: Qaysi mahsulot eng ko'p sotilgan?",
            key="user_question"
        )
        
        if st.button("📨 Yuborish", type="primary"):
            if question.strip():
                # Add to history
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                # Get AI response
                with st.spinner("AI javob bermoqda..."):
                    answer = ask_claude(question, df, st.session_state.api_key)
                
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
        
        if not st.session_state.chat_history:
            st.info("💬 Savolingizni yozing yoki chap paneldagi namuna savollardan birini bosing")
