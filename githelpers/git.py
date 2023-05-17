import os
import subprocess


class GitRepo:
    def __init__(self, path):
        self._path = path
        self._modified = None
        self._branch = None
        self._detached = None
        self._encoding = "utf-8"

    @property
    def path(self):
        return self._path

    @property
    def branch(self):
        if self._branch is None:
            self.read_status()
        return self._branch

    @property
    def detached(self):
        if self._detached is None:
            self.read_status()
        return self._detached

    @property
    def is_modified(self):
        if self._modified is None:
            self.read_status()
        return self._modified

    def run(self, command, capture_output = False):
        cmd = ["git", "-C", self._path]
        cmd.extend(command)

        return subprocess.run(cmd, capture_output=capture_output, encoding=self._encoding)

    def read_status(self):
        self._branch = None
        self._modified = None
        self._detached = None

        # Read current local branch name
        rs = self.run(["rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
        if rs.returncode == 0:
            self._branch = rs.stdout.strip()
            self._detached = self._branch == "HEAD"
        else:
            print(rs)

        # check for any local modifications
        self._modified = False


def is_git_repo(dir):
    # Fast check without subcommand: Check if .git directory exists
    gitdir = os.path.join(dir, ".git")
    return os.path.isdir(gitdir)