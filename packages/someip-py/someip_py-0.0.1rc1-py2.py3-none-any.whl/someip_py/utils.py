import argparse
import datetime
import decimal
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
import traceback
from logging import getLogger

logger = getLogger("someip.utils")


def get_protoc() -> str:
    base_dir = os.path.dirname(__file__)
    system = platform.system()
    if system == "Windows":
        protoc = os.path.join(
            base_dir, "service_interface", "protoc", "windows", "bin", "protoc.exe"
        )
    elif system in ("Linux", "Linux2"):
        protoc = os.path.join(
            base_dir, "service_interface", "protoc", "linux", "bin", "protoc"
        )
    else:
        raise NotImplementedError("protoc only support Linux and Windows")

    return protoc


def convert_proto(proto_path: str) -> None:
    protoc = get_protoc()
    pb = os.path.join(os.path.dirname(__file__), "service_interface", "pb")
    if os.path.exists(pb):
        shutil.rmtree(pb)
    os.mkdir(pb)

    system = platform.system()
    shell = True
    if system == "Windows":
        shell = False

    cmd = f"{protoc} -I={proto_path} --python_out={pb} {os.path.join(proto_path, '*.proto')}"
    subprocess.run(cmd, shell=shell)


def import_class(import_str: str):
    """Returns a class from a string including module and class.

    Args:
        import_str (str): ModulePath:ModuleClass.

    Returns:
        class: the class from the import_str.

    example::
        >>> from importutils import import_class
        >>> import_class('xxx.lib.bus.plugins.socketcanwrap:SocketcanBusWrapper')

    """
    mod_str, _, class_str = import_str.rpartition(":")
    try:
        import importlib

        try:
            module = importlib.import_module(mod_str)
            return getattr(module, class_str)
        except ModuleNotFoundError:
            raise ImportError(
                "Class %s cannot be found (%s)"
                % (class_str, traceback.format_exception(*sys.exc_info()))
            )
    except ImportError:
        __import__(mod_str)
        try:
            return getattr(sys.modules[mod_str], class_str)
        except AttributeError:
            raise ImportError(
                "Class %s cannot be found (%s)"
                % (class_str, traceback.format_exception(*sys.exc_info()))
            )


def import_object(import_str: str, *args, **kwargs):
    """Import a class and return an instance of it."""
    return import_class(import_str)(*args, **kwargs)


class JsonEncoderWrapper(json.JSONEncoder):
    """Support Json serialize with object/bytes/bytearray/datetime/decimal"""

    def default(self, o):
        if isinstance(o, object):
            if hasattr(o, "_json_object"):
                return o.__dict__
            elif hasattr(o, "_json_array"):
                return [self.default(d) for d in o.data]
            elif hasattr(o, "_json_number"):
                return o.value
            else:
                return str(o)
        elif isinstance(o, bytes):
            return o.decode()
        elif isinstance(o, bytearray):
            return list(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, decimal.Decimal):
            return float(o)

        return super(JsonEncoderWrapper, self).default(o)


def hex2int(v) -> int:
    if isinstance(v, int):
        return v
    elif isinstance(v, str):
        try:
            return int(v, base=16)
        except ValueError:
            raise ValueError("value type must be hex string")


def str2bool(v) -> bool:
    if isinstance(v, bool):
        return v

    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def type2bytes(v, fmt="!B") -> bytes:
    if v is not None:
        if isinstance(v, bytes):
            return v
        elif isinstance(v, int):
            return struct.pack(fmt, v)
        elif isinstance(v, list):
            return bytes(v)
        elif isinstance(v, str):
            try:
                return struct.pack(fmt, int(v))
            except (ValueError, struct.error):
                return bytes.fromhex(v)
        else:
            raise ValueError("value type must be str or int or list")
    else:
        return bytes()
