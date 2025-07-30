# Ancient Greek – Classical Attic (5th-4th c. BCE)

ARTICLES_DETERMINERS = frozenset([
    "ὁ", "ἡ", "τό",
    "οἱ", "αἱ", "τά",
    # Demonstratives used as determiners
    "οὗτος", "αὕτη", "τοῦτο",
    "ἐκεῖνος", "ἐκείνη", "ἐκεῖνο",
    "ὅδε", "ἥδε", "τόδε",
    # Quantifiers / distributives often mapped to adjectival slots
    "πᾶς", "πᾶσα", "πᾶν",
    "ἅπας", "ἅπασα", "ἅπαν",
    "ἕκαστος", "ἑκάστη", "ἕκαστον",
    "τις", "τι",                     # enclitic indef. when adjectival
])

POSSESSIVE_DETERMINERS = frozenset([
    "ἐμός", "ἐμή", "ἐμόν",
    "σός", "σή", "σόν",
    "ἡμέτερος", "ἡμετέρα", "ἡμέτερον",
    "ὑμέτερος", "ὑμετέρα", "ὑμέτερον",
    "σφετέρος", "σφετέρα", "σφετέρον"   # Homeric/poetic but sometimes cited
])

PERSONAL_PRONOUNS = frozenset([
    "ἐγώ", "σύ", "ἡμεῖς", "ὑμεῖς",
    "αὐτός", "αὐτή", "αὐτό",          # 3rd-pers intensive / personal
    # enclitic object forms (most corpora tag separately)
    "με", "σέ", "μοι", "μοι", "σοι", "σοί",
    "ὑμᾶς", "ὑμῶν", "ἡμᾶς", "ἡμῶν",
    "οἱ", "ἑ", "σφίσι", "τοῖς", "ταις",  # datives / reflexive older forms
])

POSSESSIVE_PRONOUNS = POSSESSIVE_DETERMINERS  # forms identical in Greek

DEMONSTRATIVE_PRONOUNS = frozenset([
    "οὗτος", "αὕτη", "τοῦτο",
    "ἐκεῖνος", "ἐκείνη", "ἐκεῖνο",
    "ὅδε", "ἥδε", "τόδε",
])

INDEFINITE_PRONOUNS = frozenset([
    "τις", "τι",
    "ἄλλος", "ἄλλη", "ἄλλο",
    "οὐδείς", "οὐδεμία", "οὐδέν",
    "μηδείς", "μηδεμία", "μηδέν",
    "ἕτερος", "ἑτέρα", "ἕτερον",
    "πλείων", "πλεῖον",
])

INTERROGATIVE_PRONOUNS = frozenset([
    "τίς", "τί",
    "ποῖος", "ποία", "ποῖον",
    "πόσος", "πόση", "πόσον",
    "ποῦ", "πόθεν", "πότε", "πῶς", "διὰ τί"
])

PREPOSITIONS = frozenset([
    "ἀνά", "ἀντί", "ἀπό", "διά", "εἰς", "ἐκ", "ἐν", "ἐπί",
    "κατά", "μετά", "παρά", "περί", "πρό", "πρός", "σύν", "ὑπέρ", "ὑπό",
    # less common / poetic / compound
    "ἄνευ", "ἐναντίον", "χωρίς"
])

COORD_CONJUNCTIONS = frozenset([
    "καί", "δέ", "ἀλλά", "ἀλλ’", "μέν", "οὐδέ", "μηδέ", "ἤ",
    "οὖν", "τοίνυν", "γάρ"
])

SUBORD_CONJUNCTIONS = frozenset([
    "ὅτι", "ὡς", "ἐπεί", "ἐπειδή", "εἴπερ",
    "ἐάν", "ἄν", "εἰ", "ἵνα", "ὅπως", "ὅταν",
    "ἐπεί", "πρίν", "πρίν ἤ", "ἕως", "ἕως ἂν",
    "ὅτε", "ὅταν", "ὁπότε", "ὃθεν", "οἷ", "ἐπείδη",
    "μή", "ἄχρι", "ἕως"
])

ADVERBS = frozenset([
    # place
    "ἐνθάδε", "ἐνταῦθα", "ἐκεῖ", "ἔνθα", "αὐτοῦ",
    # time
    "νῦν", "ἤδη", "πάλιν", "πρίν", "αὖθις", "τότε",
    # frequency/degree
    "πολλάκις", "σφόδρα", "μάλα", "ἥκιστα", "ἔτι",
    # manner / discourse
    "οὕτως", "οὕτω", "οὗτως", "οὗτω", "ὡσαύτως", "μάλιστα",
    "μικρόν", "σχεδόν", "ἄρα", "δή", "γέ", "που", "ὡς",
    # negatives & affirmatives
    "οὐ", "οὐκ", "οὐχ", "οὐδέ", "μή", "μηδέ", "οὐδαμῶς",
    "ναί", "ἦ", "ἔτι"
])

ADV_LOCUTIONS = frozenset([
    "ἐξ οὗ", "μετὰ ταῦτα", "διὰ τοῦτο", "ἐκ τούτου", "ἅμα τούτῳ",
    "ὅμως", "οὐ μὴν ἀλλά", "καθ’ ὅσον", "ἐφ’ ᾧτε", "ἐκ τούτου δὴ"
])

NEGATIONS = frozenset([
    "οὐ", "οὐκ", "οὐχ", "μή", "μηδέ", "οὐδέ", "οὐδαμῶς", "μηδαμῶς"
])

AUX_EIMI = frozenset([
    "εἰμί", "εἶ", "ἐστίν", "ἐσμέν", "ἐστέ", "εἰσίν",
    "ἦν", "ἦς", "ἦν", "ἦμεν", "ἦτε", "ἦσαν",
    "ἔσομαι", "ἔσῃ", "ἔσται", "ἐσόμεθα", "ἔσεσθε", "ἔσσονται",
    "γεγενημένος"  # perf. participle often used as auxiliary
])

MODAL_VERBS = frozenset([
    "δύναμαι", "δύνῃ", "δύναιτο", "ἐδύνατο", "δυνατός",
    "βούλομαι", "βούλει", "βούλεται", "βουλόμεθα", "βούλεσθε", "βούλονται",
    "χρή", "χρὴ", "χρήν", "δεῖ", "ἔδει", "δεήσει",
    "οἶδα", "εἴσομαι", "ἔγνων",  # know / can idiomatically
    "πρέπει", "θέλω"  # θέλω rare Attic but common later
])

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
    "aux_eimi": AUX_EIMI,
    "modals_full": MODAL_VERBS
}
