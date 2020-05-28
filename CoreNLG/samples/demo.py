import lxml

from CoreNLG.PredefObjects import TextVar
from CoreNLG.NlgTools import NlgTools

lang = 'fr' # change language to en / fr
nlg = NlgTools(lang=lang)
my_text = TextVar()

data = {
    "2018": {
        "nbi": 20000,
        "gni": 3500,
        "quarters": {
            "Q1": {
                "nbi": 7000,
                "gni": 700
            },
            "Q2": {
                "nbi": 7000,
                "gni": 1500
            },
            "Q3": {
                "nbi": 6000,
                "gni": 1700
            },
            "Q4": {
                "nbi": 5000,
                "gni": 500
            }
        }
    },
    "2019": {
        "nbi": 22000,
        "gni": 3000,
        'quarters': {
            "Q1": {
                "nbi": 5000,
                "gni": 600
            },
            "Q2": {
                "nbi": 7000,
                "gni": 1100
            },
            "Q3": {
                "nbi": 5500,
                "gni": 800
            },
            "Q4": {
                "nbi": 6500,
                "gni": 700
            }
        }
    }
}


def get_headers():
    line = TextVar(nlg.add_tag('th', '(in millions euros)'))
    for year, dico in data.items():
        line += nlg.add_tag('th', year)
        for quarter in data[year]['quarters']:
            line += nlg.add_tag('th', quarter)

    return nlg.add_tag('thead', nlg.add_tag('tr', line))


def get_line(attribute):
    line = TextVar(nlg.add_tag('th', 'NBI' if attribute == 'nbi' else 'Group net income'))
    for year, dico in data.items():
        line += nlg.add_tag('td', nlg.nlg_num(data[year][attribute], mile_sep=' '))
        for quarter in data[year]['quarters']:
            line += nlg.add_tag('td', nlg.nlg_num(data[year]['quarters'][quarter][attribute], mile_sep=' '))

    return nlg.add_tag('tr', line)


# Display html table
my_style = """
table {
border: medium solid #6495ed;
border-collapse: collapse;
}
th {
font-family: monospace;
border: thin solid #6495ed;
padding: 5px;
background-color: #D0E3FA;
}
td {
font-family: sans-serif;
border: thin solid #6495ed;
padding: 5px;
text-align: center;
background-color: #ffffff;
}
ul {
margin-top: 0;
}
"""

my_text += nlg.add_tag('style', my_style)
my_text += nlg.add_tag(
    'table',
    get_headers() +

    nlg.add_tag(
        'body',
        get_line('nbi') +
        get_line('gni')
    )
)

# saut de ligne
my_text += nlg.add_tag('p')

# Exercise 1
my_text += nlg.add_tag('b', 'Quarter comparison' if lang == 'en' else 'Comparaison par trimestre'), nlg.add_tag('p')

analysed_year = 2019
current_year = str(analysed_year)
previous_year = str(analysed_year - 1)

for i in range(1, 5):
    q_id = 'Q' + str(i)
    en_quarter = q_id
    fr_quarter = 'T' + str(i)

    # Compute variation
    nbi_current_year = data[current_year]['quarters'][q_id]["nbi"]
    nbi_previous_year = data[previous_year]['quarters'][q_id]["nbi"]
    var = (nbi_current_year - nbi_previous_year) * 100 / nbi_previous_year

    str_ratio = nlg.nlg_num(var, sep='.' if lang == 'en' else ',', mile_sep=' ', dec=1) + ' %'
    ratio_with_style = nlg.add_tag('b', str_ratio, style='color:red')

    # Defining different synonyms for variations in text
    if lang == 'en':
        def syno_increased():
            return nlg.nlg_syn('increased', 'rised')


        def syno_decreased():
            return nlg.nlg_syn('decreased', 'declined', 'dropped')
    else:
        def syno_la_hausse():
            return nlg.nlg_syn("L'augmentation", "La hausse")


        def syno_la_baisse():
            return nlg.nlg_syn('La baisse', 'La diminution', 'Le recul')


        def syno_augmente():
            return nlg.nlg_syn('augmente', "s'accroît")


        def syno_baisse():
            return nlg.nlg_syn('baisse', 'diminue', 'recule')

    # first option
    variante_1 = TextVar(

        'In', en_quarter + '-' + current_year[2:], 'the NBI',
        'has ' + syno_increased() if var > 0 else 'has ' + syno_decreased() if var < 0 else 'remained stable',
        'by ' + ratio_with_style if var != 0 else '', 'compared to', en_quarter + '-' + previous_year[2:], '.'

    ) if lang == 'en' else TextVar(

        syno_la_hausse() if var > 0 else syno_la_baisse(),
        'du NBI au', fr_quarter + '-' + current_year[2:], 'est de ' + ratio_with_style if var != 0 else '',
        nlg.nlg_syn('par rapport au', 'en comparaison du'), fr_quarter + '-' + previous_year[2:], '.'

    )

    # second option
    variante_2 = TextVar(

        'In comparison with', en_quarter + '-' + previous_year[2:], 'the NBI',
        'has ' + syno_increased() if var > 0 else 'has ' + syno_decreased() if var < 0 else 'remained stable',
        'by ' + ratio_with_style if var != 0 else '', 'in', en_quarter + '-' + current_year[2:], '.'

    ) if lang == 'en' else TextVar(

        'Au', fr_quarter + '-' + current_year[2:], ', le NBI', syno_augmente() if var > 0 else syno_baisse(),
        'de ' + ratio_with_style if var != 0 else '',
        nlg.nlg_syn('par rapport au', 'en comparaison du'), fr_quarter + '-' + previous_year[2:], '.'

    )

    # choice of option
    my_text += nlg.nlg_syn(variante_1, variante_2), nlg.add_tag('br')

# saut de ligne
my_text += nlg.add_tag('p')

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

# Exercise 2
my_text += nlg.add_tag('b', 'Main quarters' if lang == 'en' else 'Trimestres les plus importants'), nlg.add_tag('p')
for year in ["2018", "2019"]:
    q_above = [q_id for q_id in data[year]['quarters'] if data[year]['quarters'][q_id]['gni'] > 1000]
    q_above_fr = [q_id.replace('Q', 'T') for q_id in q_above]

    n_q_above = len(q_above)

    switch_to_bullet = 2

    my_text += (
        'In', year, ', concerning the Group net income, there',
        'is only one' if n_q_above == 1 else 'are ' + str(n_q_above) if n_q_above > 1 else 'is no',
        'quarter' + ('s' if n_q_above > 1 else ''), 'above 1 billion euros.',

        nlg.enum([
            q_id for q_id in q_above
        ],
            nb_elem_bullet=switch_to_bullet,
            begin_w='It is' if n_q_above < switch_to_bullet else 'The quarters are listed below:',
            end_w='.' if n_q_above < switch_to_bullet else ''
        )

    ) if lang == 'en' else (

        'En ce qui concerne le résultat net du groupe, on observe',
        'un seul' if n_q_above == 1 else str(n_q_above) if n_q_above > 1 else "qu'il n'y a aucun",
        'trimestre' + ('s' if n_q_above > 1 else ''), 'en', year, 'qui',
        "dépassent" if n_q_above > 1 else 'dépasse', "les 1 milliard d'euros.",

        nlg.enum([
            q_id for q_id in q_above_fr
        ],
            nb_elem_bullet=switch_to_bullet,
            begin_w="C'est le" if n_q_above < switch_to_bullet else 'Les différents trimestres sont les suivants :',
            end_w='.' if n_q_above < switch_to_bullet else ''
        )
    )

nlg.write_text(my_text)
lxml.html.open_in_browser(nlg.html)
