"""A small BibTeX reader, sufficient for data/zx-papers.bib (the zxcalculus.com publication list)
and data/extra.bib (papers missing from that list)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from . import DATA_DIR

LATEX_ACCENTS = {
    r"\"a": "ä", r"\"o": "ö", r"\"u": "ü", r"\"e": "ë", r"\"i": "ï", r"\'e": "é", r"\'a": "á",
    r"\'o": "ó", r"\'i": "í", r"\'u": "ú", r"\`e": "è", r"\`a": "à", r"\^o": "ô", r"\^e": "ê",
    r"\^i": "î", r"\^a": "â", r"\c c": "ç", r"\c{c}": "ç", r"\~n": "ñ", r"\v s": "š", r"\v{s}": "š",
    r"\v c": "č", r"\v{c}": "č", r"\'c": "ć", r"\o": "ø", r"\ss": "ß", r"\aa": "å", r"\"A": "Ä",
    r"\"O": "Ö", r"\"U": "Ü", r"\'E": "É", r"\l": "ł", r"\&": "&", r"\%": "%", r"\_": "_",
}


def _parse_entries(text: str) -> List[Dict[str, str]]:
    entries = []
    i = 0
    n = len(text)
    while True:
        m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(text, i)
        if not m:
            break
        etype, key = m.group(1).lower(), m.group(2)
        j = m.end()
        fields: Dict[str, str] = {}
        while j < n:
            fm = re.compile(r"\s*(\w[\w\-]*)\s*=\s*").match(text, j)
            if not fm:
                # end of entry
                k = text.find("}", j)
                j = k + 1 if k >= 0 else n
                break
            name = fm.group(1).lower()
            j = fm.end()
            if j < n and text[j] in "{\"":
                close = "}" if text[j] == "{" else '"'
                depth = 0
                start = j + 1
                k = j
                while k < n:
                    c = text[k]
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                    if (close == "}" and depth == 0 and c == "}") or (close == '"' and c == '"' and k > j and depth == 0):
                        break
                    k += 1
                value = text[start:k]
                j = k + 1
            else:
                vm = re.compile(r"[^,}\s]+").match(text, j)
                value = vm.group(0) if vm else ""
                j = vm.end() if vm else j
            fields[name] = value
            cm = re.compile(r"\s*,").match(text, j)
            if cm:
                j = cm.end()
            else:
                em = re.compile(r"\s*\}").match(text, j)
                if em:
                    j = em.end()
                    break
        entries.append({"ENTRYTYPE": etype, "ID": key, **fields})
        i = j
    return entries


def clean(s: str) -> str:
    s = s.replace("\n", " ")
    for k, v in LATEX_ACCENTS.items():
        s = s.replace("{" + k + "}", v).replace(k, v)
    s = re.sub(r"\\textit\{([^}]*)\}|\\emph\{([^}]*)\}", lambda m: m.group(1) or m.group(2), s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("--", "–")
    return re.sub(r"\s+", " ", s).strip()


def _authors(s: str) -> List[str]:
    out = []
    for a in re.split(r"\s+and\s+", clean(s)):
        a = a.strip()
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            a = f"{first} {last}"
        if a:
            out.append(a)
    return out


def _arxiv(fields: Dict[str, str]) -> str:
    for k in ("link", "url", "eprint", "journal"):
        v = fields.get(k, "")
        m = re.search(r"arxiv\.org/abs/([\w./-]+)", v) or re.search(r"arXiv:\s*([\d.]+\w*)", v, re.I)
        if m:
            return "https://arxiv.org/abs/" + m.group(1).rstrip(".")
    if fields.get("archiveprefix", "").lower() == "arxiv" and fields.get("eprint"):
        return "https://arxiv.org/abs/" + fields["eprint"]
    return ""


def _read(p: Path) -> str:
    """Decode line by line: the publication list is mostly UTF-8 with a few cp1252 lines."""
    out = []
    for line in p.read_bytes().split(b"\n"):
        try:
            out.append(line.decode("utf8"))
        except UnicodeDecodeError:
            out.append(line.decode("cp1252", errors="replace"))
    return "\n".join(out)


PARTICLES = {"van", "de", "der", "von", "den", "da", "di", "le", "la", "du"}


def last_name(author: str) -> str:
    words = author.split()
    for i, w in enumerate(words[:-1]):
        if w in PARTICLES and i > 0:
            return " ".join(words[i:])
    return words[-1] if words else ""


def load_bib(paths=None) -> Dict[str, Dict[str, object]]:
    if paths is None:
        # zx-papers.bib first, so that entries in the other .bib files can override it
        paths = [DATA_DIR / "zx-papers.bib"] + sorted(p for p in DATA_DIR.glob("*.bib") if p.name != "zx-papers.bib")
    out: Dict[str, Dict[str, object]] = {}
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        for e in _parse_entries(_read(p)):
            f = {k: v for k, v in e.items()}
            venue = clean(f.get("journal", "") or f.get("booktitle", "") or f.get("school", "")
                          or f.get("publisher", ""))
            if venue.lower().startswith("arxiv preprint"):
                venue = ""
            doi = clean(f.get("doi", ""))
            link = clean(f.get("link", "") or f.get("url", ""))
            title = clean(f.get("title", ""))
            if (title.startswith("20") and "Symposium" in title) or not title:
                # some entries in zx-papers.bib have the proceedings name in the title field
                title = clean(f.get("booktitle", title))
            out[e["ID"]] = {
                "key": e["ID"],
                "title": title,
                "authors": _authors(f.get("author", "")),
                "year": clean(f.get("year", "")),
                "venue": venue,
                "arxiv": _arxiv(f),
                "doi": doi,
                "doi_url": f"https://doi.org/{doi}" if doi else "",
                "link": link,
            }
    return out


def author_string(authors: List[str]) -> str:
    if len(authors) <= 2:
        return " and ".join(authors)
    return ", ".join(authors[:-1]) + " and " + authors[-1]


def short_cite(entry) -> str:
    authors = entry["authors"]
    last = [last_name(a) for a in authors]
    if not last:
        who = "?"
    elif len(last) == 1:
        who = last[0]
    elif len(last) == 2:
        who = f"{last[0]} & {last[1]}"
    else:
        who = f"{last[0]} et al."
    return f"{who} ({entry['year']})"
