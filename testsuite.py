# 0 - Secure Firmware (if available)
sfw_vm = False
new_exception(TTTException, Exception)
sfw = None

try:
    import sfw
    sfw.watchdog(0, 10000)
    sfw.kick()
    sfw_vm = True
except Exception:
    pass


# 1- IMPORTS
import streams
import threading
import json
import mcu
import gc


# 2 - INIT VARIABLES
serial = streams.serial()
kick_wd = True
gc.enable(500)

def _reset():
    mcu.reset()


commands = {
    "reset": _reset
}


def add_command(fn, name="run"):
    commands[name] = fn


# 4 - RUN DISPATCHER
ser_lock = threading.Lock()
def send(*obj):
    ser_lock.acquire()
    print(*obj)
    # print("- "*10)
    ser_lock.release()


def result(result):
    send({"ok": True, "result": result})


def read_cmd():
    # Get a line from serial port
    # print("read")
    if serial.available():
        # print("avail")
        line = serial.readline().strip(' \n')
        cmd = line.split(' ')
    
        # Split command name (first word) from arguments
        method = cmd[0]
        args = []
        for raw_arg in cmd[1:]:
            # Try to parse a string argument
            if raw_arg:
                if method == 'set_flow':
                    try:
                        # float
                        args.append(float(raw_arg))
                        continue
                    except ValueError:
                        pass
                else:
                    try:
                        # 1- JSON
                        args.append(json.loads(raw_arg))
                        continue
                    except JSONError:
                        pass
                    try:
                        # 2 - Integer
                        args.append(int(raw_arg))
                        continue
                    except ValueError:
                        pass
                # 3 (fallback) - String
                args.append(raw_arg)
        return method, args
    else:
        # print("sleep 100")
        sleep(90)
        raise TTTException

def start():
    # print("")
    # print("BOARD READY")
    while True:
        try:
            if sfw_vm and kick_wd:
                sfw.kick()
        
            cmd, args = read_cmd()
            send("TESTING:", cmd,"|", args)
            
            if cmd not in commands:
                result = ">> Invalid command name: %s" % cmd
            else:
                # print(args)

                result = commands[cmd](*args)
                
        except TTTException:
            # i = gc.info()
            # print(i[1], i[-1])
            continue
        except Exception as e:
            result = ">> Exception: %s" % str(e)
        
        # finally send the output
        send("RESULT:",result)
        send("- "*15)

def stop_wd():
    global kick_wd
    kick_wd = False