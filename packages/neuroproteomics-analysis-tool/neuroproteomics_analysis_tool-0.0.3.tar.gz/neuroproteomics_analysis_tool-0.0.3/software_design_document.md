# NeuroProteomics Analysis Tool (NPAT) Software Design Document


## 1. Introduction
### 1.1 Purpose
The Software Design Document describes the architecture and system design for the NeuroProteomics Analysis Tool (NPAT), a
package to perform enrichment analysis on gene abundance data and determine a risk score for developing neurological diseases.
NPAT is designed to help scientists, doctors, and patients determine their risk for early detection and screening to allow for preventative treatment.
This document is intended for anyone who will be
involved in the implementation of the system.

### 1.2 Background

### 1.2 Project Summary



The introduction and overview section sets the stage for the entire software design document. It should provide a high-level project summary, including goals, project scope, and primary features. This section should also explain the document's purpose and who it's for, making sure readers understand why the information is essential.

A strong introduction typically includes the following:

A brief description of the software system  
The project's objectives and key requirements  
An overview of what's in the document
Any important background information


## 2) System architecture

The system architecture section is a crucial part of a software design document. It describes the overall structure of the software system, including its major components and subsystems and how they relate to each other. This section shows how different system parts work together to achieve the desired functionality.

Key elements to include in the system architecture section are:

A high-level diagram of the architecture
Description of major components and what they do
Explanation of design patterns and architectural styles used
Discussion of important design decisions and trade-offs

## 3) Data design

The data design section focuses on how the software system stores, manages, and processes information, including details about the database structure, data models, and data processing techniques.

Essential aspects to cover in the data design section include:

Database structure and table layouts
Data flow diagrams
Data validation and integrity rules
How data will be stored and retrieved

## 4) Interface design

The interface design section describes how different parts of the system will communicate with each other and interact with external systems or services. This includes both internal interfaces between modules and external APIs or integration points.

Key elements to include in the interface design section are:

API specifications and protocols
Message formats and data structures
How errors and exceptions will be handled
Security and authentication methods

## 5) Component design

The component design section provides detailed information about individual modules or components within the system. This includes their specific functionality, what inputs they need and outputs they produce, and any algorithms or data structures they use.

For each major component, consider including:

Purpose and responsibilities
Input and output specifications
Algorithms and processing logic
Dependencies on other components or external systems

## 6) User interface design

The user interface design section focuses on how users interact with the software system. This includes details about the user interface's layout, navigation, functionality, and specific design considerations or usability requirements.

Key elements to include in this section are:

Wireframes or mockups of key screens
Description of user workflows and interactions
Accessibility considerations

## 7) Assumptions and dependencies

This section outlines any assumptions made during the design process and any external dependencies or constraints that may impact the system's implementation.

Consider including:

Technical assumptions about the development environment
Dependencies on external libraries or services
Constraints related to hardware, software, or infrastructure
Any regulatory or compliance requirements

Glossary of terms

Project Overview: A brief introduction introducing the project's purpose, scope, and objectives

System Architecture: A high-level diagram showing the major components and their relationship

Component Specifications: Detailed descriptions of each component, including its functionality, interfaces, and data structures

Part 1: Proteomics and biological pathways database

Description: Automate the maintenance of database to automatically sync with panther pathways and protein information
Contains the following tables:

Part 2: NeuroProteomics Analysis Tool (NPAT)

Description: Python class that does an enrichment analysis starting from a gene abundance dataframe and returning which pathways are overexpressed/repressed with statistical significance included
Contains the following methods/functions:
    1)connect_to_db
        input:
        operations:
        output:

    2)get_sample_ids
    3)get_samples
    4)relative_expression_filter
    5)pathway_gene_count
    6)expected_gene_count
    7)fold_change
    8)enrichment_analysis

Part 3: Text-based user interface

Description: TUI that should allow user to run multiple enrichment analysis async on old and new samples then save results to database
Contains the following functions/methods:
    1) Display greeting and description of tool plus basic usage
    2) Identify .env in working directory and ask user to confirm or provide another file then load env file for connection to database
    3) Menu with samples tab to show samples that are already present in DB or upload new samples (gene abundance dataframes)
    4) Select multiple samples from the same host and run enrichment analysis on all of them
    5) Track progress of enrichment analysis
    6) Display and save results after enrichment analysis is done
    7) Maybe view but not edit database
    8) should be tabbedcontent widget to separate functionality
Part 4: Graph analysis/neural network analysis

Interface Design: Descriptions of how the software interacts with other system, including APIs and protocols
Data Design: Details about the data models and database design
User Interface Design: Descriptions of the user interface, including layouts, controls, and interactions
Error Handling and Recovery: Strategies for handling errors and ensuring system stability
Dependencies: A list of external dependencies, such as libraries or services
