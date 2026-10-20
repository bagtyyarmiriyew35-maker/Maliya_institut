/* ============================================================
   CUSTOM ADMIN PANEL — panel.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Replace Font Awesome icons with inline SVGs (for offline mode) ─
  function replaceFAWithSVG() {
    const iconMap = {
      "fa-shield-halved": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
      "fa-gauge-high": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
      "fa-images": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
      "fa-newspaper": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8M15 18h-5M10 6h8v4h-8V6Z"/>',
      "fa-file-lines": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M10 9h4M10 13h6M10 17h6"/>',
      "fa-folder-open": '<path d="m6 14 1.45-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.55 6a2 2 0 0 1-1.94 1.5H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.93a2 2 0 0 1 1.66.9l.82 1.2a2 2 0 0 0 1.66.9H18a2 2 0 0 1 2 2v2"/>',
      "fa-trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M4 22h16M10 14.66V17c0 .55-.45 1-1 1H4v2h16v-2h-5c-.55 0-1-.45-1-1v-2.34M12 2a6 6 0 0 1 6 6v3.5c0 1.66-1.34 3-3 3H9a3 3 0 0 1-3-3V8a6 6 0 0 1 6-6Z"/>',
      "fa-building-columns": '<path d="M3 22h18M6 18v-7M10 18v-7M14 18v-7M18 18v-7M12 2 3 7h18Z"/>',
      "fa-sitemap": '<path d="M3 11h3v3H3zM18 11h3v3h-3zM10 3h4v3h-4zM10 18h4v3h-4zM12 6v5M12 14v4M6 12.5h12"/>',
      "fa-handshake": '<path d="m11 17 2 2a1 1 0 0 0 1.4 0l4-4a1 1 0 0 0 0-1.4l-2-2M12 14 7 9M18 8l-6-6a1 1 0 0 0-1.4 0L4 8a1 1 0 0 0 0 1.4l3 3c.4.4 1 .4 1.4 0L12 8M15 11l-3 3c-.4.4-1 .4-1.4 0l-1-1"/>',
      "fa-envelope": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
      "fa-gear": '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.1a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
      "fa-arrow-up-right-from-square": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3"/>',
      "fa-django": '<rect width="20" height="20" rx="4" fill="#092e20"/><path d="M6 6h4c1.5 0 2.5 1 2.5 2.5v3c0 1.5-1 2.5-2.5 2.5H6zm2.5 6h1.5c.6 0 1-.4 1-1V9.5c0-.6-.4-1-1-1h-1.5zM14 6h4.5v2h-3v6H14z" fill="white"/>',
      "fa-right-from-bracket": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
      "fa-right-to-bracket": '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>',
      "fa-bars": '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
      "fa-clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
      "fa-eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
      "fa-eye-slash": '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61M2 2l20 20"/>',
      "fa-pen": '<path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
      "fa-trash": '<path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2M10 11v6M14 11v6"/>',
      "fa-trash-can": '<path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2M10 11v6M14 11v6"/>',
      "fa-plus": '<path d="M5 12h14M12 5v14"/>',
      "fa-arrow-left": '<path d="M19 12H5M12 19l-7-7 7-7"/>',
      "fa-file-pdf": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M9 15h6M9 11h6"/>',
      "fa-file-video": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><polygon points="10 11 15 14 10 17 10 11"/>',
      "fa-file-audio": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 18V12l6-2v6"/><circle cx="8" cy="18" r="1.5"/><circle cx="14" cy="16" r="1.5"/>',
      "fa-file-image": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><circle cx="10" cy="12" r="1.5"/><path d="m18 19-3.5-3.5a1 1 0 0 0-1.4 0L7 21"/>',
      "fa-file-word": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="m9 13 1.5 5 1.5-5 1.5 5 1.5-5"/>',
      "fa-file-excel": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 13h6M9 16h6M12 11v7"/>',
      "fa-file-powerpoint": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><circle cx="12" cy="14" r="3"/>',
      "fa-file-zipper": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 6h4M10 8h4M10 10h4M10 12h4M10 14h4"/>',
      "fa-paperclip": '<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l7.88-7.88"/>',
      "fa-download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
      "fa-check": '<polyline points="20 6 9 17 4 12"/>',
      "fa-circle": '<circle cx="12" cy="12" r="10" fill="currentColor"/>',
      "fa-circle-exclamation": '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
      "fa-circle-check": '<circle cx="12" cy="12" r="10"/><polyline points="12 8 12 12 14 14"/>',
      "fa-circle-notch": '<path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>',
      "fa-lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
      "fa-user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
      "fa-cloud-arrow-up": '<path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242M12 12v9M8 16l4-4 4 4"/>',
      "fa-building": '<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01"/>',
      "fa-sliders": '<line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="2" x2="6" y1="14" y2="14"/><line x1="10" x2="14" y1="8" y2="8"/><line x1="18" x2="22" y1="16" y2="16"/>',
      "fa-link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
      "fa-image": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
      "fa-facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
      "fa-twitter": '<path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/>',
      "fa-linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
      "fa-instagram": '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
      "fa-youtube": '<path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 1.94-2z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/>'
    };

    const icons = document.querySelectorAll('i[class*="fa-"]');
    icons.forEach(icon => {
      let matchedKey = null;
      icon.classList.forEach(cls => {
        if (iconMap[cls]) {
          matchedKey = cls;
        }
      });

      if (matchedKey) {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("width", "1em");
        svg.setAttribute("height", "1em");
        svg.setAttribute("fill", "none");
        svg.setAttribute("stroke", "currentColor");
        svg.setAttribute("stroke-width", "2.2");
        svg.setAttribute("stroke-linecap", "round");
        svg.setAttribute("stroke-linejoin", "round");
        svg.style.display = "inline-block";
        svg.style.verticalAlign = "middle";
        
        // Preserve some basic layout properties
        const style = window.getComputedStyle(icon);
        svg.style.marginRight = style.marginRight;
        svg.style.marginLeft = style.marginLeft;
        svg.style.color = style.color;
        
        // Retain classes except Font Awesome ones
        icon.classList.forEach(cls => {
          if (!cls.startsWith("fa-")) {
            svg.classList.add(cls);
          }
        });
        
        // Handle specific icons needing fills
        if (matchedKey === 'fa-circle') {
          svg.setAttribute("fill", "currentColor");
        }
        
        svg.innerHTML = iconMap[matchedKey];
        icon.parentNode.replaceChild(svg, icon);
      }
    });
  }

  // Run the replacement
  replaceFAWithSVG();

  // ── Sidebar toggle (mobile) ──────────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.panel-sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    sidebar && sidebar.classList.add('open');
    overlay && overlay.classList.add('active');
  }

  function closeSidebar() {
    sidebar && sidebar.classList.remove('open');
    overlay && overlay.classList.remove('active');
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      sidebar && sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // ── Active nav link ──────────────────────────────────────
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.sidebar-nav a');
  let bestMatch = null;
  let bestLen = 0;

  navLinks.forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href.length > bestLen) {
      bestMatch = link;
      bestLen = href.length;
    }
  });

  if (bestMatch) bestMatch.classList.add('active');

  // ── Delete confirm modal ─────────────────────────────────
  const deleteModal = document.getElementById('deleteModal');
  let deleteForm = null;

  document.querySelectorAll('.btn-delete-trigger').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const formId = btn.dataset.formId;
      deleteForm = document.getElementById(formId);
      if (deleteModal) deleteModal.classList.add('active');
    });
  });

  const modalCancel = document.getElementById('modalCancel');
  const modalConfirm = document.getElementById('modalConfirm');

  if (modalCancel) {
    modalCancel.addEventListener('click', function () {
      deleteModal && deleteModal.classList.remove('active');
      deleteForm = null;
    });
  }

  if (modalConfirm) {
    modalConfirm.addEventListener('click', function () {
      if (deleteForm) deleteForm.submit();
    });
  }

  if (deleteModal) {
    deleteModal.addEventListener('click', function (e) {
      if (e.target === deleteModal) {
        deleteModal.classList.remove('active');
        deleteForm = null;
      }
    });
  }

  // ── Image preview on file input ─────────────────────────
  document.querySelectorAll('input[type="file"][data-preview]').forEach(function (input) {
    input.addEventListener('change', function () {
      const previewId = input.dataset.preview;
      const preview = document.getElementById(previewId);
      if (!preview) return;

      if (input.files && input.files[0]) {
        const file = input.files[0];
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
          };
          reader.readAsDataURL(file);
        } else {
          // For non-images (PDF etc.), show filename
          preview.style.display = 'none';
          const nameEl = document.getElementById(previewId + '_name');
          if (nameEl) nameEl.textContent = file.name;
        }
      }
    });
  });

  // Show filename, size & category on file upload areas
  document.querySelectorAll('.file-upload-area input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () {
      const area = input.closest('.file-upload-area');
      if (!area) return;
      const textEl = area.querySelector('.file-upload-text');
      const iconEl = area.querySelector('.file-upload-icon');
      if (textEl && input.files && input.files[0]) {
        const file = input.files[0];
        const ext = file.name.split('.').pop().toLowerCase();
        let sizeStr = '';
        if (file.size < 1024 * 1024) {
          sizeStr = (file.size / 1024).toFixed(1) + ' KB';
        } else {
          sizeStr = (file.size / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        let typeBadge = '';
        if (['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'].includes(ext)) {
          typeBadge = '<span style="background:#f3e8ff;color:#7c3aed;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">Wideo faýl</span>';
        } else if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'svg'].includes(ext)) {
          typeBadge = '<span style="background:#e0f2fe;color:#0284c7;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">Surat</span>';
        } else if (['mp3', 'wav', 'ogg', 'm4a', 'flac'].includes(ext)) {
          typeBadge = '<span style="background:#ffe4e6;color:#e11d48;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">Aýdym / Ses</span>';
        } else if (['pdf'].includes(ext)) {
          typeBadge = '<span style="background:#fef2f2;color:#dc2626;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">PDF resminama</span>';
        } else if (['doc', 'docx'].includes(ext)) {
          typeBadge = '<span style="background:#eff6ff;color:#2563eb;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">Word resminama</span>';
        } else if (['xls', 'xlsx', 'csv'].includes(ext)) {
          typeBadge = '<span style="background:#f0fdf4;color:#16a34a;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">Excel tablisasy</span>';
        } else if (['zip', 'rar', '7z'].includes(ext)) {
          typeBadge = '<span style="background:#faf5ff;color:#9333ea;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-left:6px;">Arhiw (Zip)</span>';
        }
        
        textEl.innerHTML = '<strong style="color:var(--panel-primary, #048848);font-size:14px;">' + file.name + '</strong>' + typeBadge + '<br><span style="color:var(--panel-text-muted);font-size:12px;">Göwrümi: ' + sizeStr + ' &bull; Ýatda saklanynda ulgama ýükleniler</span>';
      }
    });
  });

  // ── Auto-dismiss alerts ──────────────────────────────────
  const alerts = document.querySelectorAll('.panel-alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(function () { alert.remove(); }, 400);
    }, 4000);
  });

  // ── Topbar clock ────────────────────────────────────────
  const clockEl = document.getElementById('panelClock');
  if (clockEl) {
    function updateClock() {
      const now = new Date();
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      clockEl.textContent = h + ':' + m;
    }
    updateClock();
    setInterval(updateClock, 30000);
  }

  // ── Number formatting for stats ──────────────────────────
  document.querySelectorAll('.stat-card-panel .number').forEach(function (el) {
    const n = parseInt(el.textContent.replace(/\D/g, ''), 10);
    if (!isNaN(n)) el.textContent = n.toLocaleString();
  });

  // ── Slug auto-generate from title ───────────────────────
  const titleInput = document.getElementById('id_title_tm_slug_source');
  const slugInput = document.getElementById('id_slug');
  if (titleInput && slugInput && !slugInput.value) {
    titleInput.addEventListener('input', function () {
      slugInput.value = titleInput.value
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9\-]/g, '');
    });
  }

  // ── Table row highlight on hover ─────────────────────────
  document.querySelectorAll('.panel-table tbody tr').forEach(function (row) {
    row.style.transition = 'background 0.15s';
  });

});
