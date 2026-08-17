def _is_ssh_key_format(entity, kind=None):
    import re
    from network.mods.ssh.types import SSHKeyKinds

    if kind:
        if not kind.startswith("ssh-") and not kind.startswith("ecdsa-") and not kind.startswith("sk-"):
            type_regex = rf"(?:ssh-{re.escape(kind.lower())}|ecdsa-sha2-nistp[235]?[0-9][0-9])" # Looser for ecdsa
            if kind.lower() == "ecdsa":
                type_regex = r"(?:ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521|sk-ecdsa-sha2-nistp256@openssh.com)"
            elif kind.lower() == "ed25519":
                type_regex = r"(?:ssh-ed25519|sk-ssh-ed25519@openssh.com)"
            elif kind.lower() == "rsa":
                type_regex = r"ssh-rsa"
            elif kind.lower() == "dss":
                type_regex = r"ssh-dss"
            else:
                type_regex = re.escape(kind)
        else:
            type_regex = re.escape(kind.lower())
        if kind.lower() not in [t.lower().replace("ssh-", "").replace("-sha2-nistp", "").replace("@openssh.com","") for t in SSHKeyKinds] and \
           kind.lower() not in [t.lower() for t in SSHKeyKinds]:
            pass
    else:
        type_regex = r"|".join([re.escape(t) for t in SSHKeyKinds])
        type_regex = f"(?:{type_regex})"

    base64_pattern = r"[A-Za-z0-9+/]+={0,2}"
    comment_pattern = r"(?:\s+.*)?"

    pattern = re.compile(rf"^{type_regex}\s+{base64_pattern}{comment_pattern}$", re.IGNORECASE)
    match = pattern.match(entity)

    if match and kind:
        matched_type = entity.split(' ')[0].lower()
        if kind.lower() == "rsa" and matched_type == "ssh-rsa":
            return True
        elif kind.lower() == "dss" and matched_type == "ssh-dss":
            return True
        elif kind.lower() == "ecdsa" and any(m in matched_type for m in ["ecdsa-sha2", "sk-ecdsa"]):
            return True
        elif kind.lower() == "ed25519" and any(m in matched_type for m in ["ssh-ed25519", "sk-ssh-ed25519"]):
            return True
        elif matched_type == kind.lower():
            return True
        elif matched_type == f"ssh-{kind.lower()}":
            return True
        else:
            return False
    return bool(match)

def _is_ssh_key(entity, kind=None, private=False):
    import re
    if not isinstance(entity, str) or not entity.strip():
        return False

    entity = entity.strip()
    norm_kind = (kind or "").lower()
    if private:
        openssh_private_pattern = re.compile(
            r"-----BEGIN OPENSSH PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*-----END OPENSSH PRIVATE KEY-----",
            re.DOTALL
        )
        if norm_kind:
            header_map = {
                "rsa": "RSA PRIVATE KEY",
                "dss": "DSA PRIVATE KEY",
                "ecdsa": "EC PRIVATE KEY",
                "ed25519": "OPENSSH PRIVATE KEY",
                "openssh": "OPENSSH PRIVATE KEY"
            }
            expected_header_suffix = header_map.get(norm_kind, "").upper()
            if not expected_header_suffix:
                if norm_kind in ["ssh-rsa", "ssh-dss", "ecdsa-sha2-nistp256", "ssh-ed25519", "sk-ecdsa-sha2-nistp256@openssh.com"]:
                    pass
                else:
                    return False

            if expected_header_suffix == "OPENSSH PRIVATE KEY":
                return bool(openssh_private_pattern.search(entity))
            else:
                pem_private_pattern = re.compile(
                    rf"-----BEGIN {re.escape(expected_header_suffix)}-----\s*([A-Za-z0-9+/=\s]+)\s*-----END {re.escape(expected_header_suffix)}-----",
                    re.DOTALL
                )
                return bool(pem_private_pattern.search(entity))
        else:
            if openssh_private_pattern.search(entity):
                return True
            pem_any_private_pattern = re.compile(
                r"-----BEGIN (?:(RSA|DSA|EC|ENCRYPTED|OPENSSH) )?PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*-----END (?:(RSA|DSA|EC|ENCRYPTED|OPENSSH) )?PRIVATE KEY-----",
                re.DOTALL
            )
            return bool(pem_any_private_pattern.search(entity))
    else:
        return _is_ssh_key_format(entity, kind)

def _is_ssh_key_file(entity: str) -> bool:
    from utils import require
    require.path.isfile(entity)
    from typed import term
    from utils.path import File

    content = term(entity, File).read()
    return _is_ssh_key(content)

