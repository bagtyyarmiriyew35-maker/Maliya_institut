document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Mobile Menu Toggle ---
    const mobileNavToggle = document.getElementById('mobileNavToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (mobileNavToggle && navMenu) {
        mobileNavToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            const icon = mobileNavToggle.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.className = 'fa-solid fa-xmark';
            } else {
                icon.className = 'fa-solid fa-bars';
            }
        });
    }

    // Toggle Dropdowns on Mobile
    const dropdownItems = document.querySelectorAll('.dropdown-item > a, .dropdown-submenu-item > a');
    dropdownItems.forEach(item => {
        item.addEventListener('click', (e) => {
            if (window.innerWidth <= 991) {
                e.preventDefault();
                const parent = item.parentElement;
                parent.classList.toggle('active-mobile');
            }
        });
    });


    // --- 2. Homepage Slider ---
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.getElementById('sliderPrev');
    const nextBtn = document.getElementById('sliderNext');
    let currentSlide = 0;
    let slideInterval;

    if (slides.length > 0) {
        const showSlide = (index) => {
            const nextIndex = (index + slides.length) % slides.length;
            if (nextIndex === currentSlide && slides[currentSlide].classList.contains('active')) return;
            
            const prevActiveSlide = slides[currentSlide];
            
            slides.forEach(slide => {
                slide.classList.remove('active');
                slide.classList.remove('exit');
            });
            dots.forEach(dot => dot.classList.remove('active'));
            
            if (prevActiveSlide) {
                prevActiveSlide.classList.add('exit');
            }
            
            currentSlide = nextIndex;
            slides[currentSlide].classList.add('active');
            
            if (dots[currentSlide]) {
                dots[currentSlide].classList.add('active');
            }
        };

        const nextSlide = () => {
            showSlide(currentSlide + 1);
        };

        const prevSlide = () => {
            showSlide(currentSlide - 1);
        };

        // Start Auto Slider
        const startAutoplay = () => {
            slideInterval = setInterval(nextSlide, 4000);
        };

        const resetAutoplay = () => {
            clearInterval(slideInterval);
            startAutoplay();
        };

        // Event Listeners
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                resetAutoplay();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                resetAutoplay();
            });
        }

        dots.forEach(dot => {
            dot.addEventListener('click', () => {
                const index = parseInt(dot.getAttribute('data-index'), 10);
                showSlide(index);
                resetAutoplay();
            });
        });

        startAutoplay();
    }


    // --- 3. Stats Counter Animation ---
    const statCards = document.querySelectorAll('.stat-card');
    const statNumbers = document.querySelectorAll('.stat-number');
    
    if (statNumbers.length > 0) {
        const animateCounters = () => {
            statNumbers.forEach(stat => {
                const target = parseInt(stat.getAttribute('data-target'), 10);
                const isPlus = stat.innerText.includes('+');
                let count = 0;
                const duration = 2000; // 2 seconds
                const stepTime = Math.max(Math.floor(duration / target), 15);
                
                const increment = () => {
                    const progress = count / target;
                    // Ease out quadratic
                    const easedStep = Math.ceil(target * (1 - Math.pow(1 - progress, 2)));
                    count += Math.ceil(target / (duration / stepTime));
                    
                    if (count >= target) {
                        stat.innerText = target.toLocaleString() + (isPlus ? '+' : '');
                    } else {
                        stat.innerText = easedStep.toLocaleString() + (isPlus ? '+' : '');
                        setTimeout(increment, stepTime);
                    }
                };
                increment();
            });
        };

        // Trigger when scrolling to the statistics block
        const observerOptions = {
            root: null,
            threshold: 0.2
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        const statsSection = document.querySelector('.stats-section');
        if (statsSection) {
            observer.observe(statsSection);
        }
    }
});
