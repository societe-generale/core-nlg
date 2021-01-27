import json

from CoreNLG.NlgTools import NlgTools
from CoreNLG.PredefObjects import TextVar

nlg = NlgTools()

text = TextVar(
    "Le montant", nlg.nlg_syn(("est en hausse", "HAUSSE"), "augmenter", "grandit"), "de 1000 euros.",
    nlg.post_eval("HAUSSE", "je suis passé en hausse", "")
)


# print(nlg.write_text(text))
print(json.dumps(nlg.get_text_details(text), ensure_ascii=False))
# print(nlg.get_all_texts(text))