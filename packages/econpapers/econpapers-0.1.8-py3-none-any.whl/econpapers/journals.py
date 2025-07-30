from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd


class ResearchOutlet:
    def __init__(
        self, find_pdf: [0, 1], is_journal: [0, 1], folder, url_section, pages=set()
    ):
        self.find_pdf = find_pdf  # 1 = look for link to pdf, 0 = not
        self.folders = (
            folder if isinstance(folder, list) else [folder]
        )  # Accept string or list
        self.url_section = url_section  # URL part changing
        self.pages = pages  # Set to keep track of crawled pages
        self.data = []  # List to store the paper details before converting to dataframe
        self.is_journal = is_journal  # flag outlet as a journal for metadata purposes

    def get_papers(self, pageUrl):
        for folder in self.folders:
            base_url = (
                f"https://econpapers.repec.org/{self.url_section}{folder}{pageUrl}"
            )
            try:
                html = urlopen(base_url)
            except Exception as e:
                print(f"Could not open {base_url}: {e}")
                continue

            bs = BeautifulSoup(html, "html.parser")
            links = set()
            try:
                for dl in bs.find_all("dl"):
                    for link in dl.find_all(
                        "a", href=lambda href: href and href.endswith(".htm")
                    ):
                        links.add(link.attrs["href"])
            except AttributeError:
                print("Error while extracting links from dl!")

            for link in links:
                try:
                    paper_url = (
                        f"https://econpapers.repec.org/{self.url_section}{folder}{link}"
                    )
                    html = urlopen(paper_url)
                    paper = BeautifulSoup(html, "html.parser")

                    title = (
                        paper.find("meta", {"name": "citation_title"})["content"]
                        if paper.find("meta", {"name": "citation_title"})
                        else "NA"
                    )
                    authors = (
                        paper.find("meta", {"name": "citation_authors"})["content"]
                        if paper.find("meta", {"name": "citation_authors"})
                        else "NA"
                    )
                    jel_codes = (
                        paper.find("meta", {"name": "JEL-Codes"})["content"]
                        if paper.find("meta", {"name": "JEL-Codes"})
                        else "NA"
                    )
                    year = (
                        paper.find("meta", {"name": "citation_year"})["content"]
                        if paper.find("meta", {"name": "citation_year"})
                        else "NA"
                    )
                    abstract = (
                        paper.find("meta", {"name": "citation_abstract"})["content"]
                        if paper.find("meta", {"name": "citation_abstract"})
                        else "NA"
                    )

                    metadata = {
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "jel_codes": jel_codes,
                        "abstract": abstract,
                        "page_link": f"/{self.url_section}{folder}{link}",
                    }

                    if self.find_pdf == 1:
                        pdf_tag = paper.find("a", href=re.compile(".pdf"))
                        metadata["pdf_link"] = pdf_tag["href"] if pdf_tag else "NA"

                    if self.is_journal == 1:
                        journal = paper.find("meta", {"name": "citation_journal_title"})
                        metadata["journal"] = journal["content"] if journal else "NA"

                    self.data.append(metadata)

                except Exception as e:
                    print(f"Error processing page {link}: {e}")

            for link in bs.find_all("a", href=re.compile("^default[1-9]")):
                if "href" in link.attrs and link.attrs["href"] not in self.pages:
                    new_page = link.attrs["href"]
                    self.pages.add(new_page)
                    self.get_papers(new_page)  # Recursive call still works

    def get_dataframe(self):
        """Convert the data into a pandas dataframe."""
        return pd.DataFrame(self.data)


class Journal(ResearchOutlet):
    def __init__(self, folder, url_section="article", pages=set(), find_pdf=0):
        super().__init__(
            find_pdf, is_journal=1, folder=folder, url_section=url_section, pages=pages
        )
        self.pages = pages
        self.data = []
        self.find_pdf = find_pdf
        self.url_section = url_section
        self.is_journal = 1

url_component = (
    "/article/"  # Part of the URL "connecting" the domain to the actual journal page
)




def get_all_links(pageUrl: str) -> set:
    """Gets all archive divisions (name by letter) from the EconPapers home."""
    html = urlopen("https://econpapers.repec.org{}".format(pageUrl))
    bs = BeautifulSoup(html, "lxml")
    links = set()
    for list in bs.find_all("div"):
        for link in list.find_all("a", href=re.compile("default[A-Z].htm*")):
            links.add(link.attrs["href"])
    return links


# urls = get_all_links(url_component)

###############################################################################

# Step 3


def relevant_links_one_letter(pageUrl: str, journal_list: list) -> set:
    """Given one letter in the archive, looks for journals in the top X list."""
    html = urlopen("https://econpapers.repec.org{}".format(pageUrl))
    bs = BeautifulSoup(html, "html.parser")
    links = set()
    try:
        for list in bs.find_all("table"):
            for link in list.find_all("a", href=re.compile("article/[a-z]")):
                if link.text in journal_list:
                    links.add(link.attrs["href"])
    except AttributeError:
        print("Error!")
    return links


def links_all_alphabet(linkset: set, journal_list: list) -> list:
    """Iterates relevant_links_one_letter all over the alphabet."""
    link_list = []
    for i in linkset:
        link_list.append(relevant_links_one_letter(i, journal_list))
    link_list.append(relevant_links_one_letter("/article/#A", journal_list))
    return link_list


def fix_link_list(link_list: list) -> list:
    """Removes duplicate links and empty sets from the list."""
    for i in link_list[
        :
    ]:  # Decomposes sets of links, and puts them all in one larger list
        if isinstance(i, set):
            if len(i) == 0:
                link_list.remove(i)
            else:
                for j in i:
                    link_list.append(j)
                link_list.remove(i)
    link_list = list(set(link_list))  # Removes any duplicate links
    for i in link_list[:]:
        j = i.replace("/article", "")
        link_list.append(j)
        link_list.remove(i)
    return link_list


# links = links_all_alphabet(urls, journals)
# links = fix_link_list(links)


#######


# given a journal name
def get_journal_folders(journal_list: list):
    """Get folders of list of journals (case sensitive!)"""
    links_to_journals = get_all_links(url_component)
    all_links = links_all_alphabet(links_to_journals, journal_list)
    fixed_links = fix_link_list(all_links)
    return fixed_links


def papers_dataframe(journal_list: list):
    """Get paper dataframe given list of journals"""
    folders = get_journal_folders(journal_list)
    journals = Journal(folder=folders)
    journals.get_papers("")
    df = journals.get_dataframe()
    return df
