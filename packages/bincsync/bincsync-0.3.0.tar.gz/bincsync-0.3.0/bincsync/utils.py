
import bsdiff4 as bd
import oss2 as oss
import sys
import os


# support unix only.
def io_get_directory(path):

    if path.endswith('/'): return path[:-1]
    else: return '/'.join(path.split('/')[:-1])


def get_files_matched(basedir, startswith = None):

    def walk(dir, prefix = '/'):
        files = [x for x in os.listdir(dir) if (os.path.isfile(os.path.join(dir, x)) and (not x.startswith('.')))]
        dirs = [x for x in os.listdir(dir) if (os.path.isdir(os.path.join(dir, x)) and (not x.startswith('.')))]
        files = [prefix + x for x in files]
        for d in dirs: files += walk(os.path.join(dir, d), prefix = prefix + d + '/')
        return files
    
    fnames = walk(basedir)
    if startswith: fnames = [x for x in fnames if x.startswith(startswith)]
    return fnames


def get_bucket_requester(bucket, path, headers = {
    'x-oss-request-payer': 'requester'
}):
    return bucket.get_object(path, headers = headers)