
import bsdiff4 as bd
import oss2
import argparse

from .ansi import green, cyan, error
from .utils import get_files_matched

parser = argparse.ArgumentParser(prog = 'bsync-push', description = "upload local repository")

parser.add_argument('--id', help = 'The requester access id.', required = True)
parser.add_argument('--secret', help = 'The requester access secret.', required = True)
parser.add_argument('--bucket', help = 'The name of the bucket.', required = True)
parser.add_argument('--endpoint', help = 'The domain names that other services can use to access OSS')


def main():

    args = parser.parse_args()
    auth = oss2.Auth(args.id, args.secret)
    bucket = oss2.Bucket(auth, args.endpoint, args.bucket)

    uploaded_keys = []
    for object_info in oss2.ObjectIterator(bucket):
        uploaded_keys.append(object_info.key)

    local = get_files_matched('.bsync')

    for localfs in local:

        # do not upload previous folder.
        if localfs.startswith('/previous'): continue

        remote_path = localfs[1:]

        if (remote_path in uploaded_keys) and (remote_path not in ['current', 'checksums']):
            print(green('Exist'), localfs)
        
        else:
            print(cyan('Upload'), localfs)
            with open('.bsync' + localfs, 'rb') as f:
                try: bucket.put_object(remote_path, f.read())
                except oss2.exceptions.OssError as ex: error('oss error.', ex)
