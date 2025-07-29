from math import cos


def ReLU(x):
    return x * (x > 0)


def N(t: int):
    return ReLU(1200 * cos((2 * 3.14 / 24) * (t - 14))) + 120


def Price_t(t: int):
    return max(0.05, min(0.05 * (1 + N(t) / 592.2), 0.1))


if __name__ == '__main__':
    sum = 0
    for t in range(24):
        P_h = Price_t(t) * N(t) - (20382/(365*24)) - (800/(30*24))
        print(f"{t}: {P_h}")
        sum += P_h
    print(sum)
