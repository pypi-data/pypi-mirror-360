# -*- coding: utf-8 -*-
#
# Copyright 2023, 2025 NXP
#
# SPDX-License-Identifier: MIT

import os
from getpass import getuser
from socket import gethostname
from unittest.mock import MagicMock, call

from fc_client.client import Client


class TestClient:
    def test_status(self, mocker, capsys):
        class Args:
            resource = "imx8mm-evk-sh11"
            farm_type = "bsp"
            device_type = "imx8mm-evk"
            verbose = 0
            format = None

        mocker.patch(
            "fc_client.client.Client.fetch_metadata",
            return_value={},
        )

        Client.status(Args)

        output = capsys.readouterr()[0]

        assert output in (
            """+----------+------+--------+
| Resource | Farm | Status |
+----------+------+--------+
+----------+------+--------+
""",
        )

    def test_json_status(self, mocker, capsys):
        class Args:
            resource = "imx8mm-evk-sh11"
            farm_type = "bsp"
            device_type = "imx8mm-evk"
            verbose = 0
            format = "json"

        mocker.patch(
            "fc_client.client.Client.fetch_metadata",
            return_value={},
        )

        Client.status(Args)

        output = capsys.readouterr()[0]
        print(output)

        assert output in ("[]\n",)

    def test_lock(self, mocker):
        class Args:
            resource = "imx8mm-evk-sh11"
            verbose = 0

        class Output:
            def __init__(self):
                self.text = (
                    '[{"resource": "imx8mm-evk-sh11", "farm": "bsp", "status": "idle"}]'
                )

        mocker.patch(
            "subprocess.getstatusoutput",
            return_value=(
                0,
                "  acquired: fc/fc",
            ),
        )
        mocker.patch(
            "fc_client.client.Client.fetch_metadata",
            return_value={"fc": "foo", "lg": "bar"},
        )
        mocker.patch("requests.get", return_value=Output())
        mocker.patch(
            "fc_client.client.Client.communicate_with_server_sync",
            return_value={"rc": 0},
        )

        reserve_cmd = mocker.patch("subprocess.Popen", return_value=MagicMock())
        lock_cmd = mocker.patch("subprocess.call", return_value=MagicMock())
        Client.me = "/".join(
            (
                os.environ.get("LG_HOSTNAME", gethostname()),
                os.environ.get("LG_USERNAME", getuser()),
            )
        )
        Client.lock(Args)

        reserve_cmd.assert_called_with(
            ["labgrid-client", "reserve", "--wait", "name=imx8mm-evk-sh11"],
            stderr=-1,
            stdout=-1,
        )
        lock_cmd.assert_called_with(["labgrid-client", "-p", "imx8mm-evk-sh11", "lock"])

    def test_unlock(self, mocker):
        class Args:
            resource = "imx8mm-evk-sh11"

        mocker.patch(
            "fc_client.client.Client.fetch_metadata",
            return_value={"fc": "foo", "lg": "bar"},
        )

        mocker.patch("os.environ.get", return_value="test")
        mocker.patch(
            "subprocess.getstatusoutput",
            return_value=(
                0,
                """Place 'imx8mm-evk-sh11':
  matches:
    */imx8mm-evk-sh11/*
  acquired: test/test
  acquired resources:
  created: 2022-03-03 10:38:04.453874
  changed: 2023-03-28 16:17:05.881561
  reservation: AU7AKIDBHT
""",
            ),
        )
        mocker.patch(
            "subprocess.check_output",
            return_value="""Reservation 'AU7AKIDBHT':
  owner: test/test
  token: AU7AKIDBHT
  state: acquired
  filters:
    main: name=imx8mm-evk-sh11
  allocations:
    main: imx8mm-evk-sh11
  created: 2023-03-28 16:40:36.097286
  timeout: 2023-03-28 16:46:18.902555
""",
        )
        calls = [
            call(["labgrid-client", "cancel-reservation", "AU7AKIDBHT"]),
            call(["labgrid-client", "-p", "imx8mm-evk-sh11", "unlock"]),
        ]
        labgird_free = mocker.patch("subprocess.call", return_value=MagicMock())

        Client.me = "/".join(
            (
                os.environ.get("LG_HOSTNAME", gethostname()),
                os.environ.get("LG_USERNAME", getuser()),
            )
        )
        Client.unlock(Args)

        labgird_free.assert_has_calls(calls)
