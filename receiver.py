import random
from socket import *
import json
import sys

# The packet content [segment contents, seqSeg, seqAck, isAck]
def print_packet_content(type,list):
    # print the packet content, type = 0 for segment, type = 1 for Ack
    if type == 0:
        info = 'Segment received contains: data = ' + str(list[0]) + ' seqSeg = ' + str(list[1]) + ' seqAck = ' + str(list[2]) + ' isack = ' + str(list[3])
    elif type == 1:
        info = 'ACK to send contains: data = ' + str(list[0]) + ' seqSeg = ' + str(list[1]) + ' seqAck = ' + str(list[2]) + ' isack = ' + str(list[3])

    print(info)

# the receiver function
def receiver(seed_for_corrupt, prob_corrupt):
    # connect a socket to the server
    # we assume the port number to be 12000
    serverPort = 12000
    # create a TCP socket
    serverSocket = socket(AF_INET, SOCK_STREAM) 
    serverSocket.bind(('', serverPort))
    # define the maximum number of requests for connections
    serverSocket.listen(1)
    print('The server is ready to receive')
    #accept for the request for connection
    connectionSocket, addr = serverSocket.accept()
    print('The server is connected to a client')
    print('\n')
    #two states defined for receiver
    state = ['WAIT FOR 0 FROM BELOW', 'WAIT FOR 1 FROM BELOW']
    #initial state
    mystate = state[0]
    
    R1 = random.Random(float(seed_for_corrupt))
    
    # a variable to watch the execluting times of while loop
    # term_count = 0

    while True:

        rcv_pkt = connectionSocket.recv(1024).decode()
        # when rcv_pkt is empty, this means the clientSocket is closed, so break and close the connectionSocket
        if(rcv_pkt == ''):
            break

        # term_count += 1
        # print(term_count)
        # if prob_corrupt == 1 (a infinite loop )then after print the same message for twice, exit the loop
        # if(term_count == 8 and float(prob_corrupt) == 1.0):
            # print('Since the segment packet is always corrupted, the receiver program terminated')
            # break
        # current state is WAIT FOR 0 FROM BELOW
        if(mystate == state[0]):
            if (R1.random() < float(prob_corrupt)):
                # a corrupted segment is received
                print('A Corrupted segment has been received')
                # receiver is moving back to state WAIT FOR 0 FROM BELOW
                mystate = state[0]
                print('The receiver is moving back to state ' + mystate)
                print('\n')

            else:
                # an uncorrupted segment is received
                rcv_pkt = json.loads(rcv_pkt)

                if rcv_pkt[1] == 1:
                    # a duplicate segment with seqSeg = 1 has been received
                    print('A duplicate segment with sequence number 1 has been received')
                    print_packet_content(0, rcv_pkt)
                    sndpkt = [0,0,1,1]
                    print('An ACK1 is about to be sent')
                    print_packet_content(1, sndpkt)
                    connectionSocket.send(json.dumps(sndpkt).encode())
                    # receiver is moving back state WAIT FOR 0 FROM BELOW
                    mystate = state[0]
                    print('The receiver is moving back to state ' + mystate)
                    print('\n')

                elif rcv_pkt[1] == 0:
                    # a segment with seqSeg = 0 has been received
                    print('A segment with sequence number 0 has been received')
                    print_packet_content(0, rcv_pkt)
                    sndpkt = [0,0,0,1]
                    print('An ACK0 is about to be sent')
                    print_packet_content(1, sndpkt)
                    connectionSocket.send(json.dumps(sndpkt).encode())
                    # receiver is moving to state WAIT FOR 1 FROM BELOW
                    mystate = state[1]
                    print('The receiver is moving to state ' + mystate)
                    print('\n')

        # current state is WAIT FOR 1 BELOW
        elif(mystate ==  state[1]):
            if (R1.random() < float(prob_corrupt)):
                # a corrupted segment is received
                print('A Corrupted segment has been received')
                # receiver is moving back to state WAIT FOR 1 FROM BELOW
                mystate = state[1]
                print('The receiver is moving back to state ' + mystate)
                print('\n')

            else:
                # a uncorrupted segment is received
                rcv_pkt = json.loads(rcv_pkt)

                if rcv_pkt[1] == 0:
                    # a duplicate segment with seqSeg = 0 has been received
                    print('A duplicate segment with sequence number 0 has been received')
                    print_packet_content(0, rcv_pkt)
                    sndpkt = [0,0,0,1]
                    print('An ACK0 is about to be sent')
                    print_packet_content(1, sndpkt)
                    connectionSocket.send(json.dumps(sndpkt).encode())
                    # receiver is moving back state WAIT FOR 1 FROM BELOW
                    mystate = state[1]
                    print('The receiver is moving back to state ' + mystate)
                    print('\n')

                elif rcv_pkt[1] == 1:
                    # a segment with seqSeg = 1 has been received
                    print('A segment with sequence number 1 has been received')
                    print_packet_content(0, rcv_pkt)
                    sndpkt = [0,0,1,1]
                    print('An ACK1 is about to be sent')
                    print_packet_content(1, sndpkt)
                    connectionSocket.send(json.dumps(sndpkt).encode())
                    # receiver is moving to state WAIT FOR 1 FROM BELOW
                    mystate = state[0]
                    print('The receiver is moving to state ' + mystate)
                    print('\n')

    print('The server is closed for this connection')
    connectionSocket.close()

def main():
    print('input the seed used for determining if the data segments have been corrupted: ')
    seed_for_corrupt = input()
    print('input the probability that the data segment has been corrupted: ')
    prob_corrupt = input()
    print('\n')
    #receiver(seed_for_corrupt, prob_corrupt)
    receiver(seed_for_corrupt, prob_corrupt)
    # terminate the program 
    sys.exit()

# This is where the program starts
if __name__ == '__main__':
	main()  






