"""大肥鱼表情包：按概率在文字回复后面补一张本地贴纸。"""

import random
from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

STICKERS = sorted((Path(__file__).parent / "stickers").glob("*.png"))

# shortcut: 概率写死在这里，不建配置项；想调就改这一行再重载插件
APPEND_PROBABILITY = 0.3


class DafeiyuSticker(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("表情包")
    async def sticker(self, event: AstrMessageEvent):
        if not STICKERS:
            return
        yield event.chain_result([Comp.Image.fromFileSystem(str(random.choice(STICKERS)))])

    @filter.on_decorating_result()
    async def decorate(self, event: AstrMessageEvent):
        chain = event.get_result().chain
        if not STICKERS or random.random() >= APPEND_PROBABILITY:
            return
        # 纯图片（含上面的命令）不追加，否则一条消息两张图
        if any(isinstance(c, Comp.Image) for c in chain):
            return
        if not any(isinstance(c, Comp.Plain) for c in chain):
            return
        chain.append(Comp.Image.fromFileSystem(str(random.choice(STICKERS))))
