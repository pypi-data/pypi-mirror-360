import copy
import ipaddress
import select
import socket
import struct
import threading
import time
from enum import IntEnum
from logging import getLogger
from typing import Callable, Optional

from .config import Eventgroup, SDService
from .constants import A_PROCESSING_TIME, FIND_TTL, MULTICAST_ADDRESS, MULTICAST_PORT
from .frame import SOMEIPFrame, SOMEIPMessageType, SOMEIPReturnCode, SOMEIPSDFrame

logger = getLogger(name="someip.client")


class SOMEIPClient:
    """SOME/IP client."""

    class TransportType(IntEnum):
        TCP = socket.IPPROTO_TCP
        UDP = socket.IPPROTO_UDP

    def __init__(
        self,
        target_address: str = "198.99.36.3",
        target_port: Optional[int] = None,
        local_bind_address: str = "",
        mcast_address: str = MULTICAST_ADDRESS,
        mcast_port: int = MULTICAST_PORT,
        transport_type: TransportType = TransportType.TCP,
    ):
        """Init SOME/IP client.

        Args:
            target_address (str): remote SOME/IP service address.
            target_port (int): remote SOME/IP service port.
            local_bind_address (str): local address that communicate to SOME/IP service.
            mcast_address (str): multicast dst ip address.
            mcast_port (int): multicast port.
            transport_type (SOMEIPClient.TransportType): Transport protocol.
        """
        self._target_address = target_address
        self._target_port = target_port
        self._local_bind_address = local_bind_address
        self._mcast_address = mcast_address
        self._mcast_port = mcast_port
        self._address_family = socket.AF_INET
        if self._target_address and isinstance(
            ipaddress.ip_address(self._target_address), ipaddress.IPv6Address
        ):
            self._address_family = socket.AF_INET6

        self._transport_type = transport_type
        self._mcast_udp_sock = None
        self._unicast_udp_sock = self._create_unicast_udp_sock(
            bind_port=self._mcast_port
        )
        self._sock = None
        self._session_counter = 0x0001
        self._subscribe_receiver = {}
        self._connect()

    def _connect(self):
        """start to establish socket communication"""
        if self._transport_type == SOMEIPClient.TransportType.TCP:
            self._sock = self._create_tcp_sock()
        elif self._transport_type == SOMEIPClient.TransportType.UDP:
            self._sock = self._create_unicast_udp_sock()

    def _create_tcp_sock(self):
        sock = socket.socket(self._address_family, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(A_PROCESSING_TIME)
        try:
            sock.connect((self._target_address, self._target_port))
        except socket.timeout as e:
            sock.close()
            sock = None
            raise socket.timeout(e)
        return sock

    def _create_unicast_udp_sock(self, bind_port: int = 0):
        sock = socket.socket(self._address_family, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(A_PROCESSING_TIME)
        sock.bind((self._local_bind_address, bind_port))
        return sock

    def _create_multicast_udp_sock(self):
        self._mcast_udp_sock = socket.socket(self._address_family, socket.SOCK_DGRAM)
        self._mcast_udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._mcast_udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._mcast_udp_sock.settimeout(A_PROCESSING_TIME)
        self._mcast_udp_sock.bind((self._mcast_address, self._mcast_port))
        mreq = struct.pack(
            "4s4s",
            socket.inet_aton(self._mcast_address),
            socket.inet_aton(self._local_bind_address),
        )
        self._mcast_udp_sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq
        )

    def find_service(
        self,
        service_id: int,
        instance_id: int,
        major_version: int = 1,
        minor_version: int = 0,
        ttl: int = FIND_TTL,
        timeout: float = 1.0,
    ) -> SOMEIPSDFrame:
        """Create a SD FindService entry for this service.

        Args:
            service_id (int): service id of the entry.
            instance_id (int): instance id of the entry, If it is set to 0xFFFF,
                               it means all service instances of a service.
            major_version (int): The major version of the service instance this event group belongs to.
            minor_version (int): The mino version of the service instance this event group belongs to.
            ttl (int): describe the life cycle of this Entry in seconds.
            timeout (float): socket receive timeout.
        """
        self._create_multicast_udp_sock()
        frame = SOMEIPSDFrame(
            session_id=self._session_counter,
            entries=[
                SDService(
                    service_id,
                    instance_id=instance_id,
                    major_version=major_version,
                    minor_version=minor_version,
                ).create_find_entry(ttl=ttl)
            ],
        )
        self._send(
            frame.encode(),
            sock=self._unicast_udp_sock,
            addr=(self._mcast_address, self._mcast_port),
        )
        start = time.time()
        while time.time() - start < timeout:
            try:
                offer_frame = SOMEIPSDFrame.decode(
                    self._recv(timeout=timeout, sock=self._mcast_udp_sock)
                )
                offer_sd_frame, _ = offer_frame.decode_sd(offer_frame.payload)
            except (TypeError, TimeoutError):
                continue

            if (
                offer_sd_frame.entries[0].service_id == service_id
                and offer_sd_frame.entries[0].instance_id == instance_id
            ):
                return offer_frame

        return None

    def subscribe(
        self,
        service_id: int,
        method_id: int,
        instance_id: int,
        eventgroup_id: int,
        major_version: int = 1,
        ttl: int = 3,
        timeout: float = 3.0,
        callback: Optional[Callable] = None,
    ):
        """
        subcribe a eventgroup.

        Args:
            service_id (int): service id of the entry.
            method_id (int): notify id of the interface.
            instance_id (int): instance id of the entry, If it is set to 0xFFFF,
                               it means all service instances of a service.
            eventgroup_id (int): event group id.
            major_version (int): The major version of the service instance this event group belongs to.
            ttl (int): describe the life cycle of this Entry in seconds.
            timeout (float): socket receive timeout.
            callback (funcion): callback funtion when receive server notification.

        Returns:
            int: the session id of the subcriber.
        """
        if self._session_counter > 0xFFFF:
            self._session_counter = 0x0001

        session_id = self._session_counter

        if self._transport_type == SOMEIPClient.TransportType.TCP:
            recv_sock = self._create_tcp_sock()
        elif self._transport_type == SOMEIPClient.TransportType.UDP:
            recv_sock = self._create_unicast_udp_sock()

        eventgroup = Eventgroup(
            service_id=service_id,
            instance_id=instance_id,
            eventgroup_id=eventgroup_id,
            major_version=major_version,
            sockname=recv_sock.getsockname(),
            protocol=self._transport_type,
        )

        frame = SOMEIPSDFrame(
            session_id=session_id,
            entries=(eventgroup.create_subscribe_entry(ttl=ttl),),
        )
        self._send(
            frame.encode(),
            sock=self._unicast_udp_sock,
            addr=(self._target_address, self._mcast_port),
        )
        subscribe_ack_frame = SOMEIPFrame.decode(
            self._recv(timeout=timeout, sock=self._unicast_udp_sock)
        )
        SOMEIPSDFrame.check_ack(subscribe_ack_frame.payload)

        loop = None

        self._subscribe_receiver[session_id] = {
            "socket": recv_sock,
            "eventgroup": eventgroup,
            "thread": loop,
            "running": True,
        }
        self._session_counter += 1
        if callback:

            def _loop():
                while self._subscribe_receiver[session_id]["running"]:
                    try:
                        response = self._recv(sock=recv_sock)
                        notify = SOMEIPFrame.decode(response)
                    except Exception:
                        pass
                    else:
                        if (
                            notify.service_id == service_id
                            and notify.method_id == method_id
                        ):
                            success_received = callback(notify)
                            if success_received:
                                break

            loop = threading.Thread(
                target=_loop,
                name=f"subscribe_{service_id}_{self._session_counter}",
            )
            loop.daemon = True
            loop.start()
            self._subscribe_receiver[session_id]["thread"] = loop
            return self._session_counter - 1
        else:
            start = time.time()
            while time.time() - start <= timeout:
                try:
                    response = self._recv(sock=recv_sock)
                    notify = SOMEIPFrame.decode(response)
                except Exception:
                    pass
                else:
                    if (
                        notify.service_id == service_id
                        and notify.method_id == method_id
                    ):
                        return notify

    def stop_subscribe(
        self,
        counter: int,
        ttl: int = 0,
    ):
        """
        stop to subscribe eventgroup.

        Args:
            counter (int): session id of the subsciber.
            ttl (int): describe the life cycle of this Entry in seconds.
        """
        frame = SOMEIPSDFrame(
            session_id=self._session_counter,
            entries=(
                self._subscribe_receiver[counter]["eventgroup"].create_subscribe_entry(
                    ttl=ttl
                ),
            ),
        )
        self._send(
            frame.encode(),
            sock=self._unicast_udp_sock,
            addr=(self._target_address, self._mcast_port),
        )
        self._session_counter += 1
        self._subscribe_receiver[counter]["running"] = False
        if (
            self._subscribe_receiver[counter]["thread"]
            and self._subscribe_receiver[counter]["thread"].is_alive()
        ):
            self._subscribe_receiver[counter]["thread"].join(A_PROCESSING_TIME + 1.0)

        self._subscribe_receiver[counter]["socket"].close()
        self._subscribe_receiver.pop(counter, None)

    def rr_method(
        self,
        service_id: int,
        method_id: int,
        client_id: int = 1,
        session_id: int = 1,
        protocol_version: int = 1,
        interface_version: int = 1,
        message_type: SOMEIPMessageType = SOMEIPMessageType.REQUEST,
        return_code: SOMEIPReturnCode = SOMEIPReturnCode.E_OK,
        payload: bytes = b"",
        timeout: float = 5.0,
    ) -> SOMEIPFrame:
        """
        Request/Response - R&R mode.
        """
        frame = SOMEIPFrame(
            service_id=service_id,
            method_id=method_id,
            client_id=client_id,
            session_id=session_id,
            protocol_version=protocol_version,
            interface_version=interface_version,
            message_type=message_type,
            return_code=return_code,
            payload=payload,
        )
        self._send(frame.encode())
        return SOMEIPFrame.decode(self._recv(timeout=timeout))

    def ff_method(
        self,
        service_id: int,
        method_id: int,
        client_id: int = 1,
        session_id: int = 1,
        protocol_version: int = 1,
        interface_version: int = 1,
        message_type: SOMEIPMessageType = SOMEIPMessageType.REQUEST_NO_RETURN,
        return_code: SOMEIPReturnCode = SOMEIPReturnCode.E_OK,
        payload: bytes = b"",
    ):
        """
        Fire & Forget request, no reply, F&F mode.
        """
        frame = SOMEIPFrame(
            service_id=service_id,
            method_id=method_id,
            client_id=client_id,
            session_id=session_id,
            protocol_version=protocol_version,
            interface_version=interface_version,
            message_type=message_type,
            return_code=return_code,
            payload=payload,
        )
        self._send(frame.encode())

    def field_getter(
        self,
        service_id: int,
        method_id: int,
        client_id: int = 1,
        session_id: int = 1,
        protocol_version: int = 1,
        interface_version: int = 1,
        message_type: SOMEIPMessageType = SOMEIPMessageType.REQUEST,
        return_code: SOMEIPReturnCode = SOMEIPReturnCode.E_OK,
        payload: bytes = b"",
        timeout: float = 5.0,
    ) -> SOMEIPFrame:
        """
        The getter of a field shall be a request/response call that has an empty payload in the request message
        and the value of the field in the payload of the response message.
        """
        return self.rr_method(
            service_id,
            method_id,
            client_id=client_id,
            session_id=session_id,
            protocol_version=protocol_version,
            interface_version=interface_version,
            message_type=message_type,
            return_code=return_code,
            payload=payload,
            timeout=timeout,
        )

    def field_setter(
        self,
        service_id: int,
        method_id: int,
        client_id: int = 1,
        session_id: int = 1,
        protocol_version: int = 1,
        interface_version: int = 1,
        message_type: SOMEIPMessageType = SOMEIPMessageType.REQUEST,
        return_code: SOMEIPReturnCode = SOMEIPReturnCode.E_OK,
        payload: bytes = b"",
        timeout: float = 5.0,
    ) -> SOMEIPFrame:
        """
        The setter of a field shall be a request/response call that has the desired value of the field in the
        payload of the request message and the value that was set to the field in the payload of the response message.
        """
        return self.rr_method(
            service_id,
            method_id,
            client_id=client_id,
            session_id=session_id,
            protocol_version=protocol_version,
            interface_version=interface_version,
            message_type=message_type,
            return_code=return_code,
            payload=payload,
            timeout=timeout,
        )

    def _send(self, frame, sock=None, addr=None):
        sock = sock or self._sock
        addr = addr or (self._target_address, self._target_port)
        remaining = len(frame)
        while remaining > 0:
            if sock.type == socket.SocketKind.SOCK_STREAM:
                remaining -= sock.send(frame[-remaining:])
            else:
                remaining -= sock.sendto(frame[-remaining:], addr)

    def _recv(self, timeout=A_PROCESSING_TIME, sock=None):
        sock = sock or self._sock
        data = bytes()

        r, _, _ = select.select([sock], [], [], timeout)

        if r:
            data = sock.recv(1024)
        else:
            logger.debug("error recv data, ---->socket timeout")

        if data:
            return data

        raise TimeoutError("SOME/IP server failed to respond in time")

    def close(self):
        """close socket"""
        receivers = copy.deepcopy(list(self._subscribe_receiver.keys()))
        for k in receivers:
            self.stop_subscribe(k)
        del receivers
        if self._sock:
            self._sock.close()
            self._sock = None
        if self._mcast_udp_sock:
            self._mcast_udp_sock.close()
            self._mcast_udp_sock = None
        if self._unicast_udp_sock:
            self._unicast_udp_sock.close()
            self._unicast_udp_sock = None
        self._session_counter = 0x0001

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
