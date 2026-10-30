"""
Unit tests for Hreflang Sitemap Validator with Full ISO 639-1 / ISO 3166-1 Verification
"""
import unittest
import tempfile
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.hreflang_validator import validate_sitemap_hreflang, validate_hreflang_code

class TestHreflangValidator(unittest.TestCase):
    def test_sample_sitemap_without_mandatory_x_default(self):
        # x-default should NOT be mandatory per Google Search Central guidelines
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://brand.com/sa/ar/</loc>
    <xhtml:link rel="alternate" hreflang="ar-sa" href="https://brand.com/sa/ar/"/>
    <xhtml:link rel="alternate" hreflang="en-sa" href="https://brand.com/sa/en/"/>
  </url>
</urlset>"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml", encoding="utf-8") as f:
            f.write(xml_content)
            tmp_path = f.name

        try:
            res = validate_sitemap_hreflang(tmp_path)
            # Should pass: missing x-default is not an error
            self.assertEqual(res["status"], "PASS")
            self.assertEqual(res["total_issues_found"], 0)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_invalid_locale_format(self):
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://brand.com/</loc>
    <xhtml:link rel="alternate" hreflang="invalid_locale_123" href="https://brand.com/"/>
  </url>
</urlset>"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml", encoding="utf-8") as f:
            f.write(xml_content)
            tmp_path = f.name

        try:
            res = validate_sitemap_hreflang(tmp_path)
            self.assertEqual(res["status"], "FAIL")
            self.assertTrue(any(i["type"] == "INVALID_LOCALE_FORMAT" for i in res["issues"]))
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_syntactically_valid_but_fake_iso_codes(self):
        # 'zz-xx' matches the 2-letter regex ^[a-z]{2}-[a-z]{2}$ but neither zz nor xx exist in ISO standards
        issues_zz_xx = validate_hreflang_code("zz-xx")
        self.assertEqual(len(issues_zz_xx), 2)
        issue_types = [t for t, msg in issues_zz_xx]
        self.assertIn("INVALID_ISO_LANGUAGE_CODE", issue_types)
        self.assertIn("INVALID_ISO_REGION_CODE", issue_types)

        # 'en-zz' has valid language (en) but fake country (zz)
        issues_en_zz = validate_hreflang_code("en-zz")
        self.assertEqual(len(issues_en_zz), 1)
        self.assertEqual(issues_en_zz[0][0], "INVALID_ISO_REGION_CODE")

        # 'zz-sa' has fake language (zz) but valid country (sa)
        issues_zz_sa = validate_hreflang_code("zz-sa")
        self.assertEqual(len(issues_zz_sa), 1)
        self.assertEqual(issues_zz_sa[0][0], "INVALID_ISO_LANGUAGE_CODE")

    def test_sitemap_with_fake_iso_code_fails(self):
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://brand.com/</loc>
    <xhtml:link rel="alternate" hreflang="zz-xx" href="https://brand.com/"/>
  </url>
</urlset>"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml", encoding="utf-8") as f:
            f.write(xml_content)
            tmp_path = f.name

        try:
            res = validate_sitemap_hreflang(tmp_path)
            self.assertEqual(res["status"], "FAIL")
            self.assertTrue(any(i["type"] == "INVALID_ISO_LANGUAGE_CODE" for i in res["issues"]))
            self.assertTrue(any(i["type"] == "INVALID_ISO_REGION_CODE" for i in res["issues"]))
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_duplicate_hreflang_detection(self):
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://brand.com/</loc>
    <xhtml:link rel="alternate" hreflang="ar-sa" href="https://brand.com/sa1"/>
    <xhtml:link rel="alternate" hreflang="ar-sa" href="https://brand.com/sa2"/>
  </url>
</urlset>"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml", encoding="utf-8") as f:
            f.write(xml_content)
            tmp_path = f.name

        try:
            res = validate_sitemap_hreflang(tmp_path)
            self.assertEqual(res["status"], "FAIL")
            self.assertTrue(any(i["type"] == "DUPLICATE_HREFLANG" for i in res["issues"]))
        finally:
            Path(tmp_path).unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
