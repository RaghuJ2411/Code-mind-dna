from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from app.services.ai.base import AIServiceError
from app.services.ai.provider_factory import get_provider
def _generate_structured_response(
    *,
    task_type: str,
    system_prompt: str,
    context: dict,
    response_model: type[BaseModel],
    temperature: float = 0.0,
) -> BaseModel:

    # --------------------------------------------------
    # Check whether AI is enabled
    # --------------------------------------------------

    if not settings.ai_enabled:
        _raise_ai_http_exception("AI_DISABLED")

    # --------------------------------------------------
    # Create provider
    # --------------------------------------------------

    provider = get_provider()

    if provider is None:
        logger.warning(
            "AI provider could not be created",
            extra={
                "task_type": task_type,
            },
        )

        _raise_ai_http_exception("CONFIGURATION_ERROR")

    provider_name = provider.__class__.__name__

    # --------------------------------------------------
    # Generate response
    # --------------------------------------------------

    try:
        provider_resp = provider.generate_structured(
            task_type=task_type,
            system_prompt=system_prompt,
            context=context,
            response_schema=response_model.model_json_schema(),
            temperature=temperature,
        )

    except AIServiceError as exc:
        logger.warning(
            "AI mentor provider error",
            extra={
                "task_type": task_type,
                "provider": provider_name,
                "error_code": str(exc),
            },
        )

        _raise_ai_http_exception(str(exc))

    except Exception:
        logger.exception(
            "Unexpected AI mentor provider failure",
            extra={
                "task_type": task_type,
                "provider": provider_name,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI mentor request failed.",
        )

    # --------------------------------------------------
    # Extract metadata
    # --------------------------------------------------

    meta = provider_resp.get("meta", {})
    resolved_provider = meta.get("provider") or provider_name

    # --------------------------------------------------
    # Validate response
    # --------------------------------------------------

    try:
        validated = response_model.model_validate(
            provider_resp.get("result", {})
        )

    except ValidationError:
        logger.exception(
            "AI mentor provider returned invalid structured data",
            extra={
                "task_type": task_type,
                "provider": resolved_provider,
                "latency_ms": meta.get("latency_ms"),
            },
        )

        _raise_ai_http_exception("INVALID_RESPONSE")

    # --------------------------------------------------
    # Log success
    # --------------------------------------------------

    logger.info(
        "AI mentor request completed",
        extra={
            "task_type": task_type,
            "provider": resolved_provider,
            "model": meta.get("model"),
            "latency_ms": meta.get("latency_ms"),
        },
    )

    return validated
