# gitall

`gitall` is a command line tool to show the status of multiple
git repositories within some folder, and to execute git commands
on multiple git repositories.

This tool is useful if you have multiple git repositories checked
out, and you want to make sure you commited and pushed all of them
at the end of your day. It can also be used to switch branches,
show diffs, .. across multiple repositories.

## Example
```commandline
stefan:~/Projects$ gitall                                                                                                                                                                        [21:48:44]
====  /home/stefan/Projects/Organ/eOrgan (master: clean)  ====

====  /home/stefan/Projects/Organ/eOrgan-firmware (master: clean)  ====

====  /home/stefan/Projects/pplatex (master: clean)  ====

====  /home/stefan/Projects/gitall (main: modified)  ====
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

no changes added to commit (use "git add" and/or "git commit -a")

  o) Repositories: 4, Modified: 1, Errors: 0
```

## Installation

Either install the pre-built .whl package from my github:
```commandline
wget https://github.com/stefanhepp/gitall/releases/download/gitall-1.0.0/gitall-1.1.0-py3-none-any.whl
pip install gitall-1.1.0-py3-none-any.whl
```
Or install from sources (any of the following commands):
```commandline
git clone https://github.com/stefanhepp/gitall.git
pip install -e gitall
```
Or build your own package
```commandline
git clone https://github.com/stefanhepp/gitall.git
cd gitall
python -m build
pip install dist/gitall-1.0.0.-py3-none-any.whl
```

## Usage

Run the program from the commandline with no arguments to get
the status 

## Configuration

## License

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
