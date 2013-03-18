#-*-coding:utf-8-*-

import logging
import socket
import errno
import json

FATALERROR  = (errno.EBADF, errno.EINVAL, errno.ENOTSOCK)
IGNOREERROR = (errno.EAGAIN, errno.EWOULDBLOCK)

def read_sock_buf(sock, buf_len=6, is_header=True):
    buf = ""

    while True:
        try:
            tmp_buf = sock.recv(buf_len)
        except socket.error as err:
            if err.args[0] not in IGNOREERROR:
                logging.error("read socket error `%s`, %s" % (err, sock,))
                break;

        if is_header and (not tmp_buf or not tmp_buf.isdigit()):
            logging.error("can't read header message %s %s" % (tmp_buf, sock,))
            break;

        buf += tmp_buf
        if len(tmp_buf) == buf_len:
            logging.debug("read header over,header_buff=%s" % (buf, ))
            break;
        else:
            buf_len -= len(tmp_buf)
            logging.debug("read header loop,next read len %d" % (buf_len,))

    if len(buf) == 0:
        return (1, "read buff at %s failure" % (sock,))
    elif is_header:
        logging.debug("header=%s", buf)
        return read_sock_buf(sock, int(buf) + 2, False)
    elif buf[-2:] == "|>":
        return (0, buf[:-2])
    else:
        return (1, "error end flag `%s`" % (buf, ))

def write_sock_buf(sock, buf):
    if isinstance(buf, dict):
        buf = json.dumps(buf)

    logging.debug("start write `%s` to %s", buf, sock)
    buf     = str(len(buf)).zfill(6) + buf + "|>"
    buf_len = len(buf)
    start   = 0
    while True:
        try:
            start += sock.send(buf[start:])
        except socket.error as err:
            if err.args[0] not in IGNOREERROR:
                logging.error("error write response message `%s` to %s" % (buf, sock))
                break;

        logging.debug("write response message `%s` to %s len %s, total len %s" % (buf, sock, start,buf_len,))
        if start == buf_len:
            break;

    return (0, "")