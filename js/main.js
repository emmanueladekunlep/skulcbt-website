// ====== SKULCBT - MAIN JAVASCRIPT ======
// Nigeria's #1 Offline-First School Platform
// Brand: Deep Green #006B45 | Gold #F2B900

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ====== INJECT STRUCTURED DATA (SEO) ======
    function injectStructuredData() {
        const scripts = [
            {
                type: 'application/ld+json',
                id: 'org-schema',
                content: {
                    "@context": "https://schema.org",
                    "@type": "Organization",
                    "name": "SkulCBT",
                    "description": "Nigeria's #1 Offline-First School Management and CBT Platform",
                    "url": "https://skulcbt.plccglobal.com",
                    "logo": "https://skulcbt.plccglobal.com/images/skulcbt-logo.png",
                    "foundingDate": "2020",
                    "founder": {
                        "@type": "Person",
                        "name": "Emmanuel Adekunle Peace"
                    },
                    "contactPoint": {
                        "@type": "ContactPoint",
                        "telephone": "+2347032977572",
                        "contactType": "Sales",
                        "availableLanguage": ["English"]
                    },
                    "sameAs": [
                        "https://facebook.com/skulcbt",
                        "https://instagram.com/skulcbt",
                        "https://linkedin.com/company/skulcbt"
                    ]
                }
            },
            {
                type: 'application/ld+json',
                id: 'website-schema',
                content: {
                    "@context": "https://schema.org",
                    "@type": "WebSite",
                    "name": "SkulCBT",
                    "url": "https://skulcbt.plccglobal.com",
                    "description": "Nigeria's #1 Offline-First School Management and CBT Platform",
                    "potentialAction": {
                        "@type": "SearchAction",
                        "target": "https://skulcbt.plccglobal.com/search?q={search_term_string}",
                        "query-input": "required name=search_term_string"
                    }
                }
            },
            {
                type: 'application/ld+json',
                id: 'local-business-schema',
                content: {
                    "@context": "https://schema.org",
                    "@type": "LocalBusiness",
                    "name": "SkulCBT",
                    "description": "Nigeria's #1 Offline-First School Management and CBT Platform",
                    "url": "https://skulcbt.plccglobal.com",
                    "telephone": "+2347032977572",
                    "email": "emmanueladekunlep@gmail.com",
                    "address": {
                        "@type": "PostalAddress",
                        "addressCountry": "NG"
                    },
                    "priceRange": "₦20,000 - ₦75,000"
                }
            }
        ];

        scripts.forEach(function(scriptData) {
            if (!document.getElementById(scriptData.id)) {
                const script = document.createElement('script');
                script.id = scriptData.id;
                script.type = scriptData.type;
                script.textContent = JSON.stringify(scriptData.content);
                document.head.appendChild(script);
            }
        });
    }

    injectStructuredData();

    // ====== MOBILE MENU TOGGLE ======
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            const isExpanded = !mobileMenu.classList.contains('hidden');
            mobileMenuToggle.setAttribute('aria-expanded', isExpanded);
            mobileMenuToggle.setAttribute('aria-label', isExpanded ? 'Close menu' : 'Open menu');
        });

        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                mobileMenuToggle.setAttribute('aria-label', 'Open menu');
            });
        });
    }

    // ====== HEADER SCROLL EFFECT ======
    const header = document.getElementById('header');
    let scrollTimeout;

    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }

        scrollTimeout = window.requestAnimationFrame(function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }, { passive: true });

    // ====== CONTACT FORM ======
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const name = document.getElementById('name')?.value?.trim() || '';
            const email = document.getElementById('email')?.value?.trim() || '';
            const phone = document.getElementById('phone')?.value?.trim() || '';
            const subject = document.getElementById('subject')?.value || '';
            const message = document.getElementById('message')?.value?.trim() || '';

            if (!name || !email || !subject || !message) {
                showToast('Please fill in all required fields.', 'error');
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showToast('Please enter a valid email address.', 'error');
                return;
            }

            // Track conversion event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'contact_form_submit', {
                    'event_category': 'engagement',
                    'event_label': 'Contact Form'
                });
            }

            const mailtoLink = `mailto:emmanueladekunlep@gmail.com?subject=${encodeURIComponent(subject)}&body=Name: ${encodeURIComponent(name)}%0AEmail: ${encodeURIComponent(email)}%0APhone: ${encodeURIComponent(phone)}%0A%0A${encodeURIComponent(message)}`;

            window.location.href = mailtoLink;
            showToast('Thank you! Your email client has been opened.', 'success');
            contactForm.reset();
        });
    }

    // ====== DEMO REQUEST FORM ======
    const demoForm = document.getElementById('demo-form');
    if (demoForm) {
        demoForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const fullname = document.getElementById('fullname')?.value?.trim() || '';
            const email = document.getElementById('email')?.value?.trim() || '';
            const phone = document.getElementById('phone')?.value?.trim() || '';
            const school = document.getElementById('school')?.value?.trim() || '';
            const role = document.getElementById('role')?.value || '';
            const students = document.getElementById('students')?.value || '';
            const plan = document.getElementById('plan')?.value || '';
            const message = document.getElementById('message')?.value?.trim() || '';

            if (!fullname || !email || !phone || !school || !role) {
                showToast('Please fill in all required fields.', 'error');
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showToast('Please enter a valid email address.', 'error');
                return;
            }

            // Track demo request conversion
            if (typeof gtag !== 'undefined') {
                gtag('event', 'demo_request_submit', {
                    'event_category': 'conversion',
                    'event_label': 'Demo Request',
                    'value': 1
                });
            }

            // Facebook Pixel conversion
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Lead', {
                    content_name: 'Demo Request',
                    content_category: 'School Management'
                });
            }

            const subject = `Demo Request - ${school}`;
            const body = `Full Name: ${fullname}%0AEmail: ${email}%0APhone: ${phone}%0ASchool: ${school}%0ARole: ${role}%0AStudents: ${students || 'Not specified'}%0APlan: ${plan || 'Not specified'}%0A%0AMessage:${message ? '%0A' + message : ''}`;

            const mailtoLink = `mailto:emmanueladekunlep@gmail.com?subject=${encodeURIComponent(subject)}&body=${body}`;

            window.location.href = mailtoLink;
            showToast('Demo request submitted! Redirecting...', 'success');

            setTimeout(function() {
                window.location.href = 'thank-you.html';
            }, 1500);
        });
    }

    // ====== NEWSLETTER SUBSCRIPTION ======
    const newsletterForms = document.querySelectorAll('footer form, .newsletter-form');
    newsletterForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput) {
                const email = emailInput.value.trim();
                if (!email) {
                    showToast('Please enter your email address.', 'error');
                    return;
                }

                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    showToast('Please enter a valid email address.', 'error');
                    return;
                }

                // Track newsletter signup
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'newsletter_signup', {
                        'event_category': 'engagement',
                        'event_label': 'Newsletter'
                    });
                }

                showToast('Thank you for subscribing!', 'success');
                emailInput.value = '';
            }
        });
    });

    // ====== TOAST NOTIFICATION SYSTEM ======
    function showToast(message, type) {
        const existingToast = document.querySelector('.skulcbt-toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = 'skulcbt-toast fixed top-24 right-4 z-50 px-6 py-4 rounded-lg shadow-2xl max-w-md transform transition-all duration-300 translate-x-0';
        toast.style.background = type === 'error' ? '#DC2626' : '#006B45';
        toast.style.color = '#FFFFFF';
        toast.style.borderLeft = '4px solid #F2B900';

        toast.innerHTML = `
            <div class="flex items-center space-x-3">
                <span class="text-xl">${type === 'error' ? '⚠️' : '✅'}</span>
                <span class="font-medium">${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(function() {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100px)';
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 4000);
    }

    // ====== SMOOTH SCROLL FOR ANCHOR LINKS ======
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                const headerHeight = document.getElementById('header')?.offsetHeight || 80;
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Update URL without scrolling
                if (history.pushState) {
                    history.pushState(null, null, targetId);
                }
            }
        });
    });

    // ====== LAZY LOAD IMAGES ======
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                        img.setAttribute('loading', 'lazy');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px'
        });

        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // ====== WHATSAPP BUTTON (with tracking) ======
    if (!document.querySelector('#whatsapp-button')) {
        const whatsappDiv = document.createElement('div');
        whatsappDiv.id = 'whatsapp-button';
        whatsappDiv.innerHTML = `
            <a href="https://wa.me/2347032977572" target="_blank"
               class="fixed bottom-6 right-6 bg-[#25D366] text-white rounded-full p-4 shadow-2xl hover:scale-110 transition-transform z-50 hover:shadow-lg"
               aria-label="Chat on WhatsApp"
               id="whatsapp-chat-btn"
               onclick="if(typeof gtag!=='undefined'){gtag('event','whatsapp_click',{'event_category':'contact','event_label':'WhatsApp'})}">
                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
            </a>
        `;
        document.body.appendChild(whatsappDiv);
    }

    // ====== PHONE CALL TRACKING ======
    document.querySelectorAll('a[href^="tel:"]').forEach(function(link) {
        link.addEventListener('click', function() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'phone_call_click', {
                    'event_category': 'contact',
                    'event_label': this.getAttribute('href')
                });
            }
        });
    });

    // ====== EXIT INTENT (for conversions) ======
    let exitIntentTriggered = false;
    document.addEventListener('mouseleave', function(e) {
        if (e.clientY < 0 && !exitIntentTriggered) {
            exitIntentTriggered = true;
            if (typeof gtag !== 'undefined') {
                gtag('event', 'exit_intent', {
                    'event_category': 'engagement',
                    'event_label': 'Exit Intent'
                });
            }
        }
    });

    // ====== SCROLL DEPTH TRACKING ======
    let maxScrollDepth = 0;
    window.addEventListener('scroll', function() {
        const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        if (scrollPercent > maxScrollDepth) {
            maxScrollDepth = scrollPercent;
            if (maxScrollDepth >= 25 && maxScrollDepth < 30) {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'scroll_depth', {
                        'event_category': 'engagement',
                        'event_label': '25%',
                        'value': 25
                    });
                }
            } else if (maxScrollDepth >= 50 && maxScrollDepth < 55) {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'scroll_depth', {
                        'event_category': 'engagement',
                        'event_label': '50%',
                        'value': 50
                    });
                }
            } else if (maxScrollDepth >= 75 && maxScrollDepth < 80) {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'scroll_depth', {
                        'event_category': 'engagement',
                        'event_label': '75%',
                        'value': 75
                    });
                }
            } else if (maxScrollDepth >= 90) {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'scroll_depth', {
                        'event_category': 'engagement',
                        'event_label': '90%+',
                        'value': 90
                    });
                }
            }
        }
    }, { passive: true });

    // ====== PAGE VIEW TRACKING (already handled by GA4) ======
    console.log('SkulCBT Website loaded successfully!');
    console.log('🇳🇬 Built for Nigerian Schools');
    console.log('📞 Contact: 07032977572');
    console.log('📧 Email: emmanueladekunlep@gmail.com');
});