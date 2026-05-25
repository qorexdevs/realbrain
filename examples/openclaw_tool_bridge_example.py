"""Example: expose RealBrain functions from an OpenClaw/agent bridge.

This file is intentionally framework-light. In a real OpenClaw plugin, map the
host tool schema to these functions and let the host runtime own approvals,
auth, logging, and external action boundaries.
"""

from realbrain_server.tools import RealBrainToolContext, activate, dream, record_event, search_memory

ctx = RealBrainToolContext(brain_root="./demo_vault", db_path="./demo_vault/ops/brain/realbrain.sqlite")


def tool_record_event(args: dict) -> dict:
    return record_event(args["event"], ctx=ctx)


def tool_search_memory(args: dict) -> dict:
    return search_memory(args["query"], args.get("filters"), ctx=ctx)


def tool_activate(args: dict) -> dict:
    return activate(args["node_or_query"], depth=args.get("depth", 1), budget=args.get("budget", 5), ctx=ctx)


def tool_dream(args: dict) -> dict:
    return dream(mode=args.get("mode", "rem_generation"), budget=args.get("budget", 5), focus_area=args.get("focus_area"), ctx=ctx)
