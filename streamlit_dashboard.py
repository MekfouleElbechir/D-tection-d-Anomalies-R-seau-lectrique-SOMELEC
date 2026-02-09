"""
DASHBOARD STREAMLIT - Surveillance en Temps Réel
Interface web pour SOMELEC - Monitoring du réseau électrique
"""
import streamlit as st
import json
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from kafka import KafkaConsumer
from datetime import datetime
from collections import deque
import threading

# Configuration de la page
st.set_page_config(
    page_title="SOMELEC - Monitoring Réseau",
    page_icon="⚡",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
    .alert-danger {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        margin: 5px;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        margin: 5px;
    }
    .alert-success {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 10px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation du state
if 'data_buffer' not in st.session_state:
    st.session_state.data_buffer = deque(maxlen=100)
if 'alerts' not in st.session_state:
    st.session_state.alerts = deque(maxlen=20)
if 'global_model' not in st.session_state:
    st.session_state.global_model = None
if 'running' not in st.session_state:
    st.session_state.running = False

# Fonctions Kafka
def consume_electrical_data(kafka_server, villages):
    """Consomme les données électriques"""
    topics = [f'electrical-data-village-{v}' for v in villages]
    
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=[kafka_server],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='dashboard'
    )
    
    for message in consumer:
        data = message.value
        st.session_state.data_buffer.append(data)
        
        # Détecter alertes
        if data['anomaly'] > 0:
            alert = {
                'timestamp': data['timestamp'],
                'village': data['village_id'],
                'type': data['status'],
                'voltage': data['voltage'],
                'current': data['current']
            }
            st.session_state.alerts.append(alert)
        
        if not st.session_state.running:
            break

def consume_global_model(kafka_server):
    """Consomme le modèle global"""
    consumer = KafkaConsumer(
        'global-model',
        bootstrap_servers=[kafka_server],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='dashboard-model'
    )
    
    for message in consumer:
        st.session_state.global_model = message.value
        if not st.session_state.running:
            break

# En-tête
st.markdown('<div class="main-header">⚡ SOMELEC - Surveillance Réseau Électrique</div>', 
            unsafe_allow_html=True)
st.markdown("---")

# Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    kafka_server = st.text_input("Kafka Broker", "kafka:9092")
    num_villages = st.number_input("Nombre de villages", 1, 10, 2)
    villages = list(range(1, num_villages + 1))
    
    st.markdown("---")
    st.header("🔄 Contrôle")
    
    if st.button("▶️ Démarrer Monitoring" if not st.session_state.running else "⏹️ Arrêter"):
        st.session_state.running = not st.session_state.running
        
        if st.session_state.running:
            # Lancer threads de consommation
            thread1 = threading.Thread(
                target=consume_electrical_data, 
                args=(kafka_server, villages),
                daemon=True
            )
            thread2 = threading.Thread(
                target=consume_global_model,
                args=(kafka_server,),
                daemon=True
            )
            thread1.start()
            thread2.start()
    
    st.markdown("---")
    st.info("💡 **Architecture Edge-Fog-Cloud**\n\n"
            "✓ Edge: Capteurs IoT\n"
            "✓ Fog: Agrégation régionale\n"
            "✓ Cloud: Federated Learning")

# Métriques globales
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_readings = len(st.session_state.data_buffer)
    st.metric("📊 Lectures Totales", total_readings)

with col2:
    if st.session_state.data_buffer:
        anomalies = sum(1 for d in st.session_state.data_buffer if d['anomaly'] > 0)
        st.metric("⚠️ Anomalies Détectées", anomalies)
    else:
        st.metric("⚠️ Anomalies Détectées", 0)

with col3:
    if st.session_state.global_model:
        accuracy = st.session_state.global_model['avg_accuracy']
        st.metric("🎯 Accuracy Globale", f"{accuracy:.1%}")
    else:
        st.metric("🎯 Accuracy Globale", "N/A")

with col4:
    if st.session_state.global_model:
        samples = st.session_state.global_model['total_samples']
        st.metric("📈 Échantillons Global", samples)
    else:
        st.metric("📈 Échantillons Global", 0)

st.markdown("---")

# Deux colonnes principales
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Monitoring en Temps Réel")
    
    if st.session_state.data_buffer:
        # Préparer dataframe
        df = pd.DataFrame(list(st.session_state.data_buffer))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Graphique voltage et current
        fig = go.Figure()
        
        for village in villages:
            village_data = df[df['village_id'] == village]
            if not village_data.empty:
                fig.add_trace(go.Scatter(
                    x=village_data['timestamp'],
                    y=village_data['voltage'],
                    mode='lines+markers',
                    name=f'Village {village} - Voltage',
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Tension (V) par Village",
            xaxis_title="Temps",
            yaxis_title="Voltage (V)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique current
        fig2 = go.Figure()
        
        for village in villages:
            village_data = df[df['village_id'] == village]
            if not village_data.empty:
                fig2.add_trace(go.Scatter(
                    x=village_data['timestamp'],
                    y=village_data['current'],
                    mode='lines+markers',
                    name=f'Village {village} - Current',
                    line=dict(width=2)
                ))
        
        fig2.update_layout(
            title="Courant (A) par Village",
            xaxis_title="Temps",
            yaxis_title="Current (A)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
    else:
        st.info("⏳ En attente de données...")

with col_right:
    st.subheader("🚨 Alertes Récentes")
    
    if st.session_state.alerts:
        for alert in list(st.session_state.alerts)[-10:]:
            alert_type = alert['type']
            
            if '🔥' in alert_type or 'SURCHARGE' in alert_type:
                css_class = 'alert-danger'
            elif '⚠️' in alert_type:
                css_class = 'alert-warning'
            else:
                css_class = 'alert-success'
            
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{alert_type}</strong><br>
                Village {alert['village']}<br>
                V: {alert['voltage']:.1f}V | I: {alert['current']:.1f}A<br>
                <small>{alert['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Aucune alerte - Réseau stable")

# Modèle Global
st.markdown("---")
st.subheader("☁️ Modèle Global (Federated Learning)")

if st.session_state.global_model:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Feature Importances:**")
        feature_names = ['Voltage', 'Current', 'Power', 'V_ratio', 'I_ratio']
        importances = st.session_state.global_model['feature_importances']
        
        fig = go.Figure(go.Bar(
            x=importances,
            y=feature_names,
            orientation='h',
            marker=dict(color='lightblue')
        ))
        
        fig.update_layout(
            title="Importance des Features",
            xaxis_title="Importance",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Informations Modèle:**")
        st.json({
            'Ronde': st.session_state.global_model['round'],
            'Accuracy': f"{st.session_state.global_model['avg_accuracy']:.2%}",
            'Total Échantillons': st.session_state.global_model['total_samples'],
            'Dernière MAJ': datetime.fromtimestamp(
                st.session_state.global_model['timestamp']
            ).strftime('%H:%M:%S')
        })
else:
    st.info("⏳ En attente du modèle global...")

# Auto-refresh
if st.session_state.running:
    time.sleep(2)
    st.rerun()
