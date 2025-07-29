# Copyright (c) 2023-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

import re
from functools import cached_property
from hashlib import sha256
from typing import TYPE_CHECKING, Literal, Protocol

from pyavd._eos_designs.schema import EosDesigns
from pyavd._errors import AristaAvdError, AristaAvdInvalidInputsError
from pyavd._utils import Undefined, UndefinedType, get_v2, short_esi_to_route_target

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import TypeVar

    from pyavd._eos_cli_config_gen.schema import EosCliConfigGen

    from . import AvdStructuredConfigConnectedEndpointsProtocol

    T_Ptp = TypeVar("T_Ptp", EosCliConfigGen.EthernetInterfacesItem.Ptp, EosCliConfigGen.PortChannelInterfacesItem.Ptp)
    T_Link_Tracking_Groups = TypeVar(
        "T_Link_Tracking_Groups", EosCliConfigGen.EthernetInterfacesItem.LinkTrackingGroups, EosCliConfigGen.PortChannelInterfacesItem.LinkTrackingGroups
    )
    T_Sflow = TypeVar("T_Sflow", EosCliConfigGen.EthernetInterfacesItem.Sflow, EosCliConfigGen.PortChannelInterfacesItem.Sflow)
    T_FlowTracker = TypeVar("T_FlowTracker", EosCliConfigGen.EthernetInterfacesItem.FlowTracker, EosCliConfigGen.PortChannelInterfacesItem.FlowTracker)
    T_StormControl = TypeVar("T_StormControl", EosCliConfigGen.EthernetInterfacesItem.StormControl, EosCliConfigGen.PortChannelInterfacesItem.StormControl)
    T_TrunkGroups = TypeVar(
        "T_TrunkGroups", EosCliConfigGen.EthernetInterfacesItem.Switchport.Trunk.Groups, EosCliConfigGen.PortChannelInterfacesItem.Switchport.Trunk.Groups
    )
    T_EvpnEthernetSegment = TypeVar(
        "T_EvpnEthernetSegment", EosCliConfigGen.EthernetInterfacesItem.EvpnEthernetSegment, EosCliConfigGen.PortChannelInterfacesItem.EvpnEthernetSegment
    )
    T_Phone = TypeVar("T_Phone", EosCliConfigGen.EthernetInterfacesItem.Switchport.Phone, EosCliConfigGen.PortChannelInterfacesItem.Switchport.Phone)


class UtilsMixin(Protocol):
    """
    Mixin Class with internal functions.

    Class should only be used as Mixin to a AvdStructuredConfig class or other Mixins.
    """

    @cached_property
    def _filtered_connected_endpoints(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
    ) -> EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpoints:
        """
        Return list of endpoints defined under one of the keys in "connected_endpoints_keys" which are connected to this switch.

        Adapters are filtered to contain only the ones connected to this switch.
        """
        connected_endpoints = self.shared_utils.all_connected_endpoints
        filtered_connected_endpoints = EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpoints()
        for connected_endpoints_key in connected_endpoints:
            for connected_endpoint in connected_endpoints_key.value:
                filtered_adapters = EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.Adapters()
                for adapter_index, adapter in enumerate(connected_endpoint.adapters):
                    adapter._internal_data.context = f"{connected_endpoints_key.key}[name={connected_endpoint.name}].adapters[{adapter_index}]"
                    adapter_settings = self.shared_utils.get_merged_adapter_settings(adapter)
                    if not adapter_settings.switches or self.shared_utils.hostname not in adapter_settings.switches:
                        continue

                    # Verify that length of all lists are the same
                    nodes_length = len(adapter_settings.switches)
                    endpoint_ports = adapter_settings.endpoint_ports
                    if len(adapter_settings.switch_ports) != nodes_length or (endpoint_ports and len(endpoint_ports) != nodes_length):
                        msg = (
                            f"Length of lists 'switches' ({len(adapter.switches)}), 'switch_ports' ({len(adapter.switch_ports)}), "
                            f"'endpoint_ports' ({len(endpoint_ports) or '-'}) (if used) did not match on adapter {adapter_index} on"
                            f" connected_endpoint '{connected_endpoint.name}' under '{connected_endpoints_key.key}'."
                            " Notice that some or all of these variables could be inherited from 'port_profiles'"
                        )
                        raise AristaAvdError(msg)

                    filtered_adapters.append(adapter_settings)

                if filtered_adapters:
                    # The object was deepcopied inside "get_merged_adapter_settings" so we can modify it here.
                    connected_endpoint.adapters = filtered_adapters
                    connected_endpoint._internal_data.type = connected_endpoints_key._internal_data.type
                    filtered_connected_endpoints.append(connected_endpoint)

        return filtered_connected_endpoints

    @cached_property
    def _filtered_network_ports(self: AvdStructuredConfigConnectedEndpointsProtocol) -> EosDesigns.NetworkPorts:
        """Return list of endpoints defined under "network_ports" which are connected to this switch."""
        filtered_network_ports = EosDesigns.NetworkPorts()
        for index, network_port in enumerate(self.inputs.network_ports):
            network_port._internal_data.context = f"network_ports[{index}]"
            network_port_settings = self.shared_utils.get_merged_adapter_settings(network_port)

            if not network_port_settings.switches and not network_port_settings.platforms:
                continue
            if network_port_settings.switches and not self._match_regexes(network_port_settings.switches, self.shared_utils.hostname):
                continue
            if network_port_settings.platforms and (
                not self.shared_utils.platform or not self._match_regexes(network_port_settings.platforms, self.shared_utils.platform)
            ):
                continue

            filtered_network_ports.append(network_port_settings)

        return filtered_network_ports

    def _match_regexes(self: AvdStructuredConfigConnectedEndpointsProtocol, regexes: Iterable[str], value: str) -> bool:
        """
        Match a list of regexes with the supplied value.

        Regex must match the full value to pass.
        """
        return any(re.fullmatch(regex, value) for regex in regexes)

    def _get_short_esi(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        channel_group_id: int,
        short_esi: str | None = None,
        hash_extra_value: str = "",
    ) -> str | None:
        """Return short_esi for one adapter."""
        if len(set(adapter.switches)) < 2 or not self.shared_utils.overlay_evpn or not (self.shared_utils.overlay_vtep or self.shared_utils.overlay_ler):
            # Only configure ESI for EVPN multi-homing.
            return None

        # short_esi is only set when called from sub-interface port-channels.
        if (short_esi is None) and (short_esi := adapter.ethernet_segment.short_esi) is None:
            return None

        endpoint_ports = adapter.endpoint_ports
        short_esi = str(short_esi)
        if short_esi.lower() == "auto":
            esi_hash = sha256(
                "".join(
                    [hash_extra_value, *adapter.switches[:2], *adapter.switch_ports[:2], *endpoint_ports[:2], str(channel_group_id)],
                ).encode("UTF-8"),
            ).hexdigest()
            short_esi = re.sub(r"([0-9a-f]{4})", "\\1:", esi_hash)[:14]

        if len(short_esi.split(":")) != 3:
            msg = f"Invalid 'short_esi': '{short_esi}' on connected endpoints adapter. Must be in the format xxxx:xxxx:xxxx"
            raise AristaAvdError(msg)

        return short_esi

    def _get_adapter_trunk_groups(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        connected_endpoint: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem,
        output_type: type[T_TrunkGroups],
    ) -> T_TrunkGroups | UndefinedType:
        """Return trunk_groups for one adapter."""
        if not self.inputs.enable_trunk_groups or adapter.mode not in ["trunk", "trunk phone"]:
            return Undefined

        if adapter._get("trunk_groups") is None:
            msg = f"'trunk_groups' for the connected_endpoint {connected_endpoint.name} is required."
            raise AristaAvdInvalidInputsError(msg)

        return output_type(adapter.trunk_groups)

    def _get_adapter_storm_control(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        output_type: type[T_StormControl],
    ) -> T_StormControl | UndefinedType:
        """Return storm_control for one adapter."""
        if self.shared_utils.platform_settings.feature_support.interface_storm_control and adapter.storm_control:
            return adapter.storm_control._cast_as(output_type)

        return Undefined

    def _get_adapter_evpn_ethernet_segment_cfg(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        short_esi: str | None,
        node_index: int,
        connected_endpoint: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem,
        output_type: type[T_EvpnEthernetSegment],
        default_df_algo: str | None = None,
        default_redundancy: Literal["all-active", "single-active"] | None = None,
    ) -> T_EvpnEthernetSegment | UndefinedType:
        """Return evpn_ethernet_segment_cfg for one adapter."""
        if short_esi is None:
            return Undefined

        evpn_ethernet_segment = output_type(
            identifier=f"{self.inputs.evpn_short_esi_prefix}{short_esi}",
            redundancy=adapter.ethernet_segment.redundancy or default_redundancy,
            route_target=short_esi_to_route_target(short_esi),
        )
        if (designated_forwarder_algorithm := adapter.ethernet_segment.designated_forwarder_algorithm or default_df_algo) is None:
            return evpn_ethernet_segment

        if designated_forwarder_algorithm == "modulus":
            evpn_ethernet_segment.designated_forwarder_election.algorithm = "modulus"

        elif designated_forwarder_algorithm == "auto":
            auto_preferences = range((len(adapter.switches) - 1) * 100, -1, -100)
            evpn_ethernet_segment.designated_forwarder_election._update(
                algorithm="preference",
                preference_value=auto_preferences[node_index],
                dont_preempt=adapter.ethernet_segment._get_defined_attr("dont_preempt"),
            )

        elif designated_forwarder_algorithm == "preference":
            # TODO: Add check for length of designated_forwarder_preferences
            designated_forwarder_preferences = get_v2(
                adapter.ethernet_segment,
                "designated_forwarder_preferences",
                required=True,
                custom_error_msg=f"ethernet_segment.designated_forwarder_preferences for the connected_endpoint {connected_endpoint.name}.",
            )
            evpn_ethernet_segment.designated_forwarder_election._update(
                algorithm="preference",
                preference_value=designated_forwarder_preferences[node_index],
                dont_preempt=adapter.ethernet_segment._get_defined_attr("dont_preempt"),
            )

        return evpn_ethernet_segment

    def _get_adapter_link_tracking_groups(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        output_type: type[T_Link_Tracking_Groups],
    ) -> T_Link_Tracking_Groups | UndefinedType:
        """Return link_tracking_groups for one adapter."""
        if self.shared_utils.link_tracking_groups is None or not adapter.link_tracking.enabled:
            return Undefined

        output = output_type()
        default_name = next(iter(self.shared_utils.link_tracking_groups)).name
        output.append_new(name=adapter.link_tracking.name or default_name, direction="downstream")
        return output

    def _get_adapter_ptp(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        output_type: type[T_Ptp],
    ) -> T_Ptp | UndefinedType:
        """Return ptp for one adapter."""
        if not adapter.ptp.enabled:
            return Undefined

        # Apply PTP profile config
        if (ptp_profile_name := adapter.ptp.profile or self.shared_utils.ptp_profile_name) is not None:
            if ptp_profile_name not in self.inputs.ptp_profiles:
                msg = f"PTP Profile '{ptp_profile_name}' referenced under {adapter._internal_data.context} does not exist in `ptp_profiles`."
                raise AristaAvdInvalidInputsError(msg)

            # Create a copy and removes the .profile attribute since the target model has a .profile key with a different schema.
            ptp_profile_config = self.inputs.ptp_profiles[ptp_profile_name]._deepcopy()
            delattr(ptp_profile_config, "profile")
            ptp_config = ptp_profile_config._cast_as(output_type, ignore_extra_keys=True)
        else:
            ptp_config = output_type()

        ptp_config.enable = True

        if adapter.ptp.endpoint_role not in ["dynamic", "bmca"]:
            ptp_config.role = "master"

        return ptp_config

    def _get_adapter_phone(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
        connected_endpoint: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem,
        output_type: type[T_Phone],
    ) -> T_Phone | UndefinedType:
        """Return phone settings for one adapter."""
        if not adapter.phone_vlan:
            return Undefined

        # Verify that "mode" is set to "trunk phone"
        if adapter.mode != "trunk phone":
            msg = f"Setting 'phone_vlan' requires 'mode: trunk phone' to be set on connected endpoint '{connected_endpoint.name}'."
            raise AristaAvdError(msg)

        # Verify that "vlans" is not set, since data vlan is picked up from 'native_vlan'.
        if adapter.vlans:
            msg = (
                "With 'phone_vlan' and 'mode: trunk phone' the data VLAN is set via 'native_vlan' instead of 'vlans'. Found 'vlans' on connected endpoint"
                f" '{connected_endpoint.name}'."
            )
            raise AristaAvdError(msg)

        return output_type(trunk=adapter.phone_trunk_mode, vlan=adapter.phone_vlan)

    def _get_adapter_l2_mtu(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
    ) -> int | None:
        """Return l2_mtu for one adapter."""
        if self.shared_utils.platform_settings.feature_support.per_interface_l2_mtu and adapter.l2_mtu:
            return adapter.l2_mtu

        return None

    def _get_adapter_l2_mru(
        self: AvdStructuredConfigConnectedEndpointsProtocol,
        adapter: EosDesigns._DynamicKeys.DynamicConnectedEndpointsItem.ConnectedEndpointsItem.AdaptersItem,
    ) -> int | None:
        """Return l2_mru for one adapter."""
        if self.shared_utils.platform_settings.feature_support.per_interface_l2_mru and adapter.l2_mru:
            return adapter.l2_mru

        return None
