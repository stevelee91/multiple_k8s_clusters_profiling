import numpy as np

from keras.utils import np_utils
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Activation
import tensorflow as tf
(x_train, y_train), (x_test, y_test)  = tf.keras.datasets.mnist.load_data('mnist.npz')

x_train = x_train.reshape(60000, 784).astype('float32') / 255.0
x_test = x_test.reshape(10000, 784).astype('float32') / 255.0
y_train = np_utils.to_categorical(y_train)
y_test = np_utils.to_categorical(y_test)

model = Sequential()
model.add(Dense(units=64, input_dim=28*28, activation='relu'))
model.add(Dense(units=10, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
hist = model.fit(x_train, y_train, epochs=5, batch_size=32)

print('## training loss and acc ##')
print(hist.history['loss'])
#print(hist.history['acc'])

loss_and_metrics = model.evaluate(x_test, y_test, batch_size=32)
print('## evaluation loss and_metrics ##')
print(loss_and_metrics)

xhat = x_test[0:1]
yhat = model.predict(xhat)
print('## yhat ##')
print(np.argmax(yhat))
print(np.argmax(y_test[0:1]))
