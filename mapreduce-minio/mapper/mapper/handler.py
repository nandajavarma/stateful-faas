import os

from minio import Minio

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
    print(req)
    print(dir(req))
        # data = mc.get_partial_object(BUCKET, FILENAME, offset, length)
        # print(data.read())
    # r = requests.get("http://" + gateway_hostname + ":8080/function/mapper", data=data)
    # if r.status_code != 200:
        # sys.exit("Error with mapper, expected: %d, got: %d\n" % (200, r.status_code))
    return req
