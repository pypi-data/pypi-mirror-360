#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=R0913,R0914,R0902
import re
from uuid import UUID

from isoduration import parse_duration
from jsonschema import ValidationError
from semver import VersionInfo as SemVerInfo

from .config_chapter import ConfigChapter

# Use 6MB for running container by using crun, runc: https://github.com/moby/moby/pull/41168
MEMORY_LIMIT_MIN = 6 * 1000 * 1000


class Configuration(ConfigChapter):  # noqa: WPS214

    def __init__(  # noqa: WPS211
        self,
        state,
        layers,
        env,
        cmd,
        instances,
        run_parameters,
        offline_ttl,
        download_ttl,
        is_resource_limits,
        runner,
        runners,
        working_dir,
        quotas,
        alerts,
        hostname,
        exposed_ports,
        allowed_connections,
        balancing_policy,
        requested_resources,
        devices,
        resources,
        permissions,
    ):
        self._state = state
        self._layers = layers
        self._env = env
        self._cmd = cmd
        self._instances = instances
        self._run_parameters = run_parameters
        self._offline_ttl = offline_ttl
        self._download_ttl = download_ttl
        self._is_resource_limits = is_resource_limits
        self._runner = runner
        self._runners = runners
        self._working_dir = working_dir
        self._quotas = quotas
        self._alerts = alerts
        self._hostname = hostname
        self._exposed_ports = exposed_ports
        self._allowed_connections = allowed_connections
        self._balancing_policy = balancing_policy
        self._requested_resources = requested_resources
        self._devices = devices
        self._resources = resources
        self._permissions = permissions

    @property
    def state(self):
        return self._state

    @property
    def layers(self):
        return self._layers

    @property
    def env(self):
        return self._env

    @property
    def cmd(self):
        return self._cmd

    @property
    def instances(self):
        return self._instances

    @property
    def run_parameters(self):
        return self._run_parameters

    @property
    def offline_ttl(self):
        return self._offline_ttl

    @property
    def download_ttl(self):
        return self._download_ttl

    @property
    def is_resource_limits(self):
        return self._is_resource_limits

    @property
    def runner(self):
        return self._runner

    @property
    def runners(self):
        return self._runners

    @property
    def working_dir(self):
        return self._working_dir

    @property
    def quotas(self):
        return self._quotas

    @property
    def alerts(self):
        return self._alerts

    @property
    def hostname(self):
        return self._hostname

    @property
    def exposed_ports(self):
        return self._exposed_ports

    @property
    def allowed_connections(self):
        return self._allowed_connections

    @property
    def balancing_policy(self):
        return self._balancing_policy

    @property
    def requested_resources(self):
        return self._requested_resources

    @property
    def devices(self):
        return self._devices

    @property
    def resources(self):
        return self._resources

    @property
    def permissions(self):
        return self._permissions

    @classmethod
    def from_yaml(cls, input_dict):
        configuration = Configuration(
            input_dict.get('state'),
            input_dict.get('layers'),
            input_dict.get('env'),
            input_dict.get('cmd'),
            input_dict.get('instances'),
            input_dict.get('runParameters'),
            input_dict.get('offlineTTL'),
            input_dict.get('downloadTTL'),
            input_dict.get('isResourceLimits', True),
            input_dict.get('runner'),
            input_dict.get('runners', ['runc', 'crun']),
            input_dict.get('workingDir'),
            input_dict.get('quotas'),
            input_dict.get('alerts'),
            input_dict.get('hostname'),
            input_dict.get('exposedPorts'),
            input_dict.get('allowedConnections'),
            input_dict.get('balancingPolicy', 'enabled'),
            input_dict.get('requestedResources'),
            input_dict.get('devices'),
            input_dict.get('resources'),
            input_dict.get('permissions'),
        )
        ConfigChapter.validate(input_dict, validation_file='configuration_schema.json')
        configuration.validate_offline_ttl()
        configuration.validate_download_ttl()
        configuration.validate_runner()
        configuration.validate_runners()
        configuration.validate_exposed_ports()
        configuration.validate_allowed_connections()
        configuration.validate_duration_run_parameters()
        configuration.validate_duration_alerts()
        configuration.validate_quotas()
        configuration.validate_requested_resources()
        configuration.validate_layers()
        return configuration

    def validate_allowed_connections(self):
        if not self._allowed_connections:
            return

        for con in self._allowed_connections:
            connection_data = con.split('/')

            if len(connection_data) != 3:
                raise ValidationError(
                    f'Wrong format in "{con}". '
                    '\n Supported formats are: '
                    '\n  - "service-guid/port/protocol"'
                    '\n  - "service-guid/port-port/protocol" ',
                )
            Configuration.validate_uuid(connection_data[0])
            Configuration.validate_port_range(connection_data[1])
            Configuration.validate_protocol(connection_data[2])

    def validate_exposed_ports(self):
        if not self._exposed_ports:
            return

        for port in self._exposed_ports:
            if isinstance(port, int):
                continue

            parts = port.split('/')
            if len(parts) > 2:
                raise ValidationError(
                    f'Wrong format in "{port}". '
                    '\n Supported formats are: '
                    '\n  - "port-port/protocol"'
                    '\n  - "port/protocol" '
                    '\n  - "port".',
                )
            if parts[1]:
                Configuration.validate_protocol(parts[1])
            Configuration.validate_port_range(parts[0])

    def validate_duration_iso8601(self, parameter_name, parameter_value):
        if not parameter_value or not parameter_name:
            return

        try:
            parse_duration(parameter_value)
        except Exception as exc:
            raise ValidationError(
                f'Parameter: {parameter_name} does not equal to ISO 8601 duration. Error: {exc}',
            ) from exc

    def validate_duration_run_parameters(self):
        if not self.run_parameters:
            return

        self.validate_duration_iso8601('runParameters/startInterval', self.run_parameters.get('startInterval'))
        self.validate_duration_iso8601('runParameters/restartInterval', self.run_parameters.get('restartInterval'))

    def validate_duration_alerts(self):
        if not self.alerts:
            return

        for alert_name, alert_values in self.alerts.items():
            for rule_name, rule_value in alert_values.items():
                if rule_name == 'minTime':
                    self.validate_duration_iso8601('alerts/' + alert_name + '/' + rule_name, rule_value)

    def validate_runner(self):
        if not self.runner:
            return

        allowed_runners = ['runc', 'crun', 'runx', 'xrun']
        if self.runner not in allowed_runners:
            raise ValidationError(f'The runner is not supported: {self.runner}. Supported runners: {allowed_runners}')

    def validate_runners(self):
        if not self.runners:
            return

        allowed_runners = ['runc', 'crun', 'runx', 'xrun']
        for runner_name in self.runners:
            if runner_name not in allowed_runners:
                raise ValidationError(
                    f'The runner is not supported: {self.runners}. Supported runners: {allowed_runners}',
                )

    def validate_offline_ttl(self):
        if not self.offline_ttl:
            return

        self.validate_duration_iso8601('offlineTTL', self.offline_ttl)

    def validate_download_ttl(self):
        if not self.download_ttl:
            return

        self.validate_duration_iso8601('downloadTTL', self.download_ttl)

    @classmethod
    def validate_protocol(cls, protocol_str: str):
        if protocol_str not in {'tcp', 'udp'}:
            raise ValidationError(
                f'Unknown protocol "{protocol_str}". \n Known protocols are : "tcp", "udp"',
            )

    @classmethod
    def validate_port_range(cls, port_range_config: str):
        ports = port_range_config.split('-')
        if len(ports) > 2:
            raise ValidationError(
                f'Unsupported port range config in "{port_range_config}"',
            )

        for port in ports:
            if not port.isdigit():
                raise ValidationError(f'Port "{port}" is not a valid port number.')

        if len(ports) == 2 and int(ports[0]) >= int(ports[1]):
            raise ValidationError(f'Start port "{ports[0]}" is bigger or same than the last "{ports[1]}"')

    @classmethod
    def validate_uuid(cls, uuid_to_test):
        try:
            UUID(uuid_to_test, version=4)
        except ValueError as exc:
            raise ValidationError(f'Service GUID "{uuid_to_test}" is not valid') from exc

    def validate_quotas(self):
        if not self.quotas:
            return

        memory_limit = self.quotas.get('mem')
        if memory_limit and self.runner in {None, 'crun', 'runc'}:
            if self.size_with_units_to_bytes(memory_limit) < MEMORY_LIMIT_MIN:
                raise ValidationError(
                    f'runc and crun requires bigger mem quota than: {MEMORY_LIMIT_MIN} bytes',
                )

    def validate_requested_resources(self):
        if not self.requested_resources:
            return

        memory_limit = self.requested_resources.get('ram')
        if memory_limit and self.runner in {None, 'crun', 'runc'}:
            if self.size_with_units_to_bytes(memory_limit) < MEMORY_LIMIT_MIN:
                raise ValidationError(
                    f'runc and crun requires bigger mem resource than: {MEMORY_LIMIT_MIN} bytes',
                )

    def validate_layers(self):
        if not self.layers:
            return

        layer_uids = []
        for layer in self.layers:
            uid = layer.get('uid')
            min_version = layer.get('minVersion')
            max_version = layer.get('maxVersion')

            if uid in layer_uids:
                raise ValidationError(f'layer {uid} is duplicated in layers list!')

            layer_uids.append(uid)

            if min_version is not None and not SemVerInfo.is_valid(min_version):
                raise ValidationError(
                    f'minVersion: {min_version} of the layer {uid} is not valid. Use SemVer approach!',
                )

            if max_version is not None and not SemVerInfo.is_valid(max_version):
                raise ValidationError(
                    f'maxVersion: {max_version} of the layer {uid} is not valid. Use SemVer approach!',
                )

            if min_version and max_version and SemVerInfo.parse(min_version) > SemVerInfo.parse(max_version):
                raise ValidationError(f'minVersion: {min_version} > maxVersion: {max_version} of the layer {uid}!')

    def size_with_units_to_bytes(self, str_data: str or None) -> int or None:  # noqa: WPS212  # pylint: disable=R0911
        if not str_data:
            return None
        if isinstance(str_data, int):
            return str_data
        if str_data.isdigit():
            return int(str_data)
        # Allowed values: 1b, 1k, 1kb, 1K, 2M, 2m, 3g, 3G. Also can be 1.5k
        parts = list(filter(None, re.split(r'(\d*\.?\d+)', str_data.strip())))
        if len(parts) == 2:
            value_in_bytes, units = parts[0].strip(), parts[1].strip().lower()
            try:
                if units == 'b':
                    return int(value_in_bytes)
                if units in {'k', 'kb'}:
                    return int(float(value_in_bytes) * 1000)
                if units in {'ki', 'kibits'}:
                    return int(float(value_in_bytes) * 1024)
                if units in {'m', 'mb'}:
                    return int(float(value_in_bytes) * 1000 * 1000)
                if units in {'g', 'gb'}:
                    return int(float(value_in_bytes) * 1000 * 1000 * 1000)
            except ValueError:
                pass  # noqa: WPS420

        raise RuntimeError(f'Invalid size value or unknown units: {str_data}')
