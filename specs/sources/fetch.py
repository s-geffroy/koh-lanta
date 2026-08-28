import json, re, unicodedata, urllib.request, urllib.parse, os, sys, time

UA = {"User-Agent": "koh-lanta-dataset/1.0 (personal research)"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")
os.makedirs(OUT, exist_ok=True)

def _cle(titre):
    """Forme comparable d'un titre : sans accents, sans ponctuation, en bas de
    casse. « Koh-Lanta : Nicoya » et « Koh-Lanta: Nicoya » sont le meme titre ;
    « Koh-Lanta » ne l'est pas."""
    t = unicodedata.normalize("NFD", titre or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def wikitext(host, title, tries=4):
    """Le wikitexte de `title`, ou None.

    On demande explicitement les redirections (`redirects=1`) : sans elles,
    « Koh-Lanta : Malaisie » ne resout pas. Mais une redirection peut mener
    AILLEURS -- « Koh-Lanta: Bocas del Toro » renvoie a l'article general du
    programme, qui fait 19 ko et passe donc tous les controles de taille. On
    verifie donc que la page atteinte est bien celle demandee.
    """
    q = urllib.parse.urlencode({
        "action": "query", "prop": "revisions", "rvprop": "content",
        "rvslots": "main", "format": "json", "titles": title, "redirects": "1"})
    url = f"https://{host}/w/api.php?{q}"
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            time.sleep(8 * (attempt + 1))
    else:
        return None
    q = d.get("query", {})
    arrivee = title
    for etape in ("normalized", "redirects"):
        for m in q.get(etape, []) or []:
            if m["from"] == arrivee:
                arrivee = m["to"]
    if _cle(arrivee) != _cle(title):
        print(f"  ! {title} redirige vers « {arrivee} » : ignore", file=sys.stderr)
        return None
    for pid, p in (q.get("pages") or {}).items():
        if pid == "-1" or "revisions" not in p:
            return None
        return p["revisions"][0]["slots"]["main"]["*"]
    return None

def grab(sid, candidates):
    path = os.path.join(OUT, sid + ".wiki")
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        return sid, "cache", os.path.getsize(path)
    for host, title in candidates:
        try:
            t = wikitext(host, title)
        except Exception as e:
            print(f"  ! {sid} {host} {title}: {e}", file=sys.stderr); continue
        if t and len(t) > 2000:
            open(path, "w").write(t)
            return sid, f"{host}:{title}", len(t)
        time.sleep(2.0)
    return sid, "INTROUVABLE", 0

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    for sid, cands in spec:
        print("%-5s %-60s %s" % grab(sid, [tuple(c) for c in cands]), flush=True)
        time.sleep(2.5)
