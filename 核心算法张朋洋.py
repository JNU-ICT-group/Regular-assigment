#算法设计张朋洋



import numpy as np
import sys

def byte_channel(input_path, noise_path, output_path):
    """
    模拟二元对称信道 (BSC)，将噪声作用在输入消息上。

    Parameters:
        input_path (str): 输入消息文件的路径。
        noise_path (str): 噪声文件的路径。
        output_path (str): 输出文件的路径。
    """

    # Step 1: 读取输入和噪声文件
    input_data = np.fromfile(input_path, dtype='uint8')
    noise_data = np.fromfile(noise_path, dtype='uint8')

    # 检查输入和噪声文件大小是否一致
    if input_data.size != noise_data.size:
        raise ValueError("输入文件和噪声文件的大小必须相同。")
        
   #噪声加到输入上，我感觉其实是异或运算！
    # Step 2: 通过异或运算将噪声作用在输入数据上,
 
    output_data = np.bitwise_xor(input_data, noise_data)

    # Step 3: 将结果写入输出文件
    output_data.tofile(output_path)

    print(f"输出文件已保存到 {output_path}")

if __name__ == "__main__":
    # 程序入口，读取命令行参数
    if len(sys.argv) != 4:
        print("Usage: python byteChannel.py <input_file> <noise_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]  # 输入消息文件路径
    noise_file = sys.argv[2]  # 噪声文件路径
    output_file = sys.argv[3]  # 输出文件路径

    # 调用 byte_channel 函数
    byte_channel(input_file, noise_file, output_file)

#我建议后续直接在我这个文件上加改，可以给文件改成合适的名字。



#   后续通过这个命令：
#   python calcBSCInfo.py input_file output_file results.csv -v
#   来运行calcBSCInfo.py程序从而计算信道输入输出文件的统计指标