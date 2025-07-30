import markdown
import os
import ui_components
import json
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from dotenv import load_dotenv


def verbose_decorator(func):
    def wrapper(*args, **kwargs):
        verbose = kwargs.get('verbose', False)
        result = func(*args, **kwargs)
        if verbose:
            if isinstance(result, (list, tuple, dict)):
                for item in result:
                    print(item)
            else:
                print(result)
        
        return result
    return wrapper

# === HANDLE IMAGES ===

def load_config():
    load_dotenv()
    config = {}
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

    except FileNotFoundError:
        print("Warning: config.json not found. Using default image dimensions. This usually means you have not ran the setup script. Please run setup.py.")
        config = {"image_dimensions": {"width": 800, "height": 500}}
    
    return config


def get_images_all(relative_path=''):
    img_dir = os.path.join(relative_path, "templates", "assets", "img")
    if not os.path.exists(img_dir):
        print(f"Image directory {img_dir} does not exist")
        return []
    
    try:
        with os.scandir(img_dir) as images:
            list_with_posix_scan_iterator =  list(images)
            return [os.path.join(img_dir, image.name) for image in list_with_posix_scan_iterator if image.is_file()]
    except Exception as e:
        print(f"Error scanning image directory: {e}")
        return []


def image_name_cleanup(relative_path=''):
    try:
      for image in get_images_all():
          weird_chars = [" ", "\u202f", "%20"]
          for char in weird_chars:
              if char in image:
                  os.rename(relative_path+image, (relative_path+image).replace(char,"_"))
    except:
        print("Error, send for re-build")


def images_to_upload():
    """
    Determine which images need to be uploaded to the bucket, skip images that are already in the bucket and bs like .DS_Store
    """
    try:
        # Import bucket functions if available
        from r2_bucket import get_bucket_contents
        
        prev_bucket_contents = ['templates/assets/img/' + image_name for image_name in get_bucket_contents()]
        list_of_all_images = get_images_all()
        images_not_in_bucket = [image for image in list_of_all_images if image not in prev_bucket_contents]
        
        if "templates/assets/img/.DS_Store" in images_not_in_bucket: #removing .DS_Store from the list
            images_not_in_bucket.remove("templates/assets/img/.DS_Store")
        return (images_not_in_bucket)
        
    except ImportError:
        print("Warning: r2_bucket module not available. Skipping bucket operations.")
        return []
    except Exception as e:
        print(f"Error checking bucket contents: {e}")
        return []


class DefaultImageSizeProcessor(Treeprocessor):
    def __init__(self, md, config=None):
        super().__init__(md)
        self.config = config or {"image_dimensions": {"width": 800, "height": 500}}
    
    def run(self, root):
        load_dotenv()
        cdn_url = os.getenv('CDN_URL', 'https://your-amazing-non-existant-cdn.com')
        
        for img in root.iter('img'):
            image_name_cleanup()
            
            bucket_name = os.getenv('STORAGE_BUCKET_NAME')
            if bucket_name:
                try:
                    from r2_bucket import upload
                    for image in images_to_upload():
                        print(f"Uploading -> {image}")
                        upload(image)
                except ImportError:
                    print("Warning: r2_bucket module not available for uploading")
                except Exception as e:
                    print(f"Error uploading images: {e}")
            
            cleaned_name = img.get('src').split('/')[-1]

            weird_chars = [" ", "\u202f", "%20"]
            for char in weird_chars:
                if char in cleaned_name:
                    cleaned_name = cleaned_name.replace(char,"_")

            img.set('src', f'{cdn_url}/{cleaned_name}')
            
            dimensions = self.config.get('image_dimensions', {})
            default_width = str(dimensions.get('width', 800))
            default_height = str(dimensions.get('height', 500))
            
            if 'width' not in img.attrib:
                img.set('width', default_width)
            if 'height' not in img.attrib:
                img.set('height', default_height)
        
        return root


class DefaultImageSizeExtension(Extension):
    """
    Markdown extension to apply default image sizing
    """
    def __init__(self, config=None, **kwargs):
        self.config = config
        super().__init__(**kwargs)
    
    def extendMarkdown(self, md):
        processor = DefaultImageSizeProcessor(md, self.config)
        md.treeprocessors.register(processor, 'default_image_size', 15)


# === RENDER & SERVE ===

def render(markdown_content, root_location="https://google.com", css=None):
    if css is None:
        css = read_stylsheet()
    config = load_config()
    
    output_html = ui_components.html_header_with_stylesheet(css)

    extensions = ['fenced_code', 'codehilite', 'nl2br', 'tables', 'attr_list', DefaultImageSizeExtension(config)]
    
    output_html += markdown.markdown(markdown_content, extensions=extensions)

    output_html += ui_components.not_an_ssg_footer()
    output_html += ui_components.return_home_btn(root_location)

    return output_html

def serve(output_html_path = '/generated.html', port = 6969, open_browser = True):
    import http.server
    import webbrowser

    class SimpleHTMLServer(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = output_html_path 
            return super().do_GET()

    def start_server():
        server = http.server.HTTPServer(("", port), SimpleHTMLServer)
        if open_browser:
            webbrowser.open(f"http://localhost:{port}")
        else:
            print(f"Serving on http://localhost:{port}")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped by user.")
            server.server_close() 

    start_server()


# === CSS RELATED FUNCTIONS ===
@verbose_decorator
def generate_theme_css(theme_name='monokai', verbose = False):
    pre_text = "\n/* Start syntax highlighting for code fences */\n"
    post_text = "\n/* End syntax highlighting for code fences */"
    formatter = HtmlFormatter(style=theme_name)
    return pre_text + formatter.get_style_defs('.codehilite') + post_text

def read_stylsheet(path_to_stylesheet = "./articles_css.css", read_mode = "read"):
    with open(path_to_stylesheet, 'r') as file:
        func = getattr(file, read_mode)
        return func()

def write_stylsheet(css_content, path_to_stylesheet = "./articles_css.css", write_mode = "write") -> None:
    with open(path_to_stylesheet, 'w') as file:
        func = getattr(file, write_mode)
        func(css_content)

@verbose_decorator
def set_theme(style_sheet_path, theme_name = "stata-dark", verbose = False):
    css = remove_theme(style_sheet_path)
    css_generated = generate_theme_css(theme_name).splitlines(keepends=True)
    write_stylsheet(css + css_generated, style_sheet_path, write_mode="writelines")

@verbose_decorator    
def remove_theme(sytle_sheet_path, verbose = False) -> str: # Removes the theme and also returns the remaining css contents
    css = read_stylsheet(sytle_sheet_path, read_mode="readlines")
    new_css, read_flag = [], True

    for line in css:
        if "/* Start syntax highlighting for code fences */" in line:
            read_flag = False
        elif "/* End syntax highlighting for code fences */" in line:
            read_flag = True
            continue

        if read_flag:
            new_css.append(line)
    write_stylsheet(new_css, sytle_sheet_path, write_mode="writelines")
    return new_css

@verbose_decorator
def list_themes(verbose = False):
    return list(get_all_styles())


'''
# === TESTING ===
f = open("demo_comprehensive.md","r")
markdown_content = f.read()
f.close()

f = open("generated.html","w")
f.write(render(markdown_content))
f.close()
'''

#render(markdown_content)
#serve()










# === CLI INTERFACE ===
import argparse
import sys

def cli_main():
    """
    Main CLI interface for Not An SSG
    """
    parser = argparse.ArgumentParser(
        prog='not_an_ssg',
        description="Not An SSG - This is not an SSG. It's a jackfruit",
        epilog='''
Examples:
  %(prog)s render my_article.md                           # Render markdown to HTML
  %(prog)s render my_article.md --output blog.html        # Render with custom output
  %(prog)s serve --port 8080                              # Start server on port 8080
  %(prog)s run my_article.md                              # Render and serve in one command
  %(prog)s run my_article.md --watch                      # Render, serve, and watch for changes
  %(prog)s run my_article.md --port 8080 --watch          # Custom port with file watching
  %(prog)s themes list                                    # List available themes
  %(prog)s themes set monokai                             # Set syntax highlighting theme
  %(prog)s themes generate dracula --output dark.css      # Generate theme CSS

Getting additional info on commands:
  %(prog)s render -h                                      # Show help for images command
  %(prog)s serve list -h                                  # Show help for themes list subcommand
  %(prog)s run -h                                         # Show all options for run command
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output for debugging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # === RENDER COMMAND ===
    render_parser = subparsers.add_parser('render', help='Render markdown file to HTML')
    render_parser.add_argument('input', help='Input markdown file path')
    render_parser.add_argument('-o', '--output', default='generated.html',
                              help='Output HTML file path (default: generated.html)')
    render_parser.add_argument('-c', '--css', help='Custom CSS file path')
    render_parser.add_argument('-r', '--root', default='https://mebin.in',
                              help='Root URL for the return home button (default: https://mebin.in)')
    render_parser.add_argument('--no-images', action='store_true',
                              help='Skip image processing and uploading')
    
    # === SERVE COMMAND ===
    serve_parser = subparsers.add_parser('serve', help='Start development server')
    serve_parser.add_argument('-p', '--port', type=int, default=6969,
                             help='Server port (default: 6969)')
    serve_parser.add_argument('-f', '--file', default='/generated.html',
                             help='HTML file to serve (default: /generated.html)')
    serve_parser.add_argument('--no-browser', action='store_true',
                             help="Don't automatically open browser")
    
    # === RUN COMMAND ===
    run_parser = subparsers.add_parser('run', help='Render markdown and start development server')
    run_parser.add_argument('input', help='Input markdown file path')
    run_parser.add_argument('-o', '--output', default='generated.html',
                           help='Output HTML file path (default: generated.html)')
    run_parser.add_argument('-c', '--css', help='Custom CSS file path')
    run_parser.add_argument('-r', '--root', default='https://mebin.in',
                           help='Root URL for the return home button (default: https://mebin.in)')
    run_parser.add_argument('-p', '--port', type=int, default=6969,
                           help='Server port (default: 6969)')
    run_parser.add_argument('--no-browser', action='store_true',
                           help="Don't automatically open browser")
    run_parser.add_argument('--no-images', action='store_true',
                           help='Skip image processing and uploading')
    run_parser.add_argument('--watch', action='store_true',
                           help='Watch markdown file for changes and auto-rebuild')
    run_parser.add_argument('--watch-interval', type=float, default=1.0,
                           help='Watch interval in seconds (default: 1.0)')
    
    # === THEMES COMMAND ===
    themes_parser = subparsers.add_parser('themes', help='Manage syntax highlighting themes')
    themes_subparsers = themes_parser.add_subparsers(dest='theme_action', help='Theme actions')
    
    # List themes
    list_themes_parser = themes_subparsers.add_parser('list', help='List all available themes')
    
    # Set theme
    set_theme_parser = themes_subparsers.add_parser('set', help='Set active syntax highlighting theme')
    set_theme_parser.add_argument('theme_name', help='Theme name to set')
    set_theme_parser.add_argument('-s', '--stylesheet', default='./articles_css.css',
                                 help='CSS file to modify (default: ./articles_css.css)')
    
    # Generate theme CSS
    generate_theme_parser = themes_subparsers.add_parser('generate', help='Generate theme CSS')
    generate_theme_parser.add_argument('theme_name', help='Theme name to generate')
    generate_theme_parser.add_argument('-o', '--output', help='Output CSS file (prints to stdout if not specified)')
    
    # Remove theme
    remove_theme_parser = themes_subparsers.add_parser('remove', help='Remove current theme from stylesheet')
    remove_theme_parser.add_argument('-s', '--stylesheet', default='./articles_css.css',
                                    help='CSS file to modify (default: ./articles_css.css)')
    
    # === CONFIG COMMAND ===
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Config actions')
    
    # Show config
    show_config_parser = config_subparsers.add_parser('show', help='Show current configuration')
    
    # Setup
    setup_config_parser = config_subparsers.add_parser('setup', help='Run setup wizard')
    
    # === IMAGES COMMAND ===
    images_parser = subparsers.add_parser('images', help='Image management')
    images_subparsers = images_parser.add_subparsers(dest='images_action', help='Image actions')
    
    # List images
    list_images_parser = images_subparsers.add_parser('list', help='List all images in project')
    list_images_parser.add_argument('-p', '--path', default='',
                                   help='Relative path to search (default: current directory)')
    
    # Clean image names
    clean_images_parser = images_subparsers.add_parser('clean', help='Clean up image file names')
    clean_images_parser.add_argument('-p', '--path', default='',
                                    help='Relative path to clean (default: current directory)')
    
    # Upload images
    upload_images_parser = images_subparsers.add_parser('upload', help='Upload images to bucket')
    
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return
    
    # === COMMAND HANDLERS ===
    
    if args.command == 'render':
        handle_render_command(args)
    elif args.command == 'serve':
        handle_serve_command(args)
    elif args.command == 'run':
        handle_run_command(args)
    elif args.command == 'themes':
        handle_themes_command(args)
    elif args.command == 'config':
        handle_config_command(args)
    elif args.command == 'images':
        handle_images_command(args)


def handle_render_command(args):
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        css = None
        if args.css:
            try:
                with open(args.css, 'r', encoding='utf-8') as f:
                    css = f.read()
            except FileNotFoundError:
                print(f"Error: CSS file '{args.css}' not found")
                sys.exit(1)
        
        if args.verbose:
            print(f"Rendering {args.input} -> {args.output}")
            print(f"Root URL: {args.root}")
            if args.css:
                print(f"Using custom CSS: {args.css}")
            if args.no_images:
                print("Skipping image processing")
        
        html_output = render(markdown_content, args.root, css)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"Successfully rendered {args.input} to {args.output}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error rendering file: {e}")
        sys.exit(1)


def handle_serve_command(args):
    if args.verbose:
        print(f"Starting server on port {args.port}")
        print(f"Serving file: {args.file}")
        print(f"Auto-open browser: {not args.no_browser}")
    
    serve(args.file, args.port, not args.no_browser)


def handle_run_command(args):
    import time
    import threading
    from pathlib import Path
    
    def render_file():
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            css = None
            if args.css:
                try:
                    with open(args.css, 'r', encoding='utf-8') as f:
                        css = f.read()
                except FileNotFoundError:
                    print(f"Warning: CSS file '{args.css}' not found, using default")
            
            if args.verbose:
                print(f"Rendering {args.input} -> {args.output}")
            
            html_output = render(markdown_content, args.root, css)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            print(f"Rendered {args.input} to {args.output}")
            return True
            
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found")
            return False
        except Exception as e:
            print(f"Error rendering file: {e}")
            return False
    
    def watch_file():
        if not args.watch:
            return
        
        input_path = Path(args.input)
        css_path = Path(args.css) if args.css else None
        
        if not input_path.exists():
            print(f"Warning: Cannot watch non-existent file {args.input}")
            return
        
        last_md_mtime = input_path.stat().st_mtime
        last_css_mtime = css_path.stat().st_mtime if css_path and css_path.exists() else 0
        
        print(f"Watching {args.input} for changes")
        if css_path:
            print(f"Also watching {args.css} for changes")
        
        while True:
            try:
                time.sleep(args.watch_interval)
                
                current_md_mtime = input_path.stat().st_mtime if input_path.exists() else 0
                current_css_mtime = css_path.stat().st_mtime if css_path and css_path.exists() else 0
                
                if (current_md_mtime > last_md_mtime or 
                    current_css_mtime > last_css_mtime):
                    
                    print(f"File changed, rebuilding")
                    if render_file():
                        last_md_mtime = current_md_mtime
                        last_css_mtime = current_css_mtime
                        print(f"Rebuild complete at {time.strftime('%H:%M:%S')}")
                    
            except KeyboardInterrupt:
                print("\n File watching stopped")
                break
            except Exception as e:
                print(f"Error during file watching: {e}")
                time.sleep(1) 
    
    if not render_file():
        print("Failed to render file. Exiting.")
        sys.exit(1)
    
    try:
        output_path = Path(args.output)
        if not output_path.exists() or output_path.stat().st_size == 0:
            print(f"Error: Output file {args.output} is empty or doesn't exist")
            sys.exit(1)
    except Exception as e:
        print(f"Error checking output file: {e}")
        sys.exit(1)
    
    if args.watch:
        watcher_thread = threading.Thread(target=watch_file, daemon=True)
        watcher_thread.start()
    
    server_file_path = f"/{args.output}" if not args.output.startswith('/') else args.output
    
    if args.verbose:
        print(f"Starting server on port {args.port}")
        print(f"Serving file: {server_file_path}")
        print(f"Auto-open browser: {not args.no_browser}")
        if args.watch:
            print("File watching enabled - press Ctrl+C to stop")
    
    try:
        serve(server_file_path, args.port, not args.no_browser)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


def handle_themes_command(args):
    if not args.theme_action:
        print("Error: No theme action specified. Use 'list', 'set', 'generate', or 'remove'")
        sys.exit(1)
    
    if args.theme_action == 'list':
        themes = list_themes(verbose=args.verbose)
        print("Available syntax highlighting themes:")
        for i, theme in enumerate(themes, 1):
            print(f"  {i:2d}. {theme}")
        print(f"\nTotal: {len(themes)} themes available")
    
    elif args.theme_action == 'set':
        try:
            if args.verbose:
                print(f"Setting theme '{args.theme_name}' in {args.stylesheet}")
            set_theme(args.stylesheet, args.theme_name, verbose=args.verbose)
            print(f"Successfully set theme '{args.theme_name}'")
        except Exception as e:
            print(f"Error setting theme: {e}")
            sys.exit(1)
    
    elif args.theme_action == 'generate':
        try:
            if args.verbose:
                print(f"Generating CSS for theme '{args.theme_name}'")
            theme_css = generate_theme_css(args.theme_name, verbose=args.verbose)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(theme_css)
                print(f"Theme CSS saved to {args.output}")
            else:
                print(theme_css)
        except Exception as e:
            print(f"Error generating theme CSS: {e}")
            sys.exit(1)
    
    elif args.theme_action == 'remove':
        try:
            if args.verbose:
                print(f"Removing theme from {args.stylesheet}")
            remove_theme(args.stylesheet, verbose=args.verbose)
            print("Successfully removed theme from stylesheet")
        except Exception as e:
            print(f"Error removing theme: {e}")
            sys.exit(1)


def handle_config_command(args):
    if not args.config_action:
        print("Error: No config action specified. Use 'show' or 'setup'")
        sys.exit(1)
    
    if args.config_action == 'show':
        print("=== Not An SSG Configuration ===")
        
        # Show .env config
        load_dotenv()
        print("\nStorage Configuration (.env):")
        bucket_name = os.getenv('STORAGE_BUCKET_NAME')
        endpoint_url = os.getenv('STORAGE_ENDPOINT_URL')
        if bucket_name:
            print(f"  Bucket Name: {bucket_name}")
            print(f"  Endpoint URL: {endpoint_url}")
            print(f"  Access Key ID: {'*' * 10}[HIDDEN]")
            print(f"  Secret Key: {'*' * 10}[HIDDEN]")
        else:
            print("  No storage bucket configured")
        
        # Show config.json
        print("\nGeneral Configuration (config.json):")
        try:
            config = load_config()
            if 'image_dimensions' in config:
                dims = config['image_dimensions']
                print(f"  Default image width: {dims.get('width', 'Not set')}")
                print(f"  Default image height: {dims.get('height', 'Not set')}")
            else:
                print("  No image dimensions configured")
        except:
            print("  Configuration file not found")
    
    elif args.config_action == 'setup':
        print("Running setup wizard")
        import subprocess
        try:
            subprocess.run([sys.executable, 'setup.py'], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to run setup.py")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: setup.py not found in current directory")
            sys.exit(1)


def handle_images_command(args):
    if not args.images_action:
        print("Error: No images action specified. Use 'list', 'clean', or 'upload'")
        sys.exit(1)
    
    if args.images_action == 'list':
        images = get_images_all(args.path)
        if images:
            print(f"Images found in '{args.path or 'current directory'}':")
            for i, img in enumerate(images, 1):
                print(f"  {i:2d}. {img}")
            print(f"\nTotal: {len(images)} images")
        else:
            print(f"No images found in '{args.path or 'current directory'}'")
    
    elif args.images_action == 'clean':
        if args.verbose:
            print(f"Cleaning image names in '{args.path or 'current directory'}'")
        image_name_cleanup(args.path)
        print("Image name cleanup completed")
    
    elif args.images_action == 'upload':
        from r2_bucket import upload
        images = images_to_upload()
        if images:
            print(f"Uploading {len(images)} images to bucket...")
            for img in images:
                print(f"  Uploading: {img}")
                upload(img)
            print("All images uploaded successfully")
        else:
            print("No new images to upload")


if __name__ == "__main__":
    cli_main()
