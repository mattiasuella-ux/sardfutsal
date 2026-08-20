document.addEventListener("DOMContentLoaded", function () {
  const menuToggle = document.querySelector(".menu-toggle");
  const mainNav = document.querySelector("#main-nav");

  if (menuToggle && mainNav) {
    menuToggle.addEventListener("click", function () {
      mainNav.classList.toggle("open");
      const isOpen = mainNav.classList.contains("open");
      menuToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      menuToggle.setAttribute("aria-label", isOpen ? "Chiudi menu" : "Apri menu");
      menuToggle.textContent = isOpen ? "✕" : "☰";
    });

    mainNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        mainNav.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Apri menu");
        menuToggle.textContent = "☰";
      });
    });
  }

  // =========================================
  // COOKIE CONSENT + GOOGLE ANALYTICS 4
  // Inserisci il tuo Measurement ID nel campo GA4_MEASUREMENT_ID
  // per attivare Analytics. Lasciandolo vuoto, nessun Analytics viene caricato.
  // =========================================
  const GA4_MEASUREMENT_ID = ""; // es. G-XXXXXXXXXX
  const CONSENT_KEY = "sardfutsal_cookie_consent_v1";

  function loadGoogleAnalytics() {
    if (!GA4_MEASUREMENT_ID || document.querySelector('script[data-sard-ga4="1"]')) return;

    window.dataLayer = window.dataLayer || [];
    function gtag(){ window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA4_MEASUREMENT_ID, { anonymize_ip: true });

    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_MEASUREMENT_ID);
    s.dataset.sardGa4 = '1';
    document.head.appendChild(s);
  }

  function createCookieBanner() {
    if (!GA4_MEASUREMENT_ID) return;
    const existing = document.getElementById('sard-cookie-banner');
    if (existing) return;

    const banner = document.createElement('aside');
    banner.id = 'sard-cookie-banner';
    banner.className = 'cookie-banner';
    banner.setAttribute('aria-label', 'Preferenze cookie');
    banner.innerHTML = `
      <div class="cookie-banner-inner">
        <div class="cookie-banner-text">
          <div class="cookie-banner-title">Cookie e analisi</div>
          <p>Utilizziamo Google Analytics per statistiche sull'utilizzo del sito. Gli strumenti di analisi che richiedono il consenso vengono attivati solo dopo la tua scelta. <a href="cookie.html">Cookie Policy</a> · <a href="privacy.html">Privacy Policy</a></p>
        </div>
        <div class="cookie-actions">
          <button type="button" class="cookie-btn" id="sard-cookie-reject">Rifiuta</button>
          <button type="button" class="cookie-btn accept" id="sard-cookie-accept">Accetta</button>
        </div>
      </div>`;
    document.body.appendChild(banner);

    document.getElementById('sard-cookie-accept').addEventListener('click', function(){
      localStorage.setItem(CONSENT_KEY, 'accepted');
      banner.classList.remove('is-visible');
      loadGoogleAnalytics();
    });
    document.getElementById('sard-cookie-reject').addEventListener('click', function(){
      localStorage.setItem(CONSENT_KEY, 'rejected');
      banner.classList.remove('is-visible');
    });
    return banner;
  }

  function showCookieBanner() {
    const banner = createCookieBanner();
    if (banner) banner.classList.add('is-visible');
  }

  window.sardFutsalOpenCookieSettings = function(){
    localStorage.removeItem(CONSENT_KEY);
    showCookieBanner();
  };

  if (GA4_MEASUREMENT_ID) {
    const consent = localStorage.getItem(CONSENT_KEY);
    if (consent === 'accepted') loadGoogleAnalytics();
    else if (!consent) showCookieBanner();
  }
});
