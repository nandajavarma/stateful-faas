from minio import Minio

NMAPPERS = 3

def get_chunk_size(data_size):
    chunksize = data_size // NMAPPERS
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
    obj = mc.stat_object("files", "sample.csv")
    print(get_chunk_size(obj.size))
    
    return req
