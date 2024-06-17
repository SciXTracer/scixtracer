# SciXTracer

Library to trace transformations on datasets

## Why

- When developing data science workflow, it is a pain to write 
dedicated code to interact with data storage
- When deploying a data science workflow is is a pain to re-write the data processing
script to match the infrastruction IOs
- Ensuring traceability (FAIR principles) of data and results is an extra-work like adding metadata 
generation in the analysis script

SciXTracer tends to encapsulate storage, deployment and traceability into a unique API.
One code for all AI platforms 

## Functionalities

- Unique flexible dataset API using annotations
- Script runner with auto record (results + trace)
- Extensible: API is plugable to implement any scalable back end
