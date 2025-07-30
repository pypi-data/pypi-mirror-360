from html2text import HTML2Text
import bleach
from bs4 import BeautifulSoup


def _get_html2text_obj_with_config() -> HTML2Text:
    """Get HTML2Text object with config set."""
    txt_maker = HTML2Text()

    # some settings to avoid newline problems with links
    txt_maker.ignore_links = False
    txt_maker.body_width = 0
    txt_maker.protect_links = True
    txt_maker.wrap_links = False

    # table settings:
    txt_maker.ignore_tables = True  # keep row content
    return txt_maker


def _get_plaintext_from_html(html: str) -> str:
    """html -> ASCII plaintext, via HTML2Text."""
    txt_maker = _get_html2text_obj_with_config()
    doc = txt_maker.handle(html)
    return doc


def _remove_code(html: str) -> str:
    # exclude 'code' tags from link output:
    soup = BeautifulSoup(html, 'lxml')
    soup = _remove_code_via_soup(soup)
    html_str = str(soup)
    return html_str


def _remove_code_via_soup(soup):
    for s in soup.select('code'):
        s.extract()
    return soup


def _remove_del_text(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    soup = _remove_del_text_via_soup(soup)
    html_str = str(soup)
    return html_str


def _remove_del_text_via_soup(soup):
    for s in soup.select('del'):
        s.extract()
    return soup


def _remove_main_formatting(
        html: str, *,
        tags: list[str] = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']) -> str:
    return bleach.clean(html, tags=tags, strip=True)


def _remove_latex(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    soup = _remove_latex_via_soup(soup)
    html_str = str(soup)
    return html_str


def _remove_latex_via_soup(soup):
    for s in soup.select('span', {'class': 'MathJax_Preview'}):
        s.extract()
    return soup


def _get_all_latex_from_html_content(html: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')

    s_content = soup.find_all('span', {'class': 'MathJax_Preview'},
                              string=True)
    latex_found_list = [i.string for i in s_content]
    return latex_found_list
