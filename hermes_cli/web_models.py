"""Pydantic request/response models for the Hermes dashboard web server."""

from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import BaseModel, SecretStr, StrictBool, field_validator


class ConfigUpdate(BaseModel):
    config: dict
    profile: str | None = None

class EnvVarUpdate(BaseModel):
    key: str
    value: str
    profile: str | None = None
    # Bearer for the OPENAI_BASE_URL connectivity probe (auth-gated /v1/models otherwise looks
    # "reachable but empty"); ignored by plain PUT /api/env.
    api_key: str = ""
    # Sent by the Desktop's provider-connection forms: a key a tool panel also asks for (Gemini,
    # xAI...) then still counts as a provider setup in shared metrics.
    provider_setup: bool = False

class EnvVarDelete(BaseModel):
    key: str
    profile: str | None = None

class EnvVarReveal(EnvVarDelete):
    pass

class MemoryProviderConfigUpdate(BaseModel):
    values: dict[str, Any] = {}

class MemoryProviderSetupRequest(BaseModel):
    values: dict[str, Any] = {}

class CustomEndpointModelDetail(BaseModel):
    """One ``/v1/models`` row with the routing metadata a gateway may advertise on a
    reasoning alias (``gpt-5.6-sol-high`` → ``gpt-5.6-sol`` @ ``high``). See #93622."""
    id: str
    canonical_model: str | None = None
    reasoning_effort: str | None = None

class CustomEndpointUpdate(BaseModel):
    id: str = ""
    name: str
    base_url: str
    model: str
    api_key: str | None = None
    # Same choices as the CLI's custom-provider setup; "" = auto-detect at runtime.
    # None (older UI payload) leaves a hand-written api_mode alone.
    api_mode: Literal["", "chat_completions", "codex_responses", "anthropic_messages"] | None = None
    context_length: int | None = None
    discover_models: bool = True
    make_default: bool = False
    models: list[str] | None = None
    model_details: list[CustomEndpointModelDetail] | None = None

class MessagingPlatformUpdate(BaseModel):
    enabled: bool | None = None
    env: dict[str, str] = {}
    clear_env: list[str] = []
    # Explicit body profile beats the switcher's query param (same as other scoped writes).
    profile: str | None = None

class TelegramOnboardingStart(BaseModel):
    bot_name: str | None = None

class TelegramOnboardingApply(BaseModel):
    allowed_user_ids: list[str]
    profile: str | None = None

class WhatsAppOnboardingStart(BaseModel):
    mode: str | None = "bot"
    allowed_users: str | None = ""
    profile: str | None = None

class WhatsAppOnboardingApply(BaseModel):
    mode: str | None = None
    allowed_users: str | None = None
    profile: str | None = None

class AudioTranscriptionRequest(BaseModel):
    data_url: str
    mime_type: str | None = None

class ManagedFileUpload(BaseModel):
    path: str
    data_url: str
    overwrite: bool = True

class ChatImageUpload(BaseModel):
    data_url: str
    filename: str | None = None

class ManagedDirectoryCreate(BaseModel):
    path: str

class ManagedFileDelete(BaseModel):
    path: str
    recursive: bool = False

class ModelAssignment(BaseModel):
    """POST /api/model/set — assign a provider/model to a slot.

    scope="main" → model.provider + model.default; scope="auxiliary" → auxiliary.<task>.*
    (task="" = every auxiliary slot, task="__reset__" = reset every slot to provider="auto").
    """
    scope: str
    provider: str
    model: str
    task: str = ""
    # Auxiliary only. Omitted → the task's override is left alone; explicit null → cleared
    # (inherit the main agent's effort); a level → set. ``model_fields_set`` tells the two apart.
    reasoning_effort: str | None = None
    # Custom/local endpoint URL + key, honored on main AND auxiliary slots: the runtime resolvers
    # read model.base_url / auxiliary.<task>.base_url (+ .api_key) and ignore OPENAI_BASE_URL.
    base_url: str = ""
    api_key: str = ""
    confirm_expensive_model: bool = False
    profile: str | None = None

class MoaModelSlot(BaseModel):
    provider: str = ""
    model: str = ""
    # Declared so a GET round-trip doesn't strip and wipe it.
    reasoning_effort: str | None = None
    enabled: bool = True

class _MoaReferenceControls(BaseModel):
    # None = no per-preset override; inherits auxiliary.moa_reference.timeout (900s default).
    reference_timeout: float | None = None
    degraded_reference_policy: Literal["loud", "silent"] = "loud"

    @field_validator("reference_timeout", mode="before")
    @classmethod
    def _validate_reference_timeout(cls, value: Any) -> float | None:
        """Reject JSON booleans/non-finite values before float coercion."""
        if value is None or value == "":
            return None
        try:
            timeout = float(value) if not isinstance(value, bool) else math.nan
        except (TypeError, ValueError) as exc:
            raise ValueError("reference_timeout must be a finite positive number") from exc
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("reference_timeout must be a finite positive number")
        return timeout

class MoaPresetPayload(_MoaReferenceControls):
    reference_models: list[MoaModelSlot] = []
    aggregator: MoaModelSlot = MoaModelSlot()
    # None = temperature omitted from API calls (provider default), as for single-model agents.
    reference_temperature: float | None = None
    aggregator_temperature: float | None = None
    # Newer per-preset knobs (moa_config._normalize_preset): optional for older clients,
    # declared so GET round-trips don't erase them.
    fanout: str | None = None
    enabled: bool = True

class MoaConfigPayload(_MoaReferenceControls):
    default_preset: str = "default"
    active_preset: str = ""
    presets: dict[str, MoaPresetPayload] = {}
    # Backward-compatible flat payload fields for older dashboard/desktop clients.
    reference_models: list[MoaModelSlot] = []
    aggregator: MoaModelSlot = MoaModelSlot()
    reference_temperature: float | None = None
    aggregator_temperature: float | None = None

    fanout: str | None = None
    enabled: bool = True
    profile: str | None = None

class FsWriteText(BaseModel):
    path: str
    content: str

class GitPathBody(BaseModel):
    path: str

class GitFileBody(BaseModel):
    path: str
    file: str | None = None

class GitPrListBody(BaseModel):
    path: str
    branches: list[str] = []
    # PRs a session recovered from its transcript — known by number, not branch.
    numbers: list[int] = []

class SessionPrScanBody(BaseModel):
    ids: list[str] = []

class GitCommitBody(BaseModel):
    path: str
    message: str
    push: bool = False

class GitWorktreeAddBody(BaseModel):
    path: str
    name: str | None = None
    branch: str | None = None
    base: str | None = None
    existingBranch: str | None = None

class GitWorktreeRemoveBody(BaseModel):
    path: str
    worktreePath: str
    force: bool = False

class GitBranchSwitchBody(BaseModel):
    path: str
    branch: str

class CuratorPause(BaseModel):
    paused: bool

class LearningNodeRef(BaseModel):
    id: str
    profile: str | None = None

class LearningNodeEdit(BaseModel):
    id: str
    content: str
    profile: str | None = None

class DebugShareRequest(BaseModel):
    # Redaction scrubs credential-shaped tokens before logs leave the machine; opt-out only.
    redact: bool = True
    lines: int = 200  # recent log lines in the summary tail (full logs are separate)

class TTSSpeakRequest(BaseModel):
    text: str

class VoiceLiveSessionRequest(BaseModel):
    """POST /api/audio/voice-live/session: the renderer's WebRTC SDP offer plus optional prior
    text turns (``{"type":"message","role":..,"content":[..]}``) to seed the live voice model."""
    sdp: str
    history: list[dict[str, Any]] | None = None

class TTSLeaseRequest(BaseModel):
    """POST /api/audio/tts-lease: ``lease`` names the toggle/surface holding the lease
    (``desktop:read-aloud``, ``desktop:conversation``); ``active`` True acquires + warms, False releases."""
    lease: str
    active: bool = True

class STTLeaseRequest(BaseModel):
    """POST /api/audio/stt-lease: ``lease`` names the voice-input session holding the lease
    (``desktop:voice-input:<renderer>``); ``active`` True acquires + pre-loads the local
    STT model, False releases. Unlike TTS, release never unloads (shared engine)."""
    lease: str
    active: bool = True

class OAuthSubmitBody(BaseModel):
    session_id: str
    code: str

class BulkDeleteSessions(BaseModel):
    ids: list[str]
    profile: str | None = None

class SessionImport(BaseModel):
    sessions: list[dict[str, Any]]
    profile: str | None = None

class SessionRename(BaseModel):
    title: str | None = None
    archived: bool | None = None
    hidden: bool | None = None  # also used by cross-profile reconciliation
    pinned: bool | None = None  # durable "keep" (Desktop pins); exempt from auto_archive
    # Read-state watermark (sessions.last_read_at): True = unread, False = read now, None = leave.
    unread: bool | None = None
    profile: str | None = None  # session owned by another profile (opens its state.db)

class SessionOwnerBackfill(BaseModel):
    """POST /api/sessions/owner-backfill (legacy migration). ``profile`` scopes WHICH state.db is
    stamped; the stamped value is always that store's own serving-profile identity — the caller
    cannot inject an arbitrary owner."""
    profile: str | None = None

class SessionPrune(BaseModel):
    older_than_days: float | None = 90
    source: str | None = None
    profile: str | None = None
    # Extended filters (all optional, ANDed — mirrors the CLI flags); *_before/after = epoch s
    started_before: float | None = None
    started_after: float | None = None
    title_like: str | None = None
    end_reason: str | None = None
    cwd_prefix: str | None = None
    min_messages: int | None = None
    max_messages: int | None = None
    model_like: str | None = None
    provider: str | None = None
    user_id: str | None = None
    chat_id: str | None = None
    chat_type: str | None = None
    branch_like: str | None = None
    min_tokens: int | None = None
    max_tokens: int | None = None
    min_cost: float | None = None
    max_cost: float | None = None
    min_tool_calls: int | None = None
    max_tool_calls: int | None = None
    include_archived: bool = False
    dry_run: bool = False

class CronJobCreate(BaseModel):
    paused: StrictBool = False
    paused_reason: str | None = None
    prompt: str = ""
    schedule: str
    name: str = ""
    deliver: str = "local"
    skills: list[str] | None = None
    model: str | None = None
    provider: str | None = None
    base_url: str | None = None
    script: str | None = None
    context_from: Any | None = None
    enabled_toolsets: list[str] | None = None
    workdir: str | None = None
    no_agent: bool = False

class CronJobUpdate(BaseModel):
    updates: dict

class AutomationBlueprintInstantiate(BaseModel):
    blueprint: str  # blueprint key, e.g. "morning-brief"
    values: dict[str, Any] = {}  # filled slot values from the form

class MCPServerCreate(BaseModel):
    name: str
    url: str | None = None
    command: str | None = None
    args: list[str] = []
    env: dict[str, str] = {}  # KEY=VALUE for stdio servers (API keys, etc.)
    auth: str | None = None  # "none" | "oauth" | "header" | None
    # One-time provisioning input; persisted only to the profile's .env.
    bearer_token: SecretStr | None = None
    profile: str | None = None

class MCPServersReplace(BaseModel):
    # Whole-map replace (name → raw config) for the GUI mcp.json editor.
    servers: dict[str, dict[str, Any]] = {}
    profile: str | None = None

class MCPEnabledToggle(BaseModel):
    enabled: bool
    profile: str | None = None

class MCPCatalogInstall(BaseModel):
    name: str
    env: dict[str, str] = {}  # KEY=VALUE for entries declaring required env vars
    enable: bool = True
    profile: str | None = None

class PairingApprove(BaseModel):
    platform: str
    code: str = ""
    request_id: str = ""
    profile: str | None = None

class PairingRevoke(BaseModel):
    platform: str
    user_id: str
    profile: str | None = None

class WebhookCreate(BaseModel):
    name: str
    description: str | None = None
    events: list[str] = []
    prompt: str | None = None
    script: str | None = None
    skills: list[str] = []
    deliver: str = "log"
    deliver_only: bool = False
    deliver_chat_id: str | None = None
    secret: str | None = None  # omit to auto-generate

class WebhookEnabledToggle(BaseModel):
    enabled: bool

class CredentialPoolAdd(BaseModel):
    provider: str
    api_key: str  # OAuth pooling stays CLI-only (needs an interactive browser flow)
    label: str | None = None

class MemoryProviderSelect(BaseModel):
    provider: str  # "" or "built-in" disables the external provider

class MemoryReset(BaseModel):
    target: str = "all"  # "all" | "memory" | "user"

class BackupRequest(BaseModel):
    output: str | None = None  # defaults to a timestamped zip in the home dir

class ImportRequest(BaseModel):
    archive: str
    # --force: the spawned `hermes import` has stdin=DEVNULL, so its "Continue? [y/N]" prompt would
    # hit EOF and abort; the dashboard confirms in its own modal.
    force: bool = False

class HookCreate(BaseModel):
    event: str
    command: str
    matcher: str | None = None
    timeout: int | None = None
    # Also write the consent allowlist entry; without it the hook won't fire until approved.
    approve: bool = True

class HookDelete(BaseModel):
    event: str
    command: str

class SkillInstallRequest(BaseModel):
    identifier: str
    profile: str | None = None

class SkillUninstallRequest(BaseModel):
    name: str
    profile: str | None = None

class SkillsUpdateRequest(BaseModel):
    profile: str | None = None

class ProfileCreate(BaseModel):
    name: str
    clone_from: str | None = None
    clone_from_default: bool = False  # legacy clients; new ones send clone_from explicitly
    clone_all: bool = False
    # Opt-in: also copy the source's messaging channels (bot tokens, allowlists, platform sections).
    # Default False — a copied bot credential makes two profiles collide over one bot.
    clone_channels: bool = False
    no_skills: bool = False
    description: str | None = None
    provider: str | None = None
    model: str | None = None
    # Profile-builder additions, applied best-effort AFTER the profile dir exists (a hiccup never 500s).
    mcp_servers: list[MCPServerCreate] = []
    keep_skills: list[str] = []  # skills to KEEP: non-empty = replace semantics (unlisted seeded ones disabled)
    # Installed async via `hermes -p <name> skills install` (skills_hub.SKILLS_DIR is import-time-bound,
    # so HERMES_HOME can't redirect it); PIDs go back for the UI to poll.
    hub_skills: list[str] = []

class ProfileRename(BaseModel):
    new_name: str

class ProfileExport(BaseModel):
    extra_files: dict[str, str] = {}  # extra root-level files, filename → text
    output: str = ""  # archive path; empty → a staging path under HERMES_HOME

class ProfileImport(BaseModel):
    archive: str  # profile .tar.gz on the backend's filesystem
    name: str | None = None  # overrides the name inferred from the archive root

class ProfileSoulUpdate(BaseModel):
    content: str

class ProfileActiveUpdate(BaseModel):
    name: str

class ProfileDescriptionUpdate(BaseModel):
    description: str = ""

class ProfileModelUpdate(BaseModel):
    provider: str
    model: str

class ProfileDescribeAuto(BaseModel):
    overwrite: bool = False

class SkillToggle(BaseModel):
    name: str
    enabled: bool
    profile: str | None = None

class SkillCreate(BaseModel):
    name: str
    content: str
    category: str | None = None
    profile: str | None = None

class SkillContentUpdate(BaseModel):
    name: str
    content: str
    profile: str | None = None

class ToolsetToggle(BaseModel):
    enabled: bool
    profile: str | None = None

class ToolsetProviderSelect(BaseModel):
    provider: str
    # Web-only scope 'search' | 'extract'; omitted → whole-provider (legacy web.backend path).
    capability: str | None = None
    profile: str | None = None

class ToolsetModelSelect(BaseModel):
    model: str
    provider: str | None = None
    profile: str | None = None

class ToolsetEnvUpdate(BaseModel):
    env: dict[str, str]
    profile: str | None = None

class ToolsetPostSetup(BaseModel):
    key: str
    profile: str | None = None

class TerminalBackendSelect(BaseModel):
    backend: str
    profile: str | None = None

class RawConfigUpdate(BaseModel):
    yaml_text: str
    profile: str | None = None

class ThemeSetBody(BaseModel):
    name: str

class FontSetBody(BaseModel):
    font: str

class _AgentPluginInstallBody(BaseModel):
    identifier: str
    force: bool = False
    enable: bool = True
    # Install by curated-catalog name (resolves repo + pinned SHA server-side).
    catalog_name: str | None = None
    # Pin a custom source to one full 40-hex commit SHA (same contract as ``--ref``).
    ref: str | None = None

class _PluginProvidersPutBody(BaseModel):
    memory_provider: str | None = None
    context_engine: str | None = None

class _PluginVisibilityBody(BaseModel):
    hidden: bool

