import json

import click

from someip_py import SOMEIPService, __version__


@click.version_option(version=__version__)
@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def main():
    pass


@main.command(name="decode")
@click.option("-p", "--platform", help="the project platform", default="V2x")
@click.option("-i", "--idl", help="someip service matrix path", default=None)
@click.option("-s", "--service_id", help="service id", required=True)
@click.option("-m", "--method_id", help="method id", required=True)
@click.option("-t", "--message_type", type=int, help="method id", default=2)
@click.option("-P", "--payload", help="method id", required=True)
def decode(platform, idl, service_id, method_id, message_type, payload):
    """decode some/ip message"""
    s = SOMEIPService(platform=platform, arxml_path=idl)
    click.echo(
        click.style(
            json.dumps(
                s.decode_payload(
                    service_id, method_id, message_type=message_type, payload=payload
                ),
                indent=4,
            ),
            fg="cyan",
            bold=True,
        )
    )


@main.command(name="parse")
@click.option("-p", "--platform", help="the project platform", default="V2x")
@click.option("-i", "--idl", help="someip service matrix path", default=None)
@click.option("-f", "--file", help="pcap file path", required=True)
@click.option("-o", "--output", help="output dir", default=None)
def parse(platform, idl, file, output):
    """parse pcap"""
    s = SOMEIPService(platform=platform, arxml_path=idl)
    s.parse_pcap(file, output=output)
