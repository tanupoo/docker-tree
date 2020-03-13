#!/usr/bin/env python

from subprocess import Popen, PIPE
import shlex
import json

def exec_os_cmd(cmd):
    if opt.debug:
        print("cmd", cmd)
    args = shlex.split(cmd)
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    (stdout_data, stderr_data) = p.communicate()
    if p.returncode:
        print("ERROR:", p.returncode, stdout_data, stderr_data)
        exit(1)
    if opt.debug:
        print("STDOUT:")
        print(stdout_data)
        print("STDERR:")
        print(stderr_data)
    return stdout_data

def get_image_list():
    image_list = []
    result = exec_os_cmd("docker image ls -a --format '{{.ID}}' --no-trunc")
    for i in result.splitlines():
        result = exec_os_cmd("docker inspect {}".format(i.decode()))
        # add {"State":"stored"}
        x = json.loads(result)[0]
        x.update({"State":{"Status":"stored"}})
        image_list.append(x)
    return image_list

def get_container_list():
    container_list = []
    result = exec_os_cmd("docker container ls -a --format '{{.ID}}' --no-trunc")
    for i in result.splitlines():
        result = exec_os_cmd("docker inspect {}".format(i.decode()))
        # add "Parent" taken from "Image"
        x = json.loads(result)[0]
        x.update({
                "Parent":x["Image"]
                })
        container_list.append(x)
    return container_list

def print_parent(kv, indent):
    print("  "*indent, end="")
    #
    status = kv["State"]["Status"]  # saved for use later.
    status_id = status.capitalize()
    self_id = kv["Id"]
    ctime = kv["Created"] # assuming like 2020-02-21T22:20:44.446608273Z
    if opt.truncate:
        status_id = status_id[0]
        self_id = self_id.split(":")[-1][:12]
        ctime = ctime.replace("T", " ").split(".")[0]
    #
    print("{} {} {}".format(status_id, self_id, ctime), end="")
    if status == "running":
        # container
        print()
        print("{}> Mount:".format("  "*(indent+2)))
        for x in kv["Mounts"]:
            print("{}>    {} {}".format(
                    "  "*(indent+2),
                    x.get("Name",x.get("Source")),
                    x.get("Destination")))
        print("{}> Net:".format("  "*(indent+2)))
        for k, v in kv["NetworkSettings"]["Networks"].items():
            print("{}>    {} : {}".format(
                    "  "*(indent+2),
                    k, v["IPAddress"]
            ))
        print("{}> Port:".format("  "*(indent+2)))
        # >    8080/tcp : [{'HostIp': '0.0.0.0', 'HostPort': '8080'}]
        for k, v in kv["NetworkSettings"]["Ports"].items():
            if v:
                print("{}>    {}:{}:{}".format(
                        "  "*(indent+2),
                        v[0]["HostIp"], v[0]["HostPort"], k
                    ))
            else:
                print("{}>    {}".format(
                        "  "*(indent+2),
                        k
                    ))
    elif status == "stored":
        # image
        if kv["RepoTags"]:
            print(" Tag:{}".format(kv["RepoTags"]))
        else:
            print()
    #
    if kv.get("_Child"):
        for cid in kv["_Child"]:
            # XXX too slow
            c = next(x for x in hash_list if x["Id"] == cid)
            print_parent(c, indent+2)

#
# main
#
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
ap = ArgumentParser(
        description="display tree of docker containers and images.",
        formatter_class=ArgumentDefaultsHelpFormatter)
ap.add_argument("--no-trunc", action="store_false", dest="truncate",
                help="disable hash truncation.")
ap.add_argument("--debug", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

# get list.
hash_list = get_image_list()
hash_list.extend(get_container_list())

# set _Child.
for i in range(len(hash_list)):
    pid = hash_list[i]["Parent"]
    if pid:
        for j in range(len(hash_list)):
            if hash_list[j]["Id"] == pid:
                hash_list[j].setdefault("_Child", []).append(hash_list[i]["Id"])

# print result.
for kv in hash_list:
    if not kv["Parent"]:
        # it's a grand parent.
        print()
        print_parent(kv, 0)

