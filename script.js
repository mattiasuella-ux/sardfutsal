document.addEventListener("DOMContentLoaded", function () {

  const menuToggle = document.querySelector(".menu-toggle");
  const mainNav = document.querySelector("#main-nav");

  if (!menuToggle || !mainNav) return;

  menuToggle.addEventListener("click", function () {

    const isOpen = mainNav.classList.toggle("active");

    menuToggle.setAttribute(
      "aria-label",
      isOpen ? "Chiudi menu" : "Apri menu"
    );

    menuToggle.setAttribute(
      "aria-expanded",
      isOpen ? "true" : "false"
    );

    menuToggle.textContent = isOpen ? "✕" : "☰";
  });

  mainNav.querySelectorAll("a").forEach(function (link) {

    link.addEventListener("click", function () {

      mainNav.classList.remove("active");

      menuToggle.setAttribute("aria-label", "Apri menu");
      menuToggle.setAttribute("aria-expanded", "false");

      menuToggle.textContent = "☰";
    });

  });

});