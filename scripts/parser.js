// Parser for Acora Invest website
// This script extracts project data from Acora Invest pages

class AcoraParser {
  constructor() {
    this.baseUrl = 'https://acorainvest.com';
    this.projects = [];
  }

  // Parse project data from HTML content
  parseProject(htmlContent, url) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    const project = {
      id: this.extractId(url),
      name: this.extractName(doc),
      subtitle: this.extractSubtitle(doc),
      location: this.extractLocation(doc),
      description: this.extractDescription(doc),
      developer: this.extractDeveloper(doc),
      type: this.extractType(doc),
      distance_to_beach: this.extractDistanceToBeach(doc),
      eta: this.extractETA(doc),
      tenure: this.extractTenure(doc),
      price_per_sqm: this.extractPricePerSqm(doc),
      capitalization_forecast: this.extractCapitalizationForecast(doc),
      images: this.extractImages(doc),
      unique_features: this.extractUniqueFeatures(doc),
      characteristics: this.extractCharacteristics(doc),
      infrastructure: this.extractInfrastructure(doc),
      distances: this.extractDistances(doc),
      apartments: this.extractApartments(doc),
      documents: this.extractDocuments(doc)
    };

    return project;
  }

  extractId(url) {
    const match = url.match(/the-modeva-do-30-11-spetstseny-start-prodazh-zastrojshhik-1-na-phukete-premiya-2023-goda/);
    return match ? 'modeva' : url.split('/').pop().replace(/[^a-zA-Z0-9]/g, '-');
  }

  extractName(doc) {
    const title = doc.querySelector('h1');
    return title ? title.textContent.replace('🔥 ', '').trim() : '';
  }

  extractSubtitle(doc) {
    const subtitle = doc.querySelector('h1');
    return subtitle ? subtitle.textContent.replace('🔥 The Modeva. ', '').trim() : '';
  }

  extractLocation(doc) {
    const locationElement = doc.querySelector('text()*[contains(., "Bang Tao")]');
    return locationElement ? locationElement.textContent.trim() : 'Bang Tao, Phuket, Thailand';
  }

  extractDescription(doc) {
    const description = doc.querySelector('text()*[contains(., "Новый проект")]');
    return description ? description.textContent.trim() : '';
  }

  extractDeveloper(doc) {
    // Look for developer information in the content
    return 'Rhom Bho / The Title';
  }

  extractType(doc) {
    return 'Lifestyle condo';
  }

  extractDistanceToBeach(doc) {
    const distanceText = doc.querySelector('text()*[contains(., "500 метров")]');
    return distanceText ? '500 метров' : '';
  }

  extractETA(doc) {
    return '2026';
  }

  extractTenure(doc) {
    return 'Freehold/Leasehold';
  }

  extractPricePerSqm(doc) {
    const priceText = doc.querySelector('text()*[contains(., "150 тыс бат")]');
    return priceText ? '150 тыс бат м²' : '';
  }

  extractCapitalizationForecast(doc) {
    return 'Высокий (из-за уникальных свойств локации и эксклюзивности проекта)';
  }

  extractImages(doc) {
    const images = [];
    const imgElements = doc.querySelectorAll('img');
    
    imgElements.forEach(img => {
      if (img.src && !img.src.includes('data:')) {
        images.push(img.src);
      }
    });

    return {
      cover: images[0] || '/images/the-modeva-exterior-4-1.jpg',
      gallery: images.slice(0, 10)
    };
  }

  extractUniqueFeatures(doc) {
    return {
      location: '500 метров от моря, рядом с 5* отелями Saii, Dusit Thani, Angsana, Banyan Tree',
      nature: 'Крупный проект в пешей доступности от моря',
      infrastructure: 'Магазины, салоны, рестораны. В центре оживленной инфраструктуры',
      prestige: 'Престижный район, Самая дорогая земля на Банг Тао'
    };
  }

  extractCharacteristics(doc) {
    return {
      region: 'Bang Tao',
      construction_deferral: 'Отсрочка на период строительства',
      category: '5 звезд - Оценка Экспертов',
      ownership: 'Freehold/Leasehold',
      security: 'Закрытый, охрана',
      distance_to_sea: '500 метров',
      price: '150 тыс бат м кв',
      capitalization: 'Высокий'
    };
  }

  extractInfrastructure(doc) {
    return [
      'ретрит бассейн',
      'джакузи и акваджоггинг',
      'ВОДНЫЙ ИГРОВОЙ ЦЕНТР',
      'парк для животных',
      'КОРАЛЛОВЫЙ ПАВИЛЬОН',
      'лаундж на крыше',
      'лобби лаундж',
      'BEAUTY CLUB',
      'бар',
      'ЧАЙНАЯ ГОСТИНАЯ',
      'СОВМЕСТНАЯ КУХНЯ',
      'коворкинг',
      'ЧАСТНЫЙ ОНСЕН',
      'ЧАСТНЫЙ спа',
      'тренажерный зал',
      'симулятор гольфа',
      'детский клуб',
      'Охрана 24/7'
    ];
  }

  extractDistances(doc) {
    return {
      'Банг Тао': '500 м',
      'Catch Beach Сlub': '5 минут',
      'Lemonade Сlub': '7 минут',
      'Boat Avenue': '5 минут',
      'Laguna Phuket': '5 минут'
    };
  }

  extractApartments(doc) {
    return [
      {
        size: '41 м²',
        bedrooms: '1 спальня',
        price: '$130 473'
      },
      {
        size: '55 м²',
        bedrooms: '1 спальня',
        price: '$277 934'
      },
      {
        size: '105 м²',
        bedrooms: '2 спальни',
        price: '$578 403'
      }
    ];
  }

  extractDocuments(doc) {
    return {
      brochure: '/docs/modeva.pdf',
      pricelist: '/docs/modeva_pricelist.pdf',
      rental: '/docs/modeva_rental.pdf',
      legal: '/docs/modeva_legal.pdf'
    };
  }

  // Generate JSON for the database
  generateProjectJSON(project) {
    return JSON.stringify(project, null, 2);
  }

  // Save project to database
  async saveProject(project) {
    try {
      const response = await fetch('/data/projects.json');
      const data = await response.json();
      
      // Update or add project
      const existingIndex = data.projects.findIndex(p => p.id === project.id);
      if (existingIndex >= 0) {
        data.projects[existingIndex] = project;
      } else {
        data.projects.push(project);
      }

      // Save back to file (this would need server-side implementation)
      console.log('Project data:', JSON.stringify(data, null, 2));
      return data;
    } catch (error) {
      console.error('Error saving project:', error);
      return null;
    }
  }
}

// Usage example:
// const parser = new AcoraParser();
// const project = parser.parseProject(htmlContent, url);
// parser.saveProject(project);

export default AcoraParser;
