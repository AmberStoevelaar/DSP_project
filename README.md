# Simplify: Simplifying Terms and Conditions documents using a Knowledge Graph based RAG
## Overview
This repository contains the implementation of a simple RAG system for simplifying Terms and Conditions (T&Cs) using Knowledge Graphs (KG) and Natural Language Processing (NLP). 
The project employs a Named Entity Recognition (NER) with the use of Spacy-LLm, structured knowledge graph, a defined summarization workflow employing a simple retriever with RAG to process and simplify complex legal documents, in this case focusing on T&Cs.

## Repository Structure
### Main Directories and Files
#### Root Files
- **UI.py**: Implements the user interface for interacting with the project components.
- **functionalUI.py**: Provides functional implementations for the UI.
- **config.cfg**: Contains configuration settings for the implementation of Spacy-LLM in the NER.

#### Directories
 - **ChatGPT Simplified T&C's**: Contains AI-simplified versions of Terms and Conditions (T&Cs) in PDF format for tools like Apple Software License and RStudio.
 - **data**: Stores the output of the preprocessing steps. That is the entities and relationships obtained from the NER and the Cypher queries later produced with the NER results.
 - **evaluation_results**: Stores the evaluation survey results together with the notebook employed to generate graph visualizations of the results.
 - **Simplified_T&C's**: The resulting simplified T&C documents from our proposed approach.
 - **TCs**: Original T&C documents for processing
 - **tests**: Contains unit tests for validating various components of the project. Test cases for functionality, including summarization, knowledge graph, and query generation.
 - 
