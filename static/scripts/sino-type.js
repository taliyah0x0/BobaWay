// GLOBAL VARIABLES
let jsonData; // Store the fetched JSON
let save = [];
let old = "";
let lastWord = "";
let last_index = 0;
let languages_included = [1, 0, 0, 0];

// FUNCTIONS
// Get the hanzi options for the word
function getHanziOptions(word) {
    let hanzi_options = [];
    if (word in jsonData) {
        for (var i = 0; i < 4; i++) {
            if (languages_included[i]) {
                hanzi_options = hanzi_options.concat(jsonData[word][i]);
            }
        }
    }
    return hanzi_options;
}

function initiate () {
    let text = document.getElementById("input-area").innerHTML;
    text = text.replace(/&nbsp;/g, " ");
    let output = document.getElementById("output-area");
    let options = document.getElementsByClassName("options");

    let index = -1;
    const selection = window.getSelection();
    let cursorPosition = 0;

    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0); // Get the first range of the selection
        const preCaretRange = range.cloneRange(); // Clone the range
        preCaretRange.selectNodeContents(document.getElementById("input-area")); // Set the cloned range to the start of the editable div
        preCaretRange.setEnd(range.startContainer, range.startOffset); // Set the end of the range to the caret
        cursorPosition = preCaretRange.toString().length; // Get the length of the text in the range
    }

    // locate the word at the cursor position
    let start = cursorPosition;
    while (start > 0 && /\S/.test(text[start - 1])) {
        start--;
    }
    let end = cursorPosition;
    while (end < text.length && /\S/.test(text[end])) {
        end++;
    }

    let word = text.slice(start, end);
    word = word.toLowerCase();

    let tokens = text.split(/(\s+|[^\w\s])/g).filter(token => token.trim());
    let charIndex = 0;

    // locate the index of the word at the cursor position
    for (let i = 0; i < tokens.length; i++) {
        const tokenStart = charIndex;
        const tokenEnd = charIndex + tokens[i].length;

        // Check if the cursor position is within the current token
        if (cursorPosition >= tokenStart && cursorPosition <= tokenEnd) {
            index = i;
            break;
        }

        // Advance the character index, accounting for spaces between tokens
        charIndex = tokenEnd + 1; // +1 for the space
    }

    // check if the word has been deleted
    const originalTokens = old.split(/(\s+|[^\w\s])/g).filter(token => token.trim());
    let deleted = -1;
    for (let i = 0; i < originalTokens.length; i++) {
        if (originalTokens[i] !== tokens[i]) {
            deleted = i; // Index of the deleted word
            break;
        }
    }

    if (originalTokens.length > tokens.length) {
        deleted = originalTokens.length - 1;
    }

    // remove the deleted element from the output
    const all = document.getElementsByClassName("output_div");
    let all_inners = Array.from(all, el => el.innerHTML);
    if (deleted !== -1) {
        all_inners.splice(deleted, 1);
        output.innerHTML = all_inners.map(inner => `<div class="output_div">${inner}</div>`).join('');
    }

    const hanzi_options = getHanziOptions(word);

    if (hanzi_options.length > 0) {
        if (index >= all_inners.length) {
            // fill in the options for the new word
            document.getElementById("options-wrapper").innerHTML += `<div class="options" style="display: flex; flex-direction: column"></div>`;
            options[index].innerHTML = "";
            for (var i = 0; i < hanzi_options.length; i++) {
                options[index].innerHTML += `<label><input name="${word}_${index}" type="radio" class="${index}" value="${hanzi_options[i]}" onclick="editOutput(${index}, '${word}', ${i})">${hanzi_options[i]}</label>`;
            }
            document.getElementsByClassName(`${index}`)[0].checked = true;
            output.innerHTML += `<div class="output_div">${hanzi_options[0]}</div>`;
            save.push(0);
        } else {
            for (var i = 0; i < options.length; i++) {
                options[i].style.display = "none";
            }
            document.getElementsByClassName("box-title3")[0].style.display = "flex";
            options[index].style.display = "flex";
            if (last_index != index) {
                let radios = document.getElementsByClassName(`${index}`);
                let m = radios[save[index]].value;
                radios[save[index]].checked = true;

                output.innerHTML = "";
                for (var i = 0; i < index; i++) {
                    output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
                }
                output.innerHTML += `<div class="output_div">${m}</div>`;
                for (var i = index + 1; i < all_inners.length; i++) {
                    output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
                }
            } else if (options[index].innerHTML == "") {
                options[index].innerHTML = "";
                for (var i = 0; i < temp.length; i++) {
                    options[index].innerHTML += `<label><input name="${word}_${index}" type="radio" class="${index}" value="${temp[i]}" onclick="editOutput(${index}, '${word}', ${i})">${temp[i]}</label>`;
                }
                save[index] = 0;
                document.getElementsByClassName(`${index}`)[0].checked = true;

                output.innerHTML = "";
                for (var i = 0; i < index; i++) {
                    output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
                }
                output.innerHTML += `<div class="output_div">${jsonData[word][0][0]}</div>`;
                for (var i = index + 1; i < all_inners.length; i++) {
                    output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
                }
            }
        }
    } else if (/^[a-zA-Z\s]+$/.test(word) && old != text) {
        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        document.getElementsByClassName("box-title3")[0].style.display = "none";
        output.innerHTML = "";
        for (var i = 0; i < index; i++) {
            output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
        }
        output.innerHTML += `<div class="output_div">${word}</div>`;
        for (var i = index + 1; i < all_inners.length; i++) {
            output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
        }
    } else {
        for (var i = 0; i < options.length; i++) {
            options[i].style.display = "none";
        }
        document.getElementsByClassName("box-title3")[0].style.display = "none";
    }
    old = text;
    lastWord = word;
    last_index = index;
    document.getElementById("highlight-area").innerHTML = text;
}

function editOutput(index, word, radio) {
    // get the current output
    const all = document.getElementsByClassName("output_div");
    const all_inners = Array.from(all, el => el.innerHTML);
    let output = document.getElementById("output-area");

    // update the output with the new hanzi option
    const hanzi_options = getHanziOptions(word);
    const newHTML = all_inners.map(inner => `<div class="output_div">${inner}</div>`);
    newHTML[index] = `<div class="output_div">${hanzi_options[radio]}</div>`;
    output.innerHTML = newHTML.join('');
    save[index] = radio;
}

// Edit the languages included in the hanzi options
function editLanguages(index) {
    languages_included[index] = !languages_included[index] ? 1 : 0;
}

// Helper function to copy the hanzi output to the clipboard
function copy() {
    const all = document.getElementsByClassName("output_div");
    let text = "";
    for (var i = 0; i < all.length; i++) {
        text += all[i].innerHTML;
    }
    navigator.clipboard.writeText(text);
}

// Load the language data from the API
async function loadLanguageData() {
    try {
        const response = await fetch('/api/all-languages-data');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        jsonData = await response.json();
        console.log("JSON data fetched and stored:", jsonData);
    } catch (error) {
        console.error("Error fetching language data:", error);
        // Fallback to static file if API fails
        try {
            const fallbackResponse = await fetch('./static/output.json');
            jsonData = await fallbackResponse.json();
        } catch (fallbackError) {
            console.error("Fallback also failed:", fallbackError);
        }
    }
}

// Setup the interval behavior for the input area
function setupInputAreaInterval() {
    let intervalId;
    const input_area = document.getElementById("input-area");
    input_area.addEventListener("focus", () => {
        intervalId = setInterval(initiate, 200); // Run every 0.2 seconds
    });

    // Stop the loop when the textarea loses focus
    input_area.addEventListener("blur", () => {
        clearInterval(intervalId); // Stop the interval
    });
}


// SETUP
// Call this function when the page loads
loadLanguageData();

// Call this function to set up the interval behavior
setupInputAreaInterval();
