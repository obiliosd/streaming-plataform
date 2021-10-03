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

def sendRandomPostion(df, numberRaider, url, headers):
    for i in range(numberRaider):
        data = generateData(i,df)
        try:
            requests.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)

if __name__ == "__main__":
    numberRaider = int(os.environ['NUM_RAIDER'])
    interval = 5

    url = os.environ['LISTENER_URL']
    headers = {"Content-Type": "application/json"}

    filePath = os.environ['DATA_PATH']
    df = readData(filePath)

    while True:
        sendRandomPostion(df, numberRaider, url, headers)
        time.sleep(interval)
