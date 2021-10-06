import json
import os
import random
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests

def readData(filePath):
    input_file = open(filePath)
    json_array = json.load(input_file)
    coordinates = json_array['features'][0]['geometry']['coordinates'][0]
    numpy_data = np.array(coordinates[0:4])
    return pd.DataFrame(data=numpy_data, columns=["x", "y"])

def generateRandomCoordinate(df):
    x = random.uniform(df.x.min(),df.x.max())
    y = random.uniform(df.y.min(),df.y.max())
    return [x,y]

def generateData(id, df):
    data = {}
    data['key'] = id+1
    data['country'] = 'Spain'
    data['region'] = 'Barcelona'
    data['coordinates'] = generateRandomCoordinate(df)
    data['timestamp'] = str(datetime.utcnow())
    return data

def sendRandomPostion(df, numberRaider, url):
    for i in range(numberRaider):
        data = generateData(i,df)
        try:
            requests.post(url, json=data)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)

if __name__ == "__main__":  
    interval = 1
    url = os.environ['LISTENER_URL']
    numberRaider = int(os.environ['NUM_RAIDER'])
    filePath = os.environ['DATA_PATH']
    df = readData(filePath)
    while True:
        sendRandomPostion(df, numberRaider, url)
        time.sleep(interval)
