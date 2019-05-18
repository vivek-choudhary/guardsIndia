# -*- coding: utf-8 -*-

# The file has been written to override the home route and to append default db to its parameters

import odoo
from odoo import http
from odoo.http import request
import odoo.addons.web.controllers.main as main
import yaml

# Returns yaml object for the yml file read
# @param filename, type: string, description: name of the file to be parsed
# @param path, type: string, description: path for the file (without slash '/' at the end)
# TODO: Move the code to a generic file to get accessed from anywhere


def get_config_file(filename, path):
        with open(path + '/' + filename, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as err:
                print(err)


class InheritHome(main.Home):

    # Overriding index function to append db to request.params
    # Updating 'db' parameters will make the given db to load and then open login page
    # No update in function params
    @http.route()
    def index(self, **kw):
        path = str(odoo.addons.project_init.__path__[0])
        filename = 'config.yml'
        configFile = get_config_file(filename, path)

        request.params.update({'db':configFile['database']})
        return super(InheritHome, self).index(**kw)

