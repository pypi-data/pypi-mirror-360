# This script requires Python 3.11 and is to be used for intalling new API clients.
import os, time, subprocess, shutil, tempfile, shlex, re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from MediLink_API_v3 import ConfigLoader

class SwaggerHandler(FileSystemEventHandler):
    def __init__(self, json_folder):
        self.json_folder = json_folder

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.yaml') or event.src_path.endswith('.json'):
            print(f"New file detected: {event.src_path}")
            time.sleep(2)  # Add a short delay to ensure the file is ready for reading
            self.process_swagger_file(event.src_path)

    def process_swagger_file(self, file_path):
        print(f"Processing file: {file_path}")
        # Sanitize filename to replace spaces with underscores
        sanitized_file_path = os.path.join(os.path.dirname(file_path), sanitize_filename(os.path.basename(file_path)))
        if sanitized_file_path != file_path:
            os.rename(file_path, sanitized_file_path)
            print(f"Renamed file to: {sanitized_file_path}")
            file_path = sanitized_file_path

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_file_path = temp_dir_path / Path(file_path).name
            config_path = temp_dir_path / 'openapi_config.json'
            output_dir = temp_dir_path / "generated_client"

            shutil.copy(file_path, temp_file_path)
            config_source_path = Path(__file__).parent.parent / 'json' / 'openapi_config.json'
            shutil.copy(config_source_path, config_path)
            print(f"Copied files to: {temp_file_path} and {config_path}")

            swagger_definitions = ConfigLoader.load_swagger_file(str(temp_file_path))
            if swagger_definitions:
                print(f"Swagger definitions loaded successfully from: {temp_file_path}")
                if generate_api_client(temp_file_path, output_dir, config_path):
                    backport_code(output_dir)
                    move_generated_client(temp_dir, file_path)
                    provide_instructions(file_path)
            else:
                print(f"Failed to load Swagger definitions from: {temp_file_path}")

def sanitize_filename(filename):
    return filename.replace(' ', '_')

def find_executable(name):
    """Find the full path to an executable."""
    for path in os.environ["PATH"].split(os.pathsep):
        full_path = Path(path) / name
        if full_path.is_file():
            return str(full_path)
    return None

def generate_api_client(swagger_path, output_path, config_path):
    """
    Generate the API client using openapi-generator-cli.
    """
    openapi_generator_path = find_executable('openapi-generator-cli.cmd')
    if not openapi_generator_path:
        print("openapi-generator-cli not found in PATH.")
        return False
    
    command = [
        openapi_generator_path,
        'generate',
        '-i', str(swagger_path),
        '-g', 'python',
        '-o', str(output_path),
        '-c', str(config_path)
    ]
    
    print(f"Attempting command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("API client generated successfully.")
        print(result.stdout)
        print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("First attempt failed.")
        print("Error generating API client:")
        print(e.stdout)
        print(e.stderr)
    
    try:
        print("Attempting with shell=True.")
        result = subprocess.run(' '.join(command), check=True, shell=True, capture_output=True, text=True)
        print("API client generated successfully with shell=True.")
        print(result.stdout)
        print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("Second attempt with shell=True failed.")
        print("Error generating API client:")
        print(e.stdout)
        print(e.stderr)
    
    try:
        quoted_command = [
            openapi_generator_path,
            'generate',
            '-i', shlex.quote(str(swagger_path)),
            '-g', 'python',
            '-o', shlex.quote(str(output_path)),
            '-c', shlex.quote(str(config_path))
        ]
        print(f"Attempting quoted command: {' '.join(quoted_command)}")
        result = subprocess.run(' '.join(quoted_command), check=True, shell=True, capture_output=True, text=True)
        print("API client generated successfully with quoted command.")
        print(result.stdout)
        print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("Third attempt with quoted command failed.")
        print("Error generating API client:")
        print(e.stdout)
        print(e.stderr)
    
    try:
        print("Attempting with batch script.")
        batch_script_content = f"""
        @echo off
        {openapi_generator_path} generate -i "{swagger_path}" -g python -o "{output_path}" -c "{config_path}"
        """
        batch_script_path = Path(tempfile.gettempdir()) / "generate_client.bat"
        with open(batch_script_path, 'w') as batch_script:
            batch_script.write(batch_script_content)
        
        result = subprocess.run(str(batch_script_path), check=True, shell=True, capture_output=True, text=True)
        print("API client generated successfully with batch script.")
        print(result.stdout)
        print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("Fourth attempt with batch script failed.")
        print("Error generating API client:")
        print(e.stdout)
        print(e.stderr)
    
    print("All attempts to generate API client failed.")
    return False

def backport_code(output_dir):
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()

                code = re.sub(r'f"(.*?)"', r'"\1".format', code)  # Replace f-strings
                code = re.sub(r'async def', 'def', code)  # Remove async syntax
                code = re.sub(r'await ', '', code)  # Remove await syntax
                code = re.sub(r':\s*\w+ =', '=', code)  # Remove type hints in variable assignments
                code = re.sub(r'def (\w+)\(.*?\) -> .*?:', r'def \1(', code)  # Remove type hints in function definitions
                code = re.sub(r'(from pydantic import.*)', '# \1', code)  # Comment out pydantic imports
                code = re.sub(r'(import pydantic)', '# \1', code)  # Comment out pydantic imports

                with open(file_path, 'w') as f:
                    f.write(code)
                print(f"Backported {file_path}")

def move_generated_client(temp_dir, original_file_path):
    api_name = Path(original_file_path).stem
    destination_dir = Path('generated_clients') / api_name
    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    try:
        shutil.move(str(Path(temp_dir) / 'generated_client'), str(destination_dir))
        print(f"Moved generated client to {destination_dir}")
    except FileNotFoundError as e:
        print(f"Error moving generated client: {e}")
    except Exception as e:
        print(f"Unexpected error moving generated client: {e}")

def provide_instructions(swagger_path):
    api_name = Path(swagger_path).stem
    instructions = f"""
    API Client for {api_name} has been generated successfully.
    
    Integration Steps:
    1. Locate the generated client code in the 'generated_clients/{api_name}' directory.
    2. Integrate the generated client code into your project by following these steps:
        a. Copy the generated client directory to your project's client directory.
        b. Import the client classes in your project as needed.
        c. Ensure that the generated client adheres to the BaseAPIClient interface if integrating with the existing system.
    3. Update your configuration to include the new API endpoint details.
    4. Test the integration thoroughly to ensure compatibility and functionality.
    
    Example Integration:
    from clients.generated.{api_name}.api_client import ApiClient as {api_name}Client

    class New{api_name}APIClient(BaseAPIClient):
        def __init__(self, config):
            super().__init__(config)
            self.generated_client = {api_name}Client()

        def get_access_token(self, endpoint_name):
            # Implement token retrieval logic
            pass

        def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None):
            # Use the generated client to make the API call
            if call_type == 'GET':
                response = self.generated_client.call_api(url_extension, 'GET', params=params, header_params=headers)
            elif call_type == 'POST':
                response = self.generated_client.call_api(url_extension, 'POST', body=data, header_params=headers)
            elif call_type == 'DELETE':
                response = self.generated_client.call_api(url_extension, 'DELETE', header_params=headers)
            else:
                raise ValueError("Unsupported call type")
            return response
    
    """
    print(instructions)

def main():
    json_folder = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'json'))
    event_handler = SwaggerHandler(json_folder)
    observer = Observer()
    observer.schedule(event_handler, path=json_folder, recursive=False)
    observer.start()
    print(f"Monitoring folder: {json_folder}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
