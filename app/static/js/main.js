// @cosabella — Main JS

const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');
if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => navMenu.classList.toggle('active'));
    document.addEventListener('click', (e) => {
        if (!navToggle.contains(e.target) && !navMenu.contains(e.target))
            navMenu.classList.remove('active');
    });
}

const flashes = document.querySelectorAll('.flash');
flashes.forEach(flash => {
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
            ? '0 4px 20px rgba(0,0,0,0.15)'
            : '0 2px 8px rgba(0,0,0,0.08)';
    });
}

// ---- BELLA ----
const bellaMessages = [
    "✨ ¡Hola! Soy Bella. ¿Buscas algo especial hoy?",
    "💛 El oro laminado de hoy es el recuerdo de mañana.",
    "⌚ Un reloj elegante dice más que mil palabras.",
    "🚚 ¿Sabías que hacemos domicilios en toda Cartagena?",
    "💍 El mejor accesorio eres tú — nosotros solo lo complementamos.",
    "🌟 Escríbenos por WhatsApp, respondemos rapidísimo.",
    "🎁 ¿Buscas un regalo especial? ¡Tenemos opciones para todos!",
];

let bellaIndex = 0;
let bellaOpen = false;

window.toggleBella = function() {
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
}

window.closeBella = function() {
    const bubble = document.getElementById('bellaBubble');
    if (bubble) bubble.classList.remove('visible');
    bellaOpen = false;
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const bubble = document.getElementById('bellaBubble');
        if (bubble) {
            bubble.classList.add('visible');
            bellaOpen = true;
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