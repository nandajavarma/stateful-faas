import io
import os
import re
import requests
import math

from minio import Minio

NREDUCERS = 3

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    print(req)
    match = re.match(r"BUCKET=(.+)&FILENAME=(.+)&NMAPPERS=(.+)&length=(.+)&node_number=(.+)", req)
    bucket, filename, nmappers, length, node_number = match.groups(0)
    node_number = int(node_number)
    length = int(length)
    nmappers = int(nmappers)

    # Launch other mappers nodes to make the complexity logarithmic
    currently_launching = 1 if node_number == 0 else int(pow(
        2, int(math.log(node_number, 2)) + 1))
    next_launch = currently_launching + node_number
    while next_launch < nmappers:
        info = {
                "BUCKET": bucket,
                "FILENAME": filename,
                "NMAPPERS": nmappers,
                "length": length,
                "node_number": next_launch
                }
        url = "http://34.207.121.118:8080/function/mapper"
        currently_launching = 2 * currently_launching
        next_launch = currently_launching + node_number
        r = requests.post(url, data=info)

    mc = Minio('172.31.48.240:9000',
                  access_key='minioadmin',
                  secret_key='minioadmin',
                  secure=False)

    initial_offset = node_number * length
    data = mc.get_partial_object(bucket, filename, initial_offset, length)
    data = " ".join([x.decode('utf8').strip().lower() for x in data.readlines()])

    words = list(filter(None, data.split(" ")))
    data_to_write = {}
    for word in words:
        ascii_val = ord(word[0])
        key = ascii_val % NREDUCERS
        if key not in data_to_write:
            data_to_write[key] = []
        data_to_write[key].append((word, 1))

    for key, value in data_to_write.items():
        if not value:
            continue
        value_as_a_stream = io.BytesIO(bytes(str(value).encode('utf-8')))
        mc.put_object('output2', str(key), value_as_a_stream, len(bytes(str(value).encode('utf-8'))))
    if node_number >= nmappers - 2:
        # Time to launch the reducers 
        print("Launching reducers")
        info = {
                "BUCKET": 'output2',
                "node_number": 0,
                'NREDUCERS': 3
                }
        print(info)
        url = "http://34.207.121.118:8080/function/reducer"
        r = requests.post(url, data=info)
    return req
