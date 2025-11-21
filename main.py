from paramiko import SSHClient
from scp import SCPClient
import os
import subprocess

def run_ansible_playbook(playbook_path):
    os.chdir(os.path.dirname(playbook_path))
    try:
        subprocess.run(["ansible-playbook", os.path.basename(playbook_path)], check=True)
    except subprocess.CalledProcessError as e:
        return False
    else:
        return True

def main():
    print(f'Processing Start')
    playbook = run_ansible_playbook("/home/rais/Arista_Nexus_Backbone/Ansible/fabric/replace.yml")
    return playbook

if __name__ == '__main__':
    main()
