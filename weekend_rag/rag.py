import logging
from typing import List
import argparse

# For the REPL
import readline

from haystack import Pipeline, component
from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack_integrations.components.embedders.ollama import (
    OllamaDocumentEmbedder,
    OllamaTextEmbedder,
)
from haystack.components.writers import DocumentWriter

from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchBM25Retriever,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)

from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack.components.joiners.document_joiner import DocumentJoiner


logging.basicConfig(
    format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
)
logging.getLogger("haystack").setLevel(logging.WARNING)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
subparsers.add_parser("ingest")
subparsers.add_parser("query")
parser.add_argument("--model", default="llama3")
parser.add_argument("--emb-model", default="llama3")
args = parser.parse_args()

model = args.model
emb_model = args.emb_model

emb_document_store = ChromaDocumentStore(persist_path="./db")
txt_document_store = ElasticsearchDocumentStore(hosts="http://localhost:9200/")


@component
class Sniffer:
    def run(
        self,
        prompt: str,
    ):
        with open("prompt.txt", "w") as fd:
            fd.write(prompt)

        return {"size": len(prompt)}


@component
class GetFirst:
    @component.output_types(first=str)
    def run(
        self,
        data: List[str],
    ):
        print(f"Text search keywords: {data[0]}")
        return {"first": data[0]}


if args.command == "ingest":
    text_file_converter = TextFileToDocument()
    cleaner = DocumentCleaner(remove_empty_lines=False)
    splitter = DocumentSplitter(split_by="word", split_length=200, split_overlap=35)
    embedder = OllamaDocumentEmbedder(model=emb_model)
    txt_writer = DocumentWriter(txt_document_store)
    emb_writer = DocumentWriter(emb_document_store)

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("text_file_converter", text_file_converter)
    indexing_pipeline.add_component("splitter", splitter)
    indexing_pipeline.add_component("embedder", embedder)
    indexing_pipeline.add_component("txt_writer", txt_writer)
    indexing_pipeline.add_component("emb_writer", emb_writer)

    # Data prep: reading / splitting it in chunks
    indexing_pipeline.connect("text_file_converter.documents", "splitter.documents")
    # Generate embeddings
    indexing_pipeline.connect("splitter.documents", "embedder.documents")
    # Save embeddings and text
    indexing_pipeline.connect("splitter.documents", "txt_writer.documents")
    indexing_pipeline.connect("embedder.documents", "emb_writer.documents")

    documents = ["book_endings.txt"]

    # indexing_pipeline.draw("index.png")

    print(indexing_pipeline.run(data={"sources": documents}))

elif args.command == "query":
    text_embedder = OllamaTextEmbedder(model=emb_model)
    emb_retriever = ChromaEmbeddingRetriever(emb_document_store, top_k=5)
    txt_retriever = ElasticsearchBM25Retriever(
        document_store=txt_document_store, top_k=3
    )
    joiner = DocumentJoiner()
    sniffer = Sniffer()
    template = """Given these documents, answer the question:
                Documents:
                {% for doc in documents %}
                    {{ doc.content }}
                {% endfor %}
                Question: {{query}}
                Answer:"""
    template_keywords_question = """Please write the keywords that would be used to search for documents that would answer the question.
                                  Answer only with the keywords on a single line, separated by spaces. Do not write anything else:
                                  Question:
                                    {{question}}
                                  Keywords:
                                 """
    answer_prompt_builder = PromptBuilder(template=template)
    keywords_question_prompt_builder = PromptBuilder(
        template=template_keywords_question
    )
    llm = OllamaGenerator(
        model=model,
        url="http://localhost:11434/api/generate",
        generation_kwargs={
            "num_predict": 500,
            "temperature": 0.9,
        },
    )
    llm_question_keyword = OllamaGenerator(
        model=model,
        url="http://localhost:11434/api/generate",
        generation_kwargs={
            "num_predict": 100,
            "temperature": 0.1,
        },
    )
    get_first = GetFirst()

    rag_pipeline = Pipeline()
    # Keyword search
    rag_pipeline.add_component(
        "keywords_question_prompt_builder", keywords_question_prompt_builder
    )
    rag_pipeline.add_component("llm_question_keyword", llm_question_keyword)
    rag_pipeline.add_component("txt_retriever", txt_retriever)
    rag_pipeline.add_component("get_first", get_first)

    # Embedded search
    rag_pipeline.add_component("text_embedder", text_embedder)
    rag_pipeline.add_component("emb_retriever", emb_retriever)

    # LLM summary
    rag_pipeline.add_component("joiner", joiner)
    rag_pipeline.add_component("prompt_builder", answer_prompt_builder)
    rag_pipeline.add_component("sniffer", sniffer)
    rag_pipeline.add_component("llm", llm)

    # Pipeline building
    rag_pipeline.connect("text_embedder.embedding", "emb_retriever.query_embedding")
    rag_pipeline.connect("txt_retriever", "joiner")
    rag_pipeline.connect("emb_retriever", "joiner")
    rag_pipeline.connect("joiner.documents", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm")

    rag_pipeline.connect("keywords_question_prompt_builder", "llm_question_keyword")
    rag_pipeline.connect("llm_question_keyword.replies", "get_first.data")
    rag_pipeline.connect("get_first.first", "txt_retriever.query")
    rag_pipeline.connect("prompt_builder", "sniffer")

    # rag_pipeline.draw("query.png")

    while True:
        query = input("> ")
        if query:
            result = rag_pipeline.run(
                data={
                    "prompt_builder": {"query": query},
                    "text_embedder": {"text": query},
                    "keywords_question_prompt_builder": {"question": query},
                }
            )
            print(result["llm"]["replies"][0])
            print(f'Prompt length: {result["sniffer"]["size"]} bytes')
else:
    print("Don't know what to do?")
