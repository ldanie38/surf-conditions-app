
/*Give your webpage an oceanic feel by changing the background color dynamically. */

document.body.style.transition = "background 0.5s ease"; // Faster fade effect

setInterval(() => {
    let colors = ['#8dc8d8', "#a7d5e1", "#cef4ff", "#dceef3", "#72bbce","#65cbe9"];
    document.body.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
}, 2000); // Changes color every 2 seconds



/* button effect*/

const button = document.querySelector("button");

button.addEventListener("mouseover", () => {
    button.style.backgroundColor = "#f57c73";
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



/* Tides */ 
const times = tideData.map(entry => entry[0]);
const trends = tideData.map(entry => entry[1] === "Incoming Tide" ? 1 : entry[1] === "Outgoing Tide" ? -1 : 0);

const ctx = document.getElementById('tideChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: times,
        datasets: [{
            label: 'Tide Movement',
            data: trends,
            borderColor: '#0077be',
            fill: false
        }]
    },
    options: {
        scales: {
            y: { min: -1, max: 1, ticks: { stepSize: 1 } }
        }
    }
});
console.log("Tide Data:", tideData); // Debugging step











