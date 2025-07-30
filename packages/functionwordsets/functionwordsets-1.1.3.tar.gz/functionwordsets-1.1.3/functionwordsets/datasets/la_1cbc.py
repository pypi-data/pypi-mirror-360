ARTICLES_DETERMINERS = sorted({
    # Latin has no articles; set of pronominal / determinative adjectives
    "hic", "haec", "hoc",
    "ille", "illa", "illud",
    "iste", "ista", "istud",
    "is", "ea", "id",
    "aliqui", "aliqua", "aliquod",
    "quidam", "quaedam", "quoddam",
    "quicumque", "quaecumque", "quodcumque",
    "omnis", "omne", "omnes",
    "totus", "tota", "totum",
    "unus", "una", "unum",
    "alter", "altera", "alterum",
    "nullus", "nulla", "nullum",
    "solus", "sola", "solum",
    "uterque", "utraque", "utrumque",
    "alius", "alia", "aliud",
    "singuli", "singulae", "singula"
})

POSSESSIVE_DETERMINERS = sorted({
    "meus", "mea", "meum",
    "tuus", "tua", "tuum",
    "suus", "sua", "suum",
    "noster", "nostra", "nostrum",
    "vester", "vestra", "vestrum"
})

PERSONAL_PRONOUNS = sorted({
    "ego", "tu", "nos", "vos",
    "is", "ea", "id",
    "se"
})

POSSESSIVE_PRONOUNS = POSSESSIVE_DETERMINERS  # identical word-forms

DEMONSTRATIVE_PRONOUNS = sorted({
    "hic", "haec", "hoc",
    "ille", "illa", "illud",
    "iste", "ista", "istud",
    "is", "ea", "id"
})

INDEFINITE_PRONOUNS = sorted({
    "aliquis", "aliquid",
    "quis", "quid",
    "quisquam", "quidquam",
    "quicumque", "quaecumque", "quodcumque",
    "quidam", "quaedam", "quiddam",
    "quispiam", "quidpiam",
    "nemo", "nihil",
    "nullus", "nulla", "nullum",
    "alter", "altera", "alterum",
    "uter", "utra", "utrum"
})

INTERROGATIVE_PRONOUNS = sorted({
    "quis", "quid",
    "qui", "quae", "quod",
    "uter", "utra", "utrum",
    "qualis", "quantus", "quot"
})

PREPOSITIONS = sorted({
    "a", "ab", "abs", "ad", "ante", "apud", "circum", "cis",
    "contra", "cum", "de", "ex", "e", "extra",
    "in", "infra", "inter", "intra", "iuxta",
    "ob", "per", "post", "prae", "pro", "propter",
    "sine", "sub", "super", "supra", "trans", "ultra",
    "subter", "penes", "praeter"
})

COORD_CONJUNCTIONS = sorted({
    "et", "atque", "ac",
    "aut", "vel", "ve",
    "nec", "neque",
    "sed", "verum", "vero", "autem",
    "tamen", "itaque", "quoque"
})

SUBORD_CONJUNCTIONS = sorted({
    "quod", "quia", "cum", "ut", "dum",
    "si", "nisi", "ne", "ut ne", "dum ne",
    "quamquam", "etsi", "tametsi",
    "postquam", "antequam", "ubi", "quando", "quoniam",
    "donec", "utrum", "siquidem"
})

ADVERBS = sorted({
    "hic", "ibi", "illic", "inde", "hinc", "eo", "usque", "istuc",
    "hodie", "heri", "cras",
    "nunc", "statim", "mox", "iam", "iamdudum", "sero", "tandem",
    "saepe", "numquam", "nunquam", "raro", "crebro",
    "bene", "male",
    "magis", "minus", "maxime", "minime",
    "multum", "parum",
    "tam", "quam",
    "ita", "sic", "item",
    "etiam", "quoque", "quidem", "tamen", "igitur", "ergo", "enim",
    "forte", "certe", "vix", "haud",
    "non", "ne",
})

ADV_LOCUTIONS = sorted({
    "post hoc", "deinde", "praeterea", "interea", "ad hoc",
    "quam ob rem", "eo loco", "ex hoc", "proinde", "quapropter",
    "ita vero", "si quidem", "tamquam", "ut ita dicam",
    "ex quo", "hac de causa"
})

NEGATIONS = sorted({
    "non", "haud", "ne", "nec", "neque", "neu"
})

AUX_ESSE = sorted({
    "esse", "sum", "es", "est", "sumus", "estis", "sunt",
    "eram", "eras", "erat", "eramus", "eratis", "erant",
    "ero", "eris", "erit", "erimus", "eritis", "erunt",
    "fui", "fuisti", "fuit", "fuimus", "fuistis", "fuerunt",
    "forem", "fores", "foret", "foremus", "foretis", "forent"  
})

MODAL_VERBS = sorted({
    "posse", "possum", "potes", "potest", "possumus", "potestis", "possunt",
    "poteram", "poteras", "poterat", "poteramus", "poteratis", "poterant",
    "potero", "poteris", "poterit",
    "velle", "volo", "vis", "vult", "volumus", "vultis", "volunt",
    "nolle", "nolo", "non vis", "non vult", "nolumus", "non vultis", "nolunt",
    "malle", "malo", "mavis", "mavult", "malumus", "mavultis", "malunt",
    "debere", "debeo", "debes", "debet", "debemus", "debetis", "debent",
    "oportet", "licet", "fas"
})

categories = {
    "articles": ARTICLES_DETERMINERS,
    "poss_det": POSSESSIVE_DETERMINERS,
    "pers_pron": PERSONAL_PRONOUNS,
    "poss_pron": POSSESSIVE_PRONOUNS,
    "dem_pron": DEMONSTRATIVE_PRONOUNS,
    "indef_pron": INDEFINITE_PRONOUNS,
    "inter_pron": INTERROGATIVE_PRONOUNS,
    "prepositions": PREPOSITIONS,
    "coord_conj": COORD_CONJUNCTIONS,
    "subord_conj": SUBORD_CONJUNCTIONS,
    "adverbs": ADVERBS,
    "adv_locutions": ADV_LOCUTIONS,
    "negations": NEGATIONS,
    "aux_esse": AUX_ESSE,
    "modals_full": MODAL_VERBS
}

data = {
    "name": "Classical Latin – 1st c. BCE (enriched)",
    "language": "la",
    "period": "1cBC",
    "categories": categories
}
