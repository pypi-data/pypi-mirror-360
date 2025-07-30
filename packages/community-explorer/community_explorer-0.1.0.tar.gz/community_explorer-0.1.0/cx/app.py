import streamlit as st
import pandas as pd
from io import StringIO
import cx
import matplotlib.pyplot as plt
import enrichment

st.set_page_config(layout="wide")

st.title("Community Explorer (CX)")

with st.expander("How to Use This App"):
    st.write("""
    This application performs network analysis and functional enrichment on a list of genes.

    **1. Input Your Gene List:**
    -   Enter a list of genes (one per line) in the text box on the sidebar.
    -   Alternatively, you can upload a plain text file containing your gene list.

    **2. (Optional) Upload a Custom GMT File:**
    -   If you have a custom collection of gene sets (e.g., specialized pathways or experimental data), you can upload it as a GMT file.
    -   The GMT file should be a tab-separated text file where each line represents a gene set.
    -   **Format:** `GENESET_NAME <tab> DESCRIPTION <tab> GENE_1 <tab> GENE_2 <tab> ...`
    -   **Example:**
        ```
        MY_CUSTOM_PATHWAY_1	A custom pathway I defined	GENE_A	GENE_B	GENE_C
        MY_CUSTOM_PATHWAY_2	Another custom pathway	GENE_D	GENE_E	GENE_F
        ```

    **3. Analyze:**
    -   Click the "Analyze" button to start the analysis.

    **4. View Results:**
    -   **Network View:** An interactive graph showing the interactions between your genes. Genes are colored by the community they belong to.
    -   **Enrichment Table:** A detailed table of the biological pathways and functions enriched in each community.
    -   **Enrichment Plots:** Bubble plots visualizing the enrichment results.
    """)

st.sidebar.write("""
## Input Controls
""")

gene_list = st.sidebar.text_area("Enter a list of genes, one per line")

uploaded_file = st.sidebar.file_uploader("Or upload a file with a list of genes (one per line)")

gmt_file = st.sidebar.file_uploader("Optional: Upload a custom GMT file for enrichment analysis")

if uploaded_file is not None:
    try:
        gene_list = uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        gene_list = ""

if st.sidebar.button("Analyze"):
    if gene_list:
        with st.spinner("Analyzing gene list..."):
            try:
                genes = [gene.strip() for gene in gene_list.split()]
                
                gmt_token = None
                if gmt_file is not None:
                    with st.spinner("Uploading custom GMT file..."):
                        gmt_token = enrichment.upload_gmt(gmt_file)

                with st.spinner("Fetching interactions and building network..."):
                    G = cx.get_network(genes)
                    communities = cx.get_communities(G)
                
                with st.spinner("Performing enrichment analysis..."):
                    enrichment_results = cx.profile(communities, gmt_token=gmt_token)

                network_tab, table_tab, plot_tab = st.tabs(["Network View", "Enrichment Table", "Enrichment Plots"])

                with network_tab:
                    st.subheader("Gene Interaction Network")
                    fig, ax = plt.subplots(figsize=(10, 10))
                    cx.plot_network(G, communities, ax=ax)
                    st.pyplot(fig)

                with table_tab:
                    st.subheader("Enrichment Analysis")
                    st.dataframe(enrichment_results)
                    st.download_button(
                        label="Download data as CSV",
                        data=enrichment_results.to_csv().encode("utf-8"),
                        file_name="enrichment_results.csv",
                        mime="text/csv",
                    )

                with plot_tab:
                    st.subheader("Enrichment Plots")
                    fig = cx.plot_enrichment(communities, results=enrichment_results)
                    st.pyplot(fig)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
    else:
        st.sidebar.warning("Please enter a gene list or upload a file.")

