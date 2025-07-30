#!/usr/bin/env python3
"""
MatrixSwarm Launcher – Smart Boot

This tool:
- Boots the MatrixSwarm AI universe.
- Detects your current Python environment.
- Injects the correct Python interpreter and site-packages path.
- Allows manual override for edge cases or advanced users.

Run with:
  python site_boot.py --universe ai
  python site_boot.py --universe ai --python-site /custom/site-packages
  python site_boot.py --universe ai --python-bin /custom/bin/python3
"""
def main():

    import os
    import time
    import argparse
    import json
    import base64
    import sys
    import subprocess
    import site

    # Path prep
    SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if SITE_ROOT not in sys.path:
        sys.path.insert(0, SITE_ROOT)

    from pathlib import Path
    from matrixswarm.core.core_spawner import CoreSpawner
    from matrixswarm.core.tree_parser import TreeParser
    from matrixswarm.core.class_lib.processes.reaper import Reaper
    from matrixswarm.core.path_manager import PathManager
    from matrixswarm.core.swarm_session_root import SwarmSessionRoot
    from matrixswarm.boot_directives.load_boot_directive import load_boot_directive
    from matrixswarm.core.utils.boot_guard import enforce_single_matrix_instance, validate_universe_id
    from matrixswarm.core.utils.crypto_utils import generate_aes_key
    from Crypto.Random import get_random_bytes
    from Crypto.Cipher import AES
    from Crypto.PublicKey import RSA

    from matrixswarm.core.class_lib.packet_delivery.packet.standard.general.json.packet import Packet
    from matrixswarm.core.class_lib.packet_delivery.delivery_agent.file.json_file.delivery_agent import DeliveryAgent
    from matrixswarm.core.class_lib.packet_delivery.utility.crypto_processors.packet_encryption_factory import packet_encryption_factory
    from matrixswarm.core.class_lib.packet_delivery.utility.crypto_processors.football import Football

    # === ARGUMENTS ===
    parser = argparse.ArgumentParser(description="MatrixSwarm Boot Loader", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--universe", required=True, help="Target universe ID (e.g., ai, bb, os)")
    parser.add_argument("--directive", default="default", help="Boot directive (e.g., matrix)")
    parser.add_argument("--reboot", action="store_true", help="Soft reboot — skip hard cleanup")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose terminal output")
    parser.add_argument("--python-site", help="Override Python site-packages path to inject")
    parser.add_argument("--python-bin", help="Override Python interpreter to use for agent spawns")
    parser.add_argument("--encrypted-directive", help="Path to AES-GCM encrypted directive JSON")
    parser.add_argument("--swarm_key", help="Base64-encoded swarm key used to decrypt directive")
    parser.add_argument("--encryption-off", action="store_true", help="Turn encryption off for all agents")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    universe_id = args.universe.strip()
    boot_name = args.directive.strip().replace(".py", "")
    reboot = args.reboot
    #show realtime log prints - be warned you will need to open another terminal to
    #terminate the swarm
    verbose = args.verbose
    #turns debugging on
    debug = args.debug

    encryption_enabled = not args.encryption_off

    # === ENVIRONMENT DETECTION ===
    def check_python_env(user_python_bin=None, user_site_path=None, required_module="discord"):
        # Step 1: Determine Python binary
        python_exec = user_python_bin if user_python_bin else sys.executable
        print(f"🔍 Using Python: {python_exec}")

        # Step 2: Check if required module is importable
        try:
            __import__(required_module)
            print(f"'{required_module}' is installed")
        except ImportError:
            print(f"'{required_module}' not found in this environment.")
            print("Attempting to install py-cord...")

            try:
                subprocess.check_call([python_exec, "-m", "pip", "install", "py-cord"])
                print(" py-cord installed successfully.")
            except subprocess.CalledProcessError:
                print(" Failed to install py-cord. Please install it manually.")
                sys.exit(1)

        # Step 3: Determine site-packages path
        if user_site_path:
            python_site = user_site_path
            print(f"[Override] site-packages: {python_site}")
        else:
            try:
                python_site = next(p for p in site.getsitepackages() if "site-packages" in p and Path(p).exists())
            except Exception:
                python_site = site.getusersitepackages()

        if not Path(python_site).exists():
            print(f"Detected site-packages path does not exist: {python_site}")
            sys.exit(1)

        print(f"Using site-packages path: {python_site}")

        return {
            "python_exec": python_exec,
            "python_site": python_site
        }

    env = check_python_env(
        user_python_bin=args.python_bin,
        user_site_path=args.python_site
    )

    python_exec = env["python_exec"]
    python_site = env["python_site"]
    if args.python_site:
        print(f"[Override] --python-site = {args.python_site}")
    if args.python_bin:
        print(f"[Override] --python-bin  = {args.python_bin}")

    # === PRE-BOOT GUARD ===
    validate_universe_id(universe_id)
    if not reboot:
        enforce_single_matrix_instance(universe_id)
    os.environ["UNIVERSE_ID"] = universe_id

    # === BOOT SESSION SETUP ===
    SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SwarmSessionRoot.inject_boot_args(site_root=SITE_ROOT)


    session = SwarmSessionRoot()
    base_path = session.base_path
    agent_source = os.path.join(SITE_ROOT, "agent")
    pm = PathManager(root_path=base_path, agent_override=agent_source, site_root_path=SITE_ROOT)


    # === POD & COMM ===
    pod_path = pm.get_path("pod", trailing_slash=False)
    comm_path = pm.get_path("comm", trailing_slash=False)
    os.makedirs(pod_path, exist_ok=True)
    os.makedirs(comm_path, exist_ok=True)

    # === REBOOT? ===
    if reboot:
        print("[REBOOT] 💣 Full MIRV deployment initiated.")
        Reaper(pod_root=pod_path, comm_root=comm_path).kill_universe_processes(universe_id)
        time.sleep(3)

    # === LOAD TREE ===
    print(f"[BOOT] Loading directive: {boot_name}.py")
    matrix_directive = load_boot_directive(boot_name)
    tp = TreeParser.load_tree_direct(matrix_directive)
    if not tp:
        print("[FATAL] Tree load failed. Invalid structure.")
        sys.exit(1)

    rejected_nodes=    tp.get_rejected_nodes()
    if rejected_nodes:
        print(f"[RECOVERY] ⚠️ Removed duplicate nodes: {rejected_nodes}")

    # === SPAWN CORE ===
    MATRIX_UUID = matrix_directive.get("universal_id", "matrix")

    cp = CoreSpawner(path_manager=pm, site_root_path=SITE_ROOT, python_site=python_site, detected_python=python_exec)
    if verbose:
        cp.set_verbose(True)

    if debug:
        cp.set_debug(True)


    from matrixswarm.core.mixin.ghost_vault import generate_agent_keypair
    from cryptography.hazmat.primitives import serialization
    import hashlib

    # 🔐 Generate Matrix's keypair and fingerprint
    matrix_keys = generate_agent_keypair()
    matrix_pub_obj = serialization.load_pem_public_key(matrix_keys["pub"].encode())
    fp = hashlib.sha256(matrix_keys["pub"].encode()).hexdigest()[:12]

    print(f"[TRUST] Matrix pubkey fingerprint: {fp}")

    #if the directive is encrypted, decrypt
    def decrypt_directive(encrypted_path, swarm_key_b64):

        with open(encrypted_path, "r", encoding="utf-8") as f:
            bubble = json.load(f)

        key = base64.b64decode(swarm_key_b64)
        nonce = base64.b64decode(bubble["nonce"])
        tag = base64.b64decode(bubble["tag"])
        ciphertext = base64.b64decode(bubble["ciphertext"])

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(decrypted.decode())

    swarm_key_b64 = generate_aes_key()
    matrix_key_b64 = generate_aes_key()

    # === Set up Matrix comm channel and trust ===
    comm_path =cp.ensure_comm_channel(MATRIX_UUID, [{}])

    matrix_keys = generate_agent_keypair()
    matrix_pub = matrix_keys["pub"]
    matrix_priv = matrix_keys["priv"]

    _matrix_priv_obj = RSA.import_key(matrix_keys["priv"])

    is_encryption_on=encryption_enabled = int(encryption_enabled)

    #sign and assign all the identities to the agents, priv/pub keys, private aes key, identity(which includes pubkey, universal_id, timestamp)
    tp.assign_identity_to_all_nodes(_matrix_priv_obj)

    #encryption is turned on here
    mode="encrypt"
    if not bool(encryption_enabled):
        mode = "plaintext_encrypt"

    #replace matrix pubkey/privkey with the original
    tp.assign_identity_token_to_node('matrix',
                                     matrix_priv_obj=matrix_keys["priv"],
                                     replace_keys={'priv_key': matrix_priv,
                                                   'pub_key': matrix_pub,
                                                   'private_key': matrix_key_b64}
                                     )


    matrix_node = tp.nodes.get("matrix")

    fb = Football()
    fb.set_identity_sig_verifier_pubkey(matrix_pub)
    fb.add_identity(matrix_node['vault'],
                    identity_name="agent_owner", #owner identity
                    verify_universal_id=True,      #make sure the name of the agent is the same as the one in the identity
                    universal_id="matrix",         #agent name to compare to the identity
                    is_payload_identity=True,         #yes, this payload is an identity; used during receiving packets; this will be the senders packet
                    sig_verifier_pubkey=matrix_pub,   #this pubkey is used to verify the identity, always Matrix's pubkey; used during sending packets
                    is_pubkey_for_encryption=False,    #if you turn on asymmetric encryption the pubkey contained in the identity will encrypt, check payload size
                    is_privkey_for_signing=True,       #use the privkey to sign the whole subpacket
                    )

    fb.set_use_symmetric_encryption(True)

    #fb.load_identity_file(comm_path, uuid="matrix", sig_pubkey=matrix_pub)
    #here is where we add Matrix AES Key to Encrypt and sign with Matrix Public Key
    fb.set_verify_signed_payload(True)
    fb.set_pubkey_verifier(matrix_pub)


    #matrix identity needs to be loaded as the target, because the pubkey is used to encrypt the aes key
    fb.load_identity_file(vault=matrix_node['vault'], universal_id='matrix')
    fb.set_aes_encryption_pubkey(matrix_pub)
    agent = DeliveryAgent()
    agent.set_crypto_handler(packet_encryption_factory(mode, fb))
    pk = Packet()
    pk.set_data({'agent_tree': tp.root})
    agent.set_location({"path": comm_path}) \
        .set_packet(pk) \
        .set_identifier("agent_tree_master") \
        .set_address(["directive"]) \
        .deliver()

    if args.encrypted_directive and args.swarm_key:
        print(f"[BOOT] 🔐 Decrypting encrypted directive from {args.encrypted_directive}")
        matrix_directive = decrypt_directive(args.encrypted_directive, args.swarm_key)
    else:
        print(f"[BOOT] 📦 Loading plaintext directive: {boot_name}")
        matrix_directive = load_boot_directive(boot_name)

    trust_payload = {
        "encryption_enabled": int(encryption_enabled),
        "pub": matrix_pub,
        "priv": matrix_priv,
        "swarm_key": swarm_key_b64,
        "private_key": matrix_key_b64,
        "matrix_pub": matrix_pub,
        "matrix_priv": matrix_priv,
        "security_box": {},
    }

    cp.set_keys(trust_payload)

    matrix_node['children'] = []
    # 🚀 Create pod and deploy Matrix
    new_uuid, pod_path = cp.create_runtime(MATRIX_UUID)
    cp.spawn_agent(new_uuid, MATRIX_UUID, MATRIX_UUID, "site_boot", matrix_node, universe_id=universe_id)

    print("[✅] Matrix deployed at:", pod_path)
    print("[🔐] Matrix public key fingerprint:", fp)
    print("[🧠] The swarm is online.")
if __name__ == "__main__":
    main()