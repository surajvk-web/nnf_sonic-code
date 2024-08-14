// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript loaded!');
});











// script for slider
const carousel = document.querySelector(".carousel"),
      firstImg = carousel.querySelectorAll("img")[0];
arrowIcons = document.querySelectorAll(".wrapper i");

let isDragStart = false, isDragging = false, prevPageX, prevScrollLeft, positionDiff;

// Function to show/hide arrow icons based on the carousel's scroll position
const showHideIcons = () => {
    let scrollWidth = carousel.scrollWidth - carousel.clientWidth; // getting max scrollable width
    // showing and hiding prev/next icon according to carousel scroll left value
    arrowIcons[0].style.display = carousel.scrollLeft == 0 ? "none" : "block";
    arrowIcons[1].style.display = carousel.scrollLeft == scrollWidth ? "none" : "block";
};

// Function to handle auto sliding
const autoSlide = () => {
    let firstImgWidth = firstImg.clientWidth + 14;
    if (carousel.scrollLeft >= (carousel.scrollWidth - carousel.clientWidth)) {
        carousel.scrollLeft = 0;
    } else {
        carousel.scrollLeft += firstImgWidth;
    }
    showHideIcons();
};

// Adding click event listeners to arrow icons
arrowIcons.forEach(icon => {
    icon.addEventListener("click", () => {
        let firstImgWidth = firstImg.clientWidth + 14;
        carousel.scrollLeft += icon.id == "left" ? -firstImgWidth : firstImgWidth;
        setTimeout(() => showHideIcons(), 60);
    });
});

// Function to handle drag start
const dragStart = (e) => {
    isDragStart = true;
    prevPageX = e.pageX || e.touches[0].pageX;
    prevScrollLeft = carousel.scrollLeft;
    clearInterval(autoSlideInterval); // Pause auto sliding while dragging
};

// Function to handle dragging
const dragging = (e) => {
    if (!isDragStart) return;
    e.preventDefault();
    isDragging = true;
    carousel.classList.add("dragging");
    positionDiff = (e.pageX || e.touches[0].pageX) - prevPageX;
    carousel.scrollLeft = prevScrollLeft - positionDiff;
    showHideIcons();
};

// Function to handle drag stop
const dragStop = () => {
    isDragStart = false;
    carousel.classList.remove("dragging");
    if (!isDragging) return;
    isDragging = false;
    autoSlide();
    autoSlideInterval = setInterval(autoSlide, 3000); // Resume auto sliding after dragging stops
};

// Adding event listeners for dragging functionality
carousel.addEventListener("mousedown", dragStart);
carousel.addEventListener("touchstart", dragStart);
carousel.addEventListener("mousemove", dragging);
carousel.addEventListener("touchmove", dragging);
carousel.addEventListener("mouseup", dragStop);
carousel.addEventListener("mouseleave", dragStop);
carousel.addEventListener("touchend", dragStop);

// Set interval for automatic sliding
let autoSlideInterval = setInterval(autoSlide, 4000); // slides every 3 seconds

// Initial call to show/hide icons
showHideIcons();

// script for slider ends here




// script for ABOUT US
// script for ABOUT US
const container = document.querySelector('.container');

container.addEventListener('mouseenter', () => {
    container.classList.add('hovered');
});
// script for ABOUT US ends here


// script for ABOUT US ends here




// script for quiz
document.getElementById('quiz-form').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('quiz-form').style.display = 'none';
    document.getElementById('submission-message').classList.remove('hidden');
});

// script for quiz ends here





// script for BLOG POST
console.log("Image Path: {{ latest_blog.image_path }}");
// script for BLOG POST ends here

