from typed.meta import STR

class SSH_KEY(STR):
    def __isterm__(typ, trm):
        if not isinstance(trm, str):
            return False

        private = typ.__ssh_key_private__
        kinds = typ.__ssh_key_kinds__

        if not kinds:
            from network.helper.ssh import _is_ssh_key
            return (
                trm in SSHKey(private=True) or
                trm in SSHKey(private=False)
            )

        if kinds:
            return any(
                _is_ssh_key(key_string=trm, key_type=t, private=private)
                for t in kinds
            )
        return _is_ssh_key(key_string=trm, key_type=None, private=private)

    def __call__(typ, *kinds, private=False):
        kinds_set = set(str(t) for t in kinds)

        if kinds_set:
            kindsstr = ", ".join(kinds_set)
            class_name = f"SSHKey({kindsstr}, private={private})"
        else:
            class_name = f"SSHKey(private={private})"

        namespace = {
            "__display__": class_name,
            "__null__": "",
            "__ssh_key_kinds__": kinds_set,
            "__ssh_key_private__": private,
        }

        return SSH_KEY(class_name, (Str,), namespace)
