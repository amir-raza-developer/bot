// ✅ FORM FILLER JAVASCRIPT

const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

// Get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Store images globally
let selectedImages = [];

// Image upload handler
document.getElementById('imageUploadArea')?.addEventListener('click', function() {
  document.getElementById('images').click();
});

document.getElementById('imageUploadArea')?.addEventListener('dragover', function(e) {
  e.preventDefault();
  this.style.borderColor = '#357ab8';
  this.style.background = '#111';
});

document.getElementById('imageUploadArea')?.addEventListener('dragleave', function() {
  this.style.borderColor = '#4a90e2';
  this.style.background = '#0a0a0a';
});

document.getElementById('imageUploadArea')?.addEventListener('drop', function(e) {
  e.preventDefault();
  const files = e.dataTransfer.files;
  handleImageSelection(files);
});

document.getElementById('images')?.addEventListener('change', function(e) {
  handleImageSelection(e.target.files);
});

function handleImageSelection(files) {
  if (files.length === 0) return;

  const maxFiles = 100;
  if (selectedImages.length + files.length > maxFiles) {
    alert(`Max ${maxFiles} images allowed!`);
    return;
  }

  for (let file of files) {
    if (file.type.startsWith('image/')) {
      selectedImages.push(file);
    }
  }

  updateImagePreview();
}

function updateImagePreview() {
  const container = document.getElementById('previewContainer');
  container.innerHTML = '';
  document.getElementById('imgCount').textContent = selectedImages.length;

  selectedImages.forEach((img, index) => {
    const reader = new FileReader();
    reader.onload = function(e) {
      const div = document.createElement('div');
      div.className = 'image-preview';
      div.innerHTML = `
        <img src="${e.target.result}" alt="Preview">
        <button type="button" class="remove-btn" onclick="removeImage(${index})">✕</button>
      `;
      container.appendChild(div);
    };
    reader.readAsDataURL(img);
  });
}

function removeImage(index) {
  selectedImages.splice(index, 1);
  updateImagePreview();
}

// Remove all images
document.getElementById('removeBtn')?.addEventListener('click', function() {
  if (confirm('Remove all images?')) {
    selectedImages = [];
    updateImagePreview();
    document.getElementById('images').value = '';
  }
});

// Count titles
document.getElementById('titles')?.addEventListener('input', function() {
  const count = this.value.trim().split('\n').filter(t => t.trim()).length;
  document.getElementById('titlesCount').textContent = count;
});

// Count locations
document.getElementById('locations')?.addEventListener('input', function() {
  const count = this.value.trim().split('\n').filter(l => l.trim()).length;
  document.getElementById('locationsCount').textContent = count;
});

// Load previous data
async function loadPreviousData() {
  try {
    const res = await fetch('/listings/get-latest/');
    const data = await res.json();

    if (data.success && data.listing) {
      const listing = data.listing;
      document.getElementById('listing_id').value = listing.id;
      document.getElementById('price').value = listing.price;
      document.getElementById('desc').value = listing.description;
      document.getElementById('category').value = listing.category || '';
      document.getElementById('condition').value = listing.condition || '';
      document.getElementById('availability').value = listing.availability || '';
      document.getElementById('tags').value = listing.tags || '';
      document.getElementById('tabs').value = listing.tabs || 1;

      if (listing.titles.length > 0) {
        document.getElementById('titles').value = listing.titles.join('\n');
        document.getElementById('titlesCount').textContent = listing.titles.length;
      }

      if (listing.locations.length > 0) {
        document.getElementById('locations').value = listing.locations.join('\n');
        document.getElementById('locationsCount').textContent = listing.locations.length;
      }
    }
  } catch (err) {
    console.log('No previous data found');
  }
}

// Save listing data
document.getElementById('saveDataBtn')?.addEventListener('click', async function() {
  const titles = document.getElementById('titles').value
    .trim()
    .split('\n')
    .filter(t => t.trim());
  const locations = document.getElementById('locations').value
    .trim()
    .split('\n')
    .filter(l => l.trim());

  if (titles.length === 0 || locations.length === 0) {
    alert('Please enter at least one title and one location');
    return;
  }

  if (selectedImages.length === 0) {
    alert('Please upload at least one image');
    return;
  }

  const formData = new FormData();
  formData.append('listing_id', document.getElementById('listing_id').value || '');
  formData.append('price', document.getElementById('price').value);
  formData.append('description', document.getElementById('desc').value);
  formData.append('category', document.getElementById('category').value);
  formData.append('condition', document.getElementById('condition').value);
  formData.append('availability', document.getElementById('availability').value);
  formData.append('tags', document.getElementById('tags').value);
  formData.append('tabs', document.getElementById('tabs').value);

  const delivery = Array.from(document.querySelectorAll('input[name="delivery"]:checked'))
    .map(c => c.value)
    .join(',');
  formData.append('delivery', delivery);

  titles.forEach(t => formData.append('titles', t));
  locations.forEach(l => formData.append('locations', l));
  selectedImages.forEach(img => formData.append('images', img));

  try {
    const res = await fetch('/listings/save/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: formData
    });

    const data = await res.json();
    const statusEl = document.getElementById('saveStatus');

    if (data.success) {
      statusEl.textContent = '✅ ' + data.message;
      statusEl.style.color = '#4ade80';
      statusEl.style.display = 'block';
      setTimeout(() => {
        statusEl.style.display = 'none';
      }, 3000);
    } else {
      statusEl.textContent = '❌ ' + data.error;
      statusEl.style.color = '#f87171';
      statusEl.style.display = 'block';
    }
  } catch (err) {
    console.error('Error:', err);
    const statusEl = document.getElementById('saveStatus');
    statusEl.textContent = '⚠️ Error saving data';
    statusEl.style.color = '#f87171';
    statusEl.style.display = 'block';
  }
});

// Load data on page load
document.addEventListener('DOMContentLoaded', loadPreviousData);
