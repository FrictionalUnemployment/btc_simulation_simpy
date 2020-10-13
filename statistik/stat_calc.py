import numpy as np
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import scipy.stats as stats
import pandas as pd

# NUMBER_OF_BLOCKS = 2000 # Change this to change the number of blocks this program checks
NUMBER_OF_BLOCKS = int(input("Number of blocks to check: "))

timeStart = datetime.now()

latest_block = requests.get("https://blockchain.info/latestblock")
block_hash = json.loads(latest_block.text)["hash"]

raw_block = requests.get("https://blockchain.info/rawblock/" + block_hash)
block_info = json.loads(raw_block.text)

lengths_l = []
lengths = np.array([])
sizes = np.array([])
fees = np.array([])

try:
    # for i in range(NUMBER_OF_BLOCKS):
    i = 0
    while True:
        if NUMBER_OF_BLOCKS != 0 and i >= NUMBER_OF_BLOCKS:
            break
        next_block = requests.get("https://blockchain.info/rawblock/" + block_info["prev_block"])
        lengths = np.append(lengths, len(block_info["tx"]))
        lengths_l.append(len(block_info["tx"]))
        if len(lengths_l) > 1000:
            lenghts = np.append(lenghts, lenghts_l)
            lenghts_l = []
        sizes = np.append(sizes, [tx["size"] for tx in block_info["tx"]])
        fees = np.append(fees, [tx["fee"] / tx["size"] for tx in block_info["tx"]])

        block_info = json.loads(next_block.text)
        print(f"Blocks checked: {i + 1}", end="\r")
        i += 1
except KeyboardInterrupt:
    print("\nCancelling")
finally:
    print()
    lengths = np.append(lenghts, lengths_l)
    lengths_series = pd.Series(lengths)
    lengths_desc = lengths_series.describe()

    sizes_series = pd.Series(sizes)
    sizes_desc = sizes_series.describe()

    fees_series = pd.Series(fees)
    fees_desc = fees_series.describe()


    plt.figure(1)
    mean_len = lengths_desc["mean"]
    std_len = lengths_desc["std"]
    lengths.sort()
    pdf_len = stats.norm.pdf(lengths, mean_len, std_len)
    plt.plot(lengths, pdf_len)
    plt.title("Block transaction lengths")

    plt.figure(2)
    mean_tx = sizes_desc["mean"]
    std_tx = sizes_desc["std"]
    sizes.sort()
    pdf_tx = stats.norm.pdf(sizes, mean_tx, std_tx)
    plt.plot(sizes, pdf_tx)
    plt.title("Transaction sizes")

    plt.figure(3)
    mean_fee = fees_desc["mean"]
    std_fee = fees_desc["std"]
    fees.sort()
    pdf_fee = stats.norm.pdf(fees, mean_fee, std_fee)
    plt.subplot(221)
    plt.plot(fees, pdf_fee)
    plt.title("Transaction fees (BTC/byte)")

    print(f"Mean block length: {mean_len}")
    print(f"Standard deviation block length: {std_len}")
    print(f"\nMean transaction size: {mean_tx}")
    print(f"Standard deviation transaction size: {std_tx}")
    print(f"\nMean transaction fee (BTC/byte): {mean_fee}")
    print(f"Standard deviation transaction fee (BTC/byte): {std_fee}")
    print(f"\nTime taken: {datetime.now() - timeStart}")
    plt.show()
# To make a sample with the same mean and standard deviation use
# np.random.normal(loc=mean, scale=std)