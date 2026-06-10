from datetime import datetime, timezone
from pathlib import Path
import tempfile

from pydantic import ValidationError

from realbrain.models import Belief, BrainEvent, DreamRun, Neuron, Synapse
from realbrain.store import RealBrainStore


def test_models_validate_bounds_and_self_edges():
    try:
        Neuron(type="concept", title="Bad confidence", confidence=1.2)
        raise AssertionError("expected validation error")
    except ValidationError:
        pass
    try:
        Synapse(source_neuron_id="n1", target_neuron_id="n1", relation_type="related_to")
        raise AssertionError("expected validation error")
    except ValidationError:
        pass


def test_store_persists_core_records():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        event = store.record_event(BrainEvent(event_type="conversation", source="unit-test", content="A user wants evidence-backed memory.", evidence_refs=["test://1"]))
        assert store.get_event(event.id).content == event.content
        n1 = store.add_neuron(Neuron(type="concept", title="RealBrain", created_from_event=event.id, evidence_refs=[event.id], importance=8))
        n2 = store.add_neuron(Neuron(type="project", title="Example Project", importance=9))
        assert store.get_neuron(n1.id).title == "RealBrain"
        assert store.find_neurons(query="example project")[0].id == n2.id
        synapse = store.add_synapse(Synapse(source_neuron_id=n1.id, target_neuron_id=n2.id, relation_type="part_of", weight=0.4, confidence=0.7))
        updated = store.reinforce_synapse(synapse.id, delta=0.2, reason="useful retrieval")
        assert updated.weight == 0.6
        belief = store.add_belief(Belief(claim_text="Dream outputs are hypotheses, not facts.", status="fact", evidence_refs=[event.id]))
        assert store.get_belief(belief.id).status == "fact"
        dream = store.add_dream_run(DreamRun(mode="rem_generation", generated_hypotheses=["Try a small workbench."]))
        assert store.get_dream_run(dream.id).mode == "rem_generation"


def test_list_dream_runs_filters_and_orders():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        store.add_dream_run(DreamRun(mode="nrem_consolidation", started_at=datetime(2026, 1, 1, tzinfo=timezone.utc)))
        newer = store.add_dream_run(DreamRun(mode="rem_generation", started_at=datetime(2026, 2, 1, tzinfo=timezone.utc)))
        older = store.add_dream_run(DreamRun(mode="rem_generation", started_at=datetime(2026, 1, 15, tzinfo=timezone.utc)))
        rem = store.list_dream_runs(mode="rem_generation")
        assert [d.id for d in rem] == [newer.id, older.id]
        assert len(store.list_dream_runs()) == 3


def test_find_neurons_underscore_is_literal():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        hit = store.add_neuron(Neuron(type="concept", title="alpha_beta gate", importance=5))
        store.add_neuron(Neuron(type="concept", title="alphaXbeta gate", importance=5))
        found = store.find_neurons(query="alpha_beta")
        assert [n.id for n in found] == [hit.id]


def test_find_neurons_ranks_by_terms_matched():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        # one_term has higher importance but only hits a single query word, so the
        # row matching both words must still come first
        store.add_neuron(Neuron(type="concept", title="graph database", importance=9))
        both = store.add_neuron(Neuron(type="concept", title="vector graph store", importance=2))
        found = store.find_neurons(query="vector graph")
        assert found[0].id == both.id


def test_find_neurons_dedups_repeated_terms():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        # a repeated word must not outweigh a neuron that hits two distinct words
        store.add_neuron(Neuron(type="concept", title="memory cache", importance=9))
        both = store.add_neuron(Neuron(type="concept", title="memory graph index", importance=2))
        found = store.find_neurons(query="memory memory graph")
        assert found[0].id == both.id
