import numpy as np

def generate_error_channel(arr, noise) -> np.ndarray:
    """
    使用np.searchsorted对np.random.uniform的结果做分类，使其中1的概率为p（二元对称信道错误传输概率），
    即0的概率为1-p，为了方便使用byteSource产生随机序列，将二元概率空间以8个bit一组，合并为1byte长度，即N=8次扩展。
    然后使用异或将NOISE加载到256元的信源X上。这种方法仅适用于BSC

    Parameters:
        arr (numpy.ndarray): 信源X。
        noise (numpy.ndarray): 信道的噪声。

    Returns:
        numpy.ndarray: 信道输出的信源Y。
    """
    if len(arr) * 8 == len(noise):
        noise = np.packbits(noise)
    out = np.bitwise_xor(arr, noise)
    return out
