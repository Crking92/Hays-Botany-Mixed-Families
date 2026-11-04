#!/usr/bin/env python3
"""Publish two exact-hash archived, photographer-released Oxalis drummondii photographs.

Rights evidence: https://www.backyardnature.net/j/copyrite.htm
Source page: https://www.backyardnature.net/n/h/drumm-ox.htm
No new downloads, archive rewriting, or unsupported license expansions.
"""
import hashlib,json
from pathlib import Path

source_root=Path(__import__("sys").argv[1])
site=Path("site")
slug="oxalis-drummondii"
speciespath=site/"data/species"/(slug+".json")
collectionpath=site/"data/collection-index.json"
gallerypath=site/"data/gallery-index.json"
card=json.loads(speciespath.read_text())
collection=json.loads(collectionpath.read_text())
gallery=json.loads(gallerypath.read_text())
indexed={x["id"]:x for x in collection["entries"]}
assert card["scientific_name"]=="Oxalis drummondii"
assert gallery["entries"][slug]["count"]==indexed[slug]["photo_count"]==len(card["verified_photos"])
assert sum(x["photo_count"] for x in collection["entries"])==gallery["photo_count"]
assert all(gallery["entries"][id]["count"]==x["photo_count"] for id,x in indexed.items())
base=source_root/"migration/private-original-photo-holds/Oxalidaceae/Oxalis/oxalis-drummondii/images"
photos=[
("oxalis-drummondii-conrad-uvalde-flower-leaves.jpg","88ee3545e9f4f67124fcf81e66d08df52219e7ef","Flowering plant with trifoliate leaves and pink blossoms"),
("oxalis-drummondii-conrad-uvalde-flower-side.jpg","261ca068abf940c068e260e172f17657ec7660ee","Flower side view showing pale green tube and pink corolla"),
]
def sha(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
added=0
for filename,expected_sha,role in photos:
    file=base/filename
    raw=file.read_bytes()
    assert sha(raw)==expected_sha and raw.startswith(b"\xff\xd8\xff"),filename
    if any(p.get("source_blob_sha")==expected_sha for p in card["verified_photos"]):
        print("ALREADY_IN_GALLERY",filename)
        continue
    dst="media/"+slug+"/conrad-public-domain-"+expected_sha[:16]+".jpg"
    if (site/dst).exists():raise RuntimeError("Dest already exists without gallery record "+dst)
    (site/dst).parent.mkdir(parents=True,exist_ok=True)
    (site/dst).write_bytes(raw)
    card["verified_photos"].append({
        "src":dst,
        "creator":"Jim Conrad",
        "source_page":"https://www.backyardnature.net/n/h/drumm-ox.htm",
        "source_page_is_exact":True,
        "license":"Public Domain (photographer dedication)",
        "license_url":"https://www.backyardnature.net/j/copyrite.htm",
        "source_blob_sha":expected_sha,
        "role":role,
        "modified":"Original archived photograph, no new modifications",
        "noncommercial_only":False,
        "private_rights_review_only":False,
        "photo_approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY",
        "photo_approved_by":"Exact archived original and named Jim Conrad photo-domain dedication verified 2026-11-04",
        "source_review_evidence":"Jim Conrad personally photographed the Oxalis drummondii specimen shown on source page; https://www.backyardnature.net/j/copyrite.htm dedicates his own photos to public domain. Original archived Git image SHA "+expected_sha,
        "taxon_review_evidence":"Jim Conrad's photo-specific 2013 field report explicitly identifies Oxalis drummondii in northern Uvalde County, TX. Basic image recognition checked."
    })
    added+=1
    print("PHOTOGRAPH_INSTALLED",dst,expected_sha)
if added:
    indexed[slug]["photo_count"]+=added
    gallery["entries"][slug]["count"]+=added
    gallery["photo_count"]+=added
    speciespath.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
    collectionpath.write_text(json.dumps(collection,indent=2,ensure_ascii=False)+"\n")
    gallerypath.write_text(json.dumps(gallery,indent=2,ensure_ascii=False)+"\n")
assert gallery["entries"][slug]["count"]==indexed[slug]["photo_count"]==len(card["verified_photos"])
assert sum(x["photo_count"] for x in collection["entries"])==gallery["photo_count"]
print("OXALIS_PUBLIC_DOMAIN_BATCH",json.dumps({"installed":added,"gallery":gallery["photo_count"],"species":slug}))
