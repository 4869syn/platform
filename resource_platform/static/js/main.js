document.addEventListener('DOMContentLoaded', function () {
    initCarousel();
    initMobileMenu();
});

function initCarousel() {
    var carousel = document.querySelector('.carousel');
    if (!carousel) return;

    var slides = carousel.querySelectorAll('.carousel-slide');
    var dots = carousel.querySelectorAll('.carousel-dot');
    var prevBtn = carousel.querySelector('.carousel-arrow.prev');
    var nextBtn = carousel.querySelector('.carousel-arrow.next');

    if (slides.length === 0) return;

    var current = 0;
    var timer = null;
    var interval = 3000;

    function showSlide(index) {
        slides.forEach(function (s, i) { s.classList.toggle('active', i === index); });
        dots.forEach(function (d, i) { d.classList.toggle('active', i === index); });
        current = index;
    }

    function next() {
        showSlide((current + 1) % slides.length);
    }

    function prev() {
        showSlide((current - 1 + slides.length) % slides.length);
    }

    function startAuto() {
        stopAuto();
        timer = setInterval(next, interval);
    }

    function stopAuto() {
        if (timer) clearInterval(timer);
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { prev(); startAuto(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { next(); startAuto(); });

    dots.forEach(function (dot, i) {
        dot.addEventListener('click', function () { showSlide(i); startAuto(); });
    });

    carousel.addEventListener('mouseenter', stopAuto);
    carousel.addEventListener('mouseleave', startAuto);

    showSlide(0);
    if (slides.length > 1) startAuto();
}

function initMobileMenu() {
    var toggle = document.querySelector('.menu-toggle');
    var menu = document.querySelector('.navbar-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', function () {
        menu.classList.toggle('show');
    });
}

