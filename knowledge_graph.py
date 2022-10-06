from typing import Dict, List, Union


KNOWLEDGE_GRAPH = {
    "weight": 1.0,
    "name": "harry potter",
    "children": [
        {
            "weight": 0.3333,
            "name": "houses",
            "children": [
                {"weight": 0.25, "name": "gryffindor", "children": []},
                {"weight": 0.25, "name": "huffelpuff", "children": []},
                {"weight": 0.25, "name": "ravenclaw", "children": []},
                {"weight": 0.25, "name": "slytherin", "children": []},
            ],
        },
        {
            "weight": 0.3333,
            "name": "media",
            "children": [],
        },
        {
            "weight": 0.3333,
            "name": "main characters",
            "children": [],
        },
    ],
}


def leaf_concepts(concept_tree: Dict[str, Union[str, float, List[any]]]) -> List[str]:
    """Return leaf node names of knowledge web"""
    if not concept_tree["children"]:
        return [concept_tree["name"]]

    child_leafs = []

    for child in concept_tree["children"]:
        child_leafs.extend(leaf_concepts(child))

    return child_leafs
