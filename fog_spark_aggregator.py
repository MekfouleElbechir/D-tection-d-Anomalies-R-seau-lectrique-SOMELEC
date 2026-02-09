"""
COUCHE FOG avec SPARK - Agrégation Régionale
Utilise Spark pour agréger les modèles Edge
"""
import json
import time
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, ArrayType
from kafka import KafkaProducer
import argparse

class FogSparkAggregator:
    """
    Nœud Fog avec Spark pour agrégation régionale
    """
    def __init__(self, region_id, num_villages=2, kafka_server='localhost:9092'):
        self.region_id = region_id
        self.num_villages = num_villages
        self.kafka_server = kafka_server
        self.input_topic = 'edge-model-weights'
        self.output_topic = 'fog-aggregated-weights'
        self.round = 0
        
        # Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Spark Session
        self.spark = SparkSession.builder \
            .appName(f"FogAggregator-Region-{region_id}") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        print(f"✓ Nœud Fog Spark Région {region_id} initialisé")
        print(f"  Villages attendus: {num_villages}")
        print(f"  Spark Session: Actif")
    
    def aggregate_models(self, batch_df, batch_id):
        """
        Agrège les modèles d'un micro-batch Spark
        """
        print(f"\n{'='*70}")
        print(f"🌫️  AGRÉGATION FOG - Région {self.region_id} - Batch {batch_id}")
        print(f"{'='*70}")
        
        if batch_df.isEmpty():
            print("⚠️  Batch vide")
            return
        
        # Collecter les données
        models_data = batch_df.collect()
        
        print(f"  Modèles reçus: {len(models_data)}")
        
        # Vérifier qu'on a assez de villages
        if len(models_data) < self.num_villages:
            print(f"⚠️  Seulement {len(models_data)}/{self.num_villages} villages")
            # On continue quand même avec ce qu'on a
        
        # Calculer total échantillons
        total_samples = sum(row['n_samples'] for row in models_data)
        
        if total_samples == 0:
            print("❌ Total échantillons = 0")
            return
        
        # Agréger feature importances (moyenne pondérée)
        agg_importances = np.zeros(5)
        agg_mean = np.zeros(5)
        agg_std = np.zeros(5)
        
        for row in models_data:
            weight = row['n_samples'] / total_samples
            
            # Parse les strings JSON si nécessaire
            importances = row['model_params']['feature_importances']
            if isinstance(importances, str):
                importances = json.loads(importances)
            
            scaler_mean = row['model_params']['scaler_mean']
            if isinstance(scaler_mean, str):
                scaler_mean = json.loads(scaler_mean)
            
            scaler_std = row['model_params']['scaler_std']
            if isinstance(scaler_std, str):
                scaler_std = json.loads(scaler_std)
            
            agg_importances += weight * np.array(importances)
            agg_mean += weight * np.array(scaler_mean)
            agg_std += weight * np.array(scaler_std)
        
        # Calculer accuracy moyenne
        avg_accuracy = np.mean([row['accuracy'] for row in models_data])
        
        # Créer modèle agrégé
        aggregated_model = {
            'region_id': self.region_id,
            'round': self.round,
            'num_villages': len(models_data),
            'total_samples': total_samples,
            'avg_accuracy': float(avg_accuracy),
            'feature_importances': agg_importances.tolist(),
            'scaler_mean': agg_mean.tolist(),
            'scaler_std': agg_std.tolist(),
            'timestamp': time.time()
        }
        
        # Afficher résultats
        print(f"\n📊 Résultats Agrégation:")
        print(f"  Villages: {len(models_data)}/{self.num_villages}")
        print(f"  Total échantillons: {total_samples}")
        print(f"  Accuracy moyenne: {avg_accuracy:.2%}")
        print(f"  Feature Importances:")
        feature_names = ['Voltage', 'Current', 'Power', 'V_ratio', 'I_ratio']
        for name, imp in zip(feature_names, agg_importances):
            print(f"    {name:10s}: {imp:.4f}")
        
        # Publier via Kafka
        self.producer.send(self.output_topic, value=aggregated_model)
        self.producer.flush()
        
        print(f"\n📤 Modèle régional publié!")
        print(f"{'='*70}\n")
        
        self.round += 1
    
    def start_aggregation(self, window_duration=90):
        """
        Démarre l'agrégation avec Spark Streaming
        """
        print(f"\n🚀 Démarrage Fog Spark - Région {self.region_id}")
        print(f"  Window duration: {window_duration} secondes")
        print("-" * 70)
        
        # Schéma pour model_params (nested)
        model_params_schema = StructType([
            StructField("feature_importances", ArrayType(DoubleType()), True),
            StructField("scaler_mean", ArrayType(DoubleType()), True),
            StructField("scaler_std", ArrayType(DoubleType()), True)
        ])
        
        # Schéma principal
        schema = StructType([
            StructField("village_id", IntegerType(), True),
            StructField("iteration", IntegerType(), True),
            StructField("model_params", model_params_schema, True),
            StructField("n_samples", IntegerType(), True),
            StructField("accuracy", DoubleType(), True),
            StructField("timestamp", DoubleType(), True)
        ])
        
        # Lire depuis Kafka
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
        
        # Traiter par batch
        query = parsed_df \
            .writeStream \
            .foreachBatch(self.aggregate_models) \
            .trigger(processingTime=f'{window_duration} seconds') \
            .start()
        
        print(f"✓ Spark Streaming actif!")
        print(f"  En attente de modèles Edge...")
        
        try:
            query.awaitTermination()
        except KeyboardInterrupt:
            print("\n⏹️  Arrêt Fog Spark...")
            query.stop()
            self.spark.stop()
            self.producer.close()

def main():
    parser = argparse.ArgumentParser(
        description='Fog Aggregator avec Spark'
    )
    parser.add_argument('--region-id', type=int, default=1,
                        help='ID de la région')
    parser.add_argument('--num-villages', type=int, default=2,
                        help='Nombre de villages')
    parser.add_argument('--broker', type=str, default='localhost:9092',
                        help='Kafka broker')
    parser.add_argument('--window-duration', type=int, default=90,
                        help='Durée fenêtre agrégation (secondes)')
    
    args = parser.parse_args()
    
    aggregator = FogSparkAggregator(
        region_id=args.region_id,
        num_villages=args.num_villages,
        kafka_server=args.broker
    )
    
    aggregator.start_aggregation(window_duration=args.window_duration)

if __name__ == '__main__':
    main()
