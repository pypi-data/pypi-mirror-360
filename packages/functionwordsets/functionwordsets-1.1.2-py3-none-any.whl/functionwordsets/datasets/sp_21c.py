# Spanish 21st-century function word sets by grammatical nature.

ARTICLES_DETERMINERS = frozenset([
    "el", "la", "los", "las", "lo",
    "un", "una", "unos", "unas",
    "al", "del",
    "este", "esta", "estos", "estas",
    "ese", "esa", "esos", "esas",
    "aquel", "aquella", "aquellos", "aquellas",
    "cada", "todo", "toda", "todos", "todas",
    "algún", "alguna", "algunos", "algunas",
    "ningún", "ninguna",
    "otro", "otra", "otros", "otras",
    "cierto", "cierta", "ciertos", "ciertas",
    "varios", "varias", "mucho", "mucha", "muchos", "muchas",
    "poco", "poca", "pocos", "pocas",
])

POSSESSIVE_DETERMINERS = frozenset([
    "mi", "mis",
    "tu", "tus",
    "su", "sus",
    "nuestro", "nuestra", "nuestros", "nuestras",
    "vuestro", "vuestra", "vuestros", "vuestras",
])

PERSONAL_PRONOUNS = frozenset([
    "yo", "tú", "vos", "usted", "él", "ella",
    "nosotros", "nosotras", "vosotros", "vosotras", "ustedes",
    "ellos", "ellas",
    # clíticos
    "me", "te", "se", "nos", "os", "lo", "la", "los", "las", "le", "les",
    # tónicos
    "mí", "ti", "sí",
])

POSSESSIVE_PRONOUNS = frozenset([
    "mío", "mía", "míos", "mías",
    "tuyo", "tuya", "tuyos", "tuyas",
    "suyo", "suya", "suyos", "suyas",
    "nuestro", "nuestra", "nuestros", "nuestras",
    "vuestro", "vuestra", "vuestros", "vuestras",
])

DEMONSTRATIVE_PRONOUNS = frozenset([
    "este", "esta", "estos", "estas",
    "ese", "esa", "esos", "esas",
    "aquel", "aquella", "aquellos", "aquellas",
    "esto", "eso", "aquello",
])

INDEFINITE_PRONOUNS = frozenset([
    "alguien", "nadie",
    "algo", "nada",
    "alguno", "alguna", "algunos", "algunas",
    "ninguno", "ninguna",
    "cualquiera", "cualesquiera",
    "todo", "toda", "todos", "todas",
    "mucho", "mucha", "muchos", "muchas",
    "poco", "poca", "pocos", "pocas",
    "varios", "varias",
    "demás", "otro", "otros", "otra", "otras",
    "bastante", "demasiado", "menos",
])

INTERROGATIVE_PRONOUNS = frozenset([
    "quién", "quiénes",
    "qué",
    "cuál", "cuáles",
    "cuánto", "cuánta", "cuántos", "cuántas",
    "dónde", "adónde",
    "cuándo",
    "cómo",
    "por qué",
])

PREPOSITIONS = frozenset([
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para",
    "por", "según", "sin", "so", "sobre", "tras", "versus", "vía",
    # compuestas frecuentes
    "junto a", "frente a", "cerca de", "lejos de", "debajo de",
    "encima de", "dentro de", "fuera de", "delante de", "alrededor de",
    "en cuanto a", "respecto a",
])

COORD_CONJUNCTIONS = frozenset([
    "y", "e", "o", "u", "ni", "pero", "mas", "sino", "que",
])

SUBORD_CONJUNCTIONS = frozenset([
    "que", "si", "porque", "aunque", "como",
    "cuando", "mientras", "donde", "puesto que", "ya que",
    "tan pronto como", "apenas", "hasta que", "antes de que", "después de que",
    "para que", "a fin de que", "con tal que", "a menos que", "sin que",
    "dado que", "en cuanto", "de modo que", "así que",
])

ADVERBS = frozenset([
    # lugar
    "aquí", "acá", "ahí", "allí", "allá",
    "arriba", "abajo", "cerca", "lejos", "dentro", "fuera",
    # tiempo
    "ahora", "ayer", "hoy", "mañana", "siempre", "nunca", "jamás",
    "ya", "todavía", "aún", "pronto", "tarde",
    # modo / cantidad
    "bien", "mal", "mejor", "peor",
    "muy", "más", "menos", "demasiado", "bastante", "casi",
    "apenas", "mucho", "poco", "tanto", "tan",
    # afirmación / negación / duda
    "sí", "claro", "quizá", "quizás", "tal vez", "probablemente",
    "no",
    # enlace / discurso
    "entonces", "luego", "después", "antes", "además",
    "también", "tampoco", "sin embargo", "no obstante", "por lo tanto",
    "así", "pues",
])

ADV_LOCUTIONS = frozenset([
    "por ejemplo", "en cambio", "sin embargo", "por lo tanto",
    "de hecho", "en realidad", "por supuesto", "claro que sí",
    "a menudo", "de nuevo", "de vez en cuando", "cada tanto",
    "de vez en vez", "de pronto", "de repente", "a veces",
    "al final", "al principio", "a continuación",
    "por fin", "más o menos", "un poco", "poco a poco",
    "al mismo tiempo", "mientras tanto", "por ahora", "hasta ahora",
    "ahora mismo", "enseguida", "de inmediato",
    "sobre todo", "ante todo",
    "en general", "en particular",
])

NEGATIONS = frozenset([
    "no", "nunca", "jamás", "nada", "nadie",
    "ninguno", "ninguna", "ningún",
    "ni",
    "tampoco",
    "sin",
])

AUX_SER = frozenset([
    "ser", "soy", "eres", "es", "somos", "sois", "son",
    "era", "eras", "éramos", "erais", "eran",
    "fui", "fuiste", "fue", "fuimos", "fuisteis", "fueron",
    "seré", "serás", "será", "seremos", "seréis", "serán",
    "sería", "serías", "seríamos", "seríais", "serían",
    "siendo", "sido",
])

AUX_ESTAR = frozenset([
    "estar", "estoy", "estás", "está", "estamos", "estáis", "están",
    "estaba", "estabas", "estábamos", "estabais", "estaban",
    "estuve", "estuviste", "estuvo", "estuvimos", "estuvisteis", "estuvieron",
    "estaré", "estarás", "estará", "estaremos", "estaréis", "estarán",
    "estaría", "estarías", "estaríamos", "estaríais", "estarían",
    "estando", "estado",
])

AUX_HABER = frozenset([
    "haber", "he", "has", "ha", "hemos", "habéis", "han",
    "había", "habías", "habíamos", "habíais", "habían",
    "hube", "hubiste", "hubo", "hubimos", "hubisteis", "hubieron",
    "habré", "habrás", "habrá", "habremos", "habréis", "habrán",
    "habría", "habrías", "habríamos", "habríais", "habrían",
    "habiendo", "habido",
])

MODAL_VERBS = frozenset([
    # poder
    "poder", "puedo", "puedes", "puede", "podemos", "podéis", "pueden",
    # deber
    "deber", "debo", "debes", "debe", "debemos", "debéis", "deben",
    # querer
    "querer", "quiero", "quieres", "quiere", "queremos", "queréis", "quieren",
    # saber (modal de habilidad)
    "saber", "sé", "sabes", "sabe", "sabemos", "sabéis", "saben",
    # soler
    "soler", "suelo", "sueles", "suele", "solemos", "soléis", "suelen",
    # ir (perífrasis ir a + inf.)
    "ir", "voy", "vas", "va", "vamos", "vais", "van",
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
    "aux_ser": sorted(AUX_SER),
    "aux_estar": sorted(AUX_ESTAR),
    "aux_haber": sorted(AUX_HABER),
    "modals_full": sorted(MODAL_VERBS),
}

data = {
    "name": "Spanish – 21st century",
    "language": "es",
    "period": "21c",
    "categories": categories,
}
