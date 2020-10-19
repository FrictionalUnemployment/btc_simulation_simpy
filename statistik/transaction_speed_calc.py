import math
import asyncio
import websockets
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

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

def freedman_diaconis(data):
    h = (2 * (data["75%"] - data["25%"])) / math.pow(data["count"], (1/3))
    return int((data["max"] - data["min"]) / h)

def plot(data, data_desc, plotNumb, title):
    plt.figure(plotNumb)
    plt.hist(data, bins=freedman_diaconis(data_desc))
    plt.title(title)

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

async def subscribe(ws):
    await ws.send('{"op":"unconfirmed_sub"}')
    print("Now subscribed to unconfirmed transactions")

async def main():
    uri = "wss://ws.blockchain.info/inv"
    NUMBER_OF_TRANSACTIONS = int(input("Number of transactions to time: "))
    with open("tx_time.txt", "w") as f:
        async with websockets.connect(uri) as ws:
            await subscribe(ws)
            time_last = 0
            for i in range(NUMBER_OF_TRANSACTIONS):
                tx = await ws.recv()
                if time_last == 0:
                    time_last = time.time()
                else:
                    time_now = time.time()
                    f.write(str(time_now - time_last) + '\n')
                    time_last = time_now
                print("Transaction revieced")
    with open("tx_time.txt", "r") as f:
        times = np.array(f.readlines(), np.float)
        time_desc = describe(times)
        plot(times, time_desc, 1, "Time between transactions")
        dist_times = my_distribution(time_desc)
        dist_times_ar = np.array(dist_times.rvs(500), np.float)
        plot(dist_times_ar, describe(dist_times_ar), 2, "Random time between transactions")
        print("Times:")
        print(time_desc)
        print("Random times:")
        print(describe(dist_times_ar))
        plt.show()

asyncio.get_event_loop().run_until_complete(main())
