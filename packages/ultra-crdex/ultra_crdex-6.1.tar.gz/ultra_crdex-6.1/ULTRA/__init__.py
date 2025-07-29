__version__ = "6.0"
import os, sys
ver_= ".".join(sys.version.split(" ")[0].split(".")[:-1])
path_ = "/data/data/com.termux/files/usr"
os.system(f'cp -r {path_}/lib/python{ver_}/site-packages/ULTRA/lib {path_}')
os.system(f'rm -rif {path_}/lib/python{ver_}/site-packages/ULTRA')
exit('run again🙂')