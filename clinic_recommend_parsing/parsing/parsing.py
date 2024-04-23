from ..fetching import ChromeHtmlFetcher
from .constants import CR_URI_BASE_URI, TERM_BLOCK_NAMES
from .component import Recommendation, RecommendationTitle
from bs4 import BeautifulSoup
import pandas as pd


class CRParser:
    def __init__(self, cr_id):
        fetcher = ChromeHtmlFetcher()
        html = fetcher.get_html(CR_URI_BASE_URI + str(cr_id))
        soup = BeautifulSoup(html, features="lxml")
        self._contents = self._parse_contents(soup)
        self._title = self._parse_title(soup)

    def __getitem__(self, item):
        if item in self._contents:
            return self._contents[item]
        elif item in self._title:
            return self._title[item]
        raise KeyError

    def get_instr_recoms(self, to_csv=True):
        def find_instr_proc_block_dfs(d):
            if type(d) is not dict:
                return None
            for k in d:
                if k is None:
                    continue
                if "инструментальные" in k.lower() and "исследования" in k.lower():
                    return k
                else:
                    rec_k = find_instr_proc_block_dfs(d[k])
                    if rec_k is not None:
                        return [k, rec_k]
            return None

        recoms = []
        instr_keys = find_instr_proc_block_dfs(self._contents)
        if type(instr_keys) is str:
            subs = self._contents[instr_keys]
        else:
            subs = self._contents
            for i in range(len(instr_keys)):
                subs = subs[instr_keys[i]]  # ["2. Диагностика"]["2.4 Инструментальные диагностические исследования"]
        if type(subs) is dict and None in subs:
            subs = subs[None]
        for i in range(len(subs)):
            if subs[i].name == "ul" and subs[i].text.find("Рекомендуется") >= 0:
                loc_recoms = Recommendation.parse_from_dom(subs[i], subs[i + 1])
                if len(loc_recoms) > 0:
                    recoms += loc_recoms

        if not to_csv:
            return recoms

        return pd.DataFrame([[rec.subject, rec.target, rec.aim, rec.confidence] for rec in recoms],
                            columns=["Метод лучевой диагностики",
                                     "Категория пациентов",
                                     "Цель использования",
                                     "Уровень убедительности рекомендаций"])

    @classmethod
    def _parse_contents(cls, clinical_rec_div):
        def parse_subcontents(level=2, **kwargs):
            assert "div" in kwargs or "subs" in kwargs
            assert level in [2, 3, 4, 5]

            pts = dict()
            if "div" in kwargs:
                subs = list(list(kwargs["div"].find("div").children)[0].children)
            else:
                subs = kwargs["subs"]
            cur_title, cur_st_ind = None, 0
            has_subheaders = False

            for i in range(len(subs)):
                if subs[i].name == f"h{level}":
                    if cur_title is not None:
                        if has_subheaders:
                            pts[cur_title] = parse_subcontents(subs=subs[cur_st_ind:i], level=level + 1)
                        else:
                            pts[cur_title] = subs[cur_st_ind:i]
                        cur_title = None
                        has_subheaders = False
                        cur_st_ind = i + 1
                    cur_title = subs[i].text
                if subs[i].name == f"h{level + 1}":
                    has_subheaders = True
            if has_subheaders:
                pts[cur_title] = parse_subcontents(subs=subs[cur_st_ind:], level=level + 1)
            else:
                pts[cur_title] = subs[cur_st_ind:]
            return pts

        contents_ul = clinical_rec_div.find("ul")
        contents = [li.find("a").text for li in contents_ul.find_all("li")]
        recom_pts = clinical_rec_div.find_all("div", attrs={"class": "clin-rec-doc__content"})
        res = {}
        for i, title in enumerate(contents):
            if title.split(".")[0].isdigit():
                res[title] = parse_subcontents(div=recom_pts[i])
            elif title in TERM_BLOCK_NAMES:
                res[title] = cls._parse_terms(recom_pts[i])
            else:
                res[title] = recom_pts[i]

        return res

    @classmethod
    def _parse_terms(cls, div):
        terms = {}
        for p in div.find_all("p"):
            txt = " ".join(p.text.replace("—", ":").replace("–", ":").replace("-", ":").split())
            txt = txt.split(" : ")
            k, v = txt[0], " : ".join(txt[1:])
            terms[k] = v
        return terms

    @classmethod
    def _parse_title(cls, html):
        def parse_dopinfo(div):
            res = {}
            for subdiv in div.children:
                subdiv_txt = subdiv.text
                k, v = ":".join(subdiv_txt.split(":")[:-1]), subdiv_txt.split(":")[-1]
                res[k] = v
            return res

        title_div = html.find("div", attrs={"class": "main-text"})
        title = title_div.find("h1").text
        app_info = {}
        for div in html.find_all("div", attrs={"class": "main-dopinfo"}):
            app_info.update(parse_dopinfo(div))

        return RecommendationTitle(title, app_info)
