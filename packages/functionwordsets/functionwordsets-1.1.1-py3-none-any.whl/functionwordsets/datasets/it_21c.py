# Italian 21st-century function word lists by gramamtical nature

ARTICLES_DETERMINERS = frozenset([
    # articoli definiti / indeterminativi / partitivi
    "il", "lo", "l'", "la", "i", "gli", "le",
    "un", "uno", "una", "un'",
    "del", "dello", "dell'", "della", "dei", "degli", "delle",
    "al", "allo", "all'", "alla", "ai", "agli", "alle",
    # dimostrativi / interrogativi / quantificatori comuni
    "questo", "questa", "questi", "queste",
    "quel", "quello", "quell'", "quella", "quei", "quegli", "quelle",
    "qual", "quale", "quali",
    "ciascun", "ciascuno", "ciascuna",
    "ogni",
    "tutto", "tutta", "tutti", "tutte",
    "alcun", "alcuno", "alcuna", "alcuni", "alcune",
    "nessun", "nessuno", "nessuna",
    "altro", "altra", "altri", "altre",
    "diverso", "diversa", "diversi", "diverse",
    "parecchio", "parecchi", "parecchia", "parecchie",
    "molto", "molta", "molti", "molte",
    "poco", "poca", "pochi", "poche",
])

POSSESSIVE_DETERMINERS = frozenset([
    "mio", "mia", "miei", "mie",
    "tuo", "tua", "tuoi", "tue",
    "suo", "sua", "suoi", "sue",
    "nostro", "nostra", "nostri", "nostre",
    "vostro", "vostra", "vostri", "vostre",
    "loro",
])

PERSONAL_PRONOUNS = frozenset([
    "io", "tu", "lui", "lei", "egli", "ella", "esso", "essa", "essi", "esse",
    "noi", "voi", "loro",
    # clitici
    "mi", "ti", "si", "ci", "vi", "lo", "la", "li", "le", "gli", "ne",
    # tonici / riflessivi
    "me", "te", "sé", "lui", "lei", "noi", "voi", "loro",
])

POSSESSIVE_PRONOUNS = frozenset([
    "il mio", "la mia", "i miei", "le mie",
    "il tuo", "la tua", "i tuoi", "le tue",
    "il suo", "la sua", "i suoi", "le sue",
    "il nostro", "la nostra", "i nostri", "le nostre",
    "il vostro", "la vostra", "i vostri", "le vostre",
    "il loro", "la loro", "i loro", "le loro",
])

DEMONSTRATIVE_PRONOUNS = frozenset([
    "questo", "questa", "questi", "queste",
    "codesto", "codesta", "codesti", "codeste",
    "quello", "quella", "quelli", "quelle",
    "ciò", "costui", "costei", "costoro", "colui", "colei", "coloro",
])

INDEFINITE_PRONOUNS = frozenset([
    "qualcuno", "qualcuna", "qualcuni", "qualcune",
    "qualcosa",
    "ognuno", "ognuna", "ciascuno", "ciascuna",
    "nessuno", "nessuna", "niente", "nulla",
    "alcuno", "alcuna", "alcuni", "alcune",
    "tutto", "tutti", "tutte",
    "poco", "poca", "pochi", "poche",
    "parecchio", "parecchia", "parecchi", "parecchie",
    "altro", "altra", "altri", "altre",
    "chiunque", "altrove",
])

INTERROGATIVE_PRONOUNS = frozenset([
    "chi", "che", "che cosa", "cosa",
    "quale", "quali",
])

PREPOSITIONS = frozenset([
    # semplici
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "verso", "presso", "senza", "entro", "sopra", "sotto",
    "oltre", "durante", "mediante", "secondo", "circa", "riguardo",
    # articolate / locuzioni comuni (mantenute intere)
    "fino a", "davanti a", "dietro a", "insieme a", "accanto a",
    "invece di", "prima di", "dopo di", "grazie a", "a causa di",
    "per via di", "a favore di", "a fianco di", "lontano da",
    "vicino a", "attraverso", "intorno a",
])

COORD_CONJUNCTIONS = frozenset([
    "e", "o", "oppure", "ovvero", "né", "ma", "però", "bensì",
    "tuttavia", "anzi", "quindi", "dunque", "allora", "infatti",
])

SUBORD_CONJUNCTIONS = frozenset([
    "che", "se", "perché", "affinché", "poiché", "siccome",
    "benché", "sebbene", "quantunque",
    "quando", "mentre", "dopo che", "prima che", "finché",
    "dato che", "qualora", "purché", "a meno che", "come", "come se",
    "nel caso che", "fino a che",
])

ADVERBS = frozenset([
    "qui", "qua", "lì", "là", "laggiù", "lassù",
    "oggi", "ieri", "domani", "sempre", "spesso", "talvolta",
    "raramente", "mai", "già", "ancora", "presto", "tardi",
    "bene", "male", "meglio", "peggio",
    "molto", "troppo", "poco", "abbastanza", "quasi",
    "solo", "soltanto", "appena", "circa",
    "forse", "magari", "dunque", "quindi", "poi", "inoltre",
    "così", "infatti", "pure", "davvero", "veramente",
])

ADV_LOCUTIONS = frozenset([
    "subito", "adesso", "per esempio", "in effetti", "in realtà",
    "di solito", "d'altronde", "per lo meno", "almeno", "tutto sommato",
    "a dire il vero", "da un lato", "dall'altro lato", "allo stesso tempo",
    "nel frattempo", "dopo tutto", "all'improvviso", "di tanto in tanto",
    "ogni tanto", "prima o poi", "più o meno", "un po'", "a poco a poco",
    "via via", "mano a mano", "per sempre", "per ora", "di nuovo", "finora",
    "ormai", "al massimo", "al minimo",
])

NEGATIONS = frozenset([
    "non", "nessuno", "nessuna", "niente", "nulla", "mai",
    "neanche", "nemmeno", "neppure", "affatto", "punto", "mica",
    "senza", "né",
])

AUX_ESSERE = frozenset([
    "essere", "sono", "sei", "è", "siamo", "siete", "sono",
    "ero", "eri", "era", "eravamo", "eravate", "erano",
    "fui", "fosti", "fu", "fummo", "foste", "furono",
    "sarò", "sarai", "sarà", "saremo", "sarete", "saranno",
    "sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero",
    "sia", "sia", "siamo", "siate", "siano",
    "fossi", "fossi", "fosse", "fossimo", "foste", "fossero",
    "essendo", "stato",
])

AUX_AVERE = frozenset([
    "avere", "ho", "hai", "ha", "abbiamo", "avete", "hanno",
    "avevo", "avevi", "aveva", "avevamo", "avevate", "avevano",
    "ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero",
    "avrò", "avrai", "avrà", "avremo", "avrete", "avranno",
    "avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero",
    "abbia", "abbia", "abbiamo", "abbiate", "abbiano",
    "avessi", "avessi", "avesse", "avessimo", "aveste", "avessero",
    "avendo", "avuto",
])

MODAL_VERBS = frozenset([
    "potere", "posso", "puoi", "può", "possiamo", "potete", "possono",
    "potevo", "potrò", "potrei", "possa", "potessi",
    "dovere", "devo", "devi", "deve", "dobbiamo", "dovete", "devono",
    "dovevo", "dovrò", "dovrei", "debba", "dovessi",
    "volere", "voglio", "vuoi", "vuole", "vogliamo", "volete", "vogliono",
    "volevo", "vorrò", "vorrei", "voglia", "volessi",
    "sapere", "so", "sai", "sa", "sappiamo", "sapete", "sanno",
    "sapevo", "saprò", "saprei", "sappia", "sapessi",
])

categories = {
    "articles": sorted(ARTICLES_DETERMINERS),
    "poss_det": sorted(POSSESSIVE_DETERMINERS),
    "pers_pron": sorted(PERSONAL_PRONOUNS),
    "poss_pron": sorted(POSSESSIVE_PRONOUNS),
    "dem_pron": sorted(DEMONSTRATIVE_PRONOUNS),
    "indef_pron": sorted(INDEFINITE_PRONOUNS),
    "inter_pron": sorted(INTERROGATIVE_PRONOUNS),
    "prepositions": sorted(PREPOSITIONS),
    "coord_conj": sorted(COORD_CONJUNCTIONS),
    "subord_conj": sorted(SUBORD_CONJUNCTIONS),
    "adverbs": sorted(ADVERBS),
    "adv_locutions": sorted(ADV_LOCUTIONS),
    "negations": sorted(NEGATIONS),
    "aux_essere": sorted(AUX_ESSERE),
    "aux_avere": sorted(AUX_AVERE),
    "modals_full": sorted(MODAL_VERBS),
}

data = {
    "name": "Italian – 21st century",
    "language": "it",
    "period": "21c",
    "categories": categories,
}
