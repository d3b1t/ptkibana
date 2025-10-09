"""
Kibana role enumeration module

This module enumerates available Kibana roles through the /api/security/role endpoint

Contains:
- RoleEnum to perform the availability test
- run() function as an entry point for running the test
"""

from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent
from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Kibana role enumeration"


class RoleEnum:
    """
    This class enumerates available Kibana roles
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _print_roles(self, roles: dict) -> None:
        """
        This method parses the roles JSON object, prints the found roles and adds them to the JSON output
        """

        for role in roles:
            role_name = role.get("name", "None")
            ptprint(f"Found role: {role_name}", "INFO", not self.args.json, indent=4)
            role_node = self.ptjsonlib.create_node_object("kbnRole", properties={"name": role_name})
            self.ptjsonlib.add_node(role_node)


    def run(self) -> None:
        """
        This method executes the Kibana role enumeration

        Send an HTTP GET request to the /api/security/role endpoint. If the response is not HTTP 200 OK, the methods exits.
        Otherwise, the method passes the received JSON object to the _print_roles() method
        """

        response = self.http_client.send_request(url=self.args.url+"api/security/role", method="GET", headers=self.args.headers)

        if response.status_code != HTTPStatus.OK or (type(response.json()) != list and response.json().get("status", 200) != HTTPStatus.OK):
            ptprint("Could not fetch roles", "OK", not self.args.json, indent=4)
            ptprint(f"Details: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return

        roles = response.json()

        self._print_roles(roles)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the RoleEnum test"""
    RoleEnum(args, ptjsonlib, helpers, http_client, base_response).run()
