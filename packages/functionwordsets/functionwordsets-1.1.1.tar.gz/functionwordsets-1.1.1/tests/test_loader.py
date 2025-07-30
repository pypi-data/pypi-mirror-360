import functionwordsets as fw

def test_loader_core():
    # Vérifie que tous les jeux de données sont disponibles
    ids = fw.available_ids()
    assert isinstance(ids, list) and "fr_21c" in ids

    # Test sur un jeu simple
    fr = fw.load("fr_21c")
    assert "ne" in fr.all                      # test de présence
    assert len(fr.all) > 100                   # taille minimale
    sub = fr.subset(["articles", "prepositions"])
    assert sub.issubset(fr.all) and sub        # sous-ensemble valide
