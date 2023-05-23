import numpy as np 
import geopy.distance

class FireForest()

def temperature_incremental(distance,temperature=27,constant=500):
    incremental = temperature + constant/distance
    return incremental 

def humidity_incremental(distance,constant=1):
        incremental =  0.8/np.exp(1/(constant*distance))
        return incremental

