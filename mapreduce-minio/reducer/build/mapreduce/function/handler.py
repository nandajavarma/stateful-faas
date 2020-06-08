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
    obj = mc.stat_object(BUCKET, FILENAME)
    length = get_chunk_size(obj.size)
    offset = 0
    for count in range(1, NMAPPERS):
        print("\n Offset - {}\n".format(offset))
        data = mc.get_partial_object(BUCKET, FILENAME, offset, length)
        for d in data:
            print(d)
        offset = offset + length
    return req
