import simpy
import numpy as np
import random
from transaktionsinfo.Transactions import Transactions as transStruct

TIME_TO_CONFIRM = 0 # The time it will take to confirm the transaction
TRANSACTION_FEE = 3.0  # The transaction fee
TRANSACTION_SIZE = 9800   # Transaction (individual) in byte
BLOCK_SIZE = 8000000.0 # Block size in byte
WEEKS = 4              # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60 #Simulation time in minutes

def transaction_fee():
    """Return the actual transaction fee. Not done yet"""
    return random.randint(1,10)

def transaction_size():
    """Return the actual transaction size. Not done yet"""
    return TRANSACTION_SIZE

def time_to_confirm():
    """Return the actual time to confirm. Not done yet"""
    global TIME_TO_CONFIRM
    TIME_TO_CONFIRM += 10
    
    return TIME_TO_CONFIRM

def main():
    #Create an environment and start the setup process
    env = simpy.Environment() #simpy.realtimeEnvironment for real time sync
    #pipe = simpy.Store(env)
    bc_pipe = MemPool(env)
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
        self.transactions = []
        self.confirmations_made = 0
        self.blocks_confirmed = 0
        self.process = env.process(self.put_transactions())
        env.process(self.confirm_transaction())

    def confirm_transaction(self):
        while True:
            yield self.env.timeout(TIME_TO_CONFIRM)
            #Send an interrupt to add_transactions to confirm the block
            self.process.interrupt()
            
    def put_transactions(self):
        store = simpy.Store(self.env, capacity=self.capacity)
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
                    #yield store.put(self.transactions[cnt])
                    yield self.env.timeout(0.1) # The time it takes to create a transaction
                except simpy.Interrupt:
                    confirmation_in = 0 # exit while loop
                cnt += 1
            #msg = yield store.get()
            self.add_transactions_to_block(BLOCK_SIZE)
            print('Block number %d Length of array %s Counter %i' % (self.blocks_confirmed, len(self.transactions), cnt))
            self.blocks_confirmed += 1

    #Here we remove transactions from the mempool as they are 'confirmed'
    #Could also add them into a block if needed?
    def add_transactions_to_block(self, block_size):
        temporary_block_size = 0
        self.transactions.sort(key=lambda x: x.fee, reverse=True) #We prioritize the fee to be first added into the block
        for x in range(len(self.transactions)):
            if(temporary_block_size < block_size):
                temporary_block_size += self.transactions[0].size # We add the size of the transaction
                                                                  # To our temporary block size first
                                                                  # Because afterwards we remove the element
                self.transactions.pop(0) #Remove the first element
            elif(temporary_block_size == block_size):
                break
            
        
        
if __name__ == '__main__':
    main()
