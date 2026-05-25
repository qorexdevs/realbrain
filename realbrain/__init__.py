"""RealBrain: local operating-memory primitives for AI agents.

RealBrain is an engineering memory/control-plane layer, not consciousness.
It stores operational events, evidence-linked graph records, beliefs, dreams,
and a global workspace while keeping a human-readable knowledge base as the
source of truth.
"""

from .models import Belief, BrainEvent, DreamRun, GlobalWorkspaceItem, Neuron, Synapse
from .store import RealBrainStore

__all__ = [
    "Belief",
    "BrainEvent",
    "DreamRun",
    "GlobalWorkspaceItem",
    "Neuron",
    "Synapse",
    "RealBrainStore",
]
