<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Inventory and Catalog

The ANTA framework needs 2 important inputs from the user to run: a **device inventory** and a **test catalog**.

Both inputs can be defined in a file or programmatically.

## Device Inventory

A device inventory is an instance of the [AntaInventory](../api/inventory.md#anta.inventory.AntaInventory) class.

### Device Inventory File

The ANTA device inventory can easily be defined as a YAML file.
The file must comply with the following structure:

```yaml
anta_inventory:
  hosts:
    - host: < ip address value >
      port: < TCP port for eAPI. Default is 443 (Optional)>
      name: < name to display in report. Default is host:port (Optional) >
      tags: < list of tags to use to filter inventory during tests >
      disable_cache: < Disable cache per hosts. Default is False. >
  networks:
    - network: < network using CIDR notation >
      tags: < list of tags to use to filter inventory during tests >
      disable_cache: < Disable cache per network. Default is False. >
  ranges:
    - start: < first ip address value of the range >
      end: < last ip address value of the range >
      tags: < list of tags to use to filter inventory during tests >
      disable_cache: < Disable cache per range. Default is False. >
```

The inventory file must start with the `anta_inventory` key then define one or multiple methods:

- `hosts`: define each device individually
- `networks`: scan a network for devices accesible via eAPI
- `ranges`: scan a range for devices accesible via eAPI

A full description of the inventory model is available in [API documentation](api/inventory.models.input.md)

!!! info
    Caching can be disabled per device, network or range by setting the `disable_cache` key to `True` in the inventory file. For more details about how caching is implemented in ANTA, please refer to [Caching in ANTA](advanced_usages/caching.md).

### Example

```yaml
---
anta_inventory:
  hosts:
  - host: 192.168.0.10
    name: spine01
    tags: ['fabric', 'spine']
  - host: 192.168.0.11
    name: spine02
    tags: ['fabric', 'spine']
  networks:
  - network: '192.168.110.0/24'
    tags: ['fabric', 'leaf']
  ranges:
  - start: 10.0.0.9
    end: 10.0.0.11
    tags: ['fabric', 'l2leaf']
```

## Test Catalog

A test catalog is an instance of the [AntaCatalog](../api/catalog.md#anta.catalog.AntaCatalog) class.

### Test Catalog File

In addition to the inventory file, you also have to define a catalog of tests to execute against your devices. This catalog list all your tests, their inputs and their tags.

A valid test catalog file must have the following structure:
```yaml
---
<Python module>:
    - <AntaTest subclass>:
        <AntaTest.Input compliant dictionary>
```

### Example

```yaml
---
anta.tests.connectivity:
  - VerifyReachability:
      hosts:
        - source: Management0
          destination: 1.1.1.1
          vrf: MGMT
        - source: Management0
          destination: 8.8.8.8
          vrf: MGMT
      filters:
        tags: ['leaf']
      result_overwrite:
        categories:
          - "Overwritten category 1"
        description: "Test with overwritten description"
        custom_field: "Test run by John Doe"
```

It is also possible to nest Python module definition:
```yaml
anta.tests:
  connectivity:
    - VerifyReachability:
        hosts:
          - source: Management0
            destination: 1.1.1.1
            vrf: MGMT
          - source: Management0
            destination: 8.8.8.8
            vrf: MGMT
        filters:
          tags: ['leaf']
        result_overwrite:
          categories:
            - "Overwritten category 1"
          description: "Test with overwritten description"
          custom_field: "Test run by John Doe"
```

[This test catalog example](https://github.com/arista-netdevops-community/anta/blob/main/examples/tests.yaml) is maintained with all the tests defined in the `anta.tests` Python module.

### Test tags

All tests can be defined with a list of user defined tags. These tags will be mapped with device tags: when at least one tag is defined for a test, this test will only be executed on devices with the same tag. If a test is defined in the catalog without any tags, the test will be executed on all devices.

```yaml
anta.tests.system:
  - VerifyUptime:
      minimum: 10
      filters:
        tags: ['demo', 'leaf']
  - VerifyReloadCause:
  - VerifyCoredump:
  - VerifyAgentLogs:
  - VerifyCPUUtilization:
      filters:
        tags: ['leaf']
```

!!! info
    When using the CLI, you can filter the NRFU execution using tags. Refer to [this section](cli/tag-management.md) of the CLI documentation.

### Tests available in ANTA

All tests available as part of the ANTA framework are defined under the `anta.tests` Python module and are categorised per family (Python submodule).
The complete list of the tests and their respective inputs is available at the [tests section](api/tests.md) of this website.


To run test to verify the EOS software version, you can do:

```yaml
anta.tests.software:
  - VerifyEosVersion:
```

It will load the test `VerifyEosVersion` located in `anta.tests.software`. But since this test has mandatory inputs, we need to provide them as a dictionary in the YAML file:

```yaml
anta.tests.software:
  - VerifyEosVersion:
      # List of allowed EOS versions.
      versions:
        - 4.25.4M
        - 4.26.1F
```

The following example is a very minimal test catalog:

```yaml
---
# Load anta.tests.software
anta.tests.software:
  # Verifies the device is running one of the allowed EOS version.
  - VerifyEosVersion:
      # List of allowed EOS versions.
      versions:
        - 4.25.4M
        - 4.26.1F

# Load anta.tests.system
anta.tests.system:
  # Verifies the device uptime is higher than a value.
  - VerifyUptime:
      minimum: 1

# Load anta.tests.configuration
anta.tests.configuration:
  # Verifies ZeroTouch is disabled.
  - VerifyZeroTouch:
  - VerifyRunningConfigDiffs:
```

### Catalog with custom tests

In case you want to leverage your own tests collection, use your own Python package in the test catalog.
So for instance, if my custom tests are defined in the `titom73.tests.system` Python module, the test catalog will be:

```yaml
titom73.tests.system:
  - VerifyPlatform:
    type: ['cEOS-LAB']
```

!!! tip "How to create custom tests"
    To create your custom tests, you should refer to this [documentation](advanced_usages/custom-tests.md)

### Customize test description and categories

It might be interesting to use your own categories and customized test description to build a better report for your environment. ANTA comes with a handy feature to define your own `categories` and `description` in the report.

In your test catalog, use `result_overwrite` dictionary with `categories` and `description` to just overwrite this values in your report:

```yaml
anta.tests.configuration:
  - VerifyZeroTouch: # Verifies ZeroTouch is disabled.
      result_overwrite:
        categories: ['demo', 'pr296']
        description: A custom test
  - VerifyRunningConfigDiffs:
anta.tests.interfaces:
  - VerifyInterfaceUtilization:
```

Once you run `anta nrfu table`, you will see following output:

```bash
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Device IP ┃ Test Name                  ┃ Test Status ┃ Message(s) ┃ Test description                              ┃ Test category ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ spine01   │ VerifyZeroTouch            │ success     │            │ A custom test                                 │ demo, pr296   │
│ spine01   │ VerifyRunningConfigDiffs   │ success     │            │                                               │ configuration │
│ spine01   │ VerifyInterfaceUtilization │ success     │            │ Verifies interfaces utilization is below 75%. │ interfaces    │
└───────────┴────────────────────────────┴─────────────┴────────────┴───────────────────────────────────────────────┴───────────────┘
```
