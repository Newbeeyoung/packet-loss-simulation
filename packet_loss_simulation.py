#!/usr/bin/python
"""
The very first line should be the above line of code for the program to run
No blank line allowed on Line-1
"""

'''
The code is hardcoded for the network (The IP addresses are hardcoded)

the network is shown below

if n=2,          
    h1-           -h2
       s1 ----- s2

and so on till max n

Code needs to be written to handle a more general network

The below global variables need to be set according to the experiment

'''

import sys
import time
from threading import Thread
import subprocess
from os.path import isfile, join
import os
import shutil
import argparse

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

from functools import partial
from mininet.node import RemoteController

'''
Maximum of 32 hosts , working for this topology (some RAM limitations , i guess) - 
tested on a 4 GB Ubuntu 14.04 
'''
n = -1  # number of hosts
bw =1000 # link bandwidth in mbps (all links have the same bandwidth)
# bw =10# link bandwidth in mbps (all links have the same bandwidth)
qos = 1  # 1 -> if QoS needs to be applied | 0 -> no QoS

'''
y = qos_k*x utility function for sd_flow
y = x is the utility function for hd_flow
'''
qos_k = 2

workingDir = os.getcwd()

# switch_loss=1

class SimpleTopo(Topo):
    global n

    # 2 switches and n hosts (n/2 hosts per switch), a link between 2 switches
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        # Adding switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # 'dummy' is added to not use the zero index
        h = ['dummy']  # list of hosts

        # Adding hosts
        for i in range(n + 1)[1:]:
            h.append(self.addHost('h{0}'.format(i)))
            if (i % 2) == 1:
                self.addLink(h[i], s1)
            else:
                self.addLink(h[i], s2)

        self.addLink(s1, s2,loss=switch_loss)


def stream(src, dst, input_filename, output_filename, dstIP):

    print 'Executing command on server %s -> %s' % (src.name, dst.name)

    server_command='ffmpeg -i %s -an -f h264 udp://10.0.0.2:5004'%(input_filename)
    print(server_command)
    result1 = src.sendCmd(server_command)

    print 'Executing command on client %s <- %s' % (dst.name, src.name)

    client_command = 'ffmpeg -y -timeout 100 -i udp://10.0.0.2:5004 -c copy %s' % (output_filename)
    print(client_command)
    result2 = dst.sendCmd(client_command)

    return (src, dst)

def vlcStream(net):
    # 'dummy' is added to not use the zero index
    h = ['dummy']  # list of hosts

    # Getting hosts
    for i in range(n + 1)[1:]:
        h.append(net.get('h%d' % i))

    serv_cli_pairs = []  # list of tuples

    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    i=1

    f=open("stream_err.txt","a")
    for m,classname in enumerate(sorted(os.listdir(h264_dir))):

        if not os.path.exists(os.path.join(dst_dir,classname)):
            os.mkdir(os.path.join(dst_dir,classname))
        for h264 in os.listdir(os.path.join(h264_dir,classname)):

            try:
                inFile=os.path.join(h264_dir,classname,h264)
                outFile=os.path.join(dst_dir,classname,h264.split(".")[0]+".mp4")

                print 'inFile = ', inFile
                print 'outFile =', outFile

                serv_cli_pairs.append(stream(h[2 * i - 1], h[2 * i], inFile, outFile, '10.0.0.%d' % (2 * i)))

                ''' waiting for video flows to complete '''
                for src, dst in serv_cli_pairs:

                    print"Source cmd"
                    src.waitOutput()
                    print "Dest cmd"
                    dst.waitOutput()
                    print 'Video streaming complete from %s -> %s !!!' % (src.name, dst.name)
            except:
                f.write(inFile)
                f.write("\n")
                pass



def applyQueues():
    '''
    create queues for QoS
    '''

    if not qos:
        print 'No QoS !'
        command = 'sudo ovs-vsctl set port s1-eth%d qos=@newqos -- \
            --id=@newqos create qos type=linux-htb other-config:max-rate=1000000000 queues:0=@q0 -- \
            --id=@q0 create Queue other-config:min-rate=%d other-config:max-rate=%d' % (
        (n / 2) + 1, int(bw * (10 ** 6)), int(bw * (10 ** 6)))

        subprocess.call(command, shell=True)
    else:
        print 'Yes QoS !!!'
        command = 'ovs-vsctl -- set Port s1-eth%d qos=@newqos -- \
        --id=@newqos create QoS type=linux-htb other-config:max-rate=1000000000 queues=0=@q0,1=@q1,2=@q2 -- \
        --id=@q0 create Queue other-config:min-rate=%d other-config:max-rate=%d -- \
        --id=@q1 create Queue other-config:min-rate=%d other-config:max-rate=%d -- \
        --id=@q2 create Queue other-config:min-rate=%d other-config:max-rate=%d' % (
            (n / 2) + 1,
            int(bw * (10 ** 6)), int(bw * (10 ** 6)),
            int((bw * (10 ** 6)) / (qos_k + 1)), int((bw * (10 ** 6)) / (qos_k + 1)),
            int(((bw * (10 ** 6)) / (qos_k + 1)) * qos_k), int(((bw * (10 ** 6)) / (qos_k + 1)) * qos_k))

        subprocess.call(command, shell=True)

def load_classes(classes_txt_path):

    class_list=[]
    f=open(classes_txt_path,'r')

    for classname in f.readlines():
        class_list.append(classname.strip("\n"))
    return class_list

def vlcTest():
    "Create network and run simple performance test"
    topo = SimpleTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink,
                  controller=partial(RemoteController, ip='127.0.0.1', port=6633))

    net.start()
    applyQueues()

    print "Testing network connectivity"
    net.pingAll()

    # CLI(net) # starts the mininet command line prompt

    vlcStream(net)
    net.stop()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_path',
                        default=None,
                        type=str,
                        help='Directory path of videos')
    parser.add_argument('--dst_path',
                        default=None,
                        type=str,
                        help='Directory path of h.264')
    parser.add_argument('--switch_loss',
                        default=1,
                        type=int,
                        help='Proportion of packet loss in video streaming')
    args = parser.parse_args()

    n=2
    switch_loss=args.switch_loss

    h264_dir=args.h264_dir
    dst_path=args.dst_path
    dst_dir='%s/%s'%(dst_path,switch_loss)

    setLogLevel('info')
    vlcTest()
