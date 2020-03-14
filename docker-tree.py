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
        # add {"State":"image"}
        x = json.loads(result)[0]
        x.update({"State":{"Status":"image"}})
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

def print_line(indent, header, body_items=[], body_dlm=" "):
    print("{}{}".format(" "*(indent*2), header), end="")
    if body_items:
        print(body_dlm.join([ "{}".format(i) for i in body_items if i ]),
              end="")
    print()

def print_parent(kv, indent):
    status = kv["State"]["Status"]  # saved for use later.
    self_id = kv["Id"]
    if opt.truncate:
        self_id = self_id.split(":")[-1][:12]
    if opt.verbose:
        status_id = status.capitalize()
        ctime = kv["Created"]
    else:
        status_id = status.capitalize()[0]
        ctime = None
    #
    name = kv.get("Name", "")
    if opt.debug:
        print("Name:", name)
    if status == "image":
        # image
        if kv["RepoTags"]:
            print_line(indent, "> ",
                       [status_id, self_id, ctime,
                        "Tag:{}".format(",".join(kv["RepoTags"]))])
        else:
            print_line(indent, "> ", [status_id, self_id, ctime])
    else:
        # container
        print_line(indent, "> ", [status_id, self_id, ctime,
                        "Name:{}".format(name)])
        if opt.verbose:
            if kv["Mounts"]:
                print_line(indent+1, "- ", ["Mount:"])
                for x in kv["Mounts"]:
                    print_line(indent+1, "    ",
                               [x.get("Name",x.get("Source")),
                                x.get("Destination")])
            if kv["NetworkSettings"]["Networks"]:
                print_line(indent+1, "- ", ["Net:"])
                for k, v in kv["NetworkSettings"]["Networks"].items():
                    print_line(indent+1, "    ", [k, v["IPAddress"]], ":")
            if kv["NetworkSettings"]["Ports"]:
                print_line(indent+1, "- ", ["Port:"])
                for k, v in kv["NetworkSettings"]["Ports"].items():
                    if v:
                        print_line(indent+1, "    ",
                                   [v[0]["HostIp"], v[0]["HostPort"], k], ":")
                    else:
                        print_line(indent+1, "    ", [k])
    #
    if kv.get("_Child"):
        for cid in kv["_Child"]:
            # XXX too slow
            c = next(x for x in hash_list if x["Id"] == cid)
            print_parent(c, indent+1)

#
# main
#
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
ap = ArgumentParser(
        description="display tree of docker containers and images.",
        formatter_class=ArgumentDefaultsHelpFormatter)
ap.add_argument("--no-trunc", "-l", action="store_false", dest="truncate",
                help="disable hash truncation.")
ap.add_argument("--verbose", "-v", action="store_true", dest="verbose",
                help="enable verbose mode.")
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
        print_parent(kv, 0)
        print()

