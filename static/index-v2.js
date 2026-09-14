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
      heroSubtitle: "Full-stack web developer from Belgium who turns ideas into beautiful, fast, and conversion-focused websites that actually drive business results.",
      heroBio: "Since I started coding at age 9, I've been obsessed with building things. From Scratch as a kid to full-stack web development today, I've completed Harvard's CS50x and trained in modern web tech. Now I help businesses and startups build exceptional digital experiences.",
      statYears: "Years Coding",
      statProjects: "Projects Delivered",
      statSatisfaction: "Client Satisfaction",
      ctaStartProject: "Start Project",
      ctaSeeWork: "See My Work",
      heroCaption: "Full-stack developer passionate about web technology and performance",
      aboutTitlePrefix: "My",
      aboutTitleAccent: "Journey",
      aboutP1: "I've been passionate about code since age 9 when I started with Scratch. What began as a hobby has evolved into a career dedicated to creating exceptional web experiences that solve real problems and drive tangible business results.",
      aboutWhyTitle: "Why I Build",
      aboutP2: "I believe great websites aren't just beautiful-they're fast, accessible, and designed to convert. Every project I take on reflects my commitment to quality and my passion for staying ahead of what's possible on the web.",
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
      why4Text: "Enterprise-grade security and best practices built into every project.",
      contactTitlePrefix: "Ready to",
      contactTitleAccent: "Get Started?",
      contactIntro: "Fill out the form below and I'll get back to you within 24 hours to discuss your project and how I can help bring your vision to life.",
      labelFirstName: "First Name *",
      labelLastName: "Last Name *",
      labelCompany: "Company *",
      labelEmail: "Email *",
      labelPhone: "Phone Number",
      labelDetails: "Project Details *",
      submitBtn: "Send My Project Brief",
      projectsTitlePrefix: "Featured",
      projectsTitleAccent: "Projects",
      project1Title: "Portfolio Website",
      project1Text: "A modern, fully responsive portfolio showcasing web development skills with smooth animations and mobile-first design.",
      project2Title: "Full-Stack Web App",
      project2Text: "Complete web application with frontend and backend, featuring database integration and user authentication systems.",
      project3Title: "Performance Optimizer",
      project3Text: "Optimized existing websites for speed and SEO, achieving 90+ Lighthouse scores and improved user engagement metrics.",
      project4Title: "Design System",
      project4Text: "Created comprehensive design system and component library for consistent branding and rapid development across projects.",
      testimonialsTitlePrefix: "What",
      testimonialsTitleAccent: "Clients Say",
      testimonial1Text: "\"Sander delivered an amazing website that exceeded our expectations. The design is sleek, responsive, and our conversion rate increased by 40%!\"",
      testimonial2Text: "\"Professional, responsive, and incredibly fast. The mobile experience is perfect. Highly recommended to anyone looking for quality web development.\"",
      testimonial3Text: "\"Best decision we made. Sander understood our vision perfectly and created a website that truly represents our brand. Amazing work!\"",
      testimonial4Text: "\"The performance optimization Sander did on our site was incredible. Page load times cut in half and Google rankings improved significantly.\"",
      certTitleAccent: "My",
      certTitle: "Credentials",
      modalCs50Title: "Harvard CS50x Certificate",
      modalFccTitle: "Freecodecamp Responsive Web Design",
      footerText: "© 2026 Sander Pelgrims. All rights reserved. Full-Stack Web Developer from Belgium.",
      skillsTitleAccent: "My",
      skillsTitleSuffix: "Toolkit"
    },
    nl: {
      langEnglish: "English",
      langDutch: "Nederlands",
      langFrench: "Frans",
      heroTitlePrefix: "Hoi, ik ben",
      heroSubtitle: "Full-stack webdeveloper uit België die ideeën omzet in mooie, snelle en conversiegerichte websites die écht resultaat opleveren.",
      heroBio: "Sinds ik op mijn 9e begon met coderen, ben ik gefascineerd door het bouwen van projecten. Van Scratch als kind tot full-stack webontwikkeling vandaag: ik behaalde Harvard's CS50x en train continu in moderne webtechnologie. Nu help ik bedrijven en startups om uitzonderlijke digitale ervaringen te bouwen.",
      statYears: "Jaar Ervaring",
      statProjects: "Projecten Opgeleverd",
      statSatisfaction: "Tevreden Klanten",
      ctaStartProject: "Start Je Project",
      ctaSeeWork: "Bekijk Mijn Werk",
      heroCaption: "Full-stack developer met passie voor webtechnologie en performance",
      aboutTitlePrefix: "Over",
      aboutTitleAccent: "Mij",
      aboutP1: "Ik ben gepassioneerd door code sinds mijn 9e, toen ik met Scratch begon. Wat begon als hobby groeide uit tot een carrière in het bouwen van sterke webervaringen die echte problemen oplossen en tastbare businessresultaten opleveren.",
      aboutWhyTitle: "Waarom Ik Bouw",
      aboutP2: "Goede websites zijn niet alleen mooi - ze zijn snel, toegankelijk en ontworpen om te converteren. Elk project weerspiegelt mijn focus op kwaliteit en mijn passie om voorop te blijven lopen in wat mogelijk is op het web.",
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
      why4Text: "Enterprise-grade beveiliging en best practices in elk project ingebouwd.",
      contactTitlePrefix: "Klaar om",
      contactTitleAccent: "te Starten?",
      contactIntro: "Vul het formulier hieronder in en ik neem binnen 24 uur contact met je op om je project te bespreken en hoe ik je visie tot leven kan brengen.",
      labelFirstName: "Voornaam *",
      labelLastName: "Achternaam *",
      labelCompany: "Bedrijf *",
      labelEmail: "E-mail *",
      labelPhone: "Telefoonnummer",
      labelDetails: "Projectdetails *",
      submitBtn: "Verstuur Mijn Projectbrief",
      projectsTitlePrefix: "Uitgelichte",
      projectsTitleAccent: "Projecten",
      project1Title: "Portfolio Website",
      project1Text: "Een modern en volledig responsive portfolio met vloeiende animaties en mobile-first design.",
      project2Title: "Full-Stack Web App",
      project2Text: "Complete webapplicatie met frontend, backend, databasekoppeling en gebruikersauthenticatie.",
      project3Title: "Performance Optimizer",
      project3Text: "Optimalisatie van bestaande websites voor snelheid en SEO, met Lighthouse-scores van 90+.",
      project4Title: "Design Systeem",
      project4Text: "Een consistent design systeem en componentbibliotheek voor snellere ontwikkeling en herkenbare branding.",
      testimonialsTitlePrefix: "Wat",
      testimonialsTitleAccent: "Klanten Zeggen",
      testimonial1Text: "\"Sander leverde een geweldige website die onze verwachtingen overtrof. Het ontwerp is strak, snel, en onze conversieratio steeg met 40%!\"",
      testimonial2Text: "\"Professioneel, responsive en ongelooflijk snel. De mobiele ervaring is perfect. Een aanrader voor iedereen die op zoek is naar kwalitatieve webontwikkeling.\"",
      testimonial3Text: "\"Beste beslissing die we namen. Sander begreep onze visie perfect en bouwde een website die ons merk écht vertegenwoordigt. Geweldig werk!\"",
      testimonial4Text: "\"De performance-optimalisatie die Sander deed was ongelooflijk. Laadtijden werden gehalveerd en onze Google-ranking verbeterde sterk.\"",
      certTitleAccent: "Mijn",
      certTitle: "Certificaten",
      modalCs50Title: "Harvard CS50x Certificaat",
      modalFccTitle: "Freecodecamp Responsive Web Design",
      footerText: "© 2026 Sander Pelgrims. Alle rechten voorbehouden. Full-Stack Web Developer uit België.",
      skillsTitleAccent: "Mijn",
      skillsTitleSuffix: "Toolkit"
    },
    fr: {
      langEnglish: "English",
      langDutch: "Neerlandais",
      langFrench: "Francais",
      heroTitlePrefix: "Salut, je suis",
      heroSubtitle: "Developpeur full-stack en Belgique qui transforme les idees en sites beaux, rapides et orientes conversion.",
      heroBio: "Depuis l'age de 9 ans je cree avec du code. De Scratch au developpement full-stack moderne, je construis des experiences web efficaces pour startups et entreprises.",
      statYears: "Ans de Code",
      statProjects: "Projets Livres",
      statSatisfaction: "Satisfaction Client",
      ctaStartProject: "Demarrer Projet",
      ctaSeeWork: "Voir Mon Travail",
      heroCaption: "Developpeur full-stack passionne par la technologie web et la performance",
      aboutTitlePrefix: "Mon",
      aboutTitleAccent: "Parcours",
      aboutP1: "Je suis passionne par le code depuis mes 9 ans. Ce hobby est devenu une carriere axee sur des experiences web qui resolvent de vrais problemes et creent des resultats concrets.",
      aboutWhyTitle: "Pourquoi Je Cree",
      aboutP2: "Un excellent site n'est pas seulement beau-il est rapide, accessible et concu pour convertir.",
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
      why4Title: "Securise & Fiable",
      why4Text: "Bonnes pratiques et securite solide dans chaque projet.",
      contactTitlePrefix: "Pret a",
      contactTitleAccent: "Commencer ?",
      contactIntro: "Remplissez le formulaire et je vous repondrai sous 24 heures pour discuter de votre projet.",
      labelFirstName: "Prenom *",
      labelLastName: "Nom *",
      labelCompany: "Entreprise *",
      labelEmail: "E-mail *",
      labelPhone: "Telephone",
      labelDetails: "Details du Projet *",
      submitBtn: "Envoyer Mon Brief",
      projectsTitlePrefix: "Projets",
      projectsTitleAccent: "Mis en Avant",
      project1Title: "Site Portfolio",
      project1Text: "Un portfolio moderne et responsive avec animations fluides et approche mobile-first.",
      project2Title: "Application Web Full-Stack",
      project2Text: "Application complete avec frontend, backend, base de donnees et authentification.",
      project3Title: "Optimisation Performance",
      project3Text: "Optimisation de sites existants pour la vitesse et le SEO avec excellents scores Lighthouse.",
      project4Title: "Systeme de Design",
      project4Text: "Systeme de design et bibliotheque de composants pour un developpement plus rapide.",
      testimonialsTitlePrefix: "Ce Que",
      testimonialsTitleAccent: "Disent les Clients",
      testimonial1Text: "\"Sander a livre un site exceptionnel qui a depasse nos attentes.\"",
      testimonial2Text: "\"Professionnel, reactif et tres rapide. Excellente experience mobile.\"",
      testimonial3Text: "\"La meilleure decision. Le site represente parfaitement notre marque.\"",
      testimonial4Text: "\"L'optimisation performance a ete incroyable. Temps de chargement nettement reduits.\"",
      certTitleAccent: "Mes",
      certTitle: "Certificats",
      modalCs50Title: "Certificat Harvard CS50x",
      modalFccTitle: "Freecodecamp Responsive Web Design",
      footerText: "© 2026 Sander Pelgrims. Tous droits reserves. Developpeur Full-Stack en Belgique.",
      skillsTitleAccent: "Ma",
      skillsTitleSuffix: "Palette d'Outils"
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

  document.querySelectorAll(".fade-in").forEach(function (el) {
    el.style.opacity = "0";
    el.style.transform = "translateY(30px)";
    el.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
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
