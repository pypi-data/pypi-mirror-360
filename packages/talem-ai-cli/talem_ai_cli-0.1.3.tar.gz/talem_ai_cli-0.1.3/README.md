# Talem CLI Tool

This CLI tooling allows for the addition of more context to be used by Talem AI chatbot.

## Usage:

```bash
pip install talem-ai-cli
talemai
```
## Technologies used:

- Click (to build a beautiful CLI)
- PyPDF (to load and read the pdf documents)
- Request (to load online resources to lead. **beware of copyright**)
- Langchain (to convert the pdfs into vector embeddings)
- AstraDB (to store the new vector embeddings)
- Pyfiglet (to make a fashionable and large title greeting)
- Setuptools (allows to config project to be a module in pip)
- Github Actions (CI/CD pipeline whvih builds package and publishes it to Pip)
- Beautifulsoup (allows for web crawling)
- Cohere (vector embedding translation)

## Commit Guide:

- To publish your commit to Pip, use the prefix "Publish:" in your commit message. You should add this to a merge commit message to main branch. 
  
- You must update the verison of the package in `setup.py` when publishing to Pip. If you do not, the build command run by Github Actions will fail and the changes will not be pushed to the Pip registry. You will know this is the case if you get the following error:

![image](https://github.com/user-attachments/assets/5d6af954-c848-4647-8c47-6168e93462d8)

