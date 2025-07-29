# identity/__main__.py
from importlib.resources import files
import argparse
import subprocess
from pathlib import Path
from edentity.utils.configs import dump_config, dump_multiqc_config, dump_profile_config, get_default_profile, load_config
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="eDentity Metabarcoding Pipeline",
    )

    # Project-specific
    # Make --raw_data_dir required only if --profile is not provided
    parser.add_argument("--raw_data_dir", help="Path to the raw input data directory", required=('--config_file' not in os.sys.argv), )
    parser.add_argument("--work_dir", help="Working directory for outputs and temporary files", required=('--config_file' not in os.sys.argv), )
    parser.add_argument("--profile", help="Snakemake profile to use (e.g., 'slurm', 'galaxy', 'default')",
                        default=None)
    parser.add_argument("--make_json_reports", help="Generate an extended JSON report (default: False)", action="store_true")
    
    # if params are given through config file
    parser.add_argument("--config_file", help="Path to the config file", default = None)
    
    # Fastp params
    parser.add_argument("--average_qual", help="Minimum average quality score (default: 25)", default=25)
    parser.add_argument("--length_required", help="Minimum read length after trimming (default: 100)", default=100)
    parser.add_argument("--n_base_limit", help="Max N bases allowed per read (default: 0)", default=0)

    # PE merging
    parser.add_argument("--maxdiffpct", help="Max percentage difference in overlaps (default: 100)", default=100)
    parser.add_argument("--maxdiffs", help="Max differences in overlap (default: 5)", default=5)
    parser.add_argument("--minovlen", help="Minimum overlap length (default: 10)", default=10)
    parser.add_argument("--fastq_qmax", help="Maximum quality score in FASTQ files (default: 50)", default=50)

    # Primer trimming
    parser.add_argument("--forward_primer", help="Forward primer sequence", required=('--config_file' not in os.sys.argv))
    parser.add_argument("--reverse_primer", help="Reverse primer sequence", required=('--config_file' not in os.sys.argv))
    parser.add_argument("--anchoring", action="store_true", help="Use anchoring for primer matching")
    parser.add_argument("--discard_untrimmed", action="store_true", help="Discard reads without primer match")

    # Quality filtering
    parser.add_argument("--min_length", help="Minimum read length after filtering (default: 100)", default=100)
    parser.add_argument("--max_length", help="Maximum read length after filtering (default: 600)", default=600)
    parser.add_argument("--maxEE", help="Maximum expected errors (default: 1)", default=1)

    # Dereplication
    parser.add_argument("--fasta_width", help="FASTA output line width (default: 0 for single-line)", default=0)

    # Denoising
    parser.add_argument("--alpha", help="Alpha value for chimera detection (default: 2)", default=2)
    parser.add_argument("--minsize", help="Minimum size to retain sequences (default: 4)", default=4)

    # Pipeline settings
    parser.add_argument("--dataType", choices=["Illumina", "AVITI"], help="Sequencing data type", default="Illumina")
    parser.add_argument("--cpu_cores", help="Number of CPU cores to use (default: 10)", default=12, type=int)
    parser.add_argument("--log_level", help="Logging level (default: INFO)", default="INFO")

    # Fixed paths
    parser.add_argument("--license_file", help="Path to LICENSE file (default: LICENSE)", default="LICENSE")
    parser.add_argument("--changelog_file", help="Path to CHANGELOG file (default: CHANGELOG)", default="CHANGELOG")
    parser.add_argument("--conda", help="Path to conda env YAML for main tools (default: envs/vsearch.yaml)")
    parser.add_argument("--bbtoolsConda", help="Path to conda env YAML for BBTools (default: envs/bbtools.yml)")

    # snakemkae extra options
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (equivalent to -n in snakemake)")

    # add common snakemake options e.g -n, -cores e.t.c

    config = vars(parser.parse_args())
    
    
    # writeout a temp config file.
    # the confile file has params from both the default config and the command line args
    # pass this config file to snakemake
    

    # dump snakemake config file (if the user provides a config file, it will be used to override the default params)
    try:
        if config['config_file']:
            user_provided_config = load_config(config['config_file'])
            merged_config = config.copy()
            for k in user_provided_config:
                user_provided_value = user_provided_config[k]
                default = config.get(k)
                if user_provided_value not in [None, "", []]:
                    merged_config[k] = user_provided_value
                elif default not in [None, "", []]:
                    merged_config[k] = default
                else:
                    raise ValueError(f"Missing required value for '--{k}'. Please provide it via command line or config file.")
            config = merged_config

        work_dir = Path(config['work_dir']).resolve()
        snakemake_config_dir = work_dir / "edentity_pipeline_settings"
        snakemake_config_dir.mkdir(parents=True, exist_ok=True)
        snakemake_config_file_path = (snakemake_config_dir / f"{work_dir.name}_snakemake_config.yml").resolve()
        dump_config(config, snakemake_config_file_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    


    # Prepare profile config
    try:
        profile_dir = work_dir / "edentity_pipeline_settings" / f"{os.path.basename(work_dir)}_snakemake_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_path = profile_dir / "config.yaml"
        
        # get default profile
        default_profile = get_default_profile()

        # load the profile config if the user provides a profile
        # otherwise use the default profile
        if config['profile']:
            loaded_profile = load_config(config['profile'])
            # Merge: if a key in loaded_profile is empty, use value from default_profile
            profile = default_profile.copy()
            for k, v in loaded_profile.items():
                if v is not None and v != "":
                    profile[k] = v
        else:
            profile = default_profile
        profile_path = profile_path.resolve()
        dump_profile_config(profile_path, profile)
    except Exception as e:
        print(f"Error while preparing profile config: {e}")
        sys.exit(1)

    # Prepare multiqc config
    try:
        multiqc_config_dir = work_dir / "edentity_pipeline_settings" / "multiqc_config"
        multiqc_config_dir.mkdir(parents=True, exist_ok=True)
        multiqc_config_path = multiqc_config_dir / "config.yaml"
        dump_multiqc_config(multiqc_config_path)
        multiqc_config_path = multiqc_config_path.resolve()
    except Exception as e:
        print(f"Error while preparing multiqc config: {e}")
        sys.exit(1)
    

    # prepare the command to run snakemake
    try:
        cmd = [
            "snakemake",
            "--snakefile", str(files("edentity").joinpath("workflow/Snakefile").resolve()),
            "--workflow-profile", profile_dir,
            "--configfile", snakemake_config_file_path,
        ]
        
        # add snakemake extra options
        if config['dry_run']:
            cmd.append("--dry-run")

        # run snakemake 
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Snakemake failed with error: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Unexpected error while running snakemake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
