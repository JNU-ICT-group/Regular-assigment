import os
import csv
import numpy as np
from byteSourceCoder import encode, decode, compare_file
import calcCodecInfo


# 测试模块
def test_once(pmf_file_name, source_file_name, encoded_file_name, decoded_file_name):
    print('Encoding...')
    (source_len, encoded_len) = encode(pmf_file_name, source_file_name, encoded_file_name)
    print(' source len:', source_len)  # 打印源数据长度
    print('encoded len:', encoded_len)  # 打印编码后的数据长度
    print('     ratio :', (source_len / encoded_len if encoded_len else np.nan))  # 打印压缩比
    print('')

    print('Decoding...')
    (encoded_len, decoded_len) = decode(encoded_file_name, decoded_file_name)  # 执行解码
    print('encoded len:', encoded_len)  # 打印编码数据长度
    print('decoded len:', decoded_len)  # 打印解码数据长度
    print('')

    print('Comparing source and decoded...')
    diff_total = compare_file(source_file_name, decoded_file_name)  # 比较源文件和解码后的文件
    print('')
    return diff_total


def read_header_size(path):
    with open(path, 'rb') as f:
        return int.from_bytes(f.read(2), 'little')


class NAMESPACE:
    test_data_dir: str='.'
    pmf_file_name: str
    source_file_name: str
    encoded_file_name: str
    decoded_file_name: str
    csv_file_name: str


def requal(a, b, n=7):
    return round(abs(a-b), n) == 0.


def test_flow():
    namespace = NAMESPACE()
    # 设置测试数据目录和文件路径
    namespace.test_data_dir = '..\\data'
    namespace.pmf_file_name = os.path.join(namespace.test_data_dir, 'pmf.csv')
    namespace.source_file_name = os.path.join(namespace.test_data_dir, 'source.dat')
    namespace.encoded_file_name = os.path.join(namespace.test_data_dir, '_encoded.tmp')
    namespace.decoded_file_name = os.path.join(namespace.test_data_dir, '_decoded.tmp')
    namespace.csv_file_name = os.path.join(namespace.test_data_dir, '_output.csv')

    # 确保测试数据目录存在
    if not os.path.exists(namespace.test_data_dir):
        os.makedirs(namespace.test_data_dir)
    def test_uniform_distribution(self):
        # 生成测试源文件（模拟数据）
        data = np.random.randint(0, 256, size=64 * 1024, dtype=np.uint8)
        data.tofile(self.source_file_name)

        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, round(1 / 256.0, 6)) for i in range(256)]  # 使用均匀分布的概率
        with open(self.pmf_file_name, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONE)
            writer.writerows(pmf_data)
        # 测试源文件和解码文件的比较
        diff_total = test_once(self.pmf_file_name, self.source_file_name, self.encoded_file_name, self.decoded_file_name)
        calcCodecInfo.work_flow(self.source_file_name, self.encoded_file_name, self.csv_file_name,
                                header_size=read_header_size(self.encoded_file_name))
        with open(self.csv_file_name) as f:
            result = f.read().strip()
            result = tuple(map(lambda s: s.strip('"'), result.split('\n')[-1].split(',')))
            print(result)  # 打印实际结果以便调试
            assert (result[0] == self.source_file_name)
            assert (result[1]==self.encoded_file_name)
            assert requal(float(result[2]),1.0, 3)
            assert requal(float(result[3]),8.0, 3)
            assert requal(float(result[4]),0.0, 3)
            assert requal(float(result[5]),8.0, 2)
            assert requal(float(result[6]),8.0, 2)
        assert diff_total==0, "源文件和解码文件应完全相同"

    def test_empty_file(self):
        open(self.source_file_name, 'wb').close()
        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, 0.0) for i in range(256)]  # 使用均匀分布的概率
        with open(self.pmf_file_name, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONE)
            writer.writerows(pmf_data)
        # 测试源文件和解码文件的比较
        diff_total = test_once(self.pmf_file_name, self.source_file_name, self.encoded_file_name, self.decoded_file_name)
        calcCodecInfo.work_flow(self.source_file_name, self.encoded_file_name, self.csv_file_name,
                                header_size=0)
        with open(self.csv_file_name) as f:
            result = f.read().strip()
            result = tuple(map(lambda s: s.strip('"'), result.split('\n')[-1].split(',')))
            print(result)  # 打印实际结果以便调试
            assert (result[0] == self.source_file_name)
            assert (result[1]==self.encoded_file_name)
            assert requal(float(result[2]),1.0, 3)
            assert requal(float(result[3]),8.0, 3)
            assert requal(float(result[4]),0.0, 3)
            assert result[5]=='nan'
            assert result[6]=='nan'
        assert diff_total==0, "源文件和解码文件应完全相同"

    def test_unmapped_distribution(self):
        # 生成测试源文件（模拟数据）
        data = np.random.randint(0, 256, size=64 * 1024, dtype=np.uint8)
        data.tofile(self.source_file_name)

        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, round(i / 256.0, 6)) for i in range(256)]  # 使用分布不匹配的概率
        with open(self.pmf_file_name, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONE)
            writer.writerows(pmf_data)
        # 测试源文件和解码文件的比较
        diff_total = test_once(self.pmf_file_name, self.source_file_name, self.encoded_file_name, self.decoded_file_name)
        calcCodecInfo.work_flow(self.source_file_name, self.encoded_file_name, self.csv_file_name,
                                header_size=read_header_size(self.encoded_file_name))
        with open(self.csv_file_name) as f:
            result = f.read().strip()
            result = tuple(map(lambda s: s.strip('"'), result.split('\n')[-1].split(',')))
            print(result)  # 打印实际结果以便调试
            assert (result[0] == self.source_file_name)
            assert (result[1]==self.encoded_file_name)
            assert float(result[2])<1.0
            assert float(result[3])>8.0
            assert float(result[4])<0
            assert requal(float(result[5]),8.0, 2)
            assert requal(float(result[6]),8.0, 0)
        assert diff_total==0, "源文件和解码文件应完全相同"

    print('\ntest_uniform_distribution:'.title())
    test_uniform_distribution(namespace)
    print('\ntest_empty_file:'.title())
    test_empty_file(namespace)
    print('\ntest_unmapped_distribution:'.title())
    test_unmapped_distribution(namespace)
    # 删除临时文件
    if os.path.exists(namespace.encoded_file_name):
        os.remove(namespace.encoded_file_name)
    if os.path.exists(namespace.decoded_file_name):
        os.remove(namespace.decoded_file_name)
    if os.path.exists(namespace.pmf_file_name):
        os.remove(namespace.pmf_file_name)
    if os.path.exists(namespace.source_file_name):
        os.remove(namespace.source_file_name)
    if os.path.exists(namespace.csv_file_name):
        os.remove(namespace.csv_file_name)


if __name__ == '__main__':
    test_flow()
