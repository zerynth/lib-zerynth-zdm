zlib adm
========

[Project description goes here]






{
    "key":"#status"
}


{
    "version":1583154077258,
    "key":"#status",
    "value":{
        "current":{
            "@rpc1":{"t":1583146519651,"v":{"value 1":66,"value 2":126}},
            "@manifest":{"t":1583145725802,"v":["manifest","rpc1","rpc2"]},
            "my_dev_key":{"t":1583154076941,"v":442}
            
        },
        "expected":{
            "@manifest":{"t":1583145725480,"v":{}}
        }                    1583145725802
    },
    "change_id":"chan4pxuwanvc5gh"
}





{
    "version":1583154202856,
    "key":"@rpc1",
    "value":88,
    "change_id":"chan4pxv30o96msi"
}














user bearer token
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6ZXJ5bnRoIiwiaWF0IjoxNTgzMTU5ODY4LCJleHAiOjE1ODU3NTE4NjgsInVpZCI6Il9WWkJNZThJUzdHaXFqVnFWQmM5UUEiLCJqdGkiOiJpaV9QVnBjRVNHeWMyQWFEeWdLeS1nIiwibHRwIjpudWxsLCJvcmciOiIifQ.qimWHMOr3tGUmCsnRVoaAATHbfSccFQRZ8v7bbx9E1I




create workspace
{
    "workspace": {
        "id": "wks-4py3re4pbd3h",
        "name": "ws-test",
        "account_id": "_VZBMe8IS7GiqjVqVBc9QA",
        "description": "",
        "fleet": null,
        "created_at": "2020-03-02T14:40:39.083660102Z"
    }
}



create fleet
{
    "fleet": {
        "id": "flt-4py3ug8hou8e",
        "name": "f-test",
        "description": "",
        "workspace_id": "wks-4py3re4pbd3h",
        "devices": null,
        "created_at": "2020-03-02T14:41:36.226613204Z",
        "account_id": "_VZBMe8IS7GiqjVqVBc9QA"
    }
}




create device
{
    "device": {
        "id": "dev-4py3x1xk2rkf",
        "name": "ded-test",
        "fleet_id": "flt-4py3ug8hou8e",
        "created_at": "2020-03-02T14:42:24.85326415Z",
        "keys": null,
        "account_id": "_VZBMe8IS7GiqjVqVBc9QA"
    }
}


create device key
{
    "key": {
        "id": 1,
        "name": "key-test",
        "raw": "T5yha0sgvvwAkQC8RjcTazufEzC6+4zhucgva4paABI=",
        "type": "SYM256",
        "revoked": false,
        "device_id": "dev-4py3x1xk2rkf",
        "created_at": "0001-01-01T00:00:00Z",
        "account_id": "_VZBMe8IS7GiqjVqVBc9QA"
    }
}


jwt = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXYtNHB5M3gxeGsycmtmIiwidXNlciI6ImRldi00cHkzeDF4azJya2YiLCJrZXkiOjEsImV4cCI6MjUxNjIzOTAyMn0.a3H6XTmRRMAb0f1P6p4R9xyCZx4XiELbE18qJce07z0















C:\Users\Andrea\Documents\Z\LIB\zlib_adm>ztc compile -o fw.c . esp32_devkitc

[info]> Searching for C:\Users\Andrea\Documents\Z\LIB\zlib_adm\__builtins__.py

C:\Users\Andrea\Documents\Z\LIB\zlib_adm>ztc link --bc 1 --file fw.bin rwA-VBNIRSKWVJFC3cf8VA fw.c.vbo
[info]> File fw.bin saved

C:\Users\Andrea\Documents\Z\LIB\zlib_adm>certutil -encode fw.bin fw64.bin && findstr /v /c:- fw64.bin > data.b64
Input Length = 67416
Output Length = 92754
CertUtil: -encode command completed successfully.






target = esp32_devkitc
chip_id = c317fb6a0e46
vm = rwA-VBNIRSKWVJFC3cf8VA_r19.12.12_127fa64712e9199d10858c3dcc49b2e6ef4d1061_esp32-rtos


./ztc compile -o fw . esp32_devkitc

./ztc link --bc 0 --file fw0.bin rwA-VBNIRSKWVJFC3cf8VA fw.vbo
./ztc link --bc 1 --file fw1.bin rwA-VBNIRSKWVJFC3cf8VA fw.vbo


./zdm adm fota prepare wks-4py3re4pbd3h fw0.bin fw1.bin 3.1 rwA-VBNIRSKWVJFC3cf8VA

./zdm adm fota schedule 3.1 dev-4py3x1xk2rkf



5:35
./ztc link --bc 0 --file fw0.bin nlFt9EcbTX6_mXPvw7o2rQ fw.c.vbo
./ztc link --bc 1 --file fw1.bin nlFt9EcbTX6_mXPvw7o2rQ fw.c.vbo
5:35
./zdm adm fota prepare wks-4pnekzdmj66c fw0.bin fw1.bin 6.3 nlFt9EcbTX6_mXPvw7o2rQ
5:35
./zdm adm fota schedule 6.3 dev-4pnefulyx2bn


"C:\Program Files\Zerynth\python\python.exe" C:\Users\Andrea\zerynth2\dist\r2.3.3\ztc\zdm.py adm fota all wks-4py3re4pbd3h