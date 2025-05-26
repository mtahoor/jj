/**
 * Simple Toast Notification System
 *
 * This script creates and manages toast notifications that appear at the top-center
 * of the screen and automatically disappear after a few seconds.
 */

// Create toast container if it doesn't exist
function createToastContainer() {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 z-50 flex flex-col gap-2 items-center max-w-lg w-full';
    document.body.appendChild(container);
  }
  return container;
}

// Create a toast notification
function createToast(message, type = 'info') {
  const container = createToastContainer();
  const id = 'toast-' + Date.now();

  // Determine toast style based on type
  let bgColor, textColor, borderColor, iconBg, iconColor, icon;

  switch (type) {
    case 'success':
      bgColor = 'bg-green-100';
      textColor = 'text-green-800';
      borderColor = 'border-l-4 border-green-500';
      iconBg = 'bg-green-200';
      iconColor = 'text-green-500';
      icon = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>';
      break;
    case 'error':
      bgColor = 'bg-red-100';
      textColor = 'text-red-800';
      borderColor = 'border-l-4 border-red-500';
      iconBg = 'bg-red-200';
      iconColor = 'text-red-500';
      icon = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
      break;
    case 'warning':
      bgColor = 'bg-yellow-100';
      textColor = 'text-yellow-800';
      borderColor = 'border-l-4 border-yellow-500';
      iconBg = 'bg-yellow-200';
      iconColor = 'text-yellow-500';
      icon = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>';
      break;
    default: // info
      bgColor = 'bg-blue-100';
      textColor = 'text-blue-800';
      borderColor = 'border-l-4 border-blue-500';
      iconBg = 'bg-blue-200';
      iconColor = 'text-blue-500';
      icon = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>';
  }

  // Create toast element
  const toast = document.createElement('div');
  toast.id = id;
  toast.className = `flex items-center w-full max-w-md p-4 mb-2 rounded-lg shadow-md transition-all duration-300 transform ${bgColor} ${textColor} ${borderColor}`;
  toast.style.opacity = '0';
  toast.style.transform = 'translateY(-100%)';

  // Create toast content
  toast.innerHTML = `
    <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg ${iconBg} ${iconColor}">
      ${icon}
    </div>
    <div class="ml-3 text-sm font-normal flex-grow">${message}</div>
    <button type="button" class="ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex h-8 w-8 hover:bg-gray-200 hover:text-gray-900 focus:ring-2 focus:ring-gray-300" aria-label="Close">
      <span class="sr-only">Close</span>
      <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
      </svg>
    </button>
  `;

  // Add toast to container
  container.appendChild(toast);

  // Animate toast in
  setTimeout(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  }, 10);

  // Add close button event listener
  const closeButton = toast.querySelector('button');
  closeButton.addEventListener('click', () => {
    dismissToast(toast);
  });

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    dismissToast(toast);
  }, 5000);

  return toast;
}

// Dismiss a toast notification
function dismissToast(toast) {
  // Only dismiss if the toast is still visible
  if (toast.style.opacity !== '0') {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-100%)';

    // Remove from DOM after animation completes
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }

      // Check if container is empty and remove it if it is
      const container = document.getElementById('toast-container');
      if (container && container.children.length === 0) {
        container.parentNode.removeChild(container);
      }
    }, 300);
  }
}

// Process Django messages on page load
document.addEventListener('DOMContentLoaded', function() {
  // Check if Django messages are available in the page
  if (window.djangoMessages && Array.isArray(window.djangoMessages)) {
    window.djangoMessages.forEach((message, index) => {
      // Stagger the appearance of toasts
      setTimeout(() => {
        createToast(message.message, message.tags);
      }, index * 150);
    });
  }
});

// Expose functions globally
window.createToast = createToast;
window.dismissToast = dismissToast;
