openerp.guard_payments = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.HomePage = instance.Widget.extend({
        template: 'MyQWebTemplate',
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
            this.$el.find('#datetimepicker1').datetimepicker(this.options);
        },
    });

    instance.web.client_actions.add('report.report_page', 'instance.guard_payments.HomePage');
}
