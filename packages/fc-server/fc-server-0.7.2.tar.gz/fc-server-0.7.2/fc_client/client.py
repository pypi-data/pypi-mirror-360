#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2021-2025 NXP
#
# SPDX-License-Identifier: MIT


import argparse
import asyncio
import json
import os
import pathlib
import re
import signal
import socket
import subprocess
import sys
import textwrap
import time
import urllib.parse
from getpass import getuser
from socket import gethostname
from urllib.parse import urlparse, urlunparse

import aiohttp
import prettytable
import psutil
import requests
import yaml
from tenacity import retry, stop_after_attempt, wait_fixed

from fc_common import which
from fc_common.config import Config
from fc_common.version import get_runtime_version


class Client:
    daemon_pid_file = "/tmp/fc/fc_client_daemon.pid"
    etcd_url = None
    version = get_runtime_version("fc-client")
    me = "/".join(
        (
            os.environ.get("LG_HOSTNAME", gethostname()),
            os.environ.get("LG_USERNAME", getuser()),
        )
    )

    @staticmethod
    def action(caller, *caller_args):
        for caller_arg in caller_args:
            if "format" in caller_arg and caller_arg.format == "json":
                os.environ.setdefault("FC_DISABLE_INFO", "true")
                break

        Client.conditional_print(
            f"FC-CLIENT VERSION: {Client.version}, "
            "HOMEPAGE: https://fc.readthedocs.org/"
        )
        Client.mode_check()

        caller(*caller_args)

    @staticmethod
    def conditional_print(msg):
        if not os.environ.get("FC_DISABLE_INFO", None):
            print(msg)

    @staticmethod
    def verbose_print(msg, args):
        if args.verbose >= 10:
            print(msg)

    @staticmethod
    def mode_check():
        fc_server = os.environ.get("FC_SERVER", None)
        lg_crossbar = os.environ.get("LG_CROSSBAR", None)

        if fc_server and lg_crossbar:
            Client.conditional_print("MODE: single")
            Client.mode = "single"
        elif fc_server:
            Client.conditional_print(
                "MODE: cluster (LG_CROSSBAR not set, fallback to cluster mode)"
            )
            Client.mode = "cluster"
        elif lg_crossbar:
            Client.conditional_print(
                "MODE: cluster (FC_SERVER not set, fallback to cluster mode)"
            )
            Client.mode = "cluster"
        else:
            Client.conditional_print("MODE: cluster")
            Client.mode = "cluster"

    @staticmethod
    def labgrid_call(args, extras):
        verbose = ["-v"] * args.verbose

        metadata = Client.fetch_metadata(args.resource)
        os.environ["LG_CROSSBAR"] = metadata["lg"]

        # FIXME: temp fix for bootstrap command  # pylint: disable=fixme
        if extras and extras[0] in ["ssh", "scp"]:
            cmd = " ".join(extras)
            try:
                import fc_plugins  # pylint: disable=import-outside-toplevel

                cmd = fc_plugins.get_rule(metadata["lg"], extras[0])
                if len(extras) > 1:
                    cmd += " " + " ".join(extras[1:])
            except ImportError:
                pass

            os.environ["LG_PLACE"] = args.resource
            full_cmd = (
                ["labgrid-client"] + verbose + ["-p", args.resource] + cmd.split(" ")
            )
            Client.verbose_print(full_cmd, args)
            os.execvp("labgrid-client", full_cmd)
        else:
            full_cmd = ["labgrid-client"] + verbose + ["-p", args.resource] + extras
            Client.verbose_print(full_cmd, args)
            os.execvp("labgrid-client", full_cmd)

    @staticmethod
    def communicate_with_server_sync(url, aim=None):
        if aim:
            headers = {
                "X-FC-Client-ID": Client.me,
                "X-FC-Client-Version": Client.version,
                "X-FC-Aim": aim,
            }
        else:
            headers = {"X-FC-Client-ID": Client.me}

        output = requests.get(url, headers=headers)
        try:
            output_data = json.loads(output.text)
        except json.JSONDecodeError as exc:
            print(exc)
            sys.exit(
                "Fatal: unable to parse resource data,"
                f"status_code={output.status_code},"
                f"text={output.content}"
            )
        return output_data

    @staticmethod
    async def communicate_with_server_async(url, timeout=5):
        timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as response:
                    output = await response.text()
            except Exception as exc:  # pylint: disable=broad-except
                parsed = urlparse(url)
                fc_server = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
                Client.conditional_print(
                    f"Warning: {fc_server} skipped due to {type(exc)}"
                )
                return ""
        return output

    @staticmethod
    def communicate_with_daemon(msg_type, para=None):
        if os.path.exists(Client.daemon_pid_file):
            pid_file = pathlib.Path(Client.daemon_pid_file)
            pid_file = pid_file.resolve()

            pid = int(pid_file.read_text(encoding="utf-8").rstrip())

            if not psutil.pid_exists(pid):
                os.remove(Client.daemon_pid_file)

        if not os.path.exists(Client.daemon_pid_file):
            client_daemon = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "fc_client_daemon",
                "client_daemon.py",
            )
            subprocess.run([sys.executable, client_daemon], check=True)

        server_address = "\0/tmp/fc/fc_client_daemon.sock"
        retries = 0
        max_retries = 50
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        while True:
            try:
                sock.connect(server_address)
                break
            except socket.error as msg:
                if retries == max_retries:
                    sys.exit(f"Fatal: fc_client_daemon not available ({msg})")
                time.sleep(0.1)
                retries += 1

        msg = {"msg_type": msg_type, "para": para}
        json_msg = json.dumps(msg)

        sock.send(json_msg.encode("utf-8"))
        data = sock.recv(1024)
        sock.close()

        return data

    @staticmethod
    def fetch_metadata(filters):
        # single mode
        if Client.mode == "single":
            fc_server = os.environ.get("FC_SERVER", None)
            lg_crossbar = os.environ.get("LG_CROSSBAR", None)

            if filters == "all":
                return {"default": {"fc": fc_server, "lg": lg_crossbar}}
            return {"fc": fc_server, "lg": lg_crossbar}

        # cluster mode
        def check_etcd_cfg():
            Client.etcd_url = Config.load_cfg().get("etcd")
            if not Client.etcd_url:
                sys.exit("Fatal: please init cluster settings for your client first")

        check_etcd_cfg()

        data = Client.communicate_with_daemon("require_info", filters)
        json_data = json.loads(data.decode("utf-8"))

        if filters != "all" and not json_data:
            sys.exit("Fatal: invalid resource")

        return json_data

    @staticmethod
    def init(extras):
        if len(extras) == 0 or extras[0] not in ["etcd"]:
            sys.exit("Candidated init para: etcd")

        if len(extras) == 1:
            cfg = Config.load_cfg()
            cfg.pop(extras[0], "")
            Config.save_cfg(cfg)
            Client.communicate_with_daemon("daemon_stop")
            print(f"{extras[0]} removed")
        elif len(extras) == 2:
            cfg = Config.load_cfg()
            cfg.update({extras[0]: extras[1]})
            Config.save_cfg(cfg)
            Client.communicate_with_daemon("daemon_stop")
            print("Init done")
        else:
            print("Wrong command")

    @staticmethod
    def cluster_info(args):
        async def get_server_info(fc_server):
            url = f"{fc_server}/server_info"
            return await Client.communicate_with_server_async(url)

        if args.resource:
            metadata = Client.fetch_metadata(args.resource)
            print(f"export FC_SERVER={metadata['fc']}")
            print(f"export LG_CROSSBAR={metadata['lg']}")
        else:
            metadata = Client.fetch_metadata("all")
            print(f"ETCD: {Client.etcd_url}")

            # fetch server info
            tasks = [
                get_server_info(instance_meta["fc"])
                for instance_meta in metadata.values()
            ]
            loop = asyncio.get_event_loop()
            server_info_data = loop.run_until_complete(asyncio.gather(*tasks))

            # show per instance info
            print(f"Totally {len(metadata)} instances as follows:")
            index = 0
            for instance_name, data in metadata.items():
                print(f"{instance_name}({server_info_data[index]}):")
                print(f"  - export FC_SERVER={data['fc']}")
                print(f"  - export LG_CROSSBAR={data['lg']}")
                index += 1

    @staticmethod
    def all_locks(_):
        async def get_all_locks(fc_server):
            url = f"{fc_server}/all_locks"
            return await Client.communicate_with_server_async(url, 10)

        metadata = Client.fetch_metadata("all")

        instances = list(metadata.keys())
        tasks = [
            get_all_locks(instance_meta["fc"]) for instance_meta in metadata.values()
        ]
        loop = asyncio.get_event_loop()
        all_locks_data = loop.run_until_complete(asyncio.gather(*tasks))

        for index, data in enumerate(all_locks_data):
            print(f"- Instance {instances[index]}:")
            print(data)

    @staticmethod
    def status(args):  # pylint: disable=too-many-statements
        async def get_status(fc_server):
            specified_resource = args.resource
            specified_farm_type = args.farm_type
            specified_device_type = args.device_type
            specified_peripheral_info = args.peripheral_info

            url = f"{fc_server}/resources"

            if specified_resource:
                url += f"/{specified_resource}"

            query = {"verbose": args.verbose}
            if specified_farm_type:
                query["farmtype"] = specified_farm_type
            if specified_device_type:
                query["devicetype"] = specified_device_type
            if specified_peripheral_info:
                query["peripheralinfo"] = specified_peripheral_info
            query_string = urllib.parse.urlencode(query)

            if query_string:
                url += f"?{query_string}"

            if args.verbose >= 2:
                client_timeout = 15
            else:
                client_timeout = 5
            output = await Client.communicate_with_server_async(url, client_timeout)
            if output == "":
                return []

            try:
                ret = json.loads(output)
            except Exception:  # pylint: disable=broad-except
                return []

            return ret

        metadata = Client.fetch_metadata("all")

        tasks = [get_status(instance_meta["fc"]) for instance_meta in metadata.values()]
        loop = asyncio.get_event_loop()
        resource_data = loop.run_until_complete(asyncio.gather(*tasks))
        resources = sum(resource_data, [])

        if args.verbose == 0:
            field_names = ["Resource", "Farm", "Status"]
        elif args.verbose == 1:
            field_names = ["Resource", "Farm", "Status", "Comment"]
        elif args.verbose == 2:
            field_names = ["Resource", "Farm", "Status", "Comment", "Label"]
        else:
            field_names = [
                "Resource",
                "Farm",
                "Status",
                "Comment",
                "Label",
                "Info",
            ]

        if args.format == "json":
            print(json.dumps(resources))
        else:
            table = prettytable.PrettyTable(align="l")
            max_info_width = 60

            for resource in resources:
                if "comment" in resource:
                    resource["comment"] = textwrap.fill(resource["comment"], width=25)
                for key in ("label", "info"):
                    if key in resource:
                        yaml_str = yaml.dump(resource[key], allow_unicode=True)
                        if key == "info" and any(
                            len(line) > max_info_width for line in yaml_str.splitlines()
                        ):
                            yaml_str = "\n".join(
                                textwrap.fill(line, width=max_info_width)
                                for line in yaml_str.splitlines()
                            )
                        resource[key] = yaml_str
                table.add_row([resource[field.lower()] for field in field_names])

            table.field_names = field_names

            print(table.get_string(sortby="Resource"))

    @staticmethod
    @which(
        "labgrid-client",
        "Use 'pip3 install labgrid' or other customized way to install labgrid software please.",
    )  # pylint: disable=too-many-branches, too-many-statements
    def lock(args):
        def check_resource_ready():
            print(f"Check if {resource} is free...")
            url = f"{fc_server}/resources/{resource}"
            output_data = Client.communicate_with_server_sync(url, "lock")
            Client.verbose_print(output_data, args)

            rc = output_data.get("rc")  # pylint: disable=invalid-name
            if rc != 0:
                reason = output_data.get("msg", "Unknown error")
                if rc == 2 and "labgrid" in reason:
                    print(reason)
                else:
                    sys.exit(f"Fatal: {reason}")

        @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
        def check_labgrid_resource_ready(resource):
            cmd = f"labgrid-client -p {resource} show | grep acquired:"
            ret, place_info_text = subprocess.getstatusoutput(cmd)
            if ret == 0:
                acquired = place_info_text.split()[1]
                if acquired not in ["fc/fc", "None"]:
                    sys.exit(
                        f"error: place {resource} is already acquired by {acquired}"
                    )
                if acquired == "None":
                    raise Exception

        resource = args.resource
        metadata = Client.fetch_metadata(resource)

        fc_server = metadata.get("fc", None)
        if not fc_server:
            sys.exit("Fatal: invalid resource")

        if resource:
            os.environ["LG_CROSSBAR"] = metadata["lg"]

            check_resource_ready()
            try:
                check_labgrid_resource_ready(resource)
            except Exception:  # pylint: disable=broad-except
                sys.exit(
                    f"error: place {resource} is not ready, "
                    "contact admin to recover this device please "
                    "if this persists after a few minutes"
                )

            print(f"Try to acquire resource {resource}...")
            with subprocess.Popen(
                ["labgrid-client", "reserve", "--wait", f"name={resource}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as process:
                try:
                    process.communicate()
                    subprocess.call(["labgrid-client", "-p", resource, "lock"])
                except KeyboardInterrupt:
                    signal.signal(signal.SIGINT, lambda _: "")
                    token = ""
                    for line in process.stdout.readlines():
                        line = line.decode("UTF-8").strip()
                        if line.startswith("token:"):
                            token = line[7:]
                            break
                    if token:
                        subprocess.call(["labgrid-client", "cancel-reservation", token])
                        subprocess.call(
                            ["labgrid-client", "-p", resource, "unlock"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT,
                        )
        else:
            sys.exit("No resource specified.")

    @staticmethod
    @which(
        "labgrid-client",
        "Use 'pip3 install labgrid' or other customized way to install labgrid software please.",
    )
    def unlock(args):
        resource = args.resource
        metadata = Client.fetch_metadata(resource)
        os.environ["LG_CROSSBAR"] = metadata["lg"]

        if resource:  # pylint: disable=too-many-nested-blocks
            cmd = f"labgrid-client -p {resource} show"
            ret, place_info_text = subprocess.getstatusoutput(cmd)
            if ret == 0:
                token = ""
                place_info_lines = place_info_text.splitlines()
                for line in place_info_lines:
                    if line.find("reservation") >= 0:
                        token = line.split(":")[-1].strip()
                        break

                if token:
                    cmd = "labgrid-client reservations"
                    reservations_text = subprocess.check_output(cmd, shell=True)
                    reservations = yaml.load(reservations_text, Loader=yaml.FullLoader)
                    for k, v in reservations.items():  # pylint: disable=invalid-name
                        if k == f"Reservation '{token}'":
                            owner = v["owner"]
                            if owner == Client.me:
                                print("Start to free the place.")
                                signal.signal(signal.SIGINT, lambda _: "")
                                subprocess.call(
                                    ["labgrid-client", "cancel-reservation", token]
                                )
                                subprocess.call(
                                    ["labgrid-client", "-p", resource, "unlock"]
                                )
                            else:
                                sys.exit("Fatal: the resource not owned by you.")
                            break
            else:
                sys.exit(f"Fatal: {place_info_text}")
        else:
            sys.exit("No resource specified.")


class VerbosityAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest, 0)
        if values is None:
            setattr(namespace, self.dest, current + 1)
        elif values.isdigit():
            setattr(namespace, self.dest, current + int(values))
        elif re.fullmatch(r"v+", values):
            setattr(namespace, self.dest, current + len(values) + 1)
        else:
            parser.error(f"Invalid verbosity argument: {values}")


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
        "-r", "--resource", "-p", "--place", type=str, help="resource name"
    )
    parser.add_argument("-f", "--farm-type", type=str, help="farm type")
    parser.add_argument("-d", "--device-type", type=str, help="device type")
    parser.add_argument("-i", "--peripheral-info", type=str, help="peripheral info")
    parser.add_argument(
        "-v",
        "--verbose",
        action=VerbosityAction,
        nargs="?",
        default=0,
        help="increase verbosity level "
        "(can be used multiple times or with a number: -v, -vv, -v1, -v2)",
    )

    args, extras = parser.parse_known_args()

    if (
        len(extras) > 0
        and extras[0]
        in [
            "status",
            "s",
            "lock",
            "l",
            "unlock",
            "u",
            "all-locks",
            "a",
            "cluster-info",
            "c",
            "init",
            "i",
        ]
        or not args.resource
    ):
        subparsers = parser.add_subparsers(
            dest="command",
            title="available subcommands",
            metavar="COMMAND",
        )

        subparser = subparsers.add_parser(
            "status", aliases=("s",), help="list status of fc resource"
        )
        subparser.add_argument(
            "--json",
            dest="format",
            default=None,
            action="store_const",
            const="json",
            help="show as json",
        )
        subparser.set_defaults(func=Client.status)

        subparser = subparsers.add_parser(
            "lock", aliases=("l", "acquire"), help="labgrid lock resource"
        )
        subparser.set_defaults(func=Client.lock)

        subparser = subparsers.add_parser(
            "unlock", aliases=("u", "release"), help="labgrid unlock resource"
        )
        subparser.set_defaults(func=Client.unlock)

        subparser = subparsers.add_parser(
            "all-locks", aliases=("a",), help="list all locks"
        )
        subparser.set_defaults(func=Client.all_locks)

        subparser = subparsers.add_parser(
            "cluster-info", aliases=("c",), help="list cluster info"
        )
        subparser.set_defaults(func=Client.cluster_info)

        subparser = subparsers.add_parser("init", aliases=("i",), help="init fc-client")
        subparser.set_defaults(func=Client.init)

        if len(extras) > 0 and extras[0] in ["init", "i"]:
            args, extras = parser.parse_known_args(extras, namespace=args)
            Client.action(args.func, extras)
        else:
            args = parser.parse_args(extras, namespace=args)
            Client.action(args.func, args)
    else:
        Client.action(Client.labgrid_call, args, extras)


if __name__ == "__main__":
    main()
