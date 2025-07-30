# Getting Started

`dataset.sh` is a dataset manager designed to simplify the process of installing, managing, and publishing datasets.
We hope to make working with datasets as straightforward as using package managers like npm or pip for programming
libraries.

## Quickstart

### Host your own server (Optional)

```shell
docker run -v ./:/var/lib/dsh-server  datasetsh/server:latest dataset-sh-server-cli init
```

```shell
docker run -v ./:/var/lib/dsh-server  datasetsh/server:latest -d
```