# OCSF Compiler

## About

The `ocsf.compiler` package provides an alternative to "compiling" OCSF schemata
with the OCSF server. It is meant to be transparent and approachable. We have
preferred to make operations explicit and readable over efficiency.

The OCSF compilation process is rather involved. The platonic forms of the
schema are built by assembling partial definitions from multiple JSON files
using various operations that have to be applied in a specific order. These
operations may be implicitly required or explicitly declared in the definition.

Those operations include (but are not limited to):

- Expanding annotations in profiles and include files
- Merging properties from include files
- Merging properties from files in extensions that modify core schema elements
- Inheriting from base definitions using `extends`
- Applying profiles for additional attributes
- Building the `uid` enumerations (like `class_uid`) and their `name` sibling attributes
- Merging missing properties of attributes from the dictionary
- Building the extra datetime attributes from the `datetime` profile.

Many of these operations involve merging the JSON data from one file with
another, but with variations in the specifics of the merge operation.

And _some_ operations on dependencies must be completed before they can be
applied, but other operations must wait until later.

We address this with a multi-stage "compiler." `Planner`s identify operations to
be performed. `Operation`s modify definitions in the repository. A `Compilation`
combines planners in phases, analyzes a repository to identify all necessary
operations, then orders operations using the phase and a dependency map before
applying all operations. Finally, a `Protoschema` – a structure that bridges the
gap between a repository and a completed schema – converts the modified
definitions into an OCSF schema representation using the `ocsf.schema` package.

Crucially, _no_ operations are completed during planning. This means planners
err on the side of identifying operations that may later be noops.

## Usage

You can compile a schema from a repository and dump it as JSON to STDOUT with the following:

```sh
$ python -m ocsf.compile path/to/schema
```

You can also view the (many) operations performed to build the schema with the `debug` module:

```sh
$ python -m ocsf.compile.debug path/to/schema
```

The debug utility can also be used to list the properties changed by each operation and to narrow the list of operations down to just a specific file or a file and all of its prerequisite files. For more information, see its help:

```
usage: debug.py [-h] [--file FILE] [--prereqs] [--changes] [--no-changes] path

Debugging tool for OCSF compilation

positional arguments:
  path          Path to the OCSF repository

options:
  -h, --help    show this help message and exit
  --file FILE   Narrow output to operations involving <file>.
  --prereqs     Include operations on prerequisites of <file>.
  --changes     Show changed properties as well as operations.
  --no-changes  Show only operations.
```