import functionwords as fw

def test_loader_core():
    # 1. on trouve le jeu fr_21c
    ids = fw.available_ids()
    assert "fr_21c" in ids and ids, "fr_21c should be listed"

    fr = fw.load("fr_21c")
    # 2. taille approximative connue
    assert 580 < len(fr.all) < 700
    # 3. contrôle de présence
    assert "ne" in fr.all
    # 4. subset sur 2 catégories
    sub = fr.subset(["articles", "prepositions"])
    assert sub                               # not empty
    assert sub.issubset(fr.all)
