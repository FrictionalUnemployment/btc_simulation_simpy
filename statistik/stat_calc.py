import math
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import scipy.stats

NUMBER_OF_BLOCKS = int(input("Number of blocks to check: "))

timeStart = datetime.now()

latest_block = requests.get("https://blockchain.info/latestblock")
block_hash = json.loads(latest_block.text)["hash"]

raw_block = requests.get("https://blockchain.info/rawblock/" + block_hash)
block_info = json.loads(raw_block.text)

lengths_l = []
time_l = []
lengths = np.array([])
time = np.array([])
sizes = np.array([])
fees = np.array([])

try:
    prevTime = 0
    i = 0
    while True:
        if NUMBER_OF_BLOCKS != 0 and i >= NUMBER_OF_BLOCKS:
            break
        next_block = requests.get("https://blockchain.info/rawblock/" + block_info["prev_block"])
        lengths_l.append(len(block_info["tx"]))
        if len(lengths_l) > 1000:
            lenghts = np.append(lenghts, lenghts_l)
            lenghts_l = []
        if prevTime != 0:
            time_l.append(prevTime - block_info["time"])
        prevTime = block_info["time"]
        if len(time_l) > 1000:
            time = np.append(time, time_l)
            time_l = []
        sizes = np.append(sizes, [tx["size"] for tx in block_info["tx"]])
        fees = np.append(fees, [tx["fee"] / tx["size"] for tx in block_info["tx"]])

        block_info = json.loads(next_block.text)
        print(f"Blocks checked: {i + 1}", end="\r")
        i += 1
except KeyboardInterrupt:
    print("\nCancelling")
finally:
    lengths = np.append(lengths, lengths_l)
    lengths_series = pd.Series(lengths)
    lengths_desc = lengths_series.describe()

    time = np.append(time, time_l)
    time_series = pd.Series(time)
    time_desc = time_series.describe()

    sizes_series = pd.Series(sizes)
    sizes_desc = sizes_series.describe()

    fees_series = pd.Series(fees)
    fees_desc = fees_series.describe()

    def freedman_diaconis(data):
        h = (2 * (data["75%"] - data["25%"])) / math.pow(data["count"], (1/3))
        return int((data["max"] - data["min"]) / h)

    def plot(data, data_desc, plotNumb, title):
        plt.figure(plotNumb)
        plt.hist(data, bins=freedman_diaconis(data_desc))
        plt.title(title)
    
    plot(lengths, lengths_desc, 1, "Block transaction lengths")
    plot(sizes, sizes_desc, 2, "Transaction sizes")
    plot(fees, fees_desc, 3, "Transaction fees (BTC/byte)")
    plot(time, time_desc, 4, "Time between confirmations")

    # Generating random data with the same distribution to compare results
    # Funciton taken from jdehesa on stackoverflow (https://stackoverflow.com/a/50629604) with slight changes
    def my_distribution(desc):
        min_val = desc["min"]
        max_val = desc["max"]
        mean = desc["mean"]
        std = desc["std"]
        scale = max_val - min_val
        location = min_val
        # Mean and standard deviation of the unscaled beta distribution
        unscaled_mean = (mean - min_val) / scale
        unscaled_var = (std / scale) ** 2
        # Computation of alpha and beta can be derived from mean and variance formulas
        t = unscaled_mean / (1 - unscaled_mean)
        beta = ((t / unscaled_var) - (t * t) - (2 * t) - 1) / ((t * t * t) + (3 * t * t) + (3 * t) + 1)
        alpha = beta * t
        # Not all parameters may produce a valid distribution
        if alpha <= 0 or beta <= 0:
            raise ValueError('Cannot create distribution for the given parameters.')
        # Make scaled beta distribution with computed parameters
        return scipy.stats.beta(alpha, beta, scale=scale, loc=location)
    
    dist_sizes = my_distribution(sizes_desc)
    dist_fees = my_distribution(fees_desc)
    dist_time = my_distribution(time_desc)

    d_sizes_series = pd.Series(dist_sizes.rvs(1000))
    d_fees_series = pd.Series(dist_fees.rvs(1000))
    d_time_series = pd.Series(dist_time.rvs(1000))

    plot(d_sizes_series, d_sizes_series.describe(), 5, "Random Transaction sizes")
    plot(d_fees_series, d_fees_series.describe(), 6, "Random Transaction fees")
    plot(d_time_series, d_time_series.describe(), 7, "Random time between confirmations")

    print("\nLengths:")
    print(lengths_desc)
    print()
    print("Transaction sizes:")
    print(sizes_desc)
    print()
    print("Transaction fees")
    print(fees_desc)
    print()
    print("Time between confirmations")
    print(time_desc)
    print("Random transaction sizes:")
    print(d_sizes_series.describe())
    print("Random transaction fees:")
    print(d_fees_series.describe())
    print("Random time between confirmations")
    print(d_time_series.describe())
    print(f"\nTime taken: {datetime.now() - timeStart}")    
    plt.show()

# To make a sample with the same mean and standard deviation use
# np.random.normal(loc=mean, scale=std)