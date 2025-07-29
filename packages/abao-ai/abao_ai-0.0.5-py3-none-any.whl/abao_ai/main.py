import ray
import os
from abao_ai.parser import Parser
from abao_ai.discord_bot import DiscordBot
from abao_ai.info import print_info
from abao_ai.install import install
from pathlib import Path


def main():
    parser = Parser()
    args = parser.parse_args()
    match args.action:
        case "discord":
            discord = DiscordBot()
            discord.run(args.discord_token)
        case "install":
            install(
                args.model,
                args.engines_dir,
                args.precision,
                args.weight_streaming,
            )
        case _:
            print_info()


if __name__ == "__main__":
    ray.init()
    bot = DiscordBot()
    bot.run(os.getenv("DISCORD_TOKEN", ""))

    # jobs = [generate.remote() for _ in range(4)]
    # ray.get(jobs)
    # # generate_()
