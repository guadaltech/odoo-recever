# -*- coding: utf-8 -*-
# Copyright 2019 Guadaltech Soluciones Tecnológicas S.L (<http://guadaltech.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import *
import requests
import json
import werkzeug.wrappers
from dateutil import tz
import time
from requests.exceptions import ConnectionError
import datetime


class PosRecever(models.Model):
    _name = "pos.recever"
    _description = "POS Recever configuration"

    name = fields.Char(string='name', default='Config')
    recever_license = fields.Char(string='License', help='obtain it at the Recever page.')
    recever_email = fields.Char(string='Email', help='obtain it at the Recever page.')
    recever_password = fields.Char(string='Password', help='obtain it at the Recever page.')
    recever_token = fields.Text(string='Token')
    recever_baseurl = fields.Char(string='Base url', default='https://api.recever.app/api')

    @api.model
    def create(self, vals):
        """ Limit to one record. """
        recever = self.env['pos.recever'].search([])
        if len(recever) >= 1:
            raise Warning(_("There can only be one configuration. Edit the created one."))
        else:
            return super(PosRecever, self).create(vals)

    def _token_request(self):
        """ Auxiliar method that obtains and saves the token needed for the API.
            Outputs ->  token: token obtained from the API """
        recever = self.env['pos.recever'].search([])[0]
        URLbase = recever.recever_baseurl
        DATAauth = {
            "email": recever.recever_email,
            "password": recever.recever_password,
            "license": recever.recever_license
        }
        HEADERauth = {
            "Content-Type": "application/json"
        }

        r1 = requests.post(URLbase + '/licenses/authentication', data=json.dumps(DATAauth), headers=HEADERauth)
        if r1.status_code != 200:
            error = json.loads(r1.text)["error"]["message"]
            raise Warning(_(error))
        else:
            token = "Bearer " + r1.json()['token']
            recever.write({
                'recever_token': token
            })
            self.env.cr.commit()
            return token

    @api.model
    def getAuth(self):
        """ Method that checks and return the token.
            Outputs ->  token: token obtained from the API
                        recever: recever config from the database """
        try:
            recever = self.env['pos.recever'].search([])[0]
            token = recever.recever_token
            if token:
                if (datetime.datetime.now() - recever.write_date).total_seconds() / 3600 >= 360:  # Expiration check
                    token = None

            if not token:  # Expired token
                token = self._token_request()

            return werkzeug.wrappers.Response(response=[token, recever],
                                              status=200)
        except IndexError:
            raise Warning(_("Recever configuration is empty. Fill it before you continue."))
        except ConnectionError:
            raise Warning(
                _("Connection has been lost. You can't use Recever offline."))
        except Exception as e:
            raise Warning(e)

    @api.multi
    def obtain_token(self):
        """ Method that checks the filled values. """
        try:
            self._token_request()
            view = self.env.ref('gst_recever.custom_recever_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = (_("The filled content is correct. You can use Recever now."))
            return {
                'name': (_('Success')),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.recever.wizard',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
                'context': context
            }
        except Exception as e:
            raise Warning(e)

    @api.model
    def getUserData(self, QR):
        """ Method that obtains the user data in order to fill the invoice.
            Inputs -> QR: QR of the Recever account on the APK.
            Outputs -> string that contains all the data of the user. """
        try:
            datos = self.getAuth()
            if datos.status_code != 200:
                raise Warning(datos.response)
            token = datos.response[0]
            recever = datos.response[1]

            r1 = requests.get(recever.recever_baseurl + '/qrs/' + QR + '/user', headers={"Authorization": token})

            if r1.status_code != 200:
                error = json.loads(r1.text)["error"]["message"]
                raise Warning(_(error))
            else:
                return r1.text
        except ConnectionError:
            raise Warning(
                _("Connection has been lost. You can't use Recever offline."))
        except Exception as e:
            raise Warning(e)

    @api.model
    def sendToRecever(self, id, QR, type, qrRefunded, **kw):
        """ Method that sends the ticket/invoice to Recever.
            Inputs ->   id: Pos Order uid.
                        QR: QR of the Recever account on the APK.
                        type: ticket or invoice.
        """
        self.env.cr.commit()
        try:
            datos = self.getAuth()
            if datos.status_code != 200:
                raise Warning(datos.response)
            token = datos.response[0]
            recever = datos.response[1]

            # -1 to avoid errors when something goes wrong
            order = self.env['pos.order'].search(
                [('pos_reference', 'like', '%' + id + '%'), ('qr_recever_code', '=', False)])[-1]

            if order:
                ### TICKET/INVOICE START
                ticket = {}
                items = []
                iva = {}

                for line in order.lines:
                    total = line.qty * line.price_subtotal
                    if line.tax_ids:
                        for tax in line.tax_ids:
                            iva[str(tax.amount).replace(".", ",")] = round(
                                float(iva.get(tax.amount, 0.0)) + round(tax.amount / 100 * total, 2), 2)

                    items.append({'cantidad':
                                      line.qty, 'descripcion': line.display_name, 'precio':
                                      round(line.price_subtotal, 2), 'total': round(total, 2)})

                ticket['items'] = items
                ticket['total'] = {'subTotal':
                                       round(order.amount_paid - order.amount_tax, 2), 'iva': iva, 'total': round(
                    order.amount_paid, 2), 'recibido':
                                       round((order.amount_paid + order.amount_return), 2), 'cambio':
                                       order.amount_return}
                config = order.session_id.config_id
                ticket['extra'] = {'numero_documento': order.name,
                                   'datos_fiscales_establecimiento': [config.street, config.city,
                                                                      config.state_id.display_name, config.zip,
                                                                      config.country_id.display_name],
                                   'mensaje_final': config.ticket_message}
                ### TICKET/INVOICE END

                DATAticket = {
                    "purchaseDate": order.date_order.astimezone(tz.gettz(order.user_id.tz)).isoformat(),
                    "name": id,
                    "ticketType": type,
                    "ticket": json.loads(json.dumps(ticket)),
                    "qrCode": QR,
                    "license": recever.recever_license,
                    "price": round(order.amount_paid, 2),
                    "qrRefunded": qrRefunded
                }

                print(json.dumps(DATAticket))

                HEADERticket = {
                    "Authorization": token,
                    "Content-Type": "application/json"
                }
                r2 = requests.post(recever.recever_baseurl + '/recevers/', data=json.dumps(DATAticket),
                                   headers=HEADERticket)

                if r2.status_code != 200:
                    error = json.loads(r2.text)["error"]["message"]
                    raise Warning(_(error))
                else:
                    order.qr_recever_code = json.loads(r2.text)['qr']['qrCode']
                    return (_("%s send.") % type)
            else:
                raise Warning(_("A server error has occurred. If it happens frequently, contact your provider."))
        except ConnectionError:
            # TODO Cancel the POS order
            raise Warning(
                _("Connection has been lost. You can't use Recever offline."))
        except Exception as e:
            # TODO Cancel the POS order
            raise Warning(e)

    @api.model
    def wait(self, lines):
        """ Auxiliary delay method.
            Inputs -> lines: number of orderlines.
        """
        espera = 0
        if lines >= 9:
            espera = 9
        else:
            if lines == 1 or lines == 2:
                espera = 3
            else:
                espera = lines + 1
        time.sleep(espera)
        return "I have slept %s seconds." % espera
