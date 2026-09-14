// Interactive behavior for index-v2. Kept in an external file to satisfy CSP.

window.openModal = function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("active");
  }
};

window.closeModal = function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
  }
};

document.addEventListener("DOMContentLoaded", function () {
  const languageSelector = document.getElementById("language-selector");
  const languageBtn = languageSelector ? languageSelector.querySelector(".language-btn") : null;
  const languageOptions = document.querySelectorAll(".language-option");
  const currentLangSpan = document.getElementById("current-lang");
  const languageInput = document.getElementById("language");

  const TRANSLATIONS_V2 = {
    en: {
      langEnglish: "English",
      langDutch: "Nederlands",
      langFrench: "Francais",
      heroTitlePrefix: "Hey, I'm",
      heroSubtitle: "Full-stack developer based in Belgium. I build websites that load fast, look sharp, and actually get people to click \"contact.\"",
      heroBio: "I've been building things since I was 9, starting with Scratch. These days that means full-stack web apps, backed by Harvard's CS50x and a lot of hands-on practice. I work with businesses and startups who want a site that does something for them, not just one that looks nice.",
      statYears: "Years Coding",
      statSatisfaction: "Client Satisfaction",
      ctaStartProject: "Start Project",
      ctaSeeWork: "See My Work",
      heroCaption: "Full-stack developer passionate about web technology and performance",
      aboutTitlePrefix: "My",
      aboutTitleAccent: "Journey",
      aboutP1: "I've loved code since I was 9, when I started messing around in Scratch. What began as a hobby turned into a career: building web products that solve real problems instead of just looking good in a portfolio.",
      aboutWhyTitle: "Why I Build",
      aboutP2: "A good website isn't just something you look at, it loads fast, works on every screen, and actually helps you get more customers. That's the bar I hold every project to, no matter how small.",
      highlight1Title: "Continuous Learner",
      highlight1Text: "Completed Harvard's CS50x course in computer science",
      highlight2Title: "Full-Stack Developer",
      highlight2Text: "Frontend, backend, databases-I handle the complete stack",
      highlight3Title: "Performance Obsessed",
      highlight3Text: "Every millisecond counts-I optimize relentlessly",
      whyTitlePrefix: "Why Choose",
      whyTitleAccent: "Me?",
      why1Title: "Fast & Performance",
      why1Text: "Optimized websites that load in milliseconds, improving SEO and user experience.",
      why2Title: "Mobile First",
      why2Text: "Fully responsive designs that work flawlessly on all devices and screen sizes.",
      why3Title: "Conversion Focused",
      why3Text: "Every pixel designed to convert visitors into customers or leads.",
      why4Title: "Secure & Reliable",
      why4Text: "Solid security fundamentals and clean, maintainable code on every project, regardless of size.",
      contactTitlePrefix: "Ready to",
      contactTitleAccent: "Get Started?",
      contactIntro: "Fill out the form and I'll get back to you within 24 hours to talk through your project and what I can do for you.",
      labelFirstName: "First Name *",
      labelLastName: "Last Name *",
      labelCompany: "Company *",
      labelEmail: "Email *",
      labelPhone: "Phone Number",
      labelDetails: "Project Details *",
      submitBtn: "Send My Project Brief",
      projectsTitlePrefix: "Featured",
      projectsTitleAccent: "Projects",
      certTitleAccent: "My",
      certTitle: "Credentials",
      modalCs50Title: "Harvard CS50x Certificate",
      modalFccTitle: "Freecodecamp Responsive Web Design",
      footerText: "© 2026 Sander Pelgrims. All rights reserved. Full-Stack Web Developer from Belgium.",
      skillsTitleAccent: "My",
      skillsTitleSuffix: "Toolkit",
      projectViewLink: "View project",
      eyebrowAbout: "About Me",
      eyebrowWhy: "Why Work With Me",
      eyebrowSkills: "Tech Stack",
      eyebrowProjects: "Portfolio",
      eyebrowCerts: "Credentials",
      eyebrowContact: "Get In Touch"
    },
    nl: {
      langEnglish: "English",
      langDutch: "Nederlands",
      langFrench: "Frans",
      heroTitlePrefix: "Hoi, ik ben",
      heroSubtitle: "Full-stack developer uit België. Ik bouw websites die snel laden, er goed uitzien, en mensen echt op \"contact\" laten klikken.",
      heroBio: "Ik bouw al dingen sinds mijn 9e, begonnen met Scratch. Vandaag betekent dat full-stack webapplicaties, met Harvard's CS50x op zak en veel praktijkervaring. Ik werk met bedrijven en startups die een website willen die iets voor hen doet, niet gewoon een die er goed uitziet.",
      statYears: "Jaar Ervaring",
      statSatisfaction: "Tevreden Klanten",
      ctaStartProject: "Start Je Project",
      ctaSeeWork: "Bekijk Mijn Werk",
      heroCaption: "Full-stack developer met passie voor webtechnologie en performance",
      aboutTitlePrefix: "Over",
      aboutTitleAccent: "Mij",
      aboutP1: "Ik hou van code sinds mijn 9e, toen ik met Scratch begon. Wat als hobby startte, groeide uit tot een carrière: webproducten bouwen die echte problemen oplossen, niet enkel goed staan in een portfolio.",
      aboutWhyTitle: "Waarom Ik Bouw",
      aboutP2: "Een goede website is niet enkel iets om naar te kijken: hij laadt snel, werkt op elk scherm, en helpt je effectief aan meer klanten. Dat is de lat die ik voor elk project leg, hoe klein ook.",
      highlight1Title: "Blijft Leren",
      highlight1Text: "Rondde Harvard's CS50x af in computerwetenschappen",
      highlight2Title: "Full-Stack Developer",
      highlight2Text: "Frontend, backend, databases - ik doe de volledige stack",
      highlight3Title: "Performance Focus",
      highlight3Text: "Elke milliseconde telt - ik optimaliseer onvermoeibaar",
      whyTitlePrefix: "Waarom",
      whyTitleAccent: "Mij?",
      why1Title: "Snel & Performant",
      why1Text: "Geoptimaliseerde websites die in milliseconden laden, voor betere SEO en gebruikerservaring.",
      why2Title: "Mobile First",
      why2Text: "Volledig responsive designs die feilloos werken op elk toestel en schermformaat.",
      why3Title: "Conversiegericht",
      why3Text: "Elke pixel is ontworpen om bezoekers om te zetten in klanten of leads.",
      why4Title: "Veilig & Betrouwbaar",
      why4Text: "Solide beveiliging en nette, onderhoudbare code, in elk project, hoe klein ook.",
      contactTitlePrefix: "Klaar om",
      contactTitleAccent: "te Starten?",
      contactIntro: "Vul het formulier in en ik neem binnen 24 uur contact met je op om je project te bespreken.",
      labelFirstName: "Voornaam *",
      labelLastName: "Achternaam *",
      labelCompany: "Bedrijf *",
      labelEmail: "E-mail *",
      labelPhone: "Telefoonnummer",
      labelDetails: "Projectdetails *",
      submitBtn: "Verstuur Mijn Projectbrief",
      projectsTitlePrefix: "Uitgelichte",
      projectsTitleAccent: "Projecten",
      certTitleAccent: "Mijn",
      certTitle: "Certificaten",
      modalCs50Title: "Harvard CS50x Certificaat",
      modalFccTitle: "Freecodecamp Responsive Web Design",
      footerText: "© 2026 Sander Pelgrims. Alle rechten voorbehouden. Full-Stack Web Developer uit België.",
      skillsTitleAccent: "Mijn",
      skillsTitleSuffix: "Toolkit",
      projectViewLink: "Bekijk project",
      eyebrowAbout: "Over Mij",
      eyebrowWhy: "Waarom Met Mij Werken",
      eyebrowSkills: "Tech Stack",
      eyebrowProjects: "Portfolio",
      eyebrowCerts: "Certificaten",
      eyebrowContact: "Neem Contact Op"
    },
    fr: {
      langEnglish: "English",
      langDutch: "Neerlandais",
      langFrench: "Francais",
      heroTitlePrefix: "Salut, je suis",
      heroSubtitle: "Développeur full-stack basé en Belgique. Je crée des sites qui chargent vite, ont fière allure, et donnent vraiment envie de cliquer sur \"contact\".",
      heroBio: "Je construis des choses depuis mes 9 ans, en commençant par Scratch. Aujourd'hui, ça veut dire des applications web full-stack, avec le CS50x de Harvard en poche et beaucoup de pratique. Je travaille avec des entreprises et startups qui veulent un site qui leur rapporte vraiment, pas juste un site qui a l'air bien.",
      statYears: "Ans de Code",
      statSatisfaction: "Satisfaction Client",
      ctaStartProject: "Demarrer Projet",
      ctaSeeWork: "Voir Mon Travail",
      heroCaption: "Developpeur full-stack passionne par la technologie web et la performance",
      aboutTitlePrefix: "Mon",
      aboutTitleAccent: "Parcours",
      aboutP1: "Je code par passion depuis mes 9 ans. Ce hobby est devenu un métier: construire des produits web qui résolvent de vrais problèmes, pas juste de belles maquettes.",
      aboutWhyTitle: "Pourquoi Je Crée",
      aboutP2: "Un bon site ne se regarde pas seulement, il charge vite, fonctionne sur tous les écrans, et vous aide vraiment à décrocher plus de clients. C'est l'exigence que je mets dans chaque projet, peu importe sa taille.",
      highlight1Title: "Apprentissage Continu",
      highlight1Text: "Formation Harvard CS50x en informatique",
      highlight2Title: "Developpeur Full-Stack",
      highlight2Text: "Frontend, backend, bases de donnees-je gere toute la stack",
      highlight3Title: "Obsede Par la Performance",
      highlight3Text: "Chaque milliseconde compte-j'optimise sans cesse",
      whyTitlePrefix: "Pourquoi",
      whyTitleAccent: "Moi ?",
      why1Title: "Rapide & Performant",
      why1Text: "Des sites optimises qui chargent vite et ameliorent SEO et UX.",
      why2Title: "Mobile First",
      why2Text: "Designs 100% responsives sur tous les appareils.",
      why3Title: "Oriente Conversion",
      why3Text: "Chaque pixel est pense pour convertir les visiteurs.",
      why4Title: "Sécurisé & Fiable",
      why4Text: "Des bases de sécurité solides et un code propre et maintenable, sur chaque projet, quelle que soit sa taille.",
      contactTitlePrefix: "Prêt à",
      contactTitleAccent: "Commencer ?",
      contactIntro: "Remplissez le formulaire et je vous répondrai sous 24 heures pour discuter de votre projet.",
      labelFirstName: "Prenom *",
      labelLastName: "Nom *",
      labelCompany: "Entreprise *",
      labelEmail: "E-mail *",
      labelPhone: "Telephone",
      labelDetails: "Details du Projet *",
      submitBtn: "Envoyer Mon Brief",
      projectsTitlePrefix: "Projets",
      projectsTitleAccent: "Mis en Avant",
      certTitleAccent: "Mes",
      certTitle: "Certificats",
      modalCs50Title: "Certificat Harvard CS50x",
      modalFccTitle: "Freecodecamp Responsive Web Design",
      footerText: "© 2026 Sander Pelgrims. Tous droits réservés. Développeur Full-Stack en Belgique.",
      skillsTitleAccent: "Ma",
      skillsTitleSuffix: "Palette d'Outils",
      projectViewLink: "Voir le projet",
      eyebrowAbout: "À Propos",
      eyebrowWhy: "Pourquoi Travailler Avec Moi",
      eyebrowSkills: "Stack Technique",
      eyebrowProjects: "Portfolio",
      eyebrowCerts: "Certificats",
      eyebrowContact: "Prendre Contact"
    }
  };

  function getCurrentLanguage() {
    const queryLanguage = new URLSearchParams(window.location.search).get("lang");
    if (queryLanguage && ["en", "nl", "fr"].indexOf(queryLanguage) !== -1) {
      return queryLanguage;
    }

    const cookies = document.cookie.split("; ");
    for (const cookie of cookies) {
      if (cookie.startsWith("language=")) {
        return cookie.split("=")[1];
      }
    }
    return "en";
  }

  function updateLanguageDisplay(lang) {
    const langCodeMap = { en: "EN", nl: "NL", fr: "FR" };
    if (currentLangSpan) {
      currentLangSpan.textContent = langCodeMap[lang] || "EN";
    }

    languageOptions.forEach(function (opt) {
      if (opt.getAttribute("data-lang") === lang) {
        opt.classList.add("active");
      } else {
        opt.classList.remove("active");
      }
    });
  }

  function applyTranslations(lang) {
    const dict = TRANSLATIONS_V2[lang] || TRANSLATIONS_V2.en;
    document.documentElement.setAttribute("lang", lang);

    document.querySelectorAll("[data-i18n]").forEach(function (node) {
      const key = node.getAttribute("data-i18n");
      if (dict[key]) {
        node.textContent = dict[key];
      }
    });

    if (languageInput) {
      languageInput.value = lang;
    }
  }

  const savedLang = getCurrentLanguage();
  updateLanguageDisplay(savedLang);
  applyTranslations(savedLang);

  if (languageBtn) {
    languageBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      languageSelector.classList.toggle("active");
    });
  }

  languageOptions.forEach(function (option) {
    option.addEventListener("click", function (e) {
      e.preventDefault();
      const lang = this.getAttribute("data-lang");

      fetch("/api/language/" + lang, { method: "GET" })
        .then(function () {
          updateLanguageDisplay(lang);
          applyTranslations(lang);
          if (languageSelector) {
            languageSelector.classList.remove("active");
          }
        })
        .catch(function (err) {
          console.error("Failed to set language:", err);
        });
    });
  });

  document.addEventListener("click", function (e) {
    if (languageSelector && !languageSelector.contains(e.target)) {
      languageSelector.classList.remove("active");
    }
  });

  document.querySelectorAll(".modal").forEach(function (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });
  });

  document.querySelectorAll(".modal img[data-full-src]").forEach(function (img) {
    img.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      const fullSrc = img.getAttribute("data-full-src") || img.getAttribute("src");
      if (fullSrc) {
        window.open(fullSrc, "_blank", "noopener,noreferrer");
      }
    });
  });

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll(".fade-in").forEach(function (el, index) {
    el.style.opacity = "0";
    el.style.transform = "translateY(30px)";
    el.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
    el.style.transitionDelay = (index % 4) * 0.08 + "s";
    observer.observe(el);
  });

  const contactForm = document.getElementById("contactForm");
  if (contactForm) {
    const submitBtn = document.getElementById("submitBtn");
    const startedAtInput = document.getElementById("form_started_at");
    const submittedAtInput = document.getElementById("submitted_at");
    const recaptchaInput = document.getElementById("recaptcha_token");
    const recaptchaSiteKey = document.body.getAttribute("data-recaptcha-site-key") || "";

    if (startedAtInput) {
      startedAtInput.value = Math.floor(Date.now() / 1000).toString();
    }

    if (submitBtn) {
      window.setTimeout(function () {
        submitBtn.disabled = false;
      }, 2000);
    }

    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();

      if (submitBtn && submitBtn.disabled) {
        return;
      }

      if (submittedAtInput) {
        submittedAtInput.value = Math.floor(Date.now() / 1000).toString();
      }

      const completeSubmit = function () {
        contactForm.submit();
      };

      if (!recaptchaSiteKey || typeof grecaptcha === "undefined") {
        completeSubmit();
        return;
      }

      grecaptcha.ready(function () {
        grecaptcha
          .execute(recaptchaSiteKey, { action: "contact_form" })
          .then(function (token) {
            if (recaptchaInput) {
              recaptchaInput.value = token || "";
            }
            completeSubmit();
          })
          .catch(function (err) {
            console.error("reCAPTCHA token generation failed:", err);
            completeSubmit();
          });
      });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href && href !== "#") {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  });

  // Mouse-follow background spotlight. Batch updates to animation frames.
  let rafPending = false;
  let mouseX = 0;
  let mouseY = 0;

  document.addEventListener("mousemove", function (e) {
    mouseX = e.clientX;
    mouseY = e.clientY;

    if (!rafPending) {
      rafPending = true;
      window.requestAnimationFrame(function () {
        document.documentElement.style.setProperty("--mouse-x", mouseX + "px");
        document.documentElement.style.setProperty("--mouse-y", mouseY + "px");
        rafPending = false;
      });
    }
  });
});
