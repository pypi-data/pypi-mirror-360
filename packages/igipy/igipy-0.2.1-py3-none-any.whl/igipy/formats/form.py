from io import BytesIO
from struct import Struct
from typing import ClassVar, Self

from pydantic import BaseModel, Field, NonNegativeInt

from igipy.formats import FileModel
from igipy.formats.base import StructModel


class ChunkHeader(StructModel):
    _struct: ClassVar = Struct(">4sI")

    fourcc: bytes = Field(min_length=4, max_length=4)
    length: NonNegativeInt


class Chunk(BaseModel):
    header: ChunkHeader
    content: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, header: ChunkHeader) -> Self:
        content = stream.read(header.length)
        return cls(header=header, content=content)


class FORMChunk(Chunk):
    @classmethod
    def model_validate_stream(cls, stream: BytesIO, header: ChunkHeader) -> Self:
        content = stream.read(4)
        return cls(header=header, content=content)


class FORM(FileModel):
    content: list[Chunk]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        content = []

        while stream.tell() < len(stream.getvalue()):
            chunk_header = ChunkHeader.model_validate_stream(stream=stream)

            if chunk_header.fourcc == b"FORM":
                chunk = FORMChunk.model_validate_stream(stream, chunk_header)
            else:
                chunk = Chunk.model_validate_stream(stream, chunk_header)

            content.append(chunk)

        if stream.read(1) != b"":
            raise ValueError("Expected end of stream")

        return cls(content=content)
