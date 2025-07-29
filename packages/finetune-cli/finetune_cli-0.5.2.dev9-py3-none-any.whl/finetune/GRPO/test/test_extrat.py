import math


def Lorentz_modify(x):
    return 1 / (1 + abs(x))


if __name__ == '__main__':
    # 画图
    print(Lorentz(-2100000))
