import pytest

from fastapi.testclient import TestClient
from pre_test_setup_for_docker_caching import TRANSFORMERS_TESTING_CACHE, TRANSFORMER_MODEL, SENTENCE_MODEL, ONNX_MODEL
import torch
import os
import subprocess

# Due to import and config reasons, the environ is set in pre_test_setup_for_docker_caching !
# (because we import Transformer, which imports Model, imports PredictionOutput, which imports
# RETURN_PLAINTEXT_ARRAYS and this creates the starlette config.
# The config  is read by this point and starlette forbids overwriting it then)

# from starlette.config import environ
# environ["TRANSFORMERS_CACHE"] = TRANSFORMERS_TESTING_CACHE
# environ["MODEL_NAME"] = "test"
# environ["MODEL_TYPE"] = "test"
# environ["DISABLE_GPU"] = "True"
# environ["BATCH_SIZE"] = "1"
# environ["RETURN_PLAINTEXT_ARRAYS"] = "False"

from main import get_app, auth

from square_model_inference.inference.model import Model
from square_model_inference.models.prediction import PredictionOutput, PredictionOutputForGeneration, \
    PredictionOutputForEmbedding, PredictionOutputForTokenClassification, PredictionOutputForSequenceClassification,\
    PredictionOutputForQuestionAnswering
from square_model_inference.models.request import PredictionRequest, Task
from square_model_inference.inference.transformer import Transformer
from square_model_inference.inference.adaptertransformer import AdapterTransformer
from square_model_inference.inference.sentencetransformer import SentenceTransformer
from square_model_inference.inference.onnx import Onnx
from square_model_inference.core.config import ModelConfig, set_test_config, model_config


@pytest.fixture(scope="session")
def test_app():
    app = get_app()
    app.state.model = TestModel()
    app.dependency_overrides[auth] = lambda: True
    return app


class TestModel(Model):
    async def predict(self, payload, task) -> PredictionOutput:
        if task == Task.generation:
            return PredictionOutputForGeneration(generated_texts=[[""]])
        elif task == Task.question_answering:
            return PredictionOutputForQuestionAnswering(answers=[[{"score": 0, "start": 0, "end": 0, "answer": ""}]])
        elif task == Task.embedding:
            return PredictionOutputForEmbedding(word_ids=[[0]])
        elif task == Task.token_classification:
            return PredictionOutputForTokenClassification(word_ids=[[0]])
        elif task == Task.sequence_classification:
            return PredictionOutputForSequenceClassification()


# We only load bert-base-uncased, so we fix the random seed to always get the same randomly generated heads on top
@pytest.fixture(scope="class")
def test_transformer_sequence_classification():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="sequence_classification",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50

    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_embedding():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="base",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50

    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_token_classification():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="token_classification",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50

    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_question_answering():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="question_answering",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50

    )
    return Transformer()


@pytest.fixture(scope="class")
def test_transformer_generation():
    torch.manual_seed(987654321)
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        model_class="generation",
        disable_gpu=True,
        batch_size=1,
        max_input_size=50

    )
    return Transformer()


@pytest.fixture(scope="class")
def test_adapter():
    set_test_config(
        model_name=TRANSFORMER_MODEL,
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
        cache=TRANSFORMERS_TESTING_CACHE,
        preloaded_adapters=False,

    )
    return AdapterTransformer()


@pytest.fixture(scope="class")
def test_sentence_transformer():
    set_test_config(
        model_name=SENTENCE_MODEL,
        disable_gpu=True,
        batch_size=1,
        max_input_size=50,
    )
    return SentenceTransformer()


@pytest.fixture(scope="class")
def test_onnx_sequence_classification():
    onnx_path = "./onnx_models/german-bert/model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_token_classification():
    onnx_path = "./onnx_models\\NER-bert\\model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_embedding():
    onnx_path = "./onnx_models/bert-base-cased/model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_question_answering():
    onnx_path = "./onnx_models/squad2-bert/model.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
        )
        return Onnx()
    else:
        return None


@pytest.fixture(scope="class")
def test_onnx_generation():
    onnx_path = "./onnx_models/t5_encoder_decoder/t5-small-encoder.onnx"
    decoder_init_path = "./onnx_models/t5_encoder_decoder/t5-small-init-decoder.onnx"
    if os.path.isfile(onnx_path):
        set_test_config(
            model_name=ONNX_MODEL,
            disable_gpu=True,
            batch_size=1,
            max_input_size=50,
            onnx_path=onnx_path,
            decoder_path=decoder_init_path,
        )
        return Onnx()
    else:
        return None


@pytest.fixture()
def prediction_request():
    request = PredictionRequest.parse_obj({
        "input": ["test"],
        "is_preprocessed": False,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {},
        "adapter_name": ""
    })
    return request
