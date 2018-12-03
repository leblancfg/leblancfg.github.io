Title: Installing the Azure CLI on Manjaro (Arch) with Anaconda
Date: 2018-12-03
Category: Linux
Tags: linux, manjaro, arch, azure, cli
Slug: installing-azure-cli-on-manjaro-arch-with-anaconda
Authors: François Leblanc
Summary: A short guide to troubleshooting the installation of Microsoft's Azure Command Line Interface (CLI) on Manjaro Linux

I recently got access to Azure at work a few weeks back, and was trying to connect to it from my Linux workstation. As a compromise to get NVidia drivers working for my GTX960 GPU, I have Manjaro installed on it. I wasn't expecting a really seamless installation process &mdash; despite the "MS♥Linux" propaganda, that boat is going to take years to turn. Case in point out of the many we've encountered: there are no free or shared tiers for [Web App Service](https://azure.microsoft.com/en-ca/pricing/details/app-service/linux/) instances for Linux.

Both `awscli` and `gcp` are both pip-installable, but for some reason azure CLI needs to install other dependencies. However as my home setup is a little ways off the beaten path (Manjaro, with Anaconda installed) I did hit a snag worthy of sharing.

I started with:

    yaourt -S python-azure-cli --noconfirm

>N.B. that last argument is highly recomended. The azure CLI is not a single install, but rather like 100 different modules, and you will have to accept/ continue every single one of them.

but I got the error:

    rm: cannot remove '/tmp/yaourt-tmp-leblancfg/aur-python-azure-storage/pkg/python-azure-storage/usr/lib/python3.?/site-packages/azure/__init__.py': No such file or directory
    ==> ERROR: A failure occurred in package().
        Aborting...
    ==> ERROR: Makepkg was unable to build python-azure-storage.

If you don't get this error and the previous incantation works for you straight away, great! I've since [notified the package manager](https://aur.archlinux.org/packages/python-azure-cli/), and hopefully this gets resolved in later versions of the package.

Fortunately, Microsoft also packages a [distribution-independent installation script](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?view=azure-cli-latest), which you can run with:

    curl -L https://aka.ms/InstallAzureCli | bash

I thought it was in the bag but got the error:

    ERROR: This script does not support the Python Anaconda environment. Create an Anaconda virtual environment and install with 'pip'

Well darn. I want to be able to call `az` through the whole system, not just in a virtual env. If you get this and have Anaconda installed, here's an easy fix for you.

`pip` is calling the python version in your `PATH`, which it gets from the Anaconda location. Behind the scenes, Arch also has a version of Python installs, which it uses for system administration. Same applies for macOS. It's usually refered to as "system Python". To bypass this, we'll temporarily remove Anaconda from our `PATH`, install the azure client, and reinstate the original `PATH`:

>**Warning**: the following steps mess with your `PATH` variable. If for some reason the installation doesn't work, make sure to run the last command in the block.

    echo $PATH > tmp
    export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/opt/cuda/bin:/usr/lib/jvm/default/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl"
    curl -L https://aka.ms/InstallAzureCli | bash
    export PATH="$(cat tmp)"
    source ~/.bashrc

For the installation, I just used the defaults. At this point, the installation should be complete. Test with:

    az login

And make sure that your Python interpreter is back to its original state with:

    python -c "import sys;print('Anaconda' in sys.executable)"
