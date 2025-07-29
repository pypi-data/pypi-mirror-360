import ray
import re
import argparse
from pathlib import Path
from argparse import ArgumentParser, Namespace
from discord import Message, ChannelType, Embed, File, Intents, Client, Attachment
from abao_ai.shared_dir import SharedDir
from abao_ai.parser import DiscordArgumentParser
from abao_ai.flux import Flux
from abao_ai.info import get_devices


class DiscordBot(Client):
    def __init__(self) -> None:
        intents = Intents().all()
        Client.__init__(self, intents=intents)
        self.parser = DiscordArgumentParser()
        self.shared_dir = SharedDir(Path("/mnt/output"))
        self.engines_dir = Path("/mnt/engines")
        self.id = 0
        self.name = ""

    async def process_message(self, message: Message):
        if message.author.bot:
            return
        username = message.author.name
        print(message.content)
        cmd = re.sub(r"<@&?\d+>", "", message.content).strip()
        try:
            if len(message.attachments):
                for attachment in message.attachments:
                    continue
                    # await self.handle_attachment_upload_async(
                    #     attachment=attachment,
                    #     message=message,
                    #     user_id=username,
                    # )
            else:
                match message.channel.type:
                    case ChannelType.text:
                        if message.raw_mentions != [self.id]:
                            return
                        if not message.content.startswith(f"<@{self.id}>"):
                            return
                    case _:
                        return
                print(username, cmd)
                async with message.channel.typing():
                    args = self.parser.parse_cmd(cmd)
                    path = await generate.remote(args, self.shared_dir)
                    await message.reply(path.name, file=File(path))
        except argparse.ArgumentError as e:
            print(e)
            if e.message is not None and "error: None" not in e.message:
                await message.reply(content=e.message, silent=True)
            else:
                workflow = cmd.split(" ")[0] if cmd else ""
                await message.reply(content=self.parser.help(workflow), silent=True)
        except Exception as e:
            print(e)
            await message.reply(
                content=f"{e}",
                silent=True,
            )

    async def on_ready(self):
        assert self.user
        self.id = self.user.id
        self.name = self.user.name
        print(f"We have logged in as {self.name} {self.id}")
        self.parser.config_flux_parser()
        for intent in self.intents:
            print(intent)

    async def on_message_edit(self, before: Message, after: Message):
        await self.process_message(after)

    async def on_message(self, message: Message):
        await self.process_message(message)


@ray.remote(num_gpus=1, memory=32 * 1024**3)
def generate(args: Namespace, shared_dir: SharedDir) -> Path:
    sizes = args.ratio.split(":")
    width = int(sizes[0])
    height = int(sizes[1])
    prompt = " ".join(args.prompt)
    index = ray.get_gpu_ids()[0]
    device = get_devices()[0]
    engine_dir = Path("/mnt/engines") / device["name"] / f"{index}"
    precision = "fp4" if args.fp4 else "fp8" if args.fp8 else "bf16"
    flux = Flux(precision, False, engine_dir, "cuda")
    image = flux.generate(prompt=prompt, height=height, width=width, steps=50)
    path = shared_dir.save_image(image)
    return path
