#!/usr/bin/python3
"""
Copyright (c) 2024 Penterep Security s.r.o.

ptkibana is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptkibana is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptkibana.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import sys;
from difflib import IS_LINE_JUNK

sys.path.append(__file__.rsplit("/", 1)[0])

from _version import __version__
from ptlibs import ptjsonlib, ptprinthelper, ptmisclib, ptnethelper
from ptlibs.ptprinthelper import ptprint
from ptlibs.http.http_client import HttpClient
from helpers.helpers import Helpers
import requests
from modules._is_kibana import IsKibana

class PtKibana:
    def __init__(self, args):
        self.ptjsonlib = ptjsonlib.PtJsonLib()
        self.args = args
        self.http_client = HttpClient(args=self.args, ptjsonlib=self.ptjsonlib)
        self.helpers = Helpers(args=self.args, ptjsonlib=self.ptjsonlib, http_client=self.http_client)


    def _check_if_target_runs_kibana(self) -> None:
        """
        Executes the IS_KIBANA pre-check to determine if the target is running Kibana.

        This method:
        - Instantiates the `_IS_KIBANA` module
        - Calls its `run()` method
        - If the module determines that Kibana is NOT running,
        it calls `ptjsonlib.end_error()` internally and terminates the program.

        Notes:
            The `_IS_KIBANA` module is responsible for handling the error state
            and ending execution if the target does not appear to run Kibana.
        """
        IsKibana(
            args=self.args,
            ptjsonlib=self.ptjsonlib,
            helpers=self.helpers,
            http_client=self.http_client,
            base_response=self.base_response
        ).run()

    def _fetch_initial_response(self) -> None:
        """
        Sends initial HTTP requests to the requested URL. Follows redirects
        If a non-200 status code is returned, the script exits early.
        """

        try:
            # Send request to user specified page via <args.url>
            self.base_response = self.http_client.send_request(url=self.args.url, method="GET", headers=self.args.headers, allow_redirects=True)

            """
            if 300 <= self.base_response.status_code < 400:
                if not self._check_https():
                    self.ptjsonlib.end_error(f"Redirect to URL: {self.base_response.headers.get('Location', 'unknown')}", self.args.json)
            """
            if self.base_response.status_code != 200:
                self.ptjsonlib.end_error(f"Webpage returns status code: {self.base_response.status_code}", self.args.json)

        except requests.exceptions.RequestException as error_msg:
            self.ptjsonlib.end_error(f"Error retrieving initial responses:", details=error_msg, condition=self.args.json)


    def run(self) -> None:
        """Main method"""

        self._fetch_initial_response()
        self._check_if_target_runs_kibana()

        self.ptjsonlib.set_status("finished")
        ptprint(self.ptjsonlib.get_result_json(), "", self.args.json)


def get_help():
    return [
        {"description": [""]},
        {"usage": ["ptkibana <options>"]},
        {"usage_example": [
            "ptkibana -u https://www.example.com",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",            "Connect to URL"],
            ["-p",  "--proxy",                  "<proxy>",          "Set proxy (e.g. http://127.0.0.1:8080)"],
            ["-T",  "--timeout",                "",                 "Set timeout (default 10)"],
            ["-c",  "--cookie",                 "<cookie>",         "Set cookie"],
            ["-a",  "--user-agent",             "<a>",              "Set User-Agent header"],
            ["-H",  "--headers",                "<header:value>",   "Set custom header(s)"],
            ["-r",  "--redirects",              "",                 "Follow redirects (default False)"],
            ["-C",  "--cache",                  "",                 "Cache HTTP communication (load from tmp in future)"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                 "Output in JSON format"],
        ]
        }]


def parse_args():
    parser = argparse.ArgumentParser(add_help="False", description=f"{SCRIPTNAME} <options>")
    parser.add_argument("-u",  "--url",            type=str, required=True)
    parser.add_argument("-p",  "--proxy",          type=str)
    parser.add_argument("-T",  "--timeout",        type=int, default=10)
    parser.add_argument("-a",  "--user-agent",     type=str, default="Penterep Tools")
    parser.add_argument("-c",  "--cookie",         type=str)
    parser.add_argument("-H",  "--headers",        type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-r",  "--redirects",      action="store_true")
    parser.add_argument("-C",  "--cache",          action="store_true")
    parser.add_argument("-j",  "--json",           action="store_true")
    parser.add_argument("-v",  "--version",        action='version', version=f'{SCRIPTNAME} {__version__}')
    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()

    if args.proxy:
        args.proxy = {"http": args.proxy, "https": args.proxy}

    args.headers = ptnethelper.get_request_headers(args)

    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptkibana"
    args = parse_args()
    script = PtKibana(args)
    script.run()


if __name__ == "__main__":
    main()
