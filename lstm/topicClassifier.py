from tensorflow import keras
model = keras.models.load_model('tib_topic_model')
model.summary()
