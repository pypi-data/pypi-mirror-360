
# Community Explorer (cx)

`cx` is a bioinformatics tool for network analysis and visualization of gene sets. It takes a list of genes, builds a protein-protein interaction network, identifies communities (functional modules) within the network, and performs functional enrichment analysis to uncover the biological significance of these communities.

## Features

-   **Network Analysis:** Constructs interaction networks from gene lists using the STRING database.
-   **Community Detection:** Uses the Leiden algorithm to identify densely connected communities of genes.
-   **Enrichment Analysis:** Performs functional enrichment analysis on gene communities using g:Profiler.
-   **Interactive Visualization:** A web-based interface built with Streamlit allows for easy input and visualization of results.

## Installation

To install the required dependencies, use `pip` with the `pyproject.toml` file:

```bash
pip install .
```

## Usage

To run the web application, use the following command:

```bash
streamlit run app.py
```

This will start a local web server and open the application in your browser.
