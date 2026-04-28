# Architecture

## Layers

```
┌─────────────────────────────────────────────────────┐
│                  INTERFACE LAYER                     │
│   Telegram Bot  │  CLI Runner  │  (extensible)       │
└────────────────────────┬────────────────────────────┘
                         │ TaskContext
┌────────────────────────▼────────────────────────────┐
│                  AGENT RUNTIME                       │
│  Dispatcher  │  SessionManager  │  StateMachine      │
│  ApprovalGate │  PluginRegistry                      │
└────────────────────────┬────────────────────────────┘
                         │ prompt + workdir
┌────────────────────────▼────────────────────────────┐
│                  EXECUTION LAYER                     │
│  ExecutionTool (ABC)    │  WorkflowProvider (ABC)    │
│  ShellTool (built-in)   │  GitHubIssueWorkflow       │
│  ClaudeCodeTool (example)│  (your custom workflows) │
└─────────────────────────────────────────────────────┘
```

## Task Lifecycle

```
RECEIVED → PLANNING → [AWAITING_APPROVAL] → EXECUTING → DONE
                                ↓                  ↓
                           CANCELLED             FAILED → RETRYING
```

## Key Design Decisions

- **WorkflowProvider** owns prompt construction and result interpretation.
  Tools know nothing about what they're running — they just execute.
- **AuthProvider** is injected — swap AllowlistAuthProvider for OAuth or LDAP without changing anything else.
- **ApprovalGate** uses asyncio Futures so the dispatcher can `await` a human decision
  without blocking the event loop.
- Sessions are in-memory by default. For persistence, subclass SessionManager.
