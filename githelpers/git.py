import os
import subprocess


class GitRepo:
    def __init__(self, path):
        self._path = path
        self._modified = None
        self._branch = None

    @property
    def path(self):
        return self._path

    @property
    def branch(self):
        if self._branch is None:
            self.read_status()
        return self._branch

    @property
    def is_modified(self):
        if self._modified is None:
            self.read_status()
        return self._modified

    def run(self, command, capture_output = False):
        cmd = ["git", "-C", self._path]
        cmd.extend(command)

        return subprocess.run(cmd, capture_output=capture_output)

    def read_status(self):
        self._branch = "main"
        self._modified = False

def is_git_repo(dir):
    # Fast check without subcommand: Check if .git directory exists
    gitdir = os.path.join(dir, ".git")
    return os.path.isdir(gitdir)