import yaml

def load_config(confile_path):
    with open(confile_path, "r") as f:
        return yaml.safe_load(f)

# dump dicts to yaml at a given path
def dump_config(config, path):
    with open(path, "w") as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)
    

# extratct the config file from the package
def extract_package_yaml(package_file_path, target_path):
    # config_path = files("edentity").joinpath("workflow/profiles/default/config.yaml")
    with open(target_path, "w") as f:
            f.write(package_file_path.read_text())


def get_multiqc_config():
    return {
        "skip_generalstats": True,
        "show_analysis_paths": False,
        "fn_clean_exts": [
            ".gz",
            ".fastq",
            "_R1",
            "_R2",
            "_merged"
        ],
        "custom_data": {
            "edentity_summary": {
                "file_format": "tsv",
                "section_name": "eDentity Pipeline Summary",
                "plot_type": "table"
            }
        },
        "module_order": [
            "edentity_summary",
            "fastp",
            "cutadapt"
        ],
        "table_columns_visible": {
            "edentity_summary": {
                "Sample": True,
                "read_pairs": True,
                "merged_percent": True,
                "primer_trimmed_reads": True,
                "passed_quality_filtering": True,
                "dereplicated_reads": True,
                "reads_passed_denoising": True,
                "n_esv": True
            }
        }
    }

def get_default_profile():
    return {
        "jobs": "30",
        "latency-wait": "30",
        "use-conda": "False",
        "printshellcmds": "True",
        "rerun-incomplete": "True",
        "keep-incomplete": "True",
        
    }

def dump_multiqc_config(target_path):
    default_config = get_multiqc_config()
    dump_config(default_config, target_path)


def dump_profile_config(target_path, profile): # this should be flexible to handle different profiles, e.g slurm, galaxy, default.
    dump_config(profile, target_path)