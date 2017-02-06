import socket
import struct
import os
import time
import hashlib
MIN_BUFSIZE = 1024
HEAD_STRUCT = '128sIq32s'   # Structure of file head, char fileName[128], int fileNameSize,long long fileSize,char MD5[32];

def send_file(IP_address,port_no,buffer_size,fileName,md5_value):
    if (buffer_size<MIN_BUFSIZE):
        buffer_size = MIN_BUFSIZE
    file_size = os.path.getsize(fileName)#Return the file size on path
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)
        
    server_address = (IP_address,port_no)#set IP/port number
     
    fp = open(fileName, 'rb')#open again
    file_head = struct.pack(HEAD_STRUCT, fileName, len(fileName), file_size,md5_value) # Pack a structure of head

    try:
        sock.connect(server_address)
        print "IP connect to %s,port %s" % server_address
        sock.send(file_head) # Send head information to server
        print "Sending data...\n"
        start_time = time.time()
        send_size = 0
        while(send_size < file_size):
            if(file_size - send_size < buffer_size):
                file_data = fp.read(file_size - send_size)
                send_size = file_size
            else:
                file_data = fp.read(buffer_size)
                send_size += buffer_size
            sock.send(file_data)
        end_time = time.time()

        print "Total spend %f seconds" % (end_time - start_time)
        print "Send file of size : %d(KByte)" % (send_size/1000)
        fp.close()
        sock.close()
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)
    except Exception, msg:
        print "Other exception : %s" % str(msg)

    print "\nConnecting is colsed!\n"

def recv_file(IP_address,port_no,buffer_size):
    if (buffer_size<MIN_BUFSIZE):
        buffer_size = MIN_BUFSIZE
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# Enable reuse address/port
    server_address = IP_address,port_no
    # Bind server address
    sock.bind(server_address)
    print "Starting server IP on %s port %s" % server_address
    sock.listen(3)
    print "Waiting file is received......"
    client_sock, client_address = sock.accept()
    print "Socket %s:%d connected" % client_address

    info_struct = struct.calcsize(HEAD_STRUCT)#size of the struct corresponding to the given format
    file_info = client_sock.recv(info_struct)
    file_nameField, filename_size, file_size,md5_info = struct.unpack(HEAD_STRUCT, file_info)#Unpack the bytes according to the given format
    file_name = file_nameField[:filename_size]
    print "file_name:",file_name
    fp = open(file_name, 'wb')
    recv_size = 0
    print "Receiving data...\n"
    start_time = time.time()
    while (recv_size < file_size):
        if(file_size - recv_size < buffer_size):
            file_data = client_sock.recv(file_size - recv_size)
            recv_size = file_size
        else:
            file_data = client_sock.recv(buffer_size)
            recv_size += buffer_size
        fp.write(file_data)
    end_time = time.time()
    print "Total spend %f seconds" % (end_time - start_time)
    print "Receive file of size : %d (KByte)" % (recv_size/1000)   
    fp.close() 
    return file_name,md5_info
 
def calculate_md5(file_name,buffer_size):
    if (buffer_size<MIN_BUFSIZE):
        buffer_size = MIN_BUFSIZE
    print "Calculating MD5 of file..."
    md5_value = hashlib.md5()
    with open(file_name,"rb") as file_name:
       while True:
          data = file_name.read(buffer_size)
          if data == "":
             break
          md5_value.update(data)
    return md5_value.hexdigest()
  
if __name__ == '__main__':
    cmd =0
    port = input('Please set Server port number:')
    ip = raw_input('Please set Server IP address:')
    buf_size = input('Please set buffer size(byte):')
    print" "
    while(cmd!='q'):
        print "Send a file (s)"
        print "Receive a file (r)"
        print "Reset Server IP address/port number(e)"
        print "Quit (q)\n"
        cmd = raw_input('Please input command:')
        if(cmd == 'q'):    
            print('exit program')
        elif(cmd =='e'):
            port = input('Please reset  Server port number:')
            ip = raw_input('Please reset Server IP address:')
            buf_size = input('Please set buffer size(byte):')
            print" "
        else:    
            if(cmd == 's'):
                fileName = raw_input('Please input file name:')
                md5 = calculate_md5(fileName,buf_size)
                print "Data calculate MD5 : %s\n" % md5
                send_file(ip,port,buf_size,fileName,md5)
            elif(cmd == 'r'):
                fileName,md5_info = recv_file(ip,port,buf_size)
                md5 = calculate_md5(fileName,buf_size)
                if(md5_info == md5):
                    print "MD5: %s is correct!\n" % md5_info
                else:
                    print "MD5 is error!"
                    print "Recevie MD5 : %s" % md5_info
                    print "Data calculate MD5 : %s\n" % md5
            else:  
                print ("Unknown command!")

     
