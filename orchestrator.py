import subprocess, json, pathlib

def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)
PROJECT_ROOT = "E:/Oguz/onegate"
goal = pathlib.Path("goal.txt").read_text()
constraints = pathlib.Path("constraints.txt").read_text()
system = pathlib.Path("prompts/gemini_system.txt").read_text()
decider = pathlib.Path("prompts/gemini_decider.txt").read_text()
codex_prompt = pathlib.Path("prompts/codex_instruction.txt").read_text()

print("🧠 Gemini: project analysis")
analysis = run(f"""
gemini "@
{system}

Goal:
{goal}

Constraints:
{constraints}

Analyze the project.
Return a high-level refactor plan."
""")

print("👮 Semgrep: static analysis")
findings = run("semgrep --config=semgrep/semgrep.yml --json")

print("🧠 Gemini: deciding actionable tasks")
tasks = run(f"""
gemini "@
{decider}

Analysis:
{analysis}

Semgrep findings:
{findings}

Constraints:
{constraints}
"
""")

print("✍️ Codex: applying refactors")
run(f"""
codex refactor . --instruction "
{codex_prompt}

Tasks:
{tasks}
"
""")

print("✅ Final Semgrep scan")
run("semgrep --config=semgrep/semgrep.yml")

print("🎉 Done.")
