const greetingSpan = document.querySelectorAll("#greetingSpan");
const sections = document.querySelectorAll("section");
const s1box = document.getElementById("s1Box");
const body = document.body;
const contactForm = document.getElementById("contactForm");
const flipCardsGrid = document.getElementById("tools");
let cards = "";
function greetUser() {
  let greetings = ["Hi", "Hello", "Howdy", "Hey", "Hey there"];
  let randomIndex = Math.floor(Math.random() * greetings.length);
  let i = 0;
  while (i < greetingSpan.length) {
    greetingSpan[i].innerText = greetings[randomIndex];
    i++;
  }
}
greetUser();

s1box.addEventListener("click", () => {
  s2.scrollIntoView();
});

function isInviewport(element) {
  const rect = element.getBoundingClientRect();
  if (
    rect.top <= window.innerHeight / 2 &&
    rect.top >= (-1 * window.innerHeight) / 2
  ) {
    window.history.pushState({}, "", `#${element.id}`);
  }
}
function updateURL() {
  var sectionId = document.querySelector("section[id]").id;
  if (sectionId) {
  }
}
window.addEventListener("DOMContentLoaded", () => {
  updateURL();
});
document.body.addEventListener("wheel", (event) => {
  for (let i = 0; i < sections.length; i++) {
    let section = sections[i];
    isInviewport(section);
  }
});

contactForm.addEventListener("submit", (form) => {
  form.preventDefault();
  const elements = contactForm.children;
  const data = {};
  for (let i = 0; i < elements.length; i++) {
    let item = elements.item(i);
    data[item.name] = item.value;
  }
  const mailto = `mailto:${data.email}?subject=${data.fname} from ${data.cname}&body=${data.details}%0D%0A
    %0D%0A
    %0D%0A
    Extra details:%0D%0A
    company: ${data.cname}%0D%0A
    name: ${data.fname} ${data.lname}%0D%0A
    phone number: ${data.phone}%0D%0A
    %0D%0A
    %0D%0A
    This email was send from Sander's portfolio.`;
  alert(`Opening mail...
(press ok to continue)`);
  window.location.href = mailto;
});

const h1 = document.getElementsByTagName("h1")[0];

function fitText(element) {
  const height = element.offsetHeight;
  let fontSize = parseFloat(
    getComputedStyle(element).getPropertyValue("font-size")
  );
  element.style.height = "fit-content";
  let totalLineHeight = element.offsetHeight;
  let increasing;

  if (totalLineHeight > height - 5) {
    increasing = false;
  } else {
    increasing = true;
  }
}
