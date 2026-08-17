from typed.meta import STR
from utils.path import File

class SSH_KEY(STR):
    def __isterm__(typ, trm):
        if not isinstance(trm, str):
            return False

        private = typ.__ssh_key_private__
        kinds = typ.__ssh_key_kinds__

        from network.helper.ssh import _is_ssh_key
        if kinds:
            return any(
                _is_ssh_key(entity=trm, kind=t, private=private)
                for t in kinds
            )
        return _is_ssh_key(entity=trm, kind=None, private=private)

    def __call__(typ, *kinds, private=False):
        kinds_set = set(str(k) for k in kinds)
        from network.mods.ssh.types import SSHKeyKinds
        from typed import require
        require.every.isterm(kinds_set, SSHKeyKinds)

        if kinds_set:
            kinds_str = ", ".join(kinds_set)
            display_name = f"SSHKey({kinds_str}, private={private})"
        else:
            display_name = f"SSHKey(private={private})"

        from typed import Str
        class SSHKey(Str, metaclass=SSH_KEY):
            __display__ = display_name
            __name__ = display_name
            __null__ = ""
            __ssh_key_kinds__ = kinds_set
            __ssh_key_private__ = private

class SSH_KEY_FILE(File.__type__):
    def __isterm__(typ, trm):
        if not isinstance(trm, str):
            return False

        private = typ.__ssh_key_private__
        kinds = typ.__ssh_key_kinds__

        from network.helper.ssh import _is_ssh_key_file
        if kinds:
            return any(
                _is_ssh_key_file(entity=trm, kind=t, private=private)
                for t in kinds
            )
        return _is_ssh_key_file(entity=trm, kind=None, private=private)

    def __call__(typ, *kinds, private=False):
        kinds_set = set(str(k) for k in kinds)
        from network.mods.ssh.types import SSHKeyKinds
        from typed import require
        require.every.isterm(kinds_set, SSHKeyKinds)

        if kinds_set:
            kinds_str = ", ".join(kinds_set)
            display_name = f"SSHKey({kinds_str}, private={private})"
        else:
            display_name = f"SSHKey(private={private})"

        class SSHKeyFile(File, metaclass=SSH_KEY_FILE):
            __display__ = display_name
            __name__ = display_name
            __null__ = ""
            __ssh_key_kinds__ = kinds_set
            __ssh_key_private__ = private
