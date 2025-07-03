const input_area = document.getElementById("input-area");
input_area.addEventListener("focus", () => {
    intervalId = setInterval(initiate, 200); // Run every 1 second
});

// Stop the loop when the textarea loses focus
input_area.addEventListener("blur", () => {
    clearInterval(intervalId); // Stop the interval
});

let save = [];

let old = "";
let lastWord = "";
let last_index = 0;
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

    const originalTokens = old.split(/(\s+|[^\w\s])/g).filter(token => token.trim());
    let deleted = -1;
    /*if (originalTokens.length > tokens.length) {
        for (let i = 0; i < originalTokens.length; i++) {
            if (originalTokens[i] !== tokens[i]) {
                deleted = i; // Index of the deleted word
                break;
            }
        }
    }*/
    for (let i = 0; i < originalTokens.length; i++) {
        if (originalTokens[i] !== tokens[i]) {
            deleted = i; // Index of the deleted word
            break;
        }
    }

    if (originalTokens.length > tokens.length) {
        deleted = originalTokens.length - 1;
    }

    const all = document.getElementsByClassName("output_div");
    let all_inners = [];
    for (var i = 0; i < all.length; i++) {
        all_inners.push(all[i].innerHTML);
    }

    if (deleted != -1) {
        output.innerHTML = "";
        for (var i = 0; i < all_inners.length; i++) {
            if (i != deleted) {
                output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
            }
        }
        all_inners.pop(deleted);
    }

    let temp = [];
    if (word in jsonData) {
        for (var i = 0; i < 4; i++) {
            if (languages_included[i]) {
                temp = temp.concat(jsonData[word][i]);
            }
        }
    }
    if (word in jsonData && temp.length > 0) {
        if (index >= all_inners.length) {
            document.getElementById("options-wrapper").innerHTML += `<div class="options" style="display: flex; flex-direction: column"></div>`;
            options[index].innerHTML = "";
            for (var i = 0; i < temp.length; i++) {
                options[index].innerHTML += `<label><input name="${word}_${index}" type="radio" class="${index}" value="${temp[i]}" onclick="editOutput(${index}, '${word}', ${i})">${temp[i]}</label>`;
            }
            document.getElementsByClassName(`${index}`)[0].checked = true;
            output.innerHTML += `<div class="output_div">${temp[0]}</div>`;
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
    unboldAll("highlight-area");
    boldWord(index);
    let bold = text.charAt(cursorPosition - 1) != " ";
    correctHighlight(index, bold);
}

function correctHighlight(index, bold) {
    const highlightDiv = document.getElementById("highlight-area-2");
    const all = document.getElementsByClassName("output_div");
    highlightDiv.innerHTML = "";
    for (var i = 0; i < all.length; i++) {
        highlightDiv.innerHTML += all[i].innerHTML;
    }
    let counter = 0;
    for (var i = 0; i < index; i++) {
        counter += all[i].innerHTML.length;
    }
    unboldAll("highlight-area-2");
    if (bold) boldDiv(counter);
}

function editOutput(index, word, radio) {
    const all = document.getElementsByClassName("output_div");
    const all_inners = [];
    for (var i = 0; i < all.length; i++) {
        all_inners.push(all[i].innerHTML);
    }
    let output = document.getElementById("output-area");
    output.innerHTML = "";
    for (var i = 0; i < index; i++) {
        output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
    }
    let temp = jsonData[word][0];
    for (var i = 0; i < 4; i++) {
        if (languages_included[i]) {
            temp = temp.concat(jsonData[word][i]);
        }
    }
    output.innerHTML += `<div class="output_div">${temp[radio]}</div>`;
    for (var i = index + 1; i < all_inners.length; i++) {
        output.innerHTML += `<div class="output_div">${all_inners[i]}</div>`;
    }
    save[index] = radio;
}

function unboldAll(element) {
    const highlightDiv = document.getElementById(`${element}`);

    function removeBoldTags(node) {
        if (!node) return;

        if (node.nodeName === "span") {
            // Replace the bold node with its text content
            while (node.firstChild) {
                node.parentNode.insertBefore(node.firstChild, node);
            }
            node.parentNode.removeChild(node);
        } else if (node.hasChildNodes()) {
            // Recursively process child nodes
            Array.from(node.childNodes).forEach(removeBoldTags);
        }
    }

    // Start processing from the highlightDiv
    Array.from(highlightDiv.childNodes).forEach(removeBoldTags);
}

function boldWord(index) {
    const highlightDiv = document.getElementById("highlight-area");

    function wrapTokenAtIndex(node, tokenIndex) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.nodeValue;
            const tokens = text.split(/\s+/); // Split text into tokens
            let charIndex = 0;

            // Traverse tokens to find the target token at the given index
            for (let i = 0; i < tokens.length; i++) {
                const tokenStart = charIndex;
                const tokenEnd = charIndex + tokens[i].length;

                if (i === tokenIndex) {
                    const parent = node.parentNode;

                    // Split the text around the target token
                    const before = text.slice(0, tokenStart);
                    const target = text.slice(tokenStart, tokenEnd);
                    const after = text.slice(tokenEnd);

                    // Replace the original text node with new nodes
                    if (before) parent.insertBefore(document.createTextNode(before), node);

                    const boldElement = document.createElement('span');
                    boldElement.style.fontWeight = 'bold';
                    boldElement.textContent = target;
                    parent.insertBefore(boldElement, node);

                    if (after) parent.insertBefore(document.createTextNode(after), node);

                    parent.removeChild(node); // Remove the original text node
                    return;
                }

                // Update charIndex to the next token
                charIndex = tokenEnd + 1; // +1 for the space
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Process child nodes recursively
            Array.from(node.childNodes).forEach(child => wrapTokenAtIndex(child, tokenIndex));
        }
    }

    wrapTokenAtIndex(highlightDiv, index);
}

function boldDiv(index) {
    const container = document.getElementById("highlight-area-2");

    function wrapCharInTextNode(node, charIndex) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.nodeValue;

            if (charIndex >= 0 && charIndex < text.length) {
                const parent = node.parentNode;

                // Split the text into three parts: before, target character, and after
                const before = text.slice(0, charIndex);
                let non_abc = 1;
                while (/^[a-zA-Z\s]+$/.test(text.charAt(charIndex + non_abc)) && text.charAt(charIndex + non_abc) != "") {
                    non_abc++;
                }
                const target = text.slice(charIndex, charIndex + non_abc);
                const after = text.slice(charIndex + non_abc);

                // Replace the original text node with new nodes
                if (before) parent.insertBefore(document.createTextNode(before), node);

                const wrappedChar = document.createElement('span');
                wrappedChar.style.backgroundColor = 'rgb(226, 199, 140)'; // Highlight style
                wrappedChar.textContent = target;
                parent.insertBefore(wrappedChar, node);

                if (after) parent.insertBefore(document.createTextNode(after), node);

                parent.removeChild(node); // Remove the original text node
                return;
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Traverse child nodes recursively
            for (let child of Array.from(node.childNodes)) {
                const charLength = child.textContent.length;
                if (charIndex < charLength) {
                    wrapCharInTextNode(child, charIndex);
                    return;
                } else {
                    charIndex -= charLength;
                }
            }
        }
    }

    wrapCharInTextNode(container, index);
}

let languages_included = [1, 0, 0, 0];
function editLanguages(index) {
    languages_included[index] = !languages_included[index] ? 1 : 0;
}

function copy() {
    const all = document.getElementsByClassName("output_div");
    let text = "";
    for (var i = 0; i < all.length; i++) {
        text += all[i].innerHTML;
    }
    navigator.clipboard.writeText(text);
}

let jsonData; // Global variable to store the fetched JSON
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

// Call this function when the page loads
loadLanguageData();

function menuMOU() {
    let menus = document.getElementsByClassName("menu-button");
    for (var i = 0; i < menus.length; i++) {
        menus[i].style.backgroundColor = "rgb(226, 199, 140)";
    }
}
    
function menuMOV(select) {
    let menus = document.getElementsByClassName("menu-button");
    menus[select].style.backgroundColor = "#FAE6AA";
}