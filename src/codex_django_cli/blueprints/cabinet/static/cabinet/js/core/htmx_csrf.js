/* @provides cabinet.core.htmx_csrf
   @depends cabinet.core.dom */
(function (window, document) {
    document.addEventListener('htmx:configRequest', function (evt) {
        const method = evt.detail.verb.toUpperCase();
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
            const token = document.cookie.match(/csrftoken=([^;]+)/);
            if (token) {
                evt.detail.headers['X-CSRFToken'] = token[1];
            }
        }
    });
})(window, document);
