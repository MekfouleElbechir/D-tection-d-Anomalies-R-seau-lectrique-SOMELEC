"""
🌐 Hierarchical Federated Learning Dashboard
Professional Streamlit Version - Matching HTML Design
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Federated Learning Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match HTML design
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
    }
    
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    /* Header styling */
    h1 {
        color: #667eea !important;
        text-align: center;
        font-size: 2.5rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    /* Status indicator */
    .status-box {
        background: #f0f0f0;
        padding: 10px 20px;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin: 0 auto 2rem auto;
        width: fit-content;
    }
    
    .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 10px #10b981;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transition: all 0.3s;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 15px 30px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* Info cards */
    .info-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #667eea;
        margin-bottom: 20px;
    }
    
    .info-card h4 {
        color: #667eea;
        margin-bottom: 15px;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding-top: 20px;
        margin-top: 30px;
        border-top: 2px solid #e0e0e0;
        color: #666;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state for data
if 'edge_count' not in st.session_state:
    st.session_state.edge_count = 856
    st.session_state.fog_count = 245
    st.session_state.cloud_count = 133
    st.session_state.last_update = datetime.now()

# Helper functions
def generate_time_labels(count):
    """Generate time labels for charts"""
    now = datetime.now()
    return [(now - timedelta(minutes=count-i-1)).strftime('%H:%M') for i in range(count)]

def generate_data(count, min_val, max_val):
    """Generate random data for visualization"""
    return np.random.randint(min_val, max_val, count)

# Header
st.markdown("<h1>🌐 Hierarchical Federated Learning Dashboard</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real-time Monitoring: Edge → Fog → Cloud</p>', unsafe_allow_html=True)

# Status indicator
st.markdown("""
<div class="status-box">
    <span class="status-dot"></span>
    <span>System Active - Live Mode</span>
</div>
""", unsafe_allow_html=True)

# Statistics Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📱 Edge Layer",
        value=st.session_state.edge_count,
        delta="+12",
        help="Messages from Edge Villages"
    )

with col2:
    st.metric(
        label="☁️ Fog Layer",
        value=st.session_state.fog_count,
        delta="+5",
        help="Regional Aggregations"
    )

with col3:
    st.metric(
        label="🌍 Cloud Layer",
        value=st.session_state.cloud_count,
        delta="+3",
        help="Global Model Updates"
    )

with col4:
    st.metric(
        label="⚡ System Health",
        value="98%",
        delta="+2%",
        help="Overall System Health"
    )

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📈 Edge Data", 
    "☁️ Fog Analysis",
    "🌍 Cloud Metrics"
])

# TAB 1: Overview
with tab1:
    st.subheader("System Activity Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Activity timeline
        time_labels = generate_time_labels(20)
        df_activity = pd.DataFrame({
            'Time': time_labels,
            'Edge Village 1': generate_data(20, 50, 150),
            'Edge Village 2': generate_data(20, 40, 130),
        })
        
        fig = px.line(
            df_activity,
            x='Time',
            y=['Edge Village 1', 'Edge Village 2'],
            title='📈 System Activity Timeline',
            labels={'value': 'Messages', 'variable': 'Layer'}
        )
        fig.update_traces(line_shape='spline')
        fig.update_layout(
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution pie chart
        fig2 = go.Figure(data=[go.Pie(
            labels=['Edge Village 1', 'Edge Village 2', 'Fog Region', 'Cloud Global'],
            values=[428, 428, 245, 133],
            marker=dict(colors=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']),
            hole=0.4
        )])
        fig2.update_layout(
            title='📊 Layer Distribution',
            height=400,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)

# TAB 2: Edge Data
with tab2:
    st.subheader("📱 Edge Layer - Villages Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏘️ Village 1 - Power Consumption**")
        time_labels = generate_time_labels(15)
        power_data = generate_data(15, 1000, 3000)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_labels,
            y=power_data,
            mode='lines',
            name='Power (W)',
            line=dict(color='#3b82f6', width=3),
            fill='tonexty',
            fillcolor='rgba(59, 130, 246, 0.2)'
        ))
        fig.update_layout(
            height=300,
            yaxis_title='Power (W)',
            xaxis_title='Time',
            hovermode='x',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Village 1 info
        st.markdown("""
        <div class="info-card">
            <h4>Village 1 Status</h4>
            <div class="info-item">
                <span>Average Voltage:</span>
                <strong>230V</strong>
            </div>
            <div class="info-item">
                <span>Average Current:</span>
                <strong>10.5A</strong>
            </div>
            <div class="info-item">
                <span>Total Power:</span>
                <strong>2.4 kW</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**🏘️ Village 2 - Power Consumption**")
        power_data2 = generate_data(15, 1000, 3000)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=time_labels,
            y=power_data2,
            mode='lines',
            name='Power (W)',
            line=dict(color='#8b5cf6', width=3),
            fill='tonexty',
            fillcolor='rgba(139, 92, 246, 0.2)'
        ))
        fig2.update_layout(
            height=300,
            yaxis_title='Power (W)',
            xaxis_title='Time',
            hovermode='x',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Village 2 info
        st.markdown("""
        <div class="info-card">
            <h4>Village 2 Status</h4>
            <div class="info-item">
                <span>Average Voltage:</span>
                <strong>228V</strong>
            </div>
            <div class="info-item">
                <span>Average Current:</span>
                <strong>9.8A</strong>
            </div>
            <div class="info-item">
                <span>Total Power:</span>
                <strong>2.2 kW</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: Fog Analysis
with tab3:
    st.subheader("☁️ Fog Layer - Regional Aggregation")
    
    # Model accuracy chart
    rounds = list(range(1, 11))
    accuracy = [65, 72, 78, 82, 85, 87, 89, 90, 91, 92]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rounds,
        y=accuracy,
        mode='lines+markers',
        name='Model Accuracy',
        line=dict(color='#8b5cf6', width=4),
        marker=dict(size=10, color='#8b5cf6'),
        fill='tonexty',
        fillcolor='rgba(139, 92, 246, 0.2)'
    ))
    fig.update_layout(
        title='🎯 Model Accuracy Improvement',
        xaxis_title='Training Round',
        yaxis_title='Accuracy (%)',
        height=400,
        yaxis=dict(range=[60, 100]),
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Info cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>Latest Fog Update</h4>
            <div class="info-item">
                <span>Training Round:</span>
                <strong>Round 10</strong>
            </div>
            <div class="info-item">
                <span>Model Accuracy:</span>
                <strong>92.5%</strong>
            </div>
            <div class="info-item">
                <span>Active Nodes:</span>
                <strong>2 Villages</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>Convergence Status</h4>
            <div class="info-item">
                <span>Status:</span>
                <strong style="color: #10b981;">✅ Good</strong>
            </div>
            <div class="info-item">
                <span>Delta:</span>
                <strong>+1.2%</strong>
            </div>
            <div class="info-item">
                <span>Next Update:</span>
                <strong>2 minutes</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: Cloud Metrics
with tab4:
    st.subheader("🌍 Cloud Layer - Global Model")
    
    # Performance metrics
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    current = [92, 89, 91, 90]
    target = [95, 92, 93, 92]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Current',
        x=metrics,
        y=current,
        marker_color='#10b981',
        text=current,
        textposition='auto'
    ))
    fig.add_trace(go.Bar(
        name='Target',
        x=metrics,
        y=target,
        marker_color='#f59e0b',
        text=target,
        textposition='auto'
    ))
    fig.update_layout(
        title='📊 Global Model Performance Metrics',
        barmode='group',
        height=400,
        yaxis=dict(range=[0, 100]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Info cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>Global Model Info</h4>
            <div class="info-item">
                <span>Learning Rate:</span>
                <strong>0.001</strong>
            </div>
            <div class="info-item">
                <span>Batch Size:</span>
                <strong>32</strong>
            </div>
            <div class="info-item">
                <span>Epochs:</span>
                <strong>10</strong>
            </div>
            <div class="info-item">
                <span>Convergence:</span>
                <strong style="color: #10b981;">✅ Achieved</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>System Performance</h4>
            <div class="info-item">
                <span>Uptime:</span>
                <strong>99.8%</strong>
            </div>
            <div class="info-item">
                <span>Latency:</span>
                <strong>&lt;100ms</strong>
            </div>
            <div class="info-item">
                <span>Throughput:</span>
                <strong>1K msg/s</strong>
            </div>
            <div class="info-item">
                <span>Active Regions:</span>
                <strong>1 Region</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div class="footer">
    <p>Last Update: <strong style="color: #667eea;">{current_time}</strong></p>
    <p>Federated Learning System | Edge-Fog-Cloud Architecture</p>
    <p style="margin-top: 10px; font-size: 0.9rem;">
        <strong>Data Sources:</strong> Edge (2 Villages) | Fog (1 Region) | Cloud (1 Global)
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh (optional - comment out if not needed)
# time.sleep(3)
# st.rerun()