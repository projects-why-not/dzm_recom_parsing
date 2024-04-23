from .re_parsing import parse_rec_confidence, parse_rec_text


class RecommendationTitle(dict):
    def __init__(self, title, features):
        self.title = title
        super().__init__(self, **features)


class Recommendation:
    def __init__(self, subj, tgt_patients, aim, conf):
        self.subject, self.target, self.aim, self.confidence = subj, tgt_patients, aim, conf

    @classmethod
    def parse_from_dom(cls, dom_recom, dom_confidence):
        try:
            recoms = parse_rec_text(" ".join(dom_recom.text.split()))
            conf = parse_rec_confidence(" ".join(dom_confidence.text.split()))
            return [Recommendation(*rec, conf) for rec in recoms]
        except Exception as e:
            print(dom_recom.text)

        return []
