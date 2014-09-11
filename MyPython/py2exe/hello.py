
import sys

if  __name__ == '__main__':
    print "Hello World!"
    if len(sys.argv) >1:
        fp = open('d:\cmdlog.txt', "a")
        line = ''
        for i in xrange(len(sys.argv)):
            #print sys.argv[i]
            line += sys.argv[i] + ' '
        line += '\n'
        print line
        fp.write(line)
        fp.close()    