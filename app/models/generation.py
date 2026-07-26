"""Contrato validado para uma geração no Estúdio."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class SubjectType(StrEnum):
    PRESET = "preset"
    TEXT = "text"


class Texture(StrEnum):
    ORGANIC = "organic"
    COLOR = "color"
    MONO = "mono"
    MOSAIC = "mosaic"


class Depth(StrEnum):
    COMFORTABLE = "comfortable"
    MARKED = "marked"
    INTENSE = "intense"


TEXTURE_ENGINE: dict[Texture, str] = {
    Texture.ORGANIC: "pink_noise",
    Texture.COLOR: "random_dots",
    Texture.MONO: "random_dots_bw",
    Texture.MOSAIC: "colorido",
}

DEPTH_MU: dict[Depth, float] = {
    Depth.COMFORTABLE: 0.28,
    Depth.MARKED: 0.36,
    Depth.INTENSE: 0.48,
}


class GenerationParams(BaseModel):
    """Parâmetros amigáveis da UI, normalizados para o núcleo matemático."""

    subject_type: SubjectType = SubjectType.PRESET
    subject: str = "esfera"
    texture: Texture = Texture.MOSAIC
    depth: Depth = Depth.COMFORTABLE
    seed: int | None = Field(default=None, ge=0, le=4_294_967_295)
    mu: float | None = Field(default=None, ge=0.15, le=0.60)
    eye_separation: int = Field(default=200, ge=120, le=280)
    width: int = Field(default=800, ge=160, le=1600)
    height: int = Field(default=600, ge=120, le=1200)

    @model_validator(mode="after")
    def validate_subject(self) -> GenerationParams:
        self.subject = self.subject.strip()
        if self.subject_type is SubjectType.TEXT:
            if not self.subject:
                raise ValueError("Digite um texto para esconder.")
            if len(self.subject) > 12:
                raise ValueError("O texto pode ter no máximo 12 caracteres.")
        if self.eye_separation >= self.width:
            raise ValueError("O conforto visual precisa ser menor que a largura da imagem.")
        return self

    @property
    def engine_texture(self) -> str:
        return TEXTURE_ENGINE[self.texture]

    @property
    def engine_mu(self) -> float:
        return self.mu if self.mu is not None else DEPTH_MU[self.depth]
