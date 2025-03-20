import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from .monitoring import MetricsCollector
from datetime import datetime
import logging

logger = logging.getLogger('kafka_deployer.tuning')

class TuningEngine:
    def __init__(self, config_path='config/ml_config.yml'):
        self.model = RandomForestRegressor(n_estimators=100)
        self.scaler = StandardScaler()
        self.config = self._load_config(config_path)
        self._initialize_model()
        
    def _load_config(self, path):
        with open(path) as f:
            return yaml.safe_load(f)
    
    def _initialize_model(self):
        try:
            self.model = joblib.load(self.config['model_path'])
            logger.info("Loaded pre-trained tuning model")
        except FileNotFoundError:
            logger.info("No pre-trained model found, initializing new model")
    
    def detect_workload_pattern(self, metrics):
        network_ratio = metrics['network_throughput'] / (metrics['disk_io'] + 1e-6)
        if network_ratio > 5 and metrics['request_rate'] > 1000:
            return "streaming"
        elif metrics['batch_size'] > 10000 and metrics['consumer_lag'] < 100:
            return "batch"
        return "hybrid"
    
    def optimize_configuration(self, metrics, cloud_pricing):
        workload_type = self.detect_workload_pattern(metrics)
        X = self._prepare_features(metrics, cloud_pricing, workload_type)
        
        if not self.model.trained:
            return self._get_fallback_config(workload_type)
            
        predicted_params = self.model.predict(X)
        return self._map_predictions_to_config(predicted_params)
    
    def _prepare_features(self, metrics, pricing, workload_type):
        features = [
            metrics['cpu_usage'],
            metrics['memory_usage'],
            metrics['disk_io'],
            metrics['network_throughput'],
            pricing['cost_per_core'],
            pricing['disk_perf'],
            1 if workload_type == "streaming" else 0,
            metrics['consumer_lag']
        ]
        return self.scaler.transform([features])
    
    def _map_predictions_to_config(self, predictions):
        return {
            'num.io.threads': int(predictions[0]),
            'log.flush.interval.messages': int(predictions[1]),
            'num.network.threads': int(predictions[2]),
            'log.retention.hours': int(predictions[3])
        }
    
    def _get_fallback_config(self, workload_type):
        presets = {
            'streaming': {
                'num.io.threads': 8,
                'log.flush.interval.messages': 10000,
                'num.network.threads': 5,
                'log.retention.hours': 72
            },
            'batch': {
                'num.io.threads': 12,
                'log.flush.interval.messages': 50000,
                'num.network.threads': 3,
                'log.retention.hours': 168
            }
        }
        return presets.get(workload_type, presets['hybrid'])

class ConfigVersioner:
    def __init__(self):
        self.version_history = []
    
    def track_change(self, old_config, new_config, metrics):
        self.version_history.append({
            'timestamp': datetime.now(),
            'old_config': old_config,
            'new_config': new_config,
            'metrics_snapshot': metrics,
            'performance_delta': self._calculate_performance_delta(metrics)
        })
    
    def rollback_config(self, steps=1):
        if len(self.version_history) >= steps:
            return self.version_history[-steps-1]['old_config']
        return None
    
    def _calculate_performance_delta(self, metrics):
        return metrics.get('throughput', 0) / max(metrics.get('latency', 1), 1)

