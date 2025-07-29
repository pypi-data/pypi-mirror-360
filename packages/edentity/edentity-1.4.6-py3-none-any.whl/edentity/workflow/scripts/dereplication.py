from nbitk.Tools.vsearch import Vsearch
from snakemake.script import snakemake
import logging
import re
import os
import pandas as pd

config = snakemake.config
vsearch_derep = Vsearch(config)

# set logging to file
handler = logging.FileHandler(snakemake.log[0], mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "vsearch-dereplication - %(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
vsearch_derep.logger.addHandler(handler)

try:

    #  params
    derep_params = {
        "fastx_uniques": snakemake.input[0],
        "fastaout": snakemake.output[0],
        "sizeout": "",
        "fasta_width": config['fasta_width'],
        "fastq_qmax": config['fastq_qmax']}  # to allow for high quality data
    vsearch_derep.set_params(derep_params)

    # Remove the nbitkit loghandler to prevent writing to stdo
    for fh in vsearch_derep.logger.handlers[:]:
        vsearch_derep.logger.removeHandler(fh)
    vsearch_derep.logger.addHandler(handler)

    return_code = vsearch_derep.run()

    # Parse run logs to collect metrics

    sample_name = os.path.split(snakemake.input[0])[1].split("_merged")[0]  # get sample name exluding the extension

    with open(snakemake.log[0], 'r') as file:
        log_content = file.read()
        if not log_content.strip():
            dereplicated_match = 0
        else:
            inReads_match = re.search(r'(\d+)\s+seqs', log_content)
            dereplicated_match = re.search(r'(\d+)\s+unique\s+sequences', log_content)

            if inReads_match and dereplicated_match:
                inReads_match = int(inReads_match.group(1))
                dereplicated_match = int(dereplicated_match.group(1))
                # print(inReads_match, dereplicated_match)
            else:
                raise ValueError("Could not find the required information in the log file")
        #  Write the metrics to a TSV file
    report_df = pd.read_csv(snakemake.input[1], sep="\t")
    report_df['dereplicated_reads'] = dereplicated_match
    report_df.to_csv(snakemake.output[1], sep="\t", index=False)


except Exception as e:
    vsearch_derep.logger.error(e, exc_info=True)
    print(e)
    exit(1)
