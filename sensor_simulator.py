"""
COUCHE EDGE - Simulateur de Capteurs IoT pour Sous-stations Électriques
Simule les capteurs de tension (V) et courant (I) avec anomalies
"""
import json
import time
import random
import numpy as np
from kafka import KafkaProducer
from datetime import datetime
import argparse

class ElectricalSensorSimulator:
    """
    Simule un capteur IoT dans une sous-station électrique rurale (SOMELEC)
    """
    def __init__(self, village_id, kafka_server='localhost:9092'):
        self.village_id = village_id
        self.kafka_server = kafka_server
        self.topic = f'electrical-data-village-{village_id}'
        
        # Paramètres normaux pour ce village
        self.normal_voltage = 220.0  # Volts (normal)
        self.normal_current = 15.0   # Ampères (normal)
        
        # Configuration Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None
        )
        
        print(f"✓ Capteur IoT Village {village_id} initialisé")
        print(f"  Sous-station: Village-{village_id}")
        print(f"  Topic Kafka: {self.topic}")
        print(f"  Paramètres normaux: V={self.normal_voltage}V, I={self.normal_current}A")
    
    def generate_normal_reading(self):
        """Génère une lecture normale avec légère variation"""
        voltage = np.random.normal(self.normal_voltage, 3.0)  # σ=3V
        current = np.random.normal(self.normal_current, 1.5)  # σ=1.5A
        power = voltage * current  # Puissance (W)
        
        return {
            'voltage': max(0, voltage),
            'current': max(0, current),
            'power': max(0, power),
            'anomaly': 0  # Normal
        }
    
    def generate_anomaly_reading(self, anomaly_type):
        """
        Génère une anomalie spécifique
        Types:
        - 'overvoltage': Surtension (risque équipement)
        - 'undervoltage': Sous-tension (baisse qualité)
        - 'overcurrent': Surintensité (surcharge, risque incendie)
        - 'power_loss': Perte de puissance (panne partielle)
        """
        if anomaly_type == 'overvoltage':
            voltage = np.random.normal(260, 10)  # 240-280V
            current = np.random.normal(self.normal_current, 1.5)
            label = 1
            
        elif anomaly_type == 'undervoltage':
            voltage = np.random.normal(180, 10)  # 160-200V
            current = np.random.normal(self.normal_current, 1.5)
            label = 2
            
        elif anomaly_type == 'overcurrent':
            voltage = np.random.normal(self.normal_voltage, 3)
            current = np.random.normal(35, 5)  # 25-45A (surcharge!)
            label = 3
            
        elif anomaly_type == 'power_loss':
            voltage = np.random.normal(150, 15)  # Très bas
            current = np.random.normal(5, 2)     # Très bas
            label = 4
        else:
            return self.generate_normal_reading()
        
        power = voltage * current
        
        return {
            'voltage': max(0, voltage),
            'current': max(0, current),
            'power': max(0, power),
            'anomaly': label
        }
    
    def generate_reading(self):
        """Génère une lecture avec probabilité d'anomalie"""
        # 85% normal, 15% anomalies variées
        rand = random.random()
        
        if rand < 0.85:
            data = self.generate_normal_reading()
            status = "✓ Normal"
        elif rand < 0.90:
            data = self.generate_anomaly_reading('overvoltage')
            status = "⚠️ SURTENSION"
        elif rand < 0.94:
            data = self.generate_anomaly_reading('undervoltage')
            status = "⚠️ SOUS-TENSION"
        elif rand < 0.97:
            data = self.generate_anomaly_reading('overcurrent')
            status = "🔥 SURCHARGE"
        else:
            data = self.generate_anomaly_reading('power_loss')
            status = "❌ PANNE"
        
        # Ajouter métadonnées
        data['village_id'] = self.village_id
        data['timestamp'] = datetime.now().isoformat()
        data['status'] = status
        
        return data, status
    
    def start_streaming(self, duration=300, interval=2):
        """
        Démarre la simulation de streaming
        
        Args:
            duration: Durée totale en secondes (300s = 5min)
            interval: Intervalle entre lectures en secondes
        """
        print(f"\n🚀 Démarrage streaming capteur Village {self.village_id}")
        print(f"  Durée: {duration}s")
        print(f"  Intervalle: {interval}s")
        print("-" * 70)
        
        count = 0
        anomaly_count = 0
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration:
                # Générer lecture
                reading, status = self.generate_reading()
                
                # Envoyer vers Kafka
                self.producer.send(
                    self.topic,
                    key=f'village-{self.village_id}',
                    value=reading
                )
                
                count += 1
                if reading['anomaly'] > 0:
                    anomaly_count += 1
                
                # Afficher toutes les 5 lectures
                if count % 5 == 0:
                    print(f"[{count:04d}] {status} | "
                          f"V: {reading['voltage']:.1f}V | "
                          f"I: {reading['current']:.1f}A | "
                          f"P: {reading['power']:.0f}W")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Arrêt du capteur...")
        finally:
            self.producer.flush()
            self.producer.close()
            
            # Statistiques finales
            print(f"\n{'='*70}")
            print(f"📊 STATISTIQUES - Village {self.village_id}")
            print(f"{'='*70}")
            print(f"  Total lectures: {count}")
            print(f"  Lectures normales: {count - anomaly_count} ({(count-anomaly_count)/count*100:.1f}%)")
            print(f"  Anomalies détectées: {anomaly_count} ({anomaly_count/count*100:.1f}%)")
            print(f"{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(
        description='Simulateur de capteurs IoT pour sous-stations électriques (SOMELEC)'
    )
    parser.add_argument('--village-id', type=int, required=True,
                        help='ID du village (1, 2, 3, etc.)')
    parser.add_argument('--broker', type=str, default='localhost:9092',
                        help='Adresse du broker Kafka')
    parser.add_argument('--duration', type=int, default=300,
                        help='Durée de simulation en secondes (défaut: 300)')
    parser.add_argument('--interval', type=float, default=2.0,
                        help='Intervalle entre lectures en secondes (défaut: 2)')
    
    args = parser.parse_args()
    
    # Créer et démarrer le simulateur
    simulator = ElectricalSensorSimulator(
        village_id=args.village_id,
        kafka_server=args.broker
    )
    
    simulator.start_streaming(
        duration=args.duration,
        interval=args.interval
    )

if __name__ == '__main__':
    main()
