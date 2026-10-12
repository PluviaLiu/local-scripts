#!/usr/bin/env python3
"""从 Anki 的 collection.anki2 导出所有笔记类型的样式和模板。

用法: python3 export_from_anki.py [Anki profile 目录]
默认读 ~/Library/Application Support/Anki2/账户 1/
输出到本脚本所在目录的 notetypes/ 下，每个笔记类型一个文件夹:
  <名称>/styling.css
  <名称>/<序号>-<卡片模板名>.front.html
  <名称>/<序号>-<卡片模板名>.back.html

说明: Anki 运行时数据库是锁定的，脚本会先复制到临时文件再读，不影响 Anki。
注意: 这是单向快照——改这里的文件不会同步回 Anki，需要手动贴回模板管理器。
"""

import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

DEFAULT_DIR = Path.home() / "Library/Application Support/Anki2/账户 1"
OUT_DIR = Path(__file__).resolve().parent / "notetypes"


def varint(buf, i):
    r = s = 0
    while True:
        b = buf[i]
        i += 1
        r |= (b & 0x7F) << s
        if not b & 0x80:
            return r, i
        s += 7


def fields(buf):
    """解析 protobuf wire format，产出 (字段号, wire type, 值)。"""
    i = 0
    while i < len(buf):
        key, i = varint(buf, i)
        fn, wt = key >> 3, key & 7
        if wt == 0:
            v, i = varint(buf, i)
            yield fn, wt, v
        elif wt == 2:
            ln, i = varint(buf, i)
            yield fn, wt, buf[i : i + ln]
            i += ln
        else:
            raise ValueError(f"意外的 wire type {wt}（字段 {fn}），可能是 zstd 压缩格式，需换 anki 库解析")


def safe(name):
    return re.sub(r"[/\\:*?\"<>|]", "_", name).strip() or "_"


def main():
    profile = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    src = profile / "collection.anki2"
    if not src.exists():
        sys.exit(f"找不到 {src}")

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "copy.anki2"
        shutil.copy2(src, db)
        for suffix in ("-wal", "-shm"):
            extra = profile / f"collection.anki2{suffix}"
            if extra.exists():
                shutil.copy2(extra, Path(td) / f"copy.anki2{suffix}")
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        notetypes = list(con.execute("SELECT id, name, config FROM notetypes"))
        templates = {}
        for ntid, ord_, tname, cfg in con.execute(
            "SELECT ntid, ord, name, config FROM templates"
        ):
            templates.setdefault(ntid, []).append((ord_, tname, cfg))
        con.close()

    OUT_DIR.mkdir(exist_ok=True)
    for nid, name, cfg in notetypes:
        css = None
        for fn, wt, v in fields(cfg):
            if fn == 3 and wt == 2:  # notetype config: 字段 3 = styling css
                css = v.decode("utf-8")
        folder = OUT_DIR / safe(name)
        folder.mkdir(exist_ok=True)
        (folder / "styling.css").write_text(css or "", encoding="utf-8")
        for ord_, tname, tcfg in sorted(templates.get(nid, [])):
            front = back = ""
            for fn, wt, v in fields(tcfg):
                if wt == 2 and fn == 1:  # template config: 字段 1 = front
                    front = v.decode("utf-8")
                elif wt == 2 and fn == 2:  # 字段 2 = back
                    back = v.decode("utf-8")
            base = f"{ord_:02d}-{safe(tname)}"
            (folder / f"{base}.front.html").write_text(front, encoding="utf-8")
            (folder / f"{base}.back.html").write_text(back, encoding="utf-8")
        n_cards = len(templates.get(nid, []))
        print(f"{name}: {len(css or '')} 字符 CSS, {n_cards} 个卡片模板")

    print(f"\n已导出到 {OUT_DIR}")


if __name__ == "__main__":
    main()
