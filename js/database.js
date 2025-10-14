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

  // Generate passport content
  generatePassportContent(project) {
    const kpis = project.kpis || {};
    const features = project.features || [];
    const documents = project.documents || {};
    
    return `
      <div data-pp>
        <div class="pp-grid mb-4">
          <img src="${project.images.cover}" class="w-full h-64 object-cover rounded-xl" 
               alt="${project.name}" loading="lazy" decoding="async" width="1024" height="512">
          <div>
            <h4 class="text-xl font-semibold mb-1">${project.name} — ${project.location}</h4>
            <div class="text-sm text-gray-600 mb-3">
              ${project.units || ''} 
              ${project.distance_to_beach ? `• ${project.distance_to_beach} to beach` : ''}
              ${project.eta ? `• ETA ${project.eta}` : ''}
              <span class="badge badge-${project.badge} ml-2">${project.badge === 'free' ? 'Freehold' : 'Leasehold'}</span>
            </div>
            ${Object.keys(kpis).length > 0 ? `
              <div class="pp-kpi mb-3">
                ${kpis.roi ? `<div class="k"><div class="v">${kpis.roi}</div><div class="t text-xs text-gray-500">ROI (model)</div></div>` : ''}
                ${kpis.liquidity ? `<div class="k"><div class="v">${kpis.liquidity}</div><div class="t text-xs text-gray-500">Liquidity</div></div>` : ''}
                ${kpis.irr ? `<div class="k"><div class="v">${kpis.irr}</div><div class="t text-xs text-gray-500">IRR (base)</div></div>` : ''}
                ${kpis.gidr_score ? `<div class="k"><div class="v">${kpis.gidr_score}</div><div class="t text-xs text-gray-500">GIDR Score</div></div>` : ''}
              </div>
            ` : ''}
            ${features.length > 0 ? `
              <div class="grid sm:grid-cols-2 gap-3 mt-2 text-sm">
                ${features.map(feature => `<div class="flex items-center gap-2"><span>${feature}</span></div>`).join('')}
              </div>
            ` : ''}
            <div class="flex flex-wrap gap-2 mt-3">
              ${documents.brochure ? `<a href="${documents.brochure}" download class="px-3 py-2 bg-gray-900 text-white rounded">Download brochure (PDF)</a>` : ''}
              ${documents.pricelist ? `<a href="${documents.pricelist}" class="pp-doc">Price list & payment schedule (PDF)</a>` : ''}
              ${documents.rental ? `<a href="${documents.rental}" class="pp-doc">Rental program (PDF)</a>` : ''}
            </div>
          </div>
        </div>

        ${project.images.gallery ? `
          <div class="thumbs mb-3">
            ${project.images.gallery.map(img => 
              `<img src="${img}" alt="" loading="lazy" decoding="async">`
            ).join('')}
          </div>
        ` : ''}

        <div class="pp-tabs flex gap-4 border-b mb-3">
          <button class="active" onclick="ppTab('overview', this)" type="button">Overview</button>
          <button onclick="ppTab('financials', this)" type="button">Financials</button>
          <button onclick="ppTab('map', this)" type="button">Map</button>
          <button onclick="ppTab('docs', this)" type="button">Documents</button>
        </div>

        <div data-pp-tab="overview">
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <div class="space-y-2">
              ${project.overview ? Object.entries(project.overview).map(([key, value]) => 
                `<div><strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${value}</div>`
              ).join('') : ''}
            </div>
            <div class="space-y-2">
              ${project.overview?.forecast ? `<div><strong>GIDR Forecast:</strong> ${project.overview.forecast}</div>` : ''}
              ${project.overview?.risks ? `<div><strong>Risks:</strong> ${project.overview.risks}</div>` : ''}
            </div>
          </div>
        </div>

        <div class="hidden" data-pp-tab="financials">
          <div class="grid md:grid-cols-2 gap-4 text-sm">
            <div class="space-y-2">
              ${project.financials ? Object.entries(project.financials).map(([key, value]) => 
                `<div><strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${value}</div>`
              ).join('') : ''}
            </div>
            <div class="space-y-2">
              ${documents.pricelist ? `<a href="${documents.pricelist}" class="pp-doc">Price list & payment schedule (PDF)</a>` : ''}
              ${documents.rental ? `<a href="${documents.rental}" class="pp-doc">Rental program (PDF)</a>` : ''}
            </div>
          </div>
        </div>

        <div class="hidden" data-pp-tab="map">
          <div class="rounded-xl overflow-hidden border">
            <iframe title="Map" src="https://www.openstreetmap.org/export/embed.html?bbox=98.27,7.96,98.33,8.03&layer=mapnik" class="w-full" style="height:300px"></iframe>
          </div>
        </div>

        <div class="hidden" data-pp-tab="docs">
          <div class="grid md:grid-cols-2 gap-3 text-sm">
            ${documents.brochure ? `<a href="${documents.brochure}" class="pp-doc">Developer brochure (PDF)</a>` : ''}
            ${documents.legal ? `<a href="${documents.legal}" class="pp-doc">Legal brief (tenure/quota) (PDF)</a>` : ''}
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
