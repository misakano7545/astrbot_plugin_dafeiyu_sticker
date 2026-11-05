"""大肥鱼表情包：由模型按语境挑贴纸，而不是随机补一张。"""

import random
import re
from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

STICKER_DIR = Path(__file__).parent / "stickers"

# 标签 -> 什么语境该发哪张。模型照这张表挑，改这里就能改选图逻辑。
# 刻意不放：yupian（求资源）、kaidian（萝莉控）、dsh（大烧货）——QQ 审核会拦。
TAGS = {
    "big_blue_fat_fish": "被批评、摆烂、白吃白喝还理直气壮",
    "fat_fish": "吃饱了、很满足、求摸肚子",
    "dead_fish": "累死、宕机、当场去世",
    "deepsleep": "困了、道晚安",
    "big_coming": "有大新闻、预告要爆料",
    "dadeyaolaile": "准备放猛料、下猛药",
    "curse": "别人在抱怨某人，你提议直接骂",
    "hajimi": "对方闹脾气，你傲娇地哄",
    "ojj": "委屈、沮丧、蔫了",
    "keai": "单纯卖萌、无话可说",
    "ojingjing": "夸赞、厉害了",
    "mama": "讨要 token、讨要东西",
    "no-money": "有人嫌贵、嫌烧 token，怼回去",
    "unvaluable": "被问有啥用、自嘲只会聊天",
    "evaluable": "被问有啥用、居高临下地说先养着",
    "more_modal": "聊多模态、能看不能看",
    "go_to_agi": "聊开源、技术信仰",
    "update": "催更新、被催更新",
    "virus": "赛博浪漫被当成病毒",
    "push": "被安排一堆活、压力大",
    "push_one_fat_fish": "被拿难题刁难（黎曼猜想之类）",
}

# 半角/全角括号都认，模型手滑也不至于把标记漏到聊天里
# 裸写 [fat_fish] 也算：模型看词表会照抄 - fat_fish 的样子，忘了加 fish: 前缀
MARK = re.compile(r"[\[［<](?:fish[:：])?([a-z_\-]+)[\]］>]")

HINT = "\n\n【配图】想配一张贴纸时，在回复最末尾写一个标记，如 [fish:dead_fish]。系统会把它换成图。一条回复最多一个，不确定就不写。可选：\n"


class DafeiyuSticker(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("表情包")
    async def sticker(self, event: AstrMessageEvent):
        files = sorted(STICKER_DIR.glob("*.png"))
        if files:
            yield event.chain_result(
                [Comp.Image.fromFileSystem(str(random.choice(files)))]
            )

    @filter.on_llm_request()
    async def teach_tags(self, event: AstrMessageEvent, req):
        req.system_prompt = (req.system_prompt or "") + HINT + "\n".join(
            f"- [fish:{k}]：{v}" for k, v in TAGS.items()
        )

    @filter.on_decorating_result()
    async def decorate(self, event: AstrMessageEvent):
        chain = event.get_result().chain
        tag = None
        for comp in chain:
            if not isinstance(comp, Comp.Plain):
                continue
            m = MARK.search(comp.text)
            if m:
                comp.text = MARK.sub("", comp.text).rstrip()
                tag = m.group(1) if m.group(1) in TAGS else None
                break
        if tag:
            path = STICKER_DIR / f"{tag}.png"
            if path.exists():
                chain.append(Comp.Image.fromFileSystem(str(path)))
