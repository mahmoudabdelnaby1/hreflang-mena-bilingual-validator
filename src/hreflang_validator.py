#!/usr/bin/env python3
"""
Hreflang XML Sitemap & Header Validator for Bilingual Regional SEO
Complies with Google Search Central official guidelines:
- Validates hreflang against official ISO 639-1 language and ISO 3166-1 alpha-2 country codes
- Rejects syntactically plausible but non-existent ISO codes (e.g. 'zz-xx', 'ar-zz')
- Treats 'x-default' as valid optional fallback per Google specification
- Verifies self-referencing hreflang tags on audited pages
- Audits reciprocal return links (bidirectional confirmation) across sitemap entries
- Detects duplicate alternate entries on the same URL
"""
import re
import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple

# Official ISO 639-1 2-letter language codes
ISO_639_1_LANGUAGES: Set[str] = {
    "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az",
    "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs",
    "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy",
    "da", "de", "dv", "dz", "ee", "el", "en", "eo", "es", "et", "eu",
    "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd", "gl", "gn", "gu", "gv",
    "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz",
    "ia", "id", "ie", "ig", "ii", "ik", "io", "is", "it", "iu",
    "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko", "kr", "ks", "ku", "kv", "kw", "ky",
    "la", "lb", "lg", "li", "ln", "lo", "lt", "lu", "lv",
    "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my",
    "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv", "ny",
    "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt",
    "qu", "rm", "rn", "ro", "ru", "rw",
    "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw",
    "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty",
    "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"
}

# Official ISO 3166-1 alpha-2 2-letter country codes
ISO_3166_1_REGIONS: Set[str] = {
    "ad", "ae", "af", "ag", "ai", "al", "am", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az",
    "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz",
    "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz",
    "de", "dj", "dk", "dm", "do", "dz",
    "ec", "ee", "eg", "eh", "er", "es", "et", "fi", "fj", "fk", "fm", "fo", "fr",
    "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy",
    "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it",
    "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz",
    "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly",
    "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz",
    "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om",
    "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa",
    "re", "ro", "rs", "ru", "rw",
    "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "sv", "sx", "sy", "sz",
    "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tv", "tw", "tz",
    "ua", "ug", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"
}

FORMAT_PATTERN = re.compile(r"^[a-z]{2}(?:-[a-z]{2})?$", re.IGNORECASE)

def validate_hreflang_code(hreflang: str) -> List[Tuple[str, str]]:
    """
    Validates hreflang tag against ISO 639-1 and ISO 3166-1 standards.
    Returns list of (issue_type, message) tuples.
    """
    clean_code = hreflang.strip().lower()
    if clean_code == "x-default":
        return []

    if not FORMAT_PATTERN.match(clean_code):
        return [("INVALID_LOCALE_FORMAT", f"Invalid locale format '{hreflang}'. Must be ISO 639-1 (e.g. 'ar') or ISO 639-1 + ISO 3166-1 (e.g. 'ar-sa') or 'x-default'.")]

    errors = []
    parts = clean_code.split("-")
    lang = parts[0]
    if lang not in ISO_639_1_LANGUAGES:
        errors.append(("INVALID_ISO_LANGUAGE_CODE", f"Language '{lang}' in '{hreflang}' is not a recognized ISO 639-1 code."))

    if len(parts) > 1:
        region = parts[1]
        if region not in ISO_3166_1_REGIONS:
            errors.append(("INVALID_ISO_REGION_CODE", f"Region '{region}' in '{hreflang}' is not a recognized ISO 3166-1 alpha-2 code."))

    return errors

def validate_sitemap_hreflang(xml_path: str) -> Dict[str, Any]:
    issues: List[Dict[str, str]] = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}

    url_tags = root.findall("sm:url", ns)
    pages_checked = 0
    
    # Store page alternates for reciprocity check: url -> set of (hreflang, target_url)
    page_alternates: Dict[str, Dict[str, str]] = {}

    for u in url_tags:
        loc = u.find("sm:loc", ns)
        loc_url = loc.text.strip() if loc is not None and loc.text else ""
        if not loc_url:
            continue
            
        pages_checked += 1
        alternates = u.findall("xhtml:link", ns)
        
        seen_langs: Set[str] = set()
        self_referenced = False
        page_alternates[loc_url] = {}

        for alt in alternates:
            hreflang = alt.attrib.get("hreflang", "").lower().strip()
            href = alt.attrib.get("href", "").strip()

            if not hreflang:
                issues.append({"url": loc_url, "type": "MISSING_HREFLANG_ATTRIBUTE", "message": "Link tag missing hreflang attribute."})
                continue

            # Validate ISO code format and actual official ISO registration
            iso_issues = validate_hreflang_code(hreflang)
            for err_type, err_msg in iso_issues:
                issues.append({
                    "url": loc_url,
                    "type": err_type,
                    "message": err_msg
                })

            # Check for duplicate hreflang tag on same URL
            if hreflang in seen_langs:
                issues.append({
                    "url": loc_url,
                    "type": "DUPLICATE_HREFLANG",
                    "message": f"Duplicate hreflang tag '{hreflang}' defined on same page."
                })
            seen_langs.add(hreflang)

            # Check self-reference
            if href.rstrip("/") == loc_url.rstrip("/"):
                self_referenced = True

            page_alternates[loc_url][hreflang] = href

        # Google rule: page must include a self-referencing alternate link
        if alternates and not self_referenced:
            issues.append({
                "url": loc_url,
                "type": "MISSING_SELF_REFERENCE",
                "message": f"URL does not contain a self-referencing alternate hreflang link to itself."
            })

    # Reciprocity check: if Page A links to Page B, Page B should link back to Page A
    for page_url, alt_map in page_alternates.items():
        for lang, target_href in alt_map.items():
            if lang == "x-default":
                continue
            target_clean = target_href.rstrip("/")
            # If target exists in sitemap, verify return tag
            for other_page, other_alts in page_alternates.items():
                if other_page.rstrip("/") == target_clean and other_page.rstrip("/") != page_url.rstrip("/"):
                    # Check if other_page links back to page_url
                    links_back = any(dest.rstrip("/") == page_url.rstrip("/") for dest in other_alts.values())
                    if not links_back:
                        issues.append({
                            "url": page_url,
                            "type": "MISSING_RECIPROCAL_LINK",
                            "message": f"Return tag missing: '{page_url}' links to '{target_clean}' for '{lang}', but target does not link back."
                        })

    has_errors = any(i["type"] in [
        "INVALID_LOCALE_FORMAT",
        "INVALID_ISO_LANGUAGE_CODE",
        "INVALID_ISO_REGION_CODE",
        "DUPLICATE_HREFLANG",
        "MISSING_SELF_REFERENCE",
        "MISSING_RECIPROCAL_LINK"
    ] for i in issues)

    return {
        "sitemap_path": str(xml_path),
        "pages_audited": pages_checked,
        "total_issues_found": len(issues),
        "issues": issues,
        "status": "PASS" if not has_errors else "FAIL",
        "official_spec_reference": "https://developers.google.com/search/docs/specialty/international/localized-versions"
    }

def main():
    parser = argparse.ArgumentParser(description="Hreflang XML Sitemap Validator")
    parser.add_argument("--sitemap", required=True, help="Path to XML sitemap")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    res = validate_sitemap_hreflang(args.sitemap)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    main()
