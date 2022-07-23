import logging

from square_skill_api.models import QueryOutput, QueryRequest

from square_skill_helpers import ModelAPI, DataAPI

logger = logging.getLogger(__name__)

model_api = ModelAPI()
data_api = DataAPI()


async def predict(request: QueryRequest) -> QueryOutput:
    """Given a question, performs open-domain, extractive QA. First, background
    knowledge is retrieved using BM25 and the PubMed document collection. Next, the top
    10 documents are used for span extraction. Finally, the extracted answers are
    returned.
    """
    # empty index_name will use bm25
    data = await data_api(datastore_name="bioasq", index_name="", query=request.query)
    logger.info(f"Data API output:\n{data}")
    context = [d["document"]["text"] for d in data]
    context_score = [d["score"] for d in data]
    explain_kwargs = request.skill_args.get("explain_kwargs", {})

    # Call Model API
    prepared_input = [[request.query, c] for c in context]  # Change as needed
    model_request = {
        "input": prepared_input,
        "preprocessing_kwargs": {},
        "model_kwargs": {},
        "task_kwargs": {"topk": 1},
        "adapter_name": "qa/squad2@ukp",
        "explain_kwargs": explain_kwargs,
    }

    model_api_output = await model_api(
        model_name="bert-base-uncased",
        pipeline="question-answering",
        model_request=model_request,
    )
    logger.info(f"Model API output:\n{model_api_output}")

    return QueryOutput.from_question_answering(
        model_api_output=model_api_output, context=context, context_score=context_score
    )
