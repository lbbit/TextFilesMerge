#!/bin/bash

# 遍历当前目录下所有书名文件夹
for dir in */; do
  bookname=${dir%/}
  
  # 在每个书名文件夹下遍历所有章节
  for file in "$dir"*; do
    chapter=${file##*/}
    
     echo -e "\n\n✦$chapter\n\n" >> "$bookname.txt"

    
    # 将章节内容追加到结果文件
    cat "$file" >> "$bookname.txt"
  done
done