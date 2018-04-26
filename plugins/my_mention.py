from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply
import subprocess
from prettytable import PrettyTable


def grep_gpustatus(ip):
    sshcmd = "ssh -o \"ConnectTimeout 1\" -oProxyCommand='ssh -W %h:%p gatelabo' "
    #sshcmd = "ssh -oProxyCommand='ssh -W %h:%p gatelabo' "
    cmd = sshcmd + ip + " \"nvidia-smi --query-gpu=utilization.gpu --format=csv, noheader, nounits\""
    status = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    l = []
    while True:
        line = status.stdout.readline()
        l.append(line.decode('utf-8'))
        
        if not line and status.poll() is not None:
            break

    if l[0] == '':
        l.append("Nan")
    percentage = l[1].replace('\n', '')

    return percentage

def grep_cpustatus(ip):
    cpucmd = "\"mpstat\""
    sshcmd = "ssh -o \"ConnectTimeout 1\" -oProxyCommand='ssh -W %h:%p gatelabo' "
    cmd = sshcmd + ip + cpucmd
    status = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    l = []

    while True:
        line = status.stdout.readline()
        l.append(line.decode('utf-8'))

        if not line and status.poll() is not None:
            break

    print(l)

    if l[0] == '':
        stat = "Nan"

    else:
        _cpustatus = l[-2].replace('\n', '')
        cpustatus = _cpustatus.split()
        cstat = cpustatus[-1]
        _stat = 100.0 - float(cstat)
        stat = f"{_stat:.2f}" + "%"

    return stat


@respond_to('使用状況')
def mention_func(message):
    with open("./iplist.txt", "r") as f:
        tmp = f.readlines()
        IPs = list(map(lambda ip: ip.replace('\n', ''), tmp))

    print(IPs)
    gpustatus_dict = {}
    
    table = PrettyTable(['PC name', 'CPU status', 'GPU status'])
    table.padding_width = 1
    
    for ip in IPs:

        gpustat = grep_gpustatus(ip)
        cpustat = grep_cpustatus(ip)        

        table.add_row([ip, cpustat, gpustat])

    message.channel.upload_content('GPUstatus.txt', table)
