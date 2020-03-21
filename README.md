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
+-> I 72300a873c2c Tag:ubuntu:latest
|   +-> I dc8cd7028f12
|       +-> I 291f60e91c01
|           +-> I c6b7afae5de5
|               +-> I fae5136daa80
|                   +-> I 880716803a6e
|                       +-> I a428bc20948c Tag:netdebug:latest
|                           +-> E 48e1b214e5c7 Name:/heuristic_kalam
|                           +-> R 4ced86318737 Name:/keen_mahavira
+-> I 84164b03fa2e Tag:mysql:5.7
    +-> E d63a56851652 Name:/friendly_swartz
```

If you want more information about mount or network, use the option -v.

```
% docker-tree.py -v
+-> Image 72300a873c2c 2020-02-21T22:20:44.446608273Z Tag:ubuntu:latest
|   +-> Image dc8cd7028f12 2020-03-10T01:08:38.5711252Z
|       +-> Image 291f60e91c01 2020-03-10T01:08:44.0827128Z
|           +-> Image c6b7afae5de5 2020-03-10T01:08:48.0385706Z
|               +-> Image fae5136daa80 2020-03-10T01:08:58.5673291Z
|                   +-> Image 880716803a6e 2020-03-10T01:09:15.0997804Z
|                       +-> Image a428bc20948c 2020-03-10T01:09:25.7313365Z Tag:netdebug:latest
|                           +-> Exited 48e1b214e5c7 2020-03-21T15:28:25.046685902Z Name:/heuristic_kalam
|                           |     - Mount:
|                           |       debug-disk2 /mnt
|                           |     - Net:
|                           |       debug-net
|                           +-> Running 4ced86318737 2020-03-21T15:29:09.686685572Z Name:/keen_mahavira
|                                 - Mount:
|                                   debug-disk1 /mnt
|                                 - Net:
|                                   debug-net:172.18.0.2
|                                 - Port:
|                                   0.0.0.0:8888:8080/tcp
+-> Image 84164b03fa2e 2020-03-04T17:30:03.722683827Z Tag:mysql:5.7
    +-> Exited d63a56851652 2020-03-21T15:30:31.264577274Z Name:/friendly_swartz
          - Mount:
            21e629f7234e59682496abfcd813ba09e971b2ce9f5babd561856ac3b938c9e5 /var/lib/mysql
          - Net:
            debug-net
```

Then, you can use inspect comment for more detail. :)

## Limitation

Currently, this command just take the output of some docker commands. So, it may not work on other platform such as Windows. It may be improved by using the Docker socket API.
