odoo.define('web.InheritProjectInit', function (require) {
   "use strict";

    require('web.WebClient').include({
        init: function(parent) {
            this._super();
            this.set('title_part', {"zopenerp": "ERP"});
        }
    });


    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var map_title ={
        user_error: _lt('Error'),
        warning: _lt('Warning'),
        access_error: _lt('Access Error'),
        missing_error: _lt('Missing Record'),
        validation_error: _lt('Validation Error'),
        except_orm: _lt('Global Business Error'),
        access_denied: _lt('Access Denied'),
    };


    require('web.CrashManager').include({
        show_warning: function(error) {
            if (!this.active) {
                return;
            }
            new Dialog(this, {
                size: 'medium',
                title: "ERP " + (_.str.capitalize(error.type) || _t("Warning")),
                subtitle: error.data.title,
                $content: $('<div>').html(QWeb.render('CrashManager.warning', {error: error}))
            }).open();
        },
        display: function() {
            var self = this;
            var error = this.error;
            error.data.message = error.data.arguments[0];

            new Dialog(this, {
                size: 'medium',
                title: "ERP " + (_.str.capitalize(error.type) || "Warning"),
                buttons: [
                    {text: error.data.arguments[2], classes : "btn-primary", click: function() {
                        window.location.href = '#action='+error.data.arguments[1];
                        self.destroy();
                    }},
                    {text: _t("Cancel"), click: function() { self.destroy(); }, close: true}
                ],
                $content: QWeb.render('CrashManager.warning', {error: error}),
            }).open();
        },
        rpc_error: function(error) {
            var self = this;
            if (!this.active) {
                return;
            }
            if (this.connection_lost) {
                return;
            }
            if (error.code == -32098) {
                core.bus.trigger('connection_lost');
                this.connection_lost = true;
                var timeinterval = setInterval(function() {
                    ajax.jsonRpc('/web/webclient/version_info').then(function() {
                        clearInterval(timeinterval);
                        core.bus.trigger('connection_restored');
                        self.connection_lost = false;
                    });
                }, 2000);
                return;
            }
            var handler = core.crash_registry.get(error.data.name, true);
            if (handler) {
                new (handler)(this, error).display();
                return;
            }
            if (error.data.name === "openerp.http.SessionExpiredException" || error.data.name === "werkzeug.exceptions.Forbidden") {
                this.show_warning({type: "Session Expired", data: { message: _t("Your ERP session expired. Please refresh the current web page.") }});
                return;
            }
            if (_.has(map_title, error.data.exception_type)) {
                if(error.data.exception_type == 'except_orm'){
                    if(error.data.arguments[1]) {
                        error = _.extend({}, error,
                                    {
                                        data: _.extend({}, error.data,
                                            {
                                                message: error.data.arguments[1],
                                                title: error.data.arguments[0] !== 'Warning' ? (" - " + error.data.arguments[0]) : '',
                                            })
                                    });
                    }
                    else {
                        error = _.extend({}, error,
                                    {
                                        data: _.extend({}, error.data,
                                            {
                                                message: error.data.arguments[0],
                                                title:  '',
                                            })
                                    });
                    }
                }
                else {
                    error = _.extend({}, error,
                                {
                                    data: _.extend({}, error.data,
                                        {
                                            message: error.data.arguments[0],
                                            title: map_title[error.data.exception_type] !== 'Warning' ? (" - " + map_title[error.data.exception_type]) : '',
                                        })
                                });
                }

                this.show_warning(error);
            //InternalError

            } else {
                this.show_error(error);
            }
        }
    });
});