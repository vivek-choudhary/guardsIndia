odoo.define('web.sale_bom', function (require) {
    "use strict";

    var ControlPanel = require('web.ControlPanel');
    var core = require('web.core');
    var data = require('web.data');
    var Dialog = require('web.Dialog');
    var common = require('web.form_common');
    var QWeb = core.qweb;


    var FormBomView = common.AbstractField.extend({
        template: "bomWidgetTemplateView",
        init: function(field_manager, node){
            this._super(field_manager, node);
        },
        start: function() {
            this._super.apply(this, arguments);
            this.re_render();
            this.on("change:value", this, function() {
                this.re_render();
            });
        },
        re_render: function(){
            var data = this.get_value();
            if(!data || data == "[]") return;
            data = data.substring(1, data.length -1).split(',');
            data = _.map(data, function(ele){
                ele = ele.trim();
                return ele.substring(1, ele.length -1).split(':');
            });
            this.$el.children().remove();
            this.$el.append(QWeb.render('bomWidgetView', {'data':data}));
        },
    });


    core.form_widget_registry.add(
        'bom_view', FormBomView
    );
});



