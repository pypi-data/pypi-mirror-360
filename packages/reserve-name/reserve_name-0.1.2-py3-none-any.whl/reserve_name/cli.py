import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import sys
import getpass

def get_package_dir():
    """Get the directory where this package is installed."""
    return Path(__file__).parent

def load_or_create_env_config():
    """Load environment configuration or prompt user to create it."""
    package_dir = get_package_dir()
    env_path = package_dir / '.env'
    
    # Try to load existing .env file
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Found .env file at: {env_path}")
    else:
        print(f"📁 .env file not found at: {env_path}")
        create_env_file = input("Would you like to create a .env file with your API tokens? (y/n): ")
        
        if create_env_file.lower() == 'y':
            create_env_file_interactively(env_path)
            load_dotenv(env_path)
        else:
            print("⚠️  You can create a .env file later at:", env_path)
            print("Required variables: PYPI_API_TOKEN, TEST_PYPI_API_TOKEN, BASE_URL")
    
    # Check for required environment variables
    required_vars = {
        'PYPI_API_TOKEN': 'PyPI API Token',
        'TEST_PYPI_API_TOKEN': 'Test PyPI API Token', 
        'BASE_URL': 'Base directory for package creation'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append((var, description))
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var, desc in missing_vars:
            print(f"  - {var}: {desc}")
        
        prompt_for_missing = input("\nWould you like to provide these values now? (y/n): ")
        if prompt_for_missing.lower() == 'y':
            provide_missing_vars(missing_vars)
        else:
            print("❌ Cannot continue without required environment variables.")
            sys.exit(1)
    
    return {
        'pypi_token': os.getenv('PYPI_API_TOKEN'),
        'test_pypi_token': os.getenv('TEST_PYPI_API_TOKEN'),
        'default_base_dir': os.getenv('BASE_URL')
    }

def create_env_file_interactively(env_path):
    """Create a .env file interactively."""
    print(f"\n📝 Creating .env file at: {env_path}")
    print("Please provide the following information:")
    
    # Get PyPI token
    pypi_token = getpass.getpass("Enter your PyPI API token (input hidden): ")
    
    # Get Test PyPI token
    test_pypi_token = getpass.getpass("Enter your Test PyPI API token (input hidden): ")
    
    # Get base directory
    base_url = input("Enter your base directory for package creation (e.g., /home/user/packages): ")
    
    # Write to .env file
    with open(env_path, 'w') as f:
        f.write(f"PYPI_API_TOKEN={pypi_token}\n")
        f.write(f"TEST_PYPI_API_TOKEN={test_pypi_token}\n")
        f.write(f"BASE_URL={base_url}\n")
    
    print("✅ .env file created successfully!")
    
    # Set secure permissions on the .env file
    try:
        os.chmod(env_path, 0o600)  # Read/write for owner only
        print("✅ Set secure permissions on .env file")
    except Exception as e:
        print(f"⚠️  Could not set secure permissions: {e}")

def provide_missing_vars(missing_vars):
    """Prompt user to provide missing environment variables for current session."""
    print("\n📝 Please provide the missing values:")
    
    for var, desc in missing_vars:
        if 'TOKEN' in var:
            value = getpass.getpass(f"Enter {desc} (input hidden): ")
        else:
            value = input(f"Enter {desc}: ")
        
        os.environ[var] = value
        print(f"✅ Set {var}")

def create_github_actions_workflow(base_dir, package_name):
    """Create GitHub Actions workflow file for automated PyPI publishing."""
    root = Path(base_dir) / package_name
    workflows_dir = root / '.github' / 'workflows'
    
    # Create directories if they don't exist
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # GitHub Actions workflow content
    workflow_content = '''name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
'''
    
    # Write the workflow file
    workflow_path = workflows_dir / 'publish.yml'
    with open(workflow_path, 'w') as f:
        f.write(workflow_content)
    
    print(f"✅ Created GitHub Actions workflow at: {workflow_path}")
    
    return workflow_path

def print_github_actions_instructions(package_name):
    """Print instructions for setting up GitHub Actions and using tags."""
    print("\n" + "=" * 60)
    print("📋 GITHUB ACTIONS SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. 🔑 ADD YOUR PYPI API TOKEN TO GITHUB SECRETS:")
    print("   - Go to your GitHub repository")
    print("   - Click: Settings → Secrets and variables → Actions")
    print("   - Click 'New repository secret'")
    print("   - Name: PYPI_API_TOKEN")
    print("   - Value: your PyPI API token (starts with 'pypi-')")
    
    print("\n2. 🏷️  HOW TO PUBLISH WITH TAGS:")
    print("   The GitHub Action will ONLY run when you push a tag starting with 'v'")
    print("   \n   Example workflow:")
    print("   # Update version in pyproject.toml first")
    print("   git add pyproject.toml")
    print("   git commit -m 'Bump version to 1.0.1'")
    print("   git push")
    print("   \n   # Then create and push a tag")
    print("   git tag v1.0.1")
    print("   git push origin v1.0.1")
    
    print("\n3. ⚠️  IMPORTANT NOTES:")
    print("   - Regular pushes to main will NOT trigger PyPI publishing")
    print("   - Only tagged releases (v*) will automatically publish to PyPI")
    print("   - Make sure your pyproject.toml version matches your tag")
    print("   - You can check the 'Actions' tab in GitHub to see if it worked")
    
    print("\n4. 🔍 EXAMPLE TAG FORMATS THAT WORK:")
    print("   - v1.0.0")
    print("   - v1.0.1")
    print("   - v2.1.0")
    print("   - v1.0.0-beta")
    
    print("\n" + "=" * 60)

# Step 1: Initialize UV project and set up structure
def create_uv_package_structure(base_dir, package_name, package_description):
    base_path = Path(base_dir)
    
    # Change to the base directory
    os.chdir(base_path)
    
    # Initialize UV project
    print(f"Initializing UV project: {package_name}")
    subprocess.run(["uv", "init", package_name], check=True)
    
    # Change to the project directory
    project_root = base_path / package_name
    os.chdir(project_root)
    
    # Read the existing pyproject.toml
    pyproject_path = project_root / 'pyproject.toml'
    
    if pyproject_path.exists():
        # Read existing content
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Add testpypi index configuration
        testpypi_config = '''
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
'''
        
        # Update the description in pyproject.toml
        updated_content = content.replace(
            'description = "Add your description here"',
            f'description = "{package_description}"'
        )
        
        # Also update other fields if they exist
        if 'authors = [' in updated_content:
            updated_content = updated_content.replace(
                'authors = [',
                'authors = [\n    {name = "Your Name", email = "your.email@example.com"},'
            )
        
        # Write the updated content with testpypi config
        with open(pyproject_path, 'w') as f:
            f.write(updated_content + testpypi_config)
        
        print("✅ Added testpypi index configuration to pyproject.toml")
    else:
        print("❌ pyproject.toml not found after uv init")
        raise FileNotFoundError("pyproject.toml not created by uv init")

# Step 2: Build the package
def build_package(base_dir, package_name):
    root = Path(base_dir) / package_name
    os.chdir(root)
    
    print("Building the package...")
    result = subprocess.run(["uv", "build"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to build package: {result.stderr}")
        raise Exception(f"Failed to build package {package_name}")
    else:
        print("✅ Package built successfully!")
        print(result.stdout)

# Step 3: Publish to Test PyPI first
def publish_to_test_pypi(base_dir, package_name, test_pypi_token):
    root = Path(base_dir) / package_name
    os.chdir(root)
    
    # Set environment variable for test PyPI token
    env = os.environ.copy()
    env['UV_PUBLISH_TOKEN'] = test_pypi_token
    
    print("Publishing to Test PyPI...")
    
    # Publish to testpypi
    result = subprocess.run(["uv", "publish", "--index", "testpypi"], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to publish to Test PyPI: {result.stderr}")
        raise Exception(f"Failed to upload package {package_name} to Test PyPI")
    else:
        print("✅ Successfully published to Test PyPI!")
        print(result.stdout)

# Step 4: Publish to PyPI (production)
def publish_to_pypi(base_dir, package_name, pypi_token):
    root = Path(base_dir) / package_name
    os.chdir(root)
    
    # Set environment variable for PyPI token
    env = os.environ.copy()
    env['UV_PUBLISH_TOKEN'] = pypi_token
    
    print("Publishing to PyPI...")
    
    # Publish to PyPI
    result = subprocess.run(["uv", "publish"], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to publish to PyPI: {result.stderr}")
        raise Exception(f"Failed to upload package {package_name} to PyPI")
    else:
        print("✅ Successfully published to PyPI!")
        print(result.stdout)

# Step 5: Create GitHub repository
def create_github_repo(base_dir, package_name):
    root = Path(base_dir) / package_name
    
    try:
        print("Creating GitHub repository...")
        
        # Change to the package directory
        os.chdir(root)
        
        # Initialize git
        subprocess.run(["git", "init"], check=True)
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Create initial commit
        subprocess.run(["git", "commit", "-m", "initial commit"], check=True)
        
        # Create GitHub repo and push
        subprocess.run(["gh", "repo", "create", package_name, "--public", "--source=.", "--push"], check=True)
        
        print(f"✅ GitHub repository created successfully: https://github.com/$(gh api user --jq .login)/{package_name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating GitHub repository: {e}")
        print("Make sure you have 'gh' installed and authenticated (run 'gh auth login')")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating GitHub repository: {e}")
        return False

def main():
    """Main entry point for the reserve-name command."""
    print("🚀 Welcome to Reserve Name - Python Package Name Reservation Tool")
    print("=" * 60)
    
    # Load environment configuration
    config = load_or_create_env_config()
    
    # Get package details from user
    package_name = input("\nEnter the package name you want to reserve: ")
    package_description = input("Enter the description for your package: ")

    # Ask if user wants to use the default base directory
    use_default_base = input(f"Do you want to use the default base directory ({config['default_base_dir']})? (y/n): ")

    if use_default_base.lower() == 'y':
        base_dir = config['default_base_dir']
    else:
        base_dir = input("Enter the base directory where you want to create the package (e.g., D:/MyPackages): ")

    try:
        print("\n🔨 Creating UV package structure...")
        create_uv_package_structure(base_dir, package_name, package_description)

        print("\n📦 Building the package...")
        build_package(base_dir, package_name)

        print("\n🧪 Publishing to Test PyPI first...")
        publish_to_test_pypi(base_dir, package_name, config['test_pypi_token'])

        print("\n🚀 Publishing to PyPI...")
        publish_to_pypi(base_dir, package_name, config['pypi_token'])

        print(f"\n✅ Package {package_name} with description '{package_description}' has been successfully uploaded to both Test PyPI and PyPI!")
        
        # Ask if user wants to create GitHub repository
        create_github = input("\nWould you like to create a GitHub repository for this package? (y/n): ")
        
        if create_github.lower() == 'y':
            github_success = create_github_repo(base_dir, package_name)
            
            if github_success:
                # Ask if user wants to set up GitHub Actions
                setup_actions = input("\nWould you like to set up GitHub Actions for automated PyPI publishing? (y/n): ")
                
                if setup_actions.lower() == 'y':
                    print("\n⚙️ Setting up GitHub Actions...")
                    create_github_actions_workflow(base_dir, package_name)
                    
                    # Add and commit the workflow file
                    try:
                        root = Path(base_dir) / package_name
                        os.chdir(root)
                        subprocess.run(["git", "add", ".github/"], check=True)
                        subprocess.run(["git", "commit", "-m", "Add GitHub Actions workflow for PyPI publishing"], check=True)
                        subprocess.run(["git", "push"], check=True)
                        print("✅ GitHub Actions workflow committed and pushed!")
                    except subprocess.CalledProcessError as e:
                        print(f"⚠️ Created workflow file but failed to commit: {e}")
                        print("You can manually commit the .github/workflows/publish.yml file")
                    
                    # Print setup instructions
                    print_github_actions_instructions(package_name)
                else:
                    print("Skipping GitHub Actions setup.")
            else:
                print("Skipping GitHub Actions setup since repository creation failed.")
        else:
            print("Skipping GitHub repository creation.")
        
        print("\n🎉 All done! Your package name has been reserved successfully!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Package upload failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()