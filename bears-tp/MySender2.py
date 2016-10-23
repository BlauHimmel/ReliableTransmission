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
        self.point = 0

    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
            msg_type, seqno, data, checksum = self.split_packet(response_packet)
            print 'seqno:',seqno
            if self.point == int(seqno) - 1:
                self.point += 1
                print 'succeed!'
                return True
            else:
                print 'fail!'
                return False

        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet
            print 'fail!'
            return False

    
    # Main sending loop.
    def start(self):
        times = 0
        seqno = 0
        msg_type = None
        msg = self.infile.read(500)
        while not msg_type == 'end':
            times = 0
            next_msg = self.infile.read(500)
    
            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif next_msg == "":
                msg_type = 'end'

            packet = self.make_packet(msg_type,seqno,msg)
            self.send(packet)
            print "sent: %s" % packet

            response = self.receive(0.5)
            result = self.handle_response(response)
            times += 1

            while result == False:
                if times == 20:
                    print 'Time up,stop!'
                    return:
                self.send(packet)
                print "sent: %s" % packet
                response = self.receive(0.5)
                result = self.handle_response(response)
                times += 1

            msg = next_msg
            seqno += 1

        self.infile.close()


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
