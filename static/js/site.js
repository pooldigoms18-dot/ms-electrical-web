"use strict";

const menuButton = document.querySelector("[data-menu-toggle]");
const navigation = document.querySelector("[data-menu]");

if (menuButton && navigation) {
    const closeMenu = () => {
        navigation.classList.remove("is-open");
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute(
            "aria-label",
            "Abrir menú principal"
        );
    };

    const openMenu = () => {
        navigation.classList.add("is-open");
        menuButton.setAttribute("aria-expanded", "true");
        menuButton.setAttribute(
            "aria-label",
            "Cerrar menú principal"
        );
    };

    menuButton.addEventListener("click", () => {
        const isOpen =
            menuButton.getAttribute("aria-expanded") === "true";

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    navigation.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 980) {
            closeMenu();
        }
    });
}

/* =========================================================
   Aparición al hacer scroll
   El <head> pone la clase js-reveal en <html> solo si el
   navegador lo soporta y el usuario no pidió menos movimiento.
   ========================================================= */

(() => {
    const root = document.documentElement;

    if (!root.classList.contains("js-reveal")) {
        return;
    }

    window.msRevealReady = true;

    // Elementos de páginas internas que también aparecen con efecto.
    const autoTargets = [
        ".section-heading",
        ".service-card",
        ".project-card",
        ".commercial-trust-card",
        ".faq-item",
        ".final-cta-card",
    ];

    document
        .querySelectorAll(autoTargets.join(","))
        .forEach((element) => element.classList.add("reveal"));

    const targets = document.querySelectorAll(".reveal");

    // Escalonado leve entre hermanos de una misma cuadrícula.
    targets.forEach((element) => {
        const parent = element.parentElement;
        if (!parent) {
            return;
        }
        const siblings = Array.from(parent.children)
            .filter((child) => child.classList.contains("reveal"));
        const index = siblings.indexOf(element);
        if (siblings.length > 1 && index > 0) {
            element.style.setProperty(
                "--reveal-delay",
                `${Math.min(index, 5) * 0.08}s`
            );
        }
    });

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            rootMargin: "0px 0px -8% 0px",
            threshold: 0.12,
        }
    );

    targets.forEach((element) => observer.observe(element));
})();
