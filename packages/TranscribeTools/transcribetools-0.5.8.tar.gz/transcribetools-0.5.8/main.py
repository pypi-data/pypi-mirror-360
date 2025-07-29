from datetime import datetime
from pathlib import Path
from tkinter.filedialog import askdirectory
import toml
import whisper
import rich
from rich.prompt import Prompt
import rich_click as click
from result import Result, is_ok, is_err, Ok, Err


from transcribetools.model import save_config_to_toml, get_config_from_toml

MODEL = "large"
LOCALPATH = ('/Users/ncdegroot/Library/CloudStorage/'
             'OneDrive-Gedeeldebibliotheken-TilburgUniversity/'
             'Project - Reflective cafe - data')
model = None


def process_file(path):
    output_path = path.with_suffix('.txt')
    try:
        print("Start processing...")
        result = model.transcribe(str(path), verbose=True)
        # false: only progressbar; true: all; no param: no feedback
    except Exception as e:
        print(f"Error while processing {path}: '{e}'. Please fix it")
    else:
        text_to_save = result["text"]
        print(text_to_save)

        # file_name = f"{data_file.split('.')[0]}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        # Open the file in write mode
        with open(output_path, 'w') as file:
            # Write the text to the file
            file.write(text_to_save)

        print(f'Text has been saved to {output_path}')


@click.command()
@click.option("--config",
              default="config.toml",
              help="Specify config file")
@click.option("--init/--no-init",
              default=False,
              is_flag=True,
              help="Create config.toml file")
def main(config, init):
    global model
    # open config, ask for values is needed:
    #  Prompt.ask(msg)
    toml_path = Path(config)
    if not toml_path.exists():
        save_config_to_toml(toml_path, LOCALPATH, MODEL)
    result = get_config_from_toml(toml_path)
    if is_err(result):
        print(f"Exiting due to {result.err}")
        exit(1)

    config = result.ok_value
    if config:
        print(f"Config folder path: {config.folder}")
        print(f"Config model name: {config.model}")
    model = whisper.load_model(config.model)

    # internal_path = pathlib.Path('data')
    teams_path = Path(config.folder)
    path = teams_path

    txt_files = [file for file in path.glob('*') if file.suffix.lower() == '.txt']
    file_stems = [file.stem for file in txt_files]
    # file_stem indicates mp3 has been processed already
    mp3_files = [file for file in path.glob('*') if file.suffix.lower() == '.mp3' and file.stem not in file_stems]

    print(f"{len(mp3_files)} files to be processed")
    for file in mp3_files:
        print(f"Processing {file}")
        process_file(file)


if __name__ == "__main__":

    main(['--config', 'config2.toml', '--init'])
