import os
import sys
import argparse
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

# Make sure imports resolve under src/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

from email_summarizer.parser     import parse_email
from email_summarizer.summarizer import summarize
from email_summarizer.classifier import classify
from email_summarizer.fetcher    import (
    fetch_thread_raw,
    fetch_message_raw,
    list_recent_threads
)

def _do_summarize(path: str):
    raw = open(path, encoding="utf-8").read()
    msgs = parse_email(raw)
    print(f"Parsed {len(msgs)} message(s).\n")
    summary = summarize(msgs)
    print("=== AI-GENERATED SUMMARY ===\n", summary)
    return summary

def _do_classify(text: str):
    label = classify(text)
    print("\n=== ASSIGNED CATEGORY: ", label, " ===")

def _do_gmail(id: str):
    try:
        raw = fetch_thread_raw(id)
    except HttpError:
        print("Warning: not a thread ID; fetching single message…")
        raw = fetch_message_raw(id)
    msgs = parse_email(raw)
    print(f"Fetched & parsed {len(msgs)} message(s).\n")
    summary = summarize(msgs)
    print("=== AI SUMMARY ===\n", summary, "\n")
    _do_classify(summary)

def _do_threads(n: int):
    ids = list_recent_threads(n)
    print(f"Recent {n} thread IDs:")
    for t in ids:
        print(" ", t)

def main():
    parser = argparse.ArgumentParser("EmailSummarizer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("summarize", help="Summarize a .eml file")
    p.add_argument("file", help="Path to raw email file")

    p = sub.add_parser("classify", help="Summarize & classify a .eml file")
    p.add_argument("file", help="Path to raw email file")

    p = sub.add_parser("gmail", help="Fetch, summarize & classify Gmail ID")
    p.add_argument("thread_id", help="Gmail thread or message ID")

    p = sub.add_parser("threads", help="List recent Gmail thread IDs")
    p.add_argument("-n", "--count", type=int, default=5)

    args = parser.parse_args()
    if args.cmd == "summarize":
        _do_summarize(args.file)
    elif args.cmd == "classify":
        s = _do_summarize(args.file)
        _do_classify(s)
    elif args.cmd == "gmail":
        _do_gmail(args.thread_id)
    elif args.cmd == "threads":
        _do_threads(args.count)

if __name__ == "__main__":
    main()