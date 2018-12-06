openerp.guards_purchase_widget = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var session = instance.web.session;
    var Dialog = instance.web.Dialog;

    local.GuardsPurchaseWidget = instance.Widget.extend({
        template: 'GuardsPurchaseWidgetTemplate',
        events: {
            'click button.sale-widget-get-report': 'show_report',
            'click button.sale-widget-download-report': 'download_report'
        },
        init: function(parent, options){
            this._super.apply(this, arguments);
            this.name=parent.name;
            this.options = _.defaults(options || {}, {
                pickTime: this.type_of_date === 'datetime',
                useSeconds: this.type_of_date === 'datetime',
                format: 'DD/MM/YYYY',
                startDate: moment({ y: 1900 }),
                endDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                },
                language : moment.locale(),
            });
        },
        start: function() {
            this._super.apply(this, arguments);
            this.$el.find('.datetimepicker').datetimepicker(this.options);
            this.load_company().then(function(data){
                self.$('.company-drop-down').after(QWeb.render('CompanyDropDown', {'data': data}));
                self.$('#company').select2();
            });
        },
        load_company: function(){
            var deferred_obj = new $.Deferred();
            var model = new instance.web.Model('res.partner');
            deferred_obj = model.query(['name']).filter([['is_company','=',true]]).all();
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
            var from_date = this.$('#guards-sale-from').val();
            var to_date = this.$('#guards-sale-to').val();
            var company_id= this.$('#company').val();

            this.clear_display();
            from_date = from_date?from_date:'1/1/1991';
            to_date = to_date ? to_date : new Date();
            this.purchase(from_date, to_date, company_id);

        },
        clear_display: function(){
            var section = $('.render-section');
            if(section.length){
                section.children().remove();
            }
        },
        get_date: function(params_date){
            var date_array = [];
            if(params_date.length){
                date_array = params_date.split('/');
                return new Date(date_array[2], date_array[1], date_array[0]);
            }
            return params_date;
        },
        purchase: function(from_date, to_date, company){
            var model = new instance.web.Model('guards.purchase');
            var filter = ['|','&',['purchase_date','>',this.get_date(from_date)],
                                    ['purchase_date','<=',this.get_date(to_date)],['purchase_date','<=',new Date().toDateString()]];
            if(company != 'all') filter.push(['partner_id','=',parseInt(company)]);
            model.query(['partner_id', 'purchase_lines', 'purchase_date',
                'total_cost', 'status', 'invoice_number'])
                .filter(filter)
                .all().then(function(data){
                    data.forEach(function(element){
                        var purchase_product_lines_model = new instance.web.Model('guards.purchase.line');
                        var purchase_product_lines = purchase_product_lines_model.call('read',[element.purchase_lines]).then(function(purchase_line_data){
                            self.$('.purchase_table').append(QWeb.render('PurchaseWidgetProductTemplate', {'purchaseData': element, 'purchaseLines': purchase_line_data}))
                        });

                    });
                    self.$('.render-section').append(QWeb.render('PurchaseListTemplate', {'data': ''}))
            })
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

    instance.web.client_actions.add('guards_purchase_widget.guards_purchase_report_widget', 'instance.guards_purchase_widget.GuardsPurchaseWidget');
};
