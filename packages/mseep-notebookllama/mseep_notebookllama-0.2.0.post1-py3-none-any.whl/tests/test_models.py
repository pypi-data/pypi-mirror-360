import pytest

from src.notebookllama.models import (
    Notebook,
)
from src.notebookllama.utils import MindMap, Node, Edge
from src.notebookllama.audio import MultiTurnConversation, ConversationTurn
from pydantic import ValidationError


def test_notebook() -> None:
    n1 = Notebook(
        summary="This is a summary",
        questions=[
            "What is the capital of Spain?",
            "What is the capital of France?",
            "What is the capital of Italy?",
            "What is the capital of Portugal?",
            "What is the capital of Germany?",
        ],
        answers=[
            "Madrid",
            "Paris",
            "Rome",
            "Lisbon",
            "Berlin",
        ],
        highlights=["This", "is", "a", "summary"],
    )
    assert n1.summary == "This is a summary"
    assert n1.questions[0] == "What is the capital of Spain?"
    assert n1.answers[0] == "Madrid"
    assert n1.highlights[0] == "This"
    # Fewer answers than questions
    with pytest.raises(ValidationError):
        Notebook(
            summary="This is a summary",
            questions=[
                "What is the capital of France?",
                "What is the capital of Italy?",
                "What is the capital of Portugal?",
                "What is the capital of Germany?",
            ],
            answers=[
                "Paris",
                "Rome",
                "Lisbon",
            ],
            highlights=["This", "is", "a", "summary"],
        )
    # Fewer highlights than required
    with pytest.raises(ValidationError):
        Notebook(
            summary="This is a summary",
            questions=[
                "What is the capital of Spain?",
                "What is the capital of France?",
                "What is the capital of Italy?",
                "What is the capital of Portugal?",
                "What is the capital of Germany?",
            ],
            answers=[
                "Madrid",
                "Paris",
                "Rome",
                "Lisbon",
                "Berlin",
            ],
            highlights=["This", "is"],
        )


def test_mind_map() -> None:
    m1 = MindMap(
        nodes=[
            Node(id="A", content="Auxin is released"),
            Node(id="B", content="Travels to the roots"),
            Node(id="C", content="Root cells grow"),
        ],
        edges=[
            Edge(from_id="A", to_id="B"),
            Edge(from_id="A", to_id="C"),
            Edge(from_id="B", to_id="C"),
        ],
    )
    assert m1.nodes[0].id == "A"
    assert m1.nodes[0].content == "Auxin is released"
    assert m1.edges[0].from_id == "A"
    assert m1.edges[0].to_id == "B"

    with pytest.raises(ValidationError):
        MindMap(
            nodes=[
                Node(id="A", content="Auxin is released"),
                Node(id="B", content="Travels to the roots"),
                Node(id="C", content="Root cells grow"),
            ],
            edges=[
                Edge(from_id="A", to_id="B"),
                Edge(from_id="A", to_id="D"),  # "D" does not exist
                Edge(from_id="B", to_id="C"),
            ],
        )


def test_multi_turn_conversation() -> None:
    turns = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker2", content="I am very well, how about you?"),
        ConversationTurn(speaker="speaker1", content="I am well too, thanks!"),
    ]
    assert turns[0].speaker == "speaker1"
    assert turns[0].content == "Hello, who are you?"
    conversation = MultiTurnConversation(
        conversation=turns,
    )
    assert isinstance(conversation.conversation, list)
    assert isinstance(conversation.conversation[0], ConversationTurn)
    wrong_turns = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker2", content="I am very well, how about you?"),
    ]
    wrong_turns1 = [
        ConversationTurn(speaker="speaker2", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker1", content="I am very well, how about you?"),
        ConversationTurn(speaker="speaker2", content="I am well too!"),
    ]
    wrong_turns2 = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker1", content="How is your life going?"),
        ConversationTurn(
            speaker="speaker2",
            content="What is all this interest in me all of a sudden?!",
        ),
    ]
    wrong_turns3 = [
        ConversationTurn(speaker="speaker1", content="Hello, who are you?"),
        ConversationTurn(speaker="speaker2", content="I'm well! But..."),
        ConversationTurn(
            speaker="speaker2",
            content="...What is all this interest in me all of a sudden?!",
        ),
    ]
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns)
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns1)
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns2)
    with pytest.raises(ValidationError):
        MultiTurnConversation(conversation=wrong_turns3)
