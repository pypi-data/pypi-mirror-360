import pathlib
import pandas as pd
import networkx as nx


DATA_DIR = pathlib.Path() / "reactome"
DATA_FILES = [pathlib.Path() / fname for fname in ("annotations.csv",
                                                   "relationships.csv")]

def download_hierachy():
    relationships = pd.read_csv(
        "https://reactome.org/download/current/ReactomePathwaysRelation.txt",
        sep="\t", header=None, names=["source", "target"])
    relationships = relationships[relationships["source"].str.contains("HSA") & relationships["target"].str.contains("HSA")]
    relationshitps.to_csv(DATA_DIR / "relationships.csv", index=False)
    G = nx.from_pandas_edgelist(relationships, create_using=nx.DiGraph())


def download_annotations():
    annotations = pd.read_csv(
        "https://reactome.org/download/current/Ensembl2Reactome_All_Levels.txt",
        sep="\t", header=None, usecols=[0, 1])
    annotations = annotations[annotations[1].str.contains("HSA")]
    annotations.to_csv(DATA_DIR / "annotations.csv", index=False)


def download():
    annotations = download_annotations()
    hierachy = download_hierarchy()


if not(DATA_DIR.exists()):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
if not all(data_file.exists() for data_file in DATA_FILES):
    print("Downloading data for the reactome dataset.\nThis might take a while...")
    download()

annotations = pd.read_csv(DATA_DIR / "annotations.csv")
relationships = pd.read_csv(DATA_DIR / "relationships.csv")
hierarchy = nx.from_pandas_edgelist(relationships, create_using=nx.DiGraph())
