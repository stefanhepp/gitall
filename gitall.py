#!/usr/bin/env python3
import configparser
import os
import argparse
import pathlib
import sys

from colorama import Fore, Style

import githelpers


class Config:
    def __init__(self):
        self._configname = ".gitall.conf"
        self._excluded_dirs=[]
        self._excluded_patterns=[]
        self._subrepos = False
        self._use_status = True
        self._sort = True
        self._sort_status = True
        self._colored = True

    def load(self):
        config_home = os.path.expanduser("~/" + self._configname)
        if os.path.exists(config_home):
            self._load_config(config_home)
        config_local = "./" + self._configname
        if os.path.exists(config_local):
            self._load_config(config_local)

    def _load_config(self, configfile):
        config = configparser.ConfigParser()
        config.read(configfile)
        if "gitall" in config:
            gitall = config['gitall']
            # Read config values
            excluded = gitall.get("excluded", "")
            sort = gitall.get("sort", "").strip()
            self._subrepos = gitall.getboolean("subrepos") if "subrepos" in gitall else self._subrepos
            self._use_status = gitall.getboolean("use-status") if "use-status" in gitall else self._use_status
            self._colored = gitall.getboolean("colored") if "colored" in gitall else self._colored
            # Parse config values
            if sort != "":
                self._sort = (sort != "no")
                self._sort_status = (sort == "status")
            # Not a very safe way of splitting path lists, but better than nothing and good enough for me ..
            excluded = [ e.strip() for e in excluded.split(",") ]
            self.exclude(excluded)

    def exclude(self, excluded_dirs):
        for d in excluded_dirs:
            if os.path.dirname(d) == '':
                # Just a single dir name, match as pattern
                self._excluded_patterns.append(d)
            else:
                # seems to be a path, match as absolute path
                self._excluded_dirs.append( os.path.abspath(d) )

    def is_excluded(self, path, dirname):
        if dir == ".git":
            return True
        if self._excluded_patterns.count(dirname) > 0:
            return True
        if self._excluded_dirs.count(os.path.abspath(os.path.join(path, dirname))) > 0:
            return True
        return False

    @property
    def sort(self):
        return self._sort

    @property
    def sort_status(self):
        return self._sort_status and self._use_status

    @sort.setter
    def sort(self, value):
        self._sort = value

    @sort_status.setter
    def sort_status(self, value):
        self._sort_status = value

    @property
    def colored(self):
        # We only color output if there is actually something to color..
        return self._colored and self._use_status

    @property
    def use_status(self):
        return self._use_status

    @use_status.setter
    def use_status(self, value):
        self._use_status = value

    @property
    def subrepos(self):
        return self._subrepos

    @subrepos.setter
    def subrepos(self, value):
        self._subrepos = value


def find_repositories(dir: str, config: Config):
    repos = []

    rootdir=os.path.abspath(dir)

    # first, walk up to see if we are inside a git repository
    pdir = rootdir
    while pdir:
        if githelpers.is_git_repo(pdir):
            # Found a git repo
            repos.append( githelpers.GitRepo(pdir) )
            if not config.subrepos:
                # If we are not looking for nested git repos, we are done now since we are inside a repo
                return repos
        # Go to parent directory
        d = os.path.dirname(pdir)
        # Check if we reached the top
        if d == pdir:
            break
        else:
            pdir = d

    # Now walk down subdirectories
    for path, dirs, files in os.walk(rootdir):
        excluded = []
        # Check all subdirectories
        # Note: we already checked the top-level directory above when walking up
        for d in dirs:
            subdir = os.path.join(path, d)
            if config.is_excluded(path, d):
                # Do not walk down into excluded directories
                excluded.append(d)
            # Note: it would be a bit faster to check ".git" in dirs, and add 'path' as repo, but it
            #       makes the code more ugly and scans more elements when not looking into git repos.
            elif githelpers.is_git_repo(subdir):
                # Found a git repo in the sub directories
                repos.append( githelpers.GitRepo(subdir) )
                if not config.subrepos:
                    # Do not look into sub-repos if not enabled
                    excluded.append(d)
        for e in excluded:
            dirs.remove(e)

    return repos


def sort_repositories(repos, by_status=False):
    if by_status:
        repos.sort(key=lambda repo: [repo.is_modified, repo.path])
    else:
        repos.sort(key=lambda repo: repo.path)
    return repos


def print_repo_header(repo, config: Config):

    path = repo.path

    if config.use_status:
        if repo.is_modified:
            path += " (%s: modified)" % repo.branch
        elif repo.detached:
            path += " (detached)"
        else:
            path += " (%s: clean)" % repo.branch

    if config.colored:
        if config.use_status:
            if repo.is_modified:
                color = Fore.RED
            elif repo.detached:
                color = Fore.YELLOW
            else:
                color = Fore.GREEN
        else:
            color = Style.RESET_ALL
        print(Fore.CYAN + "==== " + color, path, Fore.CYAN + " ====" + Style.RESET_ALL)
    else:
        print("==== ", path, " ====")


def print_repo_status(repo, config: Config):
    if not config.use_status or repo.is_modified:
        # Only run status command if there is anything modified
        repo.run(["status"])


def run_command(repo, command):
    result = repo.run(command)
    return result.returncode


def print_summary(repos, errors, config: Config):
    if config.use_status:
        modified = sum(1 for repo in repos if repo.is_modified)
        modified = Fore.RED + str(modified) + Style.RESET_ALL if modified > 0 and config.colored else str(modified)
    else:
        modified = "-"

    errors = Fore.RED + str(errors) + Style.RESET_ALL if errors > 0 and config.colored else str(errors)

    print("  o) Repositories: %d, Modified: %s, Errors: %s" % (len(repos), str(modified), errors))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Execute a git command on multiple repositories"
    )
    parser.add_argument("-d", "--directory", action="append", type=pathlib.Path, default=[],
                        help="Search in the given directory instead of the current directory. "
                             "Can be specified multiple times.")
    parser.add_argument("-e", "--exclude", action="append", type=str, default=[],
                        help="Specify directories to exclude from the search. Can be specified multiple times.")
    parser.add_argument("-u", "--subrepos", action=argparse.BooleanOptionalAction, default=None,
                        help="Search for git repositories within git repositories.")
    parser.add_argument("-s", "--sort", choices=["no", "path", "status"], default=None,
                        help="Sort repositories based on status, list modified repos last.")
    parser.add_argument("-t", "--status", action=argparse.BooleanOptionalAction, default=None,
                        help="Check and print the status of the repositories (default: True).")
    parser.add_argument("-x", "--abort", action=argparse.BooleanOptionalAction, default=False, dest="abort_on_error",
                        help="Abort on first git command error.")
    parser.add_argument("command", metavar="command", type=str, nargs=argparse.REMAINDER)

    args = parser.parse_args()

    # Cleanup command to execute
    command = args.command
    if len(command)>0 and command[0] == "--":
        command = command[1:]

    # Setup configuration
    config = Config()
    # Load config file
    config.load()
    # Override config with commandline args
    config.exclude(args.exclude)
    if args.sort is not None:
        config.sort = args.sort != "no"
        config.sort_status = args.sort == "status"
    if args.subrepos is not None:
        config.subrepos = args.subrepos
    if args.status is not None:
        config.use_status = args.status

    # Find repositories in all dirs
    dirs = args.directory if len(args.directory) > 0 else ["."]

    repos = [repo for d in dirs for repo in find_repositories(d, config)]

    # Sort repositories
    if config.sort:
        repos = sort_repositories(repos, config.sort_status)

    # Start printing output
    #just_fix_windows_console()

    errors = 0
    lasterror = 0
    for repo in repos:
        # Print a header
        print_repo_header(repo, config)

        # Print the status or output of the command
        if len(command) == 0:
            print_repo_status(repo, config)
        else:
            retcode = run_command(repo, command)
            if retcode != 0:
               errors += 1
               lasterror = retcode
               if args.abort_on_error:
                   break

        print()

    # Print a summary of the found repositories
    print_summary(repos, errors, config)

    return lasterror


# Run main function
if __name__ == "__main__":
    retcode = main()
    sys.exit(retcode)