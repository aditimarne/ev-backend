# fix_models_v2.py
import numpy as np
import tensorflow as tf


def fix_model(input_path, output_path, n_features):
    print(f"Loading {input_path}...")
    
    # Load weights only
    old_model = tf.keras.models.load_model(
        input_path, 
        compile=False,
        custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
    )
    
    # Build new model with same architecture but compatible input
    new_model = tf.keras.Sequential()
    new_model.add(tf.keras.layers.Input(shape=(1, n_features)))
    
    # Copy LSTM/Dense layers from old model (skip InputLayer)
    for layer in old_model.layers:
        if 'input' not in layer.name:
            new_model.add(layer)
    
    # Save new model
    new_model.save(output_path)
    print(f"✅ Saved {output_path}")

# OLA model - 12 features
fix_model(
    "rul2_lstm_model_fixed.h5",
    "rul2_lstm_model_v2.h5",
    12
)

# Revolt model - 10 features  
fix_model(
    "rul1_model_fixed.h5",
    "rul1_model_v2.h5",
    10
)