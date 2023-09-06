import os
import requests
import paramiko
from flask import Blueprint, render_template, request, redirect, url_for, flash


PORT=os.environ.get('REST_SRV_PORT')
edit_config = Blueprint('edit_config', __name__)

@edit_config.route('/editconfig/<ip_address_pos>', methods=['GET'])
def edit_custom(ip_address_pos):
    custom = _get_custom(ip_address_pos)
    return render_template('edit_custom.html', custom=custom)


def _get_custom(ip_address: str) -> str:
    client  = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip_address, username='root', password='toor')
    stdin,stdout,stderr=client.exec_command('cat /opt/fxpos/custom.cfg')
    outlines = stdout.readlines()
    res = ''.join(outlines)
    return res


""" 
transport = paramiko.Transport(("host", 22))
transport.connect(username = "username", password = "password")
sftp = paramiko.SFTPClient.from_transport(transport)

f = sftp.open("/path/to/remote/file", "wb")
f.write("hello,world")
f.close() """