import concurrent.futures
import os

import openai
from openai import OpenAI
import os
import shutil
import sys
import chardet
import random

key_list = ["sk-key1",
            "sk-key2",
            ]

completed_folders = []

def semantic_sort2(chapters):
    prompt = f"给定以下小说章节标题列表:\n{chapters}\n请按照合适的顺序对其进行排序,输出结果不包含引号逗号，用换行分隔,不要输出额外信息:\n"
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=random.choice(key_list),
    )
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return None
    sorted_chapters = response.choices[0].message.content.split('\n')
    # print(f"debug: sort result: {sorted_chapters}")
    return sorted_chapters

def semantic_sort(chapters):
    prompt = f"给定以下小说章节标题列表:\n{chapters}\n请按照合适的顺序对其进行排序,如果标题中含有序号优先按序号顺序排序,输出结果不包含引号逗号,禁止修改原标题的内容,用换行分隔,不要输出额外信息:\n"
    openai.api_key = random.choice(key_list)
    client = OpenAI(api_key=openai.api_key)
    try:
        response = client.completions.create(
            model="text-davinci-002",
            prompt=prompt,
            max_tokens=1024,
            stream=False,
            n=1,
            stop=None,
            temperature=0.5,
        )
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return None

    sorted_chapters = response.choices[0].text.strip().split('\n')
    # print(f"debug: sort result: {sorted_chapters}")
    return sorted_chapters

def concat_txt_in_dir(folder_path, output_dir):
    folder = os.path.basename(folder_path)
    if folder in completed_folders:
        print(f'Skipping completed folder {folder}')
        return

    print(f'Processing folder {folder}')
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    if not txt_files:
        print(f'No txt files found in {folder}')
        return

    for i in range(3):
        print(f'Attempt {i + 1} sorting files for {folder}')
        sorted_files = semantic_sort(txt_files)
        if sorted_files:
            break
    else:
        print(f'Skipping folder {folder} after 3 failed sorts')
        return

    output_path = os.path.join(output_dir, folder + '.txt')
    txt_path = ''
    try:
        for txt_file in sorted_files:
            txt_file = txt_file.replace("'", "")
            txt_path = os.path.join(folder_path, txt_file)
            with open(txt_path, 'rb') as input_file:
                raw = input_file.read(100)
                encoding = chardet.detect(raw)['encoding']
            try:
                with open(txt_path, 'r', encoding=encoding, errors='ignore') as input_file:
                    content = input_file.read()
            except UnicodeDecodeError:
                # Fallback to a default encoding (e.g., 'utf-8')
                print(f"encoding:{encoding} decode failed, try gb2312")
                encoding = 'GB2312'
                with open(txt_path, 'r', encoding=encoding) as input_file:
                    content = input_file.read()
            with open(output_path, 'a', encoding='utf-8', errors='ignore') as output_file:
                title = f'\n\n✦[{txt_file.replace(".txt", "")}]\n\n'
                output_file.write(title)
                output_file.write(content)

        completed_folders.append(folder)
        with open(progress_file, 'w', encoding='gbk') as f:
            f.write('\n'.join(completed_folders))
        print(f'Completed concatenation for {folder}')
    except Exception as e:
        print(f"File opeartion failed: {e}, filename:{folder}, txt_path: {txt_path}")

if __name__ == '__main__':
    # output dir
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # load progress
    progress_file = 'progress.txt'
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            completed_folders = f.read().splitlines()

    # input dirs
    input_dirs = ["G:\\tmp\\t1", "G:\\tmp\\t2"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for input_dir in input_dirs:
            print(f'Beginning process in {input_dir}')
            for folder in os.listdir(input_dir):
                folder_path = os.path.join(input_dir, folder)
                if not os.path.isdir(folder_path):
                    continue
                executor.submit(concat_txt_in_dir, folder_path, output_dir)