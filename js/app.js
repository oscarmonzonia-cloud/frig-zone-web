/**
 * Frig Zone - Lógica Interactiva y Conexión con IA
 */

function initFrigZoneApp() {
  // Inicialización de Iconos Lucide
  if (typeof lucide !== 'undefined' && lucide.createIcons) {
    lucide.createIcons();
  }

  // Drawer móvil
  const navToggle = document.getElementById('navToggle');
  const navClose = document.getElementById('navClose');
  const mobileDrawer = document.getElementById('mobileDrawer');

  if (navToggle && mobileDrawer) {
    navToggle.addEventListener('click', () => {
      mobileDrawer.classList.remove('-translate-x-full');
    });
  }
  if (navClose && mobileDrawer) {
    navClose.addEventListener('click', () => {
      mobileDrawer.classList.add('-translate-x-full');
    });
  }

  document.querySelectorAll('#mobileDrawer a').forEach(link => {
    link.addEventListener('click', () => {
      if (mobileDrawer) mobileDrawer.classList.add('-translate-x-full');
    });
  });

  const WHATSAPP_NUMERO = "5491173719821";

  // Pre-Diagnóstico
  const diagForm = document.getElementById('diagForm');
  if (diagForm) {
    diagForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const equipo = document.getElementById('diagEquipo')?.value || "";
      const servicio = document.getElementById('diagServicio')?.value || "";
      const sintoma = document.getElementById('diagSintoma')?.value.trim() || "No especificado";
      const zona = document.getElementById('diagZona')?.value.trim() || "CABA";

      const mensaje = `❄️ *SOLICITUD DE PRE-DIAGNÓSTICO - FRIG ZONE* ❄️\n\n` +
        `📌 *Servicio:* ${servicio}\n` +
        `⚙️ *Equipo:* ${equipo}\n` +
        `📍 *Zona/Barrio:* ${zona}\n` +
        `📝 *Detalle/Síntoma:* ${sintoma}\n\n` +
        `_Enviado desde oscarmonzonia-cloud.github.io/frig-zone-web/_`;

      const url = `https://wa.me/${WHATSAPP_NUMERO}?text=${encodeURIComponent(mensaje)}`;
      window.location.href = url;

      if (typeof gtag === 'function') {
        gtag('event', 'generate_lead', {
          event_category: 'Conversion',
          event_label: 'PreDiagnostico',
          value: 1
        });
      }
    });
  }

  // Calculadora de Frigorías
  const calcBtn = document.getElementById('calcButton');
  if (calcBtn) {
    calcBtn.addEventListener('click', () => {
      const largo = parseFloat(document.getElementById('largo')?.value) || 0;
      const ancho = parseFloat(document.getElementById('ancho')?.value) || 0;
      const alto = parseFloat(document.getElementById('alto')?.value) || 2.6;
      const personas = parseInt(document.getElementById('personas')?.value) || 1;
      const solar = document.getElementById('solar')?.value || "normal";

      if (largo <= 0 || ancho <= 0) {
        alert("Por favor ingresá el largo y el ancho del ambiente.");
        return;
      }

      const volumen = largo * ancho * alto;
      const base = volumen * 50;
      const personasFactor = personas * 150;
      const solFactor = solar === 'directo' ? 250 : 0;
      const frigorias = Math.round(base + personasFactor + solFactor);

      let equipo = "2250 fg (approx. 2.6 kW)";
      if (frigorias > 5000) equipo = "6000 fg (approx. 6.8 kW)";
      else if (frigorias > 3800) equipo = "4500 a 5000 fg";
      else if (frigorias > 2600) equipo = "3000 a 3500 fg";

      const valElem = document.getElementById('frigoriasValue');
      const comElem = document.getElementById('frigoriasComercial');
      if (valElem) valElem.textContent = frigorias.toLocaleString('es-AR');
      if (comElem) comElem.textContent = equipo;

      const resultDiv = document.getElementById('calcResult');
      if (resultDiv) resultDiv.classList.remove('hidden');

      const mensajeCalc = `Hola Frig Zone, calculé ${frigorias} fg recomendadas para mi ambiente. ¿Podrían cotizarme el equipo o la instalación?`;
      const whatsappLink = `https://wa.me/${WHATSAPP_NUMERO}?text=${encodeURIComponent(mensajeCalc)}`;
      const calcWaLink = document.getElementById('calcWhatsAppLink');
      if (calcWaLink) calcWaLink.setAttribute('href', whatsappLink);

      if (typeof gtag === 'function') {
        gtag('event', 'calculate_frigorias', {
          event_category: 'Conversion',
          event_label: 'Calculadora',
          value: frigorias
        });
      }
    });
  }

  // Tracking WhatsApp
  document.querySelectorAll('a[href*="wa.me"]').forEach(button => {
    button.addEventListener('click', function () {
      if (typeof gtag === 'function') {
        gtag('event', 'contact_whatsapp', {
          event_category: 'Conversion',
          event_label: this.id || 'whatsapp_button',
          value: 1
        });
      }
    });
  });

  // === CONEXIÓN AL WORKER DE CLOUDFLARE (CHATBOT IA) ===
  const WORKER_ENDPOINT = "https://lively-lake-e310frigzone-bot.oscar-monzon-ia.workers.dev";

  const chatToggleBtn = document.getElementById("chatToggleBtn");
  const chatCloseBtn = document.getElementById("chatCloseBtn");
  const chatWindow = document.getElementById("chatWindow");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatMessages = document.getElementById("chatMessages");

  let chatHistory = [];

  if (chatToggleBtn && chatWindow) {
    chatToggleBtn.addEventListener("click", () => {
      chatWindow.classList.toggle("hidden");
      if (!chatWindow.classList.contains("hidden") && chatInput) {
        chatInput.focus();
      }
    });
    if (chatCloseBtn) {
      chatCloseBtn.addEventListener("click", () => {
        chatWindow.classList.add("hidden");
      });
    }
  }

  function appendMessage(text, sender) {
    if (!chatMessages) return;
    const msgWrapper = document.createElement("div");
    msgWrapper.className = sender === "user" ? "flex justify-end" : "flex gap-2";

    const bubble = document.createElement("div");
    bubble.className = sender === "user"
      ? "bg-brand-600 text-white p-3 rounded-2xl rounded-tr-none text-xs leading-relaxed max-w-[85%]"
      : "bg-slate-800 border border-slate-700 p-3 rounded-2xl rounded-tl-none text-slate-200 text-xs leading-relaxed max-w-[85%]";

    bubble.textContent = text;
    msgWrapper.appendChild(bubble);
    chatMessages.appendChild(msgWrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const userMsg = chatInput.value.trim();
      if (!userMsg) return;

      appendMessage(userMsg, "user");
      chatInput.value = "";
      chatHistory.push({ sender: "user", text: userMsg });

      // Indicador moderno de escritura (burbuja con puntos animados)
      const loadingWrapper = document.createElement("div");
      loadingWrapper.id = "botLoading";
      loadingWrapper.className = "flex gap-2 items-center";
      loadingWrapper.innerHTML = `
        <div class="bg-slate-800 border border-slate-700 px-4 py-3 rounded-2xl rounded-tl-none flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style="animation-delay: 0ms;"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style="animation-delay: 150ms;"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style="animation-delay: 300ms;"></span>
          <span class="text-[11px] text-slate-400 font-medium ml-1">Escribiendo...</span>
        </div>`;
      chatMessages.appendChild(loadingWrapper);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      try {
        const res = await fetch(WORKER_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userMsg, history: chatHistory })
        });
        const data = await res.json();
        document.getElementById("botLoading")?.remove();

        const reply = data.reply || "Disculpá, no pude procesar la consulta. Por favor escribinos directo por WhatsApp.";
        appendMessage(reply, "model");
        chatHistory.push({ sender: "model", text: reply });

        if (typeof gtag === "function") {
          gtag("event", "chatbot_interaction", {
            event_category: "Engagement",
            event_label: "IA_Query"
          });
        }
      } catch (err) {
        document.getElementById("botLoading")?.remove();
        appendMessage("Hubo un error al consultar el asistente. Podés escribirnos directo por WhatsApp.", "model");
      }
    });
  }

  // Cookie Consent Banner
  const cookieBanner = document.getElementById('cookieBanner');
  const cookieAccept = document.getElementById('cookieAccept');
  const cookieReject = document.getElementById('cookieReject');

  if (cookieBanner && !localStorage.getItem('fz_cookie_consent')) {
    cookieBanner.classList.remove('hidden');
  }

  if (cookieAccept && cookieBanner) {
    cookieAccept.addEventListener('click', () => {
      localStorage.setItem('fz_cookie_consent', 'accepted');
      cookieBanner.classList.add('hidden');
    });
  }
  if (cookieReject && cookieBanner) {
    cookieReject.addEventListener('click', () => {
      localStorage.setItem('fz_cookie_consent', 'rejected');
      cookieBanner.classList.add('hidden');
    });
  }

  // === MODAL LIGHTBOX PARA AMPLIAR IMÁGENES ===
  const imageModal = document.getElementById('imageModal');
  const imageModalImg = document.getElementById('imageModalImg');
  const imageModalTitle = document.getElementById('imageModalTitle');
  const closeImageModal = document.getElementById('closeImageModal');

  if (imageModal && imageModalImg) {
    document.querySelectorAll('.img-lightbox').forEach(img => {
      img.addEventListener('click', () => {
        const src = img.getAttribute('src');
        const title = img.getAttribute('data-title') || img.getAttribute('alt') || 'Visualización de Imagen';
        imageModalImg.setAttribute('src', src);
        if (imageModalTitle) imageModalTitle.textContent = title;
        imageModal.classList.remove('hidden');
      });
    });

    if (closeImageModal) {
      closeImageModal.addEventListener('click', () => {
        imageModal.classList.add('hidden');
      });
    }

    imageModal.addEventListener('click', (e) => {
      if (e.target === imageModal) {
        imageModal.classList.add('hidden');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !imageModal.classList.contains('hidden')) {
        imageModal.classList.add('hidden');
      }
    });
  }
}

// Ejecución segura sin importar si DOMContentLoaded ya ocurrió
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initFrigZoneApp);
} else {
  initFrigZoneApp();
}
