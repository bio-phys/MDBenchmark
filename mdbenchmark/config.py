from tomlkit import parse
from tomlkit.exceptions import ParseError

from mdbenchmark import console

CONFIG_KEY_TO_CTX = {"skip_prompts": "yes", "input": "name", "modules": "module"}
ALLOWED_CONFIG_KEYS = [
    "input",
    "job_name",
    "modules",
    "skip_validation",
    "min_nodes",
    "max_nodes",
    "time",
    "host",
    "cpu",
    "gpu",
    "skip_prompts",
]


def parse_config(toml_file):
    """
    Open config file and parse its content.
    """
    with open(toml_file, "r") as f:
        content = "".join(f.readlines())

    try:
        parsed = parse(content)
    except ParseError as e:
        console.error(
            "{filename}: {error}".format(filename=toml_file, error=e.__str__())
        )

    return parsed


def _add_single_context(ctx, param, value):
    """
    Get a value from the context, otherwise set value defined by user.
    """
    return ctx.params.get(param.name, value)


def _import_config_into_context(ctx, param, config_file):
    """
    Parse config file and put settings into click.Context.
    """
    console.info(
        'Using settings from config file "{config_file}".'.format(
            config_file=config_file
        )
    )

    parsed_config = parse_config(config_file)

    for key in parsed_config.keys():
        # Ignore invalid keys from config file
        if key not in ALLOWED_CONFIG_KEYS:
            console.info('Ignoring setting for unknown key "{key}".'.format(key=key))
            continue

        try:
            ctx_key = CONFIG_KEY_TO_CTX[key]
        except KeyError:
            ctx_key = key

        ctx.params[ctx_key] = parsed_config[key]

    return config_file
