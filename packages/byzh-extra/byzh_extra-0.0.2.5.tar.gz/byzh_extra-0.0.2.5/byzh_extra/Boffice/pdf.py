from pdf2image import convert_from_path
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from byzh_core import B_os

def b_pdf2img(pdf_path, output_dir, format='png', dpi=200, cpu_use:int = None):
    '''
    :param pdf_path:
    :param output_dir:
    :param format: png, jpg, ...
    :param dpi: 越高越清晰, 125够用
    :param cpu_use: 采用核心数(不指定则采用总核心的四分之一)
    :return:
    '''
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    pdf_name = pdf_path.stem
    if not pdf_path.is_file():
        print(f"路径 {pdf_path} 无法访问")
    os.makedirs(output_dir, exist_ok=True)

    cpu_count = os.cpu_count()
    if cpu_use is None:
        cpu_use = int(cpu_count / 4)
    print(f"[PDF to PNG] 当前CPU核心数{cpu_count}, 采用{cpu_use}个核心")
    print("[PDF to PNG] 正在处理数据中: ")
    images = convert_from_path(pdf_path, dpi=dpi, thread_count=cpu_use)

    def save_image(index, image):
        image.save(output_dir / f"{pdf_name}_{index + 1}.{format}", format.upper())

    with ThreadPoolExecutor() as executor:
        executor.map(save_image, range(len(images)), images)

    print(f"[PDF to PNG] {len(images)} 张 {format.upper()} 图片已保存至路径 {output_dir}")


def b_sort_pdf(file_path, out_path, order: list[int]):
    '''
    :param file_path:
    :param out_path:
    :param order: [1,5,4,3,2]
    :return:
    '''
    # 加载原始 PDF 文件
    reader = PdfReader(file_path)
    writer = PdfWriter()

    if len(order)!= len(reader.pages):
        raise ValueError(f"len(order)={len(order)} 与 len(PDF)={len(reader.pages)} 不匹配！")

    order = [i - 1 for i in order]

    # 添加页面到新 PDF 中
    for i in order:
        writer.add_page(reader.pages[i])

    # 保存到新文件
    B_os.makedirs(out_path)
    with open(out_path, "wb") as f:
        writer.write(f)

def b_sort_pdf1(file_path, out_path, order: list[int | tuple[int, int]]):
    '''
    :param file_path:
    :param out_path:
    :param order: [(1), (98, 118), (2, 97), (119, 168)] 或 [(1), (98, 118)]
    :return:
    '''
    reader = PdfReader(file_path)
    remain_order = [i+1 for i in range(len(reader.pages))]

    new_order = []
    for tu in order:
        if len(tu) == 1:
            num = tu[0]
            new_order.append(num)
            remain_order[num-1] = -1
        else:
            for num in range(tu[0], tu[1]+1):
                new_order.append(num)
                remain_order[num-1] = -1

    remain_order = [x for x in remain_order if x != -1]
    new_order.extend(remain_order)

    b_sort_pdf1(file_path, out_path, new_order)

def b_combine_pdf(file_path1, file_path2, out_path, order: list[list[int, int|tuple[int, int]]], remain_unmentioned=False):
    '''
    b_combine_pdf('input1.pdf', 'input2.pdf', out_path='output.pdf', order=[[2, (1, 4)], [1, 1], [2, (6, 103)]])
    :param file_path1: 1
    :param file_path2: 2
    :param out_path:
    :param order: [[1, (start, end)], ..., [2, (start, end)]]
    :return:
    '''
    reader1 = PdfReader(file_path1)
    remain_order1 = [i+1 for i in range(len(reader1.pages))]
    reader2 = PdfReader(file_path2)
    remain_order2 = [i+1 for i in range(len(reader2.pages))]

    new_order = []
    for index, tu in order:
        if isinstance(tu, int):
            new_order.append((index, tu))
        else:
            for num in range(tu[0], tu[1]+1):
                new_order.append((index, num))

    if remain_unmentioned:
        remain_order1 = [(1, x) for x in remain_order1 if x != -1]
        remain_order2 = [(2, x) for x in remain_order2 if x != -1]
        new_order.extend(remain_order1)
        new_order.extend(remain_order2)

    writer = PdfWriter()
    for element in new_order:
        if element[0] == 1:
            writer.add_page(reader1.pages[element[1]-1])
        if element[0] == 2:
            writer.add_page(reader2.pages[element[1]-1])

    # 保存到新文件
    B_os.makedirs(out_path)
    with open(out_path, "wb") as f:
        writer.write(f)


def b_combine_pdf1(file_path1, file_path2, out_path, order: list[list[int, int]], remain_unmentioned=False):
    '''
    从第1张开始，后续默认从上一次结尾的下一张开始
    b_combine_pdf1('input1.pdf', 'input2.pdf', out_path='output.pdf', order=[[2, 4], [1, 1], [2, 16]])
    :param file_path1: 1
    :param file_path2: 2
    :param out_path:
    :param order: [[1, (start, end)], ..., [2, (start, end)]]
    :return:
    '''
    a_start = 1
    b_start = 1
    new_order = []
    for index, num in order:
        if index == 1:
            new_order.append([index, (a_start, num)])
            a_start = num + 1
        elif index == 2:
            new_order.append([index, (b_start, num)])
            b_start = num + 1

    b_combine_pdf(file_path1, file_path2, out_path, new_order, remain_unmentioned)
