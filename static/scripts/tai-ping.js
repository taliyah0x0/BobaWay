let letter_map = [];
let keycode_map = [];
let numbers = ['2','3','4','5','7','8'];
let number_keycodes = [50,51,52,53,55,56];
let consonants = ['p','ts','t','ph','tsh','th','k','ch','s','kh','chh','j','b','l','d','g','h','n'];
let consonant_keycodes = [80, -1, 84, -1, -1, -1, 75, -1, 83, -1, -1, 74, 66, 76, 68, 71, 72, 78];
let vowels = ['a','e','i','o','u','ng'];
let vowel_keycodes = [65, 69, 73, 79, 85, -1];

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

function rgb(values) {
  return 'rgb(' + values.join(", ") + ')';
}

function key(index) {
  let filename = document.getElementById("filename").value;
  let change = document.getElementById("change").value;
  let og = document.getElementById("og").value;

  if (change == ""){
    document.getElementById("prev").value = filename;
  }
  if (numbers.includes(filename.substring(filename.length - 1))) {
    if (consonants.includes(document.getElementById("og").value)) {
    document.getElementById("filename").value = filename.substring(0, filename.length - 2) + letter_map[index] + filename.substring(filename.length - 1);
    } else if (change == "") {
      document.getElementById("filename").value = filename.substring(0, filename.length - 1) + letter_map[index] + filename.substring(filename.length - 1);
    } else if (change != "") {
      document.getElementById("filename").value = filename.substring(0, og.length) + letter_map[index] + filename.substring(filename.length - 1);
    }
  } else {
    if (consonants.includes(document.getElementById("og").value)) {
      document.getElementById("filename").value = filename.substring(0, filename.length - 1) + letter_map[index];
  } else if (change == "") {
  document.getElementById("filename").value += letter_map[index];
    } else if (change != "") {
      document.getElementById("filename").value = filename.substring(0, og.length) + letter_map[index];
    }
  }
    document.getElementById("change").value = letter_map[index];
  document.getElementsByClassName("large-key")[index].style.boxShadow = 'none';
   document.getElementById("full").value = 'False';
  document.mainform.submit();
  if (Number(document.getElementById("slider").value) >= 2) {
    enter(1);
  }
  setTimeout(() => {
    document.getElementsByClassName("large-key")[index].style.boxShadow = '5px 5px rgb(60, 20, 0)';
  },200);
}

function tone(index){
  let filename = document.getElementById("filename").value;
  document.getElementsByClassName("small-key")[index].style.boxShadow = 'none';
  if (filename != "") {
    if (numbers.includes(filename.substring(filename.length - 1))){
      filename = filename.substring(0, filename.length - 1);
    }
    filename += numbers[index];
    document.getElementById("filename").value = filename;
    document.getElementById("full").value = 'False';
    document.mainform.submit();
  }
  setTimeout(() => {
    document.getElementsByClassName("small-key")[index].style.boxShadow = '5px 5px rgb(60, 20, 0)';
  },200);
}

function backspace(){
  let filename = document.getElementById("filename").value;
  let og = document.getElementById("og").value;
  if (document.getElementById("change").value != ""){
    if (consonants.includes(og)) {
      document.getElementById("filename").value = og;
    } else {
    document.getElementById("filename").value = document.getElementById("prev").value;
    }
    document.getElementById("change").value = "";
  } else if (og != ""){
    document.getElementById("change").value = document.getElementById("last").value;
    document.getElementById("og").value = og.substring(0, og.length - document.getElementById("last").value.length);
    if (document.getElementById("og").value != "") {
    document.getElementById("page").value = Number(document.getElementById("page").value) - 1;
    } else if (document.getElementById("og").value == "" || vowels.includes(filename.substring(0, filename.length - 1))) {
      document.getElementById("page").value = 0;
    }
  } else if (og == "") {
    let ogg = document.getElementById("ogg").value;
    let split = ogg.split(" ");
    let new_split = [];
    for (let i = 0; i < split.length; i++){
      if (split[i] != "") {
        new_split.push(split[i]);
      }
    }
    document.getElementById("ogg").value = (new_split.slice(0, new_split.length - 1)).join(" ");
    if (document.getElementById("ogg").value != "") {
      document.getElementById("ogg").value += " ";
    }
    document.getElementById("page").value = 0;
  }
  document.getElementsByClassName("medium-key")[0].style.boxShadow = 'none';
  document.getElementById("full").value = 'False';
  document.mainform.submit();
  setTimeout(() => {
    document.getElementsByClassName("medium-key")[0].style.boxShadow = '5px 5px rgb(60, 20, 0)';
  },200);
}

function enter(type){
  let filename = document.getElementById("filename").value;
  document.getElementsByClassName("medium-key")[type + 1].style.boxShadow = 'none';
  if (filename != ""){
  let page = Number(document.getElementById("page").value);
  document.getElementById("last").value = document.getElementById("change").value;
  document.getElementById("og").value += document.getElementById("change").value;
  if (vowels.includes(filename.substring(0, filename.length - 1))){
    if (page == 0) {
      document.getElementById("page").value = 1;
      page = 1;
    }
    if (filename.substring(0, filename.length - 1) == 'ng'){
      document.getElementById("page").value = 2;
      page = 2;
    }
  }
  document.getElementById("change").value = "";
  document.getElementById("page").value = page + 1;
  if (type == 0){
    document.getElementById("page").value = 4;
  }
  document.mainform.submit();
  }
  setTimeout(() => {
    document.getElementsByClassName("medium-key")[type + 1].style.boxShadow = '5px 5px rgb(60, 20, 0)';
  },200);
}

function play() {
  let og = document.getElementById("og").value;
  let change = document.getElementById("change").value;
  let full = document.getElementById("full").value;
  let ogg = document.getElementById("ogg").value;
  if (full == 'True' && og == "" && change == "" && ogg != ""){
    piece(0);
  } else if (full == "False" && og == "" && change == "" && ogg != "") {
    document.getElementById("full").value = 'True';
    document.mainform.submit();
  } else {
    let full_word = document.getElementById("filename").innerHTML;
    var audio = new Audio(`./static/tai-sounds/${full_word}.wav`);
    audio.load();
    audio.play();
    console.log("plaid")
  }
}

function piece(file) {
  let files = document.getElementById("files").value;
  let full_word = document.getElementById("ogg").value;
  let split = full_word.split(" ");
  if (file < files) {
    var audio = new Audio(`./static/tai-sounds/${split[file]}.wav`);
    audio.load();
    audio.play();
    audio.onended = () => {
      piece(file + 1)
    };
  }
}

function start() {
    document.getElementById("slider").value = Number(document.getElementById("slider_val").value);
  if (Number(document.getElementById("slider").value) != 3){
    document.getElementById("text_box").click();
  }
  let page = document.getElementById("page").innerHTML;
  letter_map = ['p','ts','t','ph','tsh','th','k','ch','s','kh','chh','j','b','l','m','d','g','h','e','n','ng','a','i','o','u'];
  loadKeycodeMap();

  let keys = document.getElementsByClassName("large-key");
  if (page == '0'){
    for (let i = 0; i < letter_map.length; i++){
      keys[i].innerHTML = letter_map[i];
      keys[i].style.opacity = '1';
      keys[i].disabled = false;
    }
  } else if (page == '1'){
    letter_map = ['a','e','i','o','u','ng'];
    loadKeycodeMap();
    
    let keys = document.getElementsByClassName("large-key");
    for (let i = 0; i < keys.length; i++){
      keys[i].style.opacity = '0';
      keys[i].disabled = true;
    }
    for (let i = 0; i < letter_map.length; i++){
      keys[i].innerHTML = letter_map[i];
      keys[i].style.opacity = '1';
      keys[i].disabled = false;
    }
  } else if (page == '2'){
    let endings = document.getElementById("endings").innerHTML;
    let full_string = "";
    for (let i = 0; i < endings.length; i++){
      if (endings[i] != '[' && endings[i] != "'" && endings[i] != ']' && endings[i] != " "){
        full_string += endings[i];
      }
    }
    
    letter_map = full_string.split(',');
    loadKeycodeMap();
    
    for (let i = 0; i < keys.length; i++){
      keys[i].style.opacity = '0';
      keys[i].disabled = true;
    }
    for (let i = 0; i < letter_map.length; i++){
      keys[i].innerHTML = letter_map[i];
      keys[i].style.opacity = '1';
      keys[i].disabled = false;
    }
  }

  let level = document.getElementById("slider").value;
  if (level == 1){
    document.getElementById("level").innerHTML = "Easy";
      document.getElementsByClassName("arrow")[0].src = `./static/img/light-0.png`;
  document.getElementsByClassName("arrow")[1].src = `./static/img/1.png`;
  } else if (level == 2) {
    document.getElementById("level").innerHTML = "Medium";
    document.getElementsByClassName("arrow")[0].src = `./static/img/0.png`;
    document.getElementsByClassName("arrow")[1].src = `./static/img/1.png`;
  } else if (level == 3) {
    document.getElementById("level").innerHTML = "Advanced";
      document.getElementsByClassName("arrow")[0].src = `./static/img/0.png`;
  document.getElementsByClassName("arrow")[1].src = `./static/img/light-1.png`;
  }
}

function copyTextToClipboard() {
          document.getElementsByClassName("copy")[0].src = "./static/img/light-copy.png";
  let og = document.getElementById("og").value;
  let change = document.getElementById("change").value;
  let ogg = document.getElementById("ogg").value;
  let text = "";
  if (og != "" || change != ""){
    text = ogg + og + change;
  } else {
    text = document.getElementById("ogg").value;
  }
  if (!navigator.clipboard) {
    fallbackCopyTextToClipboard(text);
    return;
  }
  navigator.clipboard.writeText(text).then(function() {
    console.log('Async: Copying to clipboard was successful!');
  }, function(err) {
    console.error('Async: Could not copy text: ', err);
  });
  setTimeout(() => {
            document.getElementsByClassName("copy")[0].src = "./static/img/copy.png";
  },200);
}

function update(arrow) {
  let level = Number(document.getElementById("slider").value);
  if (arrow == 0){
    if (level > 1) {
      level -= 1;
      document.getElementsByClassName("arrow")[0].src = `./static/img/light-0.png`;
    }
  } else if (arrow == 1) {
    if (level < 3) {
      level += 1;
      document.getElementsByClassName("arrow")[1].src = `./static/img/light-1.png`;
    }
  }
  if (level == 1){
    document.getElementById("level").innerHTML = "Easy";
    document.getElementsByClassName("arrow")[0].src = `./static/img/light-0.png`;
  } else if (level == 2) {
    document.getElementById("level").innerHTML = "Medium";
    setTimeout(() => {
      document.getElementsByClassName("arrow")[0].src = `./static/img/0.png`;
    document.getElementsByClassName("arrow")[1].src = `./static/img/1.png`;
  },200);
  } else if (level == 3) {
    document.getElementById("level").innerHTML = "Advanced";
    document.getElementsByClassName("arrow")[1].src = `./static/img/light-1.png`;
  }
  document.getElementById("slider").value = level;
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

document.addEventListener('keydown', function(event) {
  if (event.keyCode == 13) { //Enter
    enter(1);
  }

  if (event.keyCode == 8) { //Backspace
    backspace();
  }

  if (event.keyCode == 32) { //Space
    enter(0);
  }

  for (var i = 0; i < keycode_map.length; i++) {
    if (keycode_map[i] != -1) {
      if (event.keyCode == keycode_map[i]) {
        key(i);
      }
    }
  }

  for (var i = 0; i < number_keycodes.length; i++) {
    if (event.keyCode == number_keycodes[i]) {
      tone(i);
    }
  }
});

function loadKeycodeMap() {
  keycode_map = [];
  for (var i = 0; i < letter_map.length; i++) {
    let keycode = 0;
    if (consonants.includes(letter_map[i])) {
      keycode = consonant_keycodes[consonants.indexOf(letter_map[i])];
    } else if (vowels.includes(letter_map[i])) {
      keycode = vowel_keycodes[vowels.indexOf(letter_map[i])];
    }
    keycode_map.push(keycode);
  }
}