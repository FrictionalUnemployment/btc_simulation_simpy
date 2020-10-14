import simpy
import numpy as np

TIME_TO_CONFIRM = 10 # The time it will take to confirm the transaction
TRANSACTION_FEE = 3.0  # The transaction fee
TRANSACTION_SIZE = 1   # Transaction (individual) in byte
BLOCK_SIZE = 8000000.0 # Block size in byte
WEEKS = 4              # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60 #Simulation time in minutes

def transaction_fee():
    """Return the actual transaction fee. Not done yet"""
    return TRANSACTION_FEE

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
    pipe = simpy.Store(env)
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
        self.process = env.process(self.add_transactions())
        env.process(self.confirm_transaction())

    def confirm_transaction(self):
        while True:
            yield self.env.timeout(TIME_TO_CONFIRM)
            #Send an interrupt to add_transactions to confirm the block
            self.process.interrupt()
            
    def add_transactions(self):
        while True:
        #Start adding transactions until we confirm
            confirmation_in = time_to_confirm()
            while confirmation_in:
                try:
                    start = self.env.now
                    #yield self.env.timeout(30)
                except simpy.Interrupt:
                    confirmation_in = 0 # exit while loop
                    
            print("Block number", self.blocks_confirmed)
            self.blocks_confirmed += 1
        
if __name__ == '__main__':
    main()
