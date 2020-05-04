$(document).ready(function () {
    try {
        document.createEvent("TouchEvent");
        $('body').addClass('mobile');
    } catch (e) {
    }

    $('.image-btn').click(function () {
        $(this).children().first().toggleClass('description-show');
        $(this).toggleClass('description-show');
    });
    $('.image-btn').mouseleave(function () {
        $(this).children().first().removeClass('description-show');
        $(this).removeClass('description-show');
    });
});
