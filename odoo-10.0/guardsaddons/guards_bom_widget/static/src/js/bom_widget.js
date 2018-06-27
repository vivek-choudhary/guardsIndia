openerp.guards_bom_widget = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var session = instance.web.session;
    var Dialog = instance.web.Dialog;

    local.BomWidget = instance.Widget.extend({
        template: 'BomWidgetTemplate',
        events: {
            'click button.bom': 'show_report',
            'click button.download-bom-report': 'download_report'
        },
        init: function(parent, options){
            this._super.apply(this, arguments);
            this.name=parent.name;
        },
        start: function() {
            this._super.apply(this, arguments);
            var that = this;
            this.load_products().then(function(data){
                self.$('.product-drop-down').after(QWeb.render('ProductDropDown', {'data': data}));
                self.$('.product-bom-drop-down').after(QWeb.render('ProductBomDropDown', {'data': []}));
                self.$('#id-product-drop-down').select2();
                self.$('#id-product-bom-drop-down').select2();
                self.$('#id-product-drop-down').on('change', that.load_product_bom);
            });
        },
        load_products: function(){
            var deferred_obj = new $.Deferred();
            var model = new instance.web.Model('guards.product');
            deferred_obj = model.query(['name']).all();
            return deferred_obj;
        },
        load_product_bom: function(event){
            var model = new instance.web.Model('guards.bom');
            model.query(['name']).filter([['product_id','=',parseInt(event.val)]]).all().then(
                function(data){
                    self.$('.product-bom-drop-down').after(QWeb.render('ProductBomDropDown', {'data': data}));
                    self.$('#s2id_id-product-bom-drop-down').remove();
                    self.$('#id-product-bom-drop-down').select2();
                }
            );

        },
        check_parameteres: function(bom, quantity){
            if(bom==undefined || quantity == undefined){
                new Dialog(this, {title: _t("Error"), size: 'medium', $content: $("<div/>").html(_t("Please fill in the required fields."))}).open();
                return false;
            }
            return true;
        },
        show_report: function(){
            var self = this;
            var product = this.$('#id-product-drop-down').val();
            var bom = this.$('#id-product-bom-drop-down').val();
            var quantity = this.$("input[name='bom-quantity']").val();

            if (!self.check_parameteres(bom, quantity))
                return false;
            this.clear_display();
            this.bom_report(product, bom, quantity);

        },
        clear_display: function(){
            var section = $('.render-section');
            if(section.length){
                section.children().remove();
            }
        },
        bom_report: function(product, bom, quantity){
            var stock_model = new instance.web.Model('guards.bom');
            stock_model.call('get_product_quantities_dict_widget', [bom, quantity],{context: new instance.web.CompoundContext()}).then(function(data){
               self.$('.render-section').append(QWeb.render('productInventoryList', {'data': data}))
            });
        },
        download_report: function(){
            var self = this;
            var origin = self.session.origin;
            var data = {};
            var product = this.$('#id-product-drop-down').val();
            data['bom_id'] = this.$('#id-product-bom-drop-down').val();
            data['quantity'] = this.$("input[name='bom-quantity']").val();


            if (!self.check_parameteres(data['bom_id'], data['quantity']))
                return false;

            self.session.rpc('/guard_product_bom/document',data).then(function(data){
                window.location= origin+data['url'];
            });
        }
    });

    instance.web.client_actions.add('sale.bom_calculation', 'instance.guards_bom_widget.BomWidget');
};
