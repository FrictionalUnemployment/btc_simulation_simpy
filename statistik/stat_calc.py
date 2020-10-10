import numpy as np
import requests
import json

latest_block = requests.get("https://blockchain.info/latestblock")
block_hash = json.loads(latest_block.text)["hash"]

raw_block = requests.get("https://blockchain.info/rawblock/" + block_hash)
block_info = json.loads(raw_block.text)

lengths = []
sizes = []

for i in range(5):
    next_block = requests.get("https://blockchain.info/rawblock/" + block_info["prev_block"])
    lengths.append(len(block_info["tx"]))

    for tx in block_info["tx"]:
        print(tx["fee"])
        print(tx["size"])
        print('\n')

    block_info = json.loads(next_block.text)

mean_len = np.mean(lengths)
std_len = np.std(lengths)

mean_tx = np.mean(sizes)
std_tx = np.std(sizes)

# sample = np.random.normal(loc=mean, scale=std)
print(mean_len)
print(std_len)
print('\n')
print(mean_tx)
print(std_tx)