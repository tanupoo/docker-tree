#!/usr/bin/env python

from subprocess import Popen, PIPE
import shlex
import json
import sys

(HDR1, HDR_NRM, HDR_END) = ("> ", "+-", "+-")
KEY_NODE_ID = "Id"
KEY_CHILDREN = "__children"
padlen = len(HDR_NRM + HDR1)
INFO_HDR = "  - "
INFO_HDR2 = "    "

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

def make_from_bottom_up_tree(L):
    def suspend(obj, xlist):
        for x in xlist:
            if obj["Parent"] == x[KEY_NODE_ID]:
                x.setdefault(KEY_CHILDREN, []).append(obj)
                return True
            elif x.get(KEY_CHILDREN):
                if suspend(obj, x.get(KEY_CHILDREN)):
                    return True

    for i in range(len(L)):
        x = L.pop(0)
        if x["Parent"]:
            suspend(x, L)
        else:
            L.append(x)

def sort_tree(xlist):
    for x in xlist:
        if x.get(KEY_CHILDREN):
            x[KEY_CHILDREN] = sort_tree(x[KEY_CHILDREN])
    return sorted(xlist, key=lambda x:(x[KEY_NODE_ID]))

def print_line(header, body_items=[], body_dlm=" "):
    print("{}".format(header), end="")
    if body_items:
        print(body_dlm.join([ "{}".format(i) for i in body_items if i ]),
              end="")
    print()

def get_better_unit(base_num):
    units = [ "B", "KB", "MB", "GB", "TB", "PB" ]
    if base_num < 1000:
        return base_num, units[0]
    ret = float(base_num)
    for i in range(len(units)):
        if ret < 1000:
            break
        ret = round(ret/1000, 2)
    return ret, units[i]

def print_node(kv, header, last_child):
    if last_child:
        head = HDR_END + HDR1
    else:
        head = HDR_NRM + HDR1
    status = kv["State"]["Status"]  # saved for use later.
    self_id = kv[KEY_NODE_ID]
    if opt.truncate:
        self_id = self_id.split(":")[-1][:12]
    if opt.verbose:
        status_id = status.capitalize()
        ctime = kv["Created"]
        img_size, unit = get_better_unit(kv["Size"])
        img_size = f"{img_size} {unit}"
    else:
        status_id = status.capitalize()[0]
        ctime = None
        img_size = None
    #
    name = kv.get("Name", "")
    if opt.debug:
        print("Name:", name)
    if status == "image":
        # image
        if kv["RepoTags"]:
            print_line(header+head,
                       [status_id, self_id, ctime, img_size,
                        "Tag:{}".format(",".join(kv["RepoTags"]))])
        else:
            print_line(header+head, [status_id, self_id, ctime, img_size])
    else:
        # container
        print_line(header+head,
                   [status_id, self_id, ctime, img_size,
                    "Name:{}".format(name)])
        if opt.verbose:
            if last_child:
                header += " ".ljust(padlen)
            else:
                header += "|".ljust(padlen)
            if kv["Mounts"]:
                print_line(header+INFO_HDR, ["Mount:"])
                for x in kv["Mounts"]:
                    print_line(header+INFO_HDR2,
                               [x.get("Name",x.get("Source")),
                                x.get("Destination")])
            if kv["NetworkSettings"]["Networks"]:
                print_line(header+INFO_HDR, ["Net:"])
                for k, v in kv["NetworkSettings"]["Networks"].items():
                    print_line(header+INFO_HDR2, [k, v["IPAddress"]], ":")
            if kv["NetworkSettings"]["Ports"]:
                print_line(header+INFO_HDR, ["Port:"])
                for k, v in kv["NetworkSettings"]["Ports"].items():
                    if v:
                        print_line(header+INFO_HDR2,
                                   [v[0]["HostIp"], v[0]["HostPort"], k], ":")
                    else:
                        print_line(header+INFO_HDR2, [k])

def print_child_tree(xlist, header, last_child):
    if last_child:
        header += " ".ljust(padlen)
    else:
        header += "|".ljust(padlen)
    print_tree(xlist, header)

def print_tree(hash_list, header):
    n = 0
    for x in hash_list:
        n += 1
        last_child = (n == len(hash_list))
        print_node(x, header, last_child)
        c = x.get(KEY_CHILDREN)
        if c:
            print_child_tree(c, header, last_child)

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
make_from_bottom_up_tree(hash_list)
hash_list = sort_tree(hash_list)
print_tree(hash_list, "")
