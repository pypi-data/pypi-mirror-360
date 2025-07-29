import subprocess
import os
from pathlib import Path
from typing import Literal

CURRENT_DIR = Path(__file__).parent
PACKAGE_DIR = CURRENT_DIR.parent

FFMPEG_PATH = PACKAGE_DIR / 'bin/ffmpeg.exe'

def b_convert_video1(input_path: Path | str, output_path: Path | str):
    '''
    通过路径
    '''
    input_path, output_path = Path(input_path), Path(output_path)

    command = [
        FFMPEG_PATH,
        '-i', input_path,  # 输入文件
        '-c', 'copy',  # 拷贝编码，无需重新压缩（快）
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"转换成功：{output_path}")
    except subprocess.CalledProcessError as e:
        print("转换失败：", e)

def b_convert_video2(video_path: Path | str, format: Literal['mp4', 'avi', 'ts', ...]):
    '''
    通过指定后缀
    '''
    input_path= Path(video_path)
    output_path = os.path.splitext(input_path)[0] + f'.{format}'
    output_path = Path(output_path)

    command = [
        FFMPEG_PATH,
        '-i', input_path,  # 输入文件
        '-c', 'copy',  # 拷贝编码，无需重新压缩（快）
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"转换成功：{output_path}")
    except subprocess.CalledProcessError as e:
        print("转换失败：", e)

def b_convert_ts2mp4(input_path: Path | str, output_path: Path | str = None):
    if output_path is None:
        output_path = str(input_path).replace('.ts', '.mp4')
        output_path = Path(output_path)
    if not str(input_path).endswith('.ts'):
        raise ValueError("输入文件必须是 .ts 格式")

    b_convert_video1(input_path, output_path)


if __name__ == '__main__':
    # 示例
    b_convert_ts2mp4('./awaaa/21.ts')
