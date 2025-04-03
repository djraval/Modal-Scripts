# Networking and security

Sandboxes are built to be secure-by-default, meaning that a default Sandbox
has no ability to accept incoming network connections or access your Modal
resources.

## Networking

Since Sandboxes may run untrusted code, they have options to restrict their
network access. To block all network access, set `block_network=True` on
`Sandbox.create`.

For more fine-grained networking control, a Sandbox’s outbound network access
can be restricted using the `cidr_allowlist` parameter. This parameter takes a
list of CIDR ranges that the Sandbox is allowed to access, blocking all other
outbound traffic.

### Forwarding ports

Sandboxes can also expose TCP ports to the internet. This is useful if, for
example, you want to connect to a web server running inside a Sandbox.

Use the `encrypted_ports` and `unencrypted_ports` parameters of
`Sandbox.create` to specify which ports to forward. You can then access the
public URL of a tunnel using the `Sandbox.tunnels` method:

    
    
    import requests
    import time
    
    sb = modal.Sandbox.create(
        "python",
        "-m",
        "http.server",
        "12345",
        encrypted_ports=[12345],
        app=my_app,
    )
    
    tunnel = sb.tunnels()[12345]
    
    time.sleep(1)  # Wait for server to start.
    
    print(f"Connecting to {tunnel.url}...")
    print(requests.get(tunnel.url, timeout=5).text)

Copy

For more details on how tunnels work, see the tunnels guide.

## Security model

In a typical Modal Function, the Function code can call other Modal APIs
allowing it to spawn containers, create and destroy Volumes, read from Dicts
and Queues, etc. Sandboxes, by contrast, are isolated from the main Modal
workspace. They have no API access, meaning the blast radius of any malicious
code is limited to the Sandbox environment.

Sandboxes are built on top of gVisor, a container runtime by Google that
provides strong isolation properties. gVisor has custom logic to prevent
Sandboxes from making malicious system calls, giving you stronger isolation
than standard runc containers.

