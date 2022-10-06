import os
import random
import json

from typing import Dict, List, Union

from knowledge_graph import KNOWLEDGE_GRAPH, leaf_concepts

# "What is the color/animal/trait for Y"


def score_a_question(
    question: Dict[str, Union[int, str, List[str], Dict[str, float]]], answer: str
) -> Dict[str, float]:
    """Evaluates evidence towards a concept. Empty evidence suggests 0 evidence"""
    if answer == question["correct"]:
        return question["weights"]
    return {}


def depth_first_support(
    knowledge_graph: Dict[str, Union[str, float, List[any]]],
    leaf_concept_supports: Dict[str, float],
    questions: List[Dict[str, Union[int, str, float, List[any]]]],
) -> Dict[str, Union[str, float, List[any]]]:

    concept, children = knowledge_graph["name"], knowledge_graph["children"]

    if not children:
        potential_support = 0.0

        for question in questions:
            try:
                potential_support += question["weights"][concept]
            except KeyError:
                pass

        topic_support = 1.0

        if potential_support > 0:
            topic_support = leaf_concept_supports[concept] / potential_support

        return {"support": topic_support, "name": concept, "children": []}

    concept_support = 0.0
    child_supports = []

    for child in children:
        support = depth_first_support(child, leaf_concept_supports, questions)
        child_supports.append(support)

        concept_support += support["support"] * child["weight"]

    return {"support": concept_support, "name": concept, "children": child_supports}


if __name__ == "__main__":

    collected_leaf_concept_scores = {h: 0.0 for h in leaf_concepts(KNOWLEDGE_GRAPH)}
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
        KNOWLEDGE_GRAPH, collected_leaf_concept_scores, questions
    )

    print("Concept scores:")
    print(json.dumps(concept_scores, indent=2))
