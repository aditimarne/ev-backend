# save this as fix_models.py in your backend folder
import tensorflow as tf
from battery_app.storage_utils import get_file_from_gridfs

# Fix rul1_model.h5 (Revolt)
print("Fixing rul1_model.h5...")
old_path = get_file_from_gridfs("rul1_model.h5")
old_model = tf.keras.models.load_model(old_path, compile=False)
old_model.save("rul1_model_fixed.h5")
print("✅ rul1_model_fixed.h5 saved")

# Fix rul2_lstm_model.h5 (OLA)
print("Fixing rul2_lstm_model.h5...")
old_path2 = get_file_from_gridfs("rul2_lstm_model.h5")
old_model2 = tf.keras.models.load_model(old_path2, compile=False)
old_model2.save("rul2_lstm_model_fixed.h5")
print("✅ rul2_lstm_model_fixed.h5 saved")