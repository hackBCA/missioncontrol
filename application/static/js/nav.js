(function (window, document) {

    var layout = document.querySelector('.page-container'),
        full_layout = document.querySelector('.full-page-container'),
        menu = document.getElementById('menu'),
        menuLink = document.getElementById('menuLink');

    function toggleClass(element, className) {
        var classes = element.className.split(/\s+/),
            length = classes.length;

        for(var i = 0; i < length; i++) {
          if (classes[i] === className) {
            classes.splice(i, 1);
            break;
          }
        }
        // The className is not found
        if (length === classes.length) {
            classes.push(className);
        }

        element.className = classes.join(' ');
    }

    menuLink.onclick = function (e) {
        var active = 'active';

        e.preventDefault();
        if (layout) {
            toggleClass(layout, active);
        } else if (full_layout) {
            toggleClass(full_layout, active);
        }
        toggleClass(menu, active);
        toggleClass(menuLink, active);
    };

}(this, this.document));