
import os
import bsdiff4 as bd
import argparse
import hashlib
import pandas as pd

from .utils import get_files_matched


parser = argparse.ArgumentParser(prog = 'bsync-make', description = "prepare local repository for upload")
parser.add_argument('--version', help = 'The version to make', required = True)

def main():

    args = parser.parse_args()
    cwd = os.getcwd()

    bsync = '.bsync'
    bsync_base = os.path.join(bsync, 'base')
    bsync_versions = os.path.join(bsync, 'versions')
    bsync_patches = os.path.join(bsync, 'patches')
    bsync_previous = os.path.join(bsync, 'previous')
    bsync_f_current = os.path.join(bsync, 'current')
    bsync_f_checksums = os.path.join(bsync, 'checksums')

    fresh = False
    if not os.path.exists(bsync):
        fresh = True
        os.makedirs(bsync)
    
    if fresh:

        # make base and previous directory with plain structure
        repos = get_files_matched('.')
        ids = [x for x in range(1, len(repos) + 1)]
        md5s = []

        for file in repos:
            with open(file[1:], 'rb') as f:
                content = f.read()
                md5s.append(hashlib.md5(content).hexdigest())

        table_checksum = pd.DataFrame({
            'id': ids,
            'source': repos,
            'repo': [f'/base/{id}' for id in ids],
            'md5': md5s
        })

        table_checksum['version'] = 'base'
        table_checksum['base'] = '-'
        table_checksum['patch'] = '-'
        table_checksum['previous'] = '-'

        if not os.path.exists(bsync_base):
            os.makedirs(bsync_base)
        
        for _id, _src, _repo in zip(table_checksum['id'], table_checksum['source'], table_checksum['repo']):
            os.system(f'cp .{_src} {bsync}{_repo}')

        # copy previous directory

        id_start = max(len(table_checksum) + 1, table_checksum['id'].max())
        version_checksum = pd.DataFrame({
            'id': [x for x in range(id_start, len(repos) + id_start)],
            'source': repos,
            'md5': md5s
        })

        version_checksum['repo'] = '-'
        version_checksum['version'] = args.version
        version_checksum['base'] = ids
        version_checksum['patch'] = '-'
        version_checksum['previous'] = '-'

        if not os.path.exists(bsync_previous):
            os.makedirs(bsync_previous)

        for _id, _baseid in zip(version_checksum['id'], version_checksum['base']):
            os.system(f'ln -s ../base/{_baseid} {bsync}/previous/{_id}')

        # make patches.
        if not os.path.exists(os.path.join(bsync_patches, args.version)):
            os.makedirs(os.path.join(bsync_patches, args.version))
        
        # the first version do not have patches

        cksums = pd.concat([table_checksum, version_checksum])
        cksums.to_csv(bsync_f_checksums, sep = '\t', index = False)

        with open(bsync_f_current, 'w') as f:
            f.writelines([args.version])
    
    else:
        
        index = pd.read_table(bsync_f_checksums)

        # calculate the versioning file identities

        repos = get_files_matched('.')
        id_start = max(len(index) + 1, index['id'].max())
        ids = [x for x in range(id_start, len(repos) + id_start)]
        md5s = []
        bases = []
        patch = []
        previous = []

        for file in repos:
            with open(file[1:], 'rb') as f:
                content = f.read()
                md5s.append(hashlib.md5(content).hexdigest())

        # to check if there is identical md5 in the index previously
        # this indicates a file's recurrence.

        id_start += len(repos)
        planned_patches = []
        patch_from = []
        patch_to = []
        patch_base = []
        patch_previous = []

        for _id, _src, _md5 in zip(ids, repos, md5s):

            # test if there is identical id
            query = index.loc[(index['md5'] == _md5) & (index['version'] != 'patch'), :]
            qsrc = index.loc[
                (index['source'] == _src) & 
                (index['version'] != 'patch') & 
                (index['version'] != 'base'), :
            ].copy()
            
            if len(query) >= 1:
                earliest = query.iloc[0, :]
                
                if earliest['version'] == 'base':
                    bases.append(earliest["id"])
                    patch.append(earliest["patch"])
                    previous.append(earliest["previous"])
                    
                    # link the base to previous
                    os.system(f'ln -s ../base/{earliest["id"]} {bsync}/previous/{_id}')
                
                else:
                    bases.append(earliest["base"])
                    patch.append(earliest["patch"])
                    previous.append(earliest["previous"])

                    # link the base to previous
                    os.system(f'ln -s ./{earliest["id"]} {bsync}/previous/{_id}')
            
            # test identical src name
            elif len(qsrc) >= 1:

                # sort the source list of the same file using the version number
                qsrc['major'] = [int(x.split('.')[0]) for x in qsrc['version']]
                qsrc['minor'] = [int(x.split('.')[1]) for x in qsrc['version']]
                qsrc['revision'] = [int(x.split('.')[2]) for x in qsrc['version']]
                qsrc = qsrc.sort_values(['major', 'minor', 'revision'], ascending = False)
                latest = qsrc.iloc[0, :]

                # add a planned patch
                planned_patches.append(id_start)
                patch_from.append(f'{bsync_previous}/{latest["id"]}')
                patch_to.append(_src)
                patch_base.append(latest['base'])
                patch_previous.append(latest['id'])

                bases.append(latest['base'])
                patch.append(
                    (' '.join([str(latest['patch']), str(id_start)]))
                    if str(latest['patch']) != '-' else str(id_start)
                )

                previous.append(latest["id"])

                # copy and previous
                os.system(f'cp .{_src} {bsync}/previous/{_id}')

                id_start += 1
            
            # completely new.
            else:

                # add a new base
                planned_patches.append(id_start)
                patch_from.append('-')
                patch_to.append(_src)
                patch_base.append(id_start)
                patch_previous.append('-')

                bases.append(id_start)
                patch.append('-')
                previous.append('-')

                # copy to base and previous
                os.system(f'cp .{_src} {bsync}/base/{id_start}')
                os.system(f'ln -s ../base/{id_start} {bsync}/previous/{_id}')
                id_start += 1

        version_checksum = pd.DataFrame({
            'id': ids,
            'source': repos,
            'md5': md5s,
            'base': bases,
            'patch': patch,
            'previous': previous
        })

        version_checksum['version'] = args.version
        version_checksum['repo'] = '-'

        # make planned patches.
        
        patch_version = []
        patch_md5 = []

        if not os.path.exists(os.path.join(bsync_patches, args.version)):
            os.makedirs(os.path.join(bsync_patches, args.version))

        for _id, _from, _to, _base, _prev in zip(
            planned_patches, patch_from, patch_to, patch_base, patch_previous
        ):
            if _from != '-':
                
                patch_path = os.path.join(bsync_patches, args.version, str(_id))
                patch_version.append('patch')
                bd.file_diff(_from, _to[1:], patch_path)

                with open(patch_path, 'rb') as f:
                    content = f.read()
                    patch_md5.append(hashlib.md5(content).hexdigest())
            
            else:

                # copy the file
                patch_version.append('base')
                with open(os.path.join(bsync_base, str(_id)), 'rb') as f:
                    content = f.read()
                    patch_md5.append(hashlib.md5(content).hexdigest())


        patch_checksum = pd.DataFrame({
            'id': planned_patches,
            'source': patch_to,
            'repo': [
                (f'/patches/{args.version}/{_id}' if _type == 'patch' else f'/base/{_id}') 
                for _id, _type in zip(planned_patches, patch_version)
            ],
            'version': patch_version,
            'md5': patch_md5,
            'base': patch_base,
            'patch': ['-'] * len(planned_patches),
            'previous': patch_previous
        })

        cksums = pd.concat([index, version_checksum, patch_checksum])
        cksums['id'] = cksums['id'].astype('int')
        cksums.to_csv(bsync_f_checksums, sep = '\t', index = False)

        with open(bsync_f_current, 'w') as f:
            f.writelines([args.version])