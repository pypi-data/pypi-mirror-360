# Proust Framework

*"In reality, every reader is, while reading, the reader of his own self."* — Marcel Proust

An AI memory and context management framework for software development, inspired by Marcel Proust's revolutionary exploration of memory, time, and narrative coherence.

## What is Proust?

Proust transforms AI-assisted development from scattered interactions into coherent narrative experiences. Like its namesake's *In Search of Lost Time*, the framework helps AI assistants maintain deep contextual memory, creating development experiences where every action builds on accumulated understanding.

**The Trinity:** **Claude + Simone + Proust** work together as an integrated development experience where Claude provides the AI intelligence, [Simone](https://github.com/Helmi/claude-simone) structures the project management workflow, and Proust maintains the persistent memory and context that connects everything across time.

### Personas

#### Proust — The Memory & Context Archivist
Keeps long-term knowledge, cross-project recall, and narrative coherence. Named after Marcel Proust, whose literary exploration of involuntary memory revolutionized our understanding of time and consciousness. Proust the AI persona maintains contextual awareness across sessions, ensuring every development decision fits into the larger story.

## Installation

Install the Proust Framework using pip or uv:

```bash
# Using uv (recommended)
uv tool install proust-framework
proust install

# Using pip
pip install proust-framework
proust install

# Or run without installing
uv run --with proust-framework proust install
```

## Quick Start

1. **Install Framework**: Use `uv tool install proust-framework`
2. **Customize Templates**: Follow the customization steps below
3. **Start Using**: Initialize your first project

## Customization

### Step 1: Replace Template Placeholders

All templates use this placeholder format:
```
{{PLACEHOLDER_NAME}}
```

**Examples:**
- `{{PROJECT_NAME}}` → Replace with your actual project name
- `{{YYYY-MM-DD}}` → Replace with current date in ISO format
- `{{COMPANY_NAME}}` → Replace with your organization name

### Step 2: Key Files to Customize

Work through templates in this order:

**1. Project Identity**
- `.proust/ethos.md` - Mission, vision, principles
- `.proust/manifesto/manifesto.yml` - Technical architecture

**2. Configuration Files**
- `.proust/universal_claude.md` - Claude Code settings
- `.proust/guardrails.yml` - AI coding standards
- `.proust/brand.yml` - Design system

**3. Project Structure**
- `.simone/00_PROJECT_MANIFEST.md` - Project status
- Templates in `.simone/99_TEMPLATES/`

### Step 3: Use Examples for Reference

Check `.examples/` directory for:
- Complete framework configurations
- All placeholders filled with example content
- Production-ready memory patterns

### Step 4: Remove Template Instructions

After customization:
- Delete instruction blocks at top of files
- Remove lines starting with "# HOW TO USE THIS TEMPLATE"
- Clean up any remaining `{{PLACEHOLDER}}` references

## Core Philosophy

### Memory as Foundation
Context persists across sessions and projects, creating continuity where traditional development tools create fragmentation.

### Narrative Coherence
Every change fits into the larger story, ensuring development decisions build on accumulated understanding rather than starting fresh each time.

### Time and Reflection
Past decisions inform present actions through structured memory patterns, creating deeper, more thoughtful development.

### Deep Context
Surface details reveal deeper patterns through persistent contextual awareness.

## Framework Structure

### `.proust/` - AI Memory System
- **Memory Configuration** - How AI assistants remember and recall context
- **Behavioral Patterns** - Consistent AI behavior across sessions
- **Identity Preservation** - Brand and voice consistency over time
- **Knowledge Architecture** - Structured information organization

### `.simone/` - Project Management System
Built on the Simone project management framework by [Helmi](https://github.com/Helmi/claude-simone):
- **Milestones** - Major project phases (M01, M02...)
- **Sprints** - Focused work periods within milestones (S01, S02...)
- **Tasks** - Atomic units of work (T01, T02...)
- **Documentation** - Requirements, architecture, and decisions
- **Templates** - Standardized formats for consistency

**Directory Structure:**
```
src/
├── .proust/                 # Memory Archive
│   ├── ethos.md            # Project identity
│   ├── universal_claude.md # AI protocols
│   ├── guardrails.yml      # Quality standards
│   ├── brand.yml           # Design system
│   └── commands/simone/    # Structured workflows
└── .simone/                # Project Structure
    ├── 00_PROJECT_MANIFEST.md
    ├── 01_PROJECT_DOCS/
    ├── 02_REQUIREMENTS/
    ├── 03_SPRINTS/
    ├── 04_GENERAL_TASKS/
    └── 99_TEMPLATES/
```

## Key Features

- 🧠 **Persistent AI Memory** - Context survives session boundaries
- 📖 **Narrative Development** - Projects as evolving stories
- 🔍 **Memory Quality Assurance** - Continuous narrative validation
- 📚 **Rich Context Patterns** - Deep contextual understanding
- ⚡ **Instant Memory Recall** - AI assistants remember everything
- 🎯 **Coherent Decision Making** - Every choice fits the larger narrative

## Usage

### Initialize New Project
1. Install the framework using installation method above
2. Customize core files (`ethos.md`, `guardrails.yml`, `brand.yml`)
3. Create your first project manifest in `.simone/00_PROJECT_MANIFEST.md`
4. Start using commands for structured workflows

### Daily Development
- Use commands from `.proust/commands/simone/` for structured workflows
- Maintain project context through the `.simone/` structure
- Let AI assistants access rich context for better development

### Quality Assurance
- Regular project reviews maintain narrative coherence
- Built-in validation ensures framework integrity
- Memory patterns persist across team members and sessions

## Advanced Documentation

- **[Command Reference](docs/command-execution.md)** - Complete command guide and execution model
- **[Status Values](docs/status-values.md)** - Task and project status definitions
- **[Claude Integration](docs/claude-integration.md)** - Claude Code slash commands mapping
- **[Framework Auditing](docs/audit-super-prompt.md)** - Validation and integrity checking

## Use Cases

### Individual Developers
- Maintain project context across work sessions
- Build consistent coding patterns and practices
- Create coherent project narratives
- Develop personal AI assistant memory

### Development Teams
- Share collective project memory
- Maintain consistent team practices
- Build institutional knowledge
- Create team-specific AI behavioral patterns

### AI Assistant Integration
- Configure Claude Code with persistent memory
- Establish consistent AI behavior patterns
- Create project-specific AI capabilities
- Build contextual AI workflows

## Philosophy in Practice

> *"We don't receive wisdom; we must discover it for ourselves after a journey that no one can take for us or spare us."* - Marcel Proust

The Proust Framework applies this wisdom to software development:

- **Discovery over Repetition** - Each project builds understanding
- **Journey over Destination** - Process creates lasting value
- **Memory over Information** - Context becomes knowledge
- **Narrative over Tasks** - Stories create meaning

## Contributing

The Proust Framework evolves through community memory and narrative. Contributions should:

1. **Honor the philosophy** - Maintain memory and narrative focus
2. **Build on existing patterns** - Extend rather than replace
3. **Document thoroughly** - Add to the collective memory
4. **Test comprehensively** - Ensure narrative coherence

## License

MIT License - Build your own memories and narratives.

Includes portions of the Simone project management framework by [Helmi](https://github.com/Helmi/claude-simone). See [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for full attribution.

---

**Version:** 0.3.2
**Inspired by:** Marcel Proust's *In Search of Lost Time*
**Built for:** AI-assisted development with persistent memory
**Repository:** https://github.com/renkasiyas/proust.git
**Package:** https://pypi.org/project/proust-framework/

*In memory of Marcel Proust (1871-1922), whose exploration of involuntary memory showed us that the past is never truly lost, only waiting to be rediscovered.*

_(Of course this was made with 🤖 Claude's help)_