#!/usr/bin/env python3
"""
AI Project Generator - Sıfırdan proje oluşturma pipeline
"""
import subprocess
import json
import pathlib
import argparse
import sys
import logging
import re
from datetime import datetime
from typing import Optional, List

# Optional tqdm for progress bar (graceful fallback)
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm = None

# Setup logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_generator.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure console encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        pass


class GeneratorError(Exception):
    """Base exception for generator errors"""
    pass


class ProjectGenerator:
    def __init__(self, config_path: str = "generator_config.json"):
        """Initialize project generator with configuration"""
        self.config = self._load_config(config_path)
        self.output_dir = pathlib.Path(self.config['output_dir'])
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.steps_completed = 0
        self.total_steps = 4  # planning, structure, implementation, validation
    
    def _progress_bar(self, items: List, desc: str = "Processing"):
        """Create a progress bar if tqdm is available, otherwise return items as-is"""
        if TQDM_AVAILABLE and tqdm:
            return tqdm(items, desc=desc, ncols=80, leave=True)
        return items
    
    def _update_progress(self, step_name: str):
        """Update and display progress for current step"""
        self.steps_completed += 1
        progress_pct = (self.steps_completed / self.total_steps) * 100
        logger.info(f"[{self.steps_completed}/{self.total_steps}] ({progress_pct:.0f}%) {step_name} completed")
        
    def _load_config(self, config_path: str) -> dict:
        """Load and validate configuration"""
        try:
            config_file = pathlib.Path(config_path)
            if not config_file.exists():
                # Create default config
                default_config = {
                    "output_dir": "generated_projects",
                    "logs_dir": "logs",
                    "templates_dir": "templates",
                    "steps": {
                        "planning": True,
                        "structure": True,
                        "implementation": True,
                        "validation": True
                    }
                }
                config_file.write_text(json.dumps(default_config, indent=2), encoding='utf-8')
                logger.info(f"Created default config: {config_path}")
                return default_config
            return json.loads(config_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise GeneratorError(f"Invalid JSON in config: {e}")
    
    def _run_command(self, cmd: str, description: str) -> str:
        """Run shell command with error handling"""
        try:
            logger.info(f"Running: {description}")
            result = subprocess.check_output(
                cmd, 
                shell=True, 
                text=True,
                encoding='utf-8',
                errors='replace',
                stderr=subprocess.STDOUT
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {description}")
            logger.error(f"Error: {e.output}")
            raise GeneratorError(f"Failed to execute: {description}") from e
    
    def _save_output(self, filename: str, content: str):
        """Save output to file with timestamp"""
        logs_dir = pathlib.Path(self.config['logs_dir'])
        logs_dir.mkdir(exist_ok=True)
        output_path = logs_dir / f"{self.timestamp}_{filename}"
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"Saved output to: {output_path}")
    
    def step_planning(self, project_name: str, description: str, tech_stack: str) -> dict:
        """Step 1: Generate project plan with Gemini"""
        if not self.config['steps'].get('planning', True):
            logger.info("Skipping planning step")
            return {}
        
        logger.info("[GEMINI] Creating project plan")
        
        # Ensure logs directory exists
        logs_dir = pathlib.Path(self.config['logs_dir'])
        logs_dir.mkdir(exist_ok=True)
        
        # Create planning prompt
        prompt_file = logs_dir / f"{self.timestamp}_planning_prompt.txt"
        prompt_content = f"""You are a senior software architect and full-stack developer.

PROJECT BRIEF:
Name: {project_name}
Description: {description}
Technology Stack: {tech_stack}

YOUR TASK:
Create a comprehensive project plan with the following structure (RETURN ONLY VALID JSON):

{{
  "project_name": "{project_name}",
  "description": "{description}",
  "tech_stack": "{tech_stack}",
  "folder_structure": {{
    "root_files": ["README.md", ".gitignore", "package.json"],
    "directories": {{
      "src": ["index.js", "app.js"],
      "public": ["index.html", "styles.css"],
      "config": ["config.js"]
    }}
  }},
  "dependencies": {{
    "runtime": ["express", "dotenv"],
    "dev": ["nodemon", "eslint"]
  }},
  "setup_commands": [
    "npm install",
    "npm run dev"
  ],
  "files_to_generate": [
    {{
      "path": "README.md",
      "description": "Project documentation with setup instructions"
    }},
    {{
      "path": "package.json",
      "description": "NPM package configuration"
    }},
    {{
      "path": "src/index.js",
      "description": "Main application entry point"
    }}
  ]
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown formatting
- Include all necessary files for a working project
- Be specific about folder structure
- Include setup instructions"""
        
        prompt_file.write_text(prompt_content, encoding='utf-8')
        
        # Use PowerShell to pipe to gemini
        prompt_file_abs = str(prompt_file.absolute())
        cmd = f'powershell -Command "Get-Content \'{prompt_file_abs}\' | gemini -p -"'
        
        plan_output = self._run_command(cmd, "Project planning")
        self._save_output("project_plan.json", plan_output)
        
        # Extract JSON from response
        try:
            plan = json.loads(plan_output)
            logger.info(f"Project plan created: {len(plan.get('files_to_generate', []))} files to generate")
            return plan
        except json.JSONDecodeError:
            logger.warning("Plan output is not valid JSON, attempting to extract...")
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', plan_output)
            if json_match:
                plan_json = json_match.group(1).strip()
                self._save_output("project_plan_extracted.json", plan_json)
                return json.loads(plan_json)
            
            # Try to find any JSON object
            json_match = re.search(r'\{[\s\S]*\}', plan_output)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise GeneratorError("Could not extract valid JSON from planning output")
    
    def step_structure(self, project_name: str, plan: dict) -> Optional[pathlib.Path]:
        """Step 2: Create project folder structure"""
        if not self.config['steps'].get('structure', True):
            logger.info("Skipping structure step")
            return None
        
        logger.info("[FILESYSTEM] Creating project structure")
        
        # Create project root directory
        output_base = pathlib.Path(self.config['output_dir'])
        project_root = output_base / project_name
        
        if project_root.exists():
            logger.warning(f"Project directory already exists: {project_root}")
            # Add timestamp suffix
            project_root = output_base / f"{project_name}_{self.timestamp}"
        
        project_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created project root: {project_root}")
        
        # Create folder structure from plan
        folder_structure = plan.get('folder_structure', {})
        
        # Create root files (empty for now)
        for root_file in folder_structure.get('root_files', []):
            (project_root / root_file).touch()
            logger.info(f"  Created: {root_file}")
        
        # Create directories and their files
        directories = folder_structure.get('directories', {})
        for dir_name, files in directories.items():
            dir_path = project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  Created directory: {dir_name}/")
            
            for file_name in files:
                file_path = dir_path / file_name
                # Create parent directories if file is nested (e.g., css/styles.css)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()
                logger.info(f"    Created: {dir_name}/{file_name}")
        
        logger.info(f"Project structure created successfully: {project_root}")
        return project_root
    
    def step_implementation(self, project_root: pathlib.Path, plan: dict):
        """Step 3: Generate code files with Codex"""
        if not self.config['steps'].get('implementation', True):
            logger.info("Skipping implementation step")
            return
        
        logger.info("[CODEX] Generating project files")
        
        files_to_generate = plan.get('files_to_generate', [])
        if not files_to_generate:
            logger.warning("No files to generate in plan")
            return
        
        logger.info(f"Generating {len(files_to_generate)} files...")
        
        # Ensure logs directory exists
        logs_dir = pathlib.Path(self.config['logs_dir'])
        logs_dir.mkdir(exist_ok=True)
        
        # Create comprehensive prompt for Codex
        prompt_file = logs_dir / f"{self.timestamp}_implementation_prompt.txt"
        
        files_list = "\n".join([
            f"- {f['path']}: {f['description']}" 
            for f in files_to_generate
        ])
        
        prompt_content = f"""You are an expert full-stack developer.

PROJECT: {plan.get('project_name', 'Unknown')}
DESCRIPTION: {plan.get('description', 'No description')}
TECH STACK: {plan.get('tech_stack', 'Not specified')}

PROJECT ROOT: {project_root}

FILES TO CREATE:
{files_list}

DEPENDENCIES:
Runtime: {', '.join(plan.get('dependencies', {}).get('runtime', []))}
Dev: {', '.join(plan.get('dependencies', {}).get('dev', []))}

INSTRUCTIONS:
1. Generate complete, production-ready code for each file
2. Include proper error handling and best practices
3. Add helpful comments
4. Ensure all files work together as a cohesive project
5. Follow the specified tech stack conventions

Start by creating all necessary files with complete implementations.
Work in the directory: {project_root}"""
        
        prompt_file.write_text(prompt_content, encoding='utf-8')
        
        # Use PowerShell to pipe to codex
        prompt_file_abs = str(prompt_file.absolute())
        cmd = f'cd "{project_root}" && powershell -Command "Get-Content \'{prompt_file_abs}\' | codex exec --dangerously-bypass-approvals-and-sandbox"'
        
        try:
            result = self._run_command(cmd, "Code generation")
            self._save_output("codex_implementation.txt", result)
            logger.info("Code generation completed successfully")
        except GeneratorError as e:
            logger.error(f"Code generation failed: {e}")
            logger.warning("Some files may not have been generated")
    
    def step_validation(self, project_root: pathlib.Path):
        """Step 4: Validate generated project"""
        if not self.config['steps'].get('validation', True):
            logger.info("Skipping validation step")
            return
        
        logger.info("[VALIDATION] Checking generated project")
        
        # Count generated files
        all_files = list(project_root.rglob('*'))
        file_count = len([f for f in all_files if f.is_file()])
        dir_count = len([f for f in all_files if f.is_dir()])
        
        logger.info(f"  Files created: {file_count}")
        logger.info(f"  Directories created: {dir_count}")
        
        # Check for essential files
        essential_files = ['README.md', 'package.json', '.gitignore']
        for essential in essential_files:
            file_path = project_root / essential
            if file_path.exists():
                size = file_path.stat().st_size
                logger.info(f"  ✓ {essential} ({size} bytes)")
            else:
                logger.warning(f"  ✗ {essential} not found")
        
        logger.info("Validation completed")
    
    def generate(self, project_name: str, description: str, tech_stack: str):
        """Run the complete project generation pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("AI PROJECT GENERATOR")
            logger.info("=" * 60)
            logger.info(f"Project: {project_name}")
            logger.info(f"Description: {description}")
            logger.info(f"Tech Stack: {tech_stack}")
            logger.info("=" * 60)
            
            # Step 1: Planning
            plan = self.step_planning(project_name, description, tech_stack)
            self._update_progress("Planning")
            
            # Step 2: Create structure
            project_root = self.step_structure(project_name, plan)
            self._update_progress("Structure")
            
            # Step 3: Generate code
            if project_root:
                self.step_implementation(project_root, plan)
                self._update_progress("Implementation")
                
                # Step 4: Validate
                self.step_validation(project_root)
                self._update_progress("Validation")
            
            logger.info("=" * 60)
            logger.info("SUCCESS: Project generation completed")
            logger.info(f"Project location: {project_root}")
            logger.info("=" * 60)
            
            return project_root
            
        except GeneratorError as e:
            logger.error(f"Generation failed: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.warning("Generation interrupted by user")
            sys.exit(130)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='AI-powered project generator - Sıfırdan proje oluştur',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek kullanım:
  python project_generator.py --name "MyPortfolio" --description "Kişisel portfolyo sitesi" --tech "HTML, CSS, JavaScript"
  python project_generator.py --name "BlogAPI" --description "RESTful blog API" --tech "Node.js, Express, MongoDB"
        """
    )
    parser.add_argument(
        '--name', 
        required=True,
        help='Proje ismi (örn: MyWebsite)'
    )
    parser.add_argument(
        '--description',
        required=True,
        help='Proje açıklaması (örn: E-ticaret sitesi)'
    )
    parser.add_argument(
        '--tech',
        required=True,
        help='Teknoloji stack (örn: React, Node.js, PostgreSQL)'
    )
    parser.add_argument(
        '--config', 
        default='generator_config.json',
        help='Config dosyası yolu (default: generator_config.json)'
    )
    parser.add_argument(
        '--skip-planning',
        action='store_true',
        help='Planning adımını atla'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Validation adımını atla'
    )
    
    args = parser.parse_args()
    
    # Load generator
    generator = ProjectGenerator(args.config)
    
    # Override config with CLI args
    if args.skip_planning:
        generator.config['steps']['planning'] = False
    if args.skip_validation:
        generator.config['steps']['validation'] = False
    
    # Generate project
    generator.generate(args.name, args.description, args.tech)


if __name__ == "__main__":
    main()
