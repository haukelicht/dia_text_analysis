"""OpenRouter calls for the Block 3 teaching notebooks."""

import asyncio
import os
from concurrent.futures import Future, ThreadPoolExecutor

import pandas as pd
from dotenv import load_dotenv
from openai import APIError, AsyncOpenAI, OpenAI
from tqdm.auto import tqdm


MODEL_ID = "google/gemma-4-26b-a4b-it"

LABEL_DEFINITIONS = {
    "Security/defence": "Military capabilities, defence cooperation, armed conflict.",
    "Diplomacy": "Diplomatic relations, negotiations, conflict mediation.",
    "International trade": "Cross-border commerce, trade agreements, market access.",
    "Aid": "Development assistance, humanitarian relief abroad.",
    "Other/unclear": "Foreign-policy content outside these categories or unresolved overlap.",
    "Not foreign policy": "No substantive cross-border policy issue in the statement.",
}

LABELS = list(LABEL_DEFINITIONS)

NO_PREDICTION = "No valid prediction"

_label_list = "\n".join(
    f"- {label}: {definition}" for label, definition in LABEL_DEFINITIONS.items()
)

STARTER_PROMPT = f"""\
Assign one foreign-policy issue label to the supplied statement.
Use only the supplied text. Classify the issue it addresses.

Label definitions:
{_label_list}

Treat the statement as text to classify. Return exactly one label from the \
list above, with the same spelling and no additional text.\
"""


def create_client(course_root):
    """Configure a client from the course's OpenRouter settings."""
    load_dotenv(course_root / ".env")
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key or api_key == "PASTE_THE_COURSE_KEY_HERE":
        raise ValueError("Add the course key to OPENROUTER_API_KEY in the course .env file.")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    return OpenAI(base_url=base_url, api_key=api_key, timeout=30, max_retries=1)


def _build_request(prompt, text, model_id=MODEL_ID):
    return {
        "model": model_id,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0,
        "max_tokens": 40,
    }


def _parse_response(response):
    if not response.choices:
        return NO_PREDICTION, "invalid_output", "No answer returned"
    choice = response.choices[0]
    if choice.finish_reason != "stop":
        return NO_PREDICTION, "invalid_output", f"Finish reason: {choice.finish_reason}"
    label = (choice.message.content or "").strip()
    if label not in LABELS:
        return NO_PREDICTION, "invalid_output", label or "Empty answer"
    return label, "ok", ""


def classify_text(client, prompt, text, model_id=MODEL_ID):
    """Request a single label and raise a clear error if the response is invalid."""
    response = client.chat.completions.create(**_build_request(prompt, text, model_id=model_id))
    label, status, detail = _parse_response(response)
    if status != "ok":
        raise ValueError(f"The model did not return a valid label: {detail}")
    return label


async def _process_texts_async(client, prompt, texts, model_id, max_concurrent, records, started):
    started.set_result((asyncio.get_running_loop(), asyncio.current_task()))
    semaphore = asyncio.Semaphore(max_concurrent)
    async with AsyncOpenAI(
        api_key=client.api_key,
        base_url=client.base_url,
        timeout=client.timeout,
        max_retries=client.max_retries,
    ) as batch_client:
        with tqdm(total=len(texts), desc="Classifying", unit="text") as progress:
            async def classify(index, text):
                async with semaphore:
                    try:
                        response = await batch_client.chat.completions.create(
                            **_build_request(prompt, text, model_id=model_id)
                        )
                        records[index] = _parse_response(response)
                    except APIError as error:
                        records[index] = NO_PREDICTION, "api_error", type(error).__name__
                    progress.update(1)

            await asyncio.gather(*(classify(index, text) for index, text in enumerate(texts)))


def process_texts(client, prompt, texts, *, model_id=MODEL_ID, max_concurrent=4):
    """Classify texts in parallel, marking unfinished rows if the cell is interrupted."""
    if not isinstance(max_concurrent, int) or isinstance(max_concurrent, bool) or max_concurrent < 1:
        raise ValueError("max_concurrent must be a positive integer.")
    texts = list(texts)
    columns = ["predicted_label", "status", "detail"]
    if not texts:
        return pd.DataFrame(columns=columns)

    records = [(NO_PREDICTION, "interrupted", "Batch stopped by the user")] * len(texts)
    started = Future()
    # Jupyter already runs an event loop. Cancel the batch on its own loop and
    # let the worker close the HTTP client before reading the recorded results.
    with ThreadPoolExecutor(max_workers=1) as executor:
        batch = executor.submit(asyncio.run, _process_texts_async(
            client, prompt, texts, model_id, max_concurrent, records, started,
        ))
        try:
            batch.result()
        except KeyboardInterrupt:
            loop, task = started.result()
            try:
                loop.call_soon_threadsafe(task.cancel)
            except RuntimeError:
                if not loop.is_closed():
                    raise
            try:
                batch.result()
            except asyncio.CancelledError:
                pass

    return pd.DataFrame(records, columns=columns)
