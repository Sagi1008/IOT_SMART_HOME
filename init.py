import socket
BROKER = socket.gethostbyname('broker.hivemq.com')
PORT = 1883
COMM_ROOT = 'course/SmartParking/'
DB_NAME = 'parkingdata.db'
MAX_SPOTS = 12
BARRIER_AUTO_CLOSE_S = 8
