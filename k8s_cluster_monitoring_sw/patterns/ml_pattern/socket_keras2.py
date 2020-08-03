import numpy as np

from keras.utils import np_utils
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Activation
import tensorflow as tf
import socket 

# 통신 정보 설정
IP = ''
PORT = 8080
SIZE = 1024
ADDR = (IP, PORT)

# 서버 소켓 설정
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind(ADDR)  # 주소 바인딩
    server_socket.listen()  # 클라이언트의 요청을 받을 준비

    # 무한루프 진입
    while True:
        client_socket, client_addr = server_socket.accept()  # 수신대기, 접속한 클라이언트 정보 (소켓, 주소) 반환
        msg = client_socket.recv(SIZE)  # 클라이언트가 보낸 메시지 반환
        print("[{}] message : {}".format(client_addr,msg))  # 클라이언트가 보낸 메시지 출력
        print(msg)
        msg_dec = msg.decode()
        print(msg_dec)

        #client_socket.sendall(result.encode())  # 클라이언트에게 응답

        (x_train, y_train), (x_test, y_test)  = tf.keras.datasets.mnist.load_data('mnist.npz')

        x_train = x_train.reshape(60000, 784).astype('float32') / 255.0
        x_test = x_test.reshape(10000, 784).astype('float32') / 255.0
        y_train = np_utils.to_categorical(y_train)
        y_test = np_utils.to_categorical(y_test)

        model = Sequential()
        model.add(Dense(units=64, input_dim=28*28, activation='relu'))
        model.add(Dense(units=10, activation='softmax'))

        model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
        hist = model.fit(x_train, y_train, epochs=int(msg_dec), batch_size=32)
        #hist = model.fit(x_train, y_train, epochs="%s", batch_size=32) % int(msg_dec)

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
        result = str(np.argmax(y_test[0:1]))
        client_socket.sendall(result.encode())  # 클라이언트에게 응답
        client_socket.close()  # 클라이언트 소켓 종료

