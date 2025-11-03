(function () {
  const slides = document.querySelectorAll("#carousel-slides .slide");
  const dotsContainer = document.getElementById("carousel-dots");
  const prevBtn = document.getElementById("prev-slide");
  const nextBtn = document.getElementById("next-slide");

  if (!slides.length) return;

  let current = 0;

  // crear dots
  slides.forEach((_, i) => {
    const dot = document.createElement("button");
    dot.className =
      "w-2 h-2 rounded-full focus:outline-none border border-transparent";
    dot.setAttribute("data-index", i);
    dotsContainer.appendChild(dot);
  });

  const dots = dotsContainer.querySelectorAll("button");

  function render() {
    slides.forEach((slide, i) => {
      if (i === current) {
        slide.classList.remove("hidden");
      } else {
        slide.classList.add("hidden");
      }
    });

    dots.forEach((dot, i) => {
      if (i === current) {
        dot.classList.remove(
          "bg-gray-400",
          "dark:bg-gray-500"
        );
        dot.classList.add("bg-blue-techo");
      } else {
        dot.classList.remove("bg-blue-techo");
        dot.classList.add("bg-gray-400", "dark:bg-gray-500");
      }
    });
  }

  function goNext() {
    current = (current + 1) % slides.length;
    render();
  }

  function goPrev() {
    current = (current - 1 + slides.length) % slides.length;
    render();
  }

  // click en botones
  if (nextBtn) nextBtn.addEventListener("click", goNext);
  if (prevBtn) prevBtn.addEventListener("click", goPrev);

  // click en los dots
  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      current = parseInt(dot.getAttribute("data-index"), 10);
      render();
    });
  });

  // autorotar cada 6s
  setInterval(goNext, 6000);

  // primer render
  render();
})();

