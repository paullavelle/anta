<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Execute Network Readiness For Use (NRFU) Testing

ANTA provides a set of commands for performing NRFU tests on devices. These commands are under the `anta nrfu` namespace and offer multiple output format options:

- [Text view](#performing-nrfu-with-text-rendering)
- [Table view](#performing-nrfu-with-table-rendering)
- [JSON view](#performing-nrfu-with-json-rendering)
- [Custom template view](#performing-nrfu-with-custom-reports)

### NRFU Command overview

```bash
anta nrfu --help
Usage: anta nrfu [OPTIONS] COMMAND [ARGS]...

  Run NRFU against inventory devices

Options:
  -c, --catalog FILE  Path to the test catalog YAML file  [env var:
                      ANTA_CATALOG; required]
  --help              Show this message and exit.

Commands:
  json        ANTA command to check network state with JSON result
  table       ANTA command to check network states with table result
  text        ANTA command to check network states with text result
  tpl-report  ANTA command to check network state with templated report
```

All commands under the `anta nrfu` namespace require a catalog yaml file specified with the `--catalog` option.

## Tag management

The `--tags` option can be used to target specific devices in your inventory and run only tests configured with this specific tags from your catalog. The default tag is set to `all` and is implicit. Expected behaviour is provided below:

| Command | Description |
| ------- | ----------- |
| `none` | Run all tests on all devices according `tag` definition in your inventory and test catalog. And tests with no tag are executed on all devices|
| `--tags leaf` | Run all tests marked with `leaf` tag on all devices configured with `leaf` tag.<br/> All other tags are ignored |
| `--tags leaf,spine` | Run all tests marked with `leaf` tag on all devices configured with `leaf` tag.<br/>Run all tests marked with `spine` tag on all devices configured with `spine` tag.<br/> All other tags are ignored |

!!! info
    [More examples](tag-management.md) available on this dedicated page.

## Performing NRFU with text rendering

The `text` subcommand provides a straightforward text report for each test executed on all devices in your inventory.

### Command overview

```bash
anta nrfu text --help
Usage: anta nrfu text [OPTIONS]

  ANTA command to check network states with text result

Options:
  -t, --tags TEXT    List of tags using comma as separator: tag1,tag2,tag3
  -s, --search TEXT  Regular expression to search in both name and test
  --skip-error       Hide tests in errors due to connectivity issue
  --help             Show this message and exit.
```

The [`--tags` option allows](#tag-management) to target specific devices in your inventory and run tests with the exact same tags from your catalog, while the `--search` option permits filtering based on a regular expression pattern in both the hostname and the test name.

The `--skip-error` option can be used to exclude tests that failed due to connectivity issues or unsupported commands.

### Example

```bash
anta nrfu text --tags LEAF --search DC1-LEAF1A
```
[![anta nrfu text results](../imgs/anta-nrfu-text-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-text-output.png)

## Performing NRFU with table rendering

The `table` command under the `anta nrfu` namespace offers a clear and organized table view of the test results, suitable for filtering. It also has its own set of options for better control over the output.

### Command overview

```bash
anta nrfu table --help
Usage: anta nrfu table [OPTIONS]

  ANTA command to check network states with table result

Options:
  --tags TEXT               List of tags using comma as separator:
                            tag1,tag2,tag3
  -d, --device TEXT         Show a summary for this device
  -t, --test TEXT           Show a summary for this test
  --group-by [device|test]  Group result by test or host. default none
  --help                    Show this message and exit.
```

The `--device` and `--test` options show a summarized view of the test results for a specific host or test case, respectively.

The `--group-by` option show a summarized view of the test results per host or per test.

### Examples

```bash
anta nrfu table --tags LEAF
```
[![anta nrfu table results](../imgs/anta-nrfu-table-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-table-output.png)

For larger setups, you can also group the results by host or test to get a summarized view:

```bash
anta nrfu table --group-by device
```
[![anta nrfu table group_by_host_output](../imgs/anta-nrfu-table-group-by-host-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-table-group-by-host-output.png)

```bash
anta nrfu table --group-by test
```
[![anta nrfu table group_by_test_output](../imgs/anta-nrfu-table-group-by-test-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-table-group-by-test-output.png)

To get more specific information, it is possible to filter on a single device or a single test:

```bash
anta nrfu table --device spine1
```
[![anta nrfu table filter_host_output](../imgs/anta-nrfu-table-filter-host-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-table-filter-host-output.png)

```bash
anta nrfu table --test VerifyZeroTouch
```
[![anta nrfu table filter_test_output](../imgs/anta-nrfu-table-filter-test-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-table-filter-test-output.png)

## Performing NRFU with JSON rendering

The JSON rendering command in NRFU testing is useful in generating a JSON output that can subsequently be passed on to another tool for reporting purposes.

### Command overview

```bash
anta nrfu json --help
Usage: anta nrfu json [OPTIONS]

  ANTA command to check network state with JSON result

Options:
  -t, --tags TEXT    List of tags using comma as separator: tag1,tag2,tag3
  -o, --output FILE  Path to save report as a file  [env var:
                     ANTA_NRFU_JSON_OUTPUT]
  --help             Show this message and exit.
```

The `--output` option allows you to save the JSON report as a file.

### Example

```bash
anta nrfu json --tags LEAF
```
[![anta nrfu json results](../imgs/anta-nrfu-json-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-json-output.png)

## Performing NRFU with custom reports

ANTA offers a CLI option for creating custom reports. This leverages the Jinja2 template system, allowing you to tailor reports to your specific needs.

### Command overview

```bash
anta nrfu tpl-report --help
Usage: anta nrfu tpl-report [OPTIONS]

  ANTA command to check network state with templated report

Options:
  -tpl, --template FILE  Path to the template to use for the report  [env var:
                         ANTA_NRFU_TPL_REPORT_TEMPLATE; required]
  -o, --output FILE      Path to save report as a file  [env var:
                         ANTA_NRFU_TPL_REPORT_OUTPUT]
  -t, --tags TEXT        List of tags using comma as separator: tag1,tag2,tag3
  --help                 Show this message and exit.
```
The `--template` option is used to specify the Jinja2 template file for generating the custom report.

The `--output` option allows you to choose the path where the final report will be saved.

### Example

```bash
anta nrfu tpl-report --tags LEAF --template ./custom_template.j2
```
[![anta nrfu json results](../imgs/anta-nrfu-tpl-report-output.png){ loading=lazy width="1600" }](../imgs/anta-nrfu-tpl-report-output.png)

The template `./custom_template.j2` is a simple Jinja2 template:

```j2
{% for d in data %}
* {{ d.test }} is [green]{{ d.result | upper}}[/green] for {{ d.name }}
{% endfor %}
```

The Jinja2 template has access to all `TestResult` elements and their values, as described in this [documentation](../api/result_manager_models.md#testresult-entry).

You can also save the report result to a file using the `--output` option:

```bash
anta nrfu tpl-report --tags LEAF --template ./custom_template.j2 --output nrfu-tpl-report.txt
```

The resulting output might look like this:

```bash
cat nrfu-tpl-report.txt
* VerifyMlagStatus is [green]SUCCESS[/green] for DC1-LEAF1A
* VerifyMlagInterfaces is [green]SUCCESS[/green] for DC1-LEAF1A
* VerifyMlagConfigSanity is [green]SUCCESS[/green] for DC1-LEAF1A
* VerifyMlagReloadDelay is [green]SUCCESS[/green] for DC1-LEAF1A
```
