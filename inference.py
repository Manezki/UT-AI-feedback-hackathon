import os
import random
import json

from typing import Dict, List, Tuple, Union

from knowledge_graph import KNOWLEDGE_GRAPH, leaf_concepts

# "What is the color/animal/trait for Y"


def score_a_question_beta(
    question: Dict[str, Union[int, str, List[str], Dict[str, float]]], answer: str
) -> Dict[str, Tuple[float, float]]:
    """Evaluates evidence towards a concept. With a Beta support."""
    if answer == question["correct"]:
        return {c: (0.0, w) for c, w in question["weights"].items()}
    return {c: (w, 0.0) for c, w in question["weights"].items()}


def score_a_question_naive(
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

        neg, pos = leaf_concept_supports[concept]
        # Support from Beta mean
        topic_support = pos / (neg + pos)

        return {"support": topic_support, "name": concept, "children": []}

    concept_support = 0.0
    child_supports = []

    for child in children:
        support = depth_first_support(child, leaf_concept_supports, questions)
        child_supports.append(support)

        concept_support += support["support"] * child["weight"]

    return {"support": concept_support, "name": concept, "children": child_supports}


def score_item_suite(
    questions_and_answers: List[Tuple[int, str]]
) -> Dict[str, Union[str, float, List[any]]]:
    collected_leaf_concept_scores = {
        h: (1.0, 1.0) for h in leaf_concepts(KNOWLEDGE_GRAPH)
    }
    asked_questions = []

    with open(
        os.path.join(os.path.dirname(__file__), "questions.json"), "r", encoding="utf8"
    ) as questions_json:
        question_bank = json.load(questions_json)

    for qa_dict in questions_and_answers:
        question_id, answer = qa_dict["id"], qa_dict["answer"]
        for banked in question_bank:
            if banked["id"] == question_id:
                asked_questions.append(banked)

                evidence = score_a_question_beta(banked, answer)
                for concept, (neg_support, pos_support) in evidence.items():
                    existing_neg, existing_pos = collected_leaf_concept_scores[concept]
                    collected_leaf_concept_scores[concept] = (
                        existing_neg + neg_support,
                        existing_pos + pos_support,
                    )

    return depth_first_support(
        KNOWLEDGE_GRAPH, collected_leaf_concept_scores, asked_questions
    )


if __name__ == "__main__":

    collected_leaf_concept_scores = {
        h: (1.0, 1.0) for h in leaf_concepts(KNOWLEDGE_GRAPH)
    }
    with open(
        os.path.join(os.path.dirname(__file__), "questions.json"), "r", encoding="utf8"
    ) as question_json:
        questions = json.load(question_json)

    questions_with_answers = []

    for question in questions:

        TESTING_FOR_QUESTIONS = True

        alternatives = [question["correct"]] + question["incorrects"]
        random.shuffle(alternatives)

        while TESTING_FOR_QUESTIONS:
            print(question["question"] + "\n")
            for i, a in enumerate(alternatives):
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
                answer = alternatives[answer_number]
            except KeyError:
                print(f"Answer number outside of range '{answer_number}'")
                # Loop back to start
                continue

            questions_with_answers.append(
                {
                    "id": question["id"],
                    "answer": answer,
                }
            )

            print()
            TESTING_FOR_QUESTIONS = False

    student_knowledge_graph = score_item_suite(questions_with_answers)

    print("Student knowledge graph:")
    print(json.dumps(student_knowledge_graph, indent=2))
