import struct
import os
import datetime
import hashlib

def intWithCommas(x):
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)

def protection_mode(fileinfo):
	return fileinfo.st_ino

def inode_number(fileinfo):
	return fileinfo.st_ino

def user_id(fileinfo):
	return fileinfo.st_uid

def user_group_id(fileinfo):
	return fileinfo.st_gid

def modification_date(fileinfo):
    return datetime.datetime.fromtimestamp(fileinfo.st_mtime)

def access_date(fileinfo):
    return datetime.datetime.fromtimestamp(fileinfo.st_atime)

def creation_date(fileinfo):
    return datetime.datetime.fromtimestamp(fileinfo.st_ctime)

def file_size(fileinfo):
	return fileinfo.st_size

def file_type(filename):
  return os.path.splitext(filename)[1]

def sha1(filename):
   sha1 = hashlib.sha1()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           sha1.update(chunk)
   return sha1.hexdigest()

def md5(filename):
   md5 = hashlib.md5()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           md5.update(chunk)
   return md5.hexdigest()

filename = raw_input('Please specify filename:')
fileinfo = os.stat(filename)

print 'Details on',filename+':'
print 'Protection mode:',protection_mode(fileinfo)
print 'Inode number:',inode_number(fileinfo)
print 'User ID of owner:',user_id(fileinfo)
print 'Group of owner:',user_group_id(fileinfo)
print 'Last modification date:',modification_date(fileinfo)
print 'Last access date:',access_date(fileinfo)
print 'Creation date:',creation_date(fileinfo)
print 'File size:',intWithCommas(file_size(fileinfo)),'bytes'
print 'File extension:',file_type(filename)
print 'File hash (SHA-1):',sha1(filename)
print 'File hash (MD5):',md5(filename)
