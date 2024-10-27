import socket
import os 
import threading
import sys

def get_request_parts(request: str):
    request_parts = {'Request_line': None, 'Headers': None, 'Body': None}
    #everything of the request splitted by \r\n CRLF
    request_splitted = request.decode().split('\r\n')
    '''
    for Request_Splitted:
        1- First element is the requst line, 
        2- Second is the HEADERS, last element will be for the headers will be an empty string! 
        3- Third is the Requst body which will be after the latest empty string!
    '''
    request_parts['Body'] = request_splitted.pop() 
    
    # First element is the request_line 
    # Split the req line on a space
    req_line_splitted = request_splitted.pop(0).split(' ')
    req_line = {} 
    req_line['Method'] = req_line_splitted.pop(0)
    req_line['Target'] = req_line_splitted.pop(0)
    req_line['Version'] = req_line_splitted.pop(0)
    request_parts['Request_line'] = req_line

    #Remove the last element since it's always empty string "there's two \r\n to indicate the end of the HEADERS"
    request_splitted.pop()
    #now all that is left is the HEADERS 
    #Each element in the list is KEY:VALUE together
    headers_splitted = []
    for header in request_splitted:
        key = ''
        val = ''
        for i in range(len(header)): 
            if header[i] == ':':
                key = header[0:i]
                val = header[i + 1:]
                break
        headers_splitted.append(key.strip(' '))
        headers_splitted.append(val.strip(' '))

    # headers_splitted = ''.join(request_splitted).split(' ')
    headers = {headers_splitted.pop(0):headers_splitted.pop(0) for _ in range(int(len(headers_splitted) / 2))}
    request_parts['Headers'] = headers
    print('---------------------------------')
    print(request_parts)
    print('--------------------------------')
    return request_parts

def write_file(path: str, name: str, content: str): 
    with open(path + name, 'x') as f:
        print(path + name)
        f.write(content)
        f.close() 
     

def generate_response(req_parts): 
    # Default response: 404 if the target is not found, 200 OK for root
    response = 'HTTP/1.1 404 Not Found\r\n\r\n' if req_parts['Request_line']['Target'] != '/' else 'HTTP/1.1 200 OK\r\n\r\n'
    body = ''
    
    # Handle echo request
    if 'echo'.lower() in req_parts['Request_line']['Target'].lower():
        echoed = req_parts['Request_line']['Target'].split('/')[-1]
        body = echoed
        length = str(len(body))
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{body}"
    
    # Handle user-agent request
    elif '/user-agent'.lower() in req_parts['Request_line']['Target'].lower(): 
        user_agent = req_parts['Headers'].get('User-Agent')
        body = user_agent
        length = str(len(body))
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{body}"
    

    elif 'files'.lower() in req_parts['Request_line']['Target'].lower() and req_parts['Request_line']['Method'] == 'GET':
        print('This is the case I want')
        # Last element is the path of the file! 
        path = sys.argv[-1]
        file_name = req_parts['Request_line']['Target'].split('/')[-1]
        # print(path)
        # print(os.listdir(path))
        # print(file_name)
        if file_name in os.listdir(path):
            with open(path+file_name, 'r') as f:
                content = f.read()
                body += content
                length = len(body)
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {length}\r\n\r\n{body}"
                f.close()
    elif req_parts['Request_line']['Method'] == 'POST' and 'files'.lower() in req_parts['Request_line']['Target'].lower():
        print("--------------------------FAISAL---------------------------")
        # Get file name, path, use the function above to write the content and send 201
        path = sys.argv[-1]
        file_name = req_parts['Request_line']['Target'].split('/')[-1]
        content = req_parts['Body']
        write_file(path, file_name, content)
        response = 'HTTP/1.1 201 Created\r\n\r\n' 

    print('---------------------------------')
    print(response)
    print('--------------------------------')
    return response.encode('utf-8')

def request_handler(conn):
    data = conn.recv(1024)
    req_parts = get_request_parts(data)
    response = generate_response(req_parts) 
    conn.sendall(response) 
    return

def main():
    server_socket = socket.create_server(("localhost", 4221))
    while True:    
        conn, addr = server_socket.accept() # wait for client
        t = threading.Thread(target = lambda: request_handler(conn))
        t.start()

if __name__ == "__main__":
    main()
