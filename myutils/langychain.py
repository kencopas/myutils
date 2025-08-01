from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from flask import Flask, jsonify

from myutils.logging import chat_log


class LangyChain:
    """Easy deployment of a langchain QA Chain.

    Basic Usage:
        lc = LangyChain().load_docs('./docs', '*.txt')  # Reads all txt files in ./docs
        lc.send("Hello, please summarize these documents.")  # Prints to console and logs to log file
    """

    def __init__(self, *, model: str = 'gpt-4', temperature: int = 0):

        # Create LLM
        self.llm = ChatOpenAI(
            model_name=model,
            temperature=temperature
        )

        # Create the embeddings
        self.embeddings = OpenAIEmbeddings()

    def load_docs(self, path: str, glob: str, *, chunk_size: int = 500, chunk_overlap: int = 50):
        """Loads vector data, performs similarity search with query, passes query and relevant docs to llm
        
        This method loads vectorized data from a chroma data store. Then, it vectorizes the user's query
        and performs a similarity search between the query and the documents. The top doc_k relevant documents
        are retrieved and passed to the LLM, along with the user query and the response is returned.

        Example:
            query: 'Who is Martin Luther King?'
            doc_k: 5

        In the above example, the top 5 documents that are most relevant to Martin Luther King are retrieved.
        The LLM is then given these 5 documents to refer to, as well as the user's query. The LLM uses these
        documents to construct a response to the user's query.
        """

        # Initialize DirectoryLoader, specify the directory and glob
        loader = DirectoryLoader(
            path,
            glob=glob,
            loader_cls=TextLoader
        )

        # Intialize the TextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Load and split the documents with the DirectoryLoader and TextSplitter
        documents = loader.load()
        chunks = splitter.split_documents(documents)

        # Embed the document chunks into vectors and save the vectorstore to a local path
        Chroma.from_documents(
            chunks,
            embedding=self.embeddings,
            persist_directory="db"
        )

        return self

    def send(self, query: str, *, doc_k: int = 3):

        # Load the vectorstore into memory
        vectorstore = Chroma(
            persist_directory="db",
            embedding_function=self.embeddings
        )

        # Create a retriever to retreieve the top k most similar documents
        retriever = vectorstore.as_retriever(search_kwargs={"k": doc_k})

        # Create the QA Chain to manage the llm and document retirever during user prompting
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            chain_type="stuff"
        )

        # Send a query to the QA Chain and save the response
        response = qa_chain.invoke(query)

        chat_log(
            User=response['query'],
            Model=response['result']
        )

        return response['result']

