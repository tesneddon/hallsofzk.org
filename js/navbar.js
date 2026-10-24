//Collapse the navbar on scroll
window.addEventListener('scroll', function() {
    document.querySelector('.navbar').classList.toggle('top-nav-collapse', window.scrollY > 50);
});

//Page scrolling feature, using the easeInOutExpo curve from jQuery Easing
function easeInOutExpo(t) {
    if (t === 0 || t === 1) {
        return t;
    }
    return t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2;
}

var scrollAnimation = null;

function scrollToY(to, duration) {
    var from = window.scrollY;
    var start = null;

    if (scrollAnimation !== null) {
        cancelAnimationFrame(scrollAnimation);
    }

    function step(timestamp) {
        if (start === null) {
            start = timestamp;
        }
        var t = Math.min((timestamp - start) / duration, 1);
        window.scrollTo(0, from + (to - from) * easeInOutExpo(t));
        scrollAnimation = t < 1 ? requestAnimationFrame(step) : null;
    }
    scrollAnimation = requestAnimationFrame(step);
}

document.querySelectorAll('.page-scroll a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(event) {
        var target = document.querySelector(anchor.getAttribute('href'));
        if (target === null) {
            return;
        }
        scrollToY(target.getBoundingClientRect().top + window.scrollY, 1500);
        event.preventDefault();
    });
});
