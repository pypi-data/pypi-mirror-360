#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import numpy as np
import networkx as nx
from cdlib import algorithms

import matplotlib
import matplotlib.pyplot as plt

from sklearn.metrics import jaccard_score


def get_network(genes):
    df = get_interactions(genes, required_score=0)
    G = nx.from_pandas_edgelist(df, source="preferredName_A", target="preferredName_B", edge_attr="weight")
    return G


def get_communities(G):
    c = algorithms.leiden(G, weights="score")
    return c.communities


def plot_enrichment(communities, results, source=None, top_n=10, cutoff=0.05, 
                    top_n_by_source=False, exclude_source=None, names=None):
    if source is not None:
        if isinstance(source, str):
            source=[source]
        results = results[results.source.isin(source)]
    if exclude_source is not None:
        if isinstance(source, str):
            exclude_source = [exclude_source]
        results = results[~results.source.isin(exclude_source)]
    results = results.sort_values(by=["community", "p_value"], ascending=True)
    results["mlog10p"] = -np.log10(results.p_value)
    results["fold_enrichment"] = (results.intersection_size / results.query_size) / (results.term_size / results.effective_domain_size)

    n_communities = len(communities)
    
    # Process dataframes for each community
    plot_sizes = []
    data = []
    for n, community in enumerate(communities):
        df = results[results.community == n]
        if cutoff is not None:
            # Apply cutoff only if there are significant pathways
            if df[df.p_value <= cutoff].shape[0] > 0:
                df = df[df.p_value <= cutoff]
        if top_n is not None:
            if top_n_by_source:
                df = df.groupby("source").head(top_n)
            else:
                df = df.head(top_n)
        if df.shape[0] < 1:
            continue
        plot_sizes.append(df.shape[0])
        data.append(df)

    # Setup figure with correct sizes
    fig, axes = plt.subplots(nrows=n_communities, ncols=1, sharex=True, 
                             figsize=(10, sum(plot_sizes)), 
                             dpi=150, gridspec_kw={'height_ratios': plot_sizes})
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.90, wspace=0.1, hspace=0.1)
    v = -np.log10(results.p_value)
    norm = plt.Normalize(0, max(v))

    if n_communities == 1:
        axes = [axes]
    else:
        axes = axes.tolist()
        
    for n, ax in enumerate(axes):
        df = data[n]
        df = df.sort_values(by=["source", "p_value"], ascending=False)
        p = ax.scatter(df.fold_enrichment, df.name + " " + df.native, s=df.intersection_size*100, 
                       c=df.mlog10p, cmap="Spectral", alpha=0.5, norm=norm, edgeColors="grey", linewidth=4)
        ax.grid(linestyle="--")
        ax.autoscale(enable=True) 
        title = names[n] if names is not None else "Community {}".format(n + 1)
        ax.set_title(title, fontsize=30)

    mappable = plt.gca().get_children()[0]
   
    cbar = fig.colorbar(mappable, ax=axes, location="right")
    cbar.set_label("-log(p-value)", fontsize=20)
    cbar.ax.tick_params(labelsize=40) 

    sizes = np.sort(results.intersection_size.unique())
    sizes = (pd.cut(sizes, bins=4, retbins=True)[1]).astype(int)
    if sizes[0] == 0: sizes[0] += 1
    for size in sizes:
        plt.scatter([],[], s=size*100, color="k", label=size)
    h, l = plt.gca().get_legend_handles_labels()
    lg = cbar.ax.legend(handles=h, labels=l, title="# Genes", loc='lower center', bbox_to_anchor=(0.5, -0.25),
                    labelspacing=2, borderpad=1, fontsize=20)
    lg.get_title().set_fontsize('20')
    plt.autoscale()
    plt.xlabel("Fold enrichment", fontsize=40)
    return fig


def get_communities_from_search(search, ax=None, plot=True):
    df = get_interactions(search)
    G = nx.from_pandas_edgelist(df, source="preferredName_A", target="preferredName_B", edge_attr="score")
    communities = algorithms.leiden(G, weights="score").communities
    if plot:
        plot_network(G, communities, ax=ax)
    return communities


def plot_network(G, communities=None, ax=None):
    if communities is not None:
        for n, com in enumerate(communities):
            for node in com:
                G.nodes[node]["community"] = n
        colors = [G.nodes[node]["community"] for node in G.nodes()]
        cmap = plt.cm.get_cmap('viridis', max(colors) + 1)
    else:
        colors = "black"
        cmap = None
    pos = nx.spring_layout(G)
    if ax is None:
        nx.draw_networkx(G, pos=pos, cmap=cmap, node_color=colors, with_labels=True)
    else:
        nx.draw_networkx(G, pos=pos, cmap=cmap, node_color=colors, with_labels=True, ax=ax)


def profile(communities, organism="hsapiens", sources=["GO:BP", "GO:MF", "GO:CC", "KEGG", "REAC", "WP", "CORUM", "HP"], 
            user_threshold=0.05, all_results=False, no_iea=False, 
            combined_score=False, measure_underrepresentation=False, 
            domain_scope="annotated", threshold_algo="gSCS", significance_threshold_method="fdr", gmt_token=None):
    url = "https://biit.cs.ut.ee/gprofiler/api/gost/profile/"
    if isinstance(communities, tuple):
        communities = list(communities)
    if not isinstance(communities[0], (list, tuple)):
        communities = [communities]
    query = {str(i): com for i, com in enumerate(communities)}
    
    if gmt_token:
        sources = [gmt_token]

    params = {
        "organism": organism,
        "query": query,
        "sources": sources,
        "user_threshold": user_threshold,
        "all_results": all_results,
        "no_iea": no_iea,
        "combined_score": combined_score,
        "measure_underrepresentation": measure_underrepresentation,
        "domain_scope": domain_scope,
        "threshold_algo": threshold_algo,
        "significance_threshold_method": significance_threshold_method,
        "background": None
    }
    r = requests.post(url, json=params)
    data = r.json()
    df = pd.DataFrame(data["result"])
    df["community"] = df["query"].str.replace("query_", "").astype(int)
    return df


def convert(genes, target="ENTREZGENE_ACC", organism="hsapiens"):
    url = "https://biit.cs.ut.ee/gprofiler/api/util/convert/"
    if isinstance(genes, str):
        genes = re.split(r'\s+', genes)
    params = {
        "organism": organism,
        "target": target,
        "query": genes
    }
    r = requests.post(url, json=params)
    data = r.json()
    df = pd.DataFrame(data["result"])
    return df


def get_interactions(genes, required_score=400, species=9606):
    string_api_url = "https://string-db.org/api"
    output_format = "tsv-no-header"
    method = "network"

    if isinstance(genes, (list, tuple)):
        genes = "\r".join(genes)

    params = {

        "identifiers" : genes, # your protein
        "species" : species, # species NCBI identifier 
        "required_score" : required_score, # threshold of confidence score
    }

    request_url = "/".join([string_api_url, output_format, method])
    results = requests.post(request_url, data=params)
    
    s = results.text
    df = pd.read_csv(pd.io.common.StringIO(s), sep="\t", 
                     names=["stringId_A", "stringId_B", "preferredName_A", "preferredName_B", "ncbiTaxonId", 
                            "score", "nscore", "fscore", "pscore", "ascore", "escore", "dscore", "tscore"])
    df["weight"] = df.score / 1000
    return df