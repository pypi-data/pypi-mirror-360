# ONNX2RDF

[![License](https://img.shields.io/github/license/JorgeMIng/ONNX2RDF)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15677129.svg)](https://doi.org/10.5281/zenodo.15677129)
[![Cite this software](https://img.shields.io/badge/Cite%20this-CFF-blue)](https://github.com/JorgeMIng/ONNX2RDF/blob/main/CITATION.cff)
![Python](https://img.shields.io/pypi/pyversions/onnx-2-rdf)
[![PyPI version](https://badge.fury.io/py/onnx-2-rdf.svg)](https://badge.fury.io/py/onnx2rdf)


A Python tool that converts ONNX (Open Neural Network Exchange) models into RDF (Resource Description Framework) representations. This enables semantic querying, ontology integration, and publishing ONNX models describing all the internals workflows of the models as Linked Data.

---

## ✨ Features

- ✅ Parses ONNX model structure into RDF triples (nquads, turtle, trig, trix, jsonld, hdt)
- ✅ Supports ONNX ops, attributes, metadata, functions
- ✅ Removes Initializers values reducing size of final rdf files
- ✅ YARRML and RML pipeline for flexible mappings

---

## ⚙️ System Requirements

To use this tool successfully, the following components must be installed on your system:

- ✅ **Python 3.13+**
- ✅ **Java 17+ (OpenJDK recommended)**  
  Used to run the internal **RML Mapper JAR**
- ✅ **Node.js + npm**
- ✅ [`@rmlio/yarrrml-parser`](https://www.npmjs.com/package/@rmlio/yarrrml-parser)  
  Installed globally via `npm install -g @rmlio/yarrrml-parser`

You can also use the dockerfile (see below) which will prepare the enviroment.

---

## 📦 Installation Options

### Option 1: Install from pip

```bash
pip install onnx_2_rdf
```

### Option 2: Build from Source

Clone and install with [PEP 621](https://peps.python.org/pep-0621/)-compliant `pyproject.toml`:

```bash
git clone https://github.com/JorgeMIng/ONNX2RDF.git
cd ONNX2RDF
pip install .
```

This installs the CLI command `onnx-parser`.

---

### Option 3: Using Docker

```bash
git clone https://github.com/JorgeMIng/ONNX2RDF.git
cd ONNX2RDF
docker build -t onnx2rdf .
docker run -it onnx2rdf
```

This Docker image includes:

- Python 3.13
- OpenJDK 17
- Node.js + npm
- `@rmlio/yarrrml-parser`
- ONNX2RDF + CLI

---

## 🚀 Usage

### Command-Line Interface

```bash
onnx-parser path/to/model.onnx [OPTIONS]
```

### Positional Argument

| Argument        | Description |
|-----------------|-------------|
| `model_path`    | Path to a single ONNX model file or a directory containing multiple ONNX models. Can be absolute or relative. |

### Main Options

| Option               | Description |
|----------------------|-------------|
| `--target_path`      | Output directory for RDF files (default: `rdfs`). Can be absolute or relative. |
| `--rdf_format`       | RDF serialization format: `nquads` (default), `turtle`, `trig`, `trix`, `jsonld`, `hdt`. |
| `--model_name_path`  | Used to define a specific name in the URI for the model. Defaults to the filename or folder of `model_path` |
| `--base_url`         | Base URL for resources in the RDF (e.g., `http://base.onnx.model.com/resource/`). Defaults to a hardcoded URI scheme. |

### Logging Options

| Option               | Description |
|----------------------|-------------|
| `--log_folder`       | Path to log output directory (default: `logs`). |
| `--log_persistant`   | If set, logs are stored in timestamped folders instead of `last_execution`. |
| `--log_extra`        | If set, temporary debug files are included in logs. Only applied if `--log_persistant` is also set. |
| `--to_console`       | Disable logging to the console (set to `false` to turn off). Default: `true`. |
| `--verbose` or `-v`  | Enables verbose output from the RML mapping process. (Not Recommeded too much information) |

### Pipeline Control

| Option               | Description |
|----------------------|-------------|
| `--debug`            | If set, temporary files created during execution will not be deleted (unless overridden by cache settings). |
| `--stop-parsing`     | If set, stops the process after ONNX preprocessing and before RML mapping. |
| `--id_process`       | Custom identifier added to temp and output files. Useful for parallel processing. |
| `--work_folder`      | Changes the relative base folder for input/output (models, logs, RDF). Default to folder where the software is being called from |

### Caching Options

| Option               | Description |
|----------------------|-------------|
| `--cache [PART ...]` | Enables caching by keeping temporary files in `--tmp_folder`. Optionally, specify parts to cache (valid. `all`, `load-model`, `pre-process`, `yamml2rml`,`mapping`). 
| `--tmp_folder`       | Path to the temporary working folder (default: `tmp`). |
| `--error_folder`     | Folder to store files related to errors (default: `errors`). |

### Custom Mapping

| Option               | Description |
|----------------------|-------------|
| `--extra [PART ...]` | Inject additional YARRML or RML mapping files into the pipeline. Use with caution for adding custom triples. 



---


### Example

```bash
onnx-parser models/resnet50.onnx \
  --target_path output_rdf \
  --rdf_format turtle \
  --log_persistant \
  --log_extra
```

This will:

- Parse the `resnet50.onnx` model
- Output RDF in Turtle format to `output_rdf/`
- Save logs with extra files in a timestamped log folder



## ⚙️ Advanced Usage as a Library

Besides the command-line interface, ONNX2RDF also works as a Python library for programmatic integration.

### Main Parser Class

The core class is `ONNX2RDFParser` which encapsulates all main configuration and parsing logic.

```python
from ONNX2RDF.parser import ONNX2RDFParser

parser = ONNX2RDFParser()

# Set parameters
parser.set_target_path("rdfs")
parser.set_rdf_format("nquads")
parser.set_log_extra_files(True)
parser.set_verbose(True)
# ... other configuration methods available

# Parse a single file or folder
parser.parse_file(
    model_path="models/resnet.onnx",
    model_name=None,
    base_resource_url="http://base.onnx.model.com/resource/",
    id_process="",
    extra_files=["custom-mapping.yml"]
)

# For using the pipeline (yarrml to rdf) for custom yarrrml , use:
parser.yarrml2_rdf_pipeline(
    yarrml_path="metadata/global-mapping.yml",
    file_name="global_metadata",
    output_folder="result_extra"
)

```

### About `--extra` (Custom Mappings)

The `--extra` CLI option allows adding extra YARRRML or RML mapping files to be executed **per ONNX file** during parsing. This is useful for adding custom triples dynamically for each model.

⚠️ If you want to create metadata that applies **globally to a folder** (not per file), consider using the `yarrml2_rdf_pipeline` method in the `ONNX2RDFParser` class to generate those triples once and separately.


## 🌐 URI Generation

Each RDF resource generated from an ONNX model is assigned a unique URI. These URIs follow a structured pattern to ensure clarity, uniqueness, and consistency across models and folders.

### URI Template

```
{base_url}{model_name_path}/{resource_type}/{resource_id}
```

To understand how `resource_type` and `resource_id` are created take a look at the detailed documentaion [here (link)](URI_DOCS.md)

- `base_url`: Set via `--base_url`  
  Default: `http://base.onnx.model.com/resource/`

- `model_name_path`: Used to uniquely identify the ONNX model context.  
- `resource_type`: ONNX entity type (`Node`, `Tensor`, `Graph`, etc.)  
- `resource_id`: Identifier from the ONNX model (e.g., operation or tensor name)

---

##  🌐 How `model_name_path` Is Determined

### If `--model_name_path` is **not provided**

The parser will **infer** a `model_name_path` from the ONNX file's location:

- For a **single ONNX file**: uses the file name (without extension)
- For a **folder of ONNX files**: the name of the last folder of the input path is used. Followed by the relative path from that folder to each of the onnx files on the folder (subfolders included) replacing all folder separators (`/`) with dots (`.`)


#### Examples (No `--model_name_path`):

| Input Path             | Inferred `model_name_path`              | Example URI                                                                 |
|------------------------|-----------------------------------------|------------------------------------------------------------------------------|
| `resnet.onnx`          | `resnet`                               | `http://base.onnx.model.com/resource/resnet/Node/node_id`                    |
| `models`              | `models.mobilenet` (for `models/mobilenet.onnx`) | `http://base.onnx.model.com/resource/models.mobilenet/Node/node_id`         |
| `models/exp`     | `exp.set1.mobilenet` (for `models/exp/set1/mobilenet.onnx`) | `http://base.onnx.model.com/resource/exp.set1.mobilenet/Node/node_id`       |

---

###  If `--model_name_path` **is provided**

You can **explicitly define** a model namespace using `--model_name_path`. This modifies how the `model_name_path` is constructed:

- For a **single ONNX file**: the provided `model_name_path` is used exactly as given.
- For a **folder with multiple ONNX files**: the first folder part of the input path is **replaced** by the provided `model_name_path`, and the rest of the relative path (including subfolders and filename without extension) is appended with dots (`.`) replacing folder separators.

Any slashes (`/`) in `--model_name_path` are converted to dots (`.`) for consistency.

#### Examples (`--model_name_path` used):

| Input Path             | `model_name_path`  | Final `model_name_path`| Example URI                                                                 |
|------------------------|-----------------------|------------------------------------------------|------------------------------------------------------------------------------|
| `resnet.onnx`          | `hugg/resnet`         | `hugg/resnet`                                   | `http://base.onnx.model.com/resource/hugg/resnet/Node/node_id`              |
| `models`              | `experiments/v1`      | `experiments/v1.mobilenet` (for `models/mobilenet.onnx`) | `http://base.onnx.model.com/resource/experiments/v1.mobilenet/Node/node_id` |
| `models`          | `research/cases`      | `research/cases.a.b.model` (for `models/a/b/model.onnx`) | `http://base.onnx.model.com/resource/research/cases.a.b.model/Graph/graph_id`  |



## 📚 Related Resources


- [ONNX Format](https://onnx.ai/)  
  The Open Neural Network Exchange (ONNX) standard for representing ML models.

- [RDF Basics](https://www.w3.org/RDF/)  
  Introduction to the Resource Description Framework (RDF) by W3C.

- [SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/)  
  Official SPARQL 1.1 Query Language specification and examples.


## 🛠️ TODO

Improvements and future features can be found on [TODO.md (link)](TODO.md):

Feel free to contribute! Check out the [Issues](https://github.com/JorgeMIng/ONNX2RDF/issues) tab for current tasks and discussions.

## 📄 License

This project is licensed under the terms of the Apache2.0 license.  
See [LICENSE](LICENSE) for more information.



## 🙌 Acknowledgments

- Built using the [ONNX](https://onnx.ai/) Python API.
- RML Mapping powered by the [RMLMapper](https://github.com/RMLio/rmlmapper-java).
- YARRRML parsing supported via [@rmlio/yarrrml-parser](https://www.npmjs.com/package/@rmlio/yarrrml-parser).
- HDT output enabled via [PySHACL](https://github.com/RDFLib/pySHACL) and [RDFLib](https://github.com/RDFLib/rdflib).
- Developed by OEG (Ontology Engineering Group) of Polytechnic University of Madrid.



## 📑 Citation

If you use this software, please cite it as or refer to [ZENODO (link)](https://doi.org/10.5281/zenodo.15681919):

```bibtex
@software{martin_izquierdo_2025_onnx2rdf,
  author       = {Jorge Martín Izquierdo},
  title        = {ONNX to RDF Parser},
  version      = {0.1.4},
  date         = {2025-06-16},
  doi          = {10.5281/zenodo.15681919},
  url          = {https://github.com/JorgeMIng/ONNX2RDF},
  license      = {Apache 2.0},
  affiliation  = {Universidad Politécnica de Madrid},
  keywords     = {ONNX, RDF, Semantic Web, Machine Learning},
  orcid        = {https://orcid.org/0009-0005-7696-8995}
}
```



## 📫 Contact

For questions, feedback, or contributions, feel free to reach out:

- GitHub Issues: https://github.com/JorgeMIng/ONNX2RDF/issues
- Email: **Jorge Martín Izquierdo** – [jorge.martin.izquierdo@upm.es](mailto:jorge.martin.izquierdo@upm.es)
