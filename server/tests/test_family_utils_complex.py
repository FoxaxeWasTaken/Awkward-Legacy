from src.parsing.family_utils import split_family_header


def test_split_family_header_complex_with_mp_and_tags():
    header = "Smith Michael +2030-05-15 #mp St. Mary's Church,Boston,MA,USA Johnson Emily #occu Nurse 2032-08-22"
    husband, wife = split_family_header(header)
    assert husband == "Smith Michael"
    # Should pick wife tokens (first and last) right after the place and before the tag
    assert wife == "Johnson Emily"


def test_split_family_header_simple_plus():
    header = "Doe John + Roe Jane"
    husband, wife = split_family_header(header)
    assert husband == "Doe John"
    assert wife == "Roe Jane"
