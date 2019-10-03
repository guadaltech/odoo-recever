odoo.define('recever-connector.models', ['point_of_sale.models'], function (require) {
"use strict";

var models = require('point_of_sale.models');
var _super_posmodel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({

    push_and_invoice_order: function(order){
        try {
            document.querySelector('#recever-checkbox:checked').value
            var self = this;
            var invoiced = new $.Deferred();

            if(!order.get_client()){
                invoiced.reject({code:400, message:'Missing Customer', data:{}});
                return invoiced;
            }

            var order_id = this.db.add_order(order.export_as_JSON());

            this.flush_mutex.exec(function(){
                var done = new $.Deferred();
                var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout:30000, to_invoice:true});

                transfer.fail(function(error){
                    invoiced.reject(error);
                    done.reject();
                });

                transfer.pipe(function(order_server_id){

                    if (order_server_id.length) {
                        invoiced.resolve();
                        done.resolve();
                    } else {
                        invoiced.reject({code:401, message:'Backend Invoice', data:{order: order}});
                        done.reject();
                    }
                });
                return done;
            });
            return invoiced;
        } catch(error) {
            return _super_posmodel.push_and_invoice_order.apply(this, arguments);
        }
    },

});

});