#Class for creating transaction struct

from datetime import datetime

class Transactions:
    
    def __init__(self, tid, tfee, tsize):
        self.id = tid # The Transaction ID is stored here
        self.fee = tfee # The Priority (based on amount of fee is stored here) 
        self.stamp = getTimestamp() #Time stamp is stored here
        self.size = tsize #Transaction size is stored here
        
#Get the current local timestamp
def getTimestamp():
    now = datetime.now()
    return now

#Example code to utilize this class is to use:
#my_arr = []
#my_arr.append(Transactions(1, 30, 300))
#my_arr.append(Transactions(2, 40, 400))
