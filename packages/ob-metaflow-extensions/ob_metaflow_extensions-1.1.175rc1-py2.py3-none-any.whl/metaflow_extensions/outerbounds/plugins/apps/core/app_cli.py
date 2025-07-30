import json
import os
import sys
import random
from functools import wraps, partial
from typing import Dict, List, Any, Optional, Union

# IF this CLI is supposed to be reusable across Metaflow Too
# Then we need to ensure that the click IMPORT happens from metaflow
# so that any object class comparisons end up working as expected.
# since Metaflow lazy loads Click Modules, we need to ensure that the
# module's click Groups correlate to the same module otherwise Metaflow
# will not accept the cli as valid.
# But the BIGGEST Problem of adding a `metaflow._vendor` import is that
# It will run the remote-config check and that can raise a really dirty exception
# That will break the CLI.
# So we need to find a way to import click without having it try to check for remote-config
# or load the config from the environment.
# If we import click from metaflow over here then it might
# end up creating issues with click in general. So we need to figure a
# way to figure the right import of click dynamically. a neat way to handle that would be
# to have a function that can import the correct click based on the context in which stuff is being loaded.
from .click_importer import click
from .app_config import (
    AppConfig,
    AppConfigError,
    CODE_PACKAGE_PREFIX,
    CAPSULE_DEBUG,
    AuthType,
)
from .perimeters import PerimeterExtractor
from .cli_to_config import build_config_from_options
from .utils import (
    MultiStepSpinner,
)
from . import experimental
from .validations import deploy_validations
from .code_package import CodePackager
from .capsule import (
    CapsuleDeployer,
    list_and_filter_capsules,
    CapsuleApi,
    DEPLOYMENT_READY_CONDITIONS,
    CapsuleApiException,
    CapsuleDeploymentException,
)
from .dependencies import bake_deployment_image
import shlex
import time
import uuid
from datetime import datetime


class KeyValueDictPair(click.ParamType):
    name = "KV-DICT-PAIR"  # type: ignore

    def convert(self, value, param, ctx):
        # Parse a string of the form KEY=VALUE into a dict {KEY: VALUE}
        if len(value.split("=", 1)) != 2:
            self.fail(
                f"Invalid format for {value}. Expected format: KEY=VALUE", param, ctx
            )

        key, _value = value.split("=", 1)
        try:
            return {"key": key, "value": json.loads(_value)}
        except json.JSONDecodeError:
            return {"key": key, "value": _value}
        except Exception as e:
            self.fail(f"Invalid value for {value}. Error: {e}", param, ctx)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "KV-PAIR"


class KeyValuePair(click.ParamType):
    name = "KV-PAIR"  # type: ignore

    def convert(self, value, param, ctx):
        # Parse a string of the form KEY=VALUE into a dict {KEY: VALUE}
        if len(value.split("=", 1)) != 2:
            self.fail(
                f"Invalid format for {value}. Expected format: KEY=VALUE", param, ctx
            )

        key, _value = value.split("=", 1)
        try:
            return {key: json.loads(_value)}
        except json.JSONDecodeError:
            return {key: _value}
        except Exception as e:
            self.fail(f"Invalid value for {value}. Error: {e}", param, ctx)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "KV-PAIR"


class MountMetaflowArtifact(click.ParamType):
    name = "MOUNT-METAFLOW-ARTIFACT"  # type: ignore

    def convert(self, value, param, ctx):
        """
        Convert a string like "flow=MyFlow,artifact=my_model,path=/tmp/abc" or
        "pathspec=MyFlow/123/foo/345/my_model,path=/tmp/abc" to a dict.
        """
        artifact_dict = {}
        parts = value.split(",")

        for part in parts:
            if "=" not in part:
                self.fail(
                    f"Invalid format in part '{part}'. Expected 'key=value'", param, ctx
                )

            key, val = part.split("=", 1)
            artifact_dict[key.strip()] = val.strip()

        # Validate required fields
        if "pathspec" in artifact_dict:
            if "path" not in artifact_dict:
                self.fail(
                    "When using 'pathspec', you must also specify 'path'", param, ctx
                )

            # Return as pathspec format
            return {
                "pathspec": artifact_dict["pathspec"],
                "path": artifact_dict["path"],
            }
        elif (
            "flow" in artifact_dict
            and "artifact" in artifact_dict
            and "path" in artifact_dict
        ):
            # Return as flow/artifact format
            result = {
                "flow": artifact_dict["flow"],
                "artifact": artifact_dict["artifact"],
                "path": artifact_dict["path"],
            }

            # Add optional namespace if provided
            if "namespace" in artifact_dict:
                result["namespace"] = artifact_dict["namespace"]

            return result
        else:
            self.fail(
                "Invalid format. Must be either 'flow=X,artifact=Y,path=Z' or 'pathspec=X,path=Z'",
                param,
                ctx,
            )

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "MOUNT-METAFLOW-ARTIFACT"


class MountSecret(click.ParamType):
    name = "MOUNT-SECRET"  # type: ignore

    def convert(self, value, param, ctx):
        """
        Convert a string like "id=my_secret,path=/tmp/secret" to a dict.
        """
        secret_dict = {}
        parts = value.split(",")

        for part in parts:
            if "=" not in part:
                self.fail(
                    f"Invalid format in part '{part}'. Expected 'key=value'", param, ctx
                )

            key, val = part.split("=", 1)
            secret_dict[key.strip()] = val.strip()

        # Validate required fields
        if "id" in secret_dict and "path" in secret_dict:
            return {"id": secret_dict["id"], "path": secret_dict["path"]}
        else:
            self.fail("Invalid format. Must be 'key=X,path=Y'", param, ctx)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "MOUNT-SECRET"


class CommaSeparatedList(click.ParamType):
    name = "COMMA-SEPARATED-LIST"  # type: ignore

    def convert(self, value, param, ctx):
        return value.split(",")

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "COMMA-SEPARATED-LIST"


KVPairType = KeyValuePair()
MetaflowArtifactType = MountMetaflowArtifact()
SecretMountType = MountSecret()
CommaSeparatedListType = CommaSeparatedList()
KVDictType = KeyValueDictPair()


class ColorTheme:
    TIMESTAMP = "magenta"
    LOADING_COLOR = "cyan"
    BAD_COLOR = "red"
    INFO_COLOR = "green"
    DEBUG_COLOR = "yellow"

    TL_HEADER_COLOR = "magenta"
    ROW_COLOR = "bright_white"

    INFO_KEY_COLOR = "green"
    INFO_VALUE_COLOR = "bright_white"


NativeList = list


def _logger(
    body="", system_msg=False, head="", bad=False, timestamp=True, nl=True, color=None
):
    if timestamp:
        if timestamp is True:
            dt = datetime.now()
        else:
            dt = timestamp
        tstamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        click.secho(tstamp + " ", fg=ColorTheme.TIMESTAMP, nl=False)
    if head:
        click.secho(head, fg=ColorTheme.INFO_COLOR, nl=False)
    click.secho(
        body,
        bold=system_msg,
        fg=ColorTheme.BAD_COLOR if bad else color if color is not None else None,
        nl=nl,
    )


def _logger_styled(
    body="", system_msg=False, head="", bad=False, timestamp=True, nl=True, color=None
):
    message_parts = []

    if timestamp:
        if timestamp is True:
            dt = datetime.now()
        else:
            dt = timestamp
        tstamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        message_parts.append(click.style(tstamp + " ", fg=ColorTheme.TIMESTAMP))

    if head:
        message_parts.append(click.style(head, fg=ColorTheme.INFO_COLOR))

    message_parts.append(
        click.style(
            body,
            bold=system_msg,
            fg=ColorTheme.BAD_COLOR if bad else color if color is not None else None,
        )
    )

    return "".join(message_parts)


def _spinner_logger(spinner, *msg, **kwargs):
    spinner.log(*[_logger_styled(x, timestamp=True, **kwargs) for x in msg])


class CliState(object):
    pass


def _pre_create_debug(
    app_config: AppConfig,
    capsule: CapsuleDeployer,
    state_dir: str,
    options: Dict[str, Any],
    cli_parsed_config: Dict[str, Any],
):
    if CAPSULE_DEBUG:
        os.makedirs(state_dir, exist_ok=True)
        debug_path = os.path.join(state_dir, f"debug_{time.time()}.json")
        with open(
            debug_path,
            "w",
        ) as f:
            f.write(
                json.dumps(
                    {
                        "app_state": app_config.dump_state(),  # This is the state of the app config after parsing the CLI options and right before the capsule deploy API is called
                        "capsule_input": capsule.create_input(),  # This is the input that is passed to the capsule deploy API
                        "deploy_response": capsule._capsule_deploy_response,  # This is the response from the capsule deploy API
                        "cli_options": options,  # These are the actual options passing down to the CLI
                        "cli_parsed_config": cli_parsed_config,  # This is the config object that is created after parsing options from the CLI
                    },
                    indent=2,
                    default=str,
                )
            )


def _post_create_debug(capsule: CapsuleDeployer, state_dir: str):
    if CAPSULE_DEBUG:
        debug_path = os.path.join(
            state_dir, f"debug_deploy_response_{time.time()}.json"
        )
        with open(debug_path, "w") as f:
            f.write(json.dumps(capsule._capsule_deploy_response, indent=2, default=str))


def _bake_image(app_config: AppConfig, cache_dir: str, logger):
    baking_status = bake_deployment_image(
        app_config=app_config,
        cache_file_path=os.path.join(cache_dir, "image_cache"),
        logger=logger,
    )
    app_config.set_state(
        "image",
        baking_status.resolved_image,
    )
    app_config.set_state("python_path", baking_status.python_path)
    logger("🐳 Using The Docker Image : %s" % app_config.get_state("image"))


def print_table(data, headers):
    """Print data in a formatted table."""

    if not data:
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    # Calculate actual widths based on data
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_row = " | ".join(
        [headers[i].ljust(col_widths[i]) for i in range(len(headers))]
    )
    click.secho("-" * len(header_row), fg=ColorTheme.TL_HEADER_COLOR)
    click.secho(header_row, fg=ColorTheme.TL_HEADER_COLOR, bold=True)
    click.secho("-" * len(header_row), fg=ColorTheme.TL_HEADER_COLOR)

    # Print data rows
    for row in data:
        formatted_row = " | ".join(
            [str(row[i]).ljust(col_widths[i]) for i in range(len(row))]
        )
        click.secho(formatted_row, fg=ColorTheme.ROW_COLOR, bold=True)
    click.secho("-" * len(header_row), fg=ColorTheme.TL_HEADER_COLOR)


@click.group()
def cli():
    """Outerbounds CLI tool."""
    pass


@cli.group(
    help="Commands related to Deploying/Running/Managing Apps on Outerbounds Platform."
)
@click.pass_context
def app(ctx):
    """App-related commands."""
    metaflow_set_context = getattr(ctx, "obj", None)
    ctx.obj = CliState()
    ctx.obj.trace_id = str(uuid.uuid4())
    ctx.obj.app_state_dir = os.path.join(os.curdir, ".ob_apps")
    profile = os.environ.get("METAFLOW_PROFILE", "")
    config_dir = os.path.expanduser(
        os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")
    )
    perimeter, api_server = PerimeterExtractor.for_ob_cli(
        config_dir=config_dir, profile=profile
    )
    if perimeter is None or api_server is None:
        raise AppConfigError(
            "Perimeter not found in the environment, Found perimeter: %s, api_server: %s"
            % (perimeter, api_server)
        )
    ctx.obj.perimeter = perimeter
    ctx.obj.api_url = api_server
    os.makedirs(ctx.obj.app_state_dir, exist_ok=True)


def parse_commands(app_config: AppConfig, cli_command_input):
    # There can be two modes:
    # 1. User passes command via `--` in the CLI
    # 2. User passes the `commands` key in the config.
    base_commands = []
    if len(cli_command_input) > 0:
        # TODO: we can be a little more fancy here by allowing the user to just call
        #       `outerbounds app deploy -- foo.py` and figure out if we need to stuff python
        #       in front of the command or not. But for sake of dumb simplicity, we can just
        #       assume what ever the user called on local needs to be called remotely, we can
        #       just ask them to add the outerbounds command in front of it.
        #       So the dev ex would be :
        #       `python foo.py` -> `outerbounds app deploy -- python foo.py`
        if type(cli_command_input) == str:
            base_commands.append(cli_command_input)
        else:
            base_commands.append(shlex.join(cli_command_input))
    elif app_config.get("commands", None) is not None:
        base_commands.extend(app_config.get("commands"))
    return base_commands


def deployment_instance_options(func):
    # These parameters influence how the CLI behaves for each instance of a launched deployment.
    @click.option(
        "--readiness-condition",
        type=click.Choice(DEPLOYMENT_READY_CONDITIONS.enums()),
        help=DEPLOYMENT_READY_CONDITIONS.__doc__,
        default=DEPLOYMENT_READY_CONDITIONS.ATLEAST_ONE_RUNNING,
    )
    @click.option(
        "--status-file",
        type=str,
        help="The path to the file where the final status of the deployment will be written.",
        default=None,
    )
    @click.option(
        "--readiness-wait-time",
        type=int,
        help="The time (in seconds) to monitor the deployment for readiness after the readiness condition is met.",
        default=4,
    )
    @click.option(
        "--deployment-timeout",
        "max_wait_time",
        type=int,
        help="The maximum time (in seconds) to wait for the deployment to reach readiness before timing out.",
        default=600,
    )
    @click.option(
        "--no-loader",
        is_flag=True,
        help="Do not use the loading spinner for the deployment.",
        default=False,
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def common_deploy_options(func):
    @click.option(
        "--name",
        type=str,
        help="The name of the app to deploy.",
    )
    @click.option("--port", type=int, help="Port where the app is hosted.")
    @click.option(
        "--tag",
        "tags",
        multiple=True,
        type=KVPairType,
        help="The tags of the app to deploy. Format KEY=VALUE. Example --tag foo=bar --tag x=y",
        default=None,
    )
    @click.option(
        "--image",
        type=str,
        help="The Docker image to deploy with the App",
        default=None,
    )
    @click.option(
        "--cpu",
        type=str,
        help="CPU resource request and limit",
        default=None,
    )
    @click.option(
        "--memory",
        type=str,
        help="Memory resource request and limit",
        default=None,
    )
    @click.option(
        "--gpu",
        type=str,
        help="GPU resource request and limit",
        default=None,
    )
    @click.option(
        "--disk",
        type=str,
        help="Storage resource request and limit",
        default=None,
    )
    @click.option(
        "--health-check-enabled",
        type=bool,
        help="Enable health checks",
        default=None,
    )
    @click.option(
        "--health-check-path",
        type=str,
        help="Health check path",
        default=None,
    )
    @click.option(
        "--health-check-initial-delay",
        type=int,
        help="Initial delay seconds for health check",
        default=None,
    )
    @click.option(
        "--health-check-period",
        type=int,
        help="Period seconds for health check",
        default=None,
    )
    @click.option(
        "--compute-pools",
        type=CommaSeparatedListType,
        help="The compute pools to deploy the app to. Example: --compute-pools default,large",
        default=None,
    )
    @click.option(
        "--auth-type",
        type=click.Choice(AuthType.enums()),
        help="The type of authentication to use for the app.",
        default=None,
    )
    @click.option(
        "--public-access/--private-access",
        "auth_public",
        type=bool,
        help="Whether the app is public or not.",
        default=None,
    )
    @click.option(
        "--no-deps",
        is_flag=True,
        help="Do not any dependencies. Directly used the image provided",
        default=False,
    )
    @click.option(
        "--min-replicas",
        type=int,
        help="Minimum number of replicas to deploy",
        default=None,
    )
    @click.option(
        "--max-replicas",
        type=int,
        help="Maximum number of replicas to deploy",
        default=None,
    )
    @click.option(
        "--description",
        type=str,
        help="The description of the app to deploy.",
        default=None,
    )
    @click.option(
        "--app-type",
        type=str,
        help="The type of app to deploy.",
        default=None,
    )
    @click.option(
        "--force-upgrade",
        is_flag=True,
        help="Force upgrade the app even if it is currently being upgraded.",
        default=False,
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def common_run_options(func):
    """Common options for running and deploying apps."""

    @click.option(
        "--config-file",
        type=str,
        help="The config file to use for the App (YAML or JSON)",
        default=None,
    )
    @click.option(
        "--secret",
        "secrets",
        multiple=True,
        type=str,
        help="Secrets to deploy with the App",
        default=None,
    )
    @click.option(
        "--env",
        "envs",
        multiple=True,
        type=KVPairType,
        help="Environment variables to deploy with the App. Use format KEY=VALUE",
        default=None,
    )
    @click.option(
        "--package-src-path",
        type=str,
        help="The path to the source code to deploy with the App.",
        default=None,
    )
    @click.option(
        "--package-suffixes",
        type=CommaSeparatedListType,
        help="The suffixes of the source code to deploy with the App.",
        default=None,
    )
    @click.option(
        "--dep-from-requirements",
        type=str,
        help="Path to requirements.txt file for dependencies",
        default=None,
    )
    @click.option(
        "--dep-from-pyproject",
        type=str,
        help="Path to pyproject.toml file for dependencies",
        default=None,
    )
    # TODO: [FIX ME]: Get better CLI abstraction for pypi/conda dependencies
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def _package_necessary_things(app_config: AppConfig, logger):
    # Packaging has a few things to be thought through:
    #   1. if `entrypoint_path` exists then should we package the directory
    #      where the entrypoint lives. For example : if the user calls
    #      `outerbounds app deploy foo/bar.py`  should we package `foo` dir
    #      or should we package the cwd from which foo/bar.py is being called.
    #   2. if the src path is used with the config file then how should we view
    #      that path ?
    #   3. It becomes interesting when users call the deployment with config files
    #      where there is a `src_path` and then is the src_path relative to the config file
    #      or is it relative to where the caller command is sitting. Ideally it should work
    #      like Kustomizations where its relative to where the yaml file sits for simplicity
    #      of understanding relationships between config files. Ideally users can pass the src_path
    #      from the command line and that will aliviate any need to package any other directories for
    #

    package_dir = app_config.get_state("packaging_directory")
    if package_dir is None:
        app_config.set_state("code_package_url", None)
        app_config.set_state("code_package_key", None)
        return
    from metaflow.metaflow_config import DEFAULT_DATASTORE

    package = app_config.get_state("package") or {}
    suffixes = package.get("suffixes", None)

    packager = CodePackager(
        datastore_type=DEFAULT_DATASTORE, code_package_prefix=CODE_PACKAGE_PREFIX
    )
    package_url, package_key = packager.store(
        paths_to_include=[package_dir], file_suffixes=suffixes
    )
    app_config.set_state("code_package_url", package_url)
    app_config.set_state("code_package_key", package_key)
    logger("💾 Code Package Saved to : %s" % app_config.get_state("code_package_url"))


@app.command(help="Deploy an app to the Outerbounds Platform.")
@common_deploy_options
@common_run_options
@deployment_instance_options
@experimental.wrapping_cli_options
@click.pass_context
@click.argument("command", nargs=-1, type=click.UNPROCESSED, required=False)
def deploy(
    ctx,
    command,
    readiness_condition=None,
    max_wait_time=None,
    readiness_wait_time=None,
    status_file=None,
    no_loader=False,
    **options,
):
    """Deploy an app to the Outerbounds Platform."""
    from functools import partial

    if not ctx.obj.perimeter:
        raise AppConfigError("OB_CURRENT_PERIMETER is not set")
    _current_instance_debug_dir = None
    logger = partial(_logger, timestamp=True)
    try:
        _cli_parsed_config = build_config_from_options(options)
        # Create configuration
        if options["config_file"]:
            # Load from file
            app_config = AppConfig.from_file(options["config_file"])

            # Update with any CLI options using the unified method
            app_config.update_from_cli_options(options)
        else:
            # Create from CLI options
            app_config = AppConfig(_cli_parsed_config)

        # Validate the configuration
        app_config.validate()
        logger(
            f"🚀 Deploying {app_config.get('name')} to the Outerbounds platform...",
            color=ColorTheme.INFO_COLOR,
            system_msg=True,
        )

        packaging_directory = None
        package_src_path = app_config.get("package", {}).get("src_path", None)
        if package_src_path:
            if os.path.isfile(package_src_path):
                raise AppConfigError("src_path must be a directory, not a file")
            elif os.path.isdir(package_src_path):
                packaging_directory = os.path.abspath(package_src_path)
            else:
                raise AppConfigError(f"src_path '{package_src_path}' does not exist")
        else:
            # If src_path is None then we assume then we can assume for the moment
            # that we can package the current working directory.
            packaging_directory = os.getcwd()

        app_config.set_state("packaging_directory", packaging_directory)
        logger(
            "📦 Packaging Directory : %s" % app_config.get_state("packaging_directory"),
        )
        # TODO: Construct the command needed to run the app
        #       If we are constructing the directory with the src_path
        #       then we need to add the command from the option otherwise
        #       we use the command from the entrypoint path and whatever follows `--`
        #       is the command to run.

        # Set some defaults for the deploy command
        app_config.set_deploy_defaults(packaging_directory)

        if options.get("no_deps") == True:
            # Setting this in the state will make it skip the fast-bakery step
            # of building an image.
            app_config.set_state("skip_dependencies", True)
        else:
            # Check if the user has set the dependencies in the app config
            dependencies = app_config.get("dependencies", {})
            if len(dependencies) == 0:
                # The user has not set any dependencies, so we can sniff the packaging directory
                # for a dependencies file.
                requirements_file = os.path.join(
                    packaging_directory, "requirements.txt"
                )
                pyproject_toml = os.path.join(packaging_directory, "pyproject.toml")
                if os.path.exists(pyproject_toml):
                    app_config.set_state(
                        "dependencies", {"from_pyproject_toml": pyproject_toml}
                    )
                    logger(
                        "📦 Using dependencies from pyproject.toml: %s" % pyproject_toml
                    )
                elif os.path.exists(requirements_file):
                    app_config.set_state(
                        "dependencies", {"from_requirements_file": requirements_file}
                    )
                    logger(
                        "📦 Using dependencies from requirements.txt: %s"
                        % requirements_file
                    )

        # Print the configuration
        # 1. validate that the secrets for the app exist
        # 2. TODO: validate that the compute pool specified in the app exists.
        # 3. Building Docker image if necessary (based on parameters)
        #   - We will bake images with fastbakery and pass it to the deploy command
        # TODO: validation logic can be wrapped in try catch so that we can provide
        #       better error messages.
        cache_dir = os.path.join(
            ctx.obj.app_state_dir, app_config.get("name", "default")
        )

        def _non_spinner_logger(*msg, **kwargs):
            for m in msg:
                logger(m, **kwargs)

        deploy_validations(
            app_config,
            cache_dir=cache_dir,
            logger=logger,
        )
        image_spinner = None
        img_logger = _non_spinner_logger
        if not no_loader:
            image_spinner = MultiStepSpinner(
                text=lambda: _logger_styled(
                    "🍞 Baking Docker Image",
                    timestamp=True,
                ),
                color=ColorTheme.LOADING_COLOR,
            )
            img_logger = partial(_spinner_logger, image_spinner)
            image_spinner.start()

        _bake_image(app_config, cache_dir, img_logger)
        if image_spinner:
            image_spinner.stop()

        base_commands = parse_commands(app_config, command)

        app_config.set_state("commands", base_commands)

        # TODO: Handle the case where packaging_directory is None
        # This would involve:
        # 1. Packaging the code:
        #   - We need to package the code and throw the tarball to some object store
        _package_necessary_things(app_config, logger)

        app_config.set_state("perimeter", ctx.obj.perimeter)

        capsule_spinner = None
        capsule_logger = _non_spinner_logger

        if CAPSULE_DEBUG:
            _current_instance_debug_dir = os.path.join(
                cache_dir, f"debug_deployment_instance_{time.time()}"
            )
            os.makedirs(_current_instance_debug_dir, exist_ok=True)
        # 2. Convert to the IR that the backend accepts
        capsule = CapsuleDeployer(
            app_config,
            ctx.obj.api_url,
            debug_dir=_current_instance_debug_dir,
            success_terminal_state_condition=readiness_condition,
            create_timeout=max_wait_time,
            readiness_wait_time=readiness_wait_time,
            logger_fn=capsule_logger,
        )
        if not no_loader:
            capsule_spinner = MultiStepSpinner(
                text=lambda: _logger_styled(
                    "💊 Waiting for %s %s to be ready to serve traffic"
                    % (capsule.capsule_type.lower(), capsule.identifier),
                    timestamp=True,
                ),
                color=ColorTheme.LOADING_COLOR,
            )
            capsule_logger = partial(_spinner_logger, capsule_spinner)
            capsule_spinner.start()

        currently_present_capsules = list_and_filter_capsules(
            capsule.capsule_api,
            None,
            None,
            capsule.name,
            None,
            None,
            None,
        )

        force_upgrade = app_config.get_state("force_upgrade", False)

        _pre_create_debug(
            app_config,
            capsule,
            _current_instance_debug_dir,
            options,
            _cli_parsed_config,
        )

        if len(currently_present_capsules) > 0:
            # Only update the capsule if there is no upgrade in progress
            # Only update a "already updating" capsule if the `--force-upgrade` flag is provided.
            _curr_cap = currently_present_capsules[0]
            this_capsule_is_being_updated = _curr_cap.get("status", {}).get(
                "updateInProgress", False
            )

            if this_capsule_is_being_updated and not force_upgrade:
                _upgrader = _curr_cap.get("metadata", {}).get("lastModifiedBy", None)
                message = f"{capsule.capsule_type} is currently being upgraded"
                if _upgrader:
                    message = (
                        f"{capsule.capsule_type} is currently being upgraded. Upgrade was launched by {_upgrader}. "
                        "If you wish to force upgrade, you can do so by providing the `--force-upgrade` flag."
                    )
                raise AppConfigError(message)
            capsule_logger(
                f"🚀 {'' if not force_upgrade else 'Force'} Upgrading {capsule.capsule_type.lower()} `{capsule.name}`....",
                color=ColorTheme.INFO_COLOR,
                system_msg=True,
            )
        else:
            capsule_logger(
                f"🚀 Deploying {capsule.capsule_type.lower()} to the platform....",
                color=ColorTheme.INFO_COLOR,
                system_msg=True,
            )
        # 3. Throw the job into the platform and report deployment status
        capsule.create()
        _post_create_debug(capsule, _current_instance_debug_dir)

        # We only get the `capsule_response` if the deployment is has reached
        # a successful terminal state.
        final_status = capsule.wait_for_terminal_state()
        if capsule_spinner:
            capsule_spinner.stop()

        logger(
            f"💊 {capsule.capsule_type} {app_config.config['name']} ({capsule.identifier}) deployed! {capsule.capsule_type} exposed on the URL: {capsule.url}",
            color=ColorTheme.INFO_COLOR,
            system_msg=True,
        )

        if CAPSULE_DEBUG:
            logger(
                f"[debug] 💊 {capsule.capsule_type} {app_config.config['name']} ({capsule.identifier}) deployment status [on completion]: {final_status}",
                color=ColorTheme.DEBUG_COLOR,
            )
            logger(
                f"[debug] 💊 {capsule.capsule_type} {app_config.config['name']} ({capsule.identifier}) debug info saved to `{_current_instance_debug_dir}`",
                color=ColorTheme.DEBUG_COLOR,
            )
            final_status["debug_dir"] = _current_instance_debug_dir

        if status_file:
            # Create the file if it doesn't exist
            with open(status_file, "w") as f:
                f.write(json.dumps(final_status, indent=4))
            logger(
                f"📝 {capsule.capsule_type} {app_config.config['name']} ({capsule.identifier}) deployment status written to {status_file}",
                color=ColorTheme.INFO_COLOR,
                system_msg=True,
            )

    except Exception as e:
        message = getattr(e, "message", str(e))
        logger(
            f"Deployment failed: [{e.__class__.__name__}]: {message}",
            bad=True,
            system_msg=True,
        )
        if CAPSULE_DEBUG:
            if _current_instance_debug_dir is not None:
                logger(
                    f"[debug] 💊 debug info saved to `{_current_instance_debug_dir}`",
                    color=ColorTheme.DEBUG_COLOR,
                )
            raise e
        exit(1)


def _parse_capsule_table(filtered_capsules):
    headers = ["Name", "ID", "Ready", "App Type", "Port", "Tags", "URL"]
    table_data = []

    for capsule in filtered_capsules:
        spec = capsule.get("spec", {})
        status = capsule.get("status", {}) or {}
        cap_id = capsule.get("id")
        display_name = spec.get("displayName", "")
        ready = str(status.get("readyToServeTraffic", False))
        auth_type = spec.get("authConfig", {}).get("authType", "")
        port = str(spec.get("port", ""))
        tags_str = ", ".join(
            [f"{tag['key']}={tag['value']}" for tag in spec.get("tags", [])]
        )
        access_info = status.get("accessInfo", {}) or {}
        url = access_info.get("outOfClusterURL", None)

        table_data.append(
            [
                display_name,
                cap_id,
                ready,
                auth_type,
                port,
                tags_str,
                f"https://{url}" if url else "URL not available",
            ]
        )
    return headers, table_data


@app.command(help="List apps in the Outerbounds Platform.")
@click.option("--project", type=str, help="Filter apps by project")
@click.option("--branch", type=str, help="Filter apps by branch")
@click.option("--name", type=str, help="Filter apps by name")
@click.option(
    "--tag",
    "tags",
    type=KVDictType,
    help="Filter apps by tag. Format KEY=VALUE. Example --tag foo=bar --tag x=y. If multiple tags are provided, the app must match all of them.",
    multiple=True,
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    help="Format the output",
    default="text",
)
@click.option(
    "--auth-type", type=click.Choice(AuthType.enums()), help="Filter apps by Auth type"
)
@click.pass_context
def list(ctx, project, branch, name, tags, format, auth_type):
    """List apps in the Outerbounds Platform."""
    capsule_api = CapsuleApi(
        ctx.obj.api_url,
        ctx.obj.perimeter,
    )
    filtered_capsules = list_and_filter_capsules(
        capsule_api, project, branch, name, tags, auth_type, None
    )
    if format == "json":
        click.echo(json.dumps(filtered_capsules, indent=4))
    else:
        headers, table_data = _parse_capsule_table(filtered_capsules)
        print_table(table_data, headers)


@app.command(help="Delete an app/apps from the Outerbounds Platform.")
@click.option("--name", type=str, help="Filter app to delete by name")
@click.option("--id", "cap_id", type=str, help="Filter app to delete by id")
@click.option("--project", type=str, help="Filter apps to delete by project")
@click.option("--branch", type=str, help="Filter apps to delete by branch")
@click.option(
    "--tag",
    "tags",
    multiple=True,
    type=KVDictType,
    help="Filter apps to delete by tag. Format KEY=VALUE. Example --tag foo=bar --tag x=y. If multiple tags are provided, the app must match all of them.",
)
@click.option("--auto-approve", is_flag=True, help="Do not prompt for confirmation")
@click.pass_context
def delete(ctx, name, cap_id, project, branch, tags, auto_approve):

    """Delete an app/apps from the Outerbounds Platform."""
    # Atleast one of the args need to be provided
    if not any(
        [
            name is not None,
            cap_id is not None,
            project is not None,
            branch is not None,
            len(tags) != 0,
        ]
    ):
        raise AppConfigError(
            "Atleast one of the options need to be provided. You can use --name, --id, --project, --branch, --tag"
        )

    capsule_api = CapsuleApi(ctx.obj.api_url, ctx.obj.perimeter)
    filtered_capsules = list_and_filter_capsules(
        capsule_api, project, branch, name, tags, None, cap_id
    )

    headers, table_data = _parse_capsule_table(filtered_capsules)
    click.secho("The following apps will be deleted:", fg="red", bold=True)
    print_table(table_data, headers)

    # Confirm the deletion
    if not auto_approve:
        confirm = click.prompt(
            click.style(
                "💊 Are you sure you want to delete these apps?", fg="red", bold=True
            ),
            default="no",
            type=click.Choice(["yes", "no"]),
        )
        if confirm == "no":
            exit(1)

    def item_show_func(x):
        if not x:
            return None
        name = x.get("spec", {}).get("displayName", "")
        id = x.get("id", "")
        return click.style(
            "💊 deleting %s [%s]" % (name, id),
            fg=ColorTheme.BAD_COLOR,
            bold=True,
        )

    with click.progressbar(
        filtered_capsules,
        label=click.style("💊 Deleting apps...", fg=ColorTheme.BAD_COLOR, bold=True),
        fill_char=click.style("█", fg=ColorTheme.BAD_COLOR, bold=True),
        empty_char=click.style("░", fg=ColorTheme.BAD_COLOR, bold=True),
        item_show_func=item_show_func,
    ) as bar:
        for capsule in bar:
            capsule_api.delete(capsule.get("id"))
            time.sleep(0.5 + random.random() * 2)  # delay to avoid rate limiting


@app.command(help="Run an app locally (for testing).")
@common_run_options
@click.pass_context
def run(ctx, **options):
    """Run an app locally for testing."""
    try:
        # Create configuration
        if options["config_file"]:
            # Load from file
            app_config = AppConfig.from_file(options["config_file"])

            # Update with any CLI options using the unified method
            app_config.update_from_cli_options(options)
        else:
            # Create from CLI options
            config_dict = build_config_from_options(options)
            app_config = AppConfig(config_dict)

        # Validate the configuration
        app_config.validate()

        # Print the configuration
        click.echo("Running App with configuration:")
        click.echo(app_config.to_yaml())

        # TODO: Implement local run logic
        # This would involve:
        # 1. Setting up the environment
        # 2. Running the app locally
        # 3. Reporting status

        click.echo(f"App '{app_config.config['name']}' running locally!")

    except AppConfigError as e:
        click.echo(f"Error in app configuration: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error running app: {e}", err=True)
        ctx.exit(1)


@app.command(
    help="Get detailed information about an app from the Outerbounds Platform."
)
@click.option("--name", type=str, help="Get info for app by name")
@click.option("--id", "cap_id", type=str, help="Get info for app by id")
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    help="Format the output",
    default="text",
)
@click.pass_context
def info(ctx, name, cap_id, format):
    """Get detailed information about an app from the Outerbounds Platform."""
    # Require either name or id
    if not any([name is not None, cap_id is not None]):
        raise AppConfigError(
            "Either --name or --id must be provided to get app information."
        )

    # Ensure only one is provided
    if name is not None and cap_id is not None:
        raise AppConfigError("Please provide either --name or --id, not both.")

    capsule_api = CapsuleApi(
        ctx.obj.api_url,
        ctx.obj.perimeter,
    )

    # First, find the capsule using list_and_filter_capsules
    filtered_capsules = list_and_filter_capsules(
        capsule_api, None, None, name, None, None, cap_id
    )

    if len(filtered_capsules) == 0:
        identifier = name if name else cap_id
        identifier_type = "name" if name else "id"
        raise AppConfigError(f"No app found with {identifier_type}: {identifier}")

    if len(filtered_capsules) > 1:
        raise AppConfigError(
            f"Multiple apps found with name: {name}. Please use --id to specify exactly which app you want info for."
        )

    # Get the capsule info
    capsule = filtered_capsules[0]
    capsule_id = capsule.get("id")

    # Get detailed capsule info and workers
    try:
        detailed_capsule_info = capsule_api.get(capsule_id)
        workers_info = capsule_api.get_workers(capsule_id)

        if format == "json":
            # Output in JSON format for piping to jq
            info_data = {"capsule": detailed_capsule_info, "workers": workers_info}
            click.echo(json.dumps(info_data, indent=4))
        else:
            # Output in text format
            _display_capsule_info_text(detailed_capsule_info, workers_info)

    except Exception as e:
        raise AppConfigError(f"Error retrieving information for app {capsule_id}: {e}")


def _display_capsule_info_text(capsule_info, workers_info):
    """Display capsule information in a human-readable text format."""
    spec = capsule_info.get("spec", {})
    status = capsule_info.get("status", {}) or {}
    metadata = capsule_info.get("metadata", {}) or {}

    info_color = ColorTheme.INFO_COLOR
    tl_color = ColorTheme.TL_HEADER_COLOR

    def _key_style(key: str, value: str):
        return "%s: %s" % (
            click.style(
                key,
                fg=ColorTheme.INFO_KEY_COLOR,
            ),
            click.style(str(value), fg=ColorTheme.INFO_VALUE_COLOR, bold=True),
        )

    # Basic Info
    click.secho("=== App Information ===", fg=tl_color, bold=True)
    click.secho(_key_style("Name", spec.get("displayName", "N/A")), fg=info_color)
    click.secho(_key_style("ID", capsule_info.get("id", "N/A")), fg=info_color)
    click.secho(
        _key_style("Version", capsule_info.get("version", "N/A")), fg=info_color
    )
    click.secho(
        _key_style(
            "Ready to Serve Traffic", str(status.get("readyToServeTraffic", False))
        ),
        fg=info_color,
    )
    click.secho(
        _key_style("Update In Progress", str(status.get("updateInProgress", False))),
        fg=info_color,
    )
    click.secho(
        _key_style(
            "Currently Served Version", str(status.get("currentlyServedVersion", "N/A"))
        ),
        fg=info_color,
    )

    # URLs
    access_info = status.get("accessInfo", {}) or {}
    out_cluster_url = access_info.get("outOfClusterURL")
    in_cluster_url = access_info.get("inClusterURL")

    if out_cluster_url:
        click.secho(
            _key_style("External URL", f"https://{out_cluster_url}"), fg=info_color
        )
    if in_cluster_url:
        click.secho(
            _key_style("Internal URL", f"https://{in_cluster_url}"), fg=info_color
        )

    # Resource Configuration
    click.secho("\n=== Resource Configuration ===", fg=tl_color, bold=True)
    resource_config = spec.get("resourceConfig", {})
    click.secho(_key_style("CPU", resource_config.get("cpu", "N/A")), fg=info_color)
    click.secho(
        _key_style("Memory", resource_config.get("memory", "N/A")), fg=info_color
    )
    click.secho(
        _key_style("Ephemeral Storage", resource_config.get("ephemeralStorage", "N/A")),
        fg=info_color,
    )
    if resource_config.get("gpu"):
        click.secho(_key_style("GPU", resource_config.get("gpu")), fg=info_color)

    # Autoscaling
    click.secho("\n=== Autoscaling Configuration ===", fg=tl_color, bold=True)
    autoscaling_config = spec.get("autoscalingConfig", {})
    click.secho(
        _key_style("Min Replicas", str(autoscaling_config.get("minReplicas", "N/A"))),
        fg=info_color,
    )
    click.secho(
        _key_style("Max Replicas", str(autoscaling_config.get("maxReplicas", "N/A"))),
        fg=info_color,
    )
    click.secho(
        _key_style("Available Replicas", str(status.get("availableReplicas", "N/A"))),
        fg=info_color,
    )

    # Auth Configuration
    click.secho("\n=== Authentication Configuration ===", fg=tl_color, bold=True)
    auth_config = spec.get("authConfig", {})
    click.secho(
        _key_style("Auth Type", auth_config.get("authType", "N/A")), fg=info_color
    )
    click.secho(
        _key_style("Public Access", str(auth_config.get("publicToDeployment", "N/A"))),
        fg=info_color,
    )

    # Tags
    tags = spec.get("tags", [])
    if tags:
        click.secho("\n=== Tags ===", fg=tl_color, bold=True)
        for tag in tags:
            click.secho(
                _key_style(str(tag.get("key", "N/A")), str(tag.get("value", "N/A"))),
                fg=info_color,
            )

    # Metadata
    click.secho("\n=== Metadata ===", fg=tl_color, bold=True)
    click.secho(
        _key_style("Created At", metadata.get("createdAt", "N/A")), fg=info_color
    )
    click.secho(
        _key_style("Last Modified At", metadata.get("lastModifiedAt", "N/A")),
        fg=info_color,
    )
    click.secho(
        _key_style("Last Modified By", metadata.get("lastModifiedBy", "N/A")),
        fg=info_color,
    )

    # Workers Information
    click.secho("\n=== Workers Information ===", fg=tl_color, bold=True)
    if not workers_info:
        click.secho("No workers found", fg=info_color)
    else:
        click.secho(_key_style("Total Workers", str(len(workers_info))), fg=tl_color)

        # Create a table for workers
        workers_headers = [
            "Worker ID",
            "Phase",
            "Version",
            "Activity",
            "Activity Data Available",
        ]
        workers_table_data = []

        for worker in workers_info:
            worker_id = worker.get("workerId", "N/A")
            phase = worker.get("phase", "N/A")
            version = worker.get("version", "N/A")
            activity = str(worker.get("activity", "N/A"))
            activity_data_available = str(worker.get("activityDataAvailable", False))

            workers_table_data.append(
                [
                    worker_id[:20] + "..." if len(worker_id) > 23 else worker_id,
                    phase,
                    version[:10] + "..." if len(version) > 13 else version,
                    activity,
                    activity_data_available,
                ]
            )

        print_table(workers_table_data, workers_headers)


@app.command(help="Get logs for an app worker from the Outerbounds Platform.")
@click.option("--name", type=str, help="Get logs for app by name")
@click.option("--id", "cap_id", type=str, help="Get logs for app by id")
@click.option("--worker-id", type=str, help="Get logs for specific worker")
@click.option("--file", type=str, help="Save logs to file")
@click.option(
    "--previous",
    is_flag=True,
    help="Get logs from previous container instance",
    default=False,
)
@click.pass_context
def logs(ctx, name, cap_id, worker_id, file, previous):
    """Get logs for an app worker from the Outerbounds Platform."""
    # Require either name or id
    if not any([name is not None, cap_id is not None]):
        raise AppConfigError("Either --name or --id must be provided to get app logs.")

    # Ensure only one is provided
    if name is not None and cap_id is not None:
        raise AppConfigError("Please provide either --name or --id, not both.")

    capsule_api = CapsuleApi(
        ctx.obj.api_url,
        ctx.obj.perimeter,
    )

    # First, find the capsule using list_and_filter_capsules
    filtered_capsules = list_and_filter_capsules(
        capsule_api, None, None, name, None, None, cap_id
    )

    if len(filtered_capsules) == 0:
        identifier = name if name else cap_id
        identifier_type = "name" if name else "id"
        raise AppConfigError(f"No app found with {identifier_type}: {identifier}")

    if len(filtered_capsules) > 1:
        raise AppConfigError(
            f"Multiple apps found with name: {name}. Please use --id to specify exactly which app you want logs for."
        )

    capsule = filtered_capsules[0]
    capsule_id = capsule.get("id")

    # Get workers
    try:
        workers_info = capsule_api.get_workers(capsule_id)
    except Exception as e:
        raise AppConfigError(f"Error retrieving workers for app {capsule_id}: {e}")

    if not workers_info:
        raise AppConfigError(f"No workers found for app {capsule_id}")

    # If worker_id not provided, show interactive selection
    if not worker_id:
        if len(workers_info) == 1:
            # Only one worker, use it automatically
            selected_worker = workers_info[0]
            worker_id = selected_worker.get("workerId")
            worker_phase = selected_worker.get("phase", "N/A")
            worker_version = selected_worker.get("version", "N/A")[:10]
            click.echo(
                f"📋 Using the only available worker: {worker_id[:20]}... (phase: {worker_phase}, version: {worker_version}...)"
            )
        else:
            # Multiple workers, show selection
            click.secho(
                "📋 Multiple workers found. Please select one:",
                fg=ColorTheme.INFO_COLOR,
                bold=True,
            )

            # Display workers in a table format for better readability
            headers = ["#", "Worker ID", "Phase", "Version", "Activity"]
            table_data = []

            for i, worker in enumerate(workers_info, 1):
                w_id = worker.get("workerId", "N/A")
                phase = worker.get("phase", "N/A")
                version = worker.get("version", "N/A")
                activity = str(worker.get("activity", "N/A"))

                table_data.append(
                    [
                        str(i),
                        w_id[:30] + "..." if len(w_id) > 33 else w_id,
                        phase,
                        version[:15] + "..." if len(version) > 18 else version,
                        activity,
                    ]
                )

            print_table(table_data, headers)

            # Create choices for the prompt
            worker_choices = []
            for i, worker in enumerate(workers_info, 1):
                worker_choices.append(str(i))

            selected_index = click.prompt(
                click.style(
                    "Select worker number", fg=ColorTheme.INFO_COLOR, bold=True
                ),
                type=click.Choice(worker_choices),
            )

            # Get the selected worker
            selected_worker = workers_info[int(selected_index) - 1]
            worker_id = selected_worker.get("workerId")

    # Get logs for the selected worker
    try:
        logs_response = capsule_api.logs(capsule_id, worker_id, previous=previous)
    except Exception as e:
        raise AppConfigError(f"Error retrieving logs for worker {worker_id}: {e}")

    # Format logs content
    logs_content = "\n".join([log.get("message", "") for log in logs_response])

    # Display or save logs
    if file:
        try:
            with open(file, "w") as f:
                f.write(logs_content)
            click.echo(f"📁 Logs saved to {file}")
        except Exception as e:
            raise AppConfigError(f"Error saving logs to file {file}: {e}")
    else:
        if logs_content.strip():
            click.echo(logs_content)
        else:
            click.echo("📝 No logs available for this worker.")


# if __name__ == "__main__":
#     cli()
