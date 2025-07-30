import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

from typing import Callable
from pydantic import ValidationError
from src.notebookllama.utils import process_file, get_mind_map
from src.notebookllama.models import Notebook

load_dotenv()

skip_condition = not (
    os.getenv("LLAMACLOUD_API_KEY", None)
    and os.getenv("EXTRACT_AGENT_ID", None)
    and os.getenv("LLAMACLOUD_PIPELINE_ID", None)
    and os.getenv("OPENAI_API_KEY", None)
)


@pytest.fixture()
def input_file() -> str:
    return "data/test/brain_for_kids.pdf"


@pytest.fixture()
def file_exists_fn() -> Callable[[os.PathLike[str]], bool]:
    def file_exists(file_path: os.PathLike[str]) -> bool:
        return Path(file_path).exists()

    return file_exists


@pytest.fixture()
def is_not_empty_fn() -> Callable[[os.PathLike[str]], bool]:
    def is_not_empty(file_path: os.PathLike[str]) -> bool:
        return Path(file_path).stat().st_size > 0

    return is_not_empty


@pytest.fixture
def notebook_to_process() -> Notebook:
    return Notebook(
        summary="""The Human Brain:
        The human brain is a complex organ responsible for thought, memory, emotion, and coordination. It contains about 86 billion neurons and operates through electrical and chemical signals. Divided into major parts like the cerebrum, cerebellum, and brainstem, it controls everything from basic survival functions to advanced reasoning. Despite its size, it consumes around 20% of the body’s energy. Neuroscience continues to explore its mysteries, including consciousness and neuroplasticity—its ability to adapt and reorganize.""",
        questions=[
            "How many neurons are in the human brain?",
            "What are the main parts of the human brain?",
            "What percentage of the body's energy does the brain use?",
            "What is neuroplasticity?",
            "What functions is the human brain responsible for?",
        ],
        answers=[
            "About 86 billion neurons.",
            "The cerebrum, cerebellum, and brainstem.",
            "Around 20%.",
            "The brain's ability to adapt and reorganize itself.",
            "Thought, memory, emotion, and coordination.",
        ],
        highlights=[
            "The human brain has about 86 billion neurons.",
            "It controls thought, memory, emotion, and coordination.",
            "Major brain parts include the cerebrum, cerebellum, and brainstem.",
            "The brain uses approximately 20% of the body's energy.",
            "Neuroplasticity allows the brain to adapt and reorganize.",
        ],
    )


@pytest.mark.skipif(
    condition=skip_condition,
    reason="You do not have the necessary env variables to run this test.",
)
@pytest.mark.asyncio
async def test_mind_map_creation(
    notebook_to_process: Notebook,
    file_exists_fn: Callable[[os.PathLike[str]], bool],
    is_not_empty_fn: Callable[[os.PathLike[str]], bool],
):
    test_mindmap = await get_mind_map(
        summary=notebook_to_process.summary, highlights=notebook_to_process.highlights
    )
    assert test_mindmap is not None
    assert file_exists_fn(test_mindmap)
    assert is_not_empty_fn(test_mindmap)
    os.remove(test_mindmap)


@pytest.mark.skipif(
    condition=skip_condition,
    reason="You do not have the necessary env variables to run this test.",
)
@pytest.mark.asyncio
async def test_file_processing(input_file: str) -> None:
    notebook, text = await process_file(filename=input_file)
    print(notebook)
    assert notebook is not None
    assert isinstance(text, str)
    try:
        notebook_model = Notebook.model_validate_json(json_data=notebook)
    except ValidationError:
        notebook_model = None
    assert isinstance(notebook_model, Notebook)
