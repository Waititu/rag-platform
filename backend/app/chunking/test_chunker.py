from app.chunking.service import ChunkingService


text = """
Amazon Web Services provides cloud computing infrastructure.

Amazon Simple Storage Service provides object storage.

Amazon Elastic Compute Cloud provides virtual machines.

Amazon Virtual Private Cloud provides isolated networking.

AWS Identity and Access Management controls access.
"""


chunker = ChunkingService(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = chunker.chunk(text)

for chunk in chunks:
    print("=" * 60)
    print(f"INDEX: {chunk.index}")
    print(f"START: {chunk.start_char}")
    print(f"END:   {chunk.end_char}")
    print(chunk.text)
