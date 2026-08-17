from typed import Values

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


