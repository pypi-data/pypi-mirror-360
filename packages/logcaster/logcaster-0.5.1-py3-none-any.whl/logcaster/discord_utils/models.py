from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    NaiveDatetime,
    StringConstraints,
)

MAX_EMBED_FIELDS = 25
NameType = Annotated[
    str,
    StringConstraints(
        max_length=255,
        strip_whitespace=True,
    ),
]


class EmbedFieldObject(BaseModel):
    name: NameType
    value: Annotated[str, StringConstraints(max_length=1024)]
    inline: bool = True


class EmbedAuthorObject(BaseModel):
    name: NameType
    url: str | None = None
    icon_url: str | None = None
    proxy_icon_url: str | None = None


class EmbedFooterObject(BaseModel):
    text: Annotated[str, StringConstraints(max_length=2048)]
    icon_url: str | None = None
    proxy_icon_url: str | None = None


def _cast_color(v: str | int) -> int:
    if isinstance(v, int):
        return v
    return int(v, 16)


class EmbedObject(BaseModel):
    title: NameType
    type: Literal['rich'] = 'rich'
    description: Annotated[str, StringConstraints(max_length=4096)]
    url: str | None = None
    timestamp: NaiveDatetime | None = None
    color: Annotated[int, BeforeValidator(_cast_color)] | None = None
    footer: EmbedFooterObject | None = None
    author: EmbedAuthorObject | None = None
    fields: list[EmbedFieldObject] = []

    def model_post_init(self, _: Any) -> None:
        if len(self.fields) > MAX_EMBED_FIELDS:
            raise ValueError(
                f'Embeds can have a maximum of {MAX_EMBED_FIELDS} fields'
            )


class WebhookClientPayload(BaseModel):
    embeds: list[EmbedObject] | None = None
    content: str | None = None

    def model_post_init(self, _: Any) -> None:
        if (not self.embeds) and (not self.content):
            raise ValueError(
                'At least one of `embeds` or `content` must be provided'
            )
