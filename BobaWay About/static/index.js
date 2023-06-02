//Watermelon, Strawberry, Thai, Mango, Honeydew Melon, Butterfly Pea, Taro, Sesame, Brown Sugar
const flavColors = [
  [[255, 130, 130], [255, 170, 170], "Watermelon"],
  [[255, 183, 212], [252, 219, 232], "Strawberry"],
  [[252, 163, 116], [255, 196, 165], "Thai"],
  [[255, 222, 109], [255, 241, 175], "Mango"],
  [[176, 224, 99], [218, 255, 159], "Honeydew Melon"],
  [[127, 225, 255], [191, 240, 255], "Butterfly Pea"],
  [[239, 178, 255], [247, 216, 255], "Taro"],
  [[150, 150, 150], [200, 200, 200], "Sesame"],
  [[226, 199, 140], [250, 230, 170], "Brown Sugar"],
];

function submitMOV() {
  document.getElementById("submit-shadow").style.display = "none";
}

function submitMOU() {
  document.getElementById("submit-shadow").style.display = "block";
}

function submitForm() {
  let name = document.getElementById("name").value;
  let message = document.getElementById("message").value;
  document.getElementById("submit").href = `mailto:taliyahengineering@gmail.com?subject=Bobaway - ${name}&body=${message}`;
  document.getElementById("submit").click();
}

function rgb(values) {
  return "rgb(" + values.join(", ") + ")";
}

function menuMOU() {
  menus = document.getElementsByClassName("menu-button");
  for (var i = 0; i < menus.length; i++) {
    menus[i].style.backgroundColor = rgb(flavColors[8][0]);
  }
}

function menuMOV(select) {
  menus = document.getElementsByClassName("menu-button");
  menus[select].style.backgroundColor = rgb(flavColors[8][1]);
}