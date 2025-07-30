# SCMCP

An MCP server for scRNA-Seq analysis  with natural language!

## 🪩 What can it do?

- IO module like read and write scRNA-Seq data with natural language
- Preprocessing module,like filtering, quality control, normalization, scaling, highly-variable genes, PCA, Neighbors,...
- Tool module, like clustering, differential expression etc.
- Plotting module, like violin, heatmap, dotplot
- cell-cell communication analysis
- Pseudotime analysis
- enrichment analysis

## ❓ Who is this for?

- Anyone who wants to do scRNA-Seq analysis natural language!
- Agent developers who want to call scanpy's functions for their applications

## 🌐 Where to use it?

You can use scmcp in most AI clients, plugins, or agent frameworks that support the MCP:

- AI clients, like Cherry Studio
- Plugins, like Cline
- Agent frameworks, like Agno 


## 📚 Documentation

scmcphub's complete documentation is available at https://docs.scmcphub.org


## 🎬 Demo

A demo showing scRNA-Seq cell cluster analysis in a AI client Cherry Studio using natural language based on scmcp

https://github.com/user-attachments/assets/93a8fcd8-aa38-4875-a147-a5eeff22a559

## 🏎️ Quickstart

### Install

Install from PyPI
```
pip install scmcp
```
you can test it by running
```
scmcp run
```

#### run scnapy-mcp locally
Refer to the following configuration in your MCP client:

check path
```
$ which scmcp 
/home/test/bin/scmcp
```

> it has many tools , so it couldn't work if you model context is not large...More time, I recommend it is backend mcp server for scanpy-mcp, liana-mcp,cellrank-mcp, so they can use shared Anndata object.

```
"mcpServers": {
  "scmcp": {
    "command": "/home/test/bin/scmcp",
    "args": [
      "run"
    ]
  }
}
```

#### run scmcp remotely
Refer to the following configuration in your MCP client:

run it in your server
```
scmcp run --transport shttp --port 8000
```

Then configure your MCP client in local AI client, like this:
```

"mcpServers": {
  "scmcp": {
    "url": "http://localhost:8000/mcp"
  }
}
```

## Intelligent Tool Selection (Experimental)

SCMCP implements an intelligent tool selection system to optimize performance and reduce token usage. 

### How it Works

The intelligent tool selection system operates in two phases:
1. **Search_tool**: First identifies the most relevant tools for your analysis
2. **run_tool**: Then runs only the selected tools, reducing token consumption


### Usage

1. Ensure you have the latest version of scmcp-shared installed:
```bash
pip install --upgrade scmcp-shared
```

2. Start the server with intelligent tool selection enabled:
```bash
export API_KEY=sk-***
export BASE_URL="https://api.openai.com/v1"
export MODEL="gpt-4o"
scmcp run --transport shttp --port 8000 --tool-mode auto
```

3. Configure your MCP client to connect to the server:
```json
{
  "mcpServers": {
    "scmcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```


## 🤝 Contributing

If you have any questions, welcome to submit an issue, or contact me(hsh-me@outlook.com). Contributions to the code are also welcome!

## Citing
If you use scmcp in for your research, please consider citing  following works: 
> Wolf, F., Angerer, P. & Theis, F. SCANPY: large-scale single-cell gene expression data analysis. Genome Biol 19, 15 (2018). https://doi.org/10.1186/s13059-017-1382-0

> Dimitrov D., Schäfer P.S.L, Farr E., Rodriguez Mier P., Lobentanzer S., Badia-i-Mompel P., Dugourd A., Tanevski J., Ramirez Flores R.O. and Saez-Rodriguez J. LIANA+ provides an all-in-one framework for cell–cell communication inference. Nat Cell Biol (2024). https://doi.org/10.1038/s41556-024-01469-w

> Badia-i-Mompel P., Vélez Santiago J., Braunger J., Geiss C., Dimitrov D., Müller-Dott S., Taus P., Dugourd A., Holland C.H., Ramirez Flores R.O. and Saez-Rodriguez J. 2022. decoupleR: ensemble of computational methods to infer biological activities from omics data. Bioinformatics Advances. https://doi.org/10.1093/bioadv/vbac016

> Weiler, P., Lange, M., Klein, M. et al. CellRank 2: unified fate mapping in multiview single-cell data. Nat Methods 21, 1196–1205 (2024). https://doi.org/10.1038/s41592-024-02303-9

