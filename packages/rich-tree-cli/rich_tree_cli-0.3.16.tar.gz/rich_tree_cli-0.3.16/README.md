# Rich Tree CLI

Rich Tree CLI provides a beautiful, colorful representation of your directory tree using the [rich](https://github.com/Textualize/rich) library. Generate stunning visual directory trees with custom icons, multiple export formats, and intelligent filtering - perfect for documentation, project exploration, and sharing repository structures.

## ✨ Features

- 🎨 **Beautiful terminal output** with colors and custom icons
- 📁 **Multiple export formats**: HTML, JSON, Markdown, SVG, TOML, XML, YAML, and plain text
- 🔍 **Smart filtering** with built-in gitignore support and custom patterns
- 📊 **Rich metadata** including file sizes, line counts, and file types
- 🎯 **VS Code integration** with clickable file links in HTML output
- ⚡ **Fast and lightweight** with sensible defaults
- 🛠️ **Highly configurable** sorting, depth limits, and display options

## 🚀 Quick Start

### Installation

Install the CLI globally so it's available from anywhere:

```bash
pip install rich-tree-cli
```

Or with uv:

```bash
uv pip install rich-tree-cli
```

### Basic Usage

Generate a tree for the current directory:

```bash
rtree
```

Limit recursion depth:

```bash
rtree --depth 2
```

Export to multiple formats:

```bash
rtree --output-format html json markdown yaml --output myproject
```

Show file metadata:

```bash
rtree --metadata all --depth 3
```

## 📋 Command Options

```bash
rtree [DIRECTORY] [OPTIONS]
```

### Core Options

- `--depth, -d`: Maximum depth of recursion (default: unlimited)
- `--output, -o`: Output file path (extension determined by format)
- `--output-format, -f`: Export formats: `text`, `html`, `json`, `markdown`, `svg`, `toml`, `xml`, `yaml`
- `--metadata, -m`: Show metadata: `none`, `size`, `lines`, `all`

### Filtering Options

- `--exclude, -e`: Exclude files/directories matching patterns
- `--gitignore, -g`: Use custom .gitignore file
- `--sort-order, -s`: Sort order: `files` (files first) or `dirs` (directories first)

### Display Options

- `--icons, -i`: Icon style: `emoji`, `glyphs`, `plain`
- `--disable-color, -dc`: Disable colored output
- `--no-console, -no`: Disable console output (export only)

## 🎨 Export Formats

### HTML Export

Creates a beautiful web page with VS Code integration:

- Clickable file links that open in VS Code
- Custom CSS styling with terminal aesthetics
- Professional presentation ready for documentation

### Markdown Export

Perfect for README files and documentation:

- Clean, readable format
- Integrates seamlessly with GitHub/GitLab
- Great for project overviews

### JSON/TOML/YAML Export

Machine-readable formats for automation:

- Complete directory structure data
- File metadata included
- Easy integration with other tools
- TOML output uses `[metadata]` and `[tree]` tables mirroring the JSON structure

### XML Export

Structured data for XML pipelines:

- Human and machine readable
- Works well with XSLT and other tooling

### SVG Export

Vector graphics for presentations and documentation:

- Scalable visual representation
- Embeddable in web pages and documents
- High-quality output for any size

## 💡 Examples

### Documentation Generation

```bash
# Generate project overview for README
rtree --output-format markdown --output project-structure --depth 3

# Create interactive HTML documentation
rtree --output-format html --metadata all --output docs/structure
```

### Development Workflows

```bash
# Quick project exploration
rtree --depth 2 --icons emoji

# Share repository structure with team
rtree --output-format html json --output project-overview --exclude "*.pyc" "__pycache__"

# Generate structure for AI assistance
rtree --output-format text --metadata size --depth 4
```

### Advanced Filtering

```bash
# Exclude build artifacts and dependencies
rtree --exclude "node_modules" "dist" "build" "*.log"

# Use custom gitignore
rtree --gitignore .gitignore-custom --depth 5

# Show only directories
rtree --sort-order dirs --metadata none
```

## 🏗️ Why Rich Tree CLI?

- **Developer-focused**: Built by developers, for developers, with real workflow needs in mind
- **Beautiful output**: No more ugly ASCII trees - get professional, presentation-ready visualizations
- **Flexible exports**: One command, multiple formats - perfect for documentation, sharing, and automation
- **Smart defaults**: Works great out of the box with sensible gitignore patterns and file detection
- **VS Code integration**: Seamlessly integrates with your development environment

---

## 🛠️ Built With

- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal output and formatting
- **[Jinja2](https://jinja.palletsprojects.com/)** - Powerful HTML template generation  
- **[pathspec](https://github.com/cpburnz/python-pathspec)** - Gitignore pattern matching

---

*Rich Tree CLI - Making directory structures beautiful, one tree at a time* 🌳
