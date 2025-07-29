import os
import requests
import yaml
vendor_url = "https://github.com/github-linguist/linguist/raw/refs/heads/main/lib/linguist/vendor.yml"
languages_url = "https://github.com/github-linguist/linguist/raw/refs/heads/main/lib/linguist/languages.yml"
vendor = yaml.safe_load(requests.get(vendor_url).text)
languages = yaml.safe_load(requests.get(languages_url).text)
extension_dict = {}
filename_dict = {}
for lang in languages:
    for ext in languages[lang].get("extensions", []):
        extension_dict[ext.lower()] = lang
    for filename in languages[lang].get("filenames", []):
        filename_dict[filename.lower()] = lang


def get_language_by_filename(filename: str) -> str:
    if os.path.basename(filename).lower() in filename_dict:
        return filename_dict[os.path.basename(filename).lower()]
    if os.path.splitext(filename)[1].lower() in extension_dict:
        return extension_dict[os.path.splitext(filename)[1].lower()]
    return "unknown"
