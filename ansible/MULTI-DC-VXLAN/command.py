import paramiko
import time
from datetime import datetime

# Dictionnaire des équipements (inventaire)
devices = {
    "arista": {
        "hosts": {
            "DC1-SPINE-1": {"ansible_host": "192.168.28.101", "ansible_httpapi_port": 443},
            "DC1-SPINE-2": {"ansible_host": "192.168.28.102", "ansible_httpapi_port": 443},
            "DC2-SPINE-1": {"ansible_host": "192.168.28.103", "ansible_httpapi_port": 443},
            "DC2-SPINE-2": {"ansible_host": "192.168.28.104", "ansible_httpapi_port": 443},
            "DC1-LEAF-1": {"ansible_host": "192.168.28.105", "ansible_httpapi_port": 443},
            "DC1-LEAF-2": {"ansible_host": "192.168.28.106", "ansible_httpapi_port": 443},
            "DC2-LEAF-1": {"ansible_host": "192.168.28.107", "ansible_httpapi_port": 443},
            "DC2-LEAF-2": {"ansible_host": "192.168.28.108", "ansible_httpapi_port": 443},
            "DC1-BORDER-LEAF-1": {"ansible_host": "192.168.28.109", "ansible_httpapi_port": 443},
            "DC1-BORDER-LEAF-2": {"ansible_host": "192.168.28.110", "ansible_httpapi_port": 443},
            "DC2-BORDER-LEAF-1": {"ansible_host": "192.168.28.111", "ansible_httpapi_port": 443},
            "DC2-BORDER-LEAF-2": {"ansible_host": "192.168.28.112", "ansible_httpapi_port": 443},
            "DC1-ISN-1": {"ansible_host": "192.168.28.113", "ansible_httpapi_port": 443},
            "DC1-ISN-2": {"ansible_host": "192.168.28.114", "ansible_httpapi_port": 443},
            "DC2-ISN-1": {"ansible_host": "192.168.28.115", "ansible_httpapi_port": 443},
            "DC2-ISN-2": {"ansible_host": "192.168.28.116", "ansible_httpapi_port": 443}
        },
        "vars": {
            "ansible_user": "admin",
            "ansible_httpapi_password": "admin"
        }
    }
}

# Liste des commandes à exécuter
COMMANDS = [
    "sh bgp evpn sum",
    "show interface vxlan1"
]


def ssh_run_command(host, username, password, commands):
    """Se connecte à un équipement et exécute les commandes spécifiées"""
    try:
        print(f"\n🔗 Connexion à {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, timeout=10)

        remote_conn = ssh.invoke_shell()
        time.sleep(1)

        output_total = ""
        for cmd in commands:
            remote_conn.send(cmd + "\n")
            time.sleep(2)
            output = remote_conn.recv(65535).decode('utf-8', errors='ignore')
            output_total += f"\n>>> {cmd}\n{output}"

        ssh.close()
        print(f"✅ Commandes exécutées sur {host}")
        return output_total

    except Exception as e:
        print(f"❌ Erreur sur {host} : {e}")
        return f"\n[ERREUR] Connexion échouée à {host} : {e}\n"


def main():
    creds = devices["arista"]["vars"]
    username = creds["ansible_user"]
    password = creds["ansible_httpapi_password"]

    log_filename = f"all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    with open(log_filename, "w") as logfile:
        logfile.write("==== RAPPORT GLOBAL SSH ====\n")
        logfile.write(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        logfile.write("============================\n\n")

        for name, info in devices["arista"]["hosts"].items():
            ip = info["ansible_host"]
            logfile.write(f"\n\n########## {name} ({ip}) ##########\n")
            print(f"\n=== {name} ({ip}) ===")

            result = ssh_run_command(ip, username, password, COMMANDS)
            logfile.write(result)
            logfile.write("\n" + "#" * 60 + "\n")

    print(f"\n📁 Tous les résultats sont enregistrés dans : {log_filename}")


if __name__ == "__main__":
    main()
