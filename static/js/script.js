/**
 * CampusCare – Next-Gen SaaS Frontend Script
 * Micro-interactions, Live Image Preview, Drag & Drop Upload, and UI Utilities
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle & Backdrop
  const sidebar = document.querySelector('.app-sidebar');
  const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (sidebarBackdrop) {
        sidebarBackdrop.classList.toggle('show');
      }
    });
  }

  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', function () {
      if (sidebar) sidebar.classList.remove('show');
      sidebarBackdrop.classList.remove('show');
    });
  }

  // 2. Universal Image Selection & Live Preview Handler
  const fileInput = document.getElementById('id_image') || document.querySelector('input[type="file"][name="image"]');
  const previewCard = document.getElementById('imagePreviewCard') || document.getElementById('imagePreviewContainer');
  const previewImg = document.getElementById('liveImagePreview') || document.getElementById('imagePreviewThumb');
  const metaText = document.getElementById('liveImageMeta');
  const clearBtn = document.getElementById('clearImageBtn') || document.getElementById('removeImageBtn');

  if (fileInput) {
    fileInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        const file = this.files[0];

        // Max 5MB check
        const maxSizeBytes = 5 * 1024 * 1024;
        if (file.size > maxSizeBytes) {
          alert('Selected file exceeds the 5MB size limit. Please choose a smaller image.');
          this.value = '';
          if (previewCard) previewCard.style.display = 'none';
          return;
        }

        // Live preview via FileReader
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = function (e) {
            if (previewImg) {
              previewImg.src = e.target.result;
            }
            if (metaText) {
              const sizeKb = (file.size / 1024).toFixed(1);
              metaText.innerHTML = `<span class="badge bg-light text-dark border me-1">${file.name}</span> <span class="badge bg-light text-muted border">${sizeKb} KB</span>`;
            }
            if (previewCard) {
              previewCard.style.display = 'block';
            }
          };
          reader.readAsDataURL(file);
        }
      }
    });
  }

  if (clearBtn && fileInput) {
    clearBtn.addEventListener('click', function (e) {
      e.preventDefault();
      fileInput.value = '';
      if (previewCard) previewCard.style.display = 'none';
      if (previewImg) previewImg.src = '';
      if (metaText) metaText.innerHTML = '';
    });
  }

  // 3. Dynamic Greeting (Morning, Afternoon, Evening)
  const greetingEl = document.getElementById('timeGreeting');
  if (greetingEl) {
    const hour = new Date().getHours();
    if (hour < 12) {
      greetingEl.textContent = 'Good morning';
    } else if (hour < 18) {
      greetingEl.textContent = 'Good afternoon';
    } else {
      greetingEl.textContent = 'Good evening';
    }
  }

  // 4. Password Visibility Toggle
  const togglePasswordBtns = document.querySelectorAll('.toggle-password-btn');
  togglePasswordBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        const icon = this.querySelector('i');
        if (icon) {
          icon.classList.toggle('bi-eye', !isPassword);
          icon.classList.toggle('bi-eye-slash', isPassword);
        }
      }
    });
  });

  // 5. Auto-dismiss alerts after 6 seconds
  const autoDismissAlerts = document.querySelectorAll('.alert-dismissible');
  autoDismissAlerts.forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  // 6. Live Character Counter for Description Textarea
  const descTextarea = document.querySelector('textarea[name="description"]');
  const descCountEl = document.getElementById('descCharCount');
  if (descTextarea && descCountEl) {
    function updateCount() {
      const len = descTextarea.value.length;
      descCountEl.innerHTML = `<i class="bi bi-fonts me-1"></i>${len} characters entered`;
      if (len < 15) {
        descCountEl.classList.add('text-muted');
        descCountEl.classList.remove('text-success');
      } else {
        descCountEl.classList.remove('text-muted');
        descCountEl.classList.add('text-success');
      }
    }
    descTextarea.addEventListener('input', updateCount);
    updateCount();
  }
});

/**
 * 1-Click Autofill Helper for Class-Test Evaluators
 */
function fillDemoCredentials(username, password) {
  const idInput = document.getElementById('id_identifier');
  const pwdInput = document.getElementById('id_password');
  if (idInput && pwdInput) {
    idInput.value = username;
    pwdInput.value = password;
    // Add visual flash effect
    idInput.style.backgroundColor = '#eff6ff';
    pwdInput.style.backgroundColor = '#eff6ff';
    setTimeout(function () {
      idInput.style.backgroundColor = '';
      pwdInput.style.backgroundColor = '';
    }, 600);
  }
}
