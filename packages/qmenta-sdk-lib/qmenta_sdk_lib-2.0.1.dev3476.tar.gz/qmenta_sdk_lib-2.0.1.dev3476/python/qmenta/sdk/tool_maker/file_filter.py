from typing import List, Union

from .modalities import Modality, Tag

Property_type = Union[Modality, List[Modality], List[str], str, int]


def make_tag(p: Union[List[Tag]]) -> str:
    """
    Prepends the tag t' to each string provided as argument or in the list.
    If the tag starts with "!" then the prefix is "!t'" instead.

    Parameters
    ----------
    p: tag or list of tags.

    Returns
    -------
    str
    """
    return ",".join(
        [
            f"t'{tag}'" if not tag.startswith("!") else f"!t'{tag[1:]}'"
            for tag in p
        ]
    )


def make_modality(p: Union[List[Modality], Modality]) -> str:
    return (
        "|".join([f"m'{mod.value}'" for mod in p])
        if (isinstance(p, list) and len(p) > 1)
        else f"m'{p.value}'"
    )


def make_regex(p: str) -> str:
    return f"r'{p}'"


def process_element(seq: Property_type) -> str:
    if isinstance(seq, list) and len(seq) and isinstance(seq[0], Tag):
        return make_tag(seq)
    elif isinstance(seq, Tag):
        return make_tag([seq])
    elif (isinstance(seq, Modality) and seq.value != "None") or (
        isinstance(seq, list) and len(seq) > 1 and isinstance(seq[0], Modality)
    ):
        return make_modality(seq)
    elif isinstance(seq, list) and len(seq) and isinstance(seq[0], Modality):
        return make_modality(seq[0])
    elif isinstance(seq, list) and len(seq) and isinstance(seq[0], list):
        list_output = list()
        for s in seq:
            list_output.append([process_element(i) for i in s])
        nlist = list()
        for el in list_output:
            el2 = "(" + ",".join(el) + ")"
            nlist.append(el2)
        return "|".join(nlist)
    elif isinstance(seq, str):
        return make_regex(seq)


def parse_property(filters: List[Property_type]) -> str:
    parsed = list()
    if not filters:
        return make_regex(".*")
    for _filter in filters:
        pf = process_element(_filter)
        (
            parsed.append("(" + pf + ")")
            if ("," in pf or "|" in pf) and not isinstance(_filter, str)
            else parsed.append(pf)
        )
    return (
        "(" + ",".join(parsed) + ")" if len(filters) > 1 else ",".join(parsed)
    )


def parse_file_filter_property(conditions: List) -> str:
    parsed = [parse_property(condition[0]) for condition in conditions]
    return parsed[0] if len(parsed) == 1 else ("(" + "|".join(parsed) + ")")


class ConditionForFilter(object):
    def __init__(
        self,
        file_filter_condition_name: str,
        condition: List[tuple],
        min_files: int = 1,
        max_files: Union[int, str] = 1,
    ):
        self.id = file_filter_condition_name
        self.condition = condition
        self.property = parse_file_filter_property(condition)
        assert min_files <= max_files if max_files != "*" else True
        self.number_files = f"[{min_files},{max_files}]"

    def __str__(self):
        return f"{self.number_files}({self.property})"
