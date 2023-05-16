import os


class GitRepo:
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return self._path


    @property
    def is_modified(self):
        return False


def is_git_repo(dir):
    # Fast check without subcommand: Check if .git directory exists
    gitdir = os.path.join(dir, ".git")
    return os.path.isdir(gitdir)