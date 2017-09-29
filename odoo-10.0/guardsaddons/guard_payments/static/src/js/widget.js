openerp.guard_payments = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var session = instance.web.session;

    local.HomePage = instance.Widget.extend({
        template: 'ReportTemplate',
        className: 'o_asdf_asdf',
        events: {
            'click button.report': 'show_report',
            'click button.xls-report': 'download_report'
        },
        init: function(parent, options){
            this._super.apply(this, arguments);
            this.name=parent.name;
            this.options = _.defaults(options || {}, {
                pickTime: this.type_of_date === 'datetime',
                useSeconds: this.type_of_date === 'datetime',
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
                self.$('.company-drop-down').after(QWeb.render('CompanyDropDown', {'data': data}))
            });
        },
        load_company: function(){
            var deferred_obj = new $.Deferred();
            var model = new instance.web.Model('res.partner');
            deferred_obj = model.query(['name']).filter([['is_company','=',true]]).all();
            return deferred_obj;
        },
        show_report: function(){
            var self = this;
            var type = this.$('#model-type').val();
            var from_date = this.$('#from').val();
            var to_date = this.$('#to').val();
            var company_id= this.$('#company').val();

            this.clear_display();
            from_date = from_date?from_date:'1/1/1991';
            to_date = to_date ? to_date : new Date();

            switch(type){
                case 'sale':
                    this.sale_report(from_date, to_date, company_id);
                    break;
                case 'purchase':
                    this.purchase_report(from_date, to_date, company_id);
                    break;
            }

        },
        clear_display: function(){
            var section = $('.render-section');
            if(section.length){
                section.children().remove();
            }
        },
        sale_report: function(from_date, to_date, company){
            var model = new instance.web.Model('guard.invoices');
            var filter = ['|','&',['due_date','>',from_date],['due_date','<=',to_date],['due_date','<=',new Date().toDateString()],['paid_flag','=',false]];
            if(company != 'all') filter.push(['customer','=',parseInt(company)]);
            model.query(['invoice_number', 'invoice_date', 'customer','company',
                'amount', 'due', 'overdue', 'overdue_flag'])
                .filter(filter)
                .all().then(function(data){
                    self.$('.render-section').append(QWeb.render('dataListSales', {'data': _.sortBy(data,'due')}))
            })
        },
        purchase_report: function(from_date, to_date, company){
            var model = new instance.web.Model('guard.payments');
            var filter = ['|','&',['due_date','>',from_date],['due_date','<=',to_date],['due_date','<=',new Date().toDateString()],['paid_flag','=',false]];
            if(company!='all') filter.push(['party_company','=',parseInt(company)]);
            model.query(['bill_number','bill_date', 'party_company','company', 'amount',
                'due', 'overdue', 'overdue_flag','due_flag'])
                .filter(filter)
                .all().then(function(data){
                    self.$('.render-section').append(QWeb.render('dataListPurchase', {'data': _.sortBy(data,'due')}))
            })
        },
        download_report: function(){
            var self = this;
            var data = {};
            var from_date = this.$('#from').val();
            var to_date = this.$('#to').val();
            var origin = self.session.origin;
            var type = this.$('#model-type').val();
            var company_id= this.$('#company').val();

            data['from_date'] = from_date?from_date:'1/1/1991';
            data['to_date'] = to_date ? to_date : (new Date()).toLocaleDateString();
            data['type'] = type;
            data['company_id']=false;
            if(company_id!='all'){
               data['company_id']=company_id;
            }

            self.session.rpc('/guard_payments/document',data).then(function(data){
                window.location= origin+data['url'];
            });
        }
    });

    instance.web.client_actions.add('report.report_page', 'instance.guard_payments.HomePage');
};
