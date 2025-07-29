from urllib.parse import urljoin
from markdownify import MarkdownConverter


class Converter(MarkdownConverter):
    """
    Create a custom MarkdownConverter that converts relative links to absolute URLs
    """

    def __init__(self, base_url: str, make_links_absolute: bool=True, **options):
        self.base_url = base_url
        self.make_links_absolute = make_links_absolute
        MarkdownConverter.__init__(self, **options)

    def convert_a(self, el, text, parent_tags):
        """Convert anchor tags with relative → absolute URLs"""
        if self.make_links_absolute:
            href = el.get('href')
            if href is not None:
                # Skip processing for absolute URLs and special protocols
                if not any(href.startswith(proto) for proto in ('http://', 'https://', 'mailto:', 'tel:', '#')):
                    el['href'] = urljoin(self.base_url, href)
        return super().convert_a(el, text, parent_tags)
    
    def convert_img(self, el, text, parent_tags):
        """Convert image tags with relative → absolute URLs"""
        return ""
    
    def convert_div(self, el, text, parent_tags):
        if "wikipedia.org" in self.base_url and el.get("id", "").startswith("p-"):
            return ""
        return super().convert_div(el, text, parent_tags)
