# Changelog

All notable changes to the .coder project.

---

## [2.1.0] - 2026-05-04

### Added - NVIDIA API Integration

#### New Default Model
- **z-ai/glm4.7** from NVIDIA is now the default model
- Free to use with reasoning capabilities
- 16K context window
- OpenAI-compatible API

#### New Features
- **Dual API Support**: Both NVIDIA and Gemini APIs supported
- **Reasoning Display**: Shows model's thinking process in dim color
- **Streaming Output**: Real-time response streaming
- **Flexible Model Selection**: Choose NVIDIA only, Gemini only, or mix both

#### Files Modified
1. **llm_call.py**
   - Added `z-ai/glm4.7` model definition
   - Set as `DEFAULT_MODEL`
   - Kept all Gemini models as options

2. **llm.py**
   - Added NVIDIA API client initialization
   - Added `_call_nvidia()` function with streaming
   - Refactored `call_llm()` to route to correct provider
   - Added reasoning output with color codes
   - Kept `_call_gemini()` for backward compatibility

3. **agents/sales.py**
   - Updated model selection table
   - Changed options to:
     1. NVIDIA z-ai/glm4.7 for all (recommended)
     2. Gemini 2.5 Flash-Lite for all
     3. Mix: NVIDIA for planning, Gemini for coding

4. **.env.example**
   - Added `NVIDIA_API_KEY` as primary
   - Made `GEMINI_API_KEY` optional
   - Added links to get API keys

5. **pyproject.toml**
   - Added `openai>=1.0.0` dependency

6. **test_setup.py**
   - Added test for `openai` package
   - Updated environment test to check both API keys
   - Passes if at least one API key is configured

#### New Documentation
- **SETUP_NVIDIA.md**: Complete guide for NVIDIA API setup
- **CHANGELOG.md**: This file

#### Benefits
- ✅ Free reasoning-capable model as default
- ✅ Backward compatible with Gemini
- ✅ Easy to add more providers (OpenAI, Claude, etc.)
- ✅ Flexible model mixing for optimal performance

---

## [2.0.0] - 2026-05-04

### Initial Release - Complete Multi-Agent System

#### Core System
- **Orchestrator**: Python-based pipeline manager
- **State Management**: Resume from any crash point
- **Event Logging**: Full audit trail
- **Quality Gates**: Verify output after each agent
- **Retry Logic**: Up to 3 attempts with feedback
- **Human Checkpoints**: 3 approval points

#### Agents (10 total)
1. **Sales Agent**: Requirements gathering
2. **Manager Agent**: Project planning
3. **Architect Agent**: Technical decisions
4. **DB Engineer Agent**: Database schema design
5. **Backend Engineer Agent**: API design
6. **Frontend Engineer Agent**: UI design
7. **Coder Agent**: Code generation (3 phases)
8. **Reviewer Agent**: Quality gate (2 phases)
9. **Tester Agent**: Test generation (3 phases)
10. **Delivery Agent**: Final report

#### Features
- File-based communication between agents
- Shared memory (memory.json) for consistency
- Dependency graph for parallel execution
- Rich terminal UI with colors and progress
- Complete documentation

#### Documentation
- **README.md**: Project overview
- **QUICKSTART.md**: Quick start guide
- **ARCHITECTURE.md**: Deep dive into design
- **CONTRIBUTING.md**: Contribution guide
- **PIPELINE_FLOW.md**: Visual flow diagrams
- **BUILD_SUMMARY.md**: What was built

#### Infrastructure
- **test_setup.py**: Setup verification script
- **.env.example**: Environment template
- **.gitignore**: Proper ignores for .coder output

---

## Roadmap

### [2.2.0] - Planned
- [ ] Actual code execution and testing
- [ ] Bug fix loop (Coder ↔ Tester)
- [ ] Better file parsing from LLM responses
- [ ] Enable parallel execution with threading

### [2.3.0] - Planned
- [ ] Claude API support
- [ ] OpenAI GPT-4 support
- [ ] More tech stacks (Go, Rust, etc.)
- [ ] Web UI for monitoring

### [3.0.0] - Future
- [ ] Docker containerization
- [ ] CI/CD pipeline generation
- [ ] Database migration generation
- [ ] API client generation
- [ ] Self-improving prompts

---

## Migration Guide

### From 2.0.0 to 2.1.0

#### If you want to use NVIDIA (recommended):

1. Install new dependency:
   ```bash
   uv sync
   ```

2. Get NVIDIA API key from https://build.nvidia.com/

3. Update `.env`:
   ```bash
   NVIDIA_API_KEY=nvapi-your_key_here
   ```

4. Run as normal:
   ```bash
   python main.py
   ```

#### If you want to keep using Gemini only:

1. Install new dependency (required even if not using NVIDIA):
   ```bash
   uv sync
   ```

2. Keep your existing `.env` with `GEMINI_API_KEY`

3. During model selection, choose option 2 (Gemini for all)

#### No breaking changes
- All existing functionality preserved
- Gemini still fully supported
- Can use both APIs simultaneously

---

## Contributors

- Initial system design and implementation
- NVIDIA API integration
- Documentation

---

## License

MIT License - See LICENSE file for details

---

**Version Format:** MAJOR.MINOR.PATCH
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible
