import typer
import cx
import enrichment
import pandas as pd

app = typer.Typer()

@app.command()
def analyze(
    genes: str = typer.Argument(..., help="A list of genes separated by spaces"),
    gmt_file: str = typer.Option(None, "--gmt", help="Path to a custom GMT file for enrichment analysis"),
    output_file: str = typer.Option("enrichment_results.csv", "--output", help="Path to save the enrichment results (CSV)"),
    plot_file: str = typer.Option(None, "--plot", help="Path to save the network plot (PNG)"),
):
    """
    Analyze a list of genes to find communities and perform enrichment analysis.
    """
    gene_list = genes.split()

    gmt_token = None
    if gmt_file:
        print(f"Uploading custom GMT file: {gmt_file}")
        gmt_token = enrichment.upload_gmt(gmt_file)

    print("Fetching interactions and building network...")
    G = cx.get_network(gene_list)
    communities = cx.get_communities(G)

    print("Performing enrichment analysis...")
    enrichment_results = cx.profile(communities, gmt_token=gmt_token)

    print(f"Saving enrichment results to {output_file}")
    enrichment_results.to_csv(output_file, index=False)

    if plot_file:
        print(f"Saving network plot to {plot_file}")
        fig, ax = plt.subplots(figsize=(10, 10))
        cx.plot_network(G, communities, ax=ax)
        fig.savefig(plot_file)

    print("Analysis complete.")

if __name__ == "__main__":
    app()