DEEP_DICT = """
array unset ::env
set ::env(LAYERS_RC) [dict create]

# RC fit from OpenROAD
# https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/flow/platforms/gf180/setRC.tcl
dict set ::env(LAYERS_RC) "*" Metal2 res 2.25636E-04
dict set ::env(LAYERS_RC) "*" Metal2 cap 1.35357E-04
dict set ::env(LAYERS_RC) "*" Metal3 res 2.25636E-04
dict set ::env(LAYERS_RC) "*" Metal3 cap 1.46141E-04
dict set ::env(LAYERS_RC) "*" Metal4 res 2.25636E-04
dict set ::env(LAYERS_RC) "*" Metal4 cap 1.50688E-04
dict set ::env(LAYERS_RC) "*" Metal5 res 5.85545E-05
dict set ::env(LAYERS_RC) "*" Metal5 cap 1.55595E-04
"""


def test_get_var():
    from minitcl import Interpreter

    i = Interpreter()
    i.eval("set foo bar")
    i.eval("set fee(foo) fum")
    assert i.get_var("foo") == "bar"
    assert i.get_var("fee", "foo") == "fum"


def test_set_var():
    from minitcl import Interpreter

    i = Interpreter()
    i.set_var("egg", "salad")
    i.set_var("sources", "egg", "farm")
    i.eval("set dish potato_$egg")
    i.eval("set location $sources(egg)")
    assert i.get_var("dish") == "potato_salad"
    assert i.get_var("location") == "farm"


def test_list_parse():
    from minitcl import Interpreter

    i = Interpreter()
    i.eval(DEEP_DICT)
    layers_raw = i.get_var("env", "LAYERS_RC")
    layers = i.parse_list(layers_raw)
    # as a dictionary, the tcl parser must return the top-level key and a single
    # value encoding the subdictionary
    assert layers == [
        "*",
        (
            "Metal2 {res 2.25636E-04 cap 1.35357E-04} "
            "Metal3 {res 2.25636E-04 cap 1.46141E-04} "
            "Metal4 {res 2.25636E-04 cap 1.50688E-04} "
            "Metal5 {res 5.85545E-05 cap 1.55595E-04}"
        ),
    ], "list_parse returned unexpected value"


def test_dict_parse():
    from minitcl import Interpreter

    i = Interpreter()
    i.eval(DEEP_DICT)
    i.eval("set env_dict [array get ::env]")
    raw_list = i.get_var("env_dict")
    parsed = i.parse_dict(raw_list)
    layers_rc = {
        corner: {layer: i.parse_dict(v2) for layer, v2 in i.parse_dict(v).items()}
        for corner, v in i.parse_dict(parsed["LAYERS_RC"]).items()
    }
    assert layers_rc == {
        "*": {
            "Metal2": {"res": "2.25636E-04", "cap": "1.35357E-04"},
            "Metal3": {"res": "2.25636E-04", "cap": "1.46141E-04"},
            "Metal4": {"res": "2.25636E-04", "cap": "1.50688E-04"},
            "Metal5": {"res": "5.85545E-05", "cap": "1.55595E-04"},
        }
    }, "recursive dict_parse returned unexpected value"
