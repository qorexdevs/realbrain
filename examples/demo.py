from pathlib import Path

from realbrain_server.tools import RealBrainToolContext, activate, dream, extract_events, record_event, search_memory

ctx = RealBrainToolContext(brain_root="./demo_vault", db_path="./demo_vault/ops/brain/realbrain.sqlite")
Path("./demo_vault").mkdir(exist_ok=True)

print(record_event({
    "event_type": "conversation",
    "source": "demo",
    "content": "RealBrain should help an agent remember evidence-backed decisions without treating dreams as facts.",
    "sensitivity": "personal",
    "evidence_refs": ["demo://event/1"],
}, ctx=ctx))

print(extract_events(limit=5, ctx=ctx))
print(search_memory("evidence backed decisions", ctx=ctx))
print(activate("RealBrain", ctx=ctx))
print(dream(mode="rem_generation", budget=3, focus_area="RealBrain", ctx=ctx))
