# Anki 卡片样式与模板

Anki 笔记类型的 **样式 (Styling CSS)** 和 **卡片模板 (front/back HTML)** 的导出快照，
用 `export_from_anki.py` 从本地 `collection.anki2` 数据库导出。

## 为什么放在这个仓库

浏览器端的用户脚本在另一个仓库 [tampermonkey-scripts](https://github.com/PluviaLiu/tampermonkey-scripts)，
Anki 样式属于本地配置，所以放在 local-scripts 下。

## 目录结构

```
notetypes/
  <笔记类型名>/
    styling.css                    # 样式 (Anki 模板管理器里的「样式」栏)
    <序号>-<卡片模板名>.front.html  # 正面模板
    <序号>-<卡片模板名>.back.html   # 背面模板
```

主要内容：

- **Class_ielts** — 雅思词汇卡，自定义最多（两栏布局、打字反馈、深色模式校准等改动都在这里）
- **C2E** — 早期版单词卡
- **问答题 / 填空题 / 图片遮盖** — 基础样式；四个「问答题」变体的 CSS 相同，区别在卡片模板数量

## 更新流程

在 Anki 里改完样式后：

```bash
python3 anki/export_from_anki.py   # Anki 开着也没关系，脚本读的是副本
git add anki/ && git commit -m "更新 Anki 样式导出"
```

## 恢复方法（手动贴回）

仓库里的文件**不会自动同步回 Anki**。要恢复时打开
Anki → 工具 → 管理笔记类型 → 选中对应类型 → 卡片 / 字段：
把 `styling.css` 贴到「样式」，front/back.html 分别贴到模板的正面/背面。

导出日期：2026-10-12
