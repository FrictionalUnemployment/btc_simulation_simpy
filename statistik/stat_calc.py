import numpy as np
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import scipy.stats as stats

NUMBER_OF_BLOCKS = 100 # Change this to change the number of blocks this program checks

timeStart = datetime.now()

latest_block = requests.get("https://blockchain.info/latestblock")
block_hash = json.loads(latest_block.text)["hash"]

raw_block = requests.get("https://blockchain.info/rawblock/" + block_hash)
block_info = json.loads(raw_block.text)

lengths = []
sizes = []
fees = []

for i in range(NUMBER_OF_BLOCKS):
    next_block = requests.get("https://blockchain.info/rawblock/" + block_info["prev_block"])
    lengths.append(len(block_info["tx"]))

    for tx in block_info["tx"]:
        sizes.append(tx["size"])
        fees.append(tx["fee"]/tx["size"])  # BTC/byte

    block_info = json.loads(next_block.text)
    print(f"Blocks checked: {i + 1}", end="\r")

plt.figure(1)
mean_len = np.mean(lengths)
std_len = np.std(lengths)
lengths.sort()
pdf_len = stats.norm.pdf(lengths, mean_len, std_len)
plt.plot(lengths, pdf_len)
plt.title("Block transaction lengths")

plt.figure(2)
mean_tx = np.mean(sizes)
std_tx = np.std(sizes)
sizes.sort()
pdf_tx = stats.norm.pdf(sizes, mean_tx, std_tx)
plt.plot(sizes, pdf_tx)
plt.title("Transaction sizes")

plt.figure(3)
mean_fee = np.mean(fees)
std_fee = np.std(fees)
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