"""
🌐 Federated Learning Dashboard - Streamlit Version
Simple, Clean, Works on Windows!
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Federated Learning Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    h1 {
        color: #667eea;
        text-align: center;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .status-active {
        background-color: #10b981;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🌐 Hierarchical Federated Learning Dashboard")
st.markdown("**Real-time Monitoring: Edge → Fog → Cloud**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 3)
    
    st.markdown("---")
    
    st.header("📊 System Info")
    st.info("**Status:** System Active ✅")
    st.info(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    st.header("🎯 Quick Stats")
    st.metric("Total Messages", "1,234", "+56")
    st.metric("Active Nodes", "5", "0")

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📱 Edge Layer",
        value="856",
        delta="12",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="☁️ Fog Layer", 
        value="245",
        delta="5",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="🌍 Cloud Layer",
        value="133",
        delta="3",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="⚡ System Health",
        value="98%",
        delta="2%",
        delta_color="normal"
    )

st.markdown("---")

# Charts section
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Edge Data", "☁️ Fog Analysis", "🌍 Cloud Metrics"])

with tab1:
    st.subheader("System Activity Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate sample data
        np.random.seed(42)
        time_points = pd.date_range(start='2024-01-01', periods=50, freq='H')
        
        df_activity = pd.DataFrame({
            'Time': time_points,
            'Edge Village 1': np.random.randint(50, 150, 50),
            'Edge Village 2': np.random.randint(40, 130, 50),
            'Fog Region': np.random.randint(20, 80, 50),
            'Cloud Global': np.random.randint(10, 50, 50)
        })
        
        fig = px.line(df_activity, x='Time', 
                     y=['Edge Village 1', 'Edge Village 2', 'Fog Region', 'Cloud Global'],
                     title='📈 Message Flow Over Time',
                     labels={'value': 'Messages', 'variable': 'Layer'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pie chart
        layer_data = pd.DataFrame({
            'Layer': ['Edge Village 1', 'Edge Village 2', 'Fog Region', 'Cloud Global'],
            'Count': [428, 428, 245, 133]
        })
        
        fig2 = px.pie(layer_data, values='Count', names='Layer',
                      title='📊 Distribution by Layer',
                      color_discrete_sequence=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'])
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("📱 Edge Layer - Villages Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏘️ Village 1 - Electrical Data**")
        
        # Sample data
        village1_data = pd.DataFrame({
            'Timestamp': pd.date_range(start='2024-01-01', periods=20, freq='5min'),
            'Voltage (V)': np.random.uniform(220, 240, 20),
            'Current (A)': np.random.uniform(5, 15, 20),
            'Power (W)': np.random.uniform(1000, 3000, 20)
        })
        
        fig = px.line(village1_data, x='Timestamp', y='Power (W)',
                     title='Power Consumption - Village 1')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(village1_data.tail(5), use_container_width=True)
    
    with col2:
        st.markdown("**🏘️ Village 2 - Electrical Data**")
        
        village2_data = pd.DataFrame({
            'Timestamp': pd.date_range(start='2024-01-01', periods=20, freq='5min'),
            'Voltage (V)': np.random.uniform(220, 240, 20),
            'Current (A)': np.random.uniform(5, 15, 20),
            'Power (W)': np.random.uniform(1000, 3000, 20)
        })
        
        fig = px.line(village2_data, x='Timestamp', y='Power (W)',
                     title='Power Consumption - Village 2')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(village2_data.tail(5), use_container_width=True)

with tab3:
    st.subheader("☁️ Fog Layer - Regional Aggregation")
    
    # Model weights comparison
    model_rounds = list(range(1, 11))
    accuracy = [0.65, 0.72, 0.78, 0.82, 0.85, 0.87, 0.89, 0.90, 0.91, 0.92]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=model_rounds, y=accuracy,
                            mode='lines+markers',
                            name='Model Accuracy',
                            line=dict(color='#8b5cf6', width=3),
                            marker=dict(size=10)))
    fig.update_layout(
        title='🎯 Model Accuracy Improvement',
        xaxis_title='Training Round',
        yaxis_title='Accuracy',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Latest Fog Model Update**\n\nRound: 10\nAccuracy: 92%\nNodes: 2")
    with col2:
        st.success("**Convergence Status**\n\nStatus: Good ✅\nDelta: +1%\nNext Update: 2min")

with tab4:
    st.subheader("🌍 Cloud Layer - Global Model")
    
    # Global metrics
    metrics_df = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
        'Value': [0.92, 0.89, 0.91, 0.90],
        'Target': [0.95, 0.92, 0.93, 0.92]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current', x=metrics_df['Metric'], y=metrics_df['Value'],
                        marker_color='#10b981'))
    fig.add_trace(go.Bar(name='Target', x=metrics_df['Metric'], y=metrics_df['Target'],
                        marker_color='#f59e0b'))
    fig.update_layout(
        title='📊 Global Model Performance Metrics',
        barmode='group',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Latest Global Model Update")
    
    update_data = {
        'Parameter': ['Learning Rate', 'Batch Size', 'Epochs', 'Convergence'],
        'Value': ['0.001', '32', '10', 'Achieved ✅']
    }
    st.table(pd.DataFrame(update_data))

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📡 Data Sources**")
    st.markdown("- Edge: 2 Villages")
    st.markdown("- Fog: 1 Region")
    st.markdown("- Cloud: 1 Global")

with col2:
    st.markdown("**⚙️ System Architecture**")
    st.markdown("- Hierarchical FL")
    st.markdown("- Real-time Aggregation")
    st.markdown("- Kafka Streaming")

with col3:
    st.markdown("**📊 Performance**")
    st.markdown("- Uptime: 99.8%")
    st.markdown("- Latency: <100ms")
    st.markdown("- Throughput: 1K msg/s")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()