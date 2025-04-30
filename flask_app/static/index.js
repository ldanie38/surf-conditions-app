
/*Give your webpage an oceanic feel by changing the background color dynamically. */

document.body.style.transition = "background 1s ease";

setInterval(() => {
    let colors = ["#0077be", "#0093d1", "#005f99", "#004466"];
    document.body.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
}, 5000);


/* button effect*/

const button = document.querySelector("button");

button.addEventListener("mouseover", () => {
    button.style.backgroundColor = "#ff4500";
    button.style.transform = "scale(1.05)";
    button.style.transition = "0.3s ease";
});

button.addEventListener("mouseout", () => {
    button.style.backgroundColor = "";
    button.style.transform = "scale(1)";
});

/* */
window.addEventListener("scroll", () => {
    const elements = document.querySelectorAll(".form-section, .image-section");
    elements.forEach(el => {
        let offset = window.scrollY * 0.05;
        el.style.transform = `translateY(${offset}px)`;
    });
});

window.addEventListener("scroll", function() {
    let img = document.querySelector(".image-section img");
    img.style.transform = "translateY(" + window.scrollY * 0.1 + "px)";
});









