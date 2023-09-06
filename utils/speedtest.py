import paramiko
from models.db_model import Shops

class Speedtest:
    def __init__(self, shop_number) -> None:
        self.shop_number = shop_number
        self.shop = Shops.query.filter(Shops.shop_number==self.shop_number).one()

    def run_speedtest(self):
        ip = f"192.168.{self.shop.base_ip}.100"
        return self._speedtest_by_ssh(ip)

    def _speedtest_by_ssh(self, ip):
        print(f"Wait for speedtest at {ip} about 25 sec....")
        ssh  = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, 'admin', 'vldh_mikrotik')
        stdin, stout, sterr = ssh.exec_command("/tool speed-test address=192.168.1.4 test-duration=5")
        lines = stout.readlines()
        reply = []
        for line in lines[-10:]:
            reply.append(line[:-2].strip())

        return reply