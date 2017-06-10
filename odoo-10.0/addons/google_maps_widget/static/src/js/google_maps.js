/**
 * Created by sudhanshu on 8/3/17.
 */
odoo.define('web.GoogleMaps', function (require) {

    "use strict";

    var Widget = require('web.Widget');

    var QWeb = core.qweb;
    var _t = core._t;


    var GoogleMap = Widget.extend({
        template: '',
        events:{},

        init: function(parent, options) {
            this._super(parent, options);
        },

        start: function(){
            this._super();
        },

        set_value: function(){},

        get_value: function(){},

    })
});