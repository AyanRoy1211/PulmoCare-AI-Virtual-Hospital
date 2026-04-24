from ingestion.pubmed_ingest import ingest_pubmed
from ingestion.openfda_ingest import ingest_openfda
from ingestion.medlineplus_ingest import ingest_medlineplus
from ingestion.who_guidelines_ingest import ingest_local_pdfs

steps = [
    ("MedlinePlus — Diseases & Conditions", ingest_medlineplus),
    ("OpenFDA — Drug Knowledge",            ingest_openfda),
    ("PubMed — Research Evidence",          ingest_pubmed),
    ("WHO Guidelines — Clinical Protocols", ingest_local_pdfs),
]

for name, fn in steps:
    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    fn()

print("\n🏥 All knowledge bases ready. You can now run app.py.")