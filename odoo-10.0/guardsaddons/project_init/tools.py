# __author__ = 'Navyug Infosolutions Pvt. Ltd.'

import odoo
import yaml

from odoo.exceptions import UserError
from validate_email import validate_email

class ExtraTools:
    _name = 'Extra Tools'

    def __init__(self):
        self.filename = 'config.yml'

    def getConfigFile(self):
        with open(self.filename, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as err:
                print(err)
                
    @classmethod
    def onchange_state(cls, obj):
        res = {'domain': {'city_id': []}}
        state_id = None
        if obj.state_id:
            state_id = obj.state_id.id
        res['domain']['city_id'] = [('state_id', '=', state_id)]
        return res

    @classmethod
    def clear_city_pin(cls, obj):
        if 'city_id' in obj and obj.city_id:
                obj.city_id = None
        if 'pin' in obj and obj.pin:
            obj.pin = None

    @classmethod
    def onchange_city(cls, obj):
        res = {'domain': {'pin': []}}
        city_ids = []
        if obj.city_id.ids:
            city_ids = obj.city_id.ids
        res['domain']['pin'] = [('city_id', 'in', city_ids)]
        return res

    @classmethod
    def update_pin_ids(cls, obj):
        if 'pin' in obj and 'old_ids' in obj._context:
            old_ids = obj._context['old_ids']
            if len(obj.city_id.ids) > len(old_ids):
                # City added
                diff = list(set(obj.city_id.ids) - set(old_ids))
                result_ids = obj.env['res.city.zip'].search([('city_id', 'in', diff)]).ids
                current_ids = obj.pin.ids
                if not len(old_ids):
                    obj.pin = result_ids
                else:
                    current_ids.extend(result_ids)
                    obj.pin = current_ids
            elif len(old_ids) > len(obj.city_id.ids):
                # City removed
                diff = list(set(old_ids) - set(obj.city_id.ids))
                result_ids = obj.env['res.city.zip'].search([('city_id', 'in', diff)]).ids
                obj.pin = list(set(obj.pin.ids) - set(result_ids))

    @classmethod
    def onchange_country(cls, obj):
        """
        Function to update the domain of state_id
        :return: hash with updated domain
        """
        res = {'domain': {'state_id': []}}
        if obj.country_id:
            res['domain']['state_id'] = [('country_id', '=', obj.country_id.id)]
        return res

    @classmethod
    def validate_email(cls, obj):
        """
        Function to validate email.
        Uses validate_email library.
        :return:{}
        """
        if obj.email and not validate_email(obj.email):
            raise odoo.osv.osv.except_osv('Error', 'Invalid Email!')
        return {}

    @classmethod
    def validate_mobile(cls, obj):
        """
        Function to validate mobile number
        Raises exception when mobile number is invalid
        :return:{}
        """
        try:
            int(obj.mobile)
            if obj.mobile and not len(str(obj.mobile)) == 10:
                raise Exception
        except Exception as e:
            raise odoo.osv.osv.except_osv('Error', 'Invalid Mobile Number!')
        return {}

    @classmethod
    def validate_phone(cls, obj):
        """
        Function to validate phone number
        Raises exception when phone number is invalid
        :return:{}
        """
        try:
            int(obj.phone)
        except Exception as e:
            raise odoo.osv.osv.except_osv('Error', 'Invalid Phone Number!')
        return {}

    @classmethod
    def send_mail_to_sales_head(cls, env, ref, context):
        """
        The function is used to send email to users in the Sales Head group
        notifying the creation of new MF on the system
        :param env: Object of odoo.Enviorment
        :return:
        """
        users = env['res.groups'].search([('name', '=', 'Sales Head')])[0].users
        for user in users:
            template = env.ref(ref)
            template.with_context(context=context).send_mail(user.id)
        return True

    @classmethod
    def select_all_cities(cls, obj):
        cities = obj.env['res.state.city'].search([('state_id', '=', obj.state_id.id)])
        return cities.ids

    @classmethod
    def select_all_zip(cls, obj, cities):
        all_zip = obj.env['res.city.zip'].search([('city_id', 'in', cities)])
        return all_zip.ids

    @classmethod
    def update_region(cls, obj):
        all_regions = obj.env['project.res.region'].search([])
        for region in all_regions:
            master_cities = obj.env['res.state.city'].search([('state_id', '=', region.state_id.id)])
            master_zip = obj.env['res.city.zip'].search([('city_id', 'in', region.city_id.ids)])

            # Updating cities with their zip codes
            city_difference = set(region.city_id.ids) - set(master_cities.ids)
            if len(list(city_difference)):
                net_cities = list(set(region.city_id.ids) - city_difference)
                net_pin = obj.env['res.city.zip'].search([('city_id', 'in', net_cities)]).ids
                region.write({'city_id': [(6, 0, net_cities)], 'pin': [(6, 0, net_pin)]})

            # Updating zip codes
            pin_difference = set(region.pin.ids) - set(master_zip.ids)
            if len(pin_difference):
                net_pin = list(set(region.pin.ids) - pin_difference)
                region.write({'pin': [(6, 0, net_pin)]})
