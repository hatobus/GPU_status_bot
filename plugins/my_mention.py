from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply
import subprocess
from prettytable import PrettyTable


@respond_to('使用状況')
def mention_func(message):
    with open("./iplist.txt", "r") as f:
        tmp = f.readlines()
        IPs = list(map(lambda ip: ip.replace('\n', ''), tmp))

    print(IPs)
    gpustatus_dict = {}
    for ip in IPs:
        cmd = ""
        sshcmd = "ssh -oProxyCommand='ssh -W %h:%p gatelabo' "
        cmd = sshcmd + ip + " \"nvidia-smi --query-gpu=utilization.gpu --format=csv, noheader, nounits\""
        #cmd = "ls"
        status = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        l = []
        while True:
            line = status.stdout.readline()
            l.append(line.decode('utf-8'))

            if not line and status.poll() is not None:
                break

        print(l)
        percentage = l[1].replace('\n', '')
        gpustatus_dict[ip] = percentage

    table = PrettyTable(['PC name', 'GPU status'])
    table.padding_width = 1

    for k, v in gpustatus_dict.items():
        table.add_row([k, v])

    message.channel.upload_content('GPUstatus.txt',table)
