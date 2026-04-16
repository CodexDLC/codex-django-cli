/* @provides cabinet.widgets.tabbed_assignment
   @depends cabinet.core.dom */
(function (window) {
    window.CabinetWidgets = window.CabinetWidgets || {};
    window.CabinetWidgets.createTabbedAssignment = function createTabbedAssignment(config) {
        return {
            activeKey: config.activeKey || '',
            switchTab(nextKey) {
                this.activeKey = nextKey;
                if (typeof config.onSwitch === 'function') {
                    config.onSwitch.call(this, nextKey);
                }
            },
        };
    };
})(window);
