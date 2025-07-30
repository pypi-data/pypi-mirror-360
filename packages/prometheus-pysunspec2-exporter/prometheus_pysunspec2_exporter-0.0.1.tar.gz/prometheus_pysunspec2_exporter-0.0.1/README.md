Prometheus pySunSpec2 Exporter
==============================

This (unimaginatively named) Prometheus exporter exposes all of the numeric
data points exposed by a [SunSpec](https://sunspec.org/)-compliant device.
This includes a large number of solar and energy storage systems such as those
manufactured by Fronius amongst [several
hundred](https://sunspec.org/product-certification-registry/) others.

This exporter is based on the
[pySunSpec2](https://github.com/sunspec/pysunspec2) implementation of the
SunSpec standard and therefore should support both older and more recent
SunSpec-compliant devices.


Quick-start
-----------

Install from PyPI using:

    $ pip install prometheus_pysunspec2_exporter

The exporter is started using:

    $ prometheus_pysunspec2_exporter path/to/config.yml [--address=0.0.0.0] [--port=9502]

The exporter is configured via a YAML configuration file ([full documentation
below](#config-documentation)) which looks like:

    ---
    devices:
      - tcp:  # Also supports 'rtu' (serial) and 'file' (for testing)
          ipaddr: 192.168.1.123
          slave_id: 1
        labels:  # Optional extra metric labels
          name: inverter
        excluded_models:  # Optional (accepts numbers or names)
          - common
          - 122

Metrics
-------

All numeric data points are exported as Prometheus gauge metrics whose names
begin `sunspec_*`.

Metric names are constructed from the SunSpec-defined model, group and point
names and the unit (if one is defined). For example, a metric named
`sunspec_mppt_module_1_DCW_W` comes from the ['mppt' model
(160)](https://github.com/sunspec/models/blob/25fbcac7b5b69cbd8550742549d67637bc715523/json/model_160.json),
from the first instance of the group group 'module' (`module_1`) and the point
named `DCW` with the unit `W`.

Metric help strings are constructed from the documentation in the [SunSpec
model database](https://github.com/sunspec/models) and also include documented
enumeration and bit field values where applicable.

An additional metric `sunspec_up` is 1 if data acquisition was successful or 0
otherwise. When data fetching fails, no other metrics for that device will be
included in the scrape.

The following labels are applied:

* `device_type` -- Set to the device type (i.e. one of 'tcp', 'rtu' or 'file')
* All device options are assigned to labels (e.g. `ip_addr` and `slave_id` in
  the example above).
* Additional labels specified in the config are also added.


Config Documentation
--------------------

The configuration format consists of a YAML file defining a map with the
key 'devices' set to an array of device specifications:

    ---
    devices:
      - <device specification>
      - ...

Each device specification is a map containing the following keys:

* One of `tcp`, `rtu` or `file`: Specifies how to connect to the device.
  *Required.*
* `excluded_models`: A list of SunSpec model IDs or names to exclude from the
  gathered metrics. *Optional. Default value: `[]`*
* `labels`: A map defining additional labels to add to all metrics relating to
  this device. Values here override any labels automatically added based on the
  device connection details.

The `tcp`, `rtu` and `file` values must be a map providing connection details
for the Modbus TCP or RTU device, or [dummy SunSpec data
file](https://github.com/sunspec/pysunspec2/tree/e674441123a6a8939e541f935320c857e8205b99/sunspec2/tests/test_data)
to connect to, respectively. A summary of available options, and their defaults
are enumerated below:

    # For Modbus TCP
    tcp:
      ipaddr: '127.0.0.1'              # Required (in practice). Hostname or IP.
      ipport: 502                      # Optional. Port number.
      slave_id: 1                      # Optional. Modbus slave ID
      timeout: null                    # Optional. Modbus request timeout, seconds.
      tls: false                       # Optional. Use TLS
      cafile: None                     # Optional. TLS CA for remote sunspec device.
      insecure_skip_tls_verify: false  # Optional. Skip TLS certificate checking.
      certfile: null                   # Optional. TLS client certificate.
      keyfile: null                    # Optional. TLS client private key.
      max_count: 125                   # Optional. Max number of registers per read
    
    # For Modbus RTU
    rtu:
      slave_id: <int>  # Required. Modbus slave id.
      name: <str>      # Required. Serial port name (e.g. 'com4' or '/dev/ttyUSB0').
      baudrate: 9600   # Optional. Baud rate.
      parity: N        # Optional. Parity. 'N' = None, 'E' = Even.
      timeout: null    # Optional. Modbus request timeout, seconds.
    
    # For dummy file-based devices (for test use)
    file:
      filename: <str>  # Required. The file to read
      addr: 40002      # Optional. The emulated Modbus start address

> [!NOTE]
>
> The supported options map exactly to the constructor arguments of the
> underlying pySunSpec2 device objects
> ([`SunSpecModbusClientDeviceTCP`](https://github.com/sunspec/pysunspec2/blob/e674441123a6a8939e541f935320c857e8205b99/sunspec2/modbus/client.py#L319-L322),
> [`SunSpecModbusClientDeviceRTU`](https://github.com/sunspec/pysunspec2/blob/e674441123a6a8939e541f935320c857e8205b99/sunspec2/modbus/client.py#L366-L400)
> and
> [`FileClientDevice`](https://github.com/sunspec/pysunspec2/blob/e674441123a6a8939e541f935320c857e8205b99/sunspec2/file/client.py#L61-L62)).


See also
--------

This project was inspired by Ramon Buckland's
[inosion/prometheus-sunspec-exporter](https://github.com/inosion/prometheus-sunspec-exporter)
implementation which is built on the [earlier pySunSpec
library](https://github.com/sunspec/pysunspec), but is not a drop-in
replacement. Noteworthy differences between these two exporters include:

* This implementation does have compatible metric names.
* This implementation is built on pySunSpec2 which (apparently) supports some
  newer SunSpec constructs which the original does not. As such, some newer
  devices may only be supported by pySunSpec2.
* This implementation supports reading metrics from multiple devices at once.
* This implementation auto-reconnects to devices (e.g. after a network outage).
* This implementation makes no attempts to guess the metric type to use.
  Everything is always a gauge.
* This implementation doesn't include any data filtering/fix-up functionality.
* This implementation is distributed as a regular Python package on PyPI and
  not as a Docker file.
