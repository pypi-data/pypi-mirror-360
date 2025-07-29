"""
Terminal Security Layer for VeriDoc
Command filtering and session isolation
"""

import re
import logging
import time
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SecurityPolicy:
    """Terminal security policy configuration."""
    allowed_commands: Set[str]
    blocked_commands: Set[str]
    dangerous_patterns: List[re.Pattern]
    max_command_length: int = 1000
    session_timeout: int = 3600  # 1 hour
    log_all_commands: bool = True


class TerminalSecurityManager:
    """Manages terminal security policies and command filtering."""
    
    def __init__(self, base_path: str, log_file: Optional[str] = None):
        self.base_path = Path(base_path).resolve()
        self.log_file = log_file or "logs/terminal_audit.log"
        self.sessions: Dict[str, Dict] = {}
        
        # Configure logging
        self._setup_logging()
        
        # Default security policy
        self.policy = self._create_default_policy()
    
    def _setup_logging(self):
        """Setup audit logging for terminal commands."""
        # Ensure log directory exists
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure terminal audit logger
        terminal_logger = logging.getLogger('terminal_audit')
        terminal_logger.setLevel(logging.INFO)
        
        # File handler for audit logs
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - Session: %(session_id)s - Command: %(command)s - Status: %(status)s'
        )
        handler.setFormatter(formatter)
        terminal_logger.addHandler(handler)
        
        self.audit_logger = terminal_logger
    
    def _create_default_policy(self) -> SecurityPolicy:
        """Create default security policy for terminal access."""
        # Safe commands that are generally allowed
        allowed_commands = {
            # File operations (read-only focus)
            'ls', 'cat', 'head', 'tail', 'less', 'more', 'find', 'grep', 'awk', 'sed',
            'sort', 'uniq', 'wc', 'file', 'which', 'whereis', 'locate',
            
            # Directory navigation
            'cd', 'pwd', 'tree', 'du', 'df',
            
            # Text processing
            'echo', 'printf', 'cut', 'tr', 'paste', 'join',
            
            # Development tools
            'git', 'python', 'python3', 'node', 'npm', 'pip', 'pip3',
            'make', 'cmake', 'gcc', 'g++', 'javac', 'java',
            
            # Documentation tools
            'man', 'info', 'help', 'pandoc', 'markdown',
            
            # System info (safe)
            'uname', 'whoami', 'id', 'date', 'uptime', 'ps', 'top', 'htop',
            'env', 'printenv', 'history',
            
            # Archive operations (read-only)
            'tar', 'zip', 'unzip', 'gzip', 'gunzip',
            
            # Network tools (limited)
            'curl', 'wget', 'ping',
        }
        
        # Dangerous commands that should be blocked
        blocked_commands = {
            # System modification
            'rm', 'rmdir', 'mv', 'cp', 'ln', 'chmod', 'chown', 'chgrp',
            'mount', 'umount', 'fdisk', 'mkfs', 'fsck',
            
            # Process control
            'kill', 'killall', 'pkill', 'nohup', 'bg', 'fg', 'jobs',
            
            # System administration
            'sudo', 'su', 'passwd', 'useradd', 'userdel', 'usermod',
            'groupadd', 'groupdel', 'crontab', 'systemctl', 'service',
            
            # Network services
            'ssh', 'scp', 'rsync', 'ftp', 'sftp', 'telnet', 'nc', 'netcat',
            
            # Compilation that could create executables
            'as', 'ld', 'strip', 'objcopy', 'objdump',
            
            # Package management
            'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'brew',
            
            # System configuration
            'iptables', 'ufw', 'firewall-cmd', 'semanage', 'setsebool',
        }
        
        # Dangerous patterns to detect
        dangerous_patterns = [
            re.compile(r'.*\|\s*(sh|bash|zsh|fish|csh|tcsh)\s*'),  # Piping to shell
            re.compile(r'.*>\s*/dev/.*'),  # Writing to device files
            re.compile(r'.*\$\(.*\).*'),  # Command substitution
            re.compile(r'.*`.*`.*'),  # Backtick command substitution
            re.compile(r'.*;\s*(rm|mv|cp|chmod|chown)\s+'),  # Chained dangerous commands
            re.compile(r'.*/etc/.*'),  # Accessing system config
            re.compile(r'.*/proc/.*'),  # Accessing proc filesystem
            re.compile(r'.*/sys/.*'),  # Accessing sys filesystem
            re.compile(r'.*\\x[0-9a-fA-F]{2}.*'),  # Hex encoding
            re.compile(r'.*\x00.*'),  # Null bytes
        ]
        
        return SecurityPolicy(
            allowed_commands=allowed_commands,
            blocked_commands=blocked_commands,
            dangerous_patterns=dangerous_patterns,
            max_command_length=1000,
            session_timeout=3600,
            log_all_commands=True
        )
    
    def create_session(self, session_id: str, user_info: Optional[Dict] = None) -> bool:
        """Create a new terminal session with security tracking."""
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists")
            return False
        
        self.sessions[session_id] = {
            'created_at': time.time(),
            'user_info': user_info or {},
            'command_count': 0,
            'last_activity': time.time(),
            'violations': [],
            'status': 'active'
        }
        
        self.audit_logger.info(
            "Session created",
            extra={
                'session_id': session_id,
                'command': 'SESSION_START',
                'status': 'ALLOWED'
            }
        )
        
        return True
    
    def validate_command(self, session_id: str, command: str) -> Dict[str, any]:
        """
        Validate a command against security policy.
        
        Returns:
            Dict with keys: allowed (bool), reason (str), sanitized_command (str)
        """
        result = {
            'allowed': False,
            'reason': '',
            'sanitized_command': command.strip(),
            'risk_level': 'low'
        }
        
        # Update session activity
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = time.time()
            self.sessions[session_id]['command_count'] += 1
        
        # Basic validation
        if not command or not command.strip():
            result['allowed'] = True
            result['reason'] = 'Empty command'
            return result
        
        command = command.strip()
        
        # Length check
        if len(command) > self.policy.max_command_length:
            result['reason'] = f'Command too long (max {self.policy.max_command_length} chars)'
            result['risk_level'] = 'high'
            self._log_violation(session_id, command, result['reason'])
            return result
        
        # Check for dangerous patterns
        for pattern in self.policy.dangerous_patterns:
            if pattern.search(command):
                result['reason'] = f'Command matches dangerous pattern: {pattern.pattern}'
                result['risk_level'] = 'high'
                self._log_violation(session_id, command, result['reason'])
                return result
        
        # Extract base command (first word)
        base_command = command.split()[0] if command.split() else ''
        
        # Remove path from command
        base_command = Path(base_command).name
        
        # Check blocked commands
        if base_command in self.policy.blocked_commands:
            result['reason'] = f'Command "{base_command}" is explicitly blocked'
            result['risk_level'] = 'high'
            self._log_violation(session_id, command, result['reason'])
            return result
        
        # Check allowed commands
        if base_command in self.policy.allowed_commands:
            # Additional checks for allowed commands
            sanitized = self._sanitize_command(command)
            if sanitized != command:
                result['sanitized_command'] = sanitized
                result['reason'] = 'Command sanitized'
                result['risk_level'] = 'medium'
            else:
                result['reason'] = 'Command allowed'
            
            result['allowed'] = True
            self._log_command(session_id, command, 'ALLOWED')
            return result
        
        # Unknown command - apply cautious policy
        result['reason'] = f'Unknown command "{base_command}" - not in allowed list'
        result['risk_level'] = 'medium'
        self._log_violation(session_id, command, result['reason'])
        return result
    
    def _sanitize_command(self, command: str) -> str:
        """Sanitize command to remove potentially dangerous elements."""
        # Remove null bytes
        sanitized = command.replace('\x00', '')
        
        # Remove excessive whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Basic path traversal protection for arguments
        parts = sanitized.split()
        for i, part in enumerate(parts):
            if '../' in part or '/..' in part:
                # Remove path traversal attempts from arguments
                parts[i] = part.replace('../', '').replace('/..', '')
        
        return ' '.join(parts)
    
    def _log_command(self, session_id: str, command: str, status: str):
        """Log command execution for audit trail."""
        self.audit_logger.info(
            "Command executed",
            extra={
                'session_id': session_id,
                'command': command[:100] + '...' if len(command) > 100 else command,
                'status': status
            }
        )
    
    def _log_violation(self, session_id: str, command: str, reason: str):
        """Log security violation."""
        if session_id in self.sessions:
            self.sessions[session_id]['violations'].append({
                'timestamp': time.time(),
                'command': command,
                'reason': reason
            })
        
        self.audit_logger.warning(
            "Security violation",
            extra={
                'session_id': session_id,
                'command': command[:100] + '...' if len(command) > 100 else command,
                'status': f'BLOCKED - {reason}'
            }
        )
    
    def end_session(self, session_id: str):
        """End a terminal session and log the closure."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['status'] = 'ended'
            session['ended_at'] = time.time()
            
            self.audit_logger.info(
                "Session ended",
                extra={
                    'session_id': session_id,
                    'command': 'SESSION_END',
                    'status': f'ENDED - Commands: {session["command_count"]}, Violations: {len(session["violations"])}'
                }
            )
    
    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """Get statistics for a terminal session."""
        return self.sessions.get(session_id)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions based on timeout policy."""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (current_time - session['last_activity']) > self.policy.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
            del self.sessions[session_id]
    
    def update_policy(self, 
                     allowed_commands: Optional[Set[str]] = None,
                     blocked_commands: Optional[Set[str]] = None,
                     max_command_length: Optional[int] = None):
        """Update security policy dynamically."""
        if allowed_commands is not None:
            self.policy.allowed_commands = allowed_commands
        
        if blocked_commands is not None:
            self.policy.blocked_commands = blocked_commands
        
        if max_command_length is not None:
            self.policy.max_command_length = max_command_length
        
        logger.info("Terminal security policy updated")
    
    def get_policy_summary(self) -> Dict:
        """Get summary of current security policy."""
        return {
            'allowed_commands_count': len(self.policy.allowed_commands),
            'blocked_commands_count': len(self.policy.blocked_commands),
            'dangerous_patterns_count': len(self.policy.dangerous_patterns),
            'max_command_length': self.policy.max_command_length,
            'session_timeout': self.policy.session_timeout,
            'active_sessions': len([s for s in self.sessions.values() if s['status'] == 'active'])
        }