#!/bin/bash 
#这一行是告诉系统用bash来运行这个脚本。

if ! command -v /opt/homebrew/bin/soffice &> /dev/null; then
  echo "❌ 未检测到 LibreOffice，请先运行 brew install libreoffice"
  exit 1
fi

TARGET="${1:-.}"
cd "$1" || exit 1
#切换到文件夹。如果切换失败直接退出

shopt -s nullglob
files=( *.pptx *.docx )

if [ ${#files[@]} -eq 0 ]; then
    echo "没有找到 pptx 或 docx 文件"
    exit 0
fi
echo "找到 ${#files[@]} 个文件，开始转换..."
/opt/homebrew/bin/soffice --headless --convert-to pdf "${files[@]}"
echo "转换完成，删除原文件..."
rm -f *.pptx *.docx
echo "✅ 全部完成"