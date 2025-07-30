# Not-An-SSG

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Not--An--SSG-black?logo=github)](https://github.com/mebinthattil/Not-An-SSG)

A minimal, fast static site generator focused on technical blogs and documentation. Not-An-SSG converts Markdown to beautifully styled HTML with excellent syntax highlighting, automatic image optimization, and cloud storage integration.

This evolved out of a basic SSG I wrote to power my own [website](https://mebin.in). It was not initially built to be distributed as a Python package. So this is a re-write of the original SSG with more features and a more robust CLI interface. This is my first Python package, so distributions are not guaranteed to work. Use at your own risk.

## Features

- **Fast & Lightweight**: Decently performant, yet to benchmark. But don't use this if you want the fastest SSG
- **Beautiful Themes**: Modern dark theme optimized for technical content, try `not_an_ssg themes list`
- **Rich Markdown Support**: Tables, code blocks, math expressions and more
- **Image Handling**: Smart optimizations, CDN integration and cloud uploads
- **CLI + Imports**: CLI tools, Python API, and extensive customization options
- **Responsive Design**: Works on mobile devices (yet to extensively test, but typography should be better)
- **Server mode**: Run HTML site in a server with file-watch and auto-rebuilds
- **Code Highlighting**: 100+ syntax highlighting themes powered by Pygments

## Quick Start

### Installation

```bash
pip install not_an_ssg
```

### Basic Usage

1. **Create your first blog post:**
```bash
echo "# Hello World\nThis is my first blog post!" > my-post.md
```

2. **Set up the project (REQUIRED):**
```bash
not_an_ssg config setup
```
This step is essential - it creates the necessary configuration files and directory structure that Not-An-SSG needs to function properly.

3. **Render and serve:**
```bash
not_an_ssg run my-post.md
```
> Your blog will be available at `http://localhost:6969` with automatic browser opening. 
> Port 6969 and auto browswer open is default behavior, both can be changed with flags.

4. **Learn more:**
```bash
not_an_ssg -h
```



## CLI Reference

### Core Commands

#### `render` - Convert Markdown to HTML
```bash
not_an_ssg render input.md [options]
```

**Options:**
- `-o, --output FILE`: Output HTML file (default: generated.html)
- `-c, --css FILE`: Custom CSS file path
- `-r, --root URL`: Root URL for home button (default: https://google.com)
- `--no-images`: Skip image processing and uploading
- `-v, --verbose`: Enable verbose output

**Examples:**
```bash
# Basic rendering
not_an_ssg render blog-post.md

# Custom output file and CSS
not_an_ssg render blog-post.md -o index.html -c custom.css

# Skip image processing
not_an_ssg render blog-post.md --no-images

# Verbose output for debugging
not_an_ssg render blog-post.md -v
```

#### `serve` - Start Development Server
```bash
not_an_ssg serve [options]
```

**Options:**
- `-p, --port PORT`: Server port (default: 6969)
- `-f, --file FILE`: HTML file to serve (default: /generated.html)
- `--no-browser`: Don't automatically open browser

**Examples:**
```bash
# Start server on default port
not_an_ssg serve

# Custom port and file
not_an_ssg serve -p 8080 -f /my-blog.html

# Server without opening browser
not_an_ssg serve --no-browser

# Verbose output for debugging
not_an_ssg serve -v
```

#### `run` - Render and Serve (You're prolly here for this)
```bash
not_an_ssg run input.md [options]
```

**Options:**
- All `render` options &
- All `serve` options &
- `--watch`: Watch for file changes and auto-rebuild
- `--watch-interval SECONDS`: Watch interval (default: 1.0)

**Examples:**
```bash
# Render and serve with live reload
not_an_ssg run blog-post.md --watch

# Custom port with file watching
not_an_ssg run blog-post.md -p 8080 --watch

# Verbose mode for debugging
not_an_ssg run blog-post.md -v --watch
```

### Theme Management

#### `themes list` - List Available Themes
```bash
not_an_ssg themes list
```

#### `themes set` - Apply Syntax Highlighting Theme
```bash
not_an_ssg themes set THEME_NAME [options]
```

**Options:**
- `-s, --stylesheet FILE`: CSS file to modify

> By default sets theme (override theme part only) to the default `articles_css.css` file in the script directory.

**Examples:**
```bash
# Set monokai theme
not_an_ssg themes set monokai

# Set theme for specific stylesheet
not_an_ssg themes set dracula -s custom.css

# Verbose output for debugging
not_an_ssg themes set monokai -v
```

#### `themes generate` - Generate Theme CSS
```bash
not_an_ssg themes generate THEME_NAME [options]
```

**Options:**
- `-o, --output FILE`: Output CSS file (prints to stdout if not specified)

**Examples:**
```bash
# Generate and print theme CSS
not_an_ssg themes generate github-dark

# Save theme to file
not_an_ssg themes generate monokai -o monokai-theme.css

# Verbose output for debugging
not_an_ssg themes generate monokai -v
```

#### `themes remove` - Remove Current Theme
```bash
not_an_ssg themes remove [options]
```

### Configuration Management

#### `config show` - Display Current Configuration
```bash
not_an_ssg config show

# Verbose output for debugging
not_an_ssg config show
```

#### `config setup` - Run Setup Wizard
```bash
not_an_ssg config setup

# Verbose output for debugging
not_an_ssg config setup
```

### Image Management

#### `images list` - List Project Images
```bash
not_an_ssg images list [options]

# List all images in project
not_an_ssg images list

# List images in specific path with verbose output
not_an_ssg images list -p ./v_secret_folder
```

**Options:**
- `-p, --path PATH`: Search path (default: current directory)
- `-v, --verbose`: Enable verbose output

#### `images clean` - Clean Image Filenames
```bash
not_an_ssg images clean [options]

# Clean image names in current directory
not_an_ssg images clean

# Clean specific path with verbose output
not_an_ssg images clean -p ./assets -v
```

**Options:**
- `-p, --path PATH`: Path to clean (default: current directory)
- `-v, --verbose`: Enable verbose output

#### `images upload` - Upload Images to Cloud Storage
```bash
# Upload all images to configured bucket
not_an_ssg images upload

# Upload with verbose output
not_an_ssg images upload -v
```

**Options:**
- `-v, --verbose`: Enable verbose output (highly reccomend using this)

### Common Options

- `-v, --verbose`: Enable verbose output (available on all commands)
- `-h, --help`: Show help message for any command

## Project Structure

```
your-blog/
├── templates/
│   └── assets/
│       └── img/          # Images (auto-uploaded to CDN during render, unless specified otherwise)
├── .env                  # Environment configuration (auto genned by config setup - this is for storage buckets)
├── config.json           # Project configuration (right now only for default image dimensions)
├── articles_css.css      # Main stylesheet (has all the styling and the theme - themes are swappable and auto-generated)
├── your-post.md          # Your markdown files (can be renamed)
└── generated.html        # Generated output (can be renamed)
```

## Configuration

**Important**: Before using Not-An-SSG, you must run the setup wizard. This setup is also directory dependent, so if you want to use Not-An-SSG in a different directory, you'll need to run the setup wizard again. It's not ideal, I know. Will fix this later.

```bash
not_an_ssg config setup
```

This interactive setup process will:
- Create the necessary configuration files (`config.json`, `.env`)
- Set up the required directory structure (`templates/assets/img/`)
- Configure cloud storage settings if desired
- Generate the base CSS file

### Environment Variables (.env)

The setup wizard will create and configure your `.env` file for cloud storage and CDN integration. You don't need to manually edit this file unless you want to change settings later.

Example configuration (automatically generated by setup):

```env
# Cloudflare R2 / AWS S3 Configuration
STORAGE_BUCKET_NAME=your-bucket-name
STORAGE_ACCESS_KEY_ID=your-access-key
STORAGE_SECRET_ACCESS_KEY=your-secret-key
STORAGE_ENDPOINT_URL=https://your-endpoint.com
STORAGE_REGION_NAME=auto
STORAGE_ACCOUNT_ID=your-account-id
CDN_URL=https://your-cdn.com
```
> Note: I use Cloudflare R2 for my bucket, but in theory any S3 compatible storage should work. I am however yet to test this out with S3.

### Project Configuration (config.json)

The setup wizard also creates this file with default settings:

```json
{
  "image_dimensions": {
    "width": 800,
    "height": 500
  }
}
```

You can modify these values manually if needed, or re-run `not_an_ssg config setup` to change them interactively.

## Python API

### Basic Usage

```python
from not_an_ssg import render, serve


# Read markdown content
with open('blog-post.md', 'r') as f:
    markdown_content = f.read()

# Render to HTML
html_output = render(
    markdown_content,
    root_location="https://yourblog.com",
    input_file_path="blog-post.md"
)

# Save output
with open('output.html', 'w') as f:
    f.write(html_output)

# Start development server
serve('/output.html', port=8080)
```

### Advanced Usage

```python
from not_an_ssg import (
    render, 
    generate_theme_css, 
    set_theme,
    get_images_all,
    image_name_cleanup
)

# Custom CSS with theme
custom_css = generate_theme_css('github-dark')
set_theme(custom_css, 'github-dark')

# Render with custom options
html = render(
    markdown_content,
    root_location="https://yourblog.com",
    css=custom_css,
    input_file_path="blog-post.md",
    verbose=True
)

# Image management
images = get_images_all('/path/to/project')
image_name_cleanup('/path/to/project')

```

## Markdown Features

### Code Blocks with Syntax Highlighting

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````
> You can use almost any language - powered by [Pygments](https://pygments.org/)

### Tables

```markdown
| Feature | Status |
|---------|--------|
| Cool    | Yes    |
| Pretty  | Yes    |
| Simple  | Yes    |
| Paid    | No     |
```

### Images with Auto-Processing

```markdown
![Alt text](./templates/assets/img/my-image.jpg)

<!-- With custom dimensions -->
![Alt text](./templates/assets/img/my-image.jpg){width="400" height="300"}
```

### Math Expressions

```markdown
Inline math: $E = mc^2$

Block math:
$$
\frac{d}{dx} \int_a^x f(t)dt = f(x)
$$
```

## Advanced Features

### File Watching and Live Reload

```bash
# Automatically rebuild on file changes
not_an_ssg run blog.md --watch --watch-interval 0.5
```

### Custom CSS Integration

```bash
# Use your own stylesheet
not_an_ssg run blog.md -c custom.css
```

### Cloud Storage Integration

You are expected to place all you images under `templates/assets/img/`. Then, the following features become available:
1. Cleaned filename (removes whitespaces and weird characters)
2. Uploaded to your configured cloud storage
3. Replaced img src with CDN URLs in the final HTML

### Verbose Mode for Debugging

```bash
# See detailed processing information
not_an_ssg run blog.md -v
```

## Troubleshooting

### Common Issues

1. **Images not displaying**: Ensure images are in `templates/assets/img/` directory and you've run `not_an_ssg config setup`
2. **CDN not working**: Run `not_an_ssg config setup` to configure cloud storage settings
3. **Themes not applying**: Run `not_an_ssg themes set THEME_NAME`
4. **Port already in use**: Use `-p` to specify a different port. Only applicable while using `serve`
5. **Missing files error**: Always run `not_an_ssg config setup` before using other commands, although it should automatically prompt you if it does not find the required files.

### Getting Help

```bash
# General help
not_an_ssg -h

# Command-specific help
not_an_ssg render -h
not_an_ssg run -h
```

## Requirements

- Python 3.8+
- Dependencies: `markdown`, `pygments`, `boto3`, `python-dotenv`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! This project was built for personal use but has evolved to make it public. You can find the repo [here](https://github.com/mebinthattil/Not-An-SSG).

## Changelog

### v0.1.0
- Initial release
- Core markdown rendering
- CLI interface
- Theme support
- Cloud storage integration
- Live development server
- Supports syntax highlighting

### Plans for next release
- Support a batch rendering mode
- Introduce file hashing to prevent unnecessary re-renders, reducing build time