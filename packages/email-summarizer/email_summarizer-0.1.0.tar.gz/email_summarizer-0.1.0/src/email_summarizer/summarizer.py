# src/backend/summarizer.py

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI

# Instantiate the client (uses OPENAI_API_KEY from .env)
client = OpenAI()

# ─── Chunking constants ───────────────────────────────────────────────────────
MAX_TOKENS = 2000
TOKEN_CHAR_RATIO = 4            # rough chars per token
MAX_CHUNK_CHARS = MAX_TOKENS * TOKEN_CHAR_RATIO


def _chunk_messages(messages: List[Dict]) -> List[List[Dict]]:
    """
    Split a list of parsed messages into chunks so that each chunk's
    total character length stays under MAX_CHUNK_CHARS.
    """
    chunks: List[List[Dict]] = []
    cur_chunk: List[Dict] = []
    cur_size = 0

    for msg in messages:
        segment = f"{msg['date']} - {msg['sender']}: {msg['body']}\n"
        seg_len = len(segment)
        # if adding this message would blow past our limit, start a new chunk
        if cur_chunk and cur_size + seg_len > MAX_CHUNK_CHARS:
            chunks.append(cur_chunk)
            cur_chunk = []
            cur_size = 0

        cur_chunk.append(msg)
        cur_size += seg_len

    if cur_chunk:
        chunks.append(cur_chunk)

    return chunks


def _call_api(messages: List[Dict]) -> str:
    """
    Build the prompt and call OpenAI once, returning the raw summary text.
    """
    # 1) Build the user prompt
    prompt_lines = [
        "You are an assistant that summarizes email threads.",
        "",
        "Thread messages:"
    ]
    for msg in messages:
        prompt_lines.append(f"{msg['date']} - {msg['sender']}: {msg['body']}")
    prompt_lines.append("") 
    prompt_lines.append("Summary:")
    user_content = "\n".join(prompt_lines)

    # 2) Call the ChatCompletion API
    resp = client.chat.completions.create(
        model="gpt-4",               # or another model you prefer
        messages=[{"role": "user", "content": user_content}],
        temperature=0.3,
    )

    # 3) Extract and return the summary
    return resp.choices[0].message.content.strip()


def summarize(messages: List[Dict]) -> str:
    """
    Given a list of parsed messages, either:
      - If short enough, call the API directly.
      - Otherwise, chunk → sub-summarize → final summary.
    """
    # 1) Empty‐thread guard
    if not messages:
        return ""

    # 2) Chunk the messages by size
    chunks = _chunk_messages(messages)

    # 3) If we got multiple chunks, do hierarchical summarization
    if len(chunks) > 1:
        # Summarize each chunk into its own mini-summary
        sub_summaries = [summarize(chunk) for chunk in chunks]
        # Then stitch those together into one “message” and summarize that
        combined = [{"date": "", "sender": "", "body": "\n\n".join(sub_summaries)}]
        return summarize(combined)

    # 4) Single chunk: just call the API
    return _call_api(messages)