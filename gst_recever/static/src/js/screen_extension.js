odoo.define('recever-connector.screens', ['point_of_sale.models','point_of_sale.screens','web.core','point_of_sale.gui', 'web.rpc'], function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var gui = require('point_of_sale.gui');
var _t = core._t;
var rpc = require('web.rpc');

models.load_fields("res.partner", "qr_recever_code");

screens.PaymentScreenWidget.include({

    validate_order: function(force_validation) {
        var self = this;
        if(document.querySelector('#recever-checkbox:checked') || document.querySelector('#irecever-checkbox:checked')) {
            var order = self.pos.get_order();
            var client = order.attributes.client;
            var QR, type, qrRefunded;
            if(document.querySelector('#irecever-checkbox:checked')) { //irecever
                if(client!= null) {
                    if(!client.qr_recever_code) {
                        self.gui.show_popup('error',{
                            'title': _t('Wrong client'),
                            'body':  _t('Client must have a QR code.'),
                        });
                    } else {
                        type = 'factura';
                        QR = client.qr_recever_code;
                    }
                } else {
                    self.gui.show_popup('error',{
                        'title': _t('Empty client'),
                        'body':  _t('You need to select a client in order to use iRecever.'),
                    });
                }
            } else { //recever
                if(document.getElementsByClassName('input-qr-real')[0].value == "") {
                   self.gui.show_popup('error',{
                        'title': _t('empty QR'),
                        'body':  _t('You must add a QR in order to make a Recever.'),
                   });
                } else {
                    type = 'ticket';
                    QR = document.getElementsByClassName('input-qr-real')[0].value;
                }
            }

            if(document.getElementsByClassName('qr-refunded')[0].value != "") {
                qrRefunded = document.getElementsByClassName('qr-refunded')[0].value
            };

            if(type) {
                rpc.query({
                    model: 'pos.recever',
                    method: 'getUserData',
                    args: [QR]
                }).then(function(resUser){
                    if (self.order_is_valid(force_validation)) {
                        self.finalize_validation();
                        document.getElementsByClassName('button next highlight')[0].hidden = true;
                    }
                    rpc.query({
                        model: 'pos.recever',
                        method: 'wait',
                        args: [order.orderlines.length]
                    }).then(function(resWait){
                        console.log(resWait)
                        rpc.query({
                                model: 'pos.recever',
                                method: 'sendToRecever',
                                args: [order.uid, QR, type, qrRefunded]
                        }).then(function(resRecever){
                            self.gui.show_popup('alert',{
                                'title': _t('Success'),
                                'body':  _t(resRecever),
                            });
                            document.getElementsByClassName('button next highlight')[0].hidden = false;
                        }, function(err,ev){
                            document.getElementsByClassName('button next highlight')[0].hidden = false;
                            ev.preventDefault();
                            self.gui.show_popup('error',{
                                'title': _t('Error'),
                                'body':  _t(err["data"]["arguments"][0]),
                            });
                        });
                    }, function(err, ev) {
                        document.getElementsByClassName('button next highlight')[0].hidden = false;
                        ev.preventDefault();
                        self.gui.show_popup('error',{
                            'title': _t('Error'),
                            'body':  _t(err["data"]["arguments"][0]),
                        });
                    });
                }, function(err, ev) {
                    document.getElementsByClassName('button next highlight')[0].hidden = false;
                    ev.preventDefault();
                    self.gui.show_popup('error',{
                        'title': _t('Error'),
                        'body':  _t(err["data"]["arguments"][0]),
                    });
                });
            }

        } else { //sin recever
            document.getElementsByClassName('button next highlight')[0].hidden = false;
            this._super(force_validation);
        }
    },

    renderElement: function(){

        var self = this;
        this._super();
        this.$('.search.box').hide();
        this.$('.refunded.box').hide();

        this.$('#recever-checkbox').change(function(event) {
            var order = self.pos.get_order();
            var client = order.attributes.client;
            if($(this).prop("checked")){
                $('#irecever-checkbox').prop("checked", false);
                $('.button.js_invoice').removeClass('highlight');
                order.set_to_invoice(false);
                $('.search.box').show();
                document.getElementsByClassName('button search-customer')[0].style.display = 'none';
                document.getElementsByClassName('refunded box')[0].style.display = 'block';

            } else {
                $('.search.box').hide();
                $('.refunded.box').hide();
            }
        });

        this.$('#irecever-checkbox').change(function(event) {
            var order = self.pos.get_order();
            var client = order.attributes.client;
            if($(this).prop("checked")){
                $('#recever-checkbox').prop("checked", false);
                $('.button.js_invoice').addClass('highlight');
                order.set_to_invoice(true);
                $('.search.box').show();
                document.getElementsByClassName('button search-customer')[0].style.display = 'inline-block';
                document.getElementsByClassName('refunded box')[0].style.display = 'block';
            } else {
                $('.search.box').hide();
                $('.refunded.box').hide();
                $('.button.js_invoice').removeClass('highlight');
                order.set_to_invoice(false);
            }
        });

        // Avoids the focus on the numpad
        this.$('.input-qr-real').keypress(function(event) {
            event.stopPropagation();
        });
        this.$('.input-qr-real').keydown(function(event) {
            event.stopPropagation();
        });
        this.$('.input-qr-real').keyup(function(event) {
            event.stopPropagation();
        });
        this.$('input.qr-refunded').keypress(function(event) {
            event.stopPropagation();
        });
        this.$('input.qr-refunded').keydown(function(event) {
            event.stopPropagation();
        });
        this.$('input.qr-refunded').keyup(function(event) {
            event.stopPropagation();
        });

        this.$('.search-customer').click(function() {
            var QR = document.getElementsByClassName('input-qr-real')[0].value
            if(QR == "") {
               self.gui.show_popup('error',{
                    'title': _t('empty QR'),
                    'body':  _t('You must add a QR in order to use Recever.'),
               });
            } else {
                var customers = self.pos.db.get_partners_sorted(1000);
                var found = false;
                for(var c = 0; c < customers.length; c++) {
                    if(customers[c].qr_recever_code == QR) {
                        self.new_client = customers[c];
                        var order = self.pos.get_order();
                        var bool = false;
                        if( self.old_client && self.new_client ){
                            bool = self.old_client.id !== self.new_client.id;
                        }else{
                            bool = !!self.old_client !== !!self.new_client;
                        }
                        if(bool){
                            var default_fiscal_position_id = _.findWhere(self.pos.fiscal_positions, {'id': self.pos.config.default_fiscal_position_id[0]});
                            if ( self.new_client ) {
                                if (self.new_client.property_account_position_id ){
                                    var client_fiscal_position_id = _.findWhere(self.pos.fiscal_positions, {'id': self.new_client.property_account_position_id[0]});
                                    order.fiscal_position = client_fiscal_position_id || default_fiscal_position_id;
                                }
                                order.set_pricelist(_.findWhere(self.pos.pricelists, {'id': self.new_client.property_product_pricelist[0]}) || self.pos.default_pricelist);
                            } else {
                                order.fiscal_position = default_fiscal_position_id;
                                order.set_pricelist(self.pos.default_pricelist);
                            }
                            order.set_client(self.new_client);
                        }
                        found = true;
                        break;
                    }
                }
                if(!found) {
                    self.gui.show_popup('confirm',{
                        'title': _t('Non-existent client'),
                        'body': _t('You need to create a new client to use Recever.'),
                        confirm: function(){
                            self.gui.show_screen('clientlist', null, true);
                        },
                    });
                }
            }
        });
    },

    click_invoice: function(){
        var self = this;
        if(!(document.querySelector('#recever-checkbox:checked') || document.querySelector('#irecever-checkbox:checked'))) {
            this._super();
        }
    },
});

screens.ClientListScreenWidget.include({

    show: function(){
        var self = this;
        this._super();

        this.$('.new-customer').click(function(){
            if($('#irecever-checkbox').prop("checked")) {
                var qr = document.getElementsByClassName('input-qr-real')[0].value
                if(qr != "") {
                    rpc.query({
                        model: 'pos.recever',
                        method: 'getUserData',
                        args: [qr]
                    }).then(function(response){
                        console.log(response)
                        var res = JSON.parse(response)
                        document.getElementsByClassName('detail client-name')[0].value = res["name"]
                        document.getElementsByClassName('detail client-address-street')[0].value = res["taxData"]["residence"]
                        document.getElementsByClassName('detail client-address-city')[0].value = res["taxData"]["locality"]
                        document.getElementsByClassName('detail client-address-zip')[0].value = res["postalCode"]
                        document.getElementsByClassName('detail vat')[0].value = res["taxData"]["nif"]
                        document.getElementsByClassName('detail client-recever')[0].value = qr

                    }, function(error, ev) {
                        ev.preventDefault();
                        self.gui.show_popup('error',{
                            'title': _t('Error'),
                            'body':  _t(error["data"]["arguments"][0]),
                        });
                    });
                } else {
                    self.gui.show_popup('error',{
                        'title': _t('empty QR'),
                        'body':  _t('You must add a QR in order to use Recever.'),
                    });
                }
            }
        });
    }
});
});

