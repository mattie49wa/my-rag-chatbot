# Project

Revision: 2025-05-02

Deadline: 48 hours to complete from receiving the project

Expected effort: 3 hours of concentrated work

## Introduction

Welcome to the freeflow take-home project. We find that live interview questions that don't match the work, require implementing algorithms that should be Google'd, or rely on knowing “The Trick” aren’t a good predictor of your success working in our team.  
We've therefore designed this question to match your day-to-day freeflow work. You'll have the same freedoms and constraints that a freeflow dev has, with only a few caveats:

- Use whatever IDEs, tools, languages, and technologies you like. We want you to be as productive as possible.
- Google as much as you like. While we personally use (and encourage the use of) generative AI in our work, **we ask that you refrain from generating a complete code solution using generative AI**, as we’d like to see *your* thinking, knowledge, experience, and creativity represented in the solution. 
- You'll have 48 hours from receipt of this package to return a solution. Use this time as you like; put the problem down, take walks, mull it over in the shower - whatever you need

Lastly, we understand that your time is precious. We've targeted this problem to take 3 hours, so that we're not making unreasonable demands on your time.

## Goal

Build a small solution that can answer questions about a set of provided documents. In this project we wish to answer questions about the insurability of a roof on a home (more details below). 

The project consists of implementing 3 core capabilities with 2 optional enhancement tasks.

We don't expect all backend engineers to have extensive experience with generative AI, so the enhancement tasks are optional.
If you do have experience in this space, we recommend attempting to solve these enhancements. 
If you don't, we encourage you to get started and push as far as you can within the allotted time.
Know that solving the optional enhancements demonstrate extra expertise, but are secondary to completing the core tasks effectively. 
Prioritize required tasks before addressing the enhancements.

## Problem

We'd like you to create a solution that analyzes the following documents, and answers a core question regarding policy and the coverage of a home:

Using the wind mitigation report and the training guide provided below: 
is the home roof age compliant with the underwriting guide rules set in the training guide PDF?

- [Wind mitigation report for home](https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/wind_inspection_report.pdf)
- [Training guide](https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/Training-Guide-ATG-03052019_PDF.pdf)

The answer to the question is: The Wind Mitigation Inspection Report reveals that the roof was installed in 2022. 
The training guide requires all dimensional shingle roofs to be 20 years or newer. 
Therefore, the roof can be insured under the guidelines.

## Solution

We'd like you to build a simplified architecture to solve the above problem, consisting of:

- **API Endpoint**:
  Create an endpoint (e.g., `/query`) that accepts a JSON payload with a query and documents to process. Example:
  ```json
  {
  "query": "is the home roof age compliant with the underwriting guide rules set in the training guide PDF?",
  "document_urls": [
    "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/wind_inspection_report.pdf",
    "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/Training-Guide-ATG-03052019_PDF.pdf"
    ]
  }
  ``` 
  This endpoint should process the input document(s) and return an answer when it's ready.
  Consider that LLM requests can often run for a while before returning an answer. Many load balancers and proxies have standard 30 second timeouts.
  Consider what the best (API?) design and architecture would be to solve for this restriction.
  Lastly, we are expecting to see best practices applied to the API design.

- **Processing using an LLM**:
  Use an LLM to generate a coherent answer to the user query, of your choice: e.g. OpenAI, Gemini, Claude, local models via Ollama/LM Studio, Hugging Face, etc.
  Instruct the LLM to answer the query based only on the provided document text and to indicate if the answer cannot be determined from the given text.

- **Deployment**: 
  Create a dockerfile that containerizes the application and a `run.sh` script, that when executed, builds the image and runs the container for the project. 
  Calling port `8080` on the container should provide the access to the API you have developed. 

- **Enhancement 1 (optional)**:
  Add a simple enhancement to demonstrate agent-like capability by adding a Validation Step:
  After generating the initial answer, add a step where the system (or another LLM call with a specific prompt) checks if the answer directly addresses the original query based only on the retrieved context. Append a note if it seems speculative or drifts (e.g., ```{"answer": "...", "confidence_note": "Answer based directly on provided context."}``` or ```{"answer": "...", "confidence_note": "Context does not fully cover the query, answer may be incomplete."}```).

- **Enhancement 2 (optional)**:
  Rather than passing the entire documents as inputs to the LLM, implement a strategy to pre-process and split the documents into smaller, manageable chunks suitable for embedding.
  Choose an appropriate embedding model to generate vector embeddings for each chunk.
  Set up a simple vector store to hold the embeddings. For this exercise, feel free to use a light in-memory solution.
  Implement a function that takes a user query, embeds it using the same model, and retrieves the top K most relevant document chunks from the vector store.
  Pass these document chunks to the LLM with the query of the user and have the LLM  generate a coherent answer to the user
  query, _based only_ on the retrieved document chunks as context.

- **Documentation and Explanation (README.md)**:
  Provide clear instructions on how to set up and run the application.
- Briefly explain key design choices:
  - API design
  - Prompt design for the LLM.
  - Discuss limitations of this simple system.
  - Important: Describe how you would productionize and scale this system.
  - For Enhancement 1:
    - Discuss limitations and optimizations related to validating the output
  - For Enhancement 2:
    - Discuss chunking strategy. 
    - Choice of embedding model and vector store.

We have no preferences with regard to your choice of programming language or libraries used in this project. 
What's important to us, is how you think about the problem and solve for it. 
For that reason, we also ask that you build the solution yourself, and avoid using large frameworks that solve it all for you. 

Your solution must include a `README.md` file that has complete instructions on how to run the solution (assume we don’t have any tooling installed on our machines). 

Your solution must include a `run.sh` file that, when executed, builds and runs your code and produces the outputs mentioned earlier. 
We will not accept solutions that require undocumented steps needed to run the solution (we must be able to run the solution fully only using the `run.sh` file).

Please send us a zip compressed file containing your full project solution, named `yyyy-mm-dd-candidate_name.zip` before the deadline.

## Help

If you have any urgent questions while working on this project, email us at [anders@freeflow.ai](mailto:anders@freeflow.ai) and we’ll get back to you asap.

We’re excited to see your solution, and can’t wait to go over it together. Thanks for your time!