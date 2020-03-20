import fota
import vm
import ssl
import requests

next_bcaddr = 0
wsize = 0


def _stream_cb(content):
    global next_bcaddr
    global wsize
    fota.write_slot(next_bcaddr + wsize, content)
    wsize += len(content)
    # print("> Block size",len(content), wsize)


def handle_fota(data):
    ret, msg = update(data)
    if ret:
        test()
        return True, "done, resetting"
    else:
        print("zlib_zdm_fota.handle_fota fw NOT written correctly")
        return False, msg


def test():
    record = fota.get_record()
    next_bc = 1 - record[4]
    fota.attempt(next_bc, record[1])


def update(data):
    global next_bcaddr

    record = fota.get_record()
    next_bc = 1 - record[4]

    next_bcaddr = fota.find_bytecode_slot()
    bcsize = data["fw_info"][next_bc]["fw_size"]
    # print("zlib_zdm_fota.update erasing flash for bc, size:", bcsize)
    fota.erase_slot(next_bcaddr, bcsize)
    # print("zlib_zdm_fota.update flash erased")

    url = data['fw_url'] + str(next_bc)
    # print("zlib_zdm_fota.update getting fw from:", url)

    # TODO add chunk size in data["metadata"]?
    chunk = 1024
    # TODO add zdm specific ssl context
    ctx = ssl.create_ssl_context(options=ssl.CERT_NONE)

    try:
        rr = requests.get(url, ctx=ctx, stream_callback=_stream_cb, stream_chunk=chunk)
    except Exception as e:
        print("zlib_zdm_fota.update failed http get", e)
        return False

    if bcsize != wsize:
        print("zlib_zdm_fota.update failed bc size check")
        return False, "failed size check"

    chk = fota.checksum_slot(next_bcaddr, bcsize)
    checksum = data["fw_info"][next_bc]["fw_crc"]
    fota.close_slot(next_bcaddr)

    for i, b in enumerate(chk):
        k = int(checksum[i * 2:i * 2 + 2], 16)
        if k != b:
            print("zlib_zdm_fota.update failed checksum")
            return False, "failed checksum"

    return True, ''


def is_fota_possible(metadata):
    # to be called before the fota attempt
    # compare current status with fota request. return (True, msg) if fota request is possible (vm_target version and feature are ok), (False, msg) otherwise
    print("zlib_zdm_fota.is_fota_possible")
    try:
        # TODO check fw_metadata 'vm_feature', 'vm_version', 'vm_target'

        vm_info = vm.info()
        vm_uid = vm_info[0]
        vm_target = vm_info[1]
        vm_ver = vm_info[2]

        # if metadata['vm_target'] != vm_target:
        # print("zlib_zdm_fota.is_fota_possible fota not possible: wrong vm_target")
        # return False, 'invalid vm_target'
        if metadata['vm_version'] != vm_ver:
            print("zlib_zdm_fota.is_fota_possible fota not possible: wrong vm_version")
            return False, 'invalid vm_version'
        # if metadata['vm_feature'] != vm_uid:
        # print("zlib_zdm_fota.is_fota_possible fota not possible: wrong vm_feature")
        # return False, 'invalid vm_feature'

    except Exception as e:
        print("zlib_zdm_fota.is_fota_possible", e)
        return False, 'exception'

    return True, ""


def is_fota_valid():
    # to be called after the fota attempt
    # compare current status with fota request. return True if fota succeded , False otherwise

    try:
        record = fota.get_record()

        # if current != from last working it means that device's running the new firmware
        if record[4] != record[5]:
            # check that fota is for current slot (?)
            # and that it is coming from previous slot
            return True, ""
    except Exception as e:
        print("zlib_zdm_fota.is_fota_valid", e)
        return False, "exception"

    return False, "fota failed"


def finalize_fota():
    fota.accept()


def supported():
    # return True if fota is supported by vm, False otherwise
    try:
        # TODO check on vm feature?
        fota.get_record()
    except Exception as e:
        return False
    return True