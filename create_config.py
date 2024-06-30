from pathlib import Path


def create_config():
    """Create the config file"""
    dir_name = Path(__file__).parent.resolve()
    workspace = dir_name / "workspace"
    conf_file = dir_name / "config.yml"
    sample_file = dir_name / "config_sample.yml"

    # Create the workspace
    workspace.mkdir(parents=True, exist_ok=True)

    with open(sample_file, 'r', encoding='utf-8') as file:
        data = file.read().replace('${workspace_dir}', str(workspace))

    with open(conf_file, 'w', encoding='utf-8') as file:
        file.write(data)


if __name__ == "__main__":
    create_config()
