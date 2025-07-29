from nbitk.Tools.vsearch import Vsearch
from snakemake.script import snakemake
import logging
import re
import os
import pandas as pd

config = snakemake.config
vsearch_denoise = Vsearch(config)

#  set logging to file
handler = logging.FileHandler(snakemake.log[0], mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "vsearch-denoise - %(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
vsearch_denoise.logger.addHandler(handler)

# TODO: TEST/READ SWARM clustering instead of UNOISE
try:

    #  params
    denoise_params = {
        "cluster_unoise": snakemake.input[0],
        "unoise_alpha": config['alpha'],
        "minsize": config['minsize'],
        "centroids": snakemake.output[0],
        "sizein": "",
        "sizeout": "",
        "fasta_width": "0"}
    vsearch_denoise.set_params(denoise_params)

    # Remove the nbitkit loghandler to prevent writing to stdo
    for fh in vsearch_denoise.logger.handlers[:]:
        vsearch_denoise.logger.removeHandler(fh)
    vsearch_denoise.logger.addHandler(handler)

    return_code = vsearch_denoise.run()

    # Parse run logs to collect metrics

    sample_name = os.path.split(snakemake.input[0])[1].split("_merged")[0]  # get sample name exluding the extension

    with open(snakemake.log[0], 'r') as file:
        log_content = file.read()
        if not log_content.strip():
            denoised = 0
            discarded = 0
            clusters = 0
        else:
            # minsize = int(re.search(r'minsize\s+(\d+)', log_content).group(1))

            denoised = re.search(r'(\d+)\s+seqs', log_content)
            # discarded = re.search(rf'minsize {minsize}:\s+(\d+)', log_content)
            # clusters = re.search(r'Clusters:\s+(\d+)', log_content)

            if denoised:
                denoised = int(denoised.group(1))

                # print(denoised, discarded, clusters)
            else:
                raise ValueError("Could not find the required information in the log file")

        #  Write the metrics to a TSV file
    report_df = pd.read_csv(snakemake.input[1], sep="\t")
    report_df['reads_passed_denoising'] = denoised
    report_df.to_csv(snakemake.output[1], sep="\t", index=False)

except Exception as e:
    vsearch_denoise.logger.error(e, exc_info=True)
    print(e)
    exit(1)
