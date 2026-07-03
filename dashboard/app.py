import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CreditGuard AI | Digital Lending Risk",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    /* Force all text white */
    * {
        color: #ffffff !important;
    }
    /* Hide Streamlit default toolbar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Premium top banner */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Premium card style */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2) !important;
        transition: transform 0.2s !important;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        border-right: 2px solid #00d4ff;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Sidebar markdown text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.15);
    }

    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    [data-testid="stMetricDelta"] {
        color: #51cf66 !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 5px;
        gap: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #ffffff !important;
        font-weight: 600;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: #ffffff !important;
    }

    /* Tab text */
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {
        color: #ffffff !important;
    }

    /* Custom boxes */
    .insight-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 4px solid #00d4ff;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1);
        color: #ffffff !important;
    }

    .warning-box {
        background: linear-gradient(135deg, #2d1b1b, #3d1f1f);
        border-left: 4px solid #ff6b6b;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 10px 0;
        color: #ffffff !important;
    }

    .success-box {
        background: linear-gradient(135deg, #1b2d1b, #1f3d1f);
        border-left: 4px solid #51cf66;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 10px 0;
        color: #ffffff !important;
    }

    /* Sidebar metric boxes */
    .sidebar-metric {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        text-align: center;
        color: #ffffff !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    h1 {
        background: linear-gradient(135deg, #00d4ff, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
    }

    /* Paragraphs and labels */
    p, label, span, div {
        color: #ffffff !important;
    }

    /* Divider */
    hr {
        border-color: #0f3460 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Selectbox, multiselect */
    .stSelectbox label,
    .stMultiSelect label {
        color: #ffffff !important;
    }

    /* Streamlit info/success/warning boxes */
    .stAlert {
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid #00d4ff !important;
        color: #ffffff !important;
        border-radius: 10px;
    }

    .stAlert p {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE CONNECTION
# ============================================================
@st.cache_resource
def get_conn():
    return duckdb.connect("data/home_credit.db")

conn = get_conn()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        "<h2 style='color:#00d4ff !important; text-align:center'>🏦 CreditGuard AI</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#ffffff !important; text-align:center;"
        "font-style:italic'>Digital Lending Risk Platform</p>",
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown(
        "<h3 style='color:#ffffff !important'>📋 Project Info</h3>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class='sidebar-metric'>
        <div style='color:#00d4ff !important; font-weight:700; font-size:1.1rem'>
            Group 1
        </div>
        <div style='color:#ffffff !important; font-size:0.85rem'>
            Thrive Africa Capstone
        </div>
    </div>
    <div class='sidebar-metric'>
        <div style='color:#00d4ff !important; font-weight:700; font-size:1.1rem'>
            March 2026 Cohort
        </div>
        <div style='color:#ffffff !important; font-size:0.85rem'>
            Analytics Engineering Track
        </div>
    </div>
    <div class='sidebar-metric'>
        <div style='color:#00d4ff !important; font-weight:700; font-size:1.1rem'>
            Home Credit Dataset
        </div>
        <div style='color:#ffffff !important; font-size:0.85rem'>
            7 Tables · 45M+ Rows
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown(
        "<h3 style='color:#ffffff !important'>🛠️ Tech Stack</h3>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <ul style='color:#ffffff !important; list-style:none; padding-left:0'>
        <li style='color:#ffffff !important; padding:5px 0'>
            🦆 <b style='color:#00d4ff !important'>DuckDB</b>
            <span style='color:#ffffff !important'> — SQL Engine</span>
        </li>
        <li style='color:#ffffff !important; padding:5px 0'>
            🐍 <b style='color:#00d4ff !important'>Python</b>
            <span style='color:#ffffff !important'> — Pipeline</span>
        </li>
        <li style='color:#ffffff !important; padding:5px 0'>
            🌲 <b style='color:#00d4ff !important'>Random Forest</b>
            <span style='color:#ffffff !important'> — Model</span>
        </li>
        <li style='color:#ffffff !important; padding:5px 0'>
            📊 <b style='color:#00d4ff !important'>Streamlit</b>
            <span style='color:#ffffff !important'> — Dashboard</span>
        </li>
        <li style='color:#ffffff !important; padding:5px 0'>
            🐙 <b style='color:#00d4ff !important'>GitHub</b>
            <span style='color:#ffffff !important'> — Version Control</span>
        </li>
    </ul>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown(
        "<h3 style='color:#ffffff !important'>🎯 Model Score</h3>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style='text-align:center; padding:20px;
                background:linear-gradient(135deg,#667eea,#764ba2);
                border-radius:12px; margin-top:10px'>
        <div style='font-size:2.5rem; font-weight:900;
                    color:#ffffff !important'>0.7462</div>
        <div style='color:#ffffff !important;
                    font-size:0.9rem; margin-top:5px'>ROC-AUC Score</div>
        <div style='color:#a0ffb0 !important;
                    font-size:0.85rem; margin-top:5px'>
            🏆 +0.2462 vs Baseline
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN HEADER
# ============================================================
st.title("💳 CreditGuard AI — Digital Lending Risk")
st.markdown(
    "<p style='color:#e2e8f0 !important; font-size:1.1rem'>"
    "Predicting loan defaults for digital lenders in Ghana & Nigeria "
    "using SQL-engineered features from 7 financial data tables · "
    "<b style='color:#00d4ff !important'>Group 1 · Ishango.ai · March 2026</b></p>",
    unsafe_allow_html=True
)

# ============================================================
# KPI METRICS
# ============================================================
col1, col2, col3, col4, col5 = st.columns(5)

total_apps = conn.execute(
    "SELECT COUNT(*) FROM mart_applicant_features").fetchone()[0]
default_rate = conn.execute(
    "SELECT AVG(TARGET)*100 FROM mart_applicant_features").fetchone()[0]
avg_credit = conn.execute(
    "SELECT AVG(AMT_CREDIT) FROM mart_applicant_features").fetchone()[0]
high_risk = conn.execute("""
    SELECT AVG(CASE WHEN credit_risk_band IN
    ('High Risk','Very High Risk') THEN 1.0 ELSE 0.0 END)*100
    FROM mart_applicant_features
""").fetchone()[0]
total_defaults = conn.execute(
    "SELECT SUM(TARGET) FROM mart_applicant_features").fetchone()[0]

col1.metric("👥 Applicants", f"{total_apps:,}")
col2.metric("⚠️ Default Rate", f"{default_rate:.1f}%")
col3.metric("💰 Avg Loan", f"${avg_credit:,.0f}")
col4.metric("🔴 High Risk", f"{high_risk:.1f}%")
col5.metric("❌ Defaults", f"{int(total_defaults):,}")

st.divider()

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Risk Segmentation",
    "💳 Payment Behaviour",
    "🏦 Credit Profile",
    "🎯 Model Results",
    "📈 Age Trends"
])

TEMPLATE = "plotly_dark"

# ============================================================
# TAB 1
# ============================================================
with tab1:
    st.markdown(
        "<h3 style='color:#ffffff !important'>📊 Risk Segmentation Analysis</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='insight-box'>"
        "💡 <b>Key Question:</b> Which income groups, education levels, "
        "and contract types carry the highest default risk?</div>",
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)

    with col_a:
        income_data = conn.execute(
            "SELECT * FROM analysis_default_by_income").fetchdf()
        fig = px.bar(
            income_data, x='income_band', y='default_rate_pct',
            title='🏦 Default Rate by Income Band',
            color='default_rate_pct',
            color_continuous_scale='RdYlGn_r',
            text='default_rate_pct',
            template=TEMPLATE
        )
        fig.update_traces(
            texttemplate='<b>%{text}%</b>',
            textposition='outside'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            showlegend=False,
            title_font_color='#ffffff',
            xaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff'),
            yaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        edu_data = conn.execute(
            "SELECT * FROM analysis_education_rank").fetchdf()
        fig2 = px.bar(
            edu_data, x='default_rate_pct', y='NAME_EDUCATION_TYPE',
            orientation='h',
            title='🎓 Default Rate by Education Level',
            color='risk_rank',
            color_continuous_scale='RdYlGn_r',
            text='default_rate_pct',
            template=TEMPLATE
        )
        fig2.update_traces(
            texttemplate='<b>%{text}%</b>',
            textposition='outside'
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            showlegend=False,
            title_font_color='#ffffff',
            xaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff'),
            yaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff')
        )
        st.plotly_chart(fig2, use_container_width=True)

    ntile_data = conn.execute(
        "SELECT * FROM analysis_ntile_risk").fetchdf()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=ntile_data['risk_quintile'],
        y=ntile_data['default_rate_pct'],
        name='Default Rate %',
        marker_color=['#51cf66','#94d82d','#fcc419','#ff922b','#ff6b6b'],
        text=ntile_data['default_rate_pct'],
        texttemplate='<b>%{text}%</b>',
        textposition='outside'
    ))
    fig3.add_trace(go.Scatter(
        x=ntile_data['risk_quintile'],
        y=ntile_data['avg_credit_income_ratio'],
        name='Avg Credit/Income Ratio',
        mode='lines+markers',
        line=dict(color='#00d4ff', width=3),
        marker=dict(size=10),
        yaxis='y2'
    ))
    fig3.update_layout(
        title='📊 NTILE(5) Risk Quintiles',
        template=TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        title_font_color='#ffffff',
        yaxis=dict(title='Default Rate (%)',
                   title_font_color='#ffffff',
                   tickfont_color='#ffffff'),
        yaxis2=dict(title='Credit/Income Ratio',
                    overlaying='y', side='right',
                    title_font_color='#ffffff',
                    tickfont_color='#ffffff'),
        legend=dict(font_color='#ffffff',
                    bgcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# TAB 2
# ============================================================
with tab2:
    st.markdown(
        "<h3 style='color:#ffffff !important'>💳 Payment History Analysis</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='insight-box'>💡 <b>Key Insight:</b> Payment history "
        "is the single strongest predictor of default.</div>",
        unsafe_allow_html=True
    )

    payment_data = conn.execute(
        "SELECT * FROM analysis_payment_behaviour").fetchdf()

    fig = go.Figure(go.Bar(
        x=payment_data['payment_behaviour'],
        y=payment_data['default_rate_pct'],
        marker_color=['#51cf66','#94d82d','#fcc419','#ff922b','#ff6b6b'],
        text=payment_data['default_rate_pct'],
        texttemplate='<b>%{text}%</b>',
        textposition='outside',
        width=0.6
    ))
    fig.update_layout(
        title='⚠️ Default Rate by Payment Behaviour',
        template=TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        title_font_color='#ffffff',
        xaxis=dict(title='Payment Behaviour',
                   title_font_color='#ffffff',
                   tickfont_color='#ffffff'),
        yaxis=dict(title='Default Rate (%)',
                   title_font_color='#ffffff',
                   tickfont_color='#ffffff'),
        showlegend=False,
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            "<div class='success-box'>"
            "<p style='color:#ffffff !important'>✅ <b>Never Late</b><br>"
            "Lowest default risk<br>Safe to approve</p></div>",
            unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            "<div class='insight-box'>"
            "<p style='color:#ffffff !important'>⚠️ <b>Sometimes Late</b><br>"
            "Medium risk<br>Review carefully</p></div>",
            unsafe_allow_html=True
        )
    with col_c:
        st.markdown(
            "<div class='warning-box'>"
            "<p style='color:#ffffff !important'>🔴 <b>Often Late</b><br>"
            "Highest default risk<br>Consider declining</p></div>",
            unsafe_allow_html=True
        )

# ============================================================
# TAB 3
# ============================================================
with tab3:
    st.markdown(
        "<h3 style='color:#ffffff !important'>🏦 Credit Profile</h3>",
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)

    with col_a:
        contract_data = conn.execute("""
            SELECT NAME_CONTRACT_TYPE, COUNT(*) AS count,
                   ROUND(AVG(TARGET)*100,2) AS default_rate
            FROM mart_applicant_features
            GROUP BY NAME_CONTRACT_TYPE
        """).fetchdf()
        fig = px.pie(
            contract_data, values='count',
            names='NAME_CONTRACT_TYPE',
            title='📋 Applicants by Contract Type',
            color_discrete_sequence=px.colors.sequential.Plasma,
            template=TEMPLATE,
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            title_font_color='#ffffff',
            legend=dict(font_color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        risk_band = conn.execute("""
            SELECT credit_risk_band,
                   COUNT(*) AS applicants,
                   ROUND(AVG(TARGET)*100,2) AS default_rate
            FROM mart_applicant_features
            GROUP BY credit_risk_band
            ORDER BY default_rate DESC
        """).fetchdf()
        fig2 = px.bar(
            risk_band, x='credit_risk_band', y='default_rate',
            title='🎯 Default Rate by Risk Band',
            color='default_rate',
            color_continuous_scale='RdYlGn_r',
            text='default_rate',
            template=TEMPLATE
        )
        fig2.update_traces(
            texttemplate='<b>%{text}%</b>',
            textposition='outside'
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            title_font_color='#ffffff',
            showlegend=False,
            xaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff'),
            yaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff')
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "<h3 style='color:#ffffff !important'>🔥 Top 10 Riskiest Segments</h3>",
        unsafe_allow_html=True
    )
    segments = conn.execute(
        "SELECT * FROM analysis_riskiest_segments").fetchdf()
    st.dataframe(segments, use_container_width=True)

# ============================================================
# TAB 4
# ============================================================
with tab4:
    st.markdown(
        "<h3 style='color:#ffffff !important'>🎯 Model Performance</h3>",
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)

    with col_a:
        model_results = pd.DataFrame({
            'Model': ['Baseline', 'Logistic Regression', 'Random Forest ⭐'],
            'AUC Score': [0.5000, 0.6010, 0.7462],
            'vs Baseline': ['—', '+0.1010 ✅', '+0.2462 🏆']
        })
        fig = px.bar(
            model_results, x='Model', y='AUC Score',
            title='🏆 Model AUC Comparison',
            color='AUC Score',
            color_continuous_scale='Blues',
            text='AUC Score',
            template=TEMPLATE
        )
        fig.update_traces(
            texttemplate='<b>%{text:.4f}</b>',
            textposition='outside'
        )
        fig.add_hline(
            y=0.5, line_dash="dash",
            line_color="red",
            annotation_text="Baseline",
            annotation_font_color='#ffffff'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            title_font_color='#ffffff',
            showlegend=False,
            yaxis=dict(range=[0, 0.85],
                       title_font_color='#ffffff',
                       tickfont_color='#ffffff'),
            xaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        feat_imp = pd.DataFrame({
            'Feature': [
                'EXT_SOURCE_2', 'EXT_SOURCE_3', 'EXT_SOURCE_1',
                'years_employed', 'age_years', 'bureau_debt_ratio',
                'inst_late_payment_rate', 'cc_avg_utilisation'
            ],
            'Importance': [
                0.2676, 0.2544, 0.0949, 0.0750,
                0.0484, 0.0420, 0.0380, 0.0310
            ]
        })
        fig2 = px.bar(
            feat_imp, x='Importance', y='Feature',
            orientation='h',
            title='🔍 Top Features (Random Forest)',
            color='Importance',
            color_continuous_scale='Blues',
            template=TEMPLATE
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            title_font_color='#ffffff',
            showlegend=False,
            yaxis=dict(autorange='reversed',
                       title_font_color='#ffffff',
                       tickfont_color='#ffffff'),
            xaxis=dict(title_font_color='#ffffff',
                       tickfont_color='#ffffff')
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "<h3 style='color:#ffffff !important'>💼 Business Cost Analysis</h3>",
        unsafe_allow_html=True
    )
    col_x, col_y, col_z = st.columns(3)
    col_x.metric("✅ Defaults Caught", "3,357", "True Positives")
    col_y.metric("❌ Missed Defaults", "1,608", "False Negatives")
    col_z.metric("💰 Bad Debt Prevented", "GHS 804M", "Estimated savings")

    st.markdown(
        "<div class='success-box'>"
        "<p style='color:#ffffff !important'>🏆 <b>Conclusion:</b> "
        "Our Random Forest model achieves AUC = 0.7462, catching 3,357 "
        "true defaulters and preventing an estimated GHS 804,000,000 "
        "in bad debt.</p></div>",
        unsafe_allow_html=True
    )

# ============================================================
# TAB 5
# ============================================================
with tab5:
    st.markdown(
        "<h3 style='color:#ffffff !important'>📈 Default Rate by Age (LAG)</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='insight-box'>💡 Uses the <b>LAG SQL window function</b> "
        "to show how default rates change across applicant ages.</div>",
        unsafe_allow_html=True
    )

    age_data = conn.execute(
        "SELECT * FROM analysis_age_default_trend "
        "WHERE age BETWEEN 20 AND 70"
    ).fetchdf()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=age_data['age'],
        y=age_data['default_rate'],
        mode='lines',
        name='Default Rate %',
        line=dict(color='#00d4ff', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=age_data['age'],
        y=age_data['change_vs_prev_age'],
        mode='lines',
        name='YoY Change (LAG)',
        line=dict(color='#ff6b6b', width=2, dash='dot'),
        yaxis='y2'
    ))
    fig.update_layout(
        title='📈 Default Rate by Age with LAG Analysis',
        template=TEMPLATE,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        title_font_color='#ffffff',
        xaxis=dict(title='Applicant Age (Years)',
                   title_font_color='#ffffff',
                   tickfont_color='#ffffff'),
        yaxis=dict(title='Default Rate (%)',
                   title_font_color='#ffffff',
                   tickfont_color='#ffffff'),
        yaxis2=dict(
            title='YoY Change (%)',
            overlaying='y', side='right',
            title_font_color='#ffffff',
            tickfont_color='#ffffff'
        ),
        legend=dict(font_color='#ffffff',
                    bgcolor='rgba(255,255,255,0.05)'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='insight-box'>"
        "<p style='color:#ffffff !important'>📌 <b>Finding:</b> Younger "
        "applicants (20-30) show significantly higher default rates. "
        "Risk decreases steadily with age, with the lowest rates seen "
        "in applicants aged 50-65.</p></div>",
        unsafe_allow_html=True
    )

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(
    "<p style='text-align:center; color:#a0aec0 !important; font-size:0.85rem'>"
    "💳 CreditGuard AI · Group 1 · Thrive Africa / Ishango.ai · "
    "Analytics Engineering Capstone · March 2026 · "
    "Data: Home Credit Default Risk (Kaggle) · "
    "Tools: DuckDB · Python · Streamlit</p>",
    unsafe_allow_html=True
)