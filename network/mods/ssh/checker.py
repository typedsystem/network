from typed.checker import Checker

class SSHChecker(Checker):
    def iskey(self, entity: object, kind=None, private=False):
        from network.mods.ssh.types import SSHKey
        if self.explode:
            from typed import require
            require.isterm(entity, SSHKey(kinds=[kind], private=private))
