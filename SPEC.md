# Specification: Cross-Platform Computer Usage Tracking Agent (Python)

This specification outlines the architecture, design decisions, and implementation details for a lightweight, OS-agnostic background monitoring agent written in Python. The agent tracks user logins, active applications, and system state, reporting these metrics in real-time to an MQTT broker, with a local SQLite database for offline caching.

---

## 1. Problem Statement

Giancarlo needs a unified, lightweight, cross-platform background service (Windows Desktop, Windows Server, Linux, macOS) that tracks computer usage. An Android variant with reduced capabilities is a future candidate and is explicitly out of scope for v1. 

Specifically, he needs to know:
1. When the computer boots up or shuts down.
2. Which user is logged into the operating system session.
3. What application is currently in the foreground, what its window title is, and how long it remains active.
4. How to guarantee that no data is lost when the machine is offline or the MQTT broker is unreachable.

---

## 2. Solution Architecture

The solution is a lightweight **Python background daemon** utilizing a modular, event-driven design. It abstracts OS-specific APIs behind a clean interface, maintains a lightweight SQLite database for local persistence, and uses an asynchronous MQTT client to stream metrics to a central MQTT server.

```
+-------------------------------------------------------------+
|                     OS Activity Watcher                     |
+-------------------------------------------------------------+
|  +--------------------+  +-------------------------------+  |
|  |     OS Watchers    |  |       Activity Watcher        |  |
|  | (Windows/macOS/Lin) |  |   (Window focus & AFK logic)  |  |
|  +---------+----------+  +---------------+---------------+  |
|            |                             |                  |
|            +--------------+--------------+                  |
|                           | (Activity Event)                |
|                           v                                 |
|                  +-----------------+                        |
|                  |  Event Manager  |                        |
|                  +---+---------+---+                        |
|                      |         |                            |
|         (Save Event) |         | (Publish Event)            |
|                      v         v                            |
|           +------------+     +-------------+                |
|           | SQLite DB  |     | MQTT Client |                |
|           | (Offline)  |     | (Real-time) |                |
|           +------------+     +------+------+                |
+-------------------------------------|-----------------------+
                                      | (JSON Over TCP)
                                      v
                             +-----------------+
                             |   MQTT Broker   |
                             +-----------------+
```

### 2.1 Referenced Systems (Prior Art)
During research, the following systems were analyzed as baseline architectural patterns:
- **ActivityWatch**: An open-source automated time tracker that uses a modular client-server structure. It tracks window titles and AFK (Away From Keyboard) status via native APIs (Win32, AppKit, X11/D-Bus) and stores them in local "buckets". Our agent simplifies this by streaming events directly to MQTT and using local SQLite purely for offline caching instead of a heavy local REST API server.
- **Tockler**: A lightweight cross-platform time tracker that monitors window titles and idle states, saving data to local files. It demonstrates that lightweight polling (1-5 seconds) is highly performant and non-intrusive.
- **rpi-mqtt-monitor & PyMonitorMQTT**: Lightweight daemons that publish system stats and resource usage directly to MQTT topics.

---

## 3. User Stories

### System Lifecycle & Identity
1. **As an administrator**, I want the agent to auto-start when the operating system boots up (as a service/daemon), so that monitoring begins without manual user intervention.
2. **As an administrator**, I want the agent to report a `system/startup` event to MQTT immediately on boot, so that the server knows the machine is online.
3. **As an administrator**, I want the agent to register a "Last Will and Testament" (LWT) message with the MQTT broker, so that the server is notified immediately if the computer crashes or goes offline abruptly.
4. **As an analyst**, I want each event to contain a unique machine identifier (e.g., UUID or hostname) and OS type, so that I can trace data back to a specific endpoint.

### Session & Application Monitoring
5. **As an analyst**, I want to know exactly which OS user is logged into the session, so that I can audit user-level activities on shared machines.
6. **As an analyst**, I want the agent to detect when the foreground window changes, recording the process name (e.g., `chrome.exe`), window title (e.g., `Inboxes - Gmail`), start timestamp, and active duration, so that I can map out detailed productivity stats.
7. **As an analyst**, I want the agent to detect when the user is idle (Away From Keyboard / mouse inactive for > 5 minutes), so that idle time is not incorrectly attributed to the active application.

### Resiliency & Connection Logic
8. **As an administrator**, I want the agent to write all collected events to a local SQLite database first, so that no metrics are lost during network outages or MQTT broker maintenance.
9. **As an administrator**, I want the agent to sync pending events from SQLite to MQTT as soon as connection is re-established, deleting successfully sent records from the local cache to conserve disk space.
10. **As a developer**, I want the agent to run headlessly without any user interface, consuming minimal CPU (<1%) and RAM (<30MB) so as not to degrade the host machine's performance.

---

## 4. Implementation Decisions

### 4.1 Module Structure
The Python agent will be structured into 4 primary layers:
1. **`core`**: Contains database schema (`db.py`), event definitions, configuration loaders, and logging.
2. **`platform_abstraction`**: Dynamic module loading depending on `sys.platform`. It implements a unified `PlatformWatcher` interface.
   - **Windows**: Uses `ctypes` and `pywin32` to leverage `GetForegroundWindow`, `GetWindowText`, and `GetWindowThreadProcessId`.
   - **macOS**: Uses `AppKit` and `Quartz` to monitor `NSWorkspace.sharedWorkspace().activeApplication()`.
   - **Linux**: Uses `python-xlib` for X11 environments. For modern Wayland environments (GNOME/KDE), it hooks into `D-Bus` or monitors desktop focus via system portals.
3. **`network`**: Manages the MQTT lifecycle using `paho-mqtt` or `aiomqtt` (with automatic backoffs and LWT setup).
4. **`daemon`**: The main execution loop coordinating polling, SQLite caching, and network transmissions.

### 4.2 SQLite Database Schema
To guarantee data persistence, a lightweight SQLite database file `cache.db` will be maintained in the agent's application directory.

```sql
CREATE TABLE IF NOT EXISTS event_cache (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    event_type TEXT NOT NULL,         -- 'startup', 'shutdown', 'login', 'logout', 'focus_change', 'idle'
    username TEXT,
    process_name TEXT,
    window_title TEXT,
    start_time TIMESTAMP NOT NULL,    -- UTC ISO8601
    duration_seconds REAL,            -- NULL for instant events like startup/login
    payload TEXT,                     -- Additional JSON metadata
    sent_status INTEGER DEFAULT 0     -- 0 = pending, 1 = sent
);

CREATE INDEX IF NOT EXISTS idx_pending_events ON event_cache(sent_status);
```

### 4.3 MQTT Topic Structure & JSON Payloads
To ensure modular data processing, messages are published to hierarchical MQTT topics.

#### Topic: `client/os_watcher/{hostname}/status`
- Used for LWT and connection state tracking.
- **LWT Payload**: `{"status": "offline", "timestamp": "2026-10-08T16:31:47Z"}`
- **Startup Payload**: `{"status": "online", "os": "Windows 11", "ip": "192.168.1.15", "version": "1.0.0"}`

#### Topic: `client/os_watcher/{hostname}/events`
- Used for login, logout, and application focus changes.
- **Window Focus Event Payload**:
```json
{
  "event_id": "uuid-v4-string",
  "event_type": "focus_change",
  "username": "giancarlo",
  "process_name": "pycharm64.exe",
  "window_title": "computeruse-watcher [Z:\\Customers\\Demo] - SPEC.md",
  "start_time": "2026-10-08T16:30:00Z",
  "duration_seconds": 120.5
}
```

### 4.4 MQTT Transport & Configuration
(Confirmed with the owner — 2026-10-08)

- **Transport**: plain TCP on port **1883, no TLS** in v1 — deployment assumes a trusted local network or VPN. TLS remains a configuration flag (`use_tls: true`) for a future phase.
- **Auth**: optional username/password (broker ACLs). Credentials come from environment variables or a local config file, never hardcoded.
- **MQTT level**: v3.1.1 for broad broker compatibility. The `status` topic is published **retained** (`online` on connect); the **LWT** on the same topic carries the `offline` message.
- **QoS**: 1 on all topics. Events are also persisted locally first (see 4.2), so QoS 1 + SQLite guarantees no data loss even during broker hiccups.

---

## 5. Testing Decisions

1. **Abstraction Mocking**: We will write unit tests using `pytest` that mock the `PlatformWatcher` classes. This ensures we can test the state transition logic (e.g., focus change, idle threshold, database queuing) on any OS without requiring native API availability.
2. **Local SQLite Rollback Integration Test**: 
   - Start the daemon with a mocked MQTT client that simulates a broker disconnection.
   - Inject simulated window changes.
   - Assert records are written to `event_cache` with `sent_status = 0`.
   - Restore the simulated MQTT broker and verify the events are published and purged/marked sent in SQLite.
3. **Memory and CPU Profile Tests**: Run the agent for 1 hour under high window-switching loads, asserting that RAM does not exceed 40MB and average CPU remains below 1%.

---

## 6. Out of Scope

- **Global Inventory / Asset Management**: Tracking complete lists of installed software or file system scanning (explicitly decoupled into separate scheduled crons/agents as per the user's instructions).
- **Remote Agent Execution**: Modifying files or executing commands received from the MQTT broker (this is a one-way telemetry tracking agent for security/performance).
- **Web Portal Visualizer**: The web backend, MQTT broker setup, and PostgreSQL data warehouse are handled by other services.
- **Android**: Excluded from v1 per owner decision (2026-10-08); candidate for a future reduced-capabilities phase (foreground app + boot/shutdown events only, no window titles).
- **Concurrent RDP sessions**: The agent tracks a single active session per host; per-user RDP session splitting is a future extension.
- **Window title redaction**: Titles are reported full, as-is (owner decision, 2026-10-08); any privacy filtering is the responsibility of the server/warehouse, not the agent.

---

## 7. Next Steps & Agent Roadmap

1. **Phase 1 (Core & SQLite)**: Set up the Python project structure, database caching manager, and config handler.
2. **Phase 2 (OS Adapters)**: Build and test Windows, Linux, and macOS active window hooks.
3. **Phase 3 (MQTT Client)**: Integrate connection persistence, auto-reconnect, and SQLite-to-MQTT sync pipeline.
4. **Phase 4 (Packaging)**: Create deployment scripts / setup guides (Windows Service, systemd daemon, LaunchAgent).
5. **Phase 5 (Future — not scheduled)**: Android variant with reduced capabilities (foreground app + boot/shutdown events; no window titles).

---

## 8. Decision Log (Confirmed with the Owner — 2026-10-08)

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | Android in v1? | **No** — future phase | Keep v1 scope tight: Windows / Linux / macOS only. |
| 2 | Window title privacy | **Full title, as-is** | Maximum fidelity for later analysis; filtering handled server-side. |
| 3 | MQTT transport | **No TLS, port 1883** (trusted local/VPN), optional user/pass | Simpler v1; TLS stays as a config flag for later. |
| 4 | Windows Server / RDP | **Single active session per machine** | Covers 90% of cases; concurrent session tracking deferred. |
