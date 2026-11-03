# astrbot_plugin_dafeiyu_sticker

AstrBot 小插件：在文字回复后面按概率补一张本地文字贴纸，群聊里更像群友。

- `/表情包` 手动发一张
- 不再随机：模型在回复末尾写 `[fish:tag]`，插件把标记换成对应贴纸（标签表在 `main.py` 的 `TAGS`）

图片在 `stickers/` 下，直接替换同名 png 即可换图。
