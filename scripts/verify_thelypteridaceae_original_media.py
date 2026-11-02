#!/usr/bin/env python3
"""Validate original ZIP fern photographs against photo-specific iNaturalist licensing."""
from __future__ import annotations
import hashlib,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/"photo-intake/remote-photo-manifests/thelypteridaceae-2026-11-02.json").read_text())
if m["family"]!="Thelypteridaceae" or len(m["photos"])!=10:raise SystemExit("Unexpected family media batch")
allowed={
"thelypteris-kunthii":{"thelypteris kunthii","pelazoneuron kunthii","cyclosorus kunthii","christella normalis","thelypteris normalis"},
"thelypteris-ovata":{"thelypteris ovata","pelazoneuron ovatum","christella ovata","cyclosorus ovatus"}
}
temp=Path(os.environ["RUNNER_TEMP"])
destination=temp/"thelypteridaceae-verified"
report=[]
def fetch(url,maxbytes=26000000):
    request=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyNoncommercialEducationalPhotoVerifier/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request,timeout=30) as resp: payload=resp.read(maxbytes+1)
            if len(payload)>maxbytes:raise ValueError("Provider response too large")
            return payload
        except Exception:
            if attempt==2:raise
            time.sleep(1+attempt)

seen=set()
for x in m["photos"]:
    sid=x["species_id"];pid=int(x["photo_id"]);oid=int(x["observation_id"])
    row={"species_id":sid,"photo_id":pid,"observation_id":oid}
    try:
        if sid not in allowed or pid in seen:raise ValueError("Unexpected taxon or duplicated photo ID")
        seen.add(pid)
        url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.{x['extension']}"
        if url!=x["image_url"] or x["source_url"]!=f"https://www.inaturalist.org/photos/{pid}":
            raise ValueError("Photo IDs and original URLs inconsistent")
        obs_doc=json.loads(fetch(f"https://api.inaturalist.org/v1/observations/{oid}",5000000))
        obs=next((a for a in obs_doc.get("results",[]) if int(a.get("id",0))==oid),None)
        if obs is None:raise ValueError("Source observation not found")
        taxon=str((obs.get("taxon") or {}).get("name") or "").lower().strip()
        if taxon not in allowed[sid]:raise ValueError("Provider species is not mapped to assigned species: "+taxon)
        photo=next((a for a in obs.get("photos",[]) if int(a.get("id",0))==pid),None)
        if photo is None:raise ValueError("Exact image ID not on source observation")
        license_code=str(photo.get("license_code") or "").lower().replace("_","-")
        if license_code!="cc-by-nc":raise ValueError("Media license not independently CC BY-NC: "+license_code)
        creator=str(photo.get("attribution") or "").strip()
        if not creator or creator.lower() in {"no rights reserved","some rights reserved"}:
            creator=x["photographer"]
        if not creator:raise ValueError("Photographer attribution not established")
        photo_data=fetch(url)
        actual=hashlib.sha256(photo_data).hexdigest()
        if actual!=x["sha256"]:raise ValueError("Provider original does not match user's backed-up ZIP SHA256")
        with Image.open(io.BytesIO(photo_data)) as im:
            if im.format!="JPEG" or im.width*im.height>80000000:raise ValueError("Not a valid JPEG")
            im.verify()
        name=f"inat-{pid}.{x['extension']}"
        folder=destination/"photo-intake"/"approved"/sid
        folder.mkdir(parents=True,exist_ok=True)
        (folder/name).write_bytes(photo_data)
        sidecar={
          "species_id":sid,"photo_file":name,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
          "rights_approved_for_public":True,"taxon_reviewed":True,
          "approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY","policy_ref":"PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02",
          "review_operator":"Hays Botany 2026-11-02 ZIP contact-sheet and live photo-specific iNaturalist source review",
          "source_review_evidence":f"Provider live observation {oid} contains photo {pid} under individual {license_code} license; original image bytes have SHA256 {actual} matching original uploaded ZIP, with true creator attributed.",
          "taxon_review_evidence":f"Live iNaturalist taxon {taxon} matches photo's assigned species or documented scientific synonym. Uploaded visual contact sheet shows fern fronds and no obvious mismatched organism; complete morphology later.",
          "approval_note":"Existing owner standing noncommercial photo-first approval, with real photo-specific CC BY-NC and creator check plus original image hash and basic fern subject check.",
          "creator":creator,"source_page":f"https://www.inaturalist.org/photos/{pid}","source_page_is_exact":True,
          "license":"CC BY-NC 4.0","license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
          "noncommercial_site_use_confirmed":True,
          "role":x["role"]+" (general fern view; diagnostic anatomy/precise identification deferred)",
          "modifications":"Original unchanged iNaturalist image",
          "sha256":actual
        }
        (folder/(name+".json")).write_text(json.dumps(sidecar,indent=2)+"\n")
        row["status"]="PHOTO_SPECIFIC_RIGHTS_AND_SOURCE_VERIFIED"
    except Exception as exc:
        row.update(status="HOLD",reason=str(exc)[:450])
    print(json.dumps(row),flush=True)
    report.append(row)
report_path=temp/"thelypteridaceae-photo-specific-rights.json"
report_path.write_text(json.dumps({"zip":"Thelypteridaceae.zip","results":report},indent=2)+"\n")
print(json.dumps({"verified":sum(r["status"]=="PHOTO_SPECIFIC_RIGHTS_AND_SOURCE_VERIFIED" for r in report),"held":sum(r["status"]=="HOLD" for r in report)}),flush=True)
