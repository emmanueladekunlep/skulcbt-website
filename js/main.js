// ====== SKULCBT - MAIN JAVASCRIPT ======
// Nigeria's #1 Offline-First School Platform

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ====== MOBILE MENU TOGGLE ======
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            // Toggle aria-expanded
            const isExpanded = mobileMenu.classList.contains('hidden') === false;
            mobileMenuToggle.setAttribute('aria-expanded', isExpanded);
        });

        // Close mobile menu when a link is clicked
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // ====== HEADER SCROLL EFFECT ======
    const header = document.getElementById('header');
    let lastScrollY = 0;

    window.addEventListener('scroll', function() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScrollY = currentScrollY;
    });

    // ====== CONTACT FORM ======
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const name = document.getElementById('name')?.value || '';
            const email = document.getElementById('email')?.value || '';
            const phone = document.getElementById('phone')?.value || '';
            const subject = document.getElementById('subject')?.value || '';
            const message = document.getElementById('message')?.value || '';
            
            // Simple validation
            if (!name || !email || !subject || !message) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Build mailto link
            const mailtoLink = `mailto:emmanueladekunlep@gmail.com?subject=${encodeURIComponent(subject)}&body=Name: ${encodeURIComponent(name)}%0AEmail: ${encodeURIComponent(email)}%0APhone: ${encodeURIComponent(phone)}%0A%0A${encodeURIComponent(message)}`;
            
            // Open email client
            window.location.href = mailtoLink;
            
            // Show success message
            alert('Thank you for your message! Your email client has been opened. We\'ll respond within 24 hours.');
            
            // Reset form
            contactForm.reset();
        });
    }

    // ====== DEMO REQUEST FORM ======
    const demoForm = document.getElementById('demo-form');
    if (demoForm) {
        demoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const fullname = document.getElementById('fullname')?.value || '';
            const email = document.getElementById('email')?.value || '';
            const phone = document.getElementById('phone')?.value || '';
            const school = document.getElementById('school')?.value || '';
            const role = document.getElementById('role')?.value || '';
            const students = document.getElementById('students')?.value || '';
            const plan = document.getElementById('plan')?.value || '';
            const message = document.getElementById('message')?.value || '';
            
            // Validation
            if (!fullname || !email || !phone || !school || !role) {
                alert('Please fill in all required fields.');
                return;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Build mailto link
            const subject = `Demo Request - ${school}`;
            const body = `Full Name: ${fullname}%0AEmail: ${email}%0APhone: ${phone}%0ASchool: ${school}%0ARole: ${role}%0AStudents: ${students || 'Not specified'}%0APlan: ${plan || 'Not specified'}%0A%0AMessage:${message ? '%0A' + message : ''}`;
            
            const mailtoLink = `mailto:emmanueladekunlep@gmail.com?subject=${encodeURIComponent(subject)}&body=${body}`;
            
            // Open email client
            window.location.href = mailtoLink;
            
            // Show success message and redirect to thank you page
            alert('Thank you! Your demo request has been submitted. You will be redirected to our thank you page.');
            window.location.href = 'thank-you.html';
        });
    }

    // ====== SUBSCRIPTION NEWSLETTER FORM ======
    const newsletterForms = document.querySelectorAll('footer form');
    newsletterForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput) {
                const email = emailInput.value.trim();
                if (!email) {
                    alert('Please enter your email address.');
                    return;
                }
                
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    alert('Please enter a valid email address.');
                    return;
                }
                
                alert('Thank you for subscribing! You\'ll receive updates from SkulCBT.');
                emailInput.value = '';
            }
        });
    });

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
            }
        });
    });

    // ====== LAZY LOAD IMAGES (Performance) ======
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.getAttribute('data-src');
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // ====== WHATSAPP BUTTON (Fallback if not in HTML) ======
    // Check if WhatsApp button already exists
    if (!document.querySelector('#whatsapp-button')) {
        const whatsappDiv = document.createElement('div');
        whatsappDiv.id = 'whatsapp-button';
        whatsappDiv.innerHTML = `
            <a href="https://wa.me/2347032977572" target="_blank" 
               class="fixed bottom-6 right-6 bg-[#25D366] text-white rounded-full p-4 shadow-2xl hover:scale-110 transition-transform z-50"
               aria-label="Chat on WhatsApp">
                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
            </a>
        `;
        document.body.appendChild(whatsappDiv);
    }

    console.log('SkulCBT Website loaded successfully!');
    console.log('🇳🇬 Built for Nigerian Schools');
    console.log('📞 Contact: 07032977572');
    console.log('📧 Email: emmanueladekunlep@gmail.com');
});