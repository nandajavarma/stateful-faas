from ast import literal_eval
import io
import os
import re
import requests

from minio import Minio



def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    match = re.match(r"number=(.+)", req)
    number = int(match.groups(0))

    # Launch other mappers nodes to make the complexity logarithmic
    url = "http://3.138.111.110:8080/function/{}"
    if number%3 == 0:
        url = url.format("fizz")
    elif number%5 == 0:
        url = url.format("buzz")
    else:
        url = url.format("identity")
    r = requests.post(url, data=number)
    r.raise_for_status()
    print(r)


    return req
