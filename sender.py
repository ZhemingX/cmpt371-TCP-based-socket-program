import random
from socket import *
import json
import sys
import time
import signal

# input list
# The seed for the random number generator used for timing 
# The number of segments to send 
# The seed for the random number generator used for determining if an ACK has 
# been corrupted. 
# The probability that an ACK has been corrupted. Between [0 and 1) 
# The seed for the generation of the data field in each packet
# The round trip travel time

# server host name or IP address
serverHost = 'localhost'

# three random number generators
global R_time
global R_corrupt
global R_data

# The packet content [segment contents, seqSeg, seqAck, isAck]
def print_packet_content(type,list):
    # print the packet content, type = 0 for segment, type = 1 for Ack
    if type == 0:
        info = 'Segment sent: data = ' + str(list[0]) + ' seqSeg = ' + str(list[1]) + ' seqAck = ' + str(list[2]) + ' isack = ' + str(list[3])
    elif type == 1:
        info = 'ACK recieved: data = ' + str(list[0]) + ' seqSeg = ' + str(list[1]) + ' seqAck = ' + str(list[2]) + ' isack = ' + str(list[3])

    print(info)

# The packet content [segment contents, seqSeg, seqAck, isAck]
def make_pkt(seqSeg, R_data):
    # make segment packets
    # The integer should be a random integer between 0 and 1024
    data = int(1025 * R_data.random())
    # print(data)
    pkt = [data]
    if(seqSeg == 1):
        pkt.append(1)
    elif(seqSeg == 0):
        pkt.append(0)
    pkt.append(0)
    pkt.append(0)

    return pkt

def sender(seed_for_timing, num_of_seg, seed_for_corrupt, prob_corrupt, seed_for_data, rtt):
    # we assume the port number to be 12000
    serverPort = 12000
    # create a TCP socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    
    # create a TCP connection between the client and the server
    clientSocket.connect((serverHost, serverPort))

    print('The client is connected\n')

    # count the start time
    start = time.time()

    # four states defined for receiver
    state = ['WAIT FOR CALL 0 FROM ABOVE', 'WAIT FOR CALL 1 FROM ABOVE', 'WAIT FOR ACK 0', 'WAIT FOR ACK 1']

    R_time = random.Random(float(seed_for_timing))
    R_corrupt = random.Random(float(seed_for_corrupt))
    R_data = random.Random(float(seed_for_data))

    # count the number of segments
    num_count = 0
    # count the nextSendTime
    nextSendTime = 0
    # initial state
    mystate = state[0]
    # # a variable to watch the execluting times of while loop
    # term_count = 0

    while(num_count < int(num_of_seg)):

        # term_count += 1
        # if prob_corrupt == 1 (a infinite loop )then after print the same message for twice, exit the loop
        # if (term_count == 8 and float(prob_corrupt) == 1.0):
            # print('Since the ACK packet is always corrupted, the sender program terminated')
            # break

        if (mystate == state[0]):
            # current state is WAIT FOR CALL 0 FROM ABOVE
            if time.time() - start < nextSendTime:
                # If the elapsed time is less than the nexSendTime 
                # the program should wait till the nextSendTime 
                # to send the segment
                time.sleep(nextSendTime - (time.time() - start))
        # then you have got data from above
            sndpkt = make_pkt(0, R_data)
            print('A data segment with sequence number 0 is about to be sent')
            print_packet_content(0, sndpkt)
            clientSocket.send(json.dumps(sndpkt).encode())
            # increment the nextSendTime
            nextSendTime += 5 * R_corrupt.random()
            # after the sending of the packet is complete the time is 0 seconds
            # sender is moving to state WAIT FOR ACK 0
            mystate = state[2]
            print('The sender is moving to state ' + mystate)
            print('\n')

        elif (mystate == state[1]):
            # current state is WAIT FOR CALL 1 FROM ABOVE
            if time.time() -start < nextSendTime:
                 # If the elapsed time is less than the nexSendTime 
                 # the program should wait till the nextSendTime 
                 # to send the segment
                time.sleep(nextSendTime - (time.time() - start))
        # then you have got data from above
            sndpkt = make_pkt(1, R_data)
            print('A data segment with sequence number 1 is about to be sent')
            print_packet_content(0, sndpkt)
            clientSocket.send(json.dumps(sndpkt).encode())
            # increment the nextSendTime
            nextSendTime += 5 * R_corrupt.random()
            # after the sending of the packet is complete the time is 0 seconds
            # sender is moving to state WAIT FOR ACK 1
            mystate = state[3]
            print('The sender is moving to state ' + mystate)
            print('\n')

        elif (mystate == state[2]): 
            # current state is WAIT FOR ACK 0
            # now we first deal with time out event (haven't received by 3 seconds then resend)
          
            try:
                rcv_pkt = ''
                clientSocket.settimeout(float(rtt))
                rcv_pkt = clientSocket.recv(1024).decode()
                clientSocket.settimeout(None)
                tmp = R_corrupt.random()
                # if rcv_pkt == '', exit
                # if(rcv_pkt == ''):
                    # break
                # print(tmp)
                if (tmp < float(prob_corrupt)):
                    # a corrupted segment is received
                    print('A Corrupted ACK segment has just been received')
                    # resent the segment packet with seqSeg = 0
                    print('A data segment with sequence number 0 is about to be resent')
                    print_packet_content(0, sndpkt)
                    clientSocket.send(json.dumps(sndpkt).encode())
                    # sender is moving back to state WAIT FOR ACK 0
                    mystate = state[2]
                    print('The sender is moving back to state ' + mystate)
                    print('\n')

                elif (tmp >= float(prob_corrupt)):
                    # an uncorrupted ACK segment is received
                    # number of successful sent segments increased by 1
                    num_count = num_count + 1
                    rcvpkt = json.loads(rcv_pkt)
                    print('An ACK0 segment has just been received')
                    print_packet_content(1, rcvpkt)
                    # sender is moving to state WAIT FOR CALL 1 FROM ABOVE
                    mystate = state[1]
                    print('The sender is moving to state ' + mystate)
                    print('\n')

            except timeout as e: 
                # time out
                # print(e)
                # print('timeout so A data segment with sequence number 0 is about to be resent')
                print('A data segment with sequence number 0 is about to be resent')
                print_packet_content(0, sndpkt)
                clientSocket.send(json.dumps(sndpkt).encode())
                # sender is moving back to state WAIT FOR ACK0
                mystate = state[2]
                print('The sender is moving back to state ' + mystate)
                print('\n')

        elif (mystate == state[3]):
            # current state is WAIT FOR ACK 1
            # now we first deal with time out event (haven't received by rtt seconds then resend)
            try:
                rcv_pkt = ''
                clientSocket.settimeout(float(rtt))
                rcv_pkt = clientSocket.recv(1024).decode()
                clientSocket.settimeout(None)
                tmp = R_corrupt.random()
                # if rcv_pkt == '', exit
                # if(rcv_pkt == ''):
                    # break
                #print(tmp)
                if (tmp < float(prob_corrupt)):
                    # a corrupted segment is received
                    print('A Corrupted ACK segment has just been received')
                    # resent the segment packet with seqSeg = 1
                    print('A data segment with sequence number 1 is about to be resent')
                    print_packet_content(0, sndpkt)
                    clientSocket.send(json.dumps(sndpkt).encode())
                    # sender is moving back to state WAIT FOR ACK 1
                    mystate = state[3]
                    print('The sender is moving back to state ' + mystate)
                    print('\n')

                elif (tmp >= float(prob_corrupt)):
                    # a uncorrupted ACK segment is received
                    # number of successful sent segments increased by 1
                    num_count = num_count + 1
                    rcvpkt = json.loads(rcv_pkt)
                    print('An ACK1 segment has just been received')
                    print_packet_content(1, rcvpkt)
                    # sender is moving to state WAIT FOR CALL 0 FROM ABOVE
                    mystate = state[0]
                    print('The sender is moving to state ' + mystate)
                    print('\n')

            except timeout as e:
                # time out
                # print(e)
                # print('time out so A data segment with sequence number 1 is about to be resent')
                print('A data segment with sequence number 1 is about to be resent')
                print_packet_content(0, sndpkt)
                clientSocket.send(json.dumps(sndpkt).encode())
                # # sender is moving back to state WAIT FOR ACK1
                mystate = state[3]
                print('The sender is moving back to state ' + mystate)
                print('\n')
            
    # after the requested number of segments sent successfully, close the socket
    clientSocket.close()

def main():
    print('input the seed for the random generator used for timing: ')
    seed_for_timing = input()
    print('input the number of segments to send: ')
    num_of_seg = input()
    print('input the seed for the random number generator used for determing if an ACK has been corrupted: ')
    seed_for_corrupt = input()
    print('input the probability that an ACK has been corrupted: ')
    prob_corrupt = input()
    print('input the seed for the generation of the data field in each packet: ')
    seed_for_data = input()
    print('input the round trip travel time: ')
    rtt = input()
    # print('\n')

    sender(seed_for_timing, num_of_seg, seed_for_corrupt, prob_corrupt, seed_for_data, rtt)
    # sender(1,4,1,0.2,1,3)

    # terminate the program 
    sys.exit()

# This is where the program starts
if __name__ == '__main__':
	main() 


    
    
    


