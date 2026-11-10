/*
 * Asistente de IA del formulario de servicios.
 * El usuario escribe el nombre, pulsa "Sugerir con IA" y el formulario
 * se completa: textos, SEO, WhatsApp, beneficios, características,
 * proceso y preguntas frecuentes. Las fotos se cargan a mano.
 * Nada se guarda hasta que el usuario pulse "Guardar".
 */
(function () {
    "use strict";

    function endpointUrl() {
        // .../services/service/add/  o  .../services/service/5/change/
        return window.location.pathname.replace(
            /\/(add|\d+\/change)\/?$/,
            "/ai-suggest/"
        );
    }

    function csrfToken() {
        var input = document.querySelector("input[name=csrfmiddlewaretoken]");
        return input ? input.value : "";
    }

    function setValue(el, value, replace) {
        if (!el || value === undefined || value === null || value === "") {
            return false;
        }
        if (!replace && String(el.value).trim() !== "") {
            return false;
        }
        el.value = value;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        el.classList.remove("ai-filled");
        void el.offsetWidth; // reinicia la animación
        el.classList.add("ai-filled");
        return true;
    }

    function byId(id) {
        return document.getElementById(id);
    }

    function totalForms(prefix) {
        var el = byId("id_" + prefix + "-TOTAL_FORMS");
        return el ? parseInt(el.value, 10) || 0 : 0;
    }

    // Devuelve el índice de una fila vacía o crea una nueva con "Agregar otro".
    function freeRowIndex(prefix, firstField) {
        var total = totalForms(prefix);
        for (var i = 0; i < total; i++) {
            var field = byId("id_" + prefix + "-" + i + "-" + firstField);
            var row = field && field.closest(".inline-related");
            var deleted = row && row.classList.contains("deleted");
            if (field && !deleted && String(field.value).trim() === "") {
                return i;
            }
        }
        var group = byId(prefix + "-group");
        var addLink = group && group.querySelector(".add-row a");
        if (!addLink) {
            return -1;
        }
        addLink.click();
        var after = totalForms(prefix);
        return after > total ? after - 1 : -1;
    }

    function fillRows(prefix, items, keys, replace) {
        if (!items || !items.length) {
            return 0;
        }
        // Si se reemplaza, se vacían las filas nuevas (sin guardar) primero.
        var filled = 0;
        items.forEach(function (item, order) {
            var index = freeRowIndex(prefix, keys[0]);
            if (index < 0) {
                return;
            }
            keys.forEach(function (key) {
                setValue(byId("id_" + prefix + "-" + index + "-" + key), item[key], true);
            });
            var orderField = byId("id_" + prefix + "-" + index + "-display_order");
            if (orderField) {
                orderField.value = order + 1;
            }
            filled++;
        });
        return filled;
    }

    function hasExistingRows(prefix, firstField) {
        var total = totalForms(prefix);
        for (var i = 0; i < total; i++) {
            var field = byId("id_" + prefix + "-" + i + "-" + firstField);
            if (field && String(field.value).trim() !== "") {
                return true;
            }
        }
        return false;
    }

    function apply(s, replace) {
        var count = 0;

        if (s.category_id) {
            var cat = byId("id_category");
            if (cat && (replace || !cat.value)) {
                cat.value = String(s.category_id);
                cat.dispatchEvent(new Event("change", { bubbles: true }));
                cat.classList.add("ai-filled");
                count++;
            }
        }

        [
            "card_description",
            "introduction",
            "icon_key",
            "whatsapp_message",
            "seo_title",
            "seo_description"
        ].forEach(function (name) {
            if (setValue(byId("id_" + name), s[name], replace)) {
                count++;
            }
        });

        // Las listas solo se agregan si la sección está vacía o si se pidió reemplazar.
        var lists = [
            ["benefits", s.benefits, ["title", "description"]],
            ["features", s.features, ["title", "description"]],
            ["process_steps", s.process_steps, ["title", "description"]],
            ["faqs", s.faqs, ["question", "answer"]]
        ];
        lists.forEach(function (entry) {
            if (!replace && hasExistingRows(entry[0], entry[2][0])) {
                return;
            }
            count += fillRows(entry[0], entry[1], entry[2], replace);
        });

        return count;
    }

    function setStatus(box, text, kind) {
        var status = box.querySelector(".ai-status");
        status.textContent = text;
        status.className = "ai-status" + (kind ? " ai-status--" + kind : "");
    }

    function build() {
        var nameInput = byId("id_name");
        if (!nameInput) {
            return;
        }

        var box = document.createElement("div");
        box.className = "ai-suggest";
        box.innerHTML =
            '<button type="button" class="button ai-suggest__btn">' +
            '<span class="ai-suggest__spark" aria-hidden="true"></span>' +
            "Sugerir con IA</button>" +
            '<label class="ai-suggest__replace">' +
            '<input type="checkbox"> Reemplazar lo ya escrito</label>' +
            '<p class="ai-status" role="status" aria-live="polite">' +
            "Escribe el nombre del servicio y pulsa el botón. " +
            "Revisa los textos antes de guardar; las fotos se agregan abajo.</p>";

        var row = nameInput.closest(".form-row") || nameInput.parentNode;
        row.appendChild(box);

        var button = box.querySelector("button");
        var replaceBox = box.querySelector("input[type=checkbox]");

        button.addEventListener("click", function () {
            var name = nameInput.value.trim();
            if (name.length < 3) {
                setStatus(box, "Escribe primero el nombre del servicio.", "error");
                nameInput.focus();
                return;
            }

            button.disabled = true;
            box.classList.add("is-loading");
            setStatus(box, "Pensando el contenido para “" + name + "”…");

            fetch(endpointUrl(), {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken()
                },
                body: JSON.stringify({ name: name })
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, data: data };
                    });
                })
                .then(function (result) {
                    if (!result.ok || !result.data.suggestion) {
                        throw new Error(
                            (result.data && result.data.error) ||
                            "No se pudo obtener la sugerencia."
                        );
                    }
                    var filled = apply(result.data.suggestion, replaceBox.checked);
                    setStatus(
                        box,
                        filled
                            ? "Listo: se completaron " + filled +
                              " campos. Revísalos, agrega las fotos y guarda."
                            : "No había campos vacíos. Marca “Reemplazar lo ya escrito” para sobrescribirlos.",
                        "ok"
                    );
                })
                .catch(function (error) {
                    setStatus(box, error.message, "error");
                })
                .finally(function () {
                    button.disabled = false;
                    box.classList.remove("is-loading");
                });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", build);
    } else {
        build();
    }
})();
