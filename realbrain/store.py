from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, TypeVar

from pydantic import BaseModel

from .models import Belief, BrainEvent, DreamRun, Neuron, Synapse, utc_now

T = TypeVar("T", bound=BaseModel)


class RealBrainStore:
    """SQLite operational store for RealBrain events and graph state.

    This is an operational index, not the durable truth layer. Durable canonical
    facts still belong in Obsidian pages and are indexed by GBrain. The SQLite
    store keeps append-only event history plus inspectable graph records that can
    be rebuilt from markdown/event logs over time.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        # sqlite3's own context manager commits but never closes, so on Windows
        # the file stays locked and temp-dir cleanup fails. Close it ourselves.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS brain_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sensitivity TEXT NOT NULL,
                    processed_status TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_brain_events_type_ts
                    ON brain_events(event_type, timestamp);
                CREATE INDEX IF NOT EXISTS idx_brain_events_status
                    ON brain_events(processed_status);

                CREATE TABLE IF NOT EXISTS neurons (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    canonical_path TEXT,
                    state TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    importance INTEGER NOT NULL,
                    last_activated_at TEXT,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_neurons_type_title
                    ON neurons(type, title);
                CREATE INDEX IF NOT EXISTS idx_neurons_canonical_path
                    ON neurons(canonical_path);

                CREATE TABLE IF NOT EXISTS synapses (
                    id TEXT PRIMARY KEY,
                    source_neuron_id TEXT NOT NULL,
                    target_neuron_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    weight REAL NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    UNIQUE(source_neuron_id, target_neuron_id, relation_type)
                );
                CREATE INDEX IF NOT EXISTS idx_synapses_source
                    ON synapses(source_neuron_id);
                CREATE INDEX IF NOT EXISTS idx_synapses_target
                    ON synapses(target_neuron_id);

                CREATE TABLE IF NOT EXISTS beliefs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    owner_domain TEXT,
                    confidence REAL NOT NULL,
                    review_after TEXT,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_beliefs_status_domain
                    ON beliefs(status, owner_domain);

                CREATE TABLE IF NOT EXISTS dream_runs (
                    id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    summary_path TEXT,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_dream_runs_mode_started
                    ON dream_runs(mode, started_at);
                """
            )

    @staticmethod
    def _json(model: BaseModel) -> str:
        return model.model_dump_json()

    @staticmethod
    def _load(model: type[T], row: sqlite3.Row | None) -> T | None:
        if row is None:
            return None
        return model.model_validate_json(row["payload"])

    def record_event(self, event: BrainEvent) -> BrainEvent:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO brain_events
                    (id, event_type, source, timestamp, sensitivity, processed_status, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.event_type,
                    event.source,
                    event.timestamp.isoformat(),
                    event.sensitivity,
                    event.processed_status,
                    self._json(event),
                ),
            )
        return event

    def get_event(self, event_id: str) -> BrainEvent | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM brain_events WHERE id = ?", (event_id,)).fetchone()
        return self._load(BrainEvent, row)

    def list_events(self, *, status: str | None = None, limit: int = 100) -> list[BrainEvent]:
        limit = max(1, min(limit, 1000))
        sql = "SELECT payload FROM brain_events"
        params: list[object] = []
        if status:
            sql += " WHERE processed_status = ?"
            params.append(status)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [BrainEvent.model_validate_json(row["payload"]) for row in rows]

    def mark_event_status(self, event_id: str, status: str) -> BrainEvent | None:
        event = self.get_event(event_id)
        if event is None:
            return None
        event.processed_status = status  # type: ignore[assignment]
        return self.record_event(event)

    def add_neuron(self, neuron: Neuron) -> Neuron:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO neurons
                    (id, type, title, canonical_path, state, confidence, importance, last_activated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    neuron.id,
                    neuron.type,
                    neuron.title,
                    neuron.canonical_path,
                    neuron.state,
                    neuron.confidence,
                    neuron.importance,
                    neuron.last_activated_at.isoformat() if neuron.last_activated_at else None,
                    self._json(neuron),
                ),
            )
        return neuron

    def get_neuron(self, neuron_id: str) -> Neuron | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM neurons WHERE id = ?", (neuron_id,)).fetchone()
        return self._load(Neuron, row)

    def find_neurons(self, *, query: str | None = None, type: str | None = None,
                     min_importance: int | None = None, min_confidence: float | None = None,
                     state: str | None = None, limit: int = 100) -> list[Neuron]:
        limit = max(1, min(limit, 1000))
        select_params: list[object] = []
        where_clauses: list[str] = []
        where_params: list[object] = []
        score_sql = "0"
        if query:
            # dedup terms so a repeated word ("memory memory") can't inflate the
            # match score above a neuron that actually hits two distinct words
            terms = list(dict.fromkeys(
                term for term in re.findall(r"[a-z0-9_\-]+", query.lower()) if len(term) >= 3
            ))[:12]
            if terms:
                cond = "(LOWER(title) LIKE ? ESCAPE '\\' OR LOWER(payload) LIKE ? ESCAPE '\\')"
                score_parts = []
                for term in terms:
                    # the tokenizer keeps '_', which LIKE treats as a wildcard, so a
                    # query like "foo_bar" would also match "fooXbar" without this
                    like = "%" + term.replace("_", "\\_") + "%"
                    score_parts.append(f"(CASE WHEN {cond} THEN 1 ELSE 0 END)")
                    select_params.extend([like, like])
                    where_params.extend([like, like])
                # rank by how many query terms a neuron hits, so a row matching every
                # token outranks one that only matched a single word
                score_sql = " + ".join(score_parts)
                where_clauses.append("(" + " OR ".join([cond] * len(terms)) + ")")
        if type:
            where_clauses.append("type = ?")
            where_params.append(type)
        if min_importance is not None:
            where_clauses.append("importance >= ?")
            where_params.append(min_importance)
        if min_confidence is not None:
            where_clauses.append("confidence >= ?")
            where_params.append(min_confidence)
        if state:
            where_clauses.append("state = ?")
            where_params.append(state)
        sql = f"SELECT payload, ({score_sql}) AS score FROM neurons"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY score DESC, importance DESC, title ASC LIMIT ?"
        params = select_params + where_params + [limit]
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [Neuron.model_validate_json(row["payload"]) for row in rows]

    def activate_neuron(self, neuron_id: str) -> Neuron | None:
        neuron = self.get_neuron(neuron_id)
        if neuron is None:
            return None
        neuron.activation_count += 1
        neuron.last_activated_at = utc_now()
        return self.add_neuron(neuron)

    def add_synapse(self, synapse: Synapse) -> Synapse:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO synapses
                    (id, source_neuron_id, target_neuron_id, relation_type, weight, confidence, status, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    synapse.id,
                    synapse.source_neuron_id,
                    synapse.target_neuron_id,
                    synapse.relation_type,
                    synapse.weight,
                    synapse.confidence,
                    synapse.status,
                    self._json(synapse),
                ),
            )
        return synapse

    def get_synapse(self, synapse_id: str) -> Synapse | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM synapses WHERE id = ?", (synapse_id,)).fetchone()
        return self._load(Synapse, row)

    def list_synapses(self, *, neuron_id: str | None = None, min_weight: float | None = None,
                      relation_type: str | None = None, limit: int = 100) -> list[Synapse]:
        limit = max(1, min(limit, 1000))
        params: list[object] = []
        where_clauses: list[str] = []
        sql = "SELECT payload FROM synapses"
        if neuron_id:
            where_clauses.append("(source_neuron_id = ? OR target_neuron_id = ?)")
            params.extend([neuron_id, neuron_id])
        if min_weight is not None:
            where_clauses.append("weight >= ?")
            params.append(min_weight)
        if relation_type:
            where_clauses.append("relation_type = ?")
            params.append(relation_type)
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY weight DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [Synapse.model_validate_json(row["payload"]) for row in rows]

    def reinforce_synapse(self, synapse_id: str, *, delta: float, reason: str | None = None) -> Synapse | None:
        synapse = self.get_synapse(synapse_id)
        if synapse is None:
            return None
        synapse.weight = round(max(0.0, min(1.0, synapse.weight + delta)), 6)
        synapse.reinforcement_count += 1
        synapse.last_reinforced_at = utc_now()
        if reason:
            synapse.evidence_refs.append(f"reinforcement:{reason}")
        return self.add_synapse(synapse)

    def add_belief(self, belief: Belief) -> Belief:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO beliefs
                    (id, status, owner_domain, confidence, review_after, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    belief.id,
                    belief.status,
                    belief.owner_domain,
                    belief.confidence,
                    belief.review_after.isoformat() if belief.review_after else None,
                    self._json(belief),
                ),
            )
        return belief

    def get_belief(self, belief_id: str) -> Belief | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM beliefs WHERE id = ?", (belief_id,)).fetchone()
        return self._load(Belief, row)

    def list_beliefs(
        self,
        *,
        status: str | None = None,
        owner_domain: str | None = None,
        due_before: datetime | None = None,
        limit: int = 100,
    ) -> list[Belief]:
        limit = max(1, min(limit, 1000))
        clauses: list[str] = []
        params: list[object] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if owner_domain:
            clauses.append("owner_domain = ?")
            params.append(owner_domain)
        if due_before is not None:
            # surface beliefs whose review is already due, oldest first
            clauses.append("review_after IS NOT NULL AND review_after <= ?")
            params.append(due_before.isoformat())
        sql = "SELECT payload FROM beliefs"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY review_after ASC LIMIT ?" if due_before is not None else " ORDER BY confidence ASC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [Belief.model_validate_json(row["payload"]) for row in rows]

    def add_dream_run(self, dream_run: DreamRun) -> DreamRun:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO dream_runs
                    (id, mode, started_at, completed_at, summary_path, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dream_run.id,
                    dream_run.mode,
                    dream_run.started_at.isoformat(),
                    dream_run.completed_at.isoformat() if dream_run.completed_at else None,
                    dream_run.summary_path,
                    self._json(dream_run),
                ),
            )
        return dream_run

    def get_dream_run(self, dream_run_id: str) -> DreamRun | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM dream_runs WHERE id = ?", (dream_run_id,)).fetchone()
        return self._load(DreamRun, row)

    def list_dream_runs(self, *, mode: str | None = None, limit: int = 100) -> list[DreamRun]:
        limit = max(1, min(limit, 1000))
        sql = "SELECT payload FROM dream_runs"
        params: list[object] = []
        if mode:
            sql += " WHERE mode = ?"
            params.append(mode)
        sql += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [DreamRun.model_validate_json(row["payload"]) for row in rows]
