let isAnimating = false;

document.addEventListener("DOMContentLoaded", function() {
    // Find the first content section and show it
    const firstSection = document.querySelector('.content-section');
    if (firstSection) {
        showSection(firstSection.id); // Show the first section
    }

    isAnimating = true; // Prevent further animations during initial typing
    initialTyping('en'); // Load the page with typing animation only
});

function showSection(sectionId) {
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    const sectionToShow = document.getElementById(sectionId);
    if (sectionToShow) {
        sectionToShow.classList.add('active');
    } else {
        console.error(`No element found with ID: ${sectionId}`);
    }
}

function initialTyping(language) {
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    const typeSpeed = 10; // Speed per character in milliseconds

    elementsToTranslate.forEach((element, index) => {
        const translationKey = element.getAttribute('data-translate');
        const newText = translations[language][translationKey];

        // Start the typing animation for the initial load
        setTimeout(() => typeText(element, newText, typeSpeed), typeSpeed * index);
    });

    // Re-enable language switching after initial typing completes
    setTimeout(() => {
        isAnimating = false;
    }, typeSpeed * elementsToTranslate.length);
}

function toggleLanguage(language) {
    if (isAnimating) return; // Prevent language change during animation

    const enLink = document.getElementById('en-link');
    const jaLink = document.getElementById('ja-link');

    if (language === 'en') {
        enLink.classList.add('active');
        jaLink.classList.remove('active');
    } else if (language === 'ja') {
        jaLink.classList.add('active');
        enLink.classList.remove('active');
    }

    // Handle the text animation
    animateTextChange(language);
}

function animateTextChange(language) {
    isAnimating = true;
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    const totalDuration = 500; // Total time for all animations in milliseconds

    elementsToTranslate.forEach((element, index) => {
        const translationKey = element.getAttribute('data-translate');
        const newText = translations[language][translationKey];
        const currentText = element.textContent;

        // Calculate time per character for deletion and typing
        const maxLength = Math.max(currentText.length, newText.length);
        const deleteSpeed = totalDuration / (2 * maxLength);
        const typeSpeed = totalDuration / (2 * maxLength);

        // Start the deletion animation
        setTimeout(() => deleteText(element, newText, deleteSpeed, typeSpeed), deleteSpeed * index);
    });

    // Re-enable language switching after all animations complete
    setTimeout(() => {
        isAnimating = false;
    }, totalDuration);
}

function deleteText(element, newText, deleteSpeed, typeSpeed) {
    const currentText = element.textContent;
    let charIndex = currentText.length;

    const deleteInterval = setInterval(() => {
        if (charIndex > 0) {
            element.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
        } else {
            clearInterval(deleteInterval);
            // Start typing the new text after deletion is complete
            typeText(element, newText, typeSpeed);
        }
    }, deleteSpeed);
}

function typeText(element, newText, typeSpeed) {
    let charIndex = 0;
    element.classList.add('typing');
    element.textContent = ''; // Clear the text to start typing

    const typeInterval = setInterval(() => {
        if (charIndex < newText.length) {
            element.textContent += newText[charIndex];
            charIndex++;
        } else {
            clearInterval(typeInterval);
            element.classList.remove('typing');
        }
    }, typeSpeed);
}
