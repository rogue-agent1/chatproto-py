#!/usr/bin/env python3
"""Simple chat protocol — server and client over TCP."""
import socket,threading,argparse,sys
def server(host,port):
    clients=[];lock=threading.Lock()
    def broadcast(msg,sender=None):
        with lock:
            for c in clients:
                if c!=sender:
                    try: c.send(msg)
                    except: pass
    def handle(conn,addr):
        name=conn.recv(1024).decode().strip();broadcast(f"[{name} joined]\n".encode())
        print(f"{name} connected from {addr}")
        try:
            while True:
                data=conn.recv(1024)
                if not data: break
                broadcast(f"{name}: {data.decode()}".encode(),conn)
        except: pass
        with lock: clients.remove(conn)
        broadcast(f"[{name} left]\n".encode());conn.close()
    srv=socket.socket();srv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    srv.bind((host,port));srv.listen(10);print(f"Chat server on {host}:{port}")
    while True:
        conn,addr=srv.accept()
        with lock: clients.append(conn)
        threading.Thread(target=handle,args=(conn,addr),daemon=True).start()
def client(host,port,name):
    s=socket.socket();s.connect((host,port));s.send(f"{name}\n".encode())
    def recv():
        while True:
            data=s.recv(1024)
            if not data: break
            print(data.decode(),end="")
    threading.Thread(target=recv,daemon=True).start()
    while True:
        msg=input();s.send(msg.encode())
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd")
    a=sub.add_parser("server");a.add_argument("-p","--port",type=int,default=8888);a.add_argument("--host",default="127.0.0.1")
    a=sub.add_parser("client");a.add_argument("-p","--port",type=int,default=8888);a.add_argument("--host",default="127.0.0.1");a.add_argument("-n","--name",default="anon")
    args=p.parse_args()
    if args.cmd=="server": server(args.host,args.port)
    elif args.cmd=="client": client(args.host,args.port,args.name)
if __name__=="__main__": main()
