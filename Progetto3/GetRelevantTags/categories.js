// ── CATEGORY_TO_TAGS ──────────────────────────────────────────────────────────
// Mappa esatta dal Glue Job del Progetto 2 (ShiftX_Glue_Job.py)
// Usata sia per la selezione della macrocategoria che per i tag validi

const CATEGORY_TO_TAGS = {
    arts_design: ['UX design','animation','architecture','art','dance','design','fashion','film','graphic design','industrial design','media','music','painting','performance','photography','poetry','product design','social media','spoken word','storytelling','street art','theater','typography','writing'],
    business_management: ['behavioral economics','business','capitalism','career','competition','consumerism','crowdsourcing','economics','entrepreneur','finance','goals','innovation','investing','leadership','marketing','money','productivity','success','urban planning','women in business','work'],
    data_analytics: ['algorithm','artificial intelligence','cognitive science','data','machine learning','statistics','visualizations'],
    education_learning: ['Best of the Web','Humanities','Life','TED Books','TED Connects','TED Fellows','TED Membership','TED Prize','TED Residency','TED en Español','TED-Ed','TEDx','body language','books','cancel culture','culture','education','family','kids','language','library','machine learning','memory','motivation','teaching','ted health podcast','youth'],
    engineering_innovation: ['architecture','driverless cars','drones','electricity','energy','engineering','flight','industrial design','infrastructure','innovation','invention','manufacturing','nuclear energy','product design','renewable energy','robots','rocket science','solar energy','technology','transportation','urban planning','wind energy'],
    environment_sustainability: ['agriculture','animals','bees','biodiversity','biosphere','climate change','conservation','coral reefs','ecology','environment','farming','gardening','geography','glaciers','natural resources','nature','ocean','plastic','pollution','renewable energy','rivers','solar energy','sustainability','trees','water','weather','wildlife','wind energy'],
    food_agriculture: ['agriculture','bees','biology','botany','ecology','farming','food','gardening','marine biology','plants','synthetic biology','veganism','water'],
    health_medicine: ['AIDS','Surgery','Vaccines','Women Health','addiction','brain','cancer','coronavirus','disease','ebola','health','health care','heart','heart health','medical imaging','medical research','medicine','menopause','mental health','neurology','pain','pandemic','public health','reproductive health','sleep','ted health podcast','therapy','virus'],
    history_heritage: ['Africa','Asia','Egypt','Europe','Middle East','South America','United States','ancient world','anthropology','archaeology','black history','black history month','china','history','india'],
    law_justice: ['corruption','crime','government','human rights','justice system','law','policy','prison','protest','refugees','surveillance'],
    media_communication: ['TED Books','TV','body language','books','communication','interview','journalism','language','media','podcast','public speaking','social media','storytelling','ted health podcast','television','writing'],
    personal_development: ['compassion','emotions','empathy','fear','happiness','humor','identity','meditation','memory','mindfulness','motivation','personal growth','personality','potential','relationships','self','success','trust'],
    politics_policy: ['activism','behavioral economics','black history','black history month','corruption','democracy','economics','global issues','government','history','international relations','justice system','law','policy','politics','protest','race','terrorism','war'],
    psychology_therapy: ['PTSD','addiction','cognitive science','depression','mental health','personality','psychology','self','suicide','therapy'],
    science_research: ['CRISPR','DNA','archaeology','astronomy','bioethics','biology','biomimicry','bionics','biotech','chemistry','cognitive science','evolution','genetics','geology','marine biology','microbiology','neuroscience','paleontology','physics','rocket science','science','science fiction','synthetic biology'],
    geography_places: ['Antarctica','Asia','Brazil','cities','Europe','Africa','India','Middle East','South America','United States','natural disaster','public space','resources','international development','immigration','refugees','society','culture','environment','maps'],
    religion_faith: ['Buddhism','Christianity','Hinduism','Islam','Judaism','atheism','religion','spirituality','philosophy','ethics','values','beliefs','community','identity','society','inclusion','diversity','equality','human rights','justice system'],
    diversity_identity: ['LGBTQIA+','Transgender','gender','feminism','women','women in business','race','black history','black history month','disability','Autism spectrum disorder','inclusion','diversity','equality','human rights','identity','vulnerability','ageing','aging','sexual violence'],
    social_change: ['activism','cancel culture','corruption','culture','ethics','equality','human rights','inclusion','poverty','politics','policy','social change','society','sociology','terrorism','violence','war','international development','refugees','democracy'],
    culture_entertainment: ['comedy','entertainment','literature','magic','museums','creativity','friendship','future','gaming','ideas','storytelling','sound','sight','smell','toys','books','music','art','performance','film'],
    science_popular: ['Big Bang','String theory','dinosaurs','microbes','bacteria','fungi','insects','primates','astrobiology','forensics','science','biology','chemistry','physics','discovery','evolution','genetics','archaeology','natural disaster','disease'],
    technology_society: ['3D printing','computers','metaverse','nanotechnology','online privacy','gaming','math','technology','AI','Internet','code','blockchain','cyber security','virtual reality','innovation','science fiction','digital','software','robots','robotics'],
    health_society: ["Alzheimer's",'Women Health','Autism spectrum disorder','ageing','aging','blindness','disability','illness','pregnancy','parenting','sexual violence','vulnerability','sex','mental health','therapy','disease','virus','pandemic','health','medicine'],
    space_astronomy: ['Mars','Moon','NASA','Planets','Sun','aliens','asteroid','astronomy','dark matter','public space','rocket science','solar system','space','telescopes','universe'],
    sports_fitness: ['athletics','competition','exercise','human body','motivation','performance','soccer','sports'],
    technology_ai: ['AI','Internet','NFTs','algorithm','artificial intelligence','augmented reality','blockchain','code','cryptocurrency','cyber security','data','encryption','machine learning','quantum','software','tech','technology','virtual reality'],
    transportation_travel: ['exploration','flight','geography','maps','ocean','public space','rocket science','transportation','travel'],
};

const CATEGORY_ORDER = [
    'technology_ai','data_analytics','science_research','science_popular',
    'health_medicine','health_society','environment_sustainability',
    'business_management','education_learning','arts_design','geography_places',
    'religion_faith','diversity_identity','social_change','culture_entertainment',
    'technology_society','personal_development','politics_policy','psychology_therapy',
    'engineering_innovation','transportation_travel','space_astronomy',
    'food_agriculture','history_heritage','law_justice','media_communication','sports_fitness',
];

const VALID_CATEGORIES = CATEGORY_ORDER;

module.exports = { CATEGORY_TO_TAGS, VALID_CATEGORIES };
