# Claude Code Architecture Analysis

## Part 1: Claude Code's .claude Folder Architecture

### 1.1 Directory Structure

**Base Location:** `~/.claude/`

**Key Components:**
- `~/.claude/projects/` - Session data storage
- `~/.claude/commands/` - Custom slash commands
- `~/.claude/settings.json` - Configuration

### 1.2 Project Directory Mapping

Claude Code uses a deterministic path transformation:

```
Input Path:  /Users/john/code/myproject
Transform:   Replace '/' with '-', add leading '-'
Result:      ~/.claude/projects/-Users-john-code-myproject/
```

**Examples:**
- `/Users/john/code/myproject` → `-Users-john-code-myproject`
- `/home/user/dev/webapp` → `-home-user-dev-webapp`
- `/mnt/c/projects/ai` → `-mnt-c-projects-ai`

### 1.3 Session File Organization

Each project directory contains session files:
```
~/.claude/projects/-Users-john-code-myproject/
├── f33cdb42-0a41-40d4-91eb-c89c109af38a.jsonl
├── 8503613d-f473-4525-afb3-a568f6fc5c81.jsonl
└── a1b2c3d4-e5f6-7890-abcd-ef1234567890.jsonl
```

**File Characteristics:**
- **Format:** JSONL (JSON Lines - one JSON object per line)
- **Naming:** UUID v4 format (e.g., `f33cdb42-0a41-40d4-91eb-c89c109af38a.jsonl`)
- **Content:** Complete conversation history for one session
- **Updates:** Real-time incremental appends during conversations

### 1.4 JSONL File Structure

Each line contains a JSON object representing one conversation event:

```jsonl
{"sessionId": "f33cdb42-...", "uuid": "msg-uuid", "timestamp": "2025-07-02T20:06:59.614Z", "message": {...}}
```

**Core Fields:**
- `sessionId` - Session identifier
- `uuid` - Message unique identifier  
- `parentUuid` - Parent message (for threading)
- `timestamp` - ISO 8601 timestamp
- `cwd` - Working directory
- `requestId` - Request correlation
- `message` - Actual message content

### 1.5 Message Content Structure

**User Messages:**
```json
{
  "message": {
    "role": "user",
    "content": "User's message"
  }
}
```

**Assistant Messages:**
```json
{
  "message": {
    "role": "assistant", 
    "model": "claude-opus-4-20250514",
    "content": [
      {"type": "thinking", "thinking": "Internal reasoning...", "signature": "crypto-sig"},
      {"type": "text", "text": "Response text"},
      {"type": "tool_use", "name": "Bash", "id": "tool-id", "input": {...}},
      {"type": "tool_result", "tool_use_id": "tool-id", "content": "result"}
    ],
    "usage": {
      "input_tokens": 1500,
      "output_tokens": 750,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 0,
      "service_tier": "standard"
    }
  }
}
```

### 1.6 Real-time File Updates

Claude Code demonstrates these behaviors:
- **Incremental Updates:** New conversation entries are appended to JSONL files
- **Immediate Writing:** Each message/response creates new file entries
- **Concurrent Sessions:** Multiple sessions per project are supported with unique file names

### 1.7 Configuration System

**Settings File:** `~/.claude/settings.json` or `~/.claude/settings.local.json`
```json
{
  "permissions": {
    "allow": ["Bash(diff:*)", "WebFetch(domain:github.com)"],
    "deny": []
  }
}
```

**Custom Commands:** `~/.claude/commands/`
- Markdown files defining slash commands
- Integration with shell execution

---

## Part 2: Implementation Techniques for Custom Tools

### 2.1 Project Directory Discovery

**Path Transformation Logic:**
- Take the current working directory path
- Replace all `/` characters with `-` 
- Remove any leading `-` if it exists
- Add a single leading `-` to the result
- Combine with `~/.claude/projects/` to get the full Claude project directory

**Example:** `/Users/john/code/myproject` becomes `~/.claude/projects/-Users-john-code-myproject/`

### 2.2 Session Identification

**Smart Default with Option to Browse:**
1. **Find most recently modified session** - check all `.jsonl` files and select the one with latest modification time
2. **Show preview of most recent session**:
   - Display first message (session start)
   - Display last few messages (recent activity) 
   - Show session duration and message count
3. **Ask for confirmation**: "Export this session? (y/n/browse)"
4. **If 'y'** - proceed with export
5. **If 'n'** - exit
6. **If 'browse'** - show session selection interface

**Session Selection Interface:**
- List all sessions sorted by modification time (most recent first)
- Show preview for each session:
  - Session number, timestamp, duration
  - First message preview
  - Last activity preview
- Let user select by number: "Select session (1-5): "
- Show full preview of selected session for final confirmation

**Benefits:**
- Default works for most cases (single recent session)
- Easy browsing when multiple sessions exist
- Visual selection - no copy/pasting required
- User always sees exactly what they're exporting

### 2.3 JSONL Data Extraction

**Session Metadata Extraction:**
- Read the JSONL file line by line
- Parse each line as a separate JSON object
- Extract key metadata from the first few entries:
  - `sessionId` - the unique session identifier
  - `cwd` - the working directory path
  - `timestamp` - track earliest and latest for session duration

**Conversation Data Parsing:**
- Each line represents one conversation event
- Look for `message` objects with `role` field ("user" or "assistant")
- Extract content from the `content` field
- Handle different content types: text, thinking, tool_use, tool_result

### 2.4 Session Selection Interface

**Default Preview:**
```
[Tool] Most recent session (2025-07-06 14:30-15:25, 45 messages):
First: "Let's work on the authentication system"
Last:  "The tests are passing. Here's the summary..."

Export this session? (y/n/browse): 
```

**Browse Mode Interface:**
```
[Tool] Found 3 recent sessions:

1. 2025-07-06 14:30-15:25 (45 messages) - Most Recent
   First: "Let's work on the authentication system"
   Last:  "The tests are passing. Here's the summary..."

2. 2025-07-06 10:15-11:45 (23 messages)
   First: "Help me debug this API issue"
   Last:  "Great! That fixed the problem."

3. 2025-07-05 16:20-17:10 (12 messages)
   First: "Quick question about React hooks"
   Last:  "Thanks, that makes sense now."

Select session (1-3): 
```

**After Selection:**
```
[Tool] Selected session 2:
Session: 2025-07-06 10:15-11:45 (23 messages)
First: "Help me debug this API issue"
Last:  "Great! That fixed the problem."
Working dir: /Users/john/project

Confirm export? (y/n): 
```

---

## Key Takeaways for Custom Tool Development

1. **Directory Mapping:** Use the path transformation logic to locate session data
2. **Session Identification:** File modification times are the most reliable indicator of recent activity
3. **Multiple Sessions:** Default to the most recently modified session when multiple options exist
4. **JSONL Processing:** Process line-by-line as each line is a complete, independent JSON object
5. **Metadata Extraction:** Session info is embedded within JSONL content, not derived from filenames
6. **Simplicity:** Avoid complex session detection schemes - modification time is sufficient

This architecture enables building reliable tools using straightforward file system operations and JSON parsing.
