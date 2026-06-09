from pathlib import Path
import tempfile

from realbrain.dream_engine import DreamEngine
from realbrain.global_workspace import GlobalWorkspace
from realbrain.models import BrainEvent, Neuron, Synapse
from realbrain.obsidian_adapter import ObsidianAdapter
from realbrain.store import RealBrainStore


def test_dream_outputs_are_hypotheses_not_facts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = RealBrainStore(root / "realbrain.sqlite")
        obsidian = ObsidianAdapter(root / "vault")
        event = store.record_event(BrainEvent(event_type="reflection", source="test", content="RealBrain needs a dream loop."))
        a = store.add_neuron(Neuron(type="project", title="RealBrain", importance=9, created_from_event=event.id))
        b = store.add_neuron(Neuron(type="concept", title="Dream Engine", importance=8, created_from_event=event.id))
        store.add_synapse(Synapse(source_neuron_id=a.id, target_neuron_id=b.id, relation_type="depends_on", weight=0.7))
        result = DreamEngine(store, obsidian).run(mode="rem_generation", budget=5, focus_area="RealBrain")
        dream = result["dream_run"]
        assert dream["generated_hypotheses"]
        assert dream["accepted_changes"] == []
        assert "hypotheses_not_facts" in dream["safety_flags"]
        report = obsidian.read_markdown(dream["summary_path"])["content"]
        assert "not fact" in report.lower()
        assert "no external or high-impact actions" in report.lower()


def test_global_workspace_activation_surfaces_synapses():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = RealBrainStore(root / "realbrain.sqlite")
        obsidian = ObsidianAdapter(root / "vault")
        a = store.add_neuron(Neuron(type="agent", title="Research Agent", importance=9))
        b = store.add_neuron(Neuron(type="project", title="RealBrain", importance=9))
        store.add_synapse(Synapse(source_neuron_id=a.id, target_neuron_id=b.id, relation_type="used_for", weight=0.8))
        result = GlobalWorkspace(store, obsidian).activate("Research Agent", depth=1, budget=5)
        assert result["activated_neurons"][0]["id"] == a.id
        assert result["synapses"]
        current = obsidian.read_markdown("brain/global-workspace/current.md")["content"]
        assert "Activation request: Research Agent" in current
        assert "Related synapses" in current


def test_global_workspace_dedupes_shared_synapse():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = RealBrainStore(root / "realbrain.sqlite")
        obsidian = ObsidianAdapter(root / "vault")
        a = store.add_neuron(Neuron(type="project", title="RealBrain Core", importance=9))
        b = store.add_neuron(Neuron(type="concept", title="RealBrain Engine", importance=8))
        syn = store.add_synapse(Synapse(source_neuron_id=a.id, target_neuron_id=b.id, relation_type="depends_on", weight=0.7))
        # query matches both neurons, so the one synapse is surfaced from each end
        result = GlobalWorkspace(store, obsidian).activate("RealBrain", depth=1, budget=5)
        assert len(result["activated_neurons"]) == 2
        assert len(result["synapses"]) == 1
        assert result["synapses"][0]["id"] == syn.id
