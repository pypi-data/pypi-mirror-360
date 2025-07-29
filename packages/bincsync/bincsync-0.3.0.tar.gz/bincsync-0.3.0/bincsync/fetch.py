
import bsdiff4 as bd
import os
import oss2
import argparse
import hashlib
import pandas as pd

from .utils import io_get_directory, get_bucket_requester
from .ansi import green, cyan, error, info, warning, red, purple

parser = argparse.ArgumentParser(prog = 'bsync-fetch', description = "fetch from remote bucket.")

parser.add_argument('--id', help = 'The requester access id.', required = True)
parser.add_argument('--secret', help = 'The requester access secret.', required = True)
parser.add_argument('--bucket', help = 'The name of the bucket.', required = True)
parser.add_argument('--endpoint', help = 'The domain names that other services can use to access OSS.')
parser.add_argument('--version', help = 'The version to fetch from remote.', required = True)

def main():

    args = parser.parse_args()
    auth = oss2.Auth(args.id, args.secret)
    bucket = oss2.Bucket(auth, args.endpoint, args.bucket)

    fresh = False
    if not os.path.exists('.bsync'):
        info('you seem not to have a bsync database in the current directory.')
        info(f'downloading remote {args.bucket} v{args.version} to {os.getcwd()}')
        os.makedirs('.bsync')
        fresh = True
    
    elif os.path.exists('./.bsync/base'):
        error('you should not install a database to an established bsync database dump!')
    
    if os.path.exists('.bsync/current'):
        os.system('rm ./.bsync/current')

    with open('.bsync/checksums', 'wb') as f:
        f.write(get_bucket_requester(bucket, 'checksums').read())
    
    objt = pd.read_table('.bsync/checksums')
    objt = objt.set_index('id')

    vflist = objt.loc[objt['version'] == args.version, :]
    if len(vflist) == 0: error(f'no such version: v{args.version}')

    if not os.path.exists('.bsync/cache'):
        os.makedirs('.bsync/cache')

    download_success = True

    for _src, _md5, _base, _patch in zip(
        vflist['source'], vflist['md5'], vflist['base'], vflist['patch']
    ): 
        skip = False
        if os.path.exists(f'.bsync/cache/{_base}'):
            print(green('Cached'), f'Skipped package [base] {_base} for {_src}')
            base_checksum = objt.loc[int(_base), 'md5']
            with open(f'.bsync/cache/{_base}', 'rb') as fb:
                md5 = hashlib.md5(fb.read()).hexdigest()
                if md5 != base_checksum:
                    print('   ', red('Cache file seems to be corrupted. Download again.'))
                else: skip = True

        if not skip:
            print(cyan('Download'), f'[base] {_base} for {_src}', end = ' ')
            with open(f'.bsync/cache/{_base}', 'wb') as f:
                base_entry = objt.loc[int(_base), 'repo']
                base_checksum = objt.loc[int(_base), 'md5']
                content = get_bucket_requester(bucket, base_entry[1:]).read()
                md5 = hashlib.md5(content).hexdigest()
                if md5 == base_checksum: print(green('(MD5 Matched)'))
                else: 
                    print(red('(MD5 Inconsistant)'))
                    print('   ', green('Downloaded'), red(md5))
                    print('   ', 'Expected', red(base_checksum))
                    download_success = False
                f.write(content)
        
        if _patch == '-': pass
        else:
            patches = _patch.split(' ')
            for _pid in patches:
                
                skip = False
                if os.path.exists(f'.bsync/cache/{_pid}'):
                    print(green('Cached'), f'Skipped package [patch] {_pid} for {_src}')
                    with open(f'.bsync/cache/{_pid}', 'rb') as fb:
                        patch_checksum = objt.loc[int(_pid), 'md5']
                        md5 = hashlib.md5(fb.read()).hexdigest()
                        if md5 != patch_checksum:
                            print('   ', red('Cache file seems to be corrupted. Download again.'))
                        else: skip = True
                
                if not skip:
                    print(cyan('Download'), f'[patch] {_pid} for {_src}', end = ' ')
                    with open(f'.bsync/cache/{_pid}', 'wb') as f:
                        patch_entry = objt.loc[int(_pid), 'repo']
                        patch_checksum = objt.loc[int(_pid), 'md5']
                        content = get_bucket_requester(bucket, patch_entry[1:]).read()
                        md5 = hashlib.md5(content).hexdigest()
                        if md5 == patch_checksum: print(green('(MD5 Matched)'))
                        else: 
                            print(red('(MD5 Inconsistant)'))
                            print('   ', green('Downloaded'), red(md5))
                            print('   ', 'Expected', red(patch_checksum))
                            download_success = False
                        f.write(content)
    
    if not download_success:
        warning('the download process ended with errors.')
        warning('this may due to database corruption or transmission errors of the network.')
        warning('we do not proceed to modify the existing files, unless the download integrity is completely correct.')
        warning('you may delete the .bsync folder to enforce re-download from the server totally without cache.')
        warning('if problems still exists, report to the maintainer <xornent@outlook.com>.')
        error('procedure stopped due to failed integrity check.')

    # clear the workspace.
    # remove all files except .bsync

    for item in os.listdir():
        if item.startswith('.'): continue
        elif os.path.isfile(item):
            os.system(f'rm {item}')
        elif os.path.isdir(item):
            os.system(f'rm -r {item}')

    product_integrity = True

    for _src, _md5, _base, _patch in zip(
        vflist['source'], vflist['md5'], vflist['base'], vflist['patch']
    ):
        # ensure the directory exist
        if not os.path.exists(io_get_directory(f'.{_src}')):
            os.makedirs(io_get_directory(f'.{_src}'))
            print(purple('Make Directory'), io_get_directory(f'.{_src}'))

        # copy the base file
        os.system(f'cp ./.bsync/cache/{_base} .{_src}')

        # apply patches
        print(purple('Apply Patch'), _src, end = ' ')

        if _patch != '-':
            patches = _patch.split(' ')
            for p in patches:
                bd.file_patch_inplace(f'.{_src}', f'./.bsync/cache/{p}')
        
        with open(f'.{_src}', 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
            if md5 == _md5: print(green('(MD5 Matched)'))
            else: 
                print(red('Patched file is corrupted!'))
                product_integrity = False

    if not product_integrity:
        warning('patch integrity failed.')
        warning('this may due to database corruption or transmission errors of the network.')
        warning('we do not proceed to modify the existing files, unless the download integrity is completely correct.')
        warning('you may delete the .bsync folder to enforce re-download from the server totally without cache.')
        warning('if problems still exists, report to the maintainer <xornent@outlook.com>.')
        error('procedure stopped due to failed integrity check.')
    
    with open('./.bsync/current', 'w') as f:
        f.writelines([args.version])
    
    info(f'Installed database [Bucket: {args.bucket}] v{args.version} complete without errors.')
    
