"""
train_crop_identifier.py
------------------------
Fast Stage-1 MobileNetV2 Classifier for all 10 Agricultural Crops.
Generates:
  - models/crop_identifier_model.keras
  - models/crop_identifier_labels.json
"""

import json
import os
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------
DATA_DIR = r"D:\major project\crop_id"
TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "valid")
IMG_SIZE = (224, 224)

BATCH_SIZE = 64
EPOCHS = 6
STEPS_PER_EPOCH = 200  # Samples 12,800 images/epoch for fast CPU completion
VAL_STEPS = 50

MODEL_OUT = "models/crop_identifier_model.keras"
LABELS_OUT = "models/crop_identifier_labels.json"

os.makedirs("models", exist_ok=True)

# ---------------------------------------------------------------
# 1. DATA GENERATORS & PREPROCESSING ([0, 1] RESCALING)
# ---------------------------------------------------------------
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest",
)

val_datagen = ImageDataGenerator(rescale=1.0 / 255.0)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True,
)

val_gen = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False,
)

num_classes = train_gen.num_classes
print(
    f"\n[INFO] Detected {num_classes} Classes: {list(train_gen.class_indices.keys())}"
)

# ---------------------------------------------------------------
# 2. MODEL ARCHITECTURE
# ---------------------------------------------------------------
base_model = MobileNetV2(
    input_shape=(*IMG_SIZE, 3), include_top=False, weights="imagenet"
)
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.3)(x)
predictions = Dense(num_classes, activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# ---------------------------------------------------------------
# 3. TRAINING
# ---------------------------------------------------------------
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True,
    verbose=1,
)

print("\n[INFO] Starting Fast Training (~10-12 minutes)...")
history = model.fit(
    train_gen,
    steps_per_epoch=STEPS_PER_EPOCH,
    validation_data=val_gen,
    validation_steps=VAL_STEPS,
    epochs=EPOCHS,
    callbacks=[early_stop],
)

# ---------------------------------------------------------------
# 4. EXPORT ARTIFACTS
# ---------------------------------------------------------------
model.save(MODEL_OUT)

label_map = {str(v): k for k, v in train_gen.class_indices.items()}
with open(LABELS_OUT, "w") as f:
  json.dump(label_map, f, indent=2)

print("\n" + "=" * 55)
print(f"Model saved successfully -> {MODEL_OUT}")
print(f"Labels saved successfully -> {LABELS_OUT}")
print(f"Final Validation Accuracy: {history.history['val_accuracy'][-1]:.2%}")
print("=" * 55)