from nbitk.Tools.vsearch import Vsearch
from snakemake.script import snakemake
import logging
import re
import os
import pandas as pd

config = snakemake.config
vsearch_removeChimera = Vsearch(config)

# set logging to file
handler = logging.FileHandler(snakemake.log[0], mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "vsearch-removeChimera - %(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
vsearch_removeChimera.logger.addHandler(handler)

vsearch_removeChimera = Vsearch(config)
try:

    #  params
    chimera_params = {
        "uchime3_denovo": snakemake.input[0],
        "nonchimeras": snakemake.output[0],
        "relabel_sha1": "",
        "relabel_keep": ""
    }

    vsearch_removeChimera.set_params(chimera_params)

    # Remove the nbitkit loghandler to prevent writing to stdo
    for fh in vsearch_removeChimera.logger.handlers[:]:
        vsearch_removeChimera.logger.removeHandler(fh)

    vsearch_removeChimera.logger.addHandler(handler)

    return_code = vsearch_removeChimera.run()

    # Parse run logs to collect metrics

    sample_name = os.path.split(snakemake.input[0])[1].split("_merged")[0]  # get sample name exluding the extension

    with open(snakemake.log[0], 'r') as file:
        log_content = file.read()

        inReads_match = re.search(r'(\d+)\s+total\s+sequences.', log_content)
        unique_clusters_match = re.search(r'(\d+)\s+unique\s+sequences.', log_content)
        chimeric_match = re.search(r'Found\s+(\d+)', log_content)
        borderline_match = re.search(
            r'and\s+(\d+)(?:\s+\(\d+\.\d+%\))?\s+borderline\s+sequences', log_content
        )
        n_esv_match = re.search(
            r'Found\s+(\d+)(?:\s+\(\d+\.\d+%\))?\s+chimeras,\s+(\d+)(?:\s+\(\d+\.\d+%\))?\s+non-chimeras',
            log_content)

        if inReads_match and chimeric_match and unique_clusters_match and n_esv_match and borderline_match:
            inReads_match = int(inReads_match.group(1))
            chimeric_match = int(chimeric_match.group(1))
            borderline_match = int(borderline_match.group(1))
            unique_clusters_match = int(unique_clusters_match.group(1))  # not used anywhere at the moment;
            n_esv = int(n_esv_match.group(2))

        else:
            raise ValueError("Could not find the required information in the log file")

        #  Write the metrics to a TSV file
    report_df = pd.read_csv(snakemake.input[1], sep="\t")
    report_df['chimeric_reads'] = chimeric_match
    report_df['borderline_reads'] = borderline_match  # also filtered out
    report_df.loc[report_df['Sample'] == sample_name, 'ESVs'] = n_esv
    report_df.to_csv(snakemake.output[1], sep="\t", index=False)


except Exception as e:
    vsearch_removeChimera.logger.error(e, exc_info=True)
    print(e)
    exit(1)
