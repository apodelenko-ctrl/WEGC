// Database management for real estate projects
class ProjectDatabase {
  constructor() {
    this.projects = [];
    this.loaded = false;
  }

  async loadProjects() {
    try {
      const response = await fetch('/data/projects.json');
      const data = await response.json();
      this.projects = data.projects;
      this.loaded = true;
      return this.projects;
    } catch (error) {
      console.error('Error loading projects:', error);
      return [];
    }
  }

  getProject(id) {
    return this.projects.find(project => project.id === id);
  }

  getAllProjects() {
    return this.projects;
  }

  getProjectsByType(type) {
    return this.projects.filter(project => project.badge === type);
  }

  getProjectsByLocation(location) {
    return this.projects.filter(project => 
      project.location.toLowerCase().includes(location.toLowerCase())
    );
  }

  // Generate project card HTML
  generateProjectCard(project) {
    const badgeClass = project.badge === 'free' ? 'badge-free' : 'badge-lease';
    const badgeText = project.badge === 'free' ? 'Freehold' : 'Leasehold';
    
    return `
      <div class="border rounded-xl overflow-hidden shadow hover:shadow-lg bg-white">
        <img src="${project.images.cover}" alt="${project.name} — ${project.location}"
             class="w-full h-48 object-cover" width="768" height="384" loading="lazy" decoding="async">
        <div class="p-4">
          <h3 class="text-xl font-bold mb-1">${project.name}</h3>
          <p class="text-sm text-gray-600 mb-1">${project.location}</p>
          <p class="text-sm mb-1">${project.developer || ''}</p>
          <p class="text-sm mb-1">
            ${project.type || ''} 
            ${project.distance_to_beach ? `• ${project.distance_to_beach} to beach` : ''}
            ${project.eta ? `• ETA ${project.eta}` : ''}
            <span class="badge ${badgeClass} ml-1">${badgeText}</span>
          </p>
          <div class="mt-3 flex flex-wrap gap-2">
            ${project.documents.brochure ? 
              `<a href="${project.documents.brochure}" download class="px-3 py-2 bg-gray-900 text-white rounded">Download brochure (PDF)</a>` : ''
            }
            <button class="px-3 py-2 border rounded" data-open="${project.id}" type="button">View passport</button>
          </div>
        </div>
      </div>
    `;
  }

  // Generate passport content in Acora style
  generatePassportContent(project) {
    const documents = project.documents || {};
    const uniqueFeatures = project.unique_features || {};
    const characteristics = project.characteristics || {};
    const infrastructure = project.infrastructure || [];
    const distances = project.distances || {};
    const apartments = project.apartments || [];
    
    return `
      <div data-pp class="max-w-6xl mx-auto">
        <!-- Hero Section -->
        <div class="mb-8">
          <div class="text-4xl font-bold mb-2">🔥 ${project.name}</div>
          <div class="text-xl text-gray-600 mb-4">${project.subtitle || ''}</div>
          <div class="text-lg text-gray-700 mb-6">${project.description || ''}</div>
          
          <div class="flex gap-4 mb-6">
            <button class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              Показать на карте
            </button>
            <button class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              Онлайн покупка
            </button>
          </div>
        </div>

        <!-- Image Slider -->
        ${project.images.gallery ? `
          <div class="mb-8">
            <div class="grid grid-cols-4 gap-2 mb-4">
              ${project.images.gallery.slice(0, 4).map(img => 
                `<img src="${img}" alt="" class="w-full h-32 object-cover rounded-lg cursor-pointer hover:opacity-80 transition">`
              ).join('')}
            </div>
            <div class="text-center">
              <a href="${documents.brochure || '#'}" class="text-blue-600 hover:underline">
                Посмотрите полную Презентацию объекта
              </a>
            </div>
          </div>
        ` : ''}

        <!-- Unique Features -->
        <div class="mb-8">
          <h3 class="text-2xl font-bold mb-4">Уникальные особенности объекта</h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-semibold mb-2">Расположение</h4>
              <p class="text-gray-700">${uniqueFeatures.location || ''}</p>
            </div>
            <div>
              <h4 class="font-semibold mb-2">Природа</h4>
              <p class="text-gray-700">${uniqueFeatures.nature || ''}</p>
            </div>
            <div>
              <h4 class="font-semibold mb-2">Инфраструктура</h4>
              <p class="text-gray-700">${uniqueFeatures.infrastructure || ''}</p>
            </div>
            <div>
              <h4 class="font-semibold mb-2">Престижность</h4>
              <p class="text-gray-700">${uniqueFeatures.prestige || ''}</p>
            </div>
          </div>
        </div>

        <!-- Characteristics -->
        <div class="mb-8">
          <h3 class="text-2xl font-bold mb-4">Характеристики</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            ${Object.entries(characteristics).map(([key, value]) => `
              <div class="text-center p-4 border rounded-lg">
                <div class="text-sm text-gray-600 mb-1">${key.replace('_', ' ').toUpperCase()}</div>
                <div class="font-semibold">${value}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Infrastructure -->
        <div class="mb-8">
          <h3 class="text-2xl font-bold mb-4">Инфраструктура</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            ${infrastructure.map((item, index) => `
              <div class="text-center p-3 border rounded-lg">
                <div class="text-xs text-gray-500 mb-1">${String(index + 1).padStart(2, '0')}/</div>
                <div class="text-sm font-medium">${item}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Distances -->
        <div class="mb-8">
          <h3 class="text-2xl font-bold mb-4">Расстояние до</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            ${Object.entries(distances).map(([place, time]) => `
              <div class="flex justify-between items-center p-3 border rounded-lg">
                <span class="font-medium">${place}</span>
                <span class="text-blue-600 font-semibold">${time}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Apartments -->
        ${apartments.length > 0 ? `
          <div class="mb-8">
            <h3 class="text-2xl font-bold mb-4">Виды апартаментов</h3>
            <div class="grid md:grid-cols-3 gap-6">
              ${apartments.map(apt => `
                <div class="border rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-blue-600 mb-2">${apt.size}</div>
                  <div class="text-gray-600 mb-2">${apt.bedrooms}</div>
                  <div class="text-xl font-semibold mb-4">${apt.price}</div>
                  <button class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                    Получить консультацию эксперта
                  </button>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- Documents -->
        <div class="mb-8">
          <div class="flex gap-4">
            <button class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition">
              Прайс-лист
            </button>
            <button class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              Консультация эксперта
            </button>
          </div>
        </div>
      </div>
    `;
  }
}

// Initialize database
const projectDB = new ProjectDatabase();

// Load projects when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  await projectDB.loadProjects();
  
  // Generate portfolio section dynamically
  const portfolioSection = document.getElementById('portfolio');
  if (portfolioSection) {
    const projectsGrid = portfolioSection.querySelector('.grid');
    if (projectsGrid) {
      const projects = projectDB.getAllProjects();
      projectsGrid.innerHTML = projects.map(project => 
        projectDB.generateProjectCard(project)
      ).join('');
    }
  }
});

// Update modal content when passport is opened
document.addEventListener('click', async (e) => {
  const target = e.target.closest('[data-open]');
  if (!target) return;
  
  const projectId = target.getAttribute('data-open');
  const project = projectDB.getProject(projectId);
  
  if (!project) return;
  
  const modalBody = document.getElementById('modal-body');
  if (modalBody) {
    modalBody.innerHTML = projectDB.generatePassportContent(project);
    
    // Attach gallery clicks for lightbox
    modalBody.querySelectorAll('.thumbs img').forEach((img, idx) => {
      img.addEventListener('click', () => {
        const galleryImages = [...modalBody.querySelectorAll('.thumbs img')].map(i => i.src);
        openLb(galleryImages, idx);
      });
    });
    
    // Render sparklines when opening
    renderSparklines();
    document.getElementById('modal').classList.add('open');
  }
});
