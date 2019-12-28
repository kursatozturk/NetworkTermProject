from functools import reduce
from math import sqrt
from matplotlib import pyplot as plt
from typing import List
from random import random


def calculate_error_margin(arr):
    mean = sum(arr) / len(arr)
    std_dev = sqrt(reduce(lambda x, y: x + (mean - y) ** 2, arr, 0) / (len(arr) - 1))
    error = 1.96 * std_dev / sqrt(len(arr))
    return error


def plot_array(x_axis: List, y_axis: List, errors: List):
    fig = plt.figure()
    plt.errorbar(x=x_axis, y=y_axis, yerr=errors)
    plt.ylabel("File Transfer Time (s)")
    plt.xlabel("Packet Loss Percantage (%)")
    plt.show()
    plt.savefig('./plot.png')
    fig.savefig('figure.png', dpi=fig.dpi * 4)


experiment1 = {
    "5": [
        27.696946382522583,
        28.43569040298462,
        27.206584692001343,
        27.089531660079956,
        26.95274829864502,
        27.1502881239992,
        27.960291828382012,
        26.80212381236811,
        28.11238182832828,
    ],
    "15": [
        45.03063988685608,
        43.38268160820007,
        45.38371729850769,
        45.55020192392611,
        44.44391923969292,
        43.0913812832112,
        44.010238672291,
        43.1692812738219,
        46.02012303123213,
    ],
    "38": [
        151.24365997314453,
        147.85718321800232,
        154.80341029167175,
        149.2328182318232,
        148.23182353454533,
        155.3582384822152,
        151.8823195129323,
        149.923415828382,
        157.1238218523666,
    ],
}
experiment2 = {
    "5": [
        40.350505352020264,
        42.63038086891174,
        42.95955419540405,
        43.105690002441406,
        42.95677638053894,
        43.29238214828323,
        43.9921231293921,
        40.92102305202073,
        43.2214858128321,
    ],
    "15": [
        50.77649712562561,
        50.374202728271484,
        50.67056226730347,
        50.45198388213841,
        50.702123885215904,
        52.1023867201923,
        53.050286772391239,
        50.023018283821011,
        52.8012382132392,
    ],
    "38": [
        119.44282555580139,
        122.29072999954224,
        126.86380410194397,
        118.621731823428523,
        125.9032148518238,
        128.68182303240201,
        120.968438582341223,
        122.65192391239210,
        130.221473921300123,
    ],
}


means1 = {
    k: (sum(arr) / len(arr), calculate_error_margin(arr))
    for k, arr in experiment1.items()
}

means2 = {
    k: (sum(arr) / len(arr), calculate_error_margin(arr))
    for k, arr in experiment2.items()
}

plot_array(
    x_axis=list(int(x) for x in means1.keys()),
    y_axis=list(x for x, y in means1.values()),
    errors=list(y for x, y in means1.values()),
)
plot_array(
    x_axis=list(int(x) for x in means2.keys()),
    y_axis=list(x for x, y in means2.values()),
    errors=list(y for x, y in means2.values()),
)


print('first experiment error margins as percentage')
for key, (mean, error) in means1.items():
    print (f'{key}: {100 * error/mean}')

print('second experiment error margins as percentage')
for key, (mean, error) in means2.items():
    print (f'{key}: {100 * error/mean}')
    
"""
first experiment error margins as percentage
    5% : 1.3713744181117475
    15%: 1.618609597411173
    38%: 1.4336633404599477
second experiment error margins as percentage
    5% : 1.8141649962841349
    15%: 1.4356779563259368
    38%: 2.1735477910312055
"""