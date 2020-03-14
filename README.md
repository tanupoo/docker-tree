docker-tree
============

There are several tools to see the relationship of the docker containers and images.  For example, [sen](https://github.com/TomasTomecek/sen) is a curses-based, or [dockviz](https://github.com/justone/dockviz) is a graphviz-based.

Different from those tools, this command line tool just displays the relationship and the network information. It is not fancy like others, but is enough before you ask the docker inspect command.

## Requirement

- Python3

## Usage

Just type docker-tree.py, then you can see the tree like below.

```
% docker-tree.py
> I 72300a873c2c Tag:ubuntu:latest
  > I dc8cd7028f12
    > I 291f60e91c01
      > I c6b7afae5de5
        > I fae5136daa80
          > I 880716803a6e
            > I a428bc20948c Tag:netdebug:latest
              > I 01d91c848b70 Tag:netdebug:saved
              > R 1f9d28e605ab Name:/debug-sindan-net3
              > C acf83d7c9a67 Name:/debug-sindan-net2
              > E a1d145214df6 Name:/debug-sindan-net
          > E 32589b13ccaf Name:/musing_kapitsa
        > R 4930cff89996 Name:/gracious_solomon
```

If you want more information about mount and network, use the option -v.

```
% docker-tree -v
> Image 72300a873c2c 2020-02-21T22:20:44.446608273Z Tag:ubuntu:latest
  > Image dc8cd7028f12 2020-03-10T01:08:38.5711252Z
    > Image 291f60e91c01 2020-03-10T01:08:44.0827128Z
      > Image c6b7afae5de5 2020-03-10T01:08:48.0385706Z
        > Image fae5136daa80 2020-03-10T01:08:58.5673291Z
          > Image 880716803a6e 2020-03-10T01:09:15.0997804Z
            > Image a428bc20948c 2020-03-10T01:09:25.7313365Z Tag:netdebug:latest
              > Image 01d91c848b70 2020-03-14T09:59:45.8384972Z Tag:netdebug:saved
              > Running 1f9d28e605ab 2020-03-14T10:11:20.7288934Z Name:/debug-sindan-net3
                - Net:
                    sindan-docker_default:172.21.0.6
                - Port:
                    0.0.0.0:8880:8880/tcp
              > Created acf83d7c9a67 2020-03-14T10:10:05.8275987Z Name:/debug-sindan-net2
                - Net:
                    sindan-docker_default
              > Exited a1d145214df6 2020-03-14T09:52:05.1332245Z Name:/debug-sindan-net
                - Net:
                    sindan-docker_default
          > Exited 32589b13ccaf 2020-03-14T09:49:30.2058773Z Name:/musing_kapitsa
            - Net:
                bridge
        > Running 4930cff89996 2020-03-14T09:50:10.4103525Z Name:/gracious_solomon
          - Net:
              bridge:172.17.0.2
```

Then, you can use inspect comment for more detail. :)

## Limitation

Currently, this command just take the output of some docker commands. So, it may not work on other platform such as Windows. It may be improved by using the Docker socket API.
