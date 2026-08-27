import json, urllib.request, urllib.parse, time, os, sys
UA={"User-Agent":"koh-lanta-dataset/1.0 (personal research)"}
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"wiki")

def api(params):
    params.setdefault("format","json")
    q=urllib.parse.urlencode(params)
    req=urllib.request.Request(f"https://kohlanta.fandom.com/fr/api.php?{q}",headers=UA)
    for a in range(4):
        try:
            with urllib.request.urlopen(req,timeout=45) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code!=429 or a==3: raise
            time.sleep(6*(a+1))

def content(title):
    d=api({"action":"query","prop":"revisions","rvprop":"content","rvslots":"main",
           "titles":title,"redirects":"1"})
    for pid,p in d["query"]["pages"].items():
        if "revisions" in p: return p["revisions"][0]["slots"]["main"]["*"]
    return None

def search(term):
    d=api({"action":"query","list":"search","srsearch":term,"srlimit":3})
    return [r["title"] for r in d["query"]["search"]]

SEASONS=[
 ("s01","Les Aventuriers de Koh-Lanta (Saison 1)"),("s02","Koh-Lanta : Nicoya"),
 ("s03","Koh-Lanta : Bocas del Toro"),("s04","Koh-Lanta : Panama"),
 ("s05","Koh-Lanta : Pacifique"),("s06","Koh-Lanta : Vanuatu"),
 ("s07","Koh-Lanta : Palawan"),("s08","Koh-Lanta : Caramoan"),
 ("s09","Koh-Lanta : Palau"),("s10","Koh-Lanta : Viêtnam"),
 ("s11","Koh-Lanta : Raja Ampat"),("s12","Koh-Lanta : Malaisie"),
 ("s14","Koh-Lanta : Johor"),("s15","Koh-Lanta : Thaïlande"),
 ("s16","Koh-Lanta : L'Île au Trésor"),("s17","Koh-Lanta : Cambodge"),
 ("s18","Koh-Lanta : Fidji"),("s20","Koh-Lanta : La Guerre des Chefs"),
 ("s21","Koh-Lanta : Les 4 Terres"),("s22","Koh-Lanta : Les Armes Secrètes"),
 ("s23","Koh-Lanta : Le Totem Maudit"),("s24","Koh-Lanta : Le Feu Sacré"),
 ("s25","Koh-Lanta : Les Chasseurs d'Immunité"),("s26","Koh-Lanta : La Tribu Maudite"),
 ("s27","Koh-Lanta : La Revanche des 4 Terres"),("s28","Koh-Lanta : Les Reliques du Destin"),
 ("sp1","Koh-Lanta : Le Retour des Héros"),("sp2","Koh-Lanta : Le Choc des Héros"),
 ("sp3","Koh-Lanta : La Revanche des Héros"),("sp4","Koh-Lanta : La Nouvelle Édition"),
 ("sp5","Koh-Lanta : Le Combat des Héros"),("sp6","Koh-Lanta : L'Île des Héros"),
 ("sp7","Koh-Lanta : La Légende"),("sp8","Koh-Lanta All Stars"),
]

for sid,title in SEASONS:
    path=os.path.join(OUT,sid+".fandom.wiki")
    if os.path.exists(path) and os.path.getsize(path)>5000:
        print(f"{sid:5s} cache            {os.path.getsize(path)}"); continue
    t=content(title); used=title
    if not t or "Tribebox" not in t:
        for cand in search(title):
            t2=content(cand)
            if t2 and "Tribebox" in t2: t,used=t2,cand; break
            time.sleep(1)
    if t and "Tribebox" in t:
        open(path,"w").write(t); print(f"{sid:5s} {used:40s} {len(t)}")
    else:
        print(f"{sid:5s} INTROUVABLE ({title})")
    time.sleep(1.5)
