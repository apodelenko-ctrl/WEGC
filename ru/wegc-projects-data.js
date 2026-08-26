/* ── Общий датасет проектов для калькуляторов wegc.fund.
      Цены «от» и площади стартовых юнитов взяты из паспортов /projects/*.html.
      Не менять цифры без сверки с паспортами. ── */
window.WEGC_FX={THB_RUB:2.5,label:'ориентировочно'};

/* Ориентировочные рыночные ставки годовой аренды по районам, ฿/м² в месяц.
   Это рыночный ориентир для первого прикидочного расчёта, не обязательство WEGC. */
window.WEGC_RENT_PSM={
  'Банг Тао':800,'Сурин':950,'Камала':800,'Най Янг':620,
  'Ката · Карон':800,'Раваи':700,'Ко Кео':420
};

window.WEGC_YIELD_PROJECTS=[
 {slug:'the-title-sierra',   name:'The Title Sierra',      district:'Банг Тао',   kind:'condo', url:'/projects/the-title-sierra.html',    price:2870000,  area:28,  delivery:'3 кв. 2028', struct:'Freehold / Leasehold', lease:'both'},
 {slug:'title-vivi',         name:'The Title Vivi',        district:'Банг Тао',   kind:'condo', url:'/projects/title-vivi.html',          price:3160000,  area:27,  delivery:'4 кв. 2027', struct:'Leasehold',            lease:'leasehold'},
 {slug:'the-title-artrio',   name:'The Title Artrio',      district:'Банг Тао',   kind:'condo', url:'/projects/the-title-artrio.html',    price:4260000,  area:28,  delivery:'2026',       struct:'Leasehold',            lease:'leasehold'},
 {slug:'the-modeva',         name:'The Modeva',            district:'Банг Тао',   kind:'condo', url:'/projects/the-modeva.html',          price:4780000,  area:41,  delivery:'1 кв. 2027', struct:'Leasehold',            lease:'leasehold'},
 {slug:'the-title-vivana',   name:'The Title Vivana',      district:'Камала',     kind:'condo', url:'/projects/the-title-vivana.html',    price:3620000,  area:30,  delivery:'4 кв. 2028', struct:'Freehold / Leasehold', lease:'both'},
 {slug:'the-title-biancana', name:'The Title Biancana',    district:'Сурин',      kind:'condo', url:'/projects/the-title-biancana.html',  price:6300000,  area:31,  delivery:'4 кв. 2028', struct:'Leasehold',            lease:'leasehold'},
 {slug:'the-title-balcony',  name:'The Title Balcony',     district:'Най Янг',    kind:'condo', url:'/projects/the-title-balcony.html',   price:5240000,  area:33,  delivery:'4 кв. 2027', struct:'Leasehold',            lease:'leasehold'},
 {slug:'the-olive',          name:'The Olive',             district:'Най Янг',    kind:'condo', url:'/projects/the-olive.html',           price:4990000,  area:32,  delivery:'окт. 2028',  struct:'Freehold / Leasehold', lease:'both'},
 {slug:'the-title-katabello',name:'The Title Katabello',   district:'Ката · Карон',kind:'condo',url:'/projects/the-title-katabello.html', price:3830000,  area:28,  delivery:'3 кв. 2027', struct:'Leasehold',            lease:'leasehold'},
 {slug:'the-title-adora',    name:'The Title Adora',       district:'Раваи',      kind:'condo', url:'/projects/the-title-adora.html',     price:4200000,  area:32,  delivery:'1 кв. 2027', struct:'Leasehold',            lease:'leasehold'},
 {slug:'casa-de-monte',      name:'Casa de Monte · виллы', district:'Ко Кео',     kind:'villa', url:'/projects/casa-de-monte.html',       price:28200000, area:297, delivery:'июль 2029',  struct:'Leasehold / Freehold', lease:'both'}
];

/* Дефолты расходов по типу объекта */
window.WEGC_KIND_DEFAULTS={
  condo:{sink:600,furn:8000,maint:60,other:60000},
  villa:{sink:400,furn:6000,maint:30,other:120000}
};
