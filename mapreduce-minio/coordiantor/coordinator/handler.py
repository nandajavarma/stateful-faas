import os
import requests

from minio import Minio

NMAPPERS = 3
MINBLOCKSIZE = 30000
SAFEMEMORYSIZE = 35000

BUCKET = "files"
FILENAME = "sample.csv"

def get_chunk_size(data_size):
    global NMAPPERS
    chunksize = data_size // NMAPPERS
    print(data_size, NMAPPERS)
    if chunksize < MINBLOCKSIZE:
        chunksize = MINBLOCKSIZE
        NMAPPERS = (data_size // MINBLOCKSIZE) + 1
    if chunksize > SAFEMEMORYSIZE:
        chunksize = SAFEMEMORYSIZE
        NMAPPERS = (data_size // SAFEMEMORYSIZE) + 1
    return chunksize

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    mc = Minio('172.31.48.240:9000',
                  access_key='minioadmin',
                  secret_key='minioadmin',
                  secure=False)
    gateway_hostname = os.getenv("gateway_hostname", "gateway")
    obj = mc.stat_object(BUCKET, FILENAME)
    length = get_chunk_size(obj.size)
    info = {
            "BUCKET": BUCKET,
            "FILENAME": FILENAME,
            "NMAPPERS": NMAPPERS,
            "length": length
            }
        # data = mc.get_partial_object(BUCKET, FILENAME, offset, length)
        # print(data.read())
    url = gateway_hostname + "/function/mapper"
    print(url)
    r = requests.get(url, data=info)
    if r.status_code != 200:
        sys.exit("Error with mapper, expected: %d, got: %d\n" % (200, r.status_code))
    return req
