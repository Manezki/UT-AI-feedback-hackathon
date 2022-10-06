import os
import json

import flask

from inference import score_item_suite

app = flask.Flask(__name__)


@app.route("/questions", methods=["GET"])
def serve_questions():
    """Serve subset of questions"""
    n_questions = flask.request.args.get("n", default=10, type=int)

    with open(
        os.path.join(os.path.dirname(__file__), "questions.json"), "r", encoding="utf8"
    ) as questions_json:
        question_bank = json.load(questions_json)

    full_questions = question_bank[:n_questions]
    deliverable_questions = [
        {
            "id": q["id"],
            "question": q["question"],
            "alternatives": q["incorrects"] + [q["correct"]],
        }
        for q in full_questions
    ]

    return json.dumps(deliverable_questions)


@app.route("/knowledge-graph", methods=["POST"])
def infer_knowledge_graph():
    """Infers student's knowlege graph based on the question-answer pairs from the request"""
    question_answer_pairs = flask.request.get_json()

    return json.dumps(score_item_suite(question_answer_pairs))
