import simpy
import numpy as np
import random
from transaktionsinfo.Transactions import Transactions as transStruct
import scipy.stats

BLOCK_SIZE = 1000000.0 # Block size in byte 8 mb
WEEKS = 1              # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60 #Simulation time in minutes

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

def transaction_fee():
    fee_stats = {
        "min" : 0.0,
        "max" : 6613.452914798207,
        "std" : 39.29058098609857,
        "mean" : 40.94675290066939
    }
    fee_distribution = my_distribution(fee_stats)
    return fee_distribution.rvs(1)

def transaction_size():
    size_stats = {
        "min" : 85,
        "max" : 224490,
        "std" : 3057.464928392748,
        "mean" : 567.9297258267701
    }
    size_distribution = my_distribution(size_stats)
    return size_distribution.rvs(1)

def transaction_time():
    time_stats = {
        "min" : 0.0,
        "max" : 3.6399197578430176,
        "std" : 0.5587378196011653,
        "mean" : 0.38716406497793115
    }
    time_distribution = my_distribution(time_stats)
    return time_distribution.rvs(1)

def time_to_confirm():
    """Return the actual time to confirm. Not done yet"""
    confirm_stats = {
        "min" : 0,
        "max" : 3986,
        "std" : 587.3529955567874,
        "mean" : 586.9941656942824
    }
    confirm_distribution = my_distribution(confirm_stats)
    return confirm_distribution.rvs(1)

def main():
    #Create an environment and start the setup process
    env = simpy.Environment() #simpy.realtimeEnvironment for real time sync
    #pipe = simpy.Store(env)
    pool = MemPool(env)
    #env.process(confirm_transaction(env, pipe))
    #env.process(create_transactions(env, pipe))
    env.run(until=SIM_TIME) #Run the program until SIM_TIME

class MemPool(object):
    """
    Mempool class 

    """

    def __init__(self, env, capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.transactions = [] #Transactions in the "mempool"
        self.blocks = [] #Store transactions in each block
        self.confirmations_made = 0
        self.blocks_confirmed = 0
        self.process = env.process(self.put_transactions())
        env.process(self.confirm_transaction())

    def confirm_transaction(self):
        while True:
            yield self.env.timeout(time_to_confirm())
            #Send an interrupt to add_transactions to confirm the block
            self.process.interrupt()
            
    def put_transactions(self):
        #store = simpy.Store(self.env, capacity=self.capacity)
        cnt = 0
        while True:
        #Start adding transactions until we confirm
            confirmation_in = time_to_confirm()
            while confirmation_in:
                try:
                    #We append transactions to our array
                    self.transactions.append(transStruct(cnt,
                                                         transaction_fee(),
                                                         transaction_size(),
                                                         self.env.now))
                    yield self.env.timeout(transaction_time()) # The time it takes to create a transaction
                except simpy.Interrupt:
                    confirmation_in = 0 # exit while loop
                cnt += 1
            print('array before removal %d Time now also %d' % (len(self.transactions), self.env.now))
            self.add_transactions_to_block(BLOCK_SIZE)
            print('Block number %d Length of array %s Counter %i' % (self.blocks_confirmed, len(self.transactions), cnt))
            self.blocks_confirmed += 1

    #Here we remove transactions from the mempool as they are 'confirmed'
    #Could also add them into a block if needed?
    def add_transactions_to_block(self, block_size):
        temporary_block_size = 0
        temp_arr = []
        self.transactions.sort(key=lambda x: x.fee, reverse=True) #We prioritize the fee to be first added into the block
        for x in range(len(self.transactions)):
            if(temporary_block_size < block_size):
                temporary_block_size += self.transactions[0].size # We add the size of the transaction
                                                                  # To our temporary block size first
                                                                  # Because afterwards we remove the element
                temp_arr.append(self.transactions[0]) # Add transactions to our temporary array to later be added into the confirmed block
                self.transactions.pop(0) #Remove the first element
            elif(temporary_block_size == block_size):
                break
            
        self.blocks.append(temp_arr) #Append all transactions into a block
        
if __name__ == '__main__':
    main()
