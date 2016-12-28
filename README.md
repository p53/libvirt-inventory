Installation:
=========

  Compatible with python2 (we need to be compatible with ansible)

  **Download source:**

    git clone URL /opt/libvirt-inventory

  **Install virtualenv:**

    pip install virtualenv

  **Setup virtual environment:**

    cd /opt/libvirt-inventory
    virtualenv --no-site-packages venv

  **Activate virtual environment:**

    source venv/bin/activate

  **Install dependencies:**

    pip install -r requirements.txt

  **NOTE:** Generate your own private key and certificate, those included are for demo purposes!!

Configuration:
=========

  **Config directory:**

  You can customize location of config directory by setting up environment variable e.g.:

  ```bash
  export LIBVIRT_INVENTORY_CONFIG_DIR=~/.libvirt-inventory
  ```
  
Usage:
=========

#### Examples

  This will list all hosts:

    /opt/libvirt-inventory/libvirt-inventory.py

  This will also list all hosts:

    /opt/libvirt-inventory/libvirt-inventory.py --list

  This will list specific host, name of host is VM name:

    /opt/libvirt-inventory/libvirt-inventory.py -h my_host

  This will generate all hosts with nice json output:

    /opt/libvirt-inventory/libvirt-inventory.py --list --pretty

### Credits:

  __Author: Pavol Ipoth__

### Copyright:

  __License: GPLv3__
