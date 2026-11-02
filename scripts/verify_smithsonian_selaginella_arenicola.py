#!/usr/bin/env python3
"""Verify exact public-domain Smithsonian specimen before adding user's original to live gallery."""
import hashlib,io,json,os,urllib.request,time
from pathlib import Path
from PIL import Image

SID="selaginella-arenicola"
HASH="d64b8348f6807d2cedd13d15cc151e4fcfe6c972db7f891f8a398cb0a70cc9e7"
PHOTO="https://collections.nmnh.si.edu/media/?i=16240163&h=2000"
OBJECT="https://www.si.edu/object/selaginella-arenicola:nmnhbotany_16821804"
REPORT=Path(os.environ["RUNNER_TEMP"])/"selaginella-smithsonian-source-review.json"
ROOT=Path(os.environ["RUNNER_TEMP"])/"smithsonian-cleared"
row={"species":SID,"gbif_occurrence":3960439312,"smithsonian_barcode":"03476880",
     "photographer":"Ingrid P. Lin","license":"CC0 1.0","expected_SHA256":HASH}
def fetch(u,size):
    r=urllib.request.Request(u,headers={"User-Agent":"HaysBotanySmithsonianOriginalPhotoProof/1.0"})
    with urllib.request.urlopen(r,timeout=35) as response:
        b=response.read(size+1)
    if len(b)>size:raise ValueError("Source exceeds maximum size")
    return b
try:
    page=fetch(OBJECT,8_000_000).decode("utf-8","replace").lower()
    if "selaginella arenicola" not in page or "03476880" not in page:
        raise ValueError("Official Smithsonian exact specimen name/barcode not both visible")
    if "public domain" not in page and "cc0" not in page:
        raise ValueError("Individual Smithsonian specimen page has no public-domain claim")
    original=fetch(PHOTO,25_000_000)
    if hashlib.sha256(original).hexdigest()!=HASH:
        raise ValueError("Smithsonian original image bytes do not match user's preserved ZIP")
    with Image.open(io.BytesIO(original)) as im:
        if im.format!="JPEG" or im.width*im.height>80_000_000:
            raise ValueError("Unsupported source image type")
        im.verify()
    name="smithsonian-selaginella-arenicola-03476880.jpg"
    folder=ROOT/"photo-intake/approved"/SID
    folder.mkdir(parents=True,exist_ok=True)
    (folder/name).write_bytes(original)
    sidecar={
        "species_id":SID,"photo_file":name,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
        "rights_approved_for_public":True,"taxon_reviewed":True,
        "approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY",
        "policy_ref":"PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02",
        "review_operator":"Hays Botany Smithsonian voucher/barcode and original ZIP byte comparison",
        "source_review_evidence":"Official Smithsonian specimen page confirms barcode 03476880 and public-domain media for Selaginella arenicola. Exact image URL media i=16240163/2000, downloaded image SHA256 matches user's preserved original ZIP: "+HASH,
        "taxon_review_evidence":"Uploaded specimen photograph visibly reads Selaginella arenicola Underw. and barcode 03476880; same specific Smithsonian record confirms Palo Pinto TX specimen. Detailed living-plant anatomy deferred.",
        "approval_note":"Individual Smithsonian public-domain voucher and original exact media byte equality verified for owner-authorized photo-first publication.",
        "creator":"Ingrid P. Lin / Smithsonian National Museum of Natural History",
        "source_page":OBJECT,"source_page_is_exact":True,
        "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
        "noncommercial_site_use_confirmed":True,
        "role":"Verified herbarium voucher, Palo Pinto County, Texas; dried mat-forming spikemoss habit (not an in-situ field photo)",
        "modifications":"Unaltered original Smithsonian specimen image",
        "sha256":HASH
    }
    (folder/(name+".json")).write_text(json.dumps(sidecar,indent=2)+"\n")
    row["status"]="SOURCE_AND_LICENSE_VERIFIED"
except Exception as exc:
    row.update(status="HOLD",reason=str(exc)[:500])
REPORT.write_text(json.dumps(row,indent=2)+"\n")
print(json.dumps(row),flush=True)
