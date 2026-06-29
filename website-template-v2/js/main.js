/* WebStaffr Client Site — main.js
   Lead capture, scroll effects, form validation */

(function () {
  'use strict';

  // ── WebStaffr Lead Capture ─────────────────────────────────────────────
  // client_id and api_base are injected by builder as data attributes on <body>
  const body = document.body;
  const CLIENT_ID = body.dataset.clientId || '';
  const API_BASE = body.dataset.apiBase || '';

  const form = document.getElementById('contact-form');
  if (form && CLIENT_ID && API_BASE) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      btn.textContent = 'Sending…';

      const payload = {
        client_id: CLIENT_ID,
        name: form.name?.value || form.querySelector('[name=name]')?.value,
        phone: form.phone?.value || form.querySelector('[name=phone]')?.value,
        email: form.email?.value || form.querySelector('[name=email]')?.value,
        message: form.message?.value || form.querySelector('[name=message]')?.value,
        source: 'form',
      };

      try {
        const resp = await fetch(API_BASE + '/webhooks/lead-form', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (resp.ok) {
          btn.textContent = '✓ We\'ll call you within the hour!';
          btn.style.background = '#10b981';
          form.querySelectorAll('input,textarea').forEach(el => el.disabled = true);
        } else {
          throw new Error('Server error');
        }
      } catch (err) {
        // Graceful fallback — show phone number
        btn.disabled = false;
        btn.textContent = 'Submit →';
        const phone = document.querySelector('.contact__phone');
        if (phone) {
          const msg = document.createElement('p');
          msg.style.cssText = 'color:#ef4444;font-size:.85rem;margin-top:.5rem;text-align:center';
          msg.textContent = 'Form error — please call us directly.';
          form.appendChild(msg);
        }
      }
    });
  }

  // ── Scroll Animations ─────────────────────────────────────────────────
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll(
      '.service-card, .review-card, .why-card, .story__text, .story__image'
    ).forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity .5s ease, transform .5s ease';
      observer.observe(el);
    });

    document.addEventListener('animationend', () => {}, false);
  }

  // Trigger visible state
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.visible').forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  });

  // ── Sticky Nav ────────────────────────────────────────────────────────
  const nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('nav--scrolled', window.scrollY > 50);
    }, { passive: true });
  }

  // ── Click-to-call tracking (basic) ───────────────────────────────────
  document.querySelectorAll('a[href^="tel:"]').forEach(link => {
    link.addEventListener('click', () => {
      if (typeof gtag === 'function') {
        gtag('event', 'phone_call_click', { event_category: 'contact' });
      }
    });
  });

})();

// Intersection visible class trigger
(function () {
  if (!('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll(
    '.service-card,.review-card,.why-card,.story__text,.story__image,.local__info'
  ).forEach(el => io.observe(el));
})();
