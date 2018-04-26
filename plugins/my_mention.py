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

    print(l)
    return l

def grep_cpustatus(ip):
    cpucmd = "mpstat"
    status = subprocess.Popen(cpucmd, shell=True, stdout=subprocess.PIPE)
    l = []

    while True:
        line = status.stdout.readline()
        l.append(line.decode('utf-8'))

        if not line and status.poll() is not None:
            break

    _cpustatus = l[-2].replace('\n', '')
    cpustatus = _cpustatus.split()
    cstat = cpustatus[-1]

    return 100.0 - float(cstat)


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

        gpuline = grep_gpustatus(ip)
        cpustat = grep_cpustatus(ip)

        cpustat = f"{cpustat:.2f}" + "%"

        if gpuline[0] == '':
            gpuline.append("Nan")
        percentage = gpuline[1].replace('\n', '')
        

        table.add_row([ip, cpustat, percentage])

    message.channel.upload_content('GPUstatus.txt', table)
