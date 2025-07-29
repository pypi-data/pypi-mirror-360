"""Jobset utils: wraps CRUD operations for jobsets"""

import base64
import enum
import json
import os
import tempfile
import typing
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import click
import colorama

if typing.TYPE_CHECKING:
    from datetime import timedelta

import konduktor
from konduktor import authentication, config, constants, kube_client, logging
from konduktor.data import registry
from konduktor.utils import (
    common_utils,
    exceptions,
    kubernetes_utils,
    log_utils,
    ux_utils,
    validator,
)

if typing.TYPE_CHECKING:
    pass

logger = logging.get_logger(__name__)

JOBSET_API_GROUP = 'jobset.x-k8s.io'
JOBSET_API_VERSION = 'v1alpha2'
JOBSET_PLURAL = 'jobsets'

JOBSET_NAME_LABEL = 'trainy.ai/job-name'
JOBSET_USERID_LABEL = 'trainy.ai/user-id'
JOBSET_USER_LABEL = 'trainy.ai/username'
JOBSET_ACCELERATOR_LABEL = 'trainy.ai/accelerator'
JOBSET_NUM_ACCELERATORS_LABEL = 'trainy.ai/num-accelerators'

SECRET_BASENAME_LABEL = 'konduktor/basename'

_JOBSET_METADATA_LABELS = {
    'jobset_name_label': JOBSET_NAME_LABEL,
    'jobset_userid_label': JOBSET_USERID_LABEL,
    'jobset_user_label': JOBSET_USER_LABEL,
    'jobset_accelerator_label': JOBSET_ACCELERATOR_LABEL,
    'jobset_num_accelerators_label': JOBSET_NUM_ACCELERATORS_LABEL,
}

_RUN_DURATION_ANNOTATION_KEY = 'kueue.x-k8s.io/maxRunDurationSeconds'


class JobNotFoundError(Exception):
    pass


class JobStatus(enum.Enum):
    SUSPENDED = 'SUSPENDED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    PENDING = 'PENDING'


if typing.TYPE_CHECKING:
    import konduktor


def create_pod_spec(task: 'konduktor.Task') -> Dict[str, Any]:
    """Merges the task defintion with config
    to create a final pod spec dict for the job

    Returns:
        Dict[str, Any]: k8s pod spec
    """

    # fill out the templating variables
    assert task.resources is not None, 'Task resources are required'
    if task.resources.accelerators:
        num_gpus = list(task.resources.accelerators.values())[0]
    else:
        num_gpus = 0
    task.name = f'{task.name}-{common_utils.get_usage_run_id()[:4]}'
    node_hostnames = ','.join(
        [f'{task.name}-workers-0-{idx}.{task.name}' for idx in range(task.num_nodes)]
    )
    master_addr = f'{task.name}-workers-0-0.{task.name}'

    if task.resources.accelerators:
        accelerator_type = list(task.resources.accelerators.keys())[0]
    else:
        accelerator_type = None

    assert task.resources.cpus is not None, 'Task resources cpus are required'
    assert task.resources.memory is not None, 'Task resources memory are required'
    assert task.resources.image_id is not None, 'Task resources image_id are required'

    # template the commands to run on the container for syncing files. At this point
    # task.stores is Dict[str, storage_utils.Storage] which is (dst, storage_obj_src)
    # first we iterate through storage_mounts and then file_mounts.
    sync_commands = []
    mkdir_commands = []
    storage_secrets = {}

    # first do storage_mount sync
    for dst, store in task.storage_mounts.items():
        # TODO(asaiacai) idk why but theres an extra storage mount for the
        # file mounts. Should be cleaned up eventually in
        # maybe_translate_local_file_mounts_and_sync_up
        assert store.source is not None and isinstance(
            store.source, str
        ), 'Store source is required'
        store_scheme = urlparse(store.source).scheme
        if '/tmp/konduktor-job-filemounts-files' in dst:
            continue
        # should impelement a method here instead of raw dog dict access
        cloud_store = registry._REGISTRY[store_scheme]
        storage_secrets[store_scheme] = cloud_store._STORE.get_k8s_credential_name()
        mkdir_commands.append(
            f'cd {constants.KONDUKTOR_REMOTE_WORKDIR};' f'mkdir -p {dst}'
        )
        assert store._bucket_sub_path is not None
        sync_commands.append(
            cloud_store.make_sync_dir_command(
                os.path.join(store.source, store._bucket_sub_path), dst
            )
        )

    # then do file_mount sync.
    assert task.file_mounts is not None
    for dst, src in task.file_mounts.items():
        store_scheme = str(urlparse(store.source).scheme)
        cloud_store = registry._REGISTRY[store_scheme]
        mkdir_commands.append(
            f'cd {constants.KONDUKTOR_REMOTE_WORKDIR};'
            f'mkdir -p {os.path.dirname(dst)}'
        )
        storage_secrets[store_scheme] = cloud_store._STORE.get_k8s_credential_name()
        sync_commands.append(cloud_store.make_sync_file_command(src, dst))

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    tailscale_secret = config.get_nested(('tailscale', 'secret_name'), None)
    if tailscale_secret:
        secret_exist, err = kubernetes_utils.check_secret_exists(
            tailscale_secret, namespace, context
        )
        if not secret_exist:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.MissingSecretError(
                    f'No tailscale auth-key secret `{tailscale_secret}` found even '
                    f'though specified by `tailscale.secret_name`: {err}'
                )

    enable_ssh = config.get_nested(('ssh', 'enable'), False)
    secret_name = None
    if enable_ssh:
        private_key_path, public_key_path = authentication.get_or_generate_keys()
        with (
            open(private_key_path, 'rb') as private_key_file,
            open(public_key_path, 'rb') as public_key_file,
        ):
            private_key, public_key = private_key_file.read(), public_key_file.read()
            user_hash = common_utils.get_user_hash()
            secret_name = f'konduktor-ssh-keys-{user_hash}'
            ok, result = kubernetes_utils.set_secret(
                secret_name=secret_name,
                namespace=namespace,
                context=context,
                data={
                    'PUBKEY': base64.b64encode(public_key).decode(),
                    'PRIVKEY': base64.b64encode(private_key).decode(),
                },
            )
            if not ok:
                raise exceptions.CreateSecretError(
                    f'Failed to set k8s secret {secret_name}: \n{result}'
                )

    # Mount the user's secrets
    git_ssh_secret_name = None
    env_secret_envs = []
    default_secrets = []

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    user_hash = common_utils.get_user_hash()
    label_selector = f'konduktor/owner={user_hash}'
    user_secrets = kubernetes_utils.list_secrets(
        namespace, context, label_filter=label_selector
    )

    for secret in user_secrets:
        kind = kubernetes_utils.get_secret_kind(secret)
        if kind == 'git-ssh' and git_ssh_secret_name is None:
            git_ssh_secret_name = secret.metadata.name
        elif kind == 'env':
            env_secret_name = secret.metadata.name
            key = next(iter(secret.data))
            env_secret_envs.append(
                {
                    'name': key,
                    'valueFrom': {
                        'secretKeyRef': {'name': env_secret_name, 'key': key}
                    },
                }
            )
        elif kind == 'default':
            default_secret_name = secret.metadata.name
            basename = secret.metadata.labels.get(
                SECRET_BASENAME_LABEL, default_secret_name
            )
            default_secrets.append(
                {'k8s_name': default_secret_name, 'mount_name': basename}
            )

    with tempfile.NamedTemporaryFile() as temp:
        common_utils.fill_template(
            'pod.yaml.j2',
            {
                # TODO(asaiacai) need to parse/round these numbers and sanity check
                'cpu': kubernetes_utils.parse_cpu_or_gpu_resource(task.resources.cpus),
                'memory': kubernetes_utils.parse_memory_resource(task.resources.memory),
                'image_id': task.resources.image_id,
                'num_gpus': num_gpus,
                'master_addr': master_addr,
                'num_nodes': task.num_nodes,
                'job_name': task.name,  # append timestamp and user id here?
                'setup_cmd': task.setup or '',
                'run_cmd': task.run,
                'node_hostnames': node_hostnames,
                'accelerator_type': accelerator_type,
                'sync_commands': sync_commands,
                'mkdir_commands': mkdir_commands,
                'mount_secrets': storage_secrets,
                'remote_workdir': constants.KONDUKTOR_REMOTE_WORKDIR,
                'user': common_utils.get_cleaned_username(),
                # Tailscale credentials
                'tailscale_secret': tailscale_secret,
                # SSH
                'enable_ssh': enable_ssh,
                'secret_name': secret_name,
                # Kinds of Secrets
                # --kind git-ssh
                'git_ssh': git_ssh_secret_name,
                # --kind default
                'default_secrets': default_secrets,
            },
            temp.name,
        )
        pod_config = common_utils.read_yaml(temp.name)
        # merge with `~/.konduktor/config.yaml``
        kubernetes_utils.combine_pod_config_fields(temp.name, pod_config)
        pod_config = common_utils.read_yaml(temp.name)

    # Priority order: task.envs > secret envs > existing pod_config envs
    existing_envs = pod_config['kubernetes']['pod_config']['spec']['containers'][0].get(
        'env', []
    )
    env_map = {env['name']: env for env in existing_envs}

    # Inject secret envs
    for env in env_secret_envs:
        env_map[env['name']] = env

    # Inject task.envs
    for k, v in task.envs.items():
        env_map[k] = {'name': k, 'value': v}

    # Replace the container's env section with the merged and prioritized map
    pod_config['kubernetes']['pod_config']['spec']['containers'][0]['env'] = list(
        env_map.values()
    )

    # validate pod spec using json schema
    try:
        validator.validate_pod_spec(pod_config['kubernetes']['pod_config']['spec'])
    except ValueError as e:
        raise click.UsageError(str(e))

    return pod_config


def create_jobset(
    namespace: str,
    task: 'konduktor.Task',
    pod_spec: Dict[str, Any],
    dryrun: bool = False,
) -> Optional[Dict[str, Any]]:
    """Creates a jobset based on the task definition and pod spec
    and returns the created jobset spec
    """
    assert task.resources is not None, 'Task resources are undefined'
    if task.resources.accelerators:
        accelerator_type = list(task.resources.accelerators.keys())[0]
        num_accelerators = list(task.resources.accelerators.values())[0]
    else:
        accelerator_type = 'None'
        num_accelerators = 0
    with tempfile.NamedTemporaryFile() as temp:
        common_utils.fill_template(
            'jobset.yaml.j2',
            {
                'job_name': task.name,
                'user_id': common_utils.user_and_hostname_hash(),
                'num_nodes': task.num_nodes,
                'user': common_utils.get_cleaned_username(),
                'accelerator_type': accelerator_type,
                'num_accelerators': num_accelerators,
                'completions': task.resources.get_completions(),
                'max_restarts': task.resources.get_max_restarts(),
                **_JOBSET_METADATA_LABELS,
            },
            temp.name,
        )
        jobset_spec = common_utils.read_yaml(temp.name)
        jobset_spec['jobset']['metadata']['labels'].update(
            **(task.resources.labels or {})
        )
        assert task.resources.labels is not None
        maxRunDurationSeconds = task.resources.labels.get('maxRunDurationSeconds', None)
        if not maxRunDurationSeconds:
            raise ValueError('maxRunDurationSeconds is required')
        jobset_spec['jobset']['metadata']['annotations'][
            _RUN_DURATION_ANNOTATION_KEY
        ] = str(maxRunDurationSeconds)
    jobset_spec['jobset']['spec']['replicatedJobs'][0]['template']['spec'][
        'template'
    ] = pod_spec  # noqa: E501
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        jobset = kube_client.crd_api(context=context).create_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            body=jobset_spec['jobset'],
            dry_run='All' if dryrun else None,
        )
        logger.info(
            f'task {colorama.Fore.CYAN}{colorama.Style.BRIGHT}'
            f'{task.name}{colorama.Style.RESET_ALL} created'
        )
        return jobset
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error creating jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def list_jobset(namespace: str) -> Optional[Dict[str, Any]]:
    """Lists all jobsets in this namespace"""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).list_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error listing jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def get_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves jobset in this namespace"""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).get_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
        )
        return response
    except kube_client.api_exception() as err:
        if err.status == 404:
            raise JobNotFoundError(
                f"Jobset '{job_name}' " f"not found in namespace '{namespace}'."
            )
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error getting jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def delete_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Deletes jobset in this namespace

    Args:
        namespace: Namespace where jobset exists
        job_name: Name of jobset to delete

    Returns:
        Response from delete operation
    """
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).delete_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error deleting jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error deleting jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def get_job(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Gets a specific job from a jobset by name and worker index

    Args:
        namespace: Namespace where job exists
        job_name: Name of jobset containing the job
        worker_id: Index of the worker job to get (defaults to 0)

    Returns:
        Job object if found
    """
    try:
        # Get the job object using the job name
        # pattern {jobset-name}-workers-0-{worker_id}
        job_name = f'{job_name}-workers-0'
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.batch_api(context=context).read_namespaced_job(
            name=job_name, namespace=namespace
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error getting job: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error getting job: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def show_status_table(namespace: str, all_users: bool):
    """Compute cluster table values and display.

    Returns:
        Number of pending auto{stop,down} clusters that are not already
        STOPPED.
    """
    # TODO(zhwu): Update the information for autostop clusters.

    def _get_status_string_colorized(status: Dict[str, Any]) -> str:
        terminalState = status.get('terminalState', None)
        if terminalState and terminalState.upper() == JobStatus.COMPLETED.name.upper():
            return (
                f'{colorama.Fore.GREEN}'
                f'{JobStatus.COMPLETED.name}{colorama.Style.RESET_ALL}'
            )
        elif terminalState and terminalState.upper() == JobStatus.FAILED.name.upper():
            return (
                f'{colorama.Fore.RED}'
                f'{JobStatus.FAILED.name}{colorama.Style.RESET_ALL}'
            )
        elif status['replicatedJobsStatus'][0]['ready']:
            return (
                f'{colorama.Fore.CYAN}'
                f'{JobStatus.ACTIVE.name}{colorama.Style.RESET_ALL}'
            )
        elif status['replicatedJobsStatus'][0]['suspended']:
            return (
                f'{colorama.Fore.BLUE}'
                f'{JobStatus.SUSPENDED.name}{colorama.Style.RESET_ALL}'
            )
        else:
            return (
                f'{colorama.Fore.YELLOW}'
                f'{JobStatus.PENDING.name}{colorama.Style.RESET_ALL}'
            )

    def _get_time_delta(timestamp: str) -> Tuple[str, 'timedelta']:
        delta = datetime.now(timezone.utc) - datetime.strptime(
            timestamp, '%Y-%m-%dT%H:%M:%SZ'
        ).replace(tzinfo=timezone.utc)
        total_seconds = int(delta.total_seconds())

        days, remainder = divmod(total_seconds, 86400)  # 86400 seconds in a day
        hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
        minutes, _ = divmod(remainder, 60)  # 60 seconds in a minute

        days_str = f'{days} days, ' if days > 0 else ''
        hours_str = f'{hours} hours, ' if hours > 0 else ''
        minutes_str = f'{minutes} minutes' if minutes > 0 else ''

        return f'{days_str}{hours_str}{minutes_str}', delta

    def _get_resources(job: Dict[str, Any]) -> str:
        num_pods = int(
            job['spec']['replicatedJobs'][0]['template']['spec']['parallelism']
        )  # noqa: E501
        resources = job['spec']['replicatedJobs'][0]['template']['spec']['template'][
            'spec'
        ]['containers'][0]['resources']['limits']  # noqa: E501
        cpu, memory = resources['cpu'], resources['memory']
        accelerator = job['metadata']['labels'].get(JOBSET_ACCELERATOR_LABEL, None)
        if accelerator:
            return f'{num_pods}x({cpu}CPU, memory {memory}, {accelerator})'
        else:
            return f'{num_pods}x({cpu}CPU, memory {memory}GB)'

    if all_users:
        columns = ['NAME', 'USER', 'STATUS', 'RESOURCES', 'SUBMITTED']
    else:
        columns = ['NAME', 'STATUS', 'RESOURCES', 'SUBMITTED']
    job_table = log_utils.create_table(columns)
    job_specs = list_jobset(namespace)
    assert job_specs is not None, 'Retrieving jobs failed'
    rows = []
    for job in job_specs['items']:
        if all_users:
            rows.append(
                [
                    job['metadata']['name'],
                    job['metadata']['labels'][JOBSET_USERID_LABEL],
                    _get_status_string_colorized(job['status']),
                    _get_resources(job),
                    *_get_time_delta(job['metadata']['creationTimestamp']),
                ]
            )
        elif (
            not all_users
            and job['metadata']['labels'][JOBSET_USER_LABEL]
            == common_utils.get_cleaned_username()
        ):
            rows.append(
                [
                    job['metadata']['name'],
                    _get_status_string_colorized(job['status']),
                    _get_resources(job),
                    *_get_time_delta(job['metadata']['creationTimestamp']),
                ]
            )
    rows = [row[:-1] for row in sorted(rows, key=lambda x: x[-1])]
    # have the most recently submitted jobs at the top
    for row in rows:
        job_table.add_row(row)
    print(job_table)
