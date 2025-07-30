import requests
from functools import lru_cache
from gprofiler import GProfiler

gp = GProfiler(
    user_agent='CX',
    return_dataframe=True,
)

@lru_cache(maxsize=128)
def profile(communities, cutoff=0.05):
    results = []
    for n, cluster in enumerate(communities):
        r = gp.profile(organism='hsapiens', no_evidences=False,
                       user_threshold=cutoff, query=cluster)
        if r.shape[0] == 0:
            print("Community has zero enriched terms/pathways:")
            print(cluster)
        else:
            r["community"] = n
            r["gene_set"] = pd.Series(cluster)
            results.append(r)
    return pd.concat(results)

def get_token_form_response(response):
    if response.status_code == 200:
        token = response.json()['organism']

    else:
        try:
            error_message = 'Error: {}'.format(response.json()['message'])
        except:
            error_message = 'Error, status code {}'.format(response.status_code)
        raise AssertionError(error_message)
    return token

def upload_gmt(filename):
    if filename.endswith(".gmt"):
        with open(filename) as f:
            response = requests.post(
                'https://biit.cs.ut.ee/gprofiler/api/gost/custom/',
                json={'gmt':f.read(),
                'name': filename})

    elif filename.endswith(".zip"):
        with open(filename, 'rb') as f:
            response = requests.post(
                'https://biit.cs.ut.ee/gprofiler/api/gost/custom/zip',
                files={'zipfile':f})
    else:
        raise ValueError("Supply either a gmt file or a zip file containing gmt files")
    token = get_token_form_response(response)
    print(token)
    return token