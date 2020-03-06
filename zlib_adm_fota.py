import fota
import vm
import ssl
import requests
# import flash
import json
import mcu



next_bcaddr = 0
bcsize = 0
wsize = 0

def _stream_cb(content):
    global next_bcaddr
    global wsize
    fota.write_slot(next_bcaddr+wsize,content)
    wsize+=len(content)
    print("> Block size",len(content), wsize)




def get_record():
    record = {
        'vm_uid':   None,
        'bc_slot':  None,
        'vm_slot':  None
    }
    try:
        record['vm_uid'] = vm.info()[0]
        fota_record = fota.get_record()
        if fota_record[4]==fota_record[5] and fota_record[2]==fota_record[3]:
            record['bc_slot'] = fota_record[4]
            record['vm_slot'] = fota_record[2]

    except Exception as e:
        print("zlib_adm_fota.get_record fota unsupported")
        record['bc_slot'] = 'fota unsupported'
        record['vm_slot'] = 'fota unsupported'

    return record


def handle_fota(data):
    print("zlib_adm_fota.handle_fota")
    ret = update(data)

    if ret:
        print("zlib_adm_fota.handle_fota fw written correctly")
        test()
        return True, "resetting"
    else:
        print("zlib_adm_fota.handle_fota fw NOT written correctly")
        return False, "errors"


def test():
    record = fota.get_record()
    #new bytecode, current vm
    next_bc = 1-record[4]
    fota.attempt(next_bc,record[1])

def update(data):
    global next_bcaddr
    global bcsize
    print("zlib_adm_fota.update")

    fw_url = data['fw_url']

    # bc_slot = data['fw_metadata']['bc_slot']
    # vm_slot = data['fw_metadata']['vm_slot']

    # setup
    # awscert = __lookup(SSL_CACERT_BALTIMORE_CYBERTRUST_ROOT)
    # ctx = ssl.create_ssl_context(cacert=awscert,options=ssl.CERT_REQUIRED|ssl.SERVER_AUTH)

    # awscert = __lookup(SSL_CACERT_BALTIMORE_CYBERTRUST_ROOT)
    # ctx = ssl.create_ssl_context(cacert=awscert,options=ssl.CERT_REQUIRED|ssl.SERVER_AUTH)


    record = fota.get_record()

    # TODO insert chunk size
    chunk = 1024

    next_bc = 1-record[4]

    next_bcaddr = fota.find_bytecode_slot()
    # TODO insert fw_size

    bcsize = 200000
    # bcsize = data["fw_size"]
    print("free bc slot is:", next_bc)
    print("zlib_adm_fota.update erasing flash for bc, size", bcsize)
    fota.erase_slot(next_bcaddr, bcsize)
    print("zlib_adm_fota.update flash erased")

    # url = fw_url+str(next_bc)
    url = fw_url+str(next_bc)

    ctx = ssl.create_ssl_context(options=ssl.CERT_NONE)
    print("get", url)
    try:
        rr = requests.get(url, ctx=ctx, stream_callback=_stream_cb, stream_chunk=chunk)
        print("http get request done")
    except Exception as e:
        print("zlib_adm_fota.update get failed", e)
        return False
    # TODO insert size check
    # TODO insert checksum check
    # chk = fota.checksum_slot(next_bcaddr,bcsize)

    fota.close_slot(next_bcaddr)

    return True

def is_fota_possible(metadata):
    # to be called before the fota attempt
    # compare current status with fota request. return (True, msg) if fota request is possible (bc slot differs), (False, msg) otherwise
    print("is fota possible")
    try:
        current_record = get_record()
        print("got record")


        # TODO check fw_metadata 'vm_feature', 'vm_version', 'vm_target'
        # arg: {fw_url:https://api.adm.zerinth.com/data/workspace/wks-4pnekzdmj66c/firmware/1.2.1/download?index=, fw_size:0, fw_version:1.2.1, fw_metadata:{vm_feature:4ba8b122c38ec6b6c04191cdf935c3efbdb3a32d, vm_version:r20.02.06}}


        # if (metadata['vm_uid'] is None) or (metadata['vm_uid'] != current_record['vm_uid']):
        #     print("invalid vm_uid")
        #     return False, 'invalid vm_uid'

        # if (current_record['bc_slot'] is None) or (metadata['bc_slot']==current_record['bc_slot']):
        #     print("invalid bc_slot")
        #     return False, 'invalid bc_slot'

        # check vm slot ???

    except Exception as e:
        print(e)
        return False, 'exception'

    print("fota possible")
    return True, ""


def is_fota_valid():
    # to be colled after the fota attempt
    # compare current status with fota request. return True if fota succeded (bc slot are same", false otherwise

    try:
        record = fota.get_record()

        # if current != from last working it means that device's running the new firmware
        if record[4] !=record[5]:
            #check that fota is for current slot
            #and that it is coming from previous slot
            return True,""
    except Exception as e:
        print(e)
        return False,"fota error"
    return False,"fota failed"


# ???
def finalize_fota():
    fota.accept()


def supported():
    # return True if fota is supported by vm, false otherwise
    return True