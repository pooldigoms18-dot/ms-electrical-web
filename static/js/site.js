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