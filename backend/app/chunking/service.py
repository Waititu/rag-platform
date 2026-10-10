from dataclasses import dataclass


@dataclass
class Chunk:
    index: int
    text: str
    start_char: int
    end_char: int


class ChunkingService:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[Chunk]:
        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0
        index = 0
        text_length = len(text)

        while start < text_length:
            target_end = min(
                start + self.chunk_size,
                text_length,
            )

            end = self._find_boundary(
                text,
                start,
                target_end,
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                actual_start = start + (
                    len(text[start:end])
                    - len(text[start:end].lstrip())
                )

                actual_end = actual_start + len(chunk_text)

                chunks.append(
                    Chunk(
                        index=index,
                        text=chunk_text,
                        start_char=actual_start,
                        end_char=actual_end,
                    )
                )

                index += 1

            if end >= text_length:
                break

            next_start = max(
                end - self.chunk_overlap,
                start + 1,
            )

            start = next_start

        return chunks

    def _find_boundary(
        self,
        text: str,
        start: int,
        target_end: int,
    ) -> int:

        if target_end >= len(text):
            return len(text)

        search_start = start + int(
            self.chunk_size * 0.5
        )

        newline = text.rfind(
            "\n",
            search_start,
            target_end,
        )

        if newline > start:
            return newline

        sentence = max(
            text.rfind(". ", search_start, target_end),
            text.rfind("? ", search_start, target_end),
            text.rfind("! ", search_start, target_end),
        )

        if sentence > start:
            return sentence + 1

        space = text.rfind(
            " ",
            search_start,
            target_end,
        )

        if space > start:
            return space

        return target_end
