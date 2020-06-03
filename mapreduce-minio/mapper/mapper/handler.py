import os
import re
import requests

from minio import Minio


def laucher(node_number, nmappers, length, BUCKET, FILENAME):
    # This math shows how many nodes are currently being launched by coordinator and other mappers
    currently_launching = 1 if int(node_number) == 0 else int(pow(
        2, int(math.log(node_number, 2)) + 1))
    next_launch = currently_launching + node_number
    while next_launch < nmappers:
        info = {
                "BUCKET": BUCKET,
                "FILENAME": FILENAME,
                "NMAPPERS": nmappers,
                "length": length,
                "node_number": next_launch
                }
        url = "http://34.207.121.118:8080/function/mapper"
        r = requests.post(url, data=info)
        currently_launching = 2 * currently_launching
        next_launch = currently_launching + node_number


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    match = re.match(r"BUCKET=(.+)&FILENAME=(.+)&NMAPPERS=(.+)&length=(.+)&node_number=(.+)", req)
    bucket, filename, nmappers, length, node_number = match.groups(0)
    node_number = int(node_number)
    length = int(length)
    nmappers = int(nmappers)

    # Launch other mappers nodes to make the complexity logarithmic
    laucher(node_number, nmappers, length, bucket, filename)

    mc = Minio('172.31.48.240:9000',
                  access_key='minioadmin',
                  secret_key='minioadmin',
                  secure=False)

    initial_offset = node_number * length
    data = mc.get_partial_object(bucket, filename, initial_offset, length)
    print(data.read())
    return req
