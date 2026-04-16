/* @provides cabinet.core.dom */
(function (window) {
    window.CabinetCore = window.CabinetCore || {};

    window.CabinetCore.ensureNamespace = function ensureNamespace(path) {
        const parts = path.split('.');
        let cursor = window;
        parts.forEach((part) => {
            cursor[part] = cursor[part] || {};
            cursor = cursor[part];
        });
        return cursor;
    };
})(window);
