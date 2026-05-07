// @cosabella — Main JS

document.documentElement.classList.add('js-enabled');

const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');
const navDropdown = document.querySelector('.nav-dropdown');

if (navToggle && navMenu) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    navToggle.classList.toggle('active');
    navToggle.setAttribute('aria-expanded', navMenu.classList.contains('active') ? 'true' : 'false');
  });

  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
      navMenu.classList.remove('active');
      navToggle.classList.remove('active');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

if (navDropdown && navMenu) {
  const trigger = navDropdown.querySelector('.nav-link');
  trigger?.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
      e.preventDefault();
      navDropdown.classList.toggle('open');
    }
  });
}

const flashes = document.querySelectorAll('.flash');
flashes.forEach((flash) => {
  setTimeout(() => {
    flash.style.opacity = '0';
    flash.style.transition = 'opacity 0.5s ease';
    setTimeout(() => flash.remove(), 500);
  }, 4000);
});

const navbar = document.querySelector('.navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.style.boxShadow = window.scrollY > 20
      ? '0 8px 28px rgba(0,0,0,0.14)'
      : '0 2px 8px rgba(0,0,0,0.08)';
  });
}

window.changeImage = function changeImage(button) {
  const image = button.querySelector('img');
  const mainImage = document.getElementById('mainImage');
  if (!image || !mainImage) return;

  mainImage.src = image.src;
  mainImage.alt = image.alt;
  document.querySelectorAll('.gallery-thumb-btn').forEach((btn) => btn.classList.remove('active'));
  button.classList.add('active');
};

window.increaseQty = function increaseQty() {
  const qty = document.getElementById('cantidad');
  if (!qty) return;
  qty.value = Math.max(1, Number(qty.value || 1) + 1);
};

window.decreaseQty = function decreaseQty() {
  const qty = document.getElementById('cantidad');
  if (!qty) return;
  qty.value = Math.max(1, Number(qty.value || 1) - 1);
};

window.showProductTab = function showProductTab(panelId, button) {
  document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach((tab) => tab.classList.remove('active'));
  document.getElementById(panelId)?.classList.add('active');
  button?.classList.add('active');
};

const zoomContainer = document.getElementById('zoomContainer');
const mainImage = document.getElementById('mainImage');
const zoomIndicator = document.getElementById('zoomIndicator');
if (zoomContainer && mainImage && zoomIndicator) {
  zoomContainer.addEventListener('mousemove', (e) => {
    const rect = zoomContainer.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    mainImage.style.transformOrigin = `${x}% ${y}%`;
    mainImage.style.transform = 'scale(1.55)';
  });
  zoomContainer.addEventListener('mouseenter', () => zoomIndicator.classList.add('visible'));
  zoomContainer.addEventListener('mouseleave', () => {
    mainImage.style.transform = 'scale(1)';
    zoomIndicator.classList.remove('visible');
  });
}

// ---- BELLA ----
const bellaMessages = [
  '✨ ¡Hola! Soy Bella. ¿Buscas algo especial hoy?',
  '💛 El oro laminado de hoy es el recuerdo de mañana.',
  '⌚ Un reloj elegante dice más que mil palabras.',
  '🚚 ¿Sabías que hacemos domicilios en toda Cartagena?',
  '💍 El mejor accesorio eres tú — nosotros solo lo complementamos.',
  '🌟 Escríbenos por WhatsApp, respondemos rapidísimo.',
  '🎁 ¿Buscas un regalo especial? ¡Tenemos opciones para todos!'
];

let bellaIndex = 0;
let bellaOpen = false;

window.toggleBella = function toggleBella() {
  const bubble = document.getElementById('bellaBubble');
  if (!bubble) return;
  bellaOpen = !bellaOpen;
  if (bellaOpen) {
    bubble.classList.add('visible');
    document.getElementById('bellaMessage').textContent = bellaMessages[bellaIndex];
    bellaIndex = (bellaIndex + 1) % bellaMessages.length;
  } else {
    bubble.classList.remove('visible');
  }
};

window.closeBella = function closeBella() {
  const bubble = document.getElementById('bellaBubble');
  if (bubble) bubble.classList.remove('visible');
  bellaOpen = false;
};

document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    const bubble = document.getElementById('bellaBubble');
    if (bubble) {
      bubble.classList.add('visible');
      bellaOpen = true;
      const msg = document.getElementById('bellaMessage');
      if (msg) msg.textContent = bellaMessages[0];
    }
  }, 5000);

  setInterval(() => {
    if (!bellaOpen) return;
    bellaIndex = (bellaIndex + 1) % bellaMessages.length;
    const msg = document.getElementById('bellaMessage');
    if (msg) {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.4s ease';
      setTimeout(() => {
        msg.textContent = bellaMessages[bellaIndex];
        msg.style.opacity = '1';
      }, 300);
    }
  }, 8000);
});
