Chat-API is a project aimed at integrating Language Learning Model (LLM) tools through an API interface. It is currently in development and seeks to incorporate advanced LLM tools, similar to the OpenAI API.


How to use it.


Current Implementation.
 The project is currently working on implementing the vectorial database Weaviate.

Future Development:
Plans for future development include the integration of additional types of vectorial databases and the inclusion of a Dockerfile for virtualization in a production environment. This will allow for self-hosting of all the utilized tools, including Open Source LLMs.



## Download  and install the project:
To download the project, you can clone it using git:


```bash
git clone https://github.com/Cruiz102/chat-api.git
```

~~~
Warning : Requirements and list of all dependecies may not be complete. The requirements.txt soon is going to be update as well as a dockerfile for hosting the servers. 
~~~


## Setting The application:

### Enviroment Variables
Enable the following environment variables in your console instance. To do so, start your terminal in the project folder and execute these commands:
```bash
export WEAVIATE_URL=<YOUR WEAVIATE URL>

export WEAVIATE_API_KEY=<YOUR WEAVIATE API KEY>

export OPENAI_API_KEY=<YOUR OPENAI API KEY>

export CLASSNAME= <Class name for adding your objects to the database>
```

Your OpenAI key can be found in your API manager. For the Weaviate URL and API key, visit the Weaviate web console. You'll need to create an account and utilize the free version of their cloud solution for testing. Create a new cluster under this plan to obtain the url and api key.




# Starting APIs Servers:

The current implementation includes two servers: ingest.py and main.py. Both are implemented using FastAPI. To initialize them, execute the following commands:

For hosting the main.py server.
```bash
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

For hosting the ingest.py server.
```bash
uvicorn ingest:app --host 0.0.0.0 --port 3001 --reload
```

After initialization, you can access both APIs via their respective URLs.




## Adding a WebUI for interacting with the project.

To interact with the API, a slightly modified version of the following project can be used for connecting to the server:

[Chatbot Frontend Github Repository](https://github.com/Cruiz102/chatbot-frontend)

Follow the installation instructions provided in the repository. Note that you'll need to install Node.js on your machine to execute the installation.


## Vercel Deployment

The project has the confugurations for hosting the main server with vercel. You can access it in [here](https://vercel.com/).