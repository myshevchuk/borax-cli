from borax import tagging


def test_keyword_scoring_requires_min_occurrences():
    text = "acid base acid base buffer"
    keywords = ["acid", "base", "equilibrium"]

    scores = tagging.score_keywords_in_text(text.lower(), keywords)
    # Compare case-insensitively
    found = {kw.lower() for kw, score in scores}
    assert "acid" in found
    assert "base" in found
    assert "equilibrium" not in found


def test_title_weight_boosts_keywords():
    text = "Organic chemistry handbook.\n\n" + " organic " * 2 + " inorganic "
    keywords = ["organic", "inorganic"]
    scores = tagging.score_keywords_in_text(text.lower(), keywords)
    # Ignore case when checking which keyword wins
    assert scores[0][0].lower() == "organic"
    assert scores[0][1] >= scores[1][1]
