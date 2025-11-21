from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import os
import subprocess

# === CONFIGURATION ===
REMOTE_PATH = "/home/admin/"
BASE_CONF_PATH = "/mnt/c/Users/rrais/Desktop/Dev/EVE-GILGAMESSH/ansible/conf/MULTI-DC-VXLAN"
PLAYBOOK_PATH = "/mnt/c/Users/rrais/Desktop/Dev/EVE-GILGAMESSH/ansible/MULTI-DC-VXLAN/replace.yml"
SSH_USER, SSH_PWD = "admin", "admin"

# Inventaire IP + noms exacts
DEVICE_MAP = {
    "DC1-SPINE-1": "192.168.28.101",
    "DC1-SPINE-2": "192.168.28.102",
    "DC2-SPINE-1": "192.168.28.103",
    "DC2-SPINE-2": "192.168.28.104",

    "DC1-LEAF-1": "192.168.28.105",
    "DC1-LEAF-2": "192.168.28.106",
    "DC2-LEAF-1": "192.168.28.107",
    "DC2-LEAF-2": "192.168.28.108",

    "DC1-BORDER-LEAF-1": "192.168.28.109",
    "DC1-BORDER-LEAF-2": "192.168.28.110",
    "DC2-BORDER-LEAF-1": "192.168.28.111",
    "DC2-BORDER-LEAF-2": "192.168.28.112",
    
    "DC1-ISN-1": "192.168.28.113",
    "DC1-ISN-2": "192.168.28.114",
    "DC2-ISN-1": "192.168.28.115",
    "DC2-ISN-2": "192.168.28.116",
}


def ssh_scp_file(ip, user, pwd, local_file, remote_dir):
    """Envoie un fichier via SCP"""
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, username=user, password=pwd, look_for_keys=False)
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(local_file, remote_path=remote_dir)
    ssh.close()


def run_ansible_playbook(playbook_path):
    """Exécute un playbook Ansible"""
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
    """Envoi automatique du bon fichier .ios à chaque équipement"""
    sent = False

    for device, ip in DEVICE_MAP.items():
        # Exemple : DC1-SPINE-1 → DC1 / SPINE / 1.ios
        parts = device.split("-")
        dc = parts[0]
        role = "-".join(parts[1:-1])  # gère BORDER-LEAF et ISN
        number = parts[-1]
        ios_file = f"{number}.ios"

        # Gestion du dossier : ISN est maintenant dans son propre dossier
        local_conf = os.path.join(BASE_CONF_PATH, dc, role, ios_file)

        if not os.path.isfile(local_conf):
            print(f"⚠️ Fichier manquant : {local_conf}")
            continue

        print(f">> Envoi de {local_conf} vers {device} ({ip})")
        try:
            ssh_scp_file(ip, SSH_USER, SSH_PWD, local_conf, REMOTE_PATH)
            sent = True
        except Exception as e:
            print(f"❌ Erreur de transfert vers {device} ({ip}) : {e}")

    return sent


if __name__ == "__main__":
    # 1) Envoi des fichiers
    if main():
        print("✅ Tous les fichiers ont été envoyés !")

        # 2) Exécution du playbook Ansible
        print(f">> Exécution du playbook : {PLAYBOOK_PATH}")
        if run_ansible_playbook(PLAYBOOK_PATH):
            print("✅ Playbook exécuté avec succès !")
        else:
            print("❌ Erreur lors de l'exécution du playbook ! Vérifie le fichier et la connexion Ansible.")
    else:
        print("⚠️ Aucun fichier n'a été envoyé, le playbook n'a pas été exécuté.")

print(">>>> SCRIPT TERMINE <<<<")
