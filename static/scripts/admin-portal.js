document.addEventListener('DOMContentLoaded', function() {
    let romanizationCount = 1;
    
    // Add event listener to the plus button
    document.getElementById('add-romanization').addEventListener('click', function() {
        addRomanizationField();
    });
    
    // Add event listener to remove buttons (using event delegation)
    document.getElementById('romanization-container').addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-romanization')) {
            removeRomanizationField(e.target);
        }
    });
    
    function addRomanizationField() {
        romanizationCount++;
        
        const container = document.getElementById('romanization-container');
        const romanizationGroup = document.createElement('div');
        romanizationGroup.className = 'romanization-group';
        romanizationGroup.dataset.index = romanizationCount;
        
        romanizationGroup.innerHTML = `
            <select name="language_${romanizationCount}" required>
                <option value="Shanghainese">Shanghainese</option>
                <option value="Korean">Korean</option>
                <option value="Taiwanese">Taiwanese</option>
                <option value="Vietnamese">Vietnamese</option>
            </select>
            <input type="text" name="romanization_${romanizationCount}" placeholder="Enter the romanization" autocomplete="off" maxlength="6" required/>
            <button type="button" class="remove-romanization" title="Remove this romanization">−</button>
        `;
        
        container.appendChild(romanizationGroup);
        
        // Focus on the new romanization input
        romanizationGroup.querySelector('input[type="text"]').focus();
    }
    
    function removeRomanizationField(button) {
        const romanizationGroup = button.closest('.romanization-group');
        const container = document.getElementById('romanization-container');
        
        // Don't allow removing if it's the only field
        if (container.children.length > 1) {
            romanizationGroup.remove();
        }
    }
}); 