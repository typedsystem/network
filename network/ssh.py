import os
import stat
import shlex
from typed import typed, TYPE, Str, Bool, Tuple, List, Nill, Union, Maybe
from utils.mods.path import Path, File, Exists
from utils.mods.file import file
from utils.mods.cmd  import cmd as _cmd
from utils.mods.helper.ssh import _is_ssh_key

SSHKey = SSH_KEY('SSHKey', (Str,), {
        "__display__": 'SSHKey',
        "__null__": "",
        "_ssh_types": (),
        "_ssh_private": None
    })

class SSHErr(Exception): pass

class ssh:
    class key:
        @typed
        def prepare(key: Union(Path, SSHKey(private=True))) -> Tuple:
            try:
                if key in Path and os.path.exists(str(key)):
                    return key, False

                tmp_file = _cmd.mktemp.file()

                k = str(key)
                if not k.endswith("\n"):
                    k += "\n"

                with open(str(tmp_file), "w", encoding="utf-8", newline="\n") as f:
                    f.write(k)

                os.chmod(str(tmp_file), stat.S_IRUSR | stat.S_IWUSR)

                with open(str(tmp_file), "rb") as f:
                    data = f.read()
                return tmp_file, True
            except Exception as e:
                raise SSHErr(e)

        @typed
        def add(key: Union(File, SSHKey(private=True))) -> Nill:
            try:
                if "SSH_AUTH_SOCK" not in os.environ:
                    stderr, stdout = _cmd.run("ssh-agent -s")
                    out = stdout or ""
                    for line in out.splitlines():
                        if "SSH_AUTH_SOCK" in line or "SSH_AGENT_PID" in line:
                            k, v = line.split(";", 3)[0].split("=", 1)
                            os.environ[k] = v

                key_path, temp_key = ssh.key.prepare(key)

                rc, stderr, stdout = _cmd.run(f"ssh-add {key_path}")
                if rc != 0:
                    msg = stderr or stdout or f"SSH command failed with exit code {rc}"
                    raise SSHErr(msg)

                return stdout

                if temp_key:
                    _cmd.rm(key_path)
                return
            except Exception as e:
                raise SSHErr(e)

    @typed
    def exec(host: Str, user: Str, key: Str, cmd: Union(Str, Tuple(Str), List(Str), File), cwd: Maybe(Str)=None) -> Str:
        try:
            key_path, temp_key = ssh.key.prepare(key)
            try:
                if not cmd in Union(List, Tuple):
                    if cmd in File:
                        remote_cmd = file.read(cmd)
                    else:
                        remote_cmd = str(cmd)
                else:
                    remote_cmd = " ".join(shlex.quote(str(p)) for p in cmd)

                if cwd:
                    if "\n" in remote_cmd:
                        remote_cmd = (
                            f"cd {shlex.quote(str(cwd))} && (\n{remote_cmd}\n)"
                        )
                    else:
                        remote_cmd = f"cd {shlex.quote(str(cwd))} && {remote_cmd}"

                ssh_cmd = [
                    "ssh",
                    "-i", str(key_path),
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    remote_cmd,
                ]

                rc, stderr, stdout = _cmd.run(ssh_cmd)
                if rc != 0:
                    msg = stderr or stdout or f"SSH command failed with exit code {rc}"
                    raise SSHErr(msg)

                return stdout
            finally:
                if temp_key and key_path and os.path.exists(key_path):
                    _cmd.rm(key_path)
        except Exception as e:
            if isinstance(e, SSHErr):
                raise
            raise SSHErr(str(e))

    @typed
    def rsync(host: Str, user: Str, key: Str, source: Exists, target: Path, delete: Bool=False, pull: Bool=False) -> Nill:
        try:
            if not _cmd.exists("rsync"):
                raise SSHErr("rsync command not found in PATH")

            key_path, temp_key = ssh.key.prepare(key)
            try:
                rsync_cmd = ["rsync", "-az"]
                if delete:
                    rsync_cmd.append("--delete")

                ssh_part = [
                    "ssh",
                    "-i", str(key_path),
                    "-o", "StrictHostKeyChecking=no",
                ]
                rsync_cmd += ["-e", " ".join(shlex.quote(p) for p in ssh_part)]

                if pull:
                    src = f"{user}@{host}:{source}"
                    dst = str(target)
                else:
                    src = str(source)
                    dst = f"{user}@{host}:{target}"

                rsync_cmd += [src, dst]

                stderr, stdout = _cmd.run(rsync_cmd)

                if stderr:
                    raise SSHErr(stderr)

                return
            finally:
                if temp_key and key_path and os.path.exists(key_path):
                    _cmd.rm(key_path)
        except Exception as e:
            if isinstance(e, SSHErr):
                raise
            raise SSHErr(str(e))
