#!/usr/bin/env python3

import subprocess as sp
import os
import shlex
from console import fg, bg, fx
import click
import datetime as dt
from configparser import ConfigParser
import socket


user_glob = True


def is_int(n):
    if str(n).find(".")>=0:  return False
    if n is None:return False
    try:
        float_n = float(n) # 0.0
        int_n = int(float_n) #0.0
    except ValueError:
        return False
    else:
        return float_n == int_n


def verify_files( justprint=False):
    ok = True
    #FIS = ["~/.config/influxdb/username_local_admin",
    #    "~/.config/influxdb/password_local_admin",
    #    "~/.config/influxdb/username_local",
    #    "~/.config/influxdb/password_local",
    #    "~/.config/influxdb/server_local"]
    FIS = ["~/.config/influxdb/totalconfig.conf"]
    for i in FIS:
        if justprint:
            print( i)
        else:
            FF = os.path.expanduser(i)
            if not os.path.exists(FF):
                ok = False
                print(f"X... {FF} doesnt exist")
    return ok

def get_user_pass():
    global user_glob
    user = user_glob # must be set
    FIS = ["~/.config/influxdb/totalconfig.conf"]

    config = ConfigParser()
    config.read( os.path.expanduser(FIS[0]) )
    #print( dict(config)  )
    u, p, s = None, None, None
    if "influx local" in config.sections():
        if user:
            u = config["influx local"]['username']
            p = config["influx local"]['password']
            s = config["influx local"]['server']
        else:
            u = config["influx local"]['username_admin']
            p = config["influx local"]['password_admin']
            s = config["influx local"]['server']
        #print(u, p, s)
    return u, p, s
    # #print(f"D... user in gup is {user}")
    # u, p, d = None, None, None
    # if user:
    #     FIu = "~/.config/influxdb/username_local"
    #     FIp = "~/.config/influxdb/password_local"
    #     FIu = os.path.expanduser(FIu)
    #     FIp = os.path.expanduser(FIp)
    #     if os.path.exists(FIu) and os.path.exists(FIp):
    #         with open(FIu) as f:
    #             res = f.readlines()
    #         u = res[0].strip()
    #         with open(FIp) as f:
    #             res = f.readlines()
    #         p = res[0].strip()
    #         d = "test"
    #     # FI = "~/.influx_userpassdb"
    #     # FI = os.path.expanduser(FI)
    #     # with open(FI) as f:
    #     #     res = f.readlines()
    #     # u = res[0].strip()
    #     # p = res[1].strip()
    #     # d = res[2].strip()
    # else:
    #     FIu = "~/.config/influxdb/username_local_admin"
    #     FIp = "~/.config/influxdb/password_local_admin"
    #     FIu = os.path.expanduser(FIu)
    #     FIp = os.path.expanduser(FIp)
    #     if os.path.exists(FIu) and os.path.exists(FIp):
    #         with open(FIu) as f:
    #             res = f.readlines()
    #         u = res[0].strip()
    #         with open(FIp) as f:
    #             res = f.readlines()
    #         p = res[0].strip()
    #         d = "test"
    return u, p, d

# def get_local_machine():
#     """
#     Sometimes:   -host  www.xxx.com  is needed  with --ssl
#     # -host 127.0.0.1
#     # --ssl -host http://www.ccom:8086
#     """
#     m = None
#     FIm = "~/.config/influxdb/server_local"
#     FIm = os.path.expanduser(FIm)
#     if os.path.exists(FIm):
#         with open(FIm) as f:
#             res = f.readlines()
#         m = res[0].strip()
#         if m.find("https://") >= 0:
#             m = m.replace("https://", "")
#         elif m.find("http://") >= 0:
#             m = m.replace("http://", "")
#         elif m.find(":8086") >= 0:
#             m = m.replace(":8086", "")
#         if m.find("/") >= 0:
#             m = m.replace("/", "")

#     return m


# ============================================================
#  check if influx active
# ------------------------------------------------------------
def is_infl_active():
    CMD = f"systemctl is-active influxd"
    CMDx = shlex.split(CMD)
    result = sp.run(CMDx, capture_output=True, text=True )
    if result.returncode != 0:
        print("!...  PROBLEM with execution", CMDx)
        ok = False
    else:
        print("i... influxd seems to  be : ", result.stdout)



# ================================================================================
#          CALL  COMMAND
# --------------------------------------------------------------------------------
def call_cmd(CMD2, database=None, fromdb=None, todb=None, silent=False, format="", rfc=False):
    u, p, s = get_user_pass()
    m = s#get_local_machine()
    CMD = ""
    ssl = ""
    rfc3339 = ""
    if rfc:
        rfc3339 = "-precision rfc3339"
    if not is_int(m.split(".")[-1]):
        ssl = "--ssl"
    if database is None:
        CMD = f"influx {rfc3339} -username '{u}' -password '{p}' {ssl} -host {m} -execute '{CMD2}' {format}"
    else:
        CMD = f"influx {rfc3339} -username '{u}' -password '{p}'  {ssl} -host {m}  -database {database} -execute \"{CMD2}\" {format}"
        #print(CMD)
    CMDx = shlex.split(CMD)
    result = sp.run(CMDx, capture_output=True, text=True )
    if result.returncode != 0:
        print("!...  CMD :(=", CMDx, "#")
        ok = False
    else:
        if not silent:
            print(fg.dimgray, f"{result.stdout}", fg.default)
    return result.stdout


# ================================================================================
# EXPORT                separate call
# --------------------------------------------------------------------------------

# def export_measurement(m1, db1, silent=False):
#     print(fg.blue, f"export new measurement {m1} to {db1} ", fg.default)
#     u, p, _ = get_user_pass()
#     m = get_local_machine()
#     now = dt.datetime.now().strftime("%Y%m%d_%H%M")
#     outfilename = f"export_{db1}_{m1}_{now}.csv"
#     CMD = ""
#     ssl = ""
#     if not is_int(m.split(".")[-1]):
#         ssl = "--ssl"
#     #
#     CMD = f"influx -username '{u}' -password '{p}'  {ssl} -host {m}  -database {db1} -execute 'SELECT * FROM {m1}' -format csv"
#     #
#     with open(outfilename, "w") as f:
#         sp.run(shlex.split(CMD), stdout=f)
#     return "ok"

def export_measurement(m1, db1, silent=False):
    """
    per parts
    """
    import csv
    u, p, s = get_user_pass()
    m = s#get_local_machine()
    offset = 0
    limit = 1_000_000
    now = dt.datetime.now().strftime("%Y%m%d_%H%M")
    ssl = ""
    if not is_int(m.split(".")[-1]):
        ssl = "--ssl"
    pg = 0
    hostname = socket.gethostname()
    while True:
        pg += 1
        outfilename = f"export_{hostname}_{db1}_{m1}_{now}_{pg:02}.csv"
        print(f"\n{fg.yellow}i... saving {outfilename} {fg.default}")
        CMD = f"influx -username '{u}' -password '{p}' {ssl} -host {m} -database {db1} -execute 'SELECT * FROM {m1} ORDER BY time ASC LIMIT {limit} OFFSET {offset}' -format csv"
        result = sp.run(shlex.split(CMD), capture_output=True, text=True)
        if not result.stdout.strip():
            break
        with open(outfilename, "w") as f:
            f.write(result.stdout)
        offset += limit
    return "ok"
# ================================================================================
# backup                 separate call
# --------------------------------------------------------------------------------

def backup_portable(PATH):
    print(fg.blue, f"backing up", fg.default)
    CMD = f"influxd backup -skip-errors -portable  {os.path.expanduser(PATH)}/ "
    CMD = f"influxd backup  -portable  {os.path.expanduser(PATH)}/ "
    CMDx = shlex.split(CMD)
    with open("/tmp/mcdebu.log", "a") as f:
        f.write("\n\n")
        f.write(CMD + "\n")
        f.write("CMDx\n")
        f.write(f"{CMDx}\n")
    sp.run(CMD, shell=True)
    #---------------------------------------------------



def show_databases():
    print(fg.blue, "... showing database ...", fg.default)
    res = call_cmd( " SHOW DATABASES " )
    #print(res)
    res = res.split("\n")[3:]
    print(res, ":")
    res = [ x for x in res if (len(x) > 0) and (x[0] != "_") and (x[0] != "-")  and (x.find("name") < 0)and (x.find("i_am_") < 0)  ]
    print(res)
    return res

def create_database( db ):
    print(fg.blue, "creating database", fg.default)
    res = call_cmd( f"  CREATE DATABASE '{db}' " ).strip().split("\n")
    #print(res, ":")
    #res = [ x for x in res if (x[0] != "_") and (x[0] != "-")  and (x.find("name") < 0)and (x.find("i_am_") < 0)]
    print(res)

def drop_database( db ):
    print(fg.blue, "dropping database", fg.default)
    res = call_cmd( f"  DROP DATABASE '{db}' " ).strip().split("\n")
    #print(res, ":")
    #res = [ x for x in res if (x[0] != "_") and (x[0] != "-")  and (x.find("name") < 0)and (x.find("i_am_") < 0)]
    print(res)

def show_measurements(database):
    print(fg.blue, f"showing measurements @ {database}", fg.default)
    res = call_cmd( f"SHOW MEASUREMENTS  ", database=database)
    #
    res = res.split("\n")[3:]
    #print(res, ":")
    res = [ x for x in res if (len(x) > 0) and (x[0] != "_") and (x[0] != "-")  and (x.find("name") < 0)and (x.find("i_am_") < 0)  ]
    print(res)
    return res

def copy_measurement(m1, db1, db2, silent=False):
    if not silent:
        print(fg.blue, f"copy measurement {m1} from {db1} to {db2}", fg.default)
    CMD = f"SELECT * INTO {db2}..{m1} FROM {db1}..{m1} group by *"
    if not silent:
        print(CMD)
    res = CMD
    res = call_cmd( CMD, database=db2)
    if not silent:
        print(res)
    return res
    #res = call_cmd( f"SELECT * INTO {m1}..[{db2}] FROM {m1}..[{db1}] group by *", fromdb=db1, to_db=db2)
    #print(res)
#select * into Verhaeg_Energy..[measurement_name_destination] from Verhaeg_IoT..[measurement_name_source] group by *

def delete_measurement(m1, db1):
    print(fg.blue, f"delete measurement {m1} from {db1} ", fg.default)
    CMD = f"DROP MEASUREMENT {m1} "
    res = CMD
    res = call_cmd( CMD, database=db1)
    return res
    #res = call_cmd( f"SELECT * INTO {m1}..[{db2}] FROM {m1}..[{db1}] group by *", fromdb=db1, to_db=db2)
    #print(res)
#select * into Verhaeg_Energy..[measurement_name_destination] from Verhaeg_IoT..[measurement_name_source] group by *


# ================================================================================
# INSERT
# --------------------------------------------------------------------------------

def insert_new_measurement(m1, db1, silent=False):
    print(fg.blue, f"insert new measurement {m1} to {db1} ", fg.default)
    CMD = f"INSERT {m1},tag_key=tag_value  field_key=34"
    #res = CMD
    res = call_cmd( CMD, database=db1, silent=silent)
    return res


# ================================================================================
# COUNT
# --------------------------------------------------------------------------------

def count_measurement(m1, db1, silent=False):
    if not silent: print(fg.blue, f"count new measurement {m1} to {db1} ", fg.default)
    CMD = f"SELECT COUNT(*) FROM  {m1}"
    #res = CMD
    res = call_cmd( CMD, database=db1, silent=silent)
    return res


def show_measurement_newest_sample(m1, db1, silent=False, prepend=None, time_restrict=None):
    if not silent: print(fg.blue, f"newest measurement {m1} from {db1} ", fg.default)
    CMD = ""
    if time_restrict is None:
        CMD = f"SELECT * FROM {m1} ORDER BY time DESC LIMIT 10"
    else:
        #time_restrict = datetime.datetime.now().isoformat() + "Z"  # ISO 8601 format with Zulu time
        CMD = f"SELECT * FROM {m1} WHERE time > '{time_restrict}' ORDER BY time DESC LIMIT 10"
    res = call_cmd( CMD, database=db1, silent=silent, rfc=True)
    #res = res.split("\n")[3:]
    #res = [x for x in res if len(x) > 0] # last line
    #if not silent: print(res)
    if prepend != None:
        return f"{prepend}\n{res}"
    return res

def show_measurement_newest(m1, db1, silent=False):
    if not silent: print(fg.blue, f"newest measurement {m1} from {db1} ", fg.default)
    CMD = f"SELECT * FROM {m1} ORDER BY time DESC LIMIT 1"
    res = call_cmd( CMD, database=db1, silent=silent)
    if len(res.strip()) < 1:return None
    res = res.split("\n")[3:]
    res = [x for x in res if len(x) > 0] # last line
    if len(res) < 1:
        print("X... no data here/newest")
        return None
    res = res[0].split()[0] # t
    res = int(res)
    if not silent: print(res)
    timen = dt.datetime.fromtimestamp(res / 1e9)
    if not silent: print(timen)
    now = dt.datetime.now()
    age = (now - timen)
    if not silent: print("AGE", age)
    sage = str(age)[:-7]
    sdate = str(timen)[:-7]
    if not silent: print("AGE", age, "    ",  sage, sdate)
    return timen


def show_measurement_oldest(m1, db1, silent=False):
    if not silent: print(fg.blue, f"oldest measurement {m1} from {db1} ", fg.default)
    CMD = f"SELECT * FROM {m1} ORDER BY time ASC LIMIT 1"
    res = call_cmd( CMD, database=db1, silent=silent)
    if len(res.strip()) < 1:return None
    res = res.split("\n")[3:]
    res = [x for x in res if len(x) > 0] # last line
    if len(res) < 1:
        print("X... No Data here/oldest")
        return None
    res = res[0].split()[0] # t
    res = int(res)
    if not silent: print(res)
    timen = dt.datetime.fromtimestamp(res / 1e9)
    if not silent: print(timen)
    now = dt.datetime.now()
    age = (now - timen)
    sage = str(age)[:-7]
    sdate = str(timen)[:-7]
    if not silent: print("AGE", age, "    ", sage, sdate)
    return timen

def show_measurement_newest_oldest(m1, db1, silent=False):
    """
    """
    tn = show_measurement_newest(m1, db1, silent=True)
    to = show_measurement_oldest(m1, db1, silent=True)
    aaa = ""
    #aaa = count_measurement(m1, db1, silent=silent)
    #aaa = f"COUNT  = {aaa[3:].split()[-1]} "
    #
    if tn is None or to is None: return None
    period = str(tn - to)
    if period[-7] == ".":period = period[:-7]
    now = dt.datetime.now()
    age = now - tn
    sage = str(age)[:-7]
    ID = f" measurement {m1} of {db1}"
    # remove fractions if present
    stn = str(tn)
    if len(stn) > 21: stn = stn[:-7]
    sto = str(to)
    if len(sto) > 21: sto = sto[:-7]
    res = f"\n{ID}\n--------------------------\nAGE    = {sage}   \nPERIOD = {period}\nNEWEST = {stn}\nOLDEST = {sto}\n{aaa}"
    if not silent: print(res)
    return res



@click.command()
@click.argument('command')
@click.option('--name', '-n')
@click.option('--fromdb', '-f', default=None)
@click.option('--todb', '-t', default=None)
@click.option('--user', '-u', count=True)
def main(command, name, fromdb, todb, user):
    global user_glob
    user_glob = user
    print("Hi")
    if command == "sd":
        show_databases()
    elif command == "cd":
        if name is None:
            print("X... name is none")
        create_database( name )
    elif command == "sm":
        if name is None:
            print("X... name is none")
            return
        show_measurements( name )
    elif command == "cm":
        if name is None or fromdb is None or todb is None:
            print("X... name or db is none")
            return
        copy_measurement( name, fromdb, todb )
    elif command == "sn":
        if name is None or fromdb is None:
            print("X... name or db is none")
            return
        show_measurement_newest( name, fromdb )
    elif command == "so":
        if name is None or fromdb is None:
            print("X... name or db is none")
            return
        show_measurement_oldest( name, fromdb )
    elif command == "sno":
        if name is None or fromdb is None:
            print("X... name or db is none")
            return
        show_measurement_newest_oldest( name, fromdb )
    elif command == "sns":
        if name is None or fromdb is None:
            print("X... name or db is none")
            return
        show_measurement_newest_sample( name, fromdb )
    elif command == "im":
        if name is None or todb is None:
            print("X... name or db is none")
            return
        insert_new_measurement( name, todb )
    elif command == "bp":
        backup_portable('~/INFL' )

if __name__ == "__main__":
    main()
