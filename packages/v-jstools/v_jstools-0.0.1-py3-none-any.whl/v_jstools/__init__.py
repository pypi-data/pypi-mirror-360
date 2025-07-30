# coding=utf-8
import shutil
import os
import sys
import time
import json
import tempfile
def extractall(self, path=None, members=None, pwd=None):
    if members is None: members = self.namelist()
    path = os.getcwd() if path is None else os.fspath(path)
    for zipinfo in members:
        try:    _zipinfo = zipinfo.encode('cp437').decode('gbk')
        except: _zipinfo = zipinfo.encode('utf-8').decode('utf-8')
        print('[*] unpack...', _zipinfo)
        if _zipinfo.endswith('/') or _zipinfo.endswith('\\'):
            myp = os.path.join(path, _zipinfo)
            if not os.path.isdir(myp):
                os.makedirs(myp)
        else:
            myp = os.path.join(path, _zipinfo)
            youp = os.path.join(path, zipinfo)
            self.extract(zipinfo, path)
            if myp != youp:
                os.rename(youp, myp)
import zipfile
zipfile.ZipFile.extractall = extractall

import os
import shutil
import platform
import subprocess

def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])

def encbytefile(bytecode, password):
    import random
    class MyPRNG:
        def __init__(self, seed):
            self.state = seed
            self.a = 1103515245
            self.c = 12345
            self.m = 2**31
        def rand(self, max_val=255):
            self.state = (self.a * self.state + self.c) % self.m
            return self.state % (max_val + 1)
    prng = MyPRNG(int.from_bytes(password, 'big'))
    sequence = [prng.rand(255) for _ in range(255)]
    title = []
    for i, c in enumerate(bytecode[:4096]):
        title.append(c ^ sequence[i%len(sequence)])
    bytecode = bytes(title) + bytecode[4096:]
    return bytecode

def unpack(password):
    print('[*] unpack...')
    if not password: 
        print('[*] no password.')
        return
    localpath = os.path.split(__file__)[0]
    zfile = os.path.join(localpath, 'v_jstools.zip')
    tfile = os.path.join(localpath, 'temp.zip')
    if os.path.isfile(tfile): os.remove(tfile)
    with open(zfile, 'rb') as f1:
        with open(tfile, 'wb') as f2:
            f2.write(encbytefile(f1.read(), password.encode()))
    tpath = os.path.join(localpath, 'v_jstools')
    try:
        zf = zipfile.ZipFile(tfile)
        zf.extractall(path = tpath)
        zf.close()
        open_folder(tpath)
    except:
        if os.path.isdir(tpath):
            shutil.rmtree(tpath)
        print('[*] error password.')
        return

def execute():
    argv = sys.argv
    print('v_jstools :::: [ {} ]'.format(' '.join(argv)))
    if len(argv) == 1:
        print('[unpack]:  v_jstools unpack')
        return
    if len(argv) > 1:
        if argv[1] == 'unpack':
            password = None
            if len(argv) > 2:
                password = argv[2]
            unpack(password)
        return