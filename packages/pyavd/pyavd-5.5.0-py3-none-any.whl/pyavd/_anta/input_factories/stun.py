# Copyright (c) 2023-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from ipaddress import ip_interface

from anta.input_models.stun import StunClientTranslation
from anta.tests.stun import VerifyStunClientTranslation

from pyavd._anta.logs import LogMessage
from pyavd.j2filters import natural_sort

from ._base_classes import AntaTestInputFactory


class VerifyStunClientTranslationInputFactory(AntaTestInputFactory):
    """
    Input factory class for the `VerifyStunClientTranslation` test.

    This factory generates test inputs for verifying STUN client translations.

    It collects the source IP address for each STUN client from `local_interfaces`
    of the dynamic path selection `path_groups` that have STUN `server_profiles` configured.

    The STUN clients use a source port of 4500 by default.
    """

    def create(self) -> list[VerifyStunClientTranslation.Input] | None:
        """Create a list of inputs for the `VerifyStunClientTranslation` test."""
        stun_clients = []

        for path_group in self.structured_config.router_path_selection.path_groups:
            # Check if the path group has local interfaces with STUN server profiles
            stun_interfaces = [local_interface.name for local_interface in path_group.local_interfaces if local_interface.stun.server_profiles]
            if not stun_interfaces:
                self.logger_adapter.debug(LogMessage.PATH_GROUP_NO_STUN_INTERFACE, path_group=path_group.name)
                continue

            for interface in stun_interfaces:
                # Get the source IP address for the STUN client
                ip_address = (
                    self.structured_config.ethernet_interfaces[interface].ip_address if interface in self.structured_config.ethernet_interfaces else None
                )
                if ip_address is None:
                    self.logger_adapter.debug(LogMessage.INTERFACE_NO_IP, interface=interface)
                    continue
                if ip_address == "dhcp":
                    self.logger_adapter.debug(LogMessage.INTERFACE_USING_DHCP, interface=interface)
                    continue

                source_address = ip_interface(ip_address).ip
                stun_clients.append(StunClientTranslation(source_address=source_address))

        return [VerifyStunClientTranslation.Input(stun_clients=natural_sort(stun_clients, sort_key="source_address"))] if stun_clients else None
