import os
import argparse
import json
from urllib.parse import urlparse
import time

from .extractor import extract_urls_from_sitemap, extract_page_data
from .crawler import crawl_sitemap_url
from . import utils


def handle_sitemap_input(sitemap_input):
    sitemap_urls = []

    def process_sitemap(sitemap_url):
        xml_content = utils.get_response_text(sitemap_url)

        if xml_content:
            locs = extract_urls_from_sitemap(xml_content)

            for loc in locs:
                if loc.endswith('.xml'):
                    print(f"Processing Sitemap: {loc}")
                    process_sitemap(loc)
                else:
                    sitemap_urls.append(loc)

    if urlparse(sitemap_input).scheme in ['http', 'https']:
        process_sitemap(sitemap_input)
    elif os.path.isfile(sitemap_input):
        xml_content = utils.read_sitemap_file(sitemap_input)
        if xml_content:
            locs = extract_urls_from_sitemap(xml_content)
            for loc in locs:
                if loc.endswith('.xml'):
                    process_sitemap(loc)
                else:
                    sitemap_urls.append(loc)
    else:
        print("Invalid URL or file path")

    return sitemap_urls


def main():
    parser = argparse.ArgumentParser(
        prog="seo",
        description="An SEO command-line interface tool for parsing sitemap URLs or file paths"
    )

    parser.add_argument(
        'sitemap_input',
        type=str,
        help='The URL or file path of the sitemap to process'
    )

    args = parser.parse_args()
    sitemap_urls = handle_sitemap_input(args.sitemap_input)

    all_refined_page_data = []
    for url in sitemap_urls:
        time.sleep(1)
        raw_page_data, base_url = crawl_sitemap_url(url)
        if raw_page_data:
            refined_data = extract_page_data(raw_page_data, base_url)
            all_refined_page_data.append(refined_data)

    if all_refined_page_data:
        with open("test.txt", "w") as file:
            json.dump([data.dict() for data in all_refined_page_data], file, indent=4, ensure_ascii=False)

