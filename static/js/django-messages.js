/**
 * Django Messages to Toast Notifications
 * 
 * This script finds Django messages in the DOM and converts them to toast notifications.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize djangoMessages array if it doesn't exist
  window.djangoMessages = window.djangoMessages || [];
  
  // Find all Django message elements
  const messageElements = document.querySelectorAll('.django-message');
  
  // Convert message elements to JavaScript objects and add them to djangoMessages array
  messageElements.forEach(function(element) {
    const message = element.textContent.trim();
    const tags = element.getAttribute('data-tags') || 'info';
    
    // Add message to djangoMessages array
    window.djangoMessages.push({
      message: message,
      tags: tags
    });
    
    // Remove the message element from the DOM
    element.parentNode.removeChild(element);
  });
  
  // Process messages if createToast function is available
  if (typeof window.createToast === 'function') {
    window.djangoMessages.forEach(function(message, index) {
      // Stagger the appearance of toasts
      setTimeout(function() {
        window.createToast(message.message, message.tags);
      }, index * 150);
    });
  }
});
