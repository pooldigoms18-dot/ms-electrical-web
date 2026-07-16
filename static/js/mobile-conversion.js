"use strict";

/**
 * Mejora la experiencia de la barra de conversión móvil.
 *
 * La barra se oculta temporalmente cuando el usuario está
 * escribiendo en un formulario para no cubrir el teclado
 * ni los campos inferiores.
 */
(() => {
    const conversionBar = document.querySelector(
        "[data-mobile-conversion]"
    );

    if (!conversionBar) {
        return;
    }

    const formControlSelector = [
        "input",
        "textarea",
        "select",
    ].join(",");

    /**
     * Comprueba si un elemento es un control de formulario.
     */
    const isFormControl = (element) => {
        return (
            element instanceof HTMLElement
            && element.matches(formControlSelector)
        );
    };

    /**
     * Oculta la barra cuando un campo obtiene el foco.
     */
    document.addEventListener(
        "focusin",
        (event) => {
            if (!isFormControl(event.target)) {
                return;
            }

            conversionBar.classList.add(
                "is-hidden-for-input"
            );
        }
    );

    /**
     * Vuelve a mostrar la barra cuando se abandona el formulario.
     */
    document.addEventListener(
        "focusout",
        () => {
            window.setTimeout(
                () => {
                    const activeElement = document.activeElement;

                    if (
                        activeElement
                        && isFormControl(activeElement)
                    ) {
                        return;
                    }

                    conversionBar.classList.remove(
                        "is-hidden-for-input"
                    );
                },
                150
            );
        }
    );
})();