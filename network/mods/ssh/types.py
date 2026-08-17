from typed import Values, Str
from utils.path import File
from network.mods.ssh.meta import SSH_KEY, SSH_KEY_FILE

SSHKeyKinds = Values(
    "ssh-rsa",
    "ssh-dss",
    "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384",
    "ecdsa-sha2-nistp521",
    "sk-ecdsa-sha2-nistp256@openssh.com",
    "ssh-ed25519",
    "sk-ssh-ed25519@openssh.com"
)

class SSHKey(Str, metaclass=SSH_KEY):
    __display__ = "SSHKey"
    __null__ = ""

class SSHKeyFile(File, metaclass=SSH_KEY_FILE):
    __display__ = "SSHKeyFile"
    __null__ = ""
