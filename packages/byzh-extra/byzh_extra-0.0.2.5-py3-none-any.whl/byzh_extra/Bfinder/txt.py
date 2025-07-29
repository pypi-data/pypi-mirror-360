import os
def b_str_in_file(file_path, string, encoding='utf-8'):
    indexes = []
    with open(file_path, 'r', encoding=encoding) as f:
        for index, line in enumerate(f):
            if string in line:
                indexes.append(index + 1)
    if len(indexes) == 0:
        return False
    else:
        return indexes

def b_str_in_dir(dir_path, string, console_log=True, include_ext=['py', 'txt'], encoding='utf-8'):
    '''
    找到文件夹内的指定后缀的文件中是否包含指定字符串，并返回包含该字符串的行号
    :param dir_path:
    :param string:
    :param include_ext:
    :param encoding:
    :return: list[[行号, 文件路径], ...]
    '''
    file_paths = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not file.split('.')[-1] in include_ext:
                continue
            file_path = os.path.join(root, file)
            indexes = b_str_in_file(file_path, string, encoding)
            if indexes:
                file_paths.append([indexes, file_path])

    if console_log:
        for x in file_paths:
            print(x)
    return file_paths

if __name__ == '__main__':
    lst = b_str_in_dir(r'E:\byzh_workingplace\byzh-rc-to-pypi\uploadToPypi_extra', 'Bos')
    for i in lst:
        print(i)