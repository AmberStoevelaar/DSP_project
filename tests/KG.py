import os
import json
import spacy
from collections import Counter
from pathlib import Path
from wasabi import msg
from spacy_llm.util import assemble

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import langchain
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from neo4j import GraphDatabase

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI

#### Split text with overlap ####
def split_text(combined_text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=60
    )
    return text_splitter.split_text(combined_text)

#### Adding descriptions per node based on each text chunk ####
def summarize_section(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    if not sentences:
        return "No summary available"

    try:
        # TF-IDF (sentence embedding)
        vectorizer = TfidfVectorizer(stop_words='english')
        sentence_vectors = vectorizer.fit_transform(sentences).toarray()

        avg_vector = np.mean(sentence_vectors, axis=0).reshape(1, -1)
        similarities = cosine_similarity(avg_vector, sentence_vectors)

        # most relevant
        most_relevant_index = np.argmax(similarities)
        return sentences[most_relevant_index]

    # in case there is empty input
    except ValueError:
        return "No summary available"

# NER with spacy-llm
def run_pipeline(combined, config_path, filename, examples_path=None, verbose=False):
    if not os.getenv("OPENAI_API_KEY"):
        msg.fail("OPENAI_API_KEY env variable was not found. Set it and try again.", exits=1)

    sections = split_text(combined)
    nlp = assemble(config_path, overrides={} if examples_path is None else {"paths.examples": str(examples_path)})

    # Initialize counters and storage
    processed_data = []
    entity_counts = Counter()
    relation_counts = Counter()

    for section in sections:
        summary = summarize_section(section)
        doc = nlp(summary)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        relations = [(doc.ents[r.dep].text, r.relation, doc.ents[r.dest].text) for r in doc._.rel]

        # processed data
        processed_data.append({
            'original_text': section,
            'summary': summary,
            'entities': entities,
            'relations': relations})

        entity_counts.update([ent[1] for ent in entities])
        relation_counts.update([rel[1] for rel in relations])

    with open(filename, 'w') as f:
        json.dump(processed_data, f)

    # msg.text(f"Entity counts: {entity_counts}")
    # msg.text(f"Relation counts: {relation_counts}")

# config_path = Path("config.cfg")
# examples_path = None
# verbose = True

# file_apple = run_pipeline(combined_apple, config_path, 'apple_processed_data.json', None, verbose)

#### Cypher Query creation for Neo4j ####
def classify_and_generate_queries(json_data, file_path):
    nodes = {}
    relationships = []

    # Enhanced mapping function for entity types based on eFLINT elements
    def map_eflint_type(entity_type, entity_name):
        if 'http://' in entity_type or 'https://' in entity_name:
            return 'FACT'
        if entity_type in ['CARDINAL', 'ORDINAL']:
            return 'NUMBER'
        if entity_type == 'ORG':
            if 'terms' in entity_name.lower() or 'conditions' in entity_name.lower() or 'agreement' in entity_name.lower():
                return 'DUTY'
            else:
                return 'ACTOR'
        if 'section' in entity_name.lower() or 'section' in entity_type.lower():
            return 'SECTION'
        mapping = {
            'PERSON': 'ACTOR',
            'EVENT': 'EVENT',
            'LAW': 'DUTY',
            'WORK_OF_ART': 'ACT',
            'CONDITION': 'CONDITION',
            'DATE': 'DATE',
        }
        return mapping.get(entity_type, 'FACT')

    # Process summaries and associate them with entities
    for item in json_data:
        summary = item.get('summary', 'No summary available')
        entities = item.get('entities', [])
        relations = item.get('relations', [])

        for entity in entities:
            entity_name, entity_type = entity[:2]
            mapped_type = map_eflint_type(entity_type, entity_name)
            node_id = f"{entity_name.replace(' ', '_')}_{mapped_type}"
            if node_id not in nodes:
                nodes[node_id] = {
                    'name': entity_name,
                    'type': mapped_type,
                    'descriptions': [summary],  # Start with the current summary
                }
            else:
                nodes[node_id]['descriptions'].append(summary)  # Append additional summaries

        # Add relationships if present
        for relation in relations:
            src_id = f"{relation[0].replace(' ', '_')}_{map_eflint_type(entity_type, relation[0])}"
            tgt_id = f"{relation[2].replace(' ', '_')}_{map_eflint_type(entity_type, relation[2])}"
            relationship_type = relation[1].replace(' ', '_').replace('-', '_')
            relationships.append((src_id, relationship_type, tgt_id))

    # Create Cypher queries for nodes
    node_queries = [
        f"""
        MERGE (n:{data['type']} {{name: '{data['name'].replace("'", "")}'}})
        SET n.id = '{node_id.replace("'", "")}', 
        n.descriptions = {json.dumps([desc.replace("'", "") for desc in data['descriptions']])}
        """
        for node_id, data in nodes.items() if data['type'] != 'NUMBER'
    ]

    # Create Cypher queries for relationships
    relationship_queries = [
        f"""
        MATCH (a), (b)
        WHERE a.id = '{rel[0].replace("'", "")}' AND b.id = '{rel[2].replace("'", "")}'
        MERGE (a)-[:{rel[1].replace("'", "")}]->(b)
        """
        for rel in relationships
    ]

    queries = node_queries + relationship_queries

    # Save queries to a text file
    with open(file_path, 'w') as file:
        for query in queries:
            file.write(query.strip() + '\n')

    return queries

#### Storing queries ####
# with open('apple_processed_data.json', 'r') as file:
#     json_data = json.load(file)

# queries_apple = classify_and_generate_queries(json_data, 'apple_cypher_queries.txt')


#### Neo4j graph creation ####
def execute_queries(queries, uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for query in queries:
            session.run(query)
    driver.close()

# uri = "neo4j://localhost:7687"
# user = "neo4j"
# password = "movies11"

# execute_queries(queries_apple, uri, user, password)


#### Neo4j Connection ####
class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_all_summaries(self):
        with self.driver.session() as session:
            query = """
            MATCH (n)
            RETURN DISTINCT n.descriptions AS descriptions
            """
            results = session.run(query)
            summaries = []
            for record in results:
                descriptions = record["descriptions"]
                if descriptions:
                    summaries.extend(descriptions)
            return list(set(summaries))


#### Simplified summarization workflow in chunks ####
def summarize_in_chunks(summaries, llm):
    # summaries to single text
    combined_text = " ".join(summaries)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    split_texts = text_splitter.split_text(combined_text)

    # summarize each split / chunk
    chunk_prompt = PromptTemplate.from_template(
        """Summarize the following text while preserving key relationships, events, and timelines:
        {text}
        Helpful Answer:"""
    )
    llm_chain = LLMChain(llm=llm, prompt=chunk_prompt)

    chunk_summaries = []
    for chunk in split_texts:
        summary = llm_chain.run({"text": chunk})
        chunk_summaries.append(summary)

    # combination into final summary
    final_prompt = PromptTemplate.from_template(
        """Combine the following summaries into a cohesive final summary:
        {text}
        Helpful Answer:"""
    )
    final_chain = LLMChain(llm=llm, prompt=final_prompt)
    final_summary = final_chain.run({"text": " ".join(chunk_summaries)})

    return final_summary


#### Clearing graph in case new usage ####
def clear_graph(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    driver.close()


#### Simplified summarization workflow in bullet points (Chat-GPT structure) ####
def summarize_in_points(summaries, llm):
    # summaries to single text
    combined_text = " ".join(summaries)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=70)
    split_texts = text_splitter.split_text(combined_text)

    # summarize each split / chunk
    chunk_prompt = PromptTemplate.from_template(
        """Summarize the following text into a structured format with bullet points and headings, ensuring that key relationships and events are preserved: 
        {text} 
        Helpful Answer:"""
    )
    llm_chain = LLMChain(llm=llm, prompt=chunk_prompt)

    chunk_summaries = []
    for chunk in split_texts:
        summary = llm_chain.run({"text": chunk})
        chunk_summaries.append(summary)

    # combination into final summary
    final_prompt = PromptTemplate.from_template(
        """Combine the following summaries into a structured format with bullet points and headings, 
        while keeping the same structure, into a cohesive final summary: 
        {text} 
        Helpful Answer:"""
    )
    final_chain = LLMChain(llm=llm, prompt=final_prompt)
    final_summary = final_chain.run({"text": " ".join(chunk_summaries)})

    return final_summary


#### RAG Workflow for chunk summarization ####
def rag_summarization_with_chunks(uri, user, password):
    # retrieve descriptions
    kg = KnowledgeGraph(uri, user, password)
    summaries = kg.get_all_summaries()
    kg.close()

    if not summaries:
        print("No summaries found in the knowledge graph.")
        return "No summaries found in the knowledge graph."

    unique_summaries = list(set(summaries))
    # print("Unique Descriptions Retrieved:")
    # for idx, summary in enumerate(unique_summaries, start=1):
    #     print(f"{idx}: {summary}")

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    final_summary = summarize_in_chunks(unique_summaries, llm)
    return final_summary

# Perform RAG summarization with chunking
# apple_par_summary = rag_summarization_with_chunks(uri, user, password)


#### RAG Workflow for bullet point summarization ####
def rag_summarization_with_points(uri, user, password):
    # retrieve descriptions
    kg = KnowledgeGraph(uri, user, password)
    summaries = kg.get_all_summaries()
    kg.close()

    if not summaries:
        print("No summaries found in the knowledge graph.")
        return "No summaries found in the knowledge graph."

    unique_summaries = list(set(summaries))
    # print("Unique Descriptions Retrieved:")
    # for idx, summary in enumerate(unique_summaries, start=1):
    #     print(f"{idx}: {summary}")

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    final_summary = summarize_in_points(unique_summaries, llm)
    return final_summary

# Perform RAG summarization with chunking
# apple_points_summary = rag_summarization_with_points(uri, user, password)