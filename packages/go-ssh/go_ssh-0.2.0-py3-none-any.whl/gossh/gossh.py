# gossh.py
import argparse
import os
import socket
import keyring
import subprocess
from getpass import getpass
import datetime
import time
import sys
import paramiko

SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
APP_NAME = "gossh"
LOCAL_KEY_PATH = os.path.expanduser("~/.ssh/gossh_id_rsa")


def parse_ssh_config(path):
    hosts = []
    current = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('# Lan'):
                if ':' in line:
                    current['Lan'] = line.split(':', 1)[1].strip()
                else:
                    current['Lan'] = line.split(maxsplit=2)[2].strip() if len(line.split()) >= 3 else 'N/A'
                continue
            if line.startswith('#'):
                continue
            key, *value = line.split()
            value = ' '.join(value)
            if key.lower() == 'host':
                if current:
                    hosts.append(current)
                    current = {}
                current['Host'] = value
            else:
                current[key] = value
        if current:
            hosts.append(current)
    return hosts


def fuzzy_match(hosts, query, exact=False):
    if exact:
        return [h for h in hosts if query == h['Host']]
    q = query.lower()
    return [h for h in hosts if q in h['Host'].lower()]


def is_reachable(hostname, port, timeout=2.0):
    start = time.time()
    try:
        with socket.create_connection((hostname, port), timeout):
            latency = int((time.time() - start) * 1000)
            return True, latency, ""
    except Exception:
        return False, None, "No response (Connection timed out)"


def save_password():
    password = getpass("Enter SSH password: ")
    keyring.set_password(APP_NAME, "ssh_password", password)
    print("✅ Global password saved securely.")


def save_host_password(hostname):
    password = getpass(f"Enter SSH password for host '{hostname}': ")
    keyring.set_password(APP_NAME, f"{hostname}_password", password)
    print(f"✅ Password saved for {hostname}.")


def save_host_user(hostname):
    user = input(f"Enter SSH username for host '{hostname}': ").strip()
    keyring.set_password(APP_NAME, f"{hostname}_user", user)
    print(f"✅ Username saved for {hostname}.")


def get_password_for_host(hostname):
    pw = keyring.get_password(APP_NAME, f"{hostname}_password")
    if pw:
        return pw
    return keyring.get_password(APP_NAME, "ssh_password")


def get_user_for_host(host_entry):
    host_key = host_entry.get('Host')
    if 'User' in host_entry:
        return host_entry['User']
    user_from_keyring = keyring.get_password(APP_NAME, f"{host_key}_user")
    if user_from_keyring:
        return user_from_keyring
    print(f"❌ No username specified for host '{host_key}'. Please add 'User' in ~/.ssh/config or save one using --user.")
    sys.exit(1)


def generate_and_save_local_key():
    if os.path.exists(LOCAL_KEY_PATH):
        return False
    subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", LOCAL_KEY_PATH, "-N", ""], check=True)
    return True


def upload_public_key_via_paramiko(host_entry, password, debug=False):
    hostname = host_entry.get('Hostname') or host_entry.get('HostName') or host_entry.get('Host')
    username = get_user_for_host(host_entry)
    port = int(host_entry.get('Port', 22))
    pubkey_path = LOCAL_KEY_PATH + ".pub"
    if not os.path.exists(pubkey_path):
        return False

    with open(pubkey_path, 'r') as f:
        public_key = f.read().strip()

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=5)

        cmds = [
            'mkdir -p ~/.ssh',
            f'grep "{public_key}" ~/.ssh/authorized_keys || echo "{public_key}" >> ~/.ssh/authorized_keys',
            'chmod 700 ~/.ssh',
            'chmod 600 ~/.ssh/authorized_keys'
        ]
        for cmd in cmds:
            if debug:
                print(f"[cmd] {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            exit_code = stdout.channel.recv_exit_status()
            if debug:
                err = stderr.read().decode().strip()
                out = stdout.read().decode().strip()
                print(f"[exit:{exit_code}] {out or err}")

        client.close()
        return True
    except Exception as e:
        if debug:
            print(f"❌ Key upload failed: {e}")
        return False


def connect_via_paramiko(host_entry, password, debug=False):
    hostname = host_entry.get('Hostname') or host_entry.get('HostName') or host_entry.get('Host')
    username = get_user_for_host(host_entry)
    port = int(host_entry.get('Port', 22))

    new_key_created = generate_and_save_local_key()
    key_uploaded = upload_public_key_via_paramiko(host_entry, password, debug=debug)

    if debug:
        if new_key_created:
            print(f"🔑 New SSH key generated: {LOCAL_KEY_PATH}")
        if key_uploaded:
            print(f"📤 Public key uploaded to {hostname}")
        print(f"🔗 Connecting to {username}@{hostname}:{port}...")

    subprocess.call(["ssh", "-i", LOCAL_KEY_PATH, f"{username}@{hostname}", "-p", str(port)])


def main():
    parser = argparse.ArgumentParser(description="gossh - smart SSH connector with Paramiko & native ssh")
    parser.add_argument("query", nargs='?', help="Fuzzy or exact SSH host name")
    parser.add_argument("--pick", action="store_true", help="Pick manually from matches")
    parser.add_argument("--list", action="store_true", help="List all matched hosts and reachable status")
    parser.add_argument("--dry-run", action="store_true", help="Show which host would be connected to without connecting")
    parser.add_argument("--exact", action="store_true", help="Use exact host match instead of fuzzy")
    parser.add_argument("--save-pass", action="store_true", help="Save global SSH password securely")
    parser.add_argument("--pass", dest="save_pass_host", action="store_true", help="Save SSH password for this specific host")
    parser.add_argument("--user", dest="save_user_host", action="store_true", help="Save SSH username for this specific host")
    parser.add_argument("--debug", action="store_true", help="Show detailed debug output")

    args = parser.parse_args()

    if args.save_pass:
        save_password()
        return

    if not args.query:
        print("❌ Please provide a query (e.g., gossh beacon)")
        return

    if not os.path.exists(SSH_CONFIG_PATH):
        print(f"❌ SSH config file not found: {SSH_CONFIG_PATH}")
        return

    hosts = parse_ssh_config(SSH_CONFIG_PATH)
    matched = fuzzy_match(hosts, args.query, exact=args.exact)

    if not matched:
        print(f"❌ No match found for '{args.query}'")
        return

    if args.save_pass_host or args.save_user_host:
        if len(matched) > 1:
            print(f"** Multiple matches found:")
            for idx, h in enumerate(matched):
                print(f"{idx}. {h['Host']}")
            action = "password" if args.save_pass_host else "username"
            try:
                choice_input = input(f"Enter number of host to save {action} for: ").strip()
                choice = int(choice_input)
                if 0 <= choice < len(matched):
                    selected = matched[choice]
                else:
                    print("❌ Choice out of range.")
                    return
            except Exception:
                print("❌ Invalid choice or interrupted.")
                return
        else:
            selected = matched[0]

        hostname = selected.get('Host')
        if args.save_pass_host:
            save_host_password(hostname)
        if args.save_user_host:
            save_host_user(hostname)
        return

    if args.list:
        print("\n📋 Detailed report of matched hosts:\n")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        for idx, h in enumerate(matched):
            hostname = h.get('Hostname') or h.get('HostName') or h.get('Host')
            lan_ip = h.get('Lan', 'N/A')
            port = int(h.get('Port', 22))
            reachable, latency, reason = is_reachable(hostname, port)
            status = "\033[1;32m[OK]\033[0m" if reachable else "\033[1;31m[X]\033[0m"
            print(f"{idx}. {h['Host']}")
            print(f"   • Public IP   : {hostname}:{port}")
            print(f"   • Local IP    : {lan_ip}")
            print(f"   • Status      : {status}")
            if reachable:
                print(f"   • Latency     : {latency} ms")
            else:
                print(f"   • Reason      : {reason}")
            print(f"   • Checked at  : {now}\n")
        return

    password = get_password_for_host(matched[0]['Host'])
    if not password:
        print("* No saved password found for this host or globally. You can run with --save-pass or --pass to store it securely.")
        password = getpass("Enter SSH password: ")

    if args.pick:
        for idx, h in enumerate(matched):
            hostname = h.get('Hostname') or h.get('HostName') or h.get('Host')
            lan_ip = h.get('Lan', 'N/A')
            port = int(h.get('Port', 22))
            reachable, latency, _ = is_reachable(hostname, port)
            status = "\033[1;32m[OK]\033[0m" if reachable else "\033[1;31m[X]\033[0m"
            print(f"{idx}. {status} {h['Host']} ({hostname}:{port}) ({lan_ip})")
        try:
            choice = int(input("\nChoose a number to connect: "))
            if 0 <= choice < len(matched):
                selected = matched[choice]
                hostname = selected.get('Hostname') or selected.get('HostName') or selected.get('Host')
                port = int(selected.get('Port', 22))
                reachable, _, _ = is_reachable(hostname, port)
                if reachable:
                    if not args.dry_run:
                        connect_via_paramiko(selected, password, debug=args.debug)
                else:
                    print("❌ Selected host is not reachable.")
            else:
                print("❌ Choice out of range.")
        except Exception:
            print("❌ Invalid choice or interrupted.")
        return

    for h in matched:
        hostname = h.get('Hostname') or h.get('HostName') or h.get('Host')
        port = int(h.get('Port', 22))
        reachable, _, _ = is_reachable(hostname, port)
        if reachable:
            if not args.dry_run:
                connect_via_paramiko(h, password, debug=args.debug)
            return

    print("❌ None of the matched hosts are reachable.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("* No choice entered. Operation cancelled.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
