import os
import random
import json

from typing import Dict, List, Union

KNOWLEDGE_WEB = {
    "weight": 1.0,
    "name": "harry potter",
    "children": [
        {
            "weight": 0.33,
            "name": "houses",
            "children": [
                {"weight": 0.25, "name": "gryffindor", "children": []},
                {"weight": 0.25, "name": "huffelpuff", "children": []},
                {"weight": 0.25, "name": "ravenclaw", "children": []},
                {"weight": 0.25, "name": "slytherin", "children": []},
            ],
        },
        {
            "weight": 0.33,
            "name": "media",
            "children": [],
        },
        {
            "weight": 0.33,
            "name": "main characters",
            "children": [],
        },
    ],
}

# "What is the color/animal/trait for Y"


def score_a_question(
    question: Dict[str, Union[str, List[str], Dict[str, float]]], answer: str
) -> Dict[str, float]:
    """Evaluates evidence towards a concept. Empty evidence suggests 0 evidence"""
    if answer == question["correct"]:
        return question["weights"]
    return {}


def depth_first_support(
    concepts: Dict[str, Union[str, float, List[any]]],
    collected_supports: Dict[str, float],
    questions: List[Dict[str, Union[str, float, List[any]]]],
) -> Dict[str, Union[str, float, List[any]]]:

    concept, children = concepts["name"], concepts["children"]

    if not children:
        potential_support = 0.0

        for question in questions:
            try:
                potential_support += question["weights"][concept]
            except KeyError:
                pass

        topic_support = 1.0

        if potential_support > 0:
            topic_support = collected_supports[concept] / potential_support

        return {"support": topic_support, "name": concept, "children": []}

    concept_support = 0.0
    child_supports = []

    for child in children:
        support = depth_first_support(child, collected_supports, questions)
        child_supports.append(support)

        concept_support += support["support"] * child["weight"]

    return {"support": concept_support, "name": concept, "children": child_supports}


def leaf_concepts(concept_tree: Dict[str, Union[str, float, List[any]]]) -> List[str]:
    """Return leaf node names of knowledge web"""
    if not concept_tree["children"]:
        return [concept_tree["name"]]

    child_leafs = []

    for child in concept_tree["children"]:
        child_leafs.extend(leaf_concepts(child))

    return child_leafs


if __name__ == "__main__":

    collected_leaf_concept_scores = {h: 0.0 for h in leaf_concepts(KNOWLEDGE_WEB)}
    with open(
        os.path.join(os.path.dirname(__file__), "questions.json"), "r", encoding="utf8"
    ) as question_json:
        questions = json.load(question_json)

    for question in questions:

        TESTING_FOR_QUESTIONS = True

        alternatives = [question["correct"]] + question["incorrects"]
        random.shuffle(alternatives)
        ordered_alternatives = {i: a for i, a in enumerate(alternatives)}

        while TESTING_FOR_QUESTIONS:
            print(question["question"] + "\n")
            for i, a in ordered_alternatives.items():
                print(f"{i}: {a}")

            answer_number = input("Answer number: ")
            answer_number = answer_number.strip()

            try:
                answer_number = int(answer_number)
            except ValueError:
                print(f"Unrecognized answer number '{answer_number}'")
                # Loop back to start
                continue

            try:
                answer = ordered_alternatives[answer_number]
            except KeyError:
                print(f"Answer number outside of range '{answer_number}'")
                # Loop back to start
                continue

            evidence = score_a_question(question, answer)
            for concept, concept_support in evidence.items():
                collected_leaf_concept_scores[concept] += concept_support

            print()
            TESTING_FOR_QUESTIONS = False

    concept_scores = depth_first_support(
        KNOWLEDGE_WEB, collected_leaf_concept_scores, questions
    )

    print("Concept scores:")
    print(json.dumps(concept_scores, indent=2))
