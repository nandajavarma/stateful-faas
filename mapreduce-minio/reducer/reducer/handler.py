from ast import literal_eval
import io
import os
import re
import requests

from minio import Minio

NREDUCERS = 3




def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    match = re.match(r"BUCKET=(.+)&node_number=(.+)&NREDUCERS=(.+)", req)
    bucket, node_number, nreducers = match.groups(0)
    node_number = int(node_number)
    nreducers = int(nreducers)

    # Launch other mappers nodes to make the complexity logarithmic
    if node_number == 0:
        print("Launching more reducers")
        next_node = node_number + 1
        while next_node < nreducers:
            info = {
                    "BUCKET": bucket,
                    "node_number": next_node,
                    'NREDUCERS': 3
                    }
            url = "http://34.207.121.118:8080/function/reducer"
            r = requests.post(url, data=info)
            next_node = next_node + 1

    mc = Minio('34.207.121.118:9000',
                  access_key='minioadmin',
                  secret_key='minioadmin',
                  secure=False)

    key = str(node_number)
    data = mc.get_object(bucket, key)
    data = " ".join([x.decode('utf8').strip() for x in data.readlines()])
    mapped_data = [(m.group(1).strip("'"), int(m.group(2).strip("'"))) for m in re.finditer(r'\(([^,]*), ([^,]*)\),', data)] 
    results = {}
    for (word, count) in mapped_data:
        results[word] = results.get(word, 0) + 1
    # Sort please
    ret = {k: v for k, v in sorted(results.items(), key=lambda item: item[0])}
    value_as_a_stream = io.BytesIO(bytes(str(ret).encode('utf-8')))
    mc.put_object('output3', str(key), value_as_a_stream, len(bytes(str(ret).encode('utf-8'))))
    print("Reducer {} out of {}".format(node_number, nreducers))
    if node_number >= (nreducers  - 1):
        # Merge all the files
        full_data = []
        for i in range(0, nreducers-1):
            full_data.append(mc.get_object('output3', str(i)).read())
        value_as_a_stream = io.BytesIO(bytes(str(full_data).encode('utf-8')))
        mc.put_object('final', "result", value_as_a_stream, len(bytes(str(full_data).encode('utf-8'))))
    return req
