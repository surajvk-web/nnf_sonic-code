// javascript code for COURSE REGISTRATION message 
document.getElementById('course-registration').addEventListener('click', function(event) {
    event.preventDefault();
    const message = document.getElementById('floating-message');
    
    if (message.classList.contains('hidden')) {
        message.classList.remove('hidden');
        // Set a timeout to hide the message after 5 seconds
        setTimeout(function() {
            message.classList.add('hidden');
        }, 5000);
    } else {
        message.classList.add('hidden');
    }
});

document.addEventListener('click', function(event) {
    const message = document.getElementById('floating-message');
    const link = document.getElementById('course-registration');
    
    // Check if the click was outside the message and link
    if (!message.contains(event.target) && event.target !== link) {
        message.classList.add('hidden');
    }
});
// javascript code for course registration message till here only



// code for user login welcome message
document.addEventListener('DOMContentLoaded', function() {
  // Auto-hide flash messages after 5 seconds
  setTimeout(function() {
      const flashMessages = document.querySelectorAll('#flash-messages .alert');
      flashMessages.forEach(function(message) {
          message.style.opacity = '0';
          setTimeout(function() {
              message.remove();0
          }, 1000); // Match the transition duration in CSS
      });
  }, 5000); // 3 seconds

  // Click-to-dismiss functionality
  document.addEventListener('click', function(event) {
      if (event.target.matches('.alert-dismissible') || event.target.closest('.alert-dismissible')) {
          event.target.closest('.alert').remove();
      }
  });
});
// code for user login welcome message





// for testing line message box
function showContactInfo() {
    document.getElementById('contactModal').style.display = 'block';
  }
  
  function closeModal() {
    document.getElementById('contactModal').style.display = 'none';
  }
  
  // Close the modal if the user clicks outside of it
  window.onclick = function(event) {
    if (event.target == document.getElementById('contactModal')) {
      document.getElementById('contactModal').style.display = 'none';
    }
  }
// for testing line message box code till here only
  