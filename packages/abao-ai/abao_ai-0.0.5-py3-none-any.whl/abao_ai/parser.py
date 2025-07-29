import os
from argparse import (
    Namespace,
    ArgumentError,
)
import argparse
from shlex import split
import io


class Parser:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="abao_ai",
            description="abao.ai discord bot",
        )
        parsers = parser.add_subparsers(title="action", dest="action")
        install_parser = parsers.add_parser("install", help="install models")
        install_parser.add_argument("model", choices=["flux"])
        install_parser.add_argument("--engines-dir", default="/mnt/engines")
        install_parser.add_argument(
            "--precision", default="bf16", choices=["bf16", "fp8", "fp4"]
        )
        install_parser.add_argument("--weight-streaming", default=False)
        discord_parser = parsers.add_parser("discord", help="start discord bot")
        discord_parser.add_argument(
            "--discord-token",
            default=os.getenv("DISCORD_TOKEN"),
        )
        discord_parser.add_argument("--shared-dir", default="/mnt/output")
        self.parser = parser

    def parse_args(self) -> Namespace:
        return self.parser.parse_args()


class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=""):
        raise ArgumentError(argument=None, message=str(message))


class DiscordArgumentParser:
    def __init__(self) -> None:
        self.parser = ArgumentParser(
            prog="@bot",
            description="abao.ai discord bot",
            exit_on_error=False,
        )
        self.parsers: dict[str, ArgumentParser] = {}
        self.sub_parsers = self.parser.add_subparsers(title="workflow", dest="workflow")

    def parse_cmd(self, content: str) -> Namespace:
        argv = split(content.strip(), posix=False)
        if len(argv) == 0:
            raise ArgumentError(None, self.help(""))
        args = self.parser.parse_args(argv)
        return args

    def help(self, workflow: str) -> str:
        help_msg = io.StringIO()
        self.parser.print_help(help_msg)
        if workflow not in self.parsers:
            self.parser.print_help(help_msg)
        else:
            parser = self.parsers[workflow]
            parser.print_help(help_msg)
        return f"{help_msg.getvalue()}"

    def config_flux_parser(self):
        flux_parser = self.sub_parsers.add_parser("flux")
        flux_parser.add_argument(
            "--ratio",
            type=str,
            default="720:1280",
            choices=["720:1280", "1280:720", "1024:1024"],
        )
        precision_group = flux_parser.add_mutually_exclusive_group()
        precision_group.add_argument(
            "--fp4",
            type=bool,
            default=False,
        )
        precision_group.add_argument(
            "--fp8",
            type=bool,
            default=False,
        )
        flux_parser.add_argument(
            "--steps",
            type=int,
            default=30,
        )
        flux_parser.add_argument(
            "--seed",
            type=int,
            default=0,
        )
        flux_parser.add_argument(
            "--guidance",
            type=float,
            default=0,
        )
        flux_parser.add_argument(
            "prompt",
            nargs="+",
        )
        self.parsers["flux"] = flux_parser
