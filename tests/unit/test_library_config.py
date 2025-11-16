from borax.library_config import merge_vocab


def test_merge_vocab_unions_lists_and_merges_maps():
    default = {
        "Document_Types": ["Textbook", "Monograph"],
        "Levels": ["Introductory", "Graduate"],
        "Disciplines": {"General": {"Subfields": {"Reference": []}}},
        "Keywords": {"Core": ["theory", "methods"]},
    }
    custom = {
        "Document_Types": ["Thesis"],
        "Levels": ["Professional"],
        "Disciplines": {"Chemistry": {"Subfields": {"Organic": ["Synthesis"]}}},
        "Keywords": {"Core": ["simulation"], "Extra": ["appendix"]},
    }

    merged = merge_vocab(default, custom)

    assert set(merged["Document_Types"]) == {"Textbook", "Monograph", "Thesis"}
    assert set(merged["Levels"]) == {"Introductory", "Graduate", "Professional"}
    assert "General" in merged["Disciplines"]
    assert "Chemistry" in merged["Disciplines"]
    assert merged["Disciplines"]["Chemistry"]["Subfields"]["Organic"] == ["Synthesis"]
    assert set(merged["Keywords"]["Core"]) == {"theory", "methods", "simulation"}
    assert set(merged["Keywords"]["Extra"]) == {"appendix"}
