
# bincsync

bincsync is a tool to incrementally sync binary file distributions (as well as
creating them for upload). This tool is initially implemented for syncing
large genomic data files that changes little between versions, but have great
individual file size.

bincsync currently support the database version control from Alibaba Cloud 
object storage service (OSS). You should register an account for Alibaba OSS
to authenticate yourself to download from private repositories.

This utility suite will provide a commandline interface `bsync-fetch`. It also
provides `bsync-make` and `bsync-push` for database maintainers to publish 
databases that can be downloaded and managed with the fetch utility.

### Usage

```
usage: bsync-fetch [-h] --id ID --secret SECRET 
                        --bucket BUCKET [--endpoint ENDPOINT] --version VERSION

fetch from remote bucket.

options:
  -h, --help           show this help message and exit
  --id ID              The requester access id.
  --secret SECRET      The requester access secret.
  --bucket BUCKET      The name of the bucket.
  --endpoint ENDPOINT  The domain names that other services can use to access OSS.
  --version VERSION    The version to fetch from remote.
```

The authentication tokens passed to `--id` and `--secret` is provided by the
Alibaba Cloud service (See the [Documentation](https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair)
for details). For more explanation on `--bucket` and `--endpoint`, see
[here](https://help.aliyun.com/zh/oss/user-guide/endpoint). The `--version` 
option allow you to retrieve a specific version of the database release.
Contact your database distributor for the versioning scheme if you have no idea.

* This name is chosen because `bsync`, `bisync` and `binsync` are all registered. 