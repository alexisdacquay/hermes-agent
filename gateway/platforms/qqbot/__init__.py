"""QQBot platform package. Re-exports adapter symbols so existing import paths
(``from gateway.platforms.qqbot import QQAdapter, check_qq_requirements``) keep working.
Sub-modules: constants, utils, crypto (AES-256-GCM), onboard (QR), chunked_upload, keyboards."""

from .adapter import (
    QQAdapter,
    QQCloseError,
    _coerce_list,
    _ssrf_redirect_guard,
    check_qq_requirements,
)
from .chunked_upload import (
    ChunkedUploader,
    UploadDailyLimitExceededError,
    UploadFileTooLargeError,
)
from .crypto import decrypt_secret, generate_bind_key
from .keyboards import (
    ApprovalRequest,
    InlineKeyboard,
    InteractionEvent,
    build_approval_keyboard,
    build_approval_text,
    build_update_prompt_keyboard,
    parse_approval_button_data,
    parse_interaction_event,
    parse_update_prompt_button_data,
)
from .onboard import BindStatus, build_connect_url, qr_register
from .utils import build_user_agent, coerce_list, get_api_headers

__all__ = [
    "ApprovalRequest",
    "BindStatus",
    "ChunkedUploader",
    "InlineKeyboard",
    "InteractionEvent",
    "QQAdapter",
    "QQCloseError",
    "UploadDailyLimitExceededError",
    "UploadFileTooLargeError",
    "_coerce_list",
    "_ssrf_redirect_guard",
    "build_approval_keyboard",
    "build_approval_text",
    "build_connect_url",
    "build_update_prompt_keyboard",
    "build_user_agent",
    "check_qq_requirements",
    "coerce_list",
    "decrypt_secret",
    "generate_bind_key",
    "get_api_headers",
    "parse_approval_button_data",
    "parse_interaction_event",
    "parse_update_prompt_button_data",
    "qr_register",
]
