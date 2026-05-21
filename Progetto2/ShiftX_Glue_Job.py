###### SHIFT-X Vero — Glue ETL Job
###### Progetto 2: Watch Next + Best Category singola
###### Basato su ShiftX-Glue-Job.py con CATEGORY_TO_TAGS aggiornato ai tag reali del dataset

import sys
from pyspark.sql.functions import col, collect_list, collect_set, first, regexp_replace, struct, size, udf
from pyspark.sql.types import ArrayType, StringType

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# ═══════════════════════════════════════════════════════════════════════════════
# 1. INIT — Inizializzazione del job
# ═══════════════════════════════════════════════════════════════════════════════

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Percorsi S3 — Data Lake
S3_BUCKET = "s3://shiftx-data-2026"

tedx_dataset_path     = f"{S3_BUCKET}/final_list.csv"
details_dataset_path  = f"{S3_BUCKET}/details.csv"
tags_dataset_path     = f"{S3_BUCKET}/tags.csv"
images_dataset_path   = f"{S3_BUCKET}/images.csv"
related_dataset_path  = f"{S3_BUCKET}/related_videos.csv"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LETTURA CSV — Caricamento dei dataset dal Data Lake S3
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 2] Lettura CSV da S3...")

# --- final_list.csv (tabella principale dei talk) ---
tedx_dataset = spark.read \
    .option("header", "true") \
    .option("quote", '"') \
    .option("escape", '"') \
    .csv(tedx_dataset_path)

tedx_dataset.printSchema()

count_items = tedx_dataset.count()
count_items_not_null = tedx_dataset.filter("id is not null").count()
print(f">>> Totale talk RAW: {count_items}")
print(f">>> Talk con ID NOT NULL: {count_items_not_null}")

# Filtra record senza ID
tedx_dataset = tedx_dataset.filter("id is not null")

# --- details.csv (descrizione, durata, data pubblicazione) ---
details_dataset = spark.read \
    .option("header", "true") \
    .option("quote", '"') \
    .option("escape", '"') \
    .option("multiLine", "true") \
    .csv(details_dataset_path)

# --- tags.csv (tag associati a ogni talk) ---
tags_dataset = spark.read \
    .option("header", "true") \
    .csv(tags_dataset_path)

# --- images.csv (URL immagini per ogni talk) ---
images_dataset = spark.read \
    .option("header", "true") \
    .csv(images_dataset_path)

# --- related_videos.csv (watch next / video correlati) ---
related_dataset = spark.read \
    .option("header", "true") \
    .option("quote", '"') \
    .option("escape", '"') \
    .csv(related_dataset_path)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PULIZIA DATI
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 3] Pulizia dati...")

details_dataset = details_dataset.withColumn(
    "description",
    regexp_replace(col("description"), r"[\n\r\t]", " ")
)

details_dataset = details_dataset.select(
    col("id").alias("id_ref"),
    col("description"),
    col("duration"),
    col("publishedAt")
)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. JOIN — Costruzione del dataset principale
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 4] Join dei dataset...")

tedx_dataset_main = tedx_dataset.join(
    details_dataset,
    tedx_dataset.id == details_dataset.id_ref,
    "left"
).drop("id_ref")

tedx_dataset_main.printSchema()

images_first = images_dataset \
    .withColumnRenamed("url", "image_url") \
    .groupBy("id") \
    .agg(first("image_url").alias("image_url"))

tedx_dataset_main = tedx_dataset_main.join(
    images_first,
    on="id",
    how="left"
)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. TAGS — Aggregazione tag per talk
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 5] Aggregazione tags...")

tags_dataset_agg = tags_dataset \
    .groupBy(col("id").alias("id_ref")) \
    .agg(collect_set("tag").alias("tags"))

tags_dataset_agg.printSchema()

tedx_dataset_main = tedx_dataset_main.join(
    tags_dataset_agg,
    tedx_dataset_main.id == tags_dataset_agg.id_ref,
    "left"
).drop("id_ref")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. WATCH NEXT — Risoluzione e aggregazione video correlati
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 6] Risoluzione Watch Next...")

slug_lookup = tedx_dataset.select(
    col("slug").alias("lookup_slug"),
    col("id").alias("correct_id")
)

related_resolved = related_dataset.join(
    slug_lookup,
    related_dataset.slug == slug_lookup.lookup_slug,
    "inner"
).select(
    related_dataset.id.alias("parent_id"),
    col("correct_id").alias("related_talk_id"),
    related_dataset.slug.alias("related_slug"),
    related_dataset.title.alias("related_title"),
    related_dataset.presenterDisplayName.alias("related_speaker"),
    related_dataset.duration.alias("related_duration")
)

original_count = related_dataset.count()
valid_count = related_resolved.count()
print(f">>> Related videos originali: {original_count}")
print(f">>> Related videos validi (dopo lookup): {valid_count}")
print(f">>> Related videos scartati: {original_count - valid_count}")

related_videos_dataset_agg = related_resolved.groupBy(col("parent_id").alias("id_ref")).agg(
    collect_list(
        struct(
            col("related_talk_id").alias("id"),
            col("related_slug").alias("slug"),
            col("related_title").alias("title"),
            col("related_speaker").alias("speaker"),
            col("related_duration").alias("duration")
        )
    ).alias("related_videos")
)

related_videos_dataset_agg.printSchema()


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CATEGORY_TO_TAGS — Mapping basato su tag reali del dataset
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_TO_TAGS = {
    'arts_design': ['UX design','animation','architecture','art','dance','design','fashion','film','graphic design','industrial design','media','music','painting','performance','photography','poetry','product design','social media','spoken word','storytelling','street art','theater','typography','writing'],
    'business_management': ['behavioral economics','business','capitalism','career','competition','consumerism','crowdsourcing','economics','entrepreneur','finance','goals','innovation','investing','leadership','marketing','money','productivity','success','urban planning','women in business','work'],
    'data_analytics': ['algorithm','artificial intelligence','cognitive science','data','machine learning','statistics','visualizations'],
    'education_learning': ['Best of the Web','Humanities','Life','TED Books','TED Connects','TED Fellows','TED Membership','TED Prize','TED Residency','TED en Español','TED-Ed','TEDx','body language','books','cancel culture','culture','education','family','kids','language','library','machine learning','memory','motivation','teaching','ted health podcast','youth'],
    'engineering_innovation': ['architecture','driverless cars','drones','electricity','energy','engineering','flight','industrial design','infrastructure','innovation','invention','manufacturing','nuclear energy','product design','renewable energy','robots','rocket science','solar energy','technology','transportation','urban planning','wind energy'],
    'environment_sustainability': ['agriculture','animals','bees','biodiversity','biosphere','climate change','conservation','coral reefs','ecology','environment','farming','gardening','geography','glaciers','natural resources','nature','ocean','plastic','pollution','renewable energy','rivers','solar energy','sustainability','trees','water','weather','wildlife','wind energy'],
    'food_agriculture': ['agriculture','bees','biology','botany','ecology','farming','food','gardening','marine biology','plants','synthetic biology','veganism','water'],
    'health_medicine': ['AIDS','Surgery','Vaccines','Women Health','addiction','brain','cancer','coronavirus','disease','ebola','health','health care','heart','heart health','medical imaging','medical research','medicine','menopause','mental health','neurology','pain','pandemic','public health','reproductive health','sleep','ted health podcast','therapy','virus'],
    'history_heritage': ['Africa','Asia','Egypt','Europe','Middle East','South America','United States','ancient world','anthropology','archaeology','black history','black history month','china','history','india'],
    'law_justice': ['corruption','crime','government','human rights','justice system','law','policy','prison','protest','refugees','surveillance'],
    'media_communication': ['TED Books','TV','body language','books','communication','interview','journalism','language','media','podcast','public speaking','social media','storytelling','ted health podcast','television','writing'],
    'personal_development': ['compassion','emotions','empathy','fear','happiness','humor','identity','meditation','memory','mindfulness','motivation','personal growth','personality','potential','relationships','self','success','trust'],
    'politics_policy': ['activism','behavioral economics','black history','black history month','corruption','democracy','economics','global issues','government','history','international relations','justice system','law','policy','politics','protest','race','terrorism','war'],
    'psychology_therapy': ['PTSD','addiction','cognitive science','depression','mental health','personality','psychology','self','suicide','therapy'],
    'science_research': ['CRISPR','DNA','archaeology','astronomy','bioethics','biology','biomimicry','bionics','biotech','chemistry','cognitive science','evolution','genetics','geology','marine biology','microbiology','neuroscience','paleontology','physics','rocket science','science','science fiction','synthetic biology'],
    'geography_places': ['Antarctica','Asia','Brazil','cities','Europe','Africa','India','Middle East','South America','United States','natural disaster','public space','resources','international development','immigration','refugees','society','culture','environment','maps'],
    'religion_faith': ['Buddhism','Christianity','Hinduism','Islam','Judaism','atheism','religion','spirituality','philosophy','ethics','values','beliefs','community','identity','society','inclusion','diversity','equality','human rights','justice system'],
    'diversity_identity': ['LGBTQIA+','Transgender','gender','feminism','women','women in business','race','black history','black history month','disability','Autism spectrum disorder','inclusion','diversity','equality','human rights','identity','vulnerability','ageing','aging','sexual violence'],
    'social_change': ['activism','cancel culture','corruption','culture','ethics','equality','human rights','inclusion','poverty','politics','policy','social change','society','sociology','terrorism','violence','war','international development','refugees','democracy'],
    'culture_entertainment': ['comedy','entertainment','literature','magic','museums','creativity','friendship','future','gaming','ideas','storytelling','sound','sight','smell','toys','books','music','art','performance','film'],
    'science_popular': ['Big Bang','String theory','dinosaurs','microbes','bacteria','fungi','insects','primates','astrobiology','forensics','science','biology','chemistry','physics','discovery','evolution','genetics','archaeology','natural disaster','disease'],
    'technology_society': ['3D printing','computers','metaverse','nanotechnology','online privacy','gaming','math','technology','AI','Internet','code','blockchain','cyber security','virtual reality','innovation','science fiction','digital','software','robots','robotics'],
    'health_society': ['Alzheimer\'s', 'Women Health', 'Autism spectrum disorder', 'ageing', 'aging', 'blindness', 'disability', 'illness', 'pregnancy', 'parenting', 'sexual violence', 'vulnerability', 'sex', 'mental health', 'therapy', 'disease', 'virus', 'pandemic', 'health', 'medicine'],
    'space_astronomy': ['Mars','Moon','NASA','Planets','Sun','aliens','asteroid','astronomy','dark matter','public space','rocket science','solar system','space','telescopes','universe'],
    'sports_fitness': ['athletics','competition','exercise','human body','motivation','performance','soccer','sports'],
    'technology_ai': ['AI','Internet','NFTs','algorithm','artificial intelligence','augmented reality','blockchain','code','cryptocurrency','cyber security','data','encryption','machine learning','quantum','software','tech','technology','virtual reality'],
    'transportation_travel': ['exploration','flight','geography','maps','ocean','public space','rocket science','transportation','travel'],
}

CATEGORY_ORDER = [
    'technology_ai','data_analytics','science_research','science_popular','health_medicine','health_society','environment_sustainability','business_management','education_learning','arts_design','geography_places','religion_faith','diversity_identity','social_change','culture_entertainment','technology_society','personal_development','politics_policy','psychology_therapy','engineering_innovation','transportation_travel','space_astronomy','food_agriculture','history_heritage','law_justice','media_communication','sports_fitness',
]

CATEGORY_TO_TAGS_LOWER = {cat: set(tag.lower() for tag in tags) for cat, tags in CATEGORY_TO_TAGS.items()}


def choose_best_category(tags_list):
    if not tags_list:
        return "uncategorized"
    tags_lower = [t.lower().strip() for t in tags_list if t]
    best_category = "uncategorized"
    best_score = 0
    for idx, category in enumerate(CATEGORY_ORDER):
        score = sum(1 for tag in tags_lower if tag in CATEGORY_TO_TAGS_LOWER[category])
        if score > best_score or (score == best_score and best_category == "uncategorized"):
            best_score = score
            best_category = category
    return best_category if best_score > 0 else "uncategorized"

best_category_udf = udf(choose_best_category, StringType())


# ═══════════════════════════════════════════════════════════════════════════════
# 8. SELEZIONE FINALE — Preparazione del documento MongoDB
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 8] Preparazione documento finale...")

tedx_dataset_final = tedx_dataset_main \
    .join(related_videos_dataset_agg, tedx_dataset_main.id == related_videos_dataset_agg.id_ref, "left").drop("id_ref") \
    .withColumn("best_category", best_category_udf(col("tags"))) \
    .select(
        col("id").alias("_id"),
        col("slug"),
        col("title"),
        col("speakers"),
        col("url"),
        col("description"),
        col("duration"),
        col("publishedAt"),
        col("image_url"),
        col("tags"),
        col("best_category"),
        col("related_videos"),
    )

tedx_dataset_final.printSchema()

total_talks = tedx_dataset_final.count()
with_related = tedx_dataset_final.filter(size(col("related_videos")) > 0).count()
print(f">>> Talk totali: {total_talks}")
print(f">>> Talk con related_videos: {with_related}")
print(f">>> Talk senza related_videos: {total_talks - with_related}")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. SCRITTURA SU MONGODB ATLAS
# ═══════════════════════════════════════════════════════════════════════════════

print(">>> [Step 9] Scrittura su MongoDB Atlas...")

mongo_options = {
    "connectionName": "TEDX",
    "database": "unibg_tedx_2026",
    "collection": "tedx_data",
}

tedx_dynamic_frame = DynamicFrame.fromDF(tedx_dataset_final, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(
    tedx_dynamic_frame,
    connection_type="mongodb",
    connection_options=mongo_options
)

print("Job completato con successo!")
job.commit()
