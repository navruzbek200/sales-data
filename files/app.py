import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import re

# ── Page config ───────────────────────────────────────────────────────────────
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
.stApp { background: #0f0f13; }

.insight-card {
    background: linear-gradient(135deg, #1a1a24 0%, #1e1e2e 100%);
    border: 1px solid rgba(110,231,183,0.15);
    border-radius: 16px;
    padding: 20px;
    margin: 8px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.insight-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #6ee7b7;
    margin-bottom: 6px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.insight-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
    margin: 4px 0;
}
.insight-text { color: #94a3b8; font-size: 0.85rem; line-height: 1.5; }

.chat-user {
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 15%;
    color: white;
    font-size: 0.95rem;
}
.chat-ai {
    background: linear-gradient(135deg, #1e1e2e 0%, #1a1a24 100%);
    border: 1px solid rgba(110,231,183,0.2);
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 15% 8px 0;
    line-height: 1.6;
    font-size: 0.95rem;
}
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #6ee7b7;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(110,231,183,0.2);
}
.chart-info-badge {
    background: linear-gradient(135deg, #6366f1, #818cf8);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: white;
    display: inline-block;
    margin-bottom: 10px;
}
.stButton > button {
    background: linear-gradient(135deg, #6ee7b7 0%, #34d399 100%) !important;
    color: #0f0f13 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "df": None,
    "chat_history": [],
    "active_chart": None,   # stores chart config from last AI answer
    "api_key": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Try loading API key from secrets/env
if not st.session_state.api_key:
    try:
        st.session_state.api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    except Exception:
        st.session_state.api_key = os.environ.get("ANTHROPIC_API_KEY", "")


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Faylni o'qishda xato: {e}")
        return None


def detect_cols(df):
    """Detect common column types."""
    revenue_col = next((c for c in df.columns if any(k in c.lower() for k in ["revenue","sales","amount","daromad","summa","total"])), None)
    qty_col = next((c for c in df.columns if any(k in c.lower() for k in ["qty","quantity","count","miqdor","soni"])), None)
    profit_col = next((c for c in df.columns if any(k in c.lower() for k in ["profit","margin","foyda"])), None)
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    num_cols = df.select_dtypes(include="number").columns.tolist()
    return revenue_col, qty_col, profit_col, cat_cols, num_cols


def analyze_data(df):
    insights = []
    revenue_col, qty_col, profit_col, cat_cols, num_cols = detect_cols(df)

    insights.append({"title":"📊 Umumiy","value":f"{df.shape[0]:,} qator","text":f"{df.shape[1]} ustun"})

    if revenue_col:
        insights.append({
            "title":f"💰 Daromad",
            "value":f"{df[revenue_col].sum():,.0f}",
            "text":f"O'rtacha: {df[revenue_col].mean():,.0f} | Min: {df[revenue_col].min():,.0f}"
        })
    if qty_col:
        insights.append({
            "title":f"📦 Miqdor",
            "value":f"{df[qty_col].sum():,.0f}",
            "text":f"O'rtacha: {df[qty_col].mean():,.1f} dona"
        })
    if profit_col:
        insights.append({
            "title":f"📈 Foyda",
            "value":f"{df[profit_col].sum():,.0f}",
            "text":f"O'rtacha: {df[profit_col].mean():,.0f}"
        })
    if cat_cols and num_cols:
        g_col = cat_cols[0]
        v_col = revenue_col or num_cols[0]
        top = df.groupby(g_col)[v_col].sum().nlargest(1)
        bot = df.groupby(g_col)[v_col].sum().nsmallest(1)
        insights.append({"title":"🏆 Eng yaxshi","value":str(top.index[0]),"text":f"{top.values[0]:,.0f}"})
        insights.append({"title":"⚠️ Eng past","value":str(bot.index[0]),"text":f"{bot.values[0]:,.0f}"})
    return insights


def build_data_summary(df):
    revenue_col, qty_col, profit_col, cat_cols, num_cols = detect_cols(df)
    lines = [
        f"Dataset: {df.shape[0]} rows x {df.shape[1]} columns",
        f"Columns: {list(df.columns)}",
        f"Numeric columns: {num_cols}",
        f"Categorical columns: {cat_cols}",
        "",
        "Stats:",
        df.describe().to_string(),
        "",
        "First 8 rows:",
        df.head(8).to_string(),
    ]
    if cat_cols and num_cols:
        v = revenue_col or num_cols[0]
        for c in cat_cols[:2]:
            grp = df.groupby(c)[v].sum().sort_values(ascending=False)
            lines.append(f"\nGrouped by {c} ({v}): {grp.to_dict()}")
    return "\n".join(lines)


CHART_SCHEMA = """
When your answer involves showing a chart, append a JSON block at the very end of your message (after all text), like:
```chart
{"type":"bar","x_col":"product","y_col":"revenue","title":"Mahsulot bo'yicha daromad","top_n":10,"orientation":"h"}
```
Chart types: "bar", "pie", "line", "scatter"
orientation: "h" for horizontal bar, "v" for vertical (default)
top_n: optional, limits to top N rows
x_col and y_col must be actual column names from the dataset.
Only include this JSON if a chart would genuinely help. If no chart needed, omit it.
"""


def ask_claude(question: str, df: pd.DataFrame, api_key: str):
    """Call Claude, parse text + optional chart JSON."""
    if not api_key:
        return "❌ API key topilmadi. Chap panelda API key kiriting.", None

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        summary = build_data_summary(df)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=f"""Sen ma'lumot tahlilchisisan. Foydalanuvchi savollariga O'zbek tilida javob ber.
Aniq raqamlar keltir, emojilardan foydalanilsin. Qisqa va aniq bo'l.

{CHART_SCHEMA}

Dataset ma'lumotlari:
{summary}""",
            messages=[{"role":"user","content":question}]
        )

        full_text = response.content[0].text
        chart_cfg = None

        # Extract chart JSON if present
        match = re.search(r"```chart\s*(\{.*?\})\s*```", full_text, re.DOTALL)
        if match:
            try:
                chart_cfg = json.loads(match.group(1))
                # Remove chart block from displayed text
                full_text = full_text[:match.start()].strip()
            except Exception:
                pass

        return full_text, chart_cfg

    except Exception as e:
        return f"❌ Xato: {str(e)}", None


def render_dynamic_chart(df, cfg):
    """Render a chart from AI-provided config dict."""
    if cfg is None:
        return

    chart_type = cfg.get("type","bar")
    x_col = cfg.get("x_col")
    y_col = cfg.get("y_col")
    title = cfg.get("title","")
    top_n = cfg.get("top_n", None)
    orientation = cfg.get("orientation","v")

    # Validate columns
    if x_col not in df.columns or (y_col and y_col not in df.columns):
        return

    DARK = {"plot_bgcolor":"#1a1a24","paper_bgcolor":"#0f0f13","font":dict(color="#e2e8f0")}
    TEAL = ["#1e1e2e","#6ee7b7"]

    try:
        if chart_type in ("bar","line"):
            if y_col:
                agg = df.groupby(x_col)[y_col].sum().reset_index()
            else:
                agg = df.groupby(x_col).size().reset_index(name="count")
                y_col = "count"
            if top_n:
                agg = agg.nlargest(int(top_n), y_col)

            if chart_type == "bar":
                fig = px.bar(agg, x=y_col if orientation=="h" else x_col,
                             y=x_col if orientation=="h" else y_col,
                             orientation=orientation,
                             color=y_col, color_continuous_scale=TEAL,
                             title=title)
            else:
                fig = px.line(agg, x=x_col, y=y_col, title=title,
                              color_discrete_sequence=["#6ee7b7"])
                fig.update_traces(line_width=3)

            fig.update_layout(**DARK, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "pie":
            if y_col:
                agg = df.groupby(x_col)[y_col].sum().reset_index()
            else:
                agg = df.groupby(x_col).size().reset_index(name="count")
                y_col = "count"
            if top_n:
                agg = agg.nlargest(int(top_n), y_col)
            fig = px.pie(agg, values=y_col, names=x_col, hole=0.4, title=title,
                         color_discrete_sequence=px.colors.sequential.Teal)
            fig.update_layout(**DARK)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=title,
                             color_discrete_sequence=["#6ee7b7"])
            fig.update_layout(**DARK)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.caption(f"Grafik xatosi: {e}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">📂 Fayl yuklash</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV yoki Excel fayl", type=["csv","xlsx","xls"],
                                 help="Sales CSV/Excel fayl yuklang")
    if uploaded:
        df_new = load_data(uploaded)
        if df_new is not None:
            st.session_state.df = df_new
            st.session_state.chat_history = []
            st.session_state.active_chart = None
            st.success(f"✅ {df_new.shape[0]:,} qator yuklandi")

    st.markdown("---")
    st.markdown('<div class="section-title">🔑 API Key</div>', unsafe_allow_html=True)
    api_input = st.text_input("Anthropic API Key", value=st.session_state.api_key,
                               type="password", help="Claude uchun API key")
    if api_input:
        st.session_state.api_key = api_input
    if st.session_state.api_key:
        st.success("✅ API key sozlangan")
    else:
        st.warning("⚠️ API key kiritilmagan")

    st.markdown("---")
    st.markdown('<div class="section-title">💡 Namuna savollar</div>', unsafe_allow_html=True)
    sample_qs = [
        "Eng ko'p daromad keltirgan mahsulot?",
        "Qaysi region eng yaxshi natija ko'rsatdi?",
        "O'rtacha buyurtma qiymati qancha?",
        "Kategoriya bo'yicha foyda taqsimotini ko'rsat",
        "Eng past ko'rsatkichlar qayerda?",
    ]
    for q in sample_qs:
        if st.button(q, key=f"sq_{hash(q)}", use_container_width=True):
            st.session_state["pending_question"] = q

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-family:Space Mono,monospace;font-size:1.9rem;color:#6ee7b7;margin-bottom:2px;'>
📊 Sales Data Analyzer
</h1>
<p style='color:#64748b;font-size:0.9rem;margin-top:0;'>
AI tahlil + Dinamik graflar · CSV / Excel
</p>
""", unsafe_allow_html=True)

# ── No data ───────────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.markdown("""
    <div style='text-align:center;padding:60px;border:2px dashed rgba(110,231,183,0.3);border-radius:16px;margin-top:40px;'>
        <div style='font-size:3rem;margin-bottom:12px;'>📁</div>
        <div style='font-size:1.1rem;font-weight:600;color:#94a3b8;'>Chap paneldan fayl yuklang</div>
        <div style='font-size:0.85rem;margin-top:8px;color:#475569;'>CSV yoki Excel formatdagi sotish ma'lumotlari</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = st.session_state.df

# ── KPI Cards ─────────────────────────────────────────────────────────────────
insights = analyze_data(df)
cols = st.columns(len(insights))
for i, ins in enumerate(insights):
    with cols[i]:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{ins['title']}</div>
            <div class="insight-value">{ins['value']}</div>
            <div class="insight-text">{ins['text']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Jadval", "📊 Grafik", "🤖 AI Chat"])

# ── Tab 1: Table ──────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Ma\'lumotlar jadvali</div>', unsafe_allow_html=True)
    n = st.selectbox("Ko'rsatish", [10, 25, 50, 100, "Hammasi"], index=1)
    display_df = df if n == "Hammasi" else df.head(int(n))
    st.dataframe(display_df, use_container_width=True, height=420)
    st.caption(f"Jami: {len(df):,} qator · {df.shape[1]} ustun")

# ── Tab 2: Charts ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Vizualizatsiya</div>', unsafe_allow_html=True)

    revenue_col, qty_col, profit_col, cat_cols, num_cols = detect_cols(df)

    # Show AI-driven chart if available
    if st.session_state.active_chart:
        st.markdown('<div class="chart-info-badge">🤖 AI tomonidan tanlangan grafik</div>', unsafe_allow_html=True)
        render_dynamic_chart(df, st.session_state.active_chart)
        st.markdown("---")
        st.markdown('<div class="section-title">Qo\'lda sozlash</div>', unsafe_allow_html=True)

    if cat_cols and num_cols:
        c1, c2 = st.columns(2)
        with c1:
            x_sel = st.selectbox("Kategoriya (X)", cat_cols, key="man_x")
            y_sel = st.selectbox("Qiymat (Y)", num_cols, key="man_y")
            top_n = st.slider("Top N", 3, 20, 10, key="man_n")

            agg = df.groupby(x_sel)[y_sel].sum().nlargest(top_n).reset_index()
            fig_bar = px.bar(agg, x=y_sel, y=x_sel, orientation="h",
                             color=y_sel, color_continuous_scale=["#1e1e2e","#6ee7b7"],
                             title=f"Top {top_n}: {x_sel} bo'yicha {y_sel}")
            fig_bar.update_layout(plot_bgcolor="#1a1a24", paper_bgcolor="#0f0f13",
                                   font=dict(color="#e2e8f0"), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            pie_data = df.groupby(x_sel)[y_sel].sum().nlargest(8).reset_index()
            fig_pie = px.pie(pie_data, values=y_sel, names=x_sel, hole=0.4,
                             title=f"{x_sel} taqsimoti",
                             color_discrete_sequence=px.colors.sequential.Teal)
            fig_pie.update_layout(plot_bgcolor="#1a1a24", paper_bgcolor="#0f0f13",
                                   font=dict(color="#e2e8f0"))
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Grafik uchun kamida bitta kategoriya va bitta raqamli ustun kerak.")

# ── Tab 3: AI Chat ────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">🤖 AI bilan suhbat</div>', unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.warning("⚠️ Chat ishlatish uchun chap panelda Anthropic API key kiriting")
    else:
        # Chat history display
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                    # Show inline chart for this message if it has one
                    if msg.get("chart"):
                        render_dynamic_chart(df, msg["chart"])

        if not st.session_state.chat_history:
            st.info("💬 Savol yozing yoki chap paneldan namuna savol bosing")

        # Input area
        pending = st.session_state.pop("pending_question", "")
        question = st.text_input(
            "Savol bering",
            value=pending,
            placeholder="Masalan: Qaysi mahsulot eng ko'p sotilgan?",
            key="user_question"
        )

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            send = st.button("📨 Yuborish", type="primary", use_container_width=True)
        with col_btn2:
            if st.button("🗑️ Tozalash", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.active_chart = None
                st.rerun()

        if send and question.strip():
            st.session_state.chat_history.append({"role":"user","content":question})

            with st.spinner("🤖 AI javob bermoqda..."):
                answer_text, chart_cfg = ask_claude(question, df, st.session_state.api_key)

            msg_entry = {"role":"assistant","content":answer_text}
            if chart_cfg:
                msg_entry["chart"] = chart_cfg
                st.session_state.active_chart = chart_cfg  # update Grafik tab too

            st.session_state.chat_history.append(msg_entry)
            st.rerun()
