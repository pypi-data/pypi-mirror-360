# sbpkg 1.1.3

### About

Simple, fast and full-featured SBo package manager.

Sbpkg is a command-line tool to synchronize with the SlackBuilds.org
repository. It features resolving dependency support, install and
uninstall scripts, and the ability to sync your local machine with
a remote repository to automatically upgrade packages.

### Features

- Install packages with resolving dependencies.
- Build SlackBuilds scripts without installing.
- Check and upgrade installed SBo packages on your system.
- Check your installed packages and dependencies based on repository.
- Remove installed packages with their dependencies.
- Automatic calculate the installed package size.
- Automatic MD5 checksum for download sources.
- Automatic GPG verification for SBo scripts.
- Display the full path of package dependencies.
- Display packages that depend on other packages.
- Search SlackBuilds in the repository.
- Download slackbuilds scripts with sources without build or install them.
- Display the full information of packages in your terminal.
- Display the contents of the SlackBuild files in your terminal.

### Install

```bash
$ tar xvf sbpkg-1.1.3.tar.gz
$ cd sbpkg-1.1.3
$ ./install.sh
```

## Screenshots

### sbpkg --install \<packages\>

<img src="https://gitlab.com/dslackw/images/-/raw/master/sbpkg/install.png" width="900" title="sbpkg --install <packages>">

### sbpkg --remove \<packages\>

<img src="https://gitlab.com/dslackw/images/-/raw/master/sbpkg/remove.png" width="900" title="sbpkg --remove <packages>">

### sbpkg --upgrade

<img src="https://gitlab.com/dslackw/images/-/raw/master/sbpkg/upgrade.png" width="900" title="sbpkg --upgrade">

### sbpkg --pkg-info \<packages\>

<img src="https://gitlab.com/dslackw/images/-/raw/master/sbpkg/information.png" width="900" title="sbpkg --pkg-information <packages>">