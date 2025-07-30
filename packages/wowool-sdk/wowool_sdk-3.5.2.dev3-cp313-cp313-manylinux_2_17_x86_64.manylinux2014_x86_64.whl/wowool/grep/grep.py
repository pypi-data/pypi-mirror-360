from wowool.diagnostic import Diagnostics
from wowool.grep.app_id import APP_ID
from wowool.native.core.engine import Engine, Component
from wowool.document.analysis.document import AnalysisDocument
from wowool.native.core import Domain
from wowool.annotation import Concept
import logging
from wowool.string import canonicalize
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)

logger = logging.getLogger(__name__)


def filter_grep_annotations(concept):
    return concept.uri == "GREP"


def summary(results):
    from collections import defaultdict

    freq = defaultdict(int)
    collocations = {}
    groups = defaultdict(lambda: defaultdict(int))
    for match in results:
        collocation_hash = ""
        freq[match["text"]] += 1
        for group in match["groups"]:
            collocation_hash += f"""{group["name"]}{group["text"]}"""
            groups[group["name"]][group["text"]] += 1

        if len(groups):
            if collocation_hash in collocations:
                collocations[collocation_hash][0] += 1
            else:
                collocations[collocation_hash] = [1, match]

    freq = sorted(freq.items(), key=lambda k_v: k_v[1], reverse=False)
    collocations = sorted(collocations.items(), key=lambda k_v: k_v[0], reverse=False)

    headers = ["cnt", "matches"]
    for key, match in collocations:
        for group in match[1]["groups"]:
            headers.append(group["name"])
        break

    summary_data = []
    summary_section = {
        "name": "match",
        "data": [{"count": v, "groups": [k]} for k, v in freq],
    }
    summary_data.append(summary_section)

    if len(headers) > 2:
        for name, data in groups.items():
            freq = sorted(data.items(), key=lambda k_v: k_v[1], reverse=False)
            summary_section = {
                "name": name,
                "data": [{"count": v, "groups": [k]} for k, v in freq],
            }
            summary_data.append(summary_section)

    columns = []
    for key, match in collocations:
        item = {
            "count": match[0],
            "groups": [],
        }
        for group in match[1]["groups"]:
            item["groups"].append(group["text"])
        columns.append(item)

    if columns:
        summary_section = {"name": "collocation", "data": columns}
        summary_data.append(summary_section)
    return summary_data


class Grep(Component):
    ID = APP_ID

    def __init__(self, expression: str, lemma: bool = False, engine: Engine | None = None):
        """
        Initialize the Grep application.

        :param expression: a wowoolian expression
        :type expression: str
        :param lemma: return the lemma instead of the canonical or literal
        :type lemma: bool
        """
        super(Grep, self).__init__(engine)
        self.expression = expression
        source = f"rule:{{ {expression} }} = GREP;"
        logger.debug(f"{source=}")
        self.domain = Domain(source=source, engine=self.engine)
        self.groups = [c for c in self.domain.concepts if c != "GREP"]
        self.lemma = lemma
        logger.debug(f"sub groups:{self.groups}")

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        :param document: The document we want to enrich with the semantic grep matches and aggregated results.
        :type document:  AnalysisDocument
        :return: The given document with the matches, summary of the matches and collocations if any. See the :ref:`json format <json_apps_grep>`
        """

        document = self.domain(document)
        api_results = []
        for sentence_index, sentence in enumerate(document.analysis):
            for concept in Concept.iter(sentence, filter_grep_annotations):
                canonical = canonicalize(concept, self.lemma)
                match = {
                    "text": canonical,
                    "groups": [],
                    "sentence_index": sentence_index,
                }
                pre_groups = {group: {"name": group, "text": ""} for group in self.groups}
                for child in Concept.iter(concept, lambda c: c.uri in self.groups):
                    if self.lemma:
                        child_canonical = child.lemma
                    else:
                        child_canonical = canonicalize(child)
                    pre_groups[child.uri]["text"] = child_canonical
                    if child_canonical != child.literal:
                        pre_groups[child.uri]["literal"] = child.literal

                match["groups"] = [v for k, v in pre_groups.items()]
                api_results.append(match)
        logger.debug(f"{api_results=}")
        api_summary = summary(api_results)
        logger.debug(f"{api_summary=}")
        for section in api_summary:
            logger.debug(f"- {section['name']}")
            for data in section["data"]:
                logger.debug(f"  - count: {data['count']}")
                logger.debug(f"  - groups :{data['groups']}")

        document.add_results(self.ID, {"matches": api_results, "summary": api_summary})
        return document
