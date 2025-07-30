#!/usr/bin/env python3
"""
WarpClaude - Universal BDD Project Generator for Claude Code
Automatically sets up Claude Code environment and manages BDD development lifecycle
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
import platform
import time

# Try to import optional packages
try:
    import questionary
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Embedded command content
BDDINIT_CONTENT = '''**BDD INITIALIZATION COMMAND**

Initialize a BDD-driven project with domain models, state diagrams, and minimal feature files.

**ARGUMENTS PARSING:**
Parse the following arguments from "$ARGUMENTS":
1. `tech_stack` - Technology stack (e.g., python-django, node-express, ruby-rails)
2. `source_folder` - Target directory for the project
3. `app_goal` - One sentence describing the app's purpose

**PHASE 1: ENVIRONMENT SETUP**

First, ensure the project structure exists:
- Create the source_folder if it doesn't exist
- Create features/ directory
- Create features/steps/ directory
- Create docs/ directory for documentation
- Create pseudocode/ directory for architecture planning

Based on tech_stack, set up the appropriate BDD framework:

**Python Stack:**
- Check if behave is installed: `pip show behave`
- For Django projects: Install behave-django
- For Flask/FastAPI: Install behave
- Create features/environment.py with basic configuration

**Node.js Stack:**
- Check if cucumber is installed: `npm list cucumber`
- Install @cucumber/cucumber if needed
- Create cucumber.js configuration file

**Ruby Stack:**
- Check if cucumber is installed: `gem list cucumber`
- Install cucumber gem if needed
- Create cucumber.yml configuration

**PHASE 2: GOAL ANALYSIS & APP NAMING**

Analyze the app_goal to extract:
- Core domain entities
- Primary user actions
- Key business processes
- Success criteria

Generate an appropriate app name:
- Extract key concepts from the goal
- Create a memorable, descriptive name
- Ensure it's suitable for the domain

**PHASE 3: DOMAIN-DRIVEN DESIGN DOCUMENT**

Create `docs/ddd.md` with minimal, essential domain model:

```markdown
# Domain Model - [App Name]

## Bounded Context
[Single bounded context for this simple app]

## Aggregates
[List only essential aggregates - usually 1-3 for simple apps]

### [Aggregate Name]
- **Root Entity**: [Entity name]
- **Value Objects**: [List if any, keep minimal]
- **Business Rules**: [Core invariants only]

## Domain Events
[List 2-4 critical events that drive the system]

## Ubiquitous Language
[5-10 key terms max, with clear definitions]
```

Focus on:
- Only entities that directly serve the app goal
- Remove any "nice-to-have" concepts
- Keep relationships simple
- No technical implementation details

**PHASE 4: STATE DIAGRAM GENERATION**

Create `docs/state-diagram.md` with Mermaid stateDiagram:

```markdown
# State Flow - [App Name]

## Business State Diagram

\```mermaid
stateDiagram-v2
    [*] --> Initial
    Initial --> [Core State 1]
    [Core State 1] --> [Core State 2]: [Action]
    [Core State 2] --> [End State]: [Completion]
    [End State] --> [*]
\```

## State Definitions
- **Initial**: [What triggers the process]
- **[Core States]**: [What happens in each state]
- **[End State]**: [Success condition]

## Transitions
[List each transition with business rules]
```

Rules for state diagram:
- Maximum 5-7 states total
- Only happy path transitions
- No error states unless critical
- Clear start and end

**PHASE 5: MISSION DOCUMENT**

Create `docs/mission.md`:

```markdown
# Mission - [App Name]

## Vision
[Elaborate the one-sentence goal into 2-3 paragraphs]

## Success Criteria
1. [Specific, measurable outcome 1]
2. [Specific, measurable outcome 2]
3. [Specific, measurable outcome 3]

## In Scope
- [Core feature 1]
- [Core feature 2]
- [Core feature 3]

## Out of Scope
- [Explicitly excluded feature 1]
- [Explicitly excluded feature 2]
- [Future enhancement 1]

## App Name Rationale
**Chosen Name**: [App Name]
**Reasoning**: [Why this name fits the mission]
```

**PHASE 6: MINIMAL FEATURE FILES**

Create ultra-minimal feature files - first pass:

1. Identify all possible features
2. Reduce to happy paths only
3. Further reduce to critical path only

Final features should be:
- One core workflow feature
- Optional: One setup feature (only if required)
- Maximum 3-5 scenarios total across all features

Example `features/core_workflow.feature`:
```gherkin
Feature: [Core Workflow Name]
  As a [primary user]
  I want to [primary action]
  So that [primary value]

  Scenario: [Single Critical Path]
    Given [minimal precondition]
    When [essential action]
    Then [core success criteria]
```

**PHASE 7: 1990s PSEUDOCODE ARCHITECTURE**

Generate strict procedural pseudocode with:
- Clear BEGIN/END blocks
- Explicit variable declarations
- Simple procedural flow
- No patterns or abstractions

Structure:
```
pseudocode/
├── main_controller.pseudo
├── data_manager.pseudo
├── business_rules.pseudo
└── io_handler.pseudo
```

Example format:
```
PROGRAM MainController
BEGIN
    DECLARE userInput AS STRING
    DECLARE dataStore AS DataManager
    DECLARE result AS BOOLEAN
    
    FUNCTION ProcessRequest(input)
    BEGIN
        VALIDATE input
        IF input IS VALID THEN
            result = dataStore.Save(input)
            RETURN result
        ELSE
            RETURN FALSE
        END IF
    END
    
    // Main execution
    userInput = GetUserInput()
    result = ProcessRequest(userInput)
    DisplayResult(result)
END
```

**PHASE 8: ARCHITECTURE REVIEW & SIMPLIFICATION**

Review all pseudocode and ask:
1. Can any two modules be combined?
2. Is there any unnecessary indirection?
3. Could this be done with fewer files?
4. Would a beginner understand this immediately?

Simplify until the answer to #4 is absolutely YES.

**PHASE 9: SUMMARY GENERATION**

Create `summary.md`:

```markdown
# BDD Project Initialized - [App Name]

## Generated Structure
- ✅ BDD framework configured ([behave/cucumber])
- ✅ Domain model defined (docs/ddd.md)
- ✅ State flow mapped (docs/state-diagram.md)
- ✅ Mission clarified (docs/mission.md)
- ✅ Features created ([list feature files])
- ✅ Architecture planned ([list pseudocode files])

## Quick Start
1. Review the generated documents in docs/
2. Examine the features/ directory
3. Check pseudocode/ for the planned architecture

## Next Steps
Run the bddloop command to:
- Generate step definitions
- Implement the pseudocode as real code
- Make all tests pass

## Configuration
- Tech Stack: [chosen stack]
- BDD Framework: [behave/cucumber]
- App Goal: "[original goal]"
```

**EXECUTION PRINCIPLES:**

1. **Ruthless Simplification**: Always choose the simpler option
2. **No Gold Plating**: Only what directly serves the stated goal
3. **Clear Over Clever**: 1990s clarity beats modern patterns
4. **Test-First Thinking**: Everything prepared for BDD implementation
5. **Single Responsibility**: Each component does ONE thing

Begin by parsing arguments and systematically work through each phase, constantly asking "Can this be simpler?"'''

BDDWARP_CONTENT = '''**BDD WARP COMMAND**

Execute a BDD-driven development loop that continuously runs tests, implements code, and verifies the full application stack.

**ARGUMENTS PARSING:**
Parse the following arguments from "$ARGUMENTS":
1. `source_folder` - Project directory created by bddinit
2. `iterations` - Number of loops (1-N or "infinite")

**PHASE 1: INITIAL ASSESSMENT**

Navigate to source_folder and verify BDD setup:
- Check for features/ directory with .feature files
- Verify features/steps/ directory exists
- Confirm behave (or cucumber) is installed
- Read docs/mission.md, ddd.md, and state-diagram.md for context
- Examine pseudocode/ for implementation guidance

**CRITICAL: Understand the Mission**
Read mission.md and identify:
- What is the ONE main purpose of this app?
- What is the critical path to achieve that purpose?
- Is this a web app (needs browser) or CLI app (needs menu)?
- What would make the user say "this works!"?

Run initial BDD test suite:
```bash
behave --format progress3 --no-capture
```

Capture and analyze:
- Which steps are undefined
- Which steps fail
- Overall test structure

**FAIL-FIRST PRINCIPLE:**
Remember: We WANT tests to fail initially. This is TDD:
- No mocks or stubs
- No "pass" statements
- Love exceptions and errors
- Each failure guides implementation

**PHASE 2: IMPLEMENTATION LOOP**

For iteration = 1 to iterations (or infinite):

**Step 1: Run Tests & Capture State**
```bash
behave --format progress3 --no-capture > test_output.txt
```
Parse output to identify:
- Undefined steps needing implementation
- Failing steps needing code
- Passing steps (victory markers)

**Step 2: Generate Step Definitions**
Deploy Sub Agent for undefined steps:
```
TASK: Generate step definitions for BDD tests

CONTEXT:
- Feature file: [content]
- Undefined steps: [list]
- Tech stack: [from bddinit]

REQUIREMENTS:
1. Create step definition files in features/steps/
2. Each step should RAISE NotImplementedError
3. Include proper behave decorators
4. Match step text exactly
5. Add TODO comments for implementation

DELIVERABLE: Step definition files that fail correctly
```

**Step 3: Implement Domain/Model Layer**
Deploy Sub Agent for data layer:
```
TASK: Implement database models and domain logic

CONTEXT:
- Domain model: [from ddd.md]
- Pseudocode: [from pseudocode/]
- Tech stack: [framework specific]

REQUIREMENTS:
1. Create database models/tables
2. Run migrations if needed (Django: migrate, etc)
3. Implement domain logic from DDD
4. Create test data fixtures
5. Verify database connectivity

DELIVERABLE: Working data layer with test data
```

**Step 4: Implement API Layer**
Deploy Sub Agent for API:
```
TASK: Implement API endpoints

CONTEXT:
- Pseudocode: [main_controller.pseudo]
- Routes needed: [from features]
- Models: [from previous step]

REQUIREMENTS:
1. Create all API endpoints
2. Connect to real database
3. Implement business logic
4. Generate API documentation
5. Test each endpoint manually

DELIVERABLE: Working API with documentation
```

**Step 5: Connect Frontend**
Deploy Sub Agent for UI:
```
TASK: Wire frontend to API

CONTEXT:
- Pseudocode: [web_interface.pseudo]
- API endpoints: [from previous step]
- UI framework: [JavaScript/etc]

REQUIREMENTS:
1. Replace any hardcoded data with API calls
2. Implement real fetch/ajax requests
3. Handle loading states
4. Display real data from backend
5. Ensure error handling

DELIVERABLE: Frontend connected to live API
```

**Step 6: Create User Entry Point**
Deploy Sub Agent for user experience:
```
TASK: Create single-file entry point for users

CONTEXT:
- Mission goal: [from mission.md]
- App type: [web or CLI]
- Tech stack: [from setup]

REQUIREMENTS FOR WEB APPS:
1. Create play.py (or start.py) that:
   - Finds available ports automatically
   - Starts backend API server
   - Serves frontend (if separate)
   - Opens browser to the GAME/APP (not API docs!)
   - Shows "Starting [App Name]..." message
2. Handle Ctrl+C gracefully to stop all services

REQUIREMENTS FOR CLI APPS:
1. Create menu.py using Rich/Textual/Blessed that:
   - Shows beautiful welcome screen
   - Provides numbered menu options
   - Has "1. Quick Start" as first option (no params)
   - Includes help and exit options
   - Uses colors and boxes for visual appeal
2. Make the critical path obvious and immediate

DELIVERABLE: One file that starts everything
```

**Step 7: Integration Testing**
Run full stack test:
```bash
# Use the new entry point
python play.py &  # or menu.py for CLI
APP_PID=$!

# Wait for startup
sleep 3

# Run integration tests
behave --tags=@integration

# Kill app
kill $APP_PID
```

**Step 8: Reality Checks**
Deploy Sub Agent for verification:
```
TASK: Perform user-focused reality verification

REQUIREMENTS:
1. Run the entry point file (play.py/menu.py)
2. Verify it opens to the MAIN PURPOSE immediately
3. For web: Ensure browser opens to game/app (NOT api docs)
4. For CLI: Ensure menu is beautiful and clear
5. Test the critical path as a real user would
6. Verify NO technical barriers between user and goal
7. Check that mission.md goal is achievable in <3 clicks/actions

DELIVERABLE: Reality check report proving user success
```

Deploy Screenshot Sub Agent:
```
TASK: Capture screenshots of running application

CONTEXT:
- App type: [web or CLI]
- Entry point: [play.py or menu.py]

REQUIREMENTS:
1. Create screenshots/ directory
2. For web apps:
   - Use selenium/playwright headless browser
   - Capture: landing page, main interaction, success state
3. For CLI apps:
   - Capture terminal output as images using available tools
   - Alternative: Save text output to screenshots/cli_output.txt
4. Name files descriptively: 01_landing.png, 02_game_in_progress.png, etc.
5. Include a screenshots/README.md explaining what each image shows

DELIVERABLE: screenshots/ folder with captured images and documentation
```

**Step 9: Test Data Verification**
Create and test with realistic data:
- Generate test_data.json with realistic examples
- Create unit tests for data transformations
- Verify edge cases in data flow
- Test validation at each layer

**Step 10: Documentation & README**
Create user-friendly README.md:
```markdown
# [App Name]

[One sentence description from mission.md]

## Quick Start

```bash
python play.py
```

That's it! The game/app will start automatically.

## What This Does
[2-3 sentences about the main purpose]

## Requirements
- Python 3.x
- [Any other requirements]
```

Verify documentation:
- README focuses on USER not developer
- First command is the entry point
- No complex setup instructions
- API docs exist but are secondary

**PHASE 3: LOGGING & EVOLUTION**

**Update droid_log.md:**
```markdown
# Droid Log - Iteration [N]

## Patterns Observed
- [Pattern]: [Description]
- [Challenge]: [How resolved]

## Wild Successes
- [Success]: [What worked well]

## Common Issues
- [Issue]: [Root cause and fix]

## Screenshot Status
- Screenshots captured: [Yes/No]
- Location: screenshots/
- Issues encountered: [Any screenshot setup problems]
```

**Update prompt_evolution.md:**
```markdown
# Prompt Evolution - Iteration [N]

## Improvements for Next Time
- Instead of: "[current approach]"
- Try: "[better approach]"

## Effective Patterns
- "[pattern]" works well for [situation]

## Self-Notes
- [Advice for next iteration]
```

**Step 11: Apply Self-Improvements**
Read prompt_evolution.md and immediately apply suggestions:
- Adjust prompts based on learnings
- Modify approach based on patterns
- Implement suggested improvements
- Focus on user experience improvements

**PHASE 4: LOOP CONTROL**

After each iteration:
1. Check if all tests are passing
2. If yes and iterations != infinite: Complete
3. If no and iterations remaining: Continue
4. If infinite: Continue until context limits

**Progress Tracking:**
```
Iteration [N] of [Total]
- Tests Passing: X/Y
- Coverage: Z%
- Integration: [Status]
```

**PHASE 5: FINAL VERIFICATION**

When all tests pass:
1. Run full test suite one final time
2. Start application and verify manually
3. Document any remaining issues
4. Create summary report

**SUCCESS CRITERIA:**
- All behave tests passing
- Single entry point (play.py/menu.py) works perfectly
- User reaches main goal in <3 actions
- For web: Browser opens to game/app directly
- For CLI: Beautiful menu with quick start
- No technical barriers for users
- README has one simple command to start
- Mission.md goal is immediately achievable

**EXECUTION PRINCIPLES:**

1. **Test-Driven**: Let failing tests drive development
2. **Real Implementation**: No mocks, actual code
3. **Full Stack**: Verify every layer
4. **Continuous Feedback**: Behave is the truth
5. **Self-Improving**: Learn and adapt each iteration
6. **Reality-Based**: Screenshots and manual verification
7. **Data-Centric**: Test actual data flow
8. **Documentation-Aware**: Keep all docs in sync
9. **USER-FIRST**: Always think "How does the user start this?"
10. **CRITICAL PATH**: Focus on mission.md goal above all else

Begin with initial test run and proceed through iterations until success!'''

def print_console(message, style=""):
    """Print with rich console if available, otherwise plain print"""
    if console and RICH_AVAILABLE:
        console.print(message, style=style)
    else:
        print(message)

def print_panel(title, content):
    """Print a panel with rich if available"""
    if console and RICH_AVAILABLE:
        console.print(Panel(content, title=title))
    else:
        print(f"\n=== {title} ===")
        print(content)
        print("=" * (len(title) + 8))

def check_command(command):
    """Check if a command exists and return version or status"""
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip() or "Installed"
        return None
    except FileNotFoundError:
        return None

def check_python_package(package):
    """Check if a Python package is installed"""
    try:
        __import__(package)
        return "Installed"
    except ImportError:
        return None

def get_shell_config():
    """Get appropriate shell config file"""
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        if (home / ".zshrc").exists():
            return home / ".zshrc"
        return home / ".bash_profile"
    elif system == "Linux":
        return home / ".bashrc"
    elif system == "Windows":
        return None
    
def install_nvm_and_node():
    """Install nvm and Node.js"""
    if platform.system() == "Windows":
        print_console("⚠️  Windows detected. Please install Node.js from nodejs.org", style="yellow")
        print_console("Then install Claude Code with: npm install -g @anthropic-ai/claude-code")
        return False
    
    print_console("📦 Installing nvm (Node Version Manager)...")
    
    # Install nvm
    nvm_install_cmd = 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash'
    result = subprocess.run(nvm_install_cmd, shell=True)
    
    if result.returncode != 0:
        print_console("❌ Failed to install nvm", style="red")
        return False
    
    # Source nvm
    shell_config = get_shell_config()
    if shell_config:
        subprocess.run(f'source {shell_config}', shell=True)
    
    # Install node using nvm
    print_console("📦 Installing Node.js...")
    # We need to run this in a new shell that has nvm loaded
    install_node_cmd = f'source {shell_config} && nvm install node'
    result = subprocess.run(install_node_cmd, shell=True, executable='/bin/bash')
    
    if result.returncode == 0:
        print_console("✅ Node.js installed successfully", style="green")
        return True
    else:
        print_console("❌ Failed to install Node.js", style="red")
        return False

def check_and_install_claude():
    """Ensure Claude Code is installed and working"""
    print_console("🔍 Checking Claude Code installation...")
    
    # Check if claude is installed
    result = subprocess.run(["claude", "doctor"], capture_output=True)
    if result.returncode == 0:
        print_console("✅ Claude Code is installed", style="green")
        return True
    
    print_console("❌ Claude Code not found. Installing...", style="yellow")
    
    # Check if npm exists
    npm_check = subprocess.run(["npm", "--version"], capture_output=True)
    if npm_check.returncode != 0:
        print_console("❌ npm not found. Installing Node.js...", style="yellow")
        if not install_nvm_and_node():
            return False
        # After installing node, we need to reload the shell environment
        print_console("⚠️  Please run this script again in a new terminal to continue", style="yellow")
        sys.exit(0)
    
    # Install Claude Code
    print_console("📦 Installing Claude Code...")
    result = subprocess.run(["npm", "install", "-g", "@anthropic-ai/claude-code"])
    
    if result.returncode == 0:
        # Verify installation
        verify = subprocess.run(["claude", "doctor"], capture_output=True)
        if verify.returncode == 0:
            print_console("✅ Claude Code installed successfully!", style="green")
            return True
    
    print_console("❌ Failed to install Claude Code", style="red")
    print_console("Please install manually: npm install -g @anthropic-ai/claude-code")
    return False

def setup_context7():
    """Install and configure Context7 MCP server"""
    print_console("🔧 Setting up Context7 MCP...", style="cyan")
    
    # Add Context7 MCP
    result = subprocess.run([
        "claude", "mcp", "add", "context7", 
        "--", "npx", "-y", "@upstash/context7-mcp@latest"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print_console("✅ Context7 MCP configured", style="green")
        return True
    else:
        print_console("⚠️  Could not configure Context7 MCP", style="yellow")
        print_console(f"Error: {result.stderr}")
        return False

def setup_claude_environment():
    """Creates .claude directory structure if not exists"""
    claude_dir = Path(".claude")
    commands_dir = claude_dir / "commands"
    
    # Create directories
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Write bddinit.md
    (commands_dir / "bddinit.md").write_text(BDDINIT_CONTENT)
    
    # Write bddwarp.md
    (commands_dir / "bddwarp.md").write_text(BDDWARP_CONTENT)
    
    # Write settings.json
    settings = {
        "commands": {
            "enabled": True,
            "directories": ["~/.claude/commands", ".claude/commands"]
        }
    }
    (claude_dir / "settings.json").write_text(json.dumps(settings, indent=2))
    
    print_console("✅ Claude environment created (.claude/commands/)", style="green")

def detect_bdd_project():
    """Returns True if features/ folder exists AND contains .feature files"""
    features_dir = Path("features")
    if features_dir.exists() and features_dir.is_dir():
        feature_files = list(features_dir.glob("*.feature"))
        return len(feature_files) > 0
    return False

def find_entry_points():
    """Find play.py, menu.py, start.py, run.py in current directory"""
    patterns = ["play.py", "menu.py", "start.py", "run.py"]
    found = []
    for pattern in patterns:
        if Path(pattern).exists():
            found.append(pattern)
    return found

def find_latest_app_directory():
    """Find the most recently created directory with features/ inside"""
    dirs_with_features = []
    for item in Path(".").iterdir():
        if item.is_dir() and (item / "features").exists():
            dirs_with_features.append(item)
    
    if dirs_with_features:
        # Return the most recently modified
        return max(dirs_with_features, key=lambda d: d.stat().st_mtime).name
    return "."

def run_bddinit():
    """Run bddinit - it will prompt for tech stack, app dir, and goal"""
    print_console("🚀 Starting BDD initialization...", style="cyan")
    # bddinit handles all the prompting internally
    subprocess.run(["claude", "/project:bddinit"])

def run_bddwarp(app_dir, iterations):
    """Run bddwarp with specified directory and iterations"""
    print_console(f"🔄 Starting BDD development ({iterations} iterations)...", style="cyan")
    subprocess.run(["claude", "/project:bddwarp", app_dir, str(iterations)])

def simple_input(prompt):
    """Simple input function when questionary not available"""
    return input(f"{prompt}: ")

def simple_select(prompt, choices):
    """Simple selection when questionary not available"""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    while True:
        try:
            selection = int(input("Choose (number): "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
        except ValueError:
            pass
        print("Invalid choice. Please enter a number.")

def get_input(prompt, default=None):
    """Get input with fallback for missing questionary"""
    if QUESTIONARY_AVAILABLE:
        return questionary.text(prompt, default=default).ask()
    else:
        result = simple_input(prompt)
        return result if result else default

def get_select(prompt, choices):
    """Get selection with fallback for missing questionary"""
    if QUESTIONARY_AVAILABLE:
        return questionary.select(prompt, choices=choices).ask()
    else:
        return simple_select(prompt, choices)

def handle_quick_start():
    """Option 1: Quick start - auto init + warp"""
    if detect_bdd_project():
        print_console("✓ BDD project detected. Continuing development...", style="green")
        run_bddwarp(".", 100)
    else:
        print_console("No BDD project found. Starting initialization...", style="yellow")
        run_bddinit()
        # After bddinit completes, find the created directory
        time.sleep(1)  # Give filesystem time to update
        app_dir = find_latest_app_directory()
        if app_dir != ".":
            print_console(f"📁 Found project directory: {app_dir}", style="cyan")
        run_bddwarp(app_dir, 100)

def handle_initialize():
    """Option 2: Initialize new project"""
    run_bddinit()

def handle_continue():
    """Option 3: Continue existing project"""
    if detect_bdd_project():
        iterations = get_input("Iterations (default 100)", "100")
        try:
            iterations = int(iterations)
        except ValueError:
            iterations = 100
        run_bddwarp(".", iterations)
    else:
        print_console("❌ No BDD project found. Run option 2 first.", style="red")

def handle_run_project():
    """Option 4: Run finished project"""
    entry_points = find_entry_points()
    if entry_points:
        if len(entry_points) == 1:
            selected = entry_points[0]
        else:
            selected = get_select("Run which file?", entry_points)
        print_console(f"🎮 Starting {selected}...", style="cyan")
        subprocess.run(["python", selected])
    else:
        print_console("❌ No entry point (play.py/menu.py) found.", style="red")

def handle_setup_only():
    """Option 5: Setup Claude environment only"""
    setup_claude_environment()
    print_console("✅ Claude environment setup complete", style="green")

def create_sdk_example():
    """Option 6: Create SDK example"""
    sdk_example = '''#!/usr/bin/env python3
"""Example of using Claude Code SDK with Context7"""

from claude_code_sdk import ClaudeClient, ClaudeOptions

# Configure with Context7 MCP
options = ClaudeOptions(
    mcp_config="mcp-servers.json",
    allowed_tools=["mcp__context7"]
)

# Create client
client = ClaudeClient(options=options)

# Example: Use Context7 for memory
project_goal = "Your project goal here"
tech_stack = "Your tech stack here"

response = client.prompt(f"""
    Remember this project is about: {project_goal}
    Tech stack: {tech_stack}
""")

print(response)
'''
    
    with open("claude_sdk_example.py", "w") as f:
        f.write(sdk_example)
    print_console("📝 Created claude_sdk_example.py for SDK usage", style="green")

def check_installation_status():
    """Option 7: Check installation status"""
    print_panel("Installation Status", "Checking all components...")
    
    # Check each component
    checks = {
        "Node.js": check_command(["node", "--version"]),
        "npm": check_command(["npm", "--version"]),
        "Claude Code": check_command(["claude", "--version"]),
        "Python": check_command(["python", "--version"]),
    }
    
    # Add optional package checks
    if QUESTIONARY_AVAILABLE:
        checks["Questionary"] = "Installed"
    else:
        checks["Questionary"] = "Not installed (using fallback)"
    
    if RICH_AVAILABLE:
        checks["Rich"] = "Installed"
    else:
        checks["Rich"] = "Not installed (using plain text)"
    
    # Display results
    all_good = True
    for component, status in checks.items():
        if status and "Not installed" not in status:
            print_console(f"✅ {component}: {status}", style="green")
        else:
            print_console(f"❌ {component}: {status or 'Not installed'}", style="red")
            all_good = False
    
    if all_good:
        print_console("\n✨ All components installed!", style="green bold")
    else:
        print_console("\n⚠️  Some components missing. Run setup to install.", style="yellow")

def show_interactive_menu():
    """Show the interactive menu"""
    print_panel("WarpClaude BDD Tool", "Complete BDD Development Environment")
    
    choices = [
        "1. Quick Start (Auto Init + Warp)",
        "2. Initialize New Project (bddinit)",
        "3. Continue Project (bddwarp)",
        "4. Run Finished Project",
        "5. Setup Claude Environment Only",
        "6. Create SDK Example",
        "7. Check Installation Status",
        "8. Exit"
    ]
    
    while True:
        choice = get_select("Choose an option:", choices)
        
        if "1." in choice:
            handle_quick_start()
            break
        elif "2." in choice:
            handle_initialize()
            break
        elif "3." in choice:
            handle_continue()
            break
        elif "4." in choice:
            handle_run_project()
            break
        elif "5." in choice:
            handle_setup_only()
        elif "6." in choice:
            create_sdk_example()
        elif "7." in choice:
            check_installation_status()
        elif "8." in choice:
            print_console("👋 Goodbye!", style="cyan")
            break

def show_help():
    """Show help information"""
    help_text = """
WarpClaude - BDD Development Tool for Claude Code

Usage:
  python warpclaude.py [OPTIONS]

Options:
  --menu        Launch interactive menu
  --help        Show this help message
  --check       Check installation status
  (no options)  Auto-setup and run based on project state

Features:
  ✓ Auto-installs Claude Code if missing
  ✓ Sets up Node.js via nvm if needed
  ✓ Configures Context7 MCP for enhanced memory
  ✓ Creates BDD project structure
  ✓ Manages full development lifecycle

Default Behavior:
  - If BDD project exists: Continues with bddwarp (100 iterations)
  - If no project: Starts bddinit (will prompt for details)

Examples:
  python warpclaude.py              # Auto-run based on project state
  python warpclaude.py --menu       # Show interactive menu
  python warpclaude.py --check      # Check installation status
"""
    print(help_text)

def main():
    """Main entry point"""
    # Handle command line arguments
    if "--help" in sys.argv:
        show_help()
        return
    
    if "--check" in sys.argv:
        check_installation_status()
        return
    
    # Step 1: Ensure Claude is installed
    if not check_and_install_claude():
        print_console("❌ Could not install Claude Code. Please install manually.", style="red")
        return
    
    # Step 2: Setup Context7 MCP (optional but recommended)
    setup_context7()
    
    # Step 3: Setup Claude environment
    setup_claude_environment()
    
    # Step 4: Handle menu or auto-run
    if "--menu" in sys.argv:
        show_interactive_menu()
    else:
        # DEFAULT: Auto-run based on project state
        if detect_bdd_project():
            print_console("✓ BDD project detected. Continuing development...", style="green")
            run_bddwarp(".", 100)
        else:
            print_console("No BDD project found. Starting initialization...", style="yellow")
            run_bddinit()

if __name__ == "__main__":
    main()