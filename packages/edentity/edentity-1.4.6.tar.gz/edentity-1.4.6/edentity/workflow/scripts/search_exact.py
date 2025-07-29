from nbitk.Tools.vsearch import Vsearch
from snakemake.script import snakemake
import logging
import pandas as pd
from Bio import SeqIO
import os

config = snakemake.config
vsearch_exact = Vsearch(config)

# set logging to file
handler = logging.FileHandler(snakemake.log[0], mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "vsearch-searchExact - %(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
vsearch_exact.logger.addHandler(handler)


try:

    #  params
    search_exact_params = {
        "search_exact": snakemake.input[0],
        "db": snakemake.input[1],
        "output_no_hits": "",
        "maxhits": "1",
        "otutabout": snakemake.output[0],
    }

    vsearch_exact.set_params(search_exact_params)

    # Remove the nbitkit loghandler to prevent writing to stdo
    for fh in vsearch_exact.logger.handlers[:]:
        vsearch_exact.logger.removeHandler(fh)
    vsearch_exact.logger.addHandler(handler)

    # call up the vsearch_exact
    return_code = vsearch_exact.run()

    sample_esv_df = pd.read_csv(snakemake.output[0], sep="\t")

    # Add fasta sequence to sample ESV_table
    if sample_esv_df.shape[0] > 0:  # check if there are ESVs in the sample
        for record in SeqIO.parse(snakemake.input[1], "fasta"):
            sample_esv_df.loc[sample_esv_df['#OTU ID'] == record.id, 'sequence'] = str(record.seq)

    else:
        # the fasta file is empty, so we create an empty sequence column
        # first assert the file is empty
        assert os.path.getsize(snakemake.input[1]) == 0, "Fasta file is not empty but no ESVs found."

    # write out the ESV table
    sample_esv_df.to_csv(snakemake.output[0], sep="\t", index=False)

except Exception as e:
    vsearch_exact.logger.error(e, exc_info=True)
    print(e)
    exit(1)
