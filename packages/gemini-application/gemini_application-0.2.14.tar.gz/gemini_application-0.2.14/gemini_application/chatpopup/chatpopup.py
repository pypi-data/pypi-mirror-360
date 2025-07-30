from gemini_application.application_abstract import ApplicationAbstract
import os
import time
from langchain_community.document_loaders import PyPDFLoader
from ollama import Client
import chromadb
import re


class ChatPopup(ApplicationAbstract):
    def __init__(self):
        super().__init__()

        # Classes
        self.embeddings_model = None
        self.ollama_client = None
        self.chroma_client = None
        self.chroma_collection = None

        # Variables
        self.langchain_api_key = None
        self.llm_model_version = None
        self.prompt_type = None
        self.chunks = None
        self.docs_dir = None
        self.chroma_dir = None
        self.text_splitter = None
        self.prompt = None
        self.chunk_size = None
        self.chunk_overlap = None
        self.collection_name = None
        self.chromadb_host = None
        self.chromadb_port = None
        self.ollama_host = None
        self.ollama_port = None

    def init_parameters(self, parameters):
        """Function to initialize parameters"""
        for key, value in parameters.items():
            setattr(self, key, value)

        self.initialize_model()

    def calculate(self):
        return "Output calculated"

    def initialize_model(self):
        # API key for accessing langchain model
        os.environ["LANGCHAIN_API_KEY"] = (
            self.langchain_api_key
        )

        # Http ollama connection
        self.ollama_client = Client(host=f"http://{self.ollama_host}:{self.ollama_port}")

        # Http chromaDB storage, on Docker container
        self.chroma_client = chromadb.HttpClient(host=self.chromadb_host, port=self.chromadb_port)

        # Now create or retrieve the collection
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def delete_collection(self):
        self.chroma_client.delete_collection(name=self.collection_name)

    def update_data(self):
        # Step 1: Fetch existing metadata from the collection
        tic = time.time()
        existing_sources = set()
        all_metadata = self.chroma_collection.get(include=["documents", "metadatas"])

        if "metadatas" in all_metadata:
            for meta in all_metadata["metadatas"]:
                if meta and "source" in meta:
                    existing_sources.add(meta["source"])
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Fetched existing metadata from collection ({elapsed_time:.5f} s)")

        # Step 2: List all files and filter out existing ones
        if not os.path.exists(self.docs_dir):
            print("Model: No directory found")
            return

        all_files = [
            f for f in os.listdir(self.docs_dir)
            if os.path.isfile(os.path.join(self.docs_dir, f))
        ]
        new_files = [f for f in all_files if f not in existing_sources]
        print(f"Model: Found {len(new_files)} new files to process")

        # Step 3: Read only new files
        tic = time.time()
        docs_data = self.readfiles(self.docs_dir, filenames=new_files)
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Documents read ({elapsed_time:.5f} s)")

        # Step 4: Process and add new files to ChromaDB
        tic = time.time()
        for filename, text in docs_data.items():
            chunks = self.chunksplitter(text, self.chunk_size)
            embeds = self.getembedding(self.embeddings_model, chunks)
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename} for _ in range(len(chunks))]

            # Add the embeddings to the chromadb
            self.chroma_collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeds,
                metadatas=metadatas
            )
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: New files processed ({elapsed_time:.5f} s)")

        # Step 5: Delete missing files for searching
        missing_files = [f for f in existing_sources if f not in all_files]
        for missing_file in missing_files:
            self.chroma_collection.delete(where={"source": missing_file})
            print(f"Model: Delete data {missing_file}")

    def get_embedding(self, user_message: str):
        response = self.ollama_client.embeddings(
            model="nomic-embed-text",
            prompt=user_message
        )
        return response['embedding']

    def get_response(self, prompt: str) -> str:
        response = self.ollama_client.generate(
            model=self.llm_model_version,
            prompt=prompt,
            stream=False
        )
        # Extract text from response
        return response.model_dump().get("response", "")

    def process_prompt(self, user_message):
        print("processing prompt...")

        # Get embedding of the user query
        tic = time.time()

        query_embed = self.get_embedding(user_message)
        toc = time.time()
        print(f"Model: Embeddings retrieved from user query ({toc - tic:.5f} s)")

        # Retrieve relevant documents
        result = self.chroma_collection.query(
            query_embeddings=query_embed,
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )

        documents = result["documents"][0]
        ids = result["ids"][0]
        metadatas = result["metadatas"][0]

        # Build prompt
        related_text = "\n\n".join(documents)
        # prompt = self.prompt.format(question=user_message, context=related_text)
        prompt = f"Use the following pieces of retrieved context to answer the question. " \
                 f"If you don't know the answer, just say that you don't know. Use three " \
                 f"sentences maximum and keep the answer concise. " \
                 f"Context: {related_text}\n\nQuestion: {user_message}\nAnswer:"

        # Generate response
        tic = time.time()
        response = self.get_response(prompt)
        toc = time.time()
        print(f"Model: Ollama generated response ({toc - tic:.5f} s)")

        # Format shortened citations
        short_citations = []
        short_sources = []

        for i, meta in enumerate(metadatas):
            short_citations.append(ids[i])
            short_sources.append(meta['source'])

        return {
            "answer": response,
            "citations": short_citations,
            "sources": short_sources
        }

    def getembedding(self, embeddings_model, chunks: list[str]):
        # Embed all chunks at the same time
        response = self.ollama_client.embed(
            model=embeddings_model,
            input=chunks
        )
        embeddings = response.get('embeddings', [])

        if not isinstance(embeddings, list) or len(embeddings) != len(chunks):
            raise ValueError(f"Expected {len(chunks)} embeddings, got {len(embeddings)}")

        return embeddings

    def readfiles(self, docs_dir, filenames=None):
        text_contents = {}

        # Use provided filenames or list all from directory
        if filenames is None:
            filenames = os.listdir(docs_dir)

        for filename in filenames:
            file_path = os.path.join(docs_dir, filename)

            if not os.path.isfile(file_path):
                continue

            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                text_contents[filename] = content

            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                content = "\n".join(doc.page_content for doc in documents)
                text_contents[filename] = content

        return text_contents

    def chunksplitter(self, text, chunk_size):
        words = re.findall(r'\S+', text)

        chunks = []
        current_chunk = []
        word_count = 0

        for word in words:
            current_chunk.append(word)
            word_count += 1

            if word_count >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                word_count = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
