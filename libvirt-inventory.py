#!/usr/bin/env python2

import argparse
import os
import sys
import libvirt
import yaml
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from functools import wraps

try:
    import json
except ImportError:
    import simplejson as json

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]

class Config():
    __metaclass__ = Singleton

    def __init__(self):
        utility_name = os.path.splitext(os.path.basename(__file__))[0]
        script_path = os.path.realpath(__file__)
        dir_path = os.path.dirname(script_path)

        config_directory = os.getenv('LIBVIRT_INVENTORY_CONFIG_DIR', dir_path)
        self.config_dir = config_directory

        config_name = 'config.yml'
        config_path = '{}/{}'.format(config_directory, config_name)

        try:
            self.config = yaml.load(open(config_path, 'r'))
        except yaml.YAMLError as exc:
            msg = 'Error in configuration file: {}'.format(str(exc))
            print msg
            sys.exit(1)
        except Exception as exc:
            msg = 'Exception {}'.format(str(exc))
            print msg
            sys.exit(1)

class libvirt_domain_data_decorator(object):

    def __init__(self, *args, **kwargs):
        self.decorator_args = args
        self.decorator_kwargs = kwargs

    def __call__(self, f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            inventory = dict(_meta=dict(hostvars=dict()))

            conf = Config()
            config = conf.config
            config_dir = conf.config_dir
            port = config['libvirt_api']['port']
            username = config['libvirt_api']['auth']['username']
            password = config['libvirt_api']['auth']['password']
            auth_object = HTTPBasicAuth(username, password)

            for libvirt_server in config['libvirt_api']['servers']:
                url = f(args[0], libvirt_server, port)

                crt_name = 'certificate.crt'
                crt_path = '{}/{}'.format(config_dir, crt_name)

                ssl_verify = crt_path if config['libvirt_api']['auth']['ssl_verify'] else False

                response = requests.get(url, auth=auth_object, verify=ssl_verify)

                if response.ok:
                    domains_data = response.json()

                    for domain_data in domains_data['domains']:
                        for tag in domain_data['libvirt_tags']:
                            _push(inventory, tag, domain_data['libvirt_name'])

                        inventory['_meta']['hostvars'][domain_data['libvirt_name']] = domain_data
                        inventory['_meta']['hostvars'][domain_data['libvirt_name']]['ansible_host'] = domain_data['libvirt_ipv4']
                else:
                    msg = "Request to libvirt api on {} failed".format(libvirt_server)
                    print(msg)
                    sys.exit(1)

            return inventory
        return wrapped_f

class LibvirtInventory(object):
    ''' libvirt dynamic inventory '''

    def __init__(self):
        ''' Main execution path '''

        self.inventory = dict()  # A list of groups and the hosts in that group
        self.cache = dict()  # Details about hosts in the inventory

        conf = Config()

        self.parse_cli_args()

        if self.args.host:
            print _json_format_dict(self.get_host_info(), self.args.pretty)
        elif self.args.list:
            print _json_format_dict(self.get_inventory(), self.args.pretty)
        else:  # default action with no options
            print _json_format_dict(self.get_inventory(), self.args.pretty)

    def parse_cli_args(self):
        ''' Command line argument processing '''

        parser = argparse.ArgumentParser(
            description='Produce an Ansible Inventory file based on libvirt'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            default=True,
            help='List instances (default: True)'
        )
        parser.add_argument(
            '--host',
            action='store',
            help='Get all the variables about a specific instance'
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            default=False,
            help='Pretty format (default: False)'
        )
        self.args = parser.parse_args()

    @libvirt_domain_data_decorator()
    def get_host_info(self, libvirt_server, port):
        ''' Get variables about a specific host '''
        host = self.args.host
        url = 'https://{}:{}/domain/{}'.format(libvirt_server, port, host)
        return url

    @libvirt_domain_data_decorator()
    def get_inventory(self, libvirt_server, port):
        ''' Construct the inventory '''
        url = 'https://{}:{}/domains'.format(libvirt_server, port)
        return url

def _push(my_dict, key, element):
    '''
    Push element to the my_dict[key] list.
    After having initialized my_dict[key] if it dosn't exist.
    '''

    if key in my_dict:
        my_dict[key].append(element)
    else:
        my_dict[key] = [element]

def _json_format_dict(data, pretty=False):
    ''' Serialize data to a JSON formated str '''

    if pretty:
        return json.dumps(data, sort_keys=True, indent=2)
    else:
        return json.dumps(data)

LibvirtInventory()
