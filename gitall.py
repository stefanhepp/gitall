#!/usr/bin/env python3

import os
import argparse
import pathlib

from colorama import Fore, Style

import githelpers


class Config:
    def __init__(self):
        self._excluded_dirs=[]
        self._subrepos = False
        self._use_status = True
        self._sort = True
        self._sort_status = True
        self._colored = True

    def load(self):
        pass

    def _load_config(self, configfile):
        pass

    def exclude(self, excluded_dirs):
        for d in excluded_dirs:
            if os.path.dirname(d) == '':
                # Just a single dir name, match as pattern
                self._excluded_dirs.append(d)
            else:
                # seems to be a path, match as absolute path
                self._excluded_dirs.append( os.path.abspath(d) )

    @property
    def excluded(self):
        return self._excluded_dirs

    def is_excluded(self, basedir, dirname):
        if dirname == ".git":
            return True
        if self._excluded_dirs.count(dirname) > 0:
            return True
        if self._excluded_dirs.count(os.path.abspath(os.path.join(basedir, dirname))) > 0:
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



    githelpers.is_git_repo(rootdir)

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
            path += " (modified)"
        else:
            path += " (clean)"

    if config.colored:
        if config.use_status:
            if repo.is_modified:
                color = Fore.RED
            else:
                color = Fore.GREEN
        else:
            color = Style.RESET_ALL
        print(Fore.CYAN, "==== ", color, path, Fore.CYAN, " ====", Style.RESET_ALL)
    else:
        print("==== ", path, " ====")


def print_repo_status(repo, config: Config):
    pass


def run_command(repo, command):
    pass


def print_summary(repos, config: Config):
    modified = sum(1 for repo in repos if repo.is_modified)
    clean = len(repos) - modified

    print("  o) Repositories: %d, Modified: %d, Clean: %d" % (len(repos), modified, clean))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Execute a git command on multiple repositories"
    )
    parser.add_argument("-d", "--directory", action="append", type=pathlib.Path, default=[],
                        help="Search in the given directories instead of the current directory.")
    parser.add_argument("-e", "--exclude", action="append", type=str, default=[],
                        help="Specify directories to exclude from the search.")
    parser.add_argument("-u", "--subrepos", action=argparse.BooleanOptionalAction, default=None,
                        help="Search for git repositories within git repositories.")
    parser.add_argument("-s", "--sort", choices=["no", "path", "status"], default=None,
                        help="Sort repositories based on status, list modified repos last.")
    parser.add_argument("-n", "--status", action=argparse.BooleanOptionalAction, default=None,
                        help="Check and print the status of the repositories (default: True).")
    parser.add_argument("command", metavar="command", type=str, nargs=argparse.REMAINDER)

    args = parser.parse_args()

    # Cleanup command to execute
    command = args.command
    if len(command)>0 and command[0] == "--":
        command = command[1:]
    command = ' '.join(command)

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

    for repo in repos:
        # Print a header
        print_repo_header(repo, config)

        # Print the status or output of the command
        if command == "":
            print_repo_status(repo, config)
        else:
            run_command(repo, command)

        print()

    # Print a summary of the found repositories
    if config.use_status:
        print_summary(repos, config)


if __name__ == "__main__":
    main()