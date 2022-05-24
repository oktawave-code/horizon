import subprocess
from uritools import urisplit

def call_proc(cmd):
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return output

def filter_output(output, host):
    o_filter = ""
    for line in output.stdout:
        o_filter = o_filter + line.decode('utf-8')

    return_data = "%s" % host + " " + o_filter
    return return_data

def ping(url):
    parts = urisplit(url)
    host = parts.host #parsedUrl.netloc
    cmd = "ping -c 4 %s" % host
    output = call_proc(cmd)
    return_data = filter_output(output, host)
    return return_data
