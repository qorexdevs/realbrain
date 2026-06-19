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


def test_list_synapses_filters_by_weight():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        n1 = store.add_neuron(Neuron(type="concept", title="A"))
        n2 = store.add_neuron(Neuron(type="concept", title="B"))
        n3 = store.add_neuron(Neuron(type="concept", title="C"))
        strong = store.add_synapse(Synapse(source_neuron_id=n1.id, target_neuron_id=n2.id, relation_type="related_to", weight=0.8))
        store.add_synapse(Synapse(source_neuron_id=n1.id, target_neuron_id=n3.id, relation_type="related_to", weight=0.3))
        only_strong = store.list_synapses(min_weight=0.5)
        assert [s.id for s in only_strong] == [strong.id]
        # min_weight combines with the neuron_id filter
        assert store.list_synapses(neuron_id=n3.id, min_weight=0.5) == []
        assert len(store.list_synapses(neuron_id=n1.id)) == 2


def test_list_synapses_filters_by_relation_type():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        n1 = store.add_neuron(Neuron(type="concept", title="A"))
        n2 = store.add_neuron(Neuron(type="concept", title="B"))
        n3 = store.add_neuron(Neuron(type="concept", title="C"))
        part = store.add_synapse(Synapse(source_neuron_id=n1.id, target_neuron_id=n2.id, relation_type="part_of", weight=0.8))
        store.add_synapse(Synapse(source_neuron_id=n1.id, target_neuron_id=n3.id, relation_type="related_to", weight=0.9))
        only_part = store.list_synapses(relation_type="part_of")
        assert [s.id for s in only_part] == [part.id]
        # relation_type combines with the other filters
        assert store.list_synapses(neuron_id=n3.id, relation_type="part_of") == []


def test_list_synapses_filters_by_direction():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        n1 = store.add_neuron(Neuron(type="concept", title="A"))
        n2 = store.add_neuron(Neuron(type="concept", title="B"))
        out = store.add_synapse(Synapse(source_neuron_id=n1.id, target_neuron_id=n2.id, relation_type="related_to", weight=0.8))
        inc = store.add_synapse(Synapse(source_neuron_id=n2.id, target_neuron_id=n1.id, relation_type="related_to", weight=0.6))
        assert [s.id for s in store.list_synapses(neuron_id=n1.id, direction="out")] == [out.id]
        assert [s.id for s in store.list_synapses(neuron_id=n1.id, direction="in")] == [inc.id]
        assert len(store.list_synapses(neuron_id=n1.id)) == 2
        try:
            store.list_synapses(neuron_id=n1.id, direction="sideways")
            raise AssertionError("expected value error")
        except ValueError:
            pass


def test_list_beliefs_due_for_review():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        overdue = store.add_belief(Belief(claim_text="Recheck the cache TTL.", review_after=datetime(2026, 1, 1, tzinfo=timezone.utc)))
        soon = store.add_belief(Belief(claim_text="Revisit the rate limit.", review_after=datetime(2026, 3, 1, tzinfo=timezone.utc)))
        store.add_belief(Belief(claim_text="No review scheduled.", review_after=datetime(2026, 12, 1, tzinfo=timezone.utc)))
        store.add_belief(Belief(claim_text="Never expires."))
        due = store.list_beliefs(due_before=datetime(2026, 6, 1, tzinfo=timezone.utc))
        assert [b.id for b in due] == [overdue.id, soon.id]


def test_list_beliefs_min_confidence_filters():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        store.add_belief(Belief(claim_text="Shaky hunch.", confidence=0.2))
        strong = store.add_belief(Belief(claim_text="Solid claim.", confidence=0.9))
        kept = store.list_beliefs(min_confidence=0.5)
        assert [b.id for b in kept] == [strong.id]
        assert store.list_beliefs(min_confidence=0.95) == []


def test_list_beliefs_max_confidence_filters():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        shaky = store.add_belief(Belief(claim_text="Shaky hunch.", confidence=0.2))
        store.add_belief(Belief(claim_text="Solid claim.", confidence=0.9))
        kept = store.list_beliefs(max_confidence=0.4)
        assert [b.id for b in kept] == [shaky.id]
        # combines with min_confidence to carve out a mid band
        store.add_belief(Belief(claim_text="Middling.", confidence=0.55))
        band = store.list_beliefs(min_confidence=0.5, max_confidence=0.6)
        assert [b.claim_text for b in band] == ["Middling."]


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


def test_find_neurons_min_importance_filters():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        store.add_neuron(Neuron(type="concept", title="minor note", importance=2))
        big = store.add_neuron(Neuron(type="concept", title="key idea", importance=9))
        found = store.find_neurons(min_importance=5)
        assert [n.id for n in found] == [big.id]


def test_find_neurons_min_confidence_filters():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        store.add_neuron(Neuron(type="concept", title="hunch", confidence=0.3))
        sure = store.add_neuron(Neuron(type="concept", title="solid fact", confidence=0.9))
        found = store.find_neurons(min_confidence=0.7)
        assert [n.id for n in found] == [sure.id]


def test_find_neurons_state_filters():
    with tempfile.TemporaryDirectory() as tmp:
        store = RealBrainStore(Path(tmp) / "brain.sqlite")
        store.add_neuron(Neuron(type="concept", title="old draft", state="archived"))
        live = store.add_neuron(Neuron(type="concept", title="live note", state="active"))
        found = store.find_neurons(state="active")
        assert [n.id for n in found] == [live.id]
