const businessInput = document.getElementById("businessName");
const headlineInput = document.getElementById("headlineText");
const ctaInput = document.getElementById("ctaText");

const previewBrand = document.getElementById("previewBrand");
const previewHeadline = document.getElementById("previewHeadline");
const previewBtn = document.getElementById("previewBtn");

businessInput.addEventListener("input", () => {
  previewBrand.textContent = businessInput.value || "Your Brand";
});

headlineInput.addEventListener("input", () => {
  previewHeadline.textContent = headlineInput.value || "Your headline will appear here";
});

ctaInput.addEventListener("input", () => {
  previewBtn.textContent = ctaInput.value || "CTA";
});
