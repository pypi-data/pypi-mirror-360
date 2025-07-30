from . import experimental


def build_config_from_options(options):
    """Build an app configuration from CLI options."""
    config = {}

    # Set basic fields
    for key in [
        "name",
        "port",
        "image",
        "compute_pools",
        "description",
        "app_type",
        "force_upgrade",
    ]:
        if options.get(key):
            config[key] = options[key]

    # Handle list fields
    if options.get("tags"):
        config["tags"] = list(options["tags"])
    if options.get("secrets"):
        config["secrets"] = list(options["secrets"])

    # Build env dict from key-value pairs
    if options.get("envs"):
        env_dict = {}
        for env_item in options["envs"]:
            env_dict.update(env_item)
        config["environment"] = env_dict

    # Handle dependencies (only one type allowed)
    deps = {}
    if options.get("dep_from_task"):
        deps["from_task"] = options["dep_from_task"]
    elif options.get("dep_from_run"):
        deps["from_run"] = options["dep_from_run"]
    elif options.get("dep_from_requirements"):
        deps["from_requirements_file"] = options["dep_from_requirements"]
    elif options.get("dep_from_pyproject"):
        deps["from_pyproject_toml"] = options["dep_from_pyproject"]

    # TODO: [FIX ME]: Get better CLI abstraction for pypi/conda dependencies

    if deps:
        config["dependencies"] = deps

    # Handle resources
    resources = {}
    for key in ["cpu", "memory", "gpu", "disk"]:
        if options.get(key):
            resources[key] = options[key]

    if resources:
        config["resources"] = resources

    # Handle health check options
    health_check = {}
    if options.get("health_check_enabled") is not None:
        health_check["enabled"] = options["health_check_enabled"]
    if options.get("health_check_path"):
        health_check["path"] = options["health_check_path"]
    if options.get("health_check_initial_delay") is not None:
        health_check["initial_delay_seconds"] = options["health_check_initial_delay"]
    if options.get("health_check_period") is not None:
        health_check["period_seconds"] = options["health_check_period"]

    if health_check:
        config["health_check"] = health_check

    # Handle package options
    if options.get("package_src_path") or options.get("package_suffixes"):
        config["package"] = {}
        if options.get("package_src_path"):
            config["package"]["src_path"] = options["package_src_path"]
        if options.get("package_suffixes"):
            config["package"]["suffixes"] = options["package_suffixes"]

    # Handle auth options
    if options.get("auth_type") or options.get("auth_public"):
        config["auth"] = {}
        if options.get("auth_type"):
            config["auth"]["type"] = options["auth_type"]
        if options.get("auth_public"):
            config["auth"]["public"] = options["auth_public"]

    replicas = {}
    if options.get("min_replicas") is not None:
        replicas["min"] = options["min_replicas"]
    if options.get("max_replicas") is not None:
        replicas["max"] = options["max_replicas"]
    if len(replicas) > 0:
        config["replicas"] = replicas

    config.update(experimental.build_config_from_options(options))

    return config
