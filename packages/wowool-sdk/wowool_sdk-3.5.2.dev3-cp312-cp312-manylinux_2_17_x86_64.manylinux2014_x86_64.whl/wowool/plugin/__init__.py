import sys
import os
from pathlib import Path
import json
from wowool.string import *  # noqa
from wowool.string import initial_caps, camelize
import traceback
import logging

logger = logging.getLogger(__name__)

verbose = True if "WOWOOL_LOG_LEVEL" in os.environ and "plugin" in os.environ["WOWOOL_LOG_LEVEL"] else False

# need to add the location of the plugin.
if "WOWOOL_ROOT" not in os.environ:
    wowool_libs = Path(__file__).parent.parent / "package" / "lib"
else:
    wowool_libs = Path(os.path.expanduser(os.path.expandvars(str("${WOWOOL_ROOT}/lib"))))

assert wowool_libs.exists(), "Path of the library does not exist. {wowool_libs}"
sys.path.insert(0, str(wowool_libs.resolve()))
import wowool.package.lib.wowool_plugin as wowool_plugin  # noqa E402


def query(q, epr, f="application/json"):
    import sys
    import requests

    try:
        params = {"query": q}
        resp = requests.get(epr, params=params, headers={"Accept": f})
        return resp.text
    except Exception as e:
        print(e, file=sys.stdout)
        raise


def get_dbpedia_attribute(literal, key):
    literal = literal.replace(" ", "_")
    sparql_query = f"""
prefix dbpedia: <http://dbpedia.org/resource/>
prefix dbp: <http://dbpedia.org/ontology/>

select * where {{
        dbpedia:{literal}
                dbp:{key} ?{key} .

}}
"""
    try:
        print(sparql_query)
        response = json.loads(query(sparql_query, "http://dbpedia.org/sparql"))
        value = response["results"]["bindings"][0][key]["value"]
        if value.startswith("http://dbpedia.org/resource/"):
            return value[len("http://dbpedia.org/resource/") :]
        return value
    except KeyboardInterrupt:
        raise
    except Exception as ex:
        print("get_dbpedia_attribute:", ex)
        return None


def get_concept_base_attribute(literal, language, key=None):
    try:
        from wowool.native.concept_base import get_info

        retval = get_info(literal, key, language)
        if isinstance(retval, list):
            return retval[0]
        else:
            return retval
    except KeyboardInterrupt:
        exit(-1)
    except Exception as ex:
        print("concept_base:attribute:", ex)
    return None


def resolve_formated_attribute(ud, fvalue):
    try:
        match = wowool_plugin.match_info()

        # !!! do not remove this unused variables !!!
        sentence = match.sentence()  # noqa
        capture = match.capture()  # noqa
        rule = match.rule()  # noqa
        resolved_value = eval('f"""' + fvalue + '"""')
        if "None" in resolved_value:
            return ""
        return resolved_value
    except KeyboardInterrupt:
        exit(-1)
    except Exception as ex:
        if not str(ex).startswith("'NoneType' object has no attribute"):
            print(f"Warning:wowool:f-string:{fvalue} {ex}", file=sys.stderr)
    return ""


def is_descriptor(concept):
    return concept.uri == "Descriptor"

    # "english": [("sd", "short description"), ("sd", "ambiguous description"), ("key_prefix", ["concept_base"]), ("keys", True)],


# concept_base_descriptors
ibdesc = {
    "danish": [
        ("sd", "short description"),
        ("key_prefix", ["infoboks", "concept_base"]),
    ],
    "dutch": [("key_prefix", ["concept_base"]), ("keys", True)],
    "english": [
        ("sd", "short description"),
        ("sd", "ambiguous description"),
        ("key_prefix", ["concept_base"]),
        ("keys", True),
    ],
    "french": [("key_prefix", ["concept_base"]), ("keys", True)],
    "german": [("key_prefix", ["concept_base"]), ("keys", True)],
    "italian": [("key_prefix", ["concept_base"]), ("keys", True)],
    "portuguese": [("key_prefix", ["concept_base"]), ("keys", True)],
    "norwegian": [("key_prefix", ["infoboks"]), ("keys", True)],
    "spanish": [("key_prefix", ["ficha de", "ficha del", "ficha"]), ("keys", True)],
    "swedish": [("key_prefix", ["infoboks"]), ("keys", True)],
}


def add_descriptions(item, doc, capture, literal, language):
    from wowool.annotation import Concept
    from wowool.native.concept_base import update_concept

    found = False
    for concept in Concept.iter(doc, is_descriptor):
        if "type" in concept.attributes:
            concept_type = camelize(concept.attributes["type"][0])
            # print("is as : ", concept_type)
            attributes = concept.attributes
            del attributes["type"]
            attributes["descriptor"] = concept.lemma
            attributes["source"] = item.source

            update_concept(item.source, literal, language, concept_type, attributes)
            known_thing = capture.add_concept(concept_type)
            known_thing.add_attribute("source", item.source)
            known_thing.add_attribute("descriptor", concept.lemma)
            found = True
    return found


def call_test(ud):
    print(f"{__name__}: hello")


# Do not remove this functions they are used to trigger the python function calls
# from the wow sources ex: rule: { ... } = ::python::resolve_date
from .date_parser import set_document_date  # noqa
from .date_parser import resolve_date  # noqa


# used to init a document and load on demand.
# ! Do not remove this function, feel free to add more stuff :-)
def open_doc(ud):
    pass


# ! Do not remove this function
# ! it's used to trigger the python initialization.
def warmup():
    pass


def attribute_to_concept(ud):
    try:
        match = wowool_plugin.match_info()
        capture = match.capture()
        if capture.concept:
            concept_theme = capture.Theme
            uri_name = capture.concept

            attributes = concept_theme.attributes()
            for att in attributes:
                if att.name() == uri_name:
                    concept_theme.add_concept(initial_caps(att.value()).replace(" ", "_"))
            capture.remove()
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        print("plugin:attribute_to_concept:", ex, file=sys.stderr)
