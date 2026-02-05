#!/usr/bin/env python3
"""
AI Orchestrator - Automated refactoring pipeline
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
        logging.FileHandler('orchestrator.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


class OrchestratorError(Exception):
    """Base exception for orchestrator errors"""
    pass


class Orchestrator:
    def __init__(self, config_path: str = "config.json"):
        """Initialize orchestrator with configuration"""
        self.config = self._load_config(config_path)
        self.output_dir = pathlib.Path(self.config['output_dir'])
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.steps_completed = 0
        self.total_steps = 5  # analysis, semgrep, decide, refactor, final_scan
    
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
                raise OrchestratorError(f"Config file not found: {config_path}")
            return json.loads(config_file.read_text())
        except json.JSONDecodeError as e:
            raise OrchestratorError(f"Invalid JSON in config: {e}")
    
    def _validate_files(self):
        """Validate that all required files exist"""
        files_to_check = [
            self.config['files']['goal'],
            self.config['files']['constraints'],
            self.config['prompts']['system'],
            self.config['prompts']['decider'],
            self.config['prompts']['codex'],
            self.config['semgrep']['config']
        ]
        
        missing = []
        for file_path in files_to_check:
            if not pathlib.Path(file_path).exists():
                missing.append(file_path)
        
        if missing:
            raise OrchestratorError(f"Missing files: {', '.join(missing)}")
        
        # Check if project root exists
        project_root = pathlib.Path(self.config['project_root'])
        if not project_root.exists():
            raise OrchestratorError(f"Project root not found: {project_root}")
    
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
            raise OrchestratorError(f"Failed to execute: {description}") from e
    
    def _save_output(self, filename: str, content: str):
        """Save output to file with timestamp"""
        output_path = self.output_dir / f"{self.timestamp}_{filename}"
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"Saved output to: {output_path}")
    
    def _load_file(self, key_path: str) -> str:
        """Load content from file specified in config"""
        file_path = self.config
        for key in key_path.split('.'):
            file_path = file_path[key]
        return pathlib.Path(file_path).read_text(encoding='utf-8')
    
    def step_analysis(self) -> str:
        """Step 1: Project analysis with Gemini"""
        if not self.config['steps'].get('analysis', True):
            logger.info("Skipping analysis step")
            return ""
        
        logger.info("[GEMINI] Project analysis")
        
        system = self._load_file('prompts.system')
        goal = self._load_file('files.goal')
        constraints = self._load_file('files.constraints')
        project_root = self.config['project_root']
        
        # Create temp prompt file to avoid shell escaping issues
        prompt_file = self.output_dir / f"{self.timestamp}_analysis_prompt.txt"
        prompt_content = f"""Project Root: {project_root}

{system}

Goal:
{goal}

Constraints:
{constraints}

IMPORTANT: Analyze the project at {project_root}.
Provide a detailed, actionable refactor plan.
Format your response as clear text or markdown."""
        prompt_file.write_text(prompt_content, encoding='utf-8')
        
        # Use absolute path for Windows and PowerShell Get-Content
        prompt_file_abs = str(prompt_file.absolute())
        cmd = f'cd "{project_root}" && powershell -Command "Get-Content \'{prompt_file_abs}\' | gemini -p -"'
        analysis = self._run_command(cmd, "Gemini analysis")
        self._save_output("analysis.txt", analysis)
        return analysis
    
    def step_semgrep(self) -> str:
        """Step 2: Static analysis with Semgrep"""
        if not self.config['steps'].get('semgrep', True):
            logger.info("Skipping semgrep step")
            return ""
        
        logger.info("[SEMGREP] Static analysis")
        
        semgrep_config = self.config['semgrep']['config']
        project_root = self.config['project_root']
        
        # Run semgrep on the target project
        cmd = f'cd "{project_root}" && semgrep --config="{pathlib.Path(semgrep_config).absolute()}" --json --verbose'
        
        findings = self._run_command(cmd, "Semgrep scan")
        self._save_output("semgrep_findings.json", findings)
        
        # Parse and log summary
        try:
            findings_data = json.loads(findings)
            results = findings_data.get('results', [])
            logger.info(f"Semgrep found {len(results)} issue(s)")
        except json.JSONDecodeError:
            logger.warning("Could not parse Semgrep output")
        
        return findings
    
    def step_decide(self, analysis: str, findings: str) -> str:
        """Step 3: Decide actionable tasks with Gemini"""
        if not self.config['steps'].get('decide', True):
            logger.info("Skipping decision step")
            return ""
        
        logger.info("[GEMINI] Deciding actionable tasks")
        
        decider = self._load_file('prompts.decider')
        constraints = self._load_file('files.constraints')
        project_root = self.config['project_root']
        
        # Parse semgrep findings count
        findings_count = 0
        try:
            findings_data = json.loads(findings)
            findings_count = len(findings_data.get('results', []))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        # Create temp prompt file
        prompt_file = self.output_dir / f"{self.timestamp}_decide_prompt.txt"
        prompt_content = f"""{decider}

Project Root: {project_root}

Analysis:
{analysis}

Semgrep findings ({findings_count} issues):
{findings}

Constraints:
{constraints}

IMPORTANT: Output ONLY a valid JSON array of tasks.
Each task must have: file (path), reason (string), description (string)
Example: [{{"file": "src/main.py", "reason": "Too complex", "description": "Split into smaller functions"}}]
If no tasks, return: []"""
        prompt_file.write_text(prompt_content, encoding='utf-8')
        
        # Use absolute path for Windows and PowerShell
        prompt_file_abs = str(prompt_file.absolute())
        cmd = f'cd "{project_root}" && powershell -Command "Get-Content \'{prompt_file_abs}\' | gemini -p -"'
        tasks = self._run_command(cmd, "Gemini decision")
        self._save_output("tasks.json", tasks)
        
        # Validate JSON output
        try:
            tasks_data = json.loads(tasks)
            logger.info(f"Generated {len(tasks_data)} task(s)")
        except json.JSONDecodeError:
            logger.warning("Tasks output is not valid JSON, attempting to extract...")
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', tasks)
            if json_match:
                tasks = json_match.group(1).strip()
                self._save_output("tasks_extracted.json", tasks)
        
        return tasks
    
    def step_refactor(self, tasks: str):
        """Step 4: Apply refactors with Codex"""
        if not self.config['steps'].get('refactor', True):
            logger.info("Skipping refactor step")
            return
        
        logger.info("[CODEX] Applying refactors")
        
        # Validate tasks first
        try:
            tasks_data = json.loads(tasks)
            if not tasks_data or len(tasks_data) == 0:
                logger.info("No tasks to refactor, skipping Codex step")
                return
            logger.info(f"Applying {len(tasks_data)} refactoring task(s)")
        except json.JSONDecodeError:
            logger.warning("Tasks are not valid JSON, attempting refactor anyway...")
        
        codex_prompt = self._load_file('prompts.codex')
        project_root = self.config['project_root']
        
        # Create temp prompt file
        prompt_file = self.output_dir / f"{self.timestamp}_refactor_prompt.txt"
        prompt_content = f"""{codex_prompt}

Project Root: {project_root}

Tasks to implement:
{tasks}

IMPORTANT: Apply these refactorings to the codebase.
Work in the directory: {project_root}"""
        prompt_file.write_text(prompt_content, encoding='utf-8')
        
        # Use absolute path for Windows and PowerShell
        prompt_file_abs = str(prompt_file.absolute())
        cmd = f'cd "{project_root}" && powershell -Command "Get-Content \'{prompt_file_abs}\' | codex exec --dangerously-bypass-approvals-and-sandbox"'
        
        try:
            result = self._run_command(cmd, "Codex refactoring")
            self._save_output("codex_result.txt", result)
        except OrchestratorError as e:
            logger.error(f"Codex refactoring failed, but continuing...")
            logger.error(str(e))
    
    def step_final_scan(self):
        """Step 5: Final Semgrep scan"""
        if not self.config['steps'].get('final_scan', True):
            logger.info("Skipping final scan")
            return
        
        logger.info("[SEMGREP] Final scan")
        
        semgrep_config = self.config['semgrep']['config']
        project_root = self.config['project_root']
        
        cmd = f'cd "{project_root}" && semgrep --config="{pathlib.Path(semgrep_config).absolute()}" --json'
        
        try:
            result = self._run_command(cmd, "Final Semgrep scan")
            self._save_output("final_scan.txt", result)
            
            # Compare with initial scan
            try:
                final_data = json.loads(result)
                final_count = len(final_data.get('results', []))
                logger.info(f"Final scan: {final_count} issue(s) remaining")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        except OrchestratorError:
            logger.warning("Final scan found issues or failed")
    
    def run(self):
        """Run the complete orchestration pipeline"""
        try:
            logger.info("=" * 50)
            logger.info("Starting AI Orchestrator")
            logger.info("=" * 50)
            
            # Validate setup
            self._validate_files()
            
            # Run pipeline with progress tracking
            analysis = self.step_analysis()
            self._update_progress("Analysis")
            
            findings = self.step_semgrep()
            self._update_progress("Semgrep")
            
            tasks = self.step_decide(analysis, findings)
            self._update_progress("Decision")
            
            self.step_refactor(tasks)
            self._update_progress("Refactor")
            
            self.step_final_scan()
            self._update_progress("Final Scan")
            
            logger.info("=" * 50)
            logger.info("SUCCESS: Orchestration completed")
            logger.info(f"Results saved in: {self.output_dir}")
            logger.info("=" * 50)
            
        except OrchestratorError as e:
            logger.error(f"Orchestration failed: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.warning("Orchestration interrupted by user")
            sys.exit(130)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='AI-powered refactoring orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--config', 
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='Skip Gemini analysis step'
    )
    parser.add_argument(
        '--skip-semgrep',
        action='store_true',
        help='Skip Semgrep static analysis'
    )
    parser.add_argument(
        '--skip-refactor',
        action='store_true',
        help='Skip Codex refactoring (dry run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run analysis only, skip refactoring'
    )
    
    args = parser.parse_args()
    
    # Load orchestrator
    orchestrator = Orchestrator(args.config)
    
    # Override config with CLI args
    if args.skip_analysis:
        orchestrator.config['steps']['analysis'] = False
    if args.skip_semgrep:
        orchestrator.config['steps']['semgrep'] = False
        orchestrator.config['steps']['final_scan'] = False
    if args.skip_refactor or args.dry_run:
        orchestrator.config['steps']['refactor'] = False
        orchestrator.config['steps']['final_scan'] = False
    
    # Run
    orchestrator.run()


if __name__ == "__main__":
    main()
