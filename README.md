ALIA
====

An online learning environment to remotely teach unix and similar technologies. Currently uses docker, websockets and few other technologies.

Creating Docker Machine
-----------------------

```shell
docker-machine create -d virtualbox --engine-env DOCKER_TLS=no --engine-env DOCKER_TLS_VERIFY=no --engine-opt host=tcp://0.0.0.0:2375 default
```
