# Bauklotz

A Python-based tool for software architecture analysis and visualization.

## Overview

Bauklotz is a framework for building and executing analysis pipelines that process software project structures. It is designed to help software architects analyze codebases through configurable filters and generate various reports and visualizations.

## Features

- Pipeline-based architecture analysis
- Configurable filters for analyzing Python projects
- Multiple report formats (CSV, YAML, UML diagrams)
- Graph-based visualization of class hierarchies
- Extensible filter and report system
- Plugin system for custom filters and reports

## Installation

```bash
pip install bauklotz
```

## Usage

1. Create a configuration file describing your analysis pipeline:

```
channel input

filter builtin.python.project:PythonProjectFilter project
filter builtin.python.structure:PythonClassHierarchyFilter hierarchy
    internal_modules: "your_module"

# External filter example
filter external.metrics:ComplexityFilter complexity
    threshold: 10

report builtin.writer.uml:ClassDiagramWriter classdiagram
   path: "output/classdiagram.uml"

input -> project -> hierarchy -> complexity -> classdiagram
```

2. Run the analysis:

```bash
bauklotz config.bauklotz <project_dir> input --extension external
```

## Configuration

The pipeline is configured using a simple DSL that defines:
- Input channels
- Filters for processing (both built-in and external)
- Reports for output generation
- Connections between components

### Plugin System

Bauklotz supports external filters and reports through its plugin system. Custom filters can be added by:
1. Creating a Python module with filter implementations
2. Registering the module with Bauklotz
3. Referencing the custom filters in your configuration using `external.module:FilterName` syntax

## Core Components

- **Pipe**: Base interface for pipeline construction and execution
- **Filter**: Processes items in the pipeline
- **Report**: Generates output in various formats

## Output Formats

- CSV reports
- YAML summaries
- UML class diagrams
- Graph formats (GML)

## Documentation

For detailed documentation, please visit [documentation link]

## License

BSD3