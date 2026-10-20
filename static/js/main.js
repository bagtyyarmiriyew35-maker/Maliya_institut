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
            if (window.innerWidth <= 1240) {
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
    let slideTimer = null;

    if (slides.length > 0) {
        const handleSlidePlayback = (slide) => {
            if (slideTimer) clearTimeout(slideTimer);

            // Stop and reset videos in non-active slides
            slides.forEach(s => {
                if (s !== slide) {
                    const v = s.querySelector('video');
                    if (v) {
                        v.pause();
                        v.currentTime = 0;
                    }
                }
            });

            const video = slide.querySelector('video');
            if (video) {
                video.currentTime = 0;
                video.muted = true;
                video.removeAttribute('loop');

                const playPromise = video.play();
                if (playPromise !== undefined) {
                    playPromise.catch(err => {
                        console.warn("Video playback interrupted, using fallback timer:", err);
                        slideTimer = setTimeout(nextSlide, 6000);
                    });
                }

                // Transition to next slide ONLY AFTER video finishes!
                video.onended = () => {
                    nextSlide();
                };
            } else {
                // Image slide: Wait 6 seconds before advancing
                slideTimer = setTimeout(nextSlide, 6000);
            }
        };

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
            const activeSlide = slides[currentSlide];
            activeSlide.classList.add('active');
            
            if (dots[currentSlide]) {
                dots[currentSlide].classList.add('active');
            }

            handleSlidePlayback(activeSlide);
        };

        const nextSlide = () => {
            showSlide(currentSlide + 1);
        };

        const prevSlide = () => {
            showSlide(currentSlide - 1);
        };

        // Event Listeners
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
            });
        }

        dots.forEach(dot => {
            dot.addEventListener('click', () => {
                const index = parseInt(dot.getAttribute('data-index'), 10);
                showSlide(index);
            });
        });

        // Initialize first slide playback
        handleSlidePlayback(slides[currentSlide]);
    }


    // --- 3. Stats Counter Animation ---
    const statCards = document.querySelectorAll('.stat-card');
    const statNumbers = document.querySelectorAll('.stat-number');
    
    if (statNumbers.length > 0) {
        const animateCounters = () => {
            statNumbers.forEach(stat => {
                const fullText = (stat.getAttribute('data-display-text') || stat.innerText).trim();
                const digitsMatch = fullText.replace(/[^0-9]/g, '');
                const target = parseInt(digitsMatch, 10);
                
                if (isNaN(target) || target <= 0) {
                    stat.innerText = fullText;
                    return;
                }
                
                const suffixMatch = fullText.replace(/^[0-9\s,\.]*/, '');
                const hasSpaceSep = fullText.includes(' ');
                
                let count = 0;
                const duration = 1800;
                const stepTime = 20;
                
                const increment = () => {
                    count += Math.ceil(target / (duration / stepTime));
                    
                    if (count >= target) {
                        stat.innerText = fullText;
                    } else {
                        let formatted = count.toLocaleString();
                        if (hasSpaceSep) {
                            formatted = formatted.replace(/,/g, ' ');
                        }
                        stat.innerText = formatted + (suffixMatch ? suffixMatch : '');
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

    // --- 6. News Card Video Autoplay (Muted & Loop) ---
    const cardVideos = document.querySelectorAll('.news-card-video');
    if (cardVideos.length > 0) {
        cardVideos.forEach(vid => {
            vid.muted = true;
            vid.setAttribute('playsinline', '');
            vid.setAttribute('muted', '');
            const tryPlay = () => {
                vid.muted = true;
                const p = vid.play();
                if (p !== undefined) p.catch(() => {});
            };
            tryPlay();
            const card = vid.closest('.news-card');
            if (card) {
                card.addEventListener('mouseenter', tryPlay);
                card.addEventListener('touchstart', tryPlay, { passive: true });
            }
        });

        if ('IntersectionObserver' in window) {
            const vidObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const v = entry.target;
                    if (entry.isIntersecting) {
                        v.muted = true;
                        const p = v.play();
                        if (p !== undefined) p.catch(() => {});
                    } else {
                        v.pause();
                    }
                });
            }, { threshold: 0.1 });

            cardVideos.forEach(v => vidObserver.observe(v));
        }
    }

    // --- 7. Language Selector Instant Switch ---
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const href = this.getAttribute('href') || '';
            const langMatch = href.match(/lang=([a-zA-Z]+)/);
            if (langMatch) {
                const l = langMatch[1].toLowerCase();
                const code = (l === 'eng' || l === 'en') ? 'eng' : ((l === 'rus' || l === 'ru') ? 'rus' : 'tm');
                document.cookie = "site_lang=" + code + ";path=/;max-age=31536000;SameSite=Lax";
            }
        });
    });
});
