import math
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import scipy.stats

NUMBER_OF_BLOCKS = int(input("Number of blocks to check: "))

timeStart = datetime.now()

latest_block = requests.get("https://blockchain.info/latestblock")
block_hash = json.loads(latest_block.text)["hash"]

raw_block = requests.get("https://blockchain.info/rawblock/" + block_hash)
block_info = json.loads(raw_block.text)

lengths_o = open("lengths.txt", "w")
time_o = open("time.txt", "w")
sizes_o = open("sizes.txt", "w")
fees_o = open("fees.txt", "w")


try:
    prevTime = 0
    i = 0
    while True:
        if NUMBER_OF_BLOCKS != 0 and i >= NUMBER_OF_BLOCKS:
            break
        next_block = requests.get("https://blockchain.info/rawblock/" + block_info["prev_block"])
        lengths_o.write(str(len(block_info["tx"])) + '\n')
        if prevTime != 0:
            time_o.write(str(prevTime - block_info["time"]) + '\n')
        prevTime = block_info["time"]
        sizes_o.writelines(str(tx["size"]) + '\n' for tx in block_info["tx"])
        fees_o.writelines(str(tx["fee"] / tx["size"]) + '\n' for tx in block_info["tx"])

        block_info = json.loads(next_block.text)
        print(f"Blocks checked: {i + 1}", end="\r")
        i += 1
except KeyboardInterrupt:
    print("\nCancelling")
finally:
    lengths_o.close()
    time_o.close()
    sizes_o.close()
    fees_o.close()

    lengths_i = open("lengths.txt", "r")
    time_i = open("time.txt", "r")
    sizes_i = open("sizes.txt", "r")
    fees_i = open("fees.txt", "r")

    def describe(ar):
        desc = {}
        desc["count"] = ar.size
        desc["min"] = ar.min()
        desc["max"] = ar.max()
        desc["std"] = ar.std()
        desc["mean"] = ar.mean()
        desc["25%"] = np.percentile(ar, 25)
        desc["50%"] = np.percentile(ar, 50)
        desc["75%"] = np.percentile(ar, 75)
        return desc

    lengths = np.array(lengths_i.readlines(), np.int32)
    lengths_desc = describe(lengths)

    time = np.array(time_i.readlines(), np.int32)
    time_desc = describe(time)

    sizes = np.array(sizes_i.readlines(), np.int32)
    sizes_desc = describe(sizes)

    fees = np.array(fees_i.readlines(), np.float)
    fees_desc = describe(fees)

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

    d_sizes_ar = np.array(dist_sizes.rvs(500), np.int32)
    d_fees_ar = np.array(dist_fees.rvs(500), np.float)
    d_time_ar = np.array(dist_time.rvs(500), np.int32)

    try:
        plot(d_sizes_ar, describe(d_sizes_ar), 5, "Random Transaction sizes")
    except (ValueError, OverflowError):
        print("Unable to graph random transaction sizes. Maybe most values are in the same bin")
    try:
        plot(d_fees_ar, describe(d_fees_ar), 6, "Random Transaction fees")
    except (ValueError, OverflowError):
        print("Unable to graph random transaction fees")
    try:
        plot(d_time_ar, describe(d_time_ar), 7, "Random time between confirmations")
    except (ValueError, OverflowError):
        print("Unable to graph random time between confirmations")

    print("\nLengths:")
    print(lengths_desc)

    print("\nTransaction sizes:")
    print(sizes_desc)

    print("\nRandom transaction sizes:")
    print(describe(d_sizes_ar))

    print("\nTransaction fees")
    print(fees_desc)

    print("\nRandom transaction fees:")
    print(describe(d_fees_ar))

    print("\nTime between confirmations")
    print(time_desc)

    print("\nRandom time between confirmations")
    print(describe(d_time_ar))

    print(f"\nTime taken: {datetime.now() - timeStart}")    
    plt.show()