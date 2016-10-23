import sys
import getopt

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.windowLength = 5
        #Last ACK Received
        self.LAR = -1
        #Last Frame Sent
        self.LFS = -1
        #number of wrong response
        self.checkCount = 0
        #buffer
        self.buffer = {}
        #tag
        self.move = True

        self.timeup = False

    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            #print "recv: %s" % response_packet
            msg_type, seqno, data, checksum = self.split_packet(response_packet)
            if seqno >= self.LAR + 1:
                self.checkCount = 0
                self.LAR = int(seqno) - 1
                print 'LAR = ',self.LAR
                print 'LFS = ',self.LFS
                print '-----------------'
        #else:
            #print "recv: %s <--- CHECKSUM FAILED" % response_packet

    # window is full,waiting..
    # return -1 : success , otherwise number to resend
    def waiting(self):
        while True:
            self.checkCount = self.checkCount + 1
            resend_packet = self.buffer.get(str(self.LAR + 1))

            #print "resent: %s" % resend_packet
            self.send(resend_packet)
            response = self.receive(timeout = 0.5)
            
            while response == None:
                if self.checkCount == 100:
                    #print 'time up,resend seqno :', str(self.LAR + 1)
                    self.checkCount = 0
                    self.timeup = True
                    return self.LAR + 1
                
                self.checkCount = self.checkCount + 1
                resend_packet = self.buffer.get(str(self.LAR + 1))

                #print "resent: %s" % resend_packet
                
                self.send(resend_packet)
                response = self.receive(timeout = 0.5)
              
            self.handle_response(response)   
            msg_type, seqno, data, checksum = self.split_packet(response)
            #print 'resend type:',msg_type,'\nseqno:',seqno,'\nLAR:',self.LAR
            if seqno >= self.LAR + 1:
                #print "resend succeeded: %s" % self.LAR
                #try:
                #    del self.buffer[str(self.LAR)]
                #except KeyError:
                #    pass
                    #print 'Element in dictionary does not exists!'
                    
                self.checkCount = 0
                return -1
  
    # Main sending loop.
    def start(self):
        seqno = 0
        msg_type = None
        msg = self.infile.read(4000)
        while not msg_type == 'end':
            
            if self.move == True:
                next_msg = self.infile.read(4000)
            self.move = True;
    
            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif next_msg == "":
                msg_type = 'end'

            if self.LFS - self.LAR < self.windowLength or msg_type == 'end':
                self.LFS = self.LFS + 1
                #print 'LFS = ',self.LFS
                packet = self.make_packet(msg_type, seqno, msg)
                self.send(packet)
                self.buffer[str(seqno)] = packet
                
                #print "sent: %s" % packet
                
                res = self.receive(timeout = 0.1)
                self.handle_response(res)

                msg = next_msg
                seqno += 1
            else:
                while not self.LFS == self.LAR:
                    #print 'Waiting...'
                    code = self.waiting()
                    if self.timeup == True:
                        #print 'Time up,stop!'
                        return
                    self.move = False;
                
        while not self.LFS == self.LAR:
            #print 'Waiting...'
            code = self.waiting()
            if self.timeup == True:
                #print 'Time up,stop!'
                return
            self.move = False;
        
        print 'Completed!'
        self.LFS = 0
        self.LAR = 0
        self.infile.close()
                    
    def log(self, msg):
        if self.debug:
            print msg

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
