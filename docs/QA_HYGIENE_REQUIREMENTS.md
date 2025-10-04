# JaManager - QA Hygiene Requirements & Coding Standards

## Overview
This document defines coding standards, best practices, and hygiene requirements for the JaManager project. It serves as a continuous quality assurance guide for developers and can be used to create epics and tasks for code improvement.

## 🎯 Core Coding Standards

### Python Standards
- **Be Pythonic**: Follow PEP 8, use Python idioms, leverage built-in functions
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication, create reusable functions
- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Clean Code**: Meaningful names, small functions, clear intent
- **Type Hints**: Use type annotations for all function parameters and return values
- **Error Handling**: Specific exception handling, never bare `except:` clauses
- **Documentation**: Docstrings for all public functions, classes, and modules

### JavaScript Standards
- **ES6+ Features**: Use modern JavaScript features (const/let, arrow functions, destructuring)
- **Modular Design**: Separate concerns, avoid global variables
- **Error Handling**: Proper try-catch blocks, meaningful error messages
- **Performance**: Avoid memory leaks, optimize DOM operations
- **Accessibility**: ARIA labels, keyboard navigation, semantic HTML

### UI/UX Standards
- **Accessibility First**: WCAG 2.1 AA compliance, keyboard navigation, screen reader support
- **Responsive Design**: Mobile-first approach, consistent across all devices
- **User Experience**: Intuitive navigation, clear feedback, consistent interactions
- **Visual Design**: Consistent color scheme, typography, spacing, and component library
- **Performance**: Fast loading, smooth animations, optimized images
- **Usability**: Clear labels, helpful error messages, logical information architecture

### General Standards
- **Security First**: Input validation, output encoding, secure defaults
- **Performance**: Optimize for speed and memory usage
- **Maintainability**: Clear structure, consistent patterns, good documentation
- **Testing**: Unit tests, integration tests, test coverage > 80%
- **Version Control**: Meaningful commit messages, atomic commits, proper branching

## 🚨 Critical Issues Found (Priority 1)

### 1. Debug Code in Production
**Issue**: 522+ `console.log` statements throughout the codebase
**Files Affected**: 
- `static/js/jam-songs.js` (50+ statements)
- `static/js/jam-websocket.js` (30+ statements)
- `static/app.js` (20+ statements)
- Multiple other JS files

**Requirements**:
- [ ] Remove all `console.log` statements from production code
- [ ] Implement proper logging system with configurable levels
- [ ] Use structured logging (JSON format) for better monitoring
- [ ] Add debug mode flag for development logging

**Implementation**:
```javascript
// Replace console.log with proper logging
const logger = {
    debug: (message, data) => {
        if (DEBUG_MODE) console.log(`[DEBUG] ${message}`, data);
    },
    info: (message) => console.info(`[INFO] ${message}`),
    error: (message, error) => console.error(`[ERROR] ${message}`, error)
};
```

### 2. Incomplete TODO Items
**Issue**: 2 TODO items in production code
**Files**: `core/feature_flag_api_simple.py`
```python
created_by="api_user"  # TODO: Get actual user ID
```

**Requirements**:
- [ ] Complete all TODO items or create proper tickets
- [ ] Implement user context tracking
- [ ] Add audit trail for feature flag changes

### 3. Bare Exception Handling
**Issue**: 117 instances of bare `except:` clauses
**Examples**:
```python
except Exception as e:  # Too broad
except:  # Dangerous - catches everything
```

**Requirements**:
- [ ] Replace all bare exception handlers with specific exceptions
- [ ] Add proper error logging and user feedback
- [ ] Implement error recovery strategies where appropriate

**Implementation**:
```python
# Instead of:
except Exception as e:
    pass

# Use:
except (ValueError, TypeError) as e:
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")
```

## 🎨 UI/UX Issues (Priority 2)

### 4. Accessibility Compliance Issues
**Issue**: Limited accessibility features throughout the application
**Files Affected**: All HTML files, CSS files, JavaScript components

**Requirements**:
- [ ] Add ARIA labels to all interactive elements
- [ ] Implement proper heading hierarchy (h1 → h2 → h3)
- [ ] Add alt text to all images
- [ ] Ensure keyboard navigation works for all features
- [ ] Add focus indicators for all focusable elements
- [ ] Implement skip links for main content
- [ ] Add screen reader announcements for dynamic content

**Implementation**:
```html
<!-- Instead of: -->
<button onclick="vote()">❤️</button>

<!-- Use: -->
<button onclick="vote()" 
        aria-label="Vote for this song" 
        aria-pressed="false"
        role="button">
    <span aria-hidden="true">❤️</span>
    <span class="sr-only">Vote for this song</span>
</button>
```

### 5. Responsive Design Issues
**Issue**: Inconsistent mobile experience and breakpoints
**Files Affected**: `static/css/base.css`, `static/css/components.css`, `static/css/jam.css`

**Requirements**:
- [ ] Implement consistent breakpoint system (mobile: 320px, tablet: 768px, desktop: 1024px)
- [ ] Ensure touch targets are minimum 44px × 44px
- [ ] Fix horizontal scrolling on mobile devices
- [ ] Optimize font sizes for mobile readability
- [ ] Test on actual devices, not just browser dev tools
- [ ] Implement proper viewport meta tag

**Implementation**:
```css
/* Consistent breakpoint system */
@media (max-width: 320px) { /* Small mobile */ }
@media (max-width: 480px) { /* Mobile */ }
@media (max-width: 768px) { /* Tablet */ }
@media (max-width: 1024px) { /* Desktop */ }

/* Touch-friendly buttons */
.btn {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 16px;
}
```

### 6. Visual Design Inconsistencies
**Issue**: Inconsistent spacing, colors, and component styling
**Files Affected**: All CSS files

**Requirements**:
- [ ] Implement design system with consistent spacing scale (4px, 8px, 16px, 24px, 32px)
- [ ] Standardize color palette with semantic color names
- [ ] Create consistent component library
- [ ] Implement proper typography scale
- [ ] Add consistent border radius and shadows
- [ ] Ensure proper contrast ratios (4.5:1 for normal text, 3:1 for large text)

**Implementation**:
```css
/* Design system variables */
:root {
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    
    --color-primary: #3498db;
    --color-success: #27ae60;
    --color-danger: #e74c3c;
    --color-warning: #f39c12;
    
    --border-radius-sm: 4px;
    --border-radius-md: 8px;
    --border-radius-lg: 12px;
}
```

### 7. User Experience Issues
**Issue**: Poor user feedback and unclear interactions
**Files Affected**: JavaScript files, HTML templates

**Requirements**:
- [ ] Add loading states for all async operations
- [ ] Implement proper error messages with actionable guidance
- [ ] Add success confirmations for user actions
- [ ] Ensure consistent button states (loading, disabled, active)
- [ ] Add tooltips for complex features
- [ ] Implement proper form validation with inline feedback

**Implementation**:
```javascript
// Loading states
async function voteForSong(songId) {
    const button = document.querySelector(`[data-song-id="${songId}"] .vote-btn`);
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span> Voting...';
    
    try {
        await api.vote(songId);
        showSuccess('Vote recorded!');
    } catch (error) {
        showError('Failed to vote. Please try again.');
    } finally {
        button.disabled = false;
        button.innerHTML = '❤️ Vote';
    }
}
```

## 🔧 Code Quality Issues (Priority 3)

### 8. Inconsistent Error Handling Patterns
**Issue**: Mixed error handling approaches across the codebase
**Requirements**:
- [ ] Standardize error response format
- [ ] Implement global exception handler
- [ ] Add error codes for client-side handling
- [ ] Create error handling middleware

### 9. Missing Type Hints
**Issue**: Inconsistent type annotation usage
**Requirements**:
- [ ] Add type hints to all function signatures
- [ ] Use `mypy` for type checking
- [ ] Add return type annotations
- [ ] Use `typing` module for complex types

### 10. Security Concerns
**Issue**: Potential security vulnerabilities
**Requirements**:
- [ ] Review CORS configuration (currently allows all origins)
- [ ] Implement rate limiting
- [ ] Add input validation middleware
- [ ] Review file upload security
- [ ] Implement CSRF protection

## 📊 Performance & Monitoring (Priority 4)

### 11. Database Query Optimization
**Issue**: No query optimization or monitoring
**Requirements**:
- [ ] Add database query logging
- [ ] Implement query performance monitoring
- [ ] Add database indexes for frequently queried fields
- [ ] Use connection pooling
- [ ] Implement query caching where appropriate

### 12. WebSocket Connection Management
**Issue**: No connection monitoring or cleanup
**Requirements**:
- [ ] Add connection health monitoring
- [ ] Implement connection cleanup on errors
- [ ] Add connection limits per jam
- [ ] Monitor WebSocket message rates

### 13. Memory Management
**Issue**: Potential memory leaks in JavaScript
**Requirements**:
- [ ] Remove event listeners on component destruction
- [ ] Implement proper cleanup in WebSocket handlers
- [ ] Monitor memory usage in production
- [ ] Add memory leak detection tests

## 🧪 Testing & Quality Assurance (Priority 5)

### 14. Test Coverage
**Issue**: Limited test coverage
**Requirements**:
- [ ] Achieve >80% test coverage
- [ ] Add integration tests for all API endpoints
- [ ] Add frontend unit tests
- [ ] Add WebSocket connection tests
- [ ] Add performance tests

### 15. Code Documentation
**Issue**: Inconsistent documentation
**Requirements**:
- [ ] Add docstrings to all public functions
- [ ] Document API endpoints with OpenAPI
- [ ] Add inline comments for complex logic
- [ ] Create developer documentation

### 16. Code Review Process
**Issue**: No formal code review standards
**Requirements**:
- [ ] Implement mandatory code reviews
- [ ] Create code review checklist
- [ ] Add automated code quality checks
- [ ] Implement pre-commit hooks

## 🛠️ Development Workflow (Priority 6)

### 17. Dependency Management
**Issue**: Dependencies not pinned to exact versions
**Requirements**:
- [ ] Pin all dependencies to exact versions
- [ ] Regular dependency updates with testing
- [ ] Security vulnerability scanning
- [ ] Dependency audit reports

### 18. Environment Configuration
**Issue**: Hardcoded configuration values
**Requirements**:
- [ ] Move all configuration to environment variables
- [ ] Create configuration validation
- [ ] Add configuration documentation
- [ ] Implement configuration testing

### 19. Build & Deployment
**Issue**: Manual deployment process
**Requirements**:
- [ ] Implement CI/CD pipeline
- [ ] Add automated testing in pipeline
- [ ] Implement blue-green deployments
- [ ] Add deployment rollback capability

## 📋 Agent-Optimized Implementation Roadmap

### Phase 1: Critical Issues (5-10 minutes)
**Agent Tasks**: Automated code cleanup and immediate fixes
1. Remove all console.log statements (2-3 minutes)
2. Fix bare exception handling (3-4 minutes)
3. Complete TODO items (1-2 minutes)
4. Implement proper logging system (2-3 minutes)

### Phase 2: UI/UX & Accessibility (10-15 minutes)
**Agent Tasks**: Automated UI improvements and accessibility fixes
1. Implement accessibility features (ARIA labels, keyboard navigation) (5-7 minutes)
2. Fix responsive design issues (3-4 minutes)
3. Create design system and component library (4-5 minutes)
4. Improve user experience and feedback (3-4 minutes)

### Phase 3: Code Quality (8-12 minutes)
**Agent Tasks**: Automated code quality improvements
1. Add type hints throughout codebase (4-6 minutes)
2. Standardize error handling (2-3 minutes)
3. Implement security improvements (2-3 minutes)
4. Add input validation (2-3 minutes)

### Phase 4: Performance & Monitoring (5-8 minutes)
**Agent Tasks**: Automated performance optimizations
1. Add database monitoring (2-3 minutes)
2. Implement WebSocket monitoring (2-3 minutes)
3. Add performance metrics (1-2 minutes)
4. Optimize database queries (2-3 minutes)

### Phase 5: Testing & Documentation (10-15 minutes)
**Agent Tasks**: Automated testing and documentation generation
1. Increase test coverage (5-8 minutes)
2. Add integration tests (3-5 minutes)
3. Improve documentation (2-3 minutes)
4. Implement code review process (2-3 minutes)

### Phase 6: Workflow & Deployment (5-10 minutes)
**Agent Tasks**: Automated CI/CD and deployment setup
1. Implement CI/CD pipeline (3-5 minutes)
2. Add automated quality checks (2-3 minutes)
3. Improve deployment process (2-3 minutes)
4. Add monitoring and alerting (2-3 minutes)

**Total Estimated Time: 43-70 minutes for complete codebase transformation**

## 🎯 Success Metrics

### Code Quality Metrics
- [ ] Zero console.log statements in production
- [ ] Zero bare exception handlers
- [ ] 100% type hint coverage
- [ ] >80% test coverage
- [ ] Zero security vulnerabilities

### UI/UX Metrics
- [ ] WCAG 2.1 AA compliance (100% of pages)
- [ ] Mobile responsiveness score > 95%
- [ ] Touch target size compliance (44px minimum)
- [ ] Color contrast ratio > 4.5:1
- [ ] Page load time < 2 seconds
- [ ] User task completion rate > 90%

### Performance Metrics
- [ ] API response time < 200ms (95th percentile)
- [ ] WebSocket connection stability > 99%
- [ ] Database query time < 100ms (95th percentile)
- [ ] Memory usage stable over time

### Process Metrics
- [ ] All code changes reviewed
- [ ] All tests passing in CI/CD
- [ ] Zero production incidents
- [ ] Documentation up to date

## 🔍 Code Review Checklist

### Before Submitting PR
- [ ] No console.log statements
- [ ] Proper error handling
- [ ] Type hints added
- [ ] Tests written/updated
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Performance impact assessed
- [ ] Accessibility features implemented
- [ ] Mobile responsiveness tested
- [ ] UI/UX follows design system

### During Code Review
- [ ] Code follows project standards
- [ ] Logic is clear and maintainable
- [ ] Error cases are handled
- [ ] Security implications considered
- [ ] Performance impact acceptable
- [ ] Tests are comprehensive
- [ ] Accessibility requirements met
- [ ] UI/UX is consistent and intuitive
- [ ] Cross-browser compatibility verified

## 📚 Resources & Tools

### Recommended Tools
- **Code Quality**: `black`, `isort`, `flake8`, `mypy`
- **Testing**: `pytest`, `pytest-cov`, `httpx`
- **Security**: `bandit`, `safety`
- **Performance**: `pytest-benchmark`, `memory-profiler`
- **Documentation**: `sphinx`, `mkdocs`
- **UI/UX**: `axe-core`, `lighthouse`, `wave`, `pa11y`
- **Accessibility**: `axe-core`, `pa11y`, `lighthouse-ci`
- **Design**: `figma`, `storybook`, `chromatic`
- **Agent Tools**: `cursor-agent`, `github-copilot`, `code-review-bot`
- **Automation**: `pre-commit`, `husky`, `lint-staged`

### Learning Resources
- [PEP 8 - Python Style Guide](https://pep8.org/)
- [Clean Code by Robert Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [JavaScript Best Practices](https://github.com/airbnb/javascript)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Web Accessibility Tutorials](https://www.w3.org/WAI/tutorials/)
- [Material Design Guidelines](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

### Agent-Specific Resources
- [Cursor Agent Documentation](https://cursor.sh/docs)
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot)
- [AI Code Review Guidelines](https://github.com/features/copilot)
- [Automated Testing with AI](https://docs.pytest.org/)
- [Agent Prompt Engineering](https://www.promptingguide.ai/)

## 🤖 Agent Implementation Strategy

### Agent Task Breakdown
Each issue can be implemented by a Cursor agent using specific prompts:

#### **Console.log Removal (2-3 minutes)**
```
Agent Prompt: "Remove all console.log statements from the codebase and replace with proper logging. Use a configurable logging system with DEBUG_MODE flag."
```

#### **Accessibility Implementation (5-7 minutes)**
```
Agent Prompt: "Add ARIA labels, keyboard navigation, and screen reader support to all interactive elements. Ensure WCAG 2.1 AA compliance."
```

#### **Type Hints Addition (4-6 minutes)**
```
Agent Prompt: "Add comprehensive type hints to all Python functions, including return types and complex types from typing module."
```

#### **Error Handling Standardization (2-3 minutes)**
```
Agent Prompt: "Replace all bare exception handlers with specific exception types and proper error logging."
```

### Agent Workflow Optimization
1. **Feature Branch Strategy**: All agents work on feature branches, never directly on main
2. **Parallel Processing**: Multiple agents can work on different files simultaneously
3. **Incremental Changes**: Each agent focuses on one specific improvement
4. **Validation**: Automated testing after each agent completes their task
5. **Sequential Merge**: Merge agents one at a time with validation

### Agent-Specific Requirements
- **Feature Branch Only**: Agents NEVER work directly on main branch
- **Clear Instructions**: Each task has specific, actionable prompts
- **Atomic Changes**: Each agent makes one type of change across the codebase
- **Validation Steps**: Built-in testing and verification for each change
- **Documentation**: Agents update documentation as they make changes

### Git Workflow for Agents
```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/agent-hygiene-improvements

# 2. Each agent works on their assigned files
git checkout -b feature/agent-1-console-logs
git checkout -b feature/agent-2-accessibility
git checkout -b feature/agent-3-type-hints
# etc.

# 3. Sequential merge back to feature branch
git checkout feature/agent-hygiene-improvements
git merge feature/agent-1-console-logs --no-ff
make test  # Validate before next merge
git merge feature/agent-2-accessibility --no-ff
make test  # Validate before next merge
# Continue...

# 4. Final merge to main
git checkout main
git merge feature/agent-hygiene-improvements --no-ff
```

### Continuous Agent Monitoring
- **Code Quality Gates**: Automated checks prevent regression
- **Performance Monitoring**: Track improvement metrics in real-time
- **Agent Success Rate**: Monitor which agents are most effective
- **Feedback Loop**: Learn from agent performance to improve prompts

---

*This document should be reviewed and updated quarterly to reflect new requirements and lessons learned.*
