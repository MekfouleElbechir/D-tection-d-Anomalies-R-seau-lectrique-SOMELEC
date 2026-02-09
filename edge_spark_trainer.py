"""
COUCHE EDGE avec SPARK STREAMING - Entraînement Local
Utilise Spark Structured Streaming pour lire depuis Kafka
"""
import json
import time
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from kafka import KafkaProducer
import argparse

class EdgeSparkTrainer:
    """
    Nœud Edge avec Spark Streaming pour entraînement local
    """
    def __init__(self, village_id, kafka_server='localhost:9092'):
        self.village_id = village_id
        self.kafka_server = kafka_server
        self.input_topic = f'electrical-data-village-{village_id}'
        self.weights_topic = 'edge-model-weights'
        
        # Modèle ML
        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.iteration = 0
        self.is_trained = False
        
        # Kafka Producer pour publier poids
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Créer Spark Session
        self.spark = SparkSession.builder \
            .appName(f"EdgeTrainer-Village-{village_id}") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
            .config("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", "false") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        print(f"✓ Nœud Edge Spark Village {village_id} initialisé")
        print(f"  Spark Session: Actif")
        print(f"  Input Topic: {self.input_topic}")
        print(f"  Output Topic: {self.weights_topic}")
    
    def extract_features(self, row):
        """Extrait features d'une ligne"""
        return [
            row['voltage'],
            row['current'],
            row['power'],
            row['voltage'] / 220.0,
            row['current'] / 15.0
        ]
    
    def train_model(self, batch_df, batch_id):
        """
        Fonction appelée pour chaque micro-batch de Spark Streaming
        """
        print(f"\n{'='*70}")
        print(f"📦 MICRO-BATCH {batch_id} - Village {self.village_id}")
        print(f"{'='*70}")
        
        if batch_df.isEmpty():
            print("⚠️  Batch vide, skip...")
            return
        
        # Collecter les données
        data = batch_df.collect()
        n_samples = len(data)
        
        print(f"  Échantillons reçus: {n_samples}")
        
        if n_samples < 20:
            print(f"⚠️  Pas assez de données ({n_samples} < 20)")
            return
        
        # Préparer features et labels
        X = np.array([self.extract_features(row) for row in data])
        y = np.array([row['anomaly'] for row in data])
        
        # Normaliser
        X_scaled = self.scaler.fit_transform(X)
        
        # Entraîner Random Forest
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculer métriques
        predictions = self.model.predict(X_scaled)
        accuracy = np.mean(predictions == y)
        probas = self.model.predict_proba(X_scaled)
        confidence = np.mean(np.max(probas, axis=1))
        
        self.iteration += 1
        
        # Afficher résultats
        print(f"\n🎯 ENTRAÎNEMENT - Itération {self.iteration}")
        print(f"  Accuracy: {accuracy:.2%}")
        print(f"  Confiance: {confidence:.2%}")
        
        # Distribution classes
        unique, counts = np.unique(y, return_counts=True)
        class_names = {0: 'Normal', 1: 'Surtension', 2: 'Sous-tension',
                      3: 'Surcharge', 4: 'Panne'}
        print(f"  Distribution:")
        for cls, count in zip(unique, counts):
            print(f"    {class_names.get(cls, 'Inconnu')}: {count} ({count/n_samples*100:.1f}%)")
        
        # Publier poids via Kafka
        self.publish_weights(accuracy, n_samples)
        
        print(f"{'='*70}\n")
    
    def publish_weights(self, accuracy, n_samples):
        """Publie les poids via Kafka"""
        weights_data = {
            'village_id': self.village_id,
            'iteration': self.iteration,
            'model_params': {
                'feature_importances': self.model.feature_importances_.tolist(),
                'scaler_mean': self.scaler.mean_.tolist(),
                'scaler_std': self.scaler.scale_.tolist()
            },
            'n_samples': n_samples,
            'accuracy': accuracy,
            'timestamp': time.time()
        }
        
        self.producer.send(self.weights_topic, value=weights_data)
        self.producer.flush()
        
        print(f"📤 Poids publiés vers Kafka")
    
    def start_streaming(self, batch_duration=30):
        """
        Démarre Spark Structured Streaming
        """
        print(f"\n🚀 Démarrage Spark Streaming - Village {self.village_id}")
        print(f"  Batch duration: {batch_duration} secondes")
        print("-" * 70)
        
        # Définir le schéma des données
        schema = StructType([
            StructField("village_id", IntegerType(), True),
            StructField("voltage", DoubleType(), True),
            StructField("current", DoubleType(), True),
            StructField("power", DoubleType(), True),
            StructField("anomaly", IntegerType(), True),
            StructField("timestamp", StringType(), True),
            StructField("status", StringType(), True)
        ])
        
        # Lire depuis Kafka avec Spark Streaming
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_server) \
            .option("subscribe", self.input_topic) \
            .option("startingOffsets", "latest") \
            .load()
        
        # Parser JSON
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # Traiter chaque micro-batch
        query = parsed_df \
            .writeStream \
            .foreachBatch(self.train_model) \
            .trigger(processingTime=f'{batch_duration} seconds') \
            .start()
        
        print(f"✓ Spark Streaming actif!")
        print(f"  En attente de données sur: {self.input_topic}")
        
        try:
            query.awaitTermination()
        except KeyboardInterrupt:
            print("\n⏹️  Arrêt Spark Streaming...")
            query.stop()
            self.spark.stop()
            self.producer.close()

def main():
    parser = argparse.ArgumentParser(
        description='Edge Trainer avec Spark Streaming'
    )
    parser.add_argument('--village-id', type=int, required=True,
                        help='ID du village')
    parser.add_argument('--broker', type=str, default='localhost:9092',
                        help='Kafka broker')
    parser.add_argument('--batch-duration', type=int, default=30,
                        help='Durée du batch (secondes)')
    
    args = parser.parse_args()
    
    trainer = EdgeSparkTrainer(
        village_id=args.village_id,
        kafka_server=args.broker
    )
    
    trainer.start_streaming(batch_duration=args.batch_duration)

if __name__ == '__main__':
    main()
