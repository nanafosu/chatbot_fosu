import json
import random
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD

nltk.download('punkt')
nltk.download('wordnet')

# Load the intents from the JSON file
with open('intents.json', 'r') as file:
    intents = json.load(file)

# Extract data from intents
documents = []
words = []
classes = []
ignore_letters = ['?', '!', '.', ',']

lemmatizer = WordNetLemmatizer()

for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(list(set(words)))

pickle.dump(words, open('words.pk', 'wb'))
pickle.dump(classes, open('classes.pk', 'wb'))

training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

    for w in words:
        bag.append(1 if w in pattern_words else 0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

random.shuffle(training)

# Convert training data to NumPy arrays
train_x = np.array([row[0] for row in training])
train_y = np.array([row[1] for row in training])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))  # Add a comma here
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

initial_learning_rate = 0.01
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate, decay_steps=100000, decay_rate=0.96, staircase=True
)
sgd = tf.keras.optimizers.SGD(learning_rate=lr_schedule, momentum=0.9, nesterov=True)

model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])


hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)  # Change the filepath extension to ".h5"
print('Done')

