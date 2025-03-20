import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import yaml

def load_training_data(path):
    df = pd.read_csv(path)
    features = df[['cpu_usage', 'memory_usage', 'disk_io', 'network_throughput',
                   'cost_per_core', 'disk_perf', 'workload_type', 'consumer_lag']]
    targets = df[['io_threads', 'flush_interval', 'network_threads', 'retention_hours']]
    return features, targets

def train_model(config_path='config/ml_config.yml'):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    X, y = load_training_data(config['training_data'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = RandomForestRegressor(n_estimators=config['n_estimators'])
    model.fit(X_train, y_train)
    
    joblib.dump(model, config['model_path'])
    
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    print(f"Model trained with MSE: {mse}")
    return model

if __name__ == "__main__":
    train_model()

