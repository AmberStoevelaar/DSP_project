# Simplify: Simplifying Terms and Conditions documents using a Knowledge Graph based RAG
## Overview
This repository contains the implementation of a simple RAG system for simplifying Terms and Conditions (T&Cs) using Knowledge Graphs (KG) and Natural Language Processing (NLP). 
The project employs a Named Entity Recognition (NER) with the use of Spacy-LLm, structured knowledge graph, a defined summarization workflow employing a simple retriever with RAG to process and simplify complex legal documents, in this case focusing on T&Cs.
By turning T&C's into user-friendly format, we aim to shorten the big percentage of people who do not read T&C's before accepting them. We challenge ourselves with this project with the goal of allowing everyone to know what they are agreeing to without any risk of putting their privacy to risk :)

## Repository Structure
### Main Directories and Files
#### Root Files
- **UI.py**: Implements the user interface for interacting with the project components.
- **functionalUI.py**: Provides functional implementations for the UI.
- **config.cfg**: Contains configuration settings for the implementation of Spacy-LLM in the NER.
- **KG.ipynb**: Jupyter notebook containing all the steps taken for this project to come to light

#### Directories
 - **ChatGPT Simplified T&C's**: Contains AI-simplified versions of Terms and Conditions (T&Cs) in PDF format for tools like Apple Software License and RStudio.
 - **data**: Stores the output of the preprocessing steps. That is the entities and relationships obtained from the NER and the Cypher queries later produced with the NER results.
 - **evaluation_results**: Stores the evaluation survey results together with the notebook employed to generate graph visualizations of the results.
 - **Simplified_T&C's**: The resulting simplified T&C documents from our proposed approach.
 - **TCs**: Original T&C documents for processing
 - **tests**: Contains unit tests for validating various components of the project. Test cases for functionality, including summarization, knowledge graph, and query generation.

## Key Objectives
##### Simplification:
- Summarize large, complex T&Cs into concise and structured formats such as bullet points or coherent summaries.
- Preserve essential relationships and context, and most importantly legal accuracy.

##### Knowledge Graph Generation:
- Extract entities, relationships, and structures from the documents using Named Entity Recognition (NER) with the help of Spacy-LLM and graph-based modeling.
- Represent extracted knowledge in the graph database Neo4j for better query and visualization capabilities.

##### User Accessibility:
- Make dense legal content more understandable for users without legal backgrounds, while retaining its core legal meaning.

## How the Project Achieves Its Purpose
##### Text Splitting:
- Breaks large documents into manageable chunks to handle large-scale processing effectively.

##### Summarization:
- TF-IDF and cosine similarity for relevance-based sentence extraction, this will be defined as each node's own description that will be later used for the final summarization step.

##### GPT-powered summarization workflows to produce:
- Cohesive text summaries in a bullet point structure for more clear engagement when reading the document.

##### Knowledge Graph:
- Extracts entities (e.g., persons, organizations, agreements) and relationships from T&Cs.
- Maps them into eFLINT semantics for their integration into a Neo4j knowledge graph for advanced data analysis.

##### Query Generation:
- Creates Cypher queries to insert nodes and relationships into Neo4j.

##### RAG (Retrieval-Augmented Generation):
- Combines retrieved document content with GPT-powered generation for refined results.

## Setup
##### Requirements
- Python 3.9
- Required Python libraries (install via the provided jupyter notebook, remember to un-comment them when running it):
  - langchain
  - spacy
  - PyMuPDF
  - numpy
  - sklearn
  - openai
##### Environment Variables
Create a .env file to store your API keys and your Neo4j password, username and url:
```
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_url
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```
##### Run tests
In case you want to run the defined unit tests you can do it simply by executing:
```
python tests/test_KG.py
```
Remember to have all the necessary Python libraries installed before this step!

##### Run UI
In order to launch the UI, simply execute the following command from the project folder:

```
python functionalUI.py
```
Remember to have all the necessary Python libraries installed and the environment variables file has to be set before this step!


### Contact
For questions or contributions, please contact the project collaborators!
We are more than happy to answer any doubts or listen to constructive feedback! 😊
