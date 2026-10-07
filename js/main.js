// ====== SKULCBT - MAIN JAVASCRIPT v2 ======
// Brand: Green #0D6841 | Gold #D4AF37

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // ====== STRUCTURED DATA ======
    function injectStructuredData() {
        var scripts = [
            { id: 'org-schema', content: {
                "@context": "https://schema.org", "@type": "Organization",
                "name": "SkulCBT",
                "description": "Nigeria's #1 Offline-First School Management and CBT Platform",
                "url": "https://skulcbt.plccglobal.com",
                "logo": "https://skulcbt.plccglobal.com/images/skulcbt-logo.png",
                "foundingDate": "2020",
                "founder": { "@type": "Person", "name": "Emmanuel Adekunle Peace" },
                "contactPoint": { "@type": "ContactPoint", "telephone": "+2347032977572", "contactType": "Sales", "availableLanguage": ["English"] },
                "sameAs": ["https://facebook.com/skulcbt","https://instagram.com/skulcbt","https://linkedin.com/company/skulcbt"]
            }},
            { id: 'website-schema', content: {
                "@context": "https://schema.org", "@type": "WebSite",
                "name": "SkulCBT", "url": "https://skulcbt.plccglobal.com",
                "description": "Nigeria's #1 Offline-First School Management and CBT Platform"
            }},
            { id: 'local-business-schema', content: {
                "@context": "https://schema.org", "@type": "LocalBusiness",
                "name": "SkulCBT",
                "description": "Nigeria's #1 Offline-First School Management and CBT Platform",
                "url": "https://skulcbt.plccglobal.com",
                "telephone": "+2347032977572",
                "email": "emmanueladekunlep@gmail.com",
                "address": { "@type": "PostalAddress", "addressCountry": "NG" },
                "priceRange": "NGN 20,000 - NGN 600,000"
            }}
        ];
        scripts.forEach(function (s) {
            if (!document.getElementById(s.id)) {
                var el = document.createElement('script');
                el.id = s.id;
                el.type = 'application/ld+json';
                el.textContent = JSON.stringify(s.content);
                document.head.appendChild(el);
            }
        });
    }
    injectStructuredData();

    // ====== MOBILE MENU ======
    var toggle = document.getElementById('mobile-menu-toggle');
    var menu = document.getElementById('mobile-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            menu.classList.toggle('open');
            var open = menu.classList.contains('open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        });
        menu.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () {
                menu.classList.remove('open');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.setAttribute('aria-label', 'Open menu');
            });
        });
    }

    // ====== HEADER SHRINK ======
    var header = document.getElementById('header');
    if (header) {
        var ticking = false;
        window.addEventListener('scroll', function () {
            if (!ticking) {
                window.requestAnimationFrame(function () {
                    header.classList.toggle('scrolled', window.scrollY > 40);
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    // ====== SCROLL REVEAL ======
    var revealSelectors = '.reveal, .reveal-left, .reveal-right, .reveal-zoom, .stagger';
    var revealEls = document.querySelectorAll(revealSelectors);
    if ('IntersectionObserver' in window && revealEls.length) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
        revealEls.forEach(function (el) { io.observe(el); });
    } else {
        revealEls.forEach(function (el) { el.classList.add('visible'); });
    }

    // ====== TOAST ======
    function showToast(message, type) {
        var existing = document.querySelector('.skulcbt-toast');
        if (existing) existing.remove();
        var toast = document.createElement('div');
        toast.className = 'skulcbt-toast';
        toast.setAttribute('role', 'status');
        toast.style.cssText =
            'position:fixed;top:96px;right:16px;z-index:9999;padding:14px 20px;border-radius:12px;' +
            'max-width:380px;color:#fff;font-weight:500;box-shadow:0 10px 30px rgba(0,0,0,0.2);' +
            'background:' + (type === 'error' ? '#DC2626' : '#0D6841') + ';border-left:4px solid #D4AF37;' +
            'transition:opacity 0.3s,transform 0.3s;opacity:1;transform:translateX(0);';
        toast.innerHTML = '<span style="margin-right:8px">' + (type === 'error' ? '!' : 'OK') + '</span>' + message;
        document.body.appendChild(toast);
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(60px)';
            setTimeout(function () { toast.remove(); }, 320);
        }, 4000);
    }
    window.showToast = showToast;

    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // ====== CONTACT FORM ======
    var contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var name = (document.getElementById('name') || {}).value || '';
            var email = (document.getElementById('email') || {}).value || '';
            var phone = (document.getElementById('phone') || {}).value || '';
            var subject = (document.getElementById('subject') || {}).value || '';
            var message = (document.getElementById('message') || {}).value || '';
            if (!name.trim() || !email.trim() || !subject || !message.trim()) {
                showToast('Please fill in all required fields.', 'error'); return;
            }
            if (!emailRegex.test(email.trim())) {
                showToast('Please enter a valid email address.', 'error'); return;
            }
            if (typeof gtag !== 'undefined') gtag('event', 'contact_form_submit', { event_category: 'engagement', event_label: 'Contact Form' });
            var mailto = 'mailto:emmanueladekunlep@gmail.com?subject=' + encodeURIComponent(subject) +
                '&body=Name: ' + encodeURIComponent(name) + '%0AEmail: ' + encodeURIComponent(email) +
                '%0APhone: ' + encodeURIComponent(phone) + '%0A%0A' + encodeURIComponent(message);
            window.location.href = mailto;
            showToast('Thank you! Your email client has been opened.', 'success');
            contactForm.reset();
        });
    }

    // ====== DEMO FORM ======
    var demoForm = document.getElementById('demo-form');
    if (demoForm) {
        demoForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var fullname = (document.getElementById('fullname') || {}).value || '';
            var email = (document.getElementById('email') || {}).value || '';
            var phone = (document.getElementById('phone') || {}).value || '';
            var school = (document.getElementById('school') || {}).value || '';
            var role = (document.getElementById('role') || {}).value || '';
            var students = (document.getElementById('students') || {}).value || '';
            var plan = (document.getElementById('plan') || {}).value || '';
            var message = (document.getElementById('message') || {}).value || '';
            if (!fullname.trim() || !email.trim() || !phone.trim() || !school.trim() || !role) {
                showToast('Please fill in all required fields.', 'error'); return;
            }
            if (!emailRegex.test(email.trim())) {
                showToast('Please enter a valid email address.', 'error'); return;
            }
            if (typeof gtag !== 'undefined') gtag('event', 'demo_request_submit', { event_category: 'conversion', event_label: 'Demo Request', value: 1 });
            if (typeof fbq !== 'undefined') fbq('track', 'Lead', { content_name: 'Demo Request', content_category: 'School Management' });
            var subj = 'Demo Request - ' + school;
            var body = 'Full Name: ' + fullname + '%0AEmail: ' + email + '%0APhone: ' + phone + '%0ASchool: ' + school +
                '%0ARole: ' + role + '%0AStudents: ' + (students || 'Not specified') + '%0APlan: ' + (plan || 'Not specified') +
                '%0A%0AMessage:' + (message ? '%0A' + message : '');
            window.location.href = 'mailto:emmanueladekunlep@gmail.com?subject=' + encodeURIComponent(subj) + '&body=' + body;
            showToast('Demo request submitted! Redirecting...', 'success');
            setTimeout(function () { window.location.href = 'thank-you.html'; }, 1500);
        });
    }

    // ====== NEWSLETTER ======
    document.querySelectorAll('footer form, .newsletter-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var input = form.querySelector('input[type="email"]');
            if (!input) return;
            var email = input.value.trim();
            if (!email) { showToast('Please enter your email address.', 'error'); return; }
            if (!emailRegex.test(email)) { showToast('Please enter a valid email address.', 'error'); return; }
            if (typeof gtag !== 'undefined') gtag('event', 'newsletter_signup', { event_category: 'engagement', event_label: 'Newsletter' });
            showToast('Thank you for subscribing!', 'success');
            input.value = '';
        });
    });

    // ====== SMOOTH SCROLL (internal anchors) ======
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
        a.addEventListener('click', function (e) {
            var id = this.getAttribute('href');
            if (id === '#' || id.length < 2) return;
            var target = document.querySelector(id);
            if (!target) return;
            e.preventDefault();
            var hh = (document.getElementById('header') || {}).offsetHeight || 80;
            var top = target.getBoundingClientRect().top + window.pageYOffset - hh - 16;
            window.scrollTo({ top: top, behavior: 'smooth' });
            if (history.pushState) history.pushState(null, null, id);
        });
    });

    // ====== LAZY IMAGES ======
    if ('IntersectionObserver' in window) {
        var lazy = document.querySelectorAll('img[data-src]');
        if (lazy.length) {
            var iio = new IntersectionObserver(function (entries) {
                entries.forEach(function (en) {
                    if (en.isIntersecting) {
                        var img = en.target;
                        img.src = img.getAttribute('data-src');
                        img.removeAttribute('data-src');
                        img.setAttribute('loading', 'lazy');
                        iio.unobserve(img);
                    }
                });
            }, { rootMargin: '80px' });
            lazy.forEach(function (i) { iio.observe(i); });
        }
    }

    // ====== WHATSAPP BUTTON ======
    if (!document.querySelector('#whatsapp-button')) {
        var wa = document.createElement('div');
        wa.id = 'whatsapp-button';
        wa.innerHTML =
            '<a href="https://wa.me/2347032977572" target="_blank" rel="noopener" ' +
            'aria-label="Chat on WhatsApp" id="whatsapp-chat-btn" ' +
            'style="position:fixed;bottom:24px;right:24px;background:#25D366;color:#fff;border-radius:9999px;padding:14px;box-shadow:0 8px 24px rgba(0,0,0,0.2);z-index:9998;display:inline-flex;align-items:center;justify-content:center;">' +
            '<svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>';
        document.body.appendChild(wa);
    }

    // ====== TRACKING (phone, exit intent, scroll depth) ======
    document.querySelectorAll('a[href^="tel:"]').forEach(function (link) {
        link.addEventListener('click', function () {
            if (typeof gtag !== 'undefined') gtag('event', 'phone_call_click', { event_category: 'contact', event_label: this.getAttribute('href') });
        });
    });

    var exitFired = false;
    document.addEventListener('mouseleave', function (e) {
        if (e.clientY < 0 && !exitFired) {
            exitFired = true;
            if (typeof gtag !== 'undefined') gtag('event', 'exit_intent', { event_category: 'engagement', event_label: 'Exit Intent' });
        }
    });

    var maxDepth = 0, depthFlags = { 25: false, 50: false, 75: false, 90: false };
    window.addEventListener('scroll', function () {
        var total = document.documentElement.scrollHeight - window.innerHeight;
        if (total <= 0) return;
        var pct = (window.scrollY / total) * 100;
        if (pct > maxDepth) {
            maxDepth = pct;
            [25, 50, 75, 90].forEach(function (m) {
                if (maxDepth >= m && !depthFlags[m]) {
                    depthFlags[m] = true;
                    if (typeof gtag !== 'undefined') gtag('event', 'scroll_depth', { event_category: 'engagement', event_label: m + '%', value: m });
                }
            });
        }
    }, { passive: true });

    console.log('SkulCBT website loaded.');
});
