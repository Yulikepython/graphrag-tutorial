#!/usr/bin/env python3
"""
GraphRAG Generator Script
A Python script version of the GraphRAG tutorial for automated execution.
"""

import os
from getpass import getpass
from dotenv import load_dotenv
from langchain_community.chains.graph_qa.memgraph import MemgraphQAChain
from langchain_community.graphs import MemgraphGraph
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate as LangChainPromptTemplate

# Load environment variables from .env file
load_dotenv()


def setup_llm(provider="openai"):
    """Setup LLM based on the provider choice."""
    if provider.lower() == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API key not found in environment variables")
            api_key = getpass("Enter your OpenAI API Key: ")
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            print("✅ Using OpenAI API key from .env file")

        llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

    elif provider.lower() == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Google API key not found in environment variables")
            api_key = getpass("Enter your Google API Key: ")
            os.environ["GOOGLE_API_KEY"] = api_key
        else:
            print("✅ Using Google API key from .env file")

        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0,
            convert_system_message_to_human=True
        )
    else:
        raise ValueError("Provider must be 'openai' or 'google'")

    return llm


def setup_memgraph():
    """Setup Memgraph connection."""
    url = os.environ.get("MEMGRAPH_URI", "bolt://localhost:7687")
    username = os.environ.get("MEMGRAPH_USERNAME", "")
    password = os.environ.get("MEMGRAPH_PASSWORD", "")

    try:
        graph = MemgraphGraph(
            url=url, username=username, password=password, refresh_schema=True
        )
        print("✅ Successfully connected to Memgraph!")
        return graph
    except Exception as e:
        print(f"❌ Failed to connect to Memgraph: {e}")
        print("Make sure Memgraph is running on localhost:7687")
        raise


def create_sample_data():
    """Create sample text data for graph generation."""
    return """
    John's title is Director of the Digital Marketing Group. John belongs to the Digital Marketing Group. John works with Jane whose title is Chief Marketing Officer. Jane belongs to the Executive Group. Jane works with Sharon whose title is the Director of Client Outreach. Sharon belongs to the Sales Group.
    """


def create_knowledge_graph(llm, graph, text_data):
    """Create knowledge graph from text data."""
    print("🔄 Generating knowledge graph from text...")

    # Setup graph transformer
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Person", "Title", "Group"],
        allowed_relationships=["TITLE", "COLLABORATES", "GROUP"]
    )

    # Convert text to graph documents
    documents = [Document(page_content=text_data)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)

    # Clear existing data and add new graph
    print("🗑️  Clearing existing graph data...")
    graph.query("MATCH (n) DETACH DELETE n")

    print("➕ Adding new graph data...")
    graph.add_graph_documents(graph_documents)

    # Refresh and display schema
    graph.refresh_schema()
    print("📊 Graph schema:")
    print(graph.get_schema)

    # Debug: Show actual data in the graph
    print("\n🔍 Debug: Checking actual data in graph...")
    try:
        nodes_result = graph.query(
            "MATCH (n) RETURN labels(n), properties(n) LIMIT 10")
        print("Nodes in graph:", nodes_result)

        rels_result = graph.query(
            "MATCH (n)-[r]->(m) RETURN type(r), properties(n), properties(m) LIMIT 5")
        print("Relationships in graph:", rels_result)
    except Exception as e:
        print(f"Debug query failed: {e}")

    return graph_documents


def setup_qa_chain(llm, graph):
    """Setup the question-answering chain."""
    print("🔗 Setting up QA chain...")

    # Create few-shot examples for Cypher generation
    # Updated examples to match actual data structure from debug output
    examples = [
        {
            "question": "What is John's title?",
            "query": "MATCH (p:Person {id: 'John'})-[:TITLE]->(t:Title) RETURN t.id",
        },
        {
            "question": "Who does John collaborate with?",
            "query": "MATCH (p:Person {id: 'John'})-[:COLLABORATES]->(c:Person) RETURN c.id",
        },
        {
            "question": "What is Jane's title?",
            "query": "MATCH (p:Person {id: 'Jane'})-[:TITLE]->(t:Title) RETURN t.id",
        }
    ]

    example_prompt = PromptTemplate.from_template(
        "User input: {question}\nCypher query: {query}"
    )

    # Create a simpler, safer prompt template approach
    # Build the examples string manually to avoid template conflicts
    examples_text = ""
    for example in examples:
        examples_text += f"User input: {example['question']}\nCypher query: {example['query']}\n\n"

    # Create a custom QA chain that completely avoids template issues
    class CustomGraphQAChain:
        def __init__(self, llm, graph, examples_text):
            self.llm = llm
            self.graph = graph
            self.examples_text = examples_text

        def invoke(self, question):
            # Get schema
            schema = self.graph.get_schema

            # Create cypher prompt directly
            cypher_prompt_text = f"""You are a Cypher query expert. Given a schema and a question, you must create a syntactically correct Cypher query to answer the question.
            You must respond with ONLY the query, with no other text, explanation, or context.
            You must use the provided node and relationship labels and property names from the schema.

            Here is the schema:
            {schema}

            Here are some examples:

            {self.examples_text}User input: {question}
            Cypher query: """

            print(f"🔍 Generating Cypher query for: {question}")

            # Generate cypher query using LLM directly
            try:
                cypher_response = self.llm.invoke(cypher_prompt_text)
                cypher_query = cypher_response.content.strip()
                print(f"🔍 Generated Cypher: {cypher_query}")
            except Exception as e:
                print(f"❌ Failed to generate Cypher query: {e}")
                return {"result": f"Failed to generate query: {e}", "intermediate_steps": {}}

            # Execute cypher query
            try:
                context_result = self.graph.query(cypher_query)
                context = str(context_result)
                print(f"📊 Query result: {context}")
            except Exception as e:
                print(f"❌ Cypher execution failed: {e}")
                context = f"Query execution failed: {e}"

            # Create QA prompt directly
            qa_prompt_text = f"""You are a helpful assistant that answers user questions based on the context provided.
            If the context is empty, say you don't know the answer.
            Use only the information provided in the context to answer the question.
            Your answer should be concise and directly answer the question.

            Context:
            {context}

            Question: {question}

            Answer:
            """

            # Generate final answer using LLM directly
            try:
                answer_response = self.llm.invoke(qa_prompt_text)
                final_answer = answer_response.content.strip()
            except Exception as e:
                print(f"❌ Failed to generate answer: {e}")
                final_answer = f"Failed to generate answer: {e}"

            return {
                "result": final_answer,
                "intermediate_steps": {
                    "cypher_query": cypher_query,
                    "context": context
                }
            }

    chain = CustomGraphQAChain(llm, graph, examples_text)

    return chain


def run_sample_queries(chain):
    """Run sample queries to test the system."""
    print("\n🔍 Running sample queries...")

    questions = [
        "What is Johns title?",
        "Who does John collaborate with?",
        "What is Jane's title?"
    ]

    for question in questions:
        print(f"\n❓ Question: {question}")
        try:
            result = chain.invoke(question)
            print(f"💬 Answer: {result['result']}")
            if 'intermediate_steps' in result:
                print(f"🔍 Generated Cypher: {result['intermediate_steps']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"🔧 Debug traceback: {traceback.format_exc()}")

            # Try a simpler query to test connection
            try:
                simple_result = chain.graph.query(
                    "MATCH (n) RETURN count(n) as node_count")
                print(f"🔍 Simple test query result: {simple_result}")
            except Exception as simple_e:
                print(f"❌ Simple query also failed: {simple_e}")


def main():
    """Main function to run the GraphRAG system."""
    print("🚀 Starting GraphRAG Generator...")

    # Check if .env file exists and show API key status
    if os.path.exists('.env'):
        print("✅ .env file found")
        if os.getenv("OPENAI_API_KEY"):
            print("✅ OpenAI API key loaded from .env")
        if os.getenv("GOOGLE_API_KEY"):
            print("✅ Google API key loaded from .env")
    else:
        print("⚠️  .env file not found. API keys will be requested interactively.")

    # Choose LLM provider
    provider = input(
        "Choose LLM provider (openai/google) [openai]: ").strip() or "openai"

    try:
        # Setup components
        llm = setup_llm(provider)
        graph = setup_memgraph()

        # Create knowledge graph
        sample_text = create_sample_data()
        graph_documents = create_knowledge_graph(llm, graph, sample_text)

        # Show what was actually created
        print("\n📋 Verifying created data...")
        try:
            person_nodes = graph.query(
                "MATCH (p:Person) RETURN p.id as person_id")
            print(f"👥 Person nodes created: {person_nodes}")

            title_nodes = graph.query(
                "MATCH (t:Title) RETURN t.id as title_id")
            print(f"💼 Title nodes created: {title_nodes}")

            group_nodes = graph.query(
                "MATCH (g:Group) RETURN g.id as group_id")
            print(f"🏢 Group nodes created: {group_nodes}")
        except Exception as verify_e:
            print(f"⚠️ Could not verify created data: {verify_e}")

        # Setup QA chain
        qa_chain = setup_qa_chain(llm, graph)

        # Run sample queries
        run_sample_queries(qa_chain)

        # Interactive mode
        print("\n💡 You can now ask questions about the graph!")
        print("Type 'exit' to quit.")

        while True:
            question = input("\n❓ Your question: ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                break

            if question:
                try:
                    result = qa_chain.invoke(question)
                    print(f"💬 Answer: {result['result']}")
                    if 'intermediate_steps' in result:
                        print(
                            f"🔍 Generated Cypher: {result['intermediate_steps']}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    # Try to show more debugging info
                    print("🔧 Attempting simple debug query...")
                    try:
                        debug_result = qa_chain.graph.query(
                            "MATCH (n:Person) RETURN n.id LIMIT 3")
                        print(f"📋 Available Person nodes: {debug_result}")
                    except Exception as debug_e:
                        print(f"❌ Debug query failed: {debug_e}")

        print("👋 Goodbye!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
