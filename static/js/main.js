$(document).ready(function () {
    try {
        document.createEvent("TouchEvent");
        $('body').addClass('mobile');
    } catch (e) {
    }
});
