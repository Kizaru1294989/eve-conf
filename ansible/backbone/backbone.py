from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import os
import subprocess

# Pré-configuration
REMOTE_PATH     = "/home/cvpadmin/"
CONF_PATHS      = [
    "/mnt/c/Users/rrais/Desktop/Dev/EVE-GILGAMESSH/ansible/conf/backbone/RR",
    "/mnt/c/Users/rrais/Desktop/Dev/EVE-GILGAMESSH/ansible/conf/backbone/PE",
    "/mnt/c/Users/rrais/Desktop/Dev/EVE-GILGAMESSH/ansible/conf/backbone/P",
]
NETWORK_PREFIX   = "192.168.28."
IP_OFFSET_START = 49    # démarrage à .51
SSH_USER, SSH_PWD = "cvpadmin", "Exaprobe1234"
PLAYBOOK_PATH    = "/mnt/c/Users/rrais/Desktop/Dev/EVE-GILGAMESSH/ansible/backbone/replace.yml"


def ssh_scp_file(ip, user, pwd, local_file, remote_dir):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, username=user, password=pwd, look_for_keys=False)
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(local_file, remote_path=remote_dir)
    ssh.close()


def run_ansible_playbook(playbook_path):
    # Change de répertoire vers celui du playbook
    playbook_dir = os.path.dirname(playbook_path)
    playbook_file = os.path.basename(playbook_path)
    try:
        subprocess.run(
        ["ansible-playbook", "-i", "hosts.json", playbook_file],
        cwd=playbook_dir,
        check=True,
        )

        return True
    except subprocess.CalledProcessError:
        return False


def main():
    current_offset = IP_OFFSET_START
    sent = False

    for base_path in CONF_PATHS:
        if not os.path.isdir(base_path):
            print(f"⚠️ Le chemin {base_path} n'existe pas, on passe.")
            continue

        folders = sorted(
            [d for d in os.listdir(base_path) if d.isdigit()],
            key=lambda x: int(x)
        )
        for folder in folders:
            current_offset += 1
            ip = NETWORK_PREFIX + str(current_offset)
            local_conf = os.path.join(base_path, folder, "conf.txt")

            if not os.path.isfile(local_conf):
                print(f"⚠️ {local_conf} introuvable, skip {ip}")
                continue

            print(f">> Envoi vers {ip} ← {local_conf}")
            try:
                ssh_scp_file(ip, SSH_USER, SSH_PWD, local_conf, REMOTE_PATH)
                sent = True
            except Exception as e:
                print(f"❌ Erreur SSH/SCP pour {ip} : {e}")

    return sent


if __name__ == "__main__":
    # 1) Envoi des fichiers
    if main():
        print("✅ Envoi Validé !")

        # 2) Exécution du playbook Ansible
        print(f">> Exécution du playbook : {PLAYBOOK_PATH}")
        if run_ansible_playbook(PLAYBOOK_PATH):
            print("✅ Playbook exécuté avec succès !")
        else:
            print("❌ Erreur lors de l'exécution du playbook ! Vérifie ton playbook et la connexion Ansible.")
    else:
        print("⚠️ Aucun fichier envoyé, le playbook n'a pas été exécuté.")

# DEBUG: fin de script
print(">>>> SCRIPT TERMINE <<<<")
