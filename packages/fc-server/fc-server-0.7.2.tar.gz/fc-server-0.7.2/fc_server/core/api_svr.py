# -*- coding: utf-8 -*-
#
# Copyright 2021-2025 NXP
#
# SPDX-License-Identifier: MIT


import asyncio
import json
import logging
import weakref
from contextlib import suppress
from string import Template

import aiohttp
import flatdict
from aiohttp import web

from fc_common.version import get_runtime_version
from fc_server.core import AsyncRunMixin
from fc_server.core.config import Config


class ApiSvr(AsyncRunMixin):
    """
    Rest api server
    """

    def __init__(self, context):
        self.context = context
        self.external_info_tool = Config.api_server.get("external_info_tool", "")
        self.logger = logging.getLogger("fc_server")

    @staticmethod
    def friendly_status(status):
        with suppress(Exception):
            return Config.frameworks_config[status]["friendly_status"]
        return status

    async def resource_status(self, request):
        res = request.match_info.get("res", "")
        client_version = request.headers.get("X-FC-Client-Version", "")
        aim = request.headers.get("X-FC-Aim", None)
        if aim:
            client_id = request.headers.get("X-FC-Client-ID", "")
            self.logger.info(
                "client(%s): %s try to %s %s", client_version, client_id, aim, res
            )

            status = self.context.managed_resources_status.get(res, None)
            if not status:
                check_info = {"rc": 1, "msg": f"Fatal: invalid resource {res}"}
            elif status in ("retired",):
                check_info = {
                    "rc": 1,
                    "msg": f"Resource {res} currently in the status of {status}",
                }
            elif status in Config.registered_frameworks:
                check_info = {
                    "rc": 2,
                    "msg": f"Resource {res} currently belongs to {status}",
                }
            else:
                check_info = {"rc": 0}
            return web.json_response(check_info)

        return web.json_response(await self.fetch_resource_status(request))

    async def fetch_resource_status(
        self, request
    ):  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
        res = request.match_info.get("res", "")

        params = request.rel_url.query
        verbose = int(params.get("verbose", "0"))
        farm_type = params.get("farmtype", "")
        device_type = params.get("devicetype", "")
        peripheral_info = params.get("peripheralinfo", "")

        # get all labgrid managed resources
        labgrid_managed_resources = []
        comments = {}
        overlay_comments = {}
        for framework in self.context.framework_instances:
            if framework.__module__.split(".")[-1] == "labgrid":
                labgrid_managed_resources = framework.managed_resources
                if verbose >= 1:
                    comments = await framework.labgrid_get_comments()
            if framework.__module__.split(".")[-1] == "lava":
                if verbose >= 1:
                    overlay_comments = await framework.get_comments(self.context)
        comments.update(overlay_comments)

        if device_type and farm_type:
            scope = Config.raw_managed_resources.get(farm_type, {}).get(device_type, [])
        elif device_type:
            scope = []
            for raw_managed_resource in Config.raw_managed_resources.values():
                scope += raw_managed_resource.get(device_type, [])
        elif farm_type:
            scope = flatdict.FlatterDict(
                Config.raw_managed_resources.get(farm_type, {})
            ).values()
        else:
            scope = ["all"]

        if res:
            if scope == ["all"]:
                scope = [res]
            else:
                if res in scope:
                    scope = [res]
                else:
                    scope = []

        resources_info = []
        tool_command_list = []
        for resource, status in self.context.managed_resources_status.items():
            if scope != ["all"] and resource not in scope:
                continue

            item = {}
            item["resource"] = resource
            item["farm"] = Config.managed_resources_farm_types.get(resource, "")
            item["status"] = ApiSvr.friendly_status(status)

            if verbose >= 1:
                try:
                    item["comment"] = comments[resource]
                except KeyError:
                    item["comment"] = ""

            if verbose >= 2:
                item["label"] = (
                    {"error": "undebuggable"}
                    if resource not in labgrid_managed_resources
                    else Config.labels.copy()
                )

            if verbose >= 3:
                item["info"] = []

            resources_info.append(item)

            # fetch external resource info if needed
            if self.external_info_tool and (verbose >= 2 or peripheral_info):
                fc_resource = resource
                fc_farm_type = Config.managed_resources_farm_types.get(resource, "")
                template = Template(self.external_info_tool)
                tool_command = template.substitute(
                    {
                        "fc_resource": fc_resource,
                        "fc_farm_type": fc_farm_type,
                        "fc_peripheral_info": peripheral_info,
                    }
                )
                # FIXME: workaround to compatible with v0.6.16. To be deleted  # pylint: disable=fixme
                tool_command = "NEW=1 " + tool_command
                # END to be deleted
                tool_command_list.append(self._run_cmd(tool_command))

        fc_not_match_list = []
        if self.external_info_tool and (verbose >= 2 or peripheral_info):
            external_info_list = await asyncio.gather(*tool_command_list)
            for index, value in enumerate(external_info_list):
                if value[0] == 0:
                    additional_labels = {}
                    try:
                        content = json.loads(value[1])
                        fc_labels = content.get("fc_labels", None)
                        if isinstance(fc_labels, dict):
                            additional_labels = fc_labels
                    except json.JSONDecodeError:
                        if value[1].strip() != "FC_NOT_MATCH":
                            self.logger.error(
                                "Failed to decode JSON for informaton %s",
                                value[1],
                            )
                        content = []

                    if verbose >= 2 and "error" not in resources_info[index]["label"]:
                        resources_info[index]["label"].update(additional_labels)

                    if verbose >= 3:
                        resources_info[index]["info"] = content

                    if peripheral_info and value[1].strip() == "FC_NOT_MATCH":
                        fc_not_match_list.append(index)
                else:
                    if peripheral_info:
                        fc_not_match_list.append(index)
        elif peripheral_info:
            for index, resource in enumerate(resources_info):
                fc_not_match_list.append(index)

        resources_info = [
            item
            for index, item in enumerate(resources_info)
            if index not in fc_not_match_list
        ]

        return resources_info

    @staticmethod
    async def pong(_):
        return web.Response(text="pong")

    @staticmethod
    async def server_info(_):
        return web.Response(text=f"v{get_runtime_version('fc-server')}")

    async def all_locks(self, _):
        all_locks_info = [
            framework.lock_info(self.context)
            for framework in self.context.framework_instances
        ]
        all_locks_infos = await asyncio.gather(*all_locks_info)
        all_locks_infos = filter(lambda _: isinstance(_, str), all_locks_infos)

        return web.Response(text="\n".join(all_locks_infos))

    async def kick_booked_resource(self, request):  # pylint: disable=too-many-locals
        if not Config.enable_booking:
            return web.json_response(
                {"ret": 1, "reason": "booking not enabled for this instance"}
            )

        json_data = await request.json()
        self.logger.info(json_data)

        resource = json_data.get("resource", None)
        user = json_data.get("user", None)

        if not user:
            return web.json_response({"ret": 1, "reason": "no user specified"})

        if not resource:
            return web.json_response({"ret": 1, "reason": "no resource specified"})

        url = f"{Config.booking_system}/api/ongoing_booking/"
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as response:
                    output = await response.text()
                    json_output = json.loads(output)
                    res = json_output.get(resource, None)
                    if res:
                        allowd_user = res.get("user", "")
                        if allowd_user != user:
                            return web.json_response(
                                {"ret": 1, "reason": f"not {user}'s slot"}
                            )
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.info(exc)
                return web.json_response({"ret": 1, "reason": str(exc)})

        ret, reason = await self.context.kick_booked_resource(resource)

        return web.json_response({"ret": ret, "reason": reason})

    # FIXME: to be deleted  # pylint: disable=fixme
    async def resource_status2(self, request):
        return await self.fetch_resource_status2(request)

    async def verbose_resource_status(self, request):
        return await self.fetch_resource_status2(request, True)

    async def fetch_resource_status2(
        self, request, verbose=False
    ):  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
        # get all labgrid managed resources
        labgrid_managed_resources = []
        comments = {}
        overlay_comments = {}
        for framework in self.context.framework_instances:
            if framework.__module__.split(".")[-1] == "labgrid":
                labgrid_managed_resources = framework.managed_resources
                if verbose:
                    comments = await framework.labgrid_get_comments()
            if framework.__module__.split(".")[-1] == "lava":
                if verbose:
                    overlay_comments = await framework.get_comments(self.context)
        comments.update(overlay_comments)

        res = request.match_info.get("res", "")

        resources_info = []
        if res:
            if res in Config.managed_resources:
                item = []
                item.append(res)
                item.append(Config.managed_resources_farm_types.get(res, ""))
                item.append(
                    ApiSvr.friendly_status(
                        self.context.managed_resources_status.get(res, "")
                    )
                )
                if res not in labgrid_managed_resources:
                    item.append("non-debuggable")
                else:
                    item.append("")

                if verbose:
                    try:
                        item.append(comments[res])
                    except KeyError:
                        item.append("")

                if self.external_info_tool:
                    # fetch external resource info if needed
                    fc_resource = res
                    fc_farm_type = Config.managed_resources_farm_types.get(res, "")
                    template = Template(self.external_info_tool)
                    tool_command = template.substitute(
                        {
                            "fc_resource": fc_resource,
                            "fc_farm_type": fc_farm_type,
                            "fc_peripheral_info": "",
                        }
                    )
                    ret, info, _ = await self._run_cmd(tool_command)

                    if ret == 0:
                        item.append(info)
                    else:
                        item.append("NA")
                else:
                    item.append([])

                resources_info.append(item)
        else:
            params = request.rel_url.query
            farm_type = params.get("farmtype", "")
            device_type = params.get("devicetype", "")
            peripheral_info = params.get("peripheralinfo", "")

            if device_type and farm_type:
                scope = Config.raw_managed_resources.get(farm_type, {}).get(
                    device_type, []
                )
            elif device_type:
                scope = []
                for raw_managed_resource in Config.raw_managed_resources.values():
                    scope += raw_managed_resource.get(device_type, [])
            elif farm_type:
                scope = flatdict.FlatterDict(
                    Config.raw_managed_resources.get(farm_type, {})
                ).values()
            else:
                scope = ["all"]

            tool_command_list = []
            for resource, status in self.context.managed_resources_status.items():
                if scope != ["all"] and resource not in scope:
                    continue

                item = []
                item.append(resource)
                item.append(Config.managed_resources_farm_types.get(resource, ""))
                item.append(ApiSvr.friendly_status(status))
                if resource not in labgrid_managed_resources:
                    item.append("non-debuggable")
                else:
                    item.append("")

                if verbose:
                    try:
                        item.append(comments[resource])
                    except KeyError:
                        item.append("")

                resources_info.append(item)

                # fetch external resource info if needed
                if self.external_info_tool and device_type:
                    fc_resource = resource
                    fc_farm_type = Config.managed_resources_farm_types.get(resource, "")
                    template = Template(self.external_info_tool)
                    tool_command = template.substitute(
                        {
                            "fc_resource": fc_resource,
                            "fc_farm_type": fc_farm_type,
                            "fc_peripheral_info": peripheral_info,
                        }
                    )
                    tool_command_list.append(self._run_cmd(tool_command))

            fc_not_match_list = []
            if self.external_info_tool and device_type:
                external_info_list = await asyncio.gather(*tool_command_list)
                for index, value in enumerate(external_info_list):
                    if value[0] == 0:
                        resources_info[index].append(value[1])
                        if value[1].strip() == "FC_NOT_MATCH":
                            fc_not_match_list.append(index)
                    else:
                        resources_info[index].append("NA")
            elif (
                device_type
            ):  # for fc instance which doesn't configure external_info_tool
                for index, resource in enumerate(resources_info):
                    resource.append([])
                    if (
                        peripheral_info
                    ):  # external_info_tool not specified instance defintely not match anything
                        fc_not_match_list.append(index)

            resources_info = [
                item
                for index, item in enumerate(resources_info)
                if index not in fc_not_match_list
            ]

        return web.json_response(resources_info)

    # End to be deleted

    async def websocket_handler(self, request):
        logger = request.app["logger"]
        logger.info(f"Subscriber {request.remote} join")

        ws_resp = web.WebSocketResponse()
        await ws_resp.prepare(request)

        request.app["ws"].add(ws_resp)

        try:
            async for msg in ws_resp:
                if msg.type == aiohttp.WSMsgType.ERROR:
                    logger.info(ws_resp.exception())
        finally:
            request.app["ws"].discard(ws_resp)
            logger.info(f"Subscriber {request.remote} leave")

    async def publisher(self, app):
        logger = app["logger"]

        while True:
            msg = await self.context.publisher_queue.get()

            candidates = []
            for ws_resp in set(app["ws"]):
                logger.info(f"Send {msg} to subscriber")
                candidates.append(ws_resp.send_str(msg))
            await asyncio.gather(*candidates)

    async def on_startup(self, app):
        asyncio.create_task(self.publisher(app))

    async def start(self, **svr_args):
        app = web.Application()

        access_logger = logging.getLogger("aiohttp.access")
        access_logger.setLevel(logging.WARN)
        handler = logging.StreamHandler()
        s_format = logging.Formatter(
            fmt="%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(s_format)
        access_logger.addHandler(handler)

        app.add_routes([web.get("/ping", self.pong)])
        app.add_routes([web.get("/server_info", self.server_info)])
        app.add_routes([web.get("/all_locks", self.all_locks)])
        app.add_routes([web.get("/resources", self.resource_status)])
        app.add_routes([web.get("/resources/{res}", self.resource_status)])
        app.add_routes([web.put("/booked_resource", self.kick_booked_resource)])

        # FIXME: to be deleted  # pylint: disable=fixme
        app.add_routes([web.get("/booking", self.all_locks)])
        app.add_routes([web.get("/resource", self.resource_status2)])
        app.add_routes([web.get("/resource/{res}", self.resource_status2)])
        app.add_routes([web.get("/verbose_resource", self.verbose_resource_status)])
        app.add_routes(
            [web.get("/verbose_resource/{res}", self.verbose_resource_status)]
        )
        # END to be deleted

        # websocket
        app["logger"] = self.logger
        app["ws"] = weakref.WeakSet()
        app.add_routes([web.get("/ws", self.websocket_handler)])
        app.on_startup.append(self.on_startup)

        app_runner = web.AppRunner(app)
        await app_runner.setup()

        api_interface = "0.0.0.0"
        api_port = svr_args["port"]
        loop = asyncio.get_event_loop()
        await loop.create_server(app_runner.server, api_interface, api_port)
        self.logger.info("Api Server ready at http://%s:%d.", api_interface, api_port)
