import os
import json
import bcrypt
import base64
import getpass
import time
from datetime import datetime, date, timedelta  # Added timedelta import
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from colorama import Fore, Style, init
from typing import Optional, Dict, List, Any
import shutil
from pathlib import Path
import tempfile
import sys
import site

class TaskmanBackend:
    def __init__(self):
        """Initialize TaskMan backend"""
        try:
            # Get user's Documents folder path
            if os.name == 'nt':  # Windows
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    documents_path = winreg.QueryValueEx(key, "Personal")[0]
            else:  # Unix-like
                documents_path = os.path.expanduser("~/Documents")
                
            # Create absolute paths in Documents
            self.data_dir = os.path.join(documents_path, "TaskmanSV_Data")
            self.users_dir = os.path.join(self.data_dir, "users")
            
            print(f"Using Documents folder paths:")
            print(f"Data directory: {self.data_dir}")
            print(f"Users directory: {self.users_dir}")
            
            # Create directories with explicit paths and handle permissions
            for directory in [self.data_dir, self.users_dir]:
                try:
                    if not os.path.exists(directory):
                        # Try to create with full permissions
                        os.makedirs(directory, mode=0o777)
                        print(f"Created directory: {directory}")
                    
                    # Verify write permissions with a test file
                    test_file = os.path.join(directory, ".write_test")
                    try:
                        with open(test_file, 'w') as f:
                            f.write("test")
                        os.remove(test_file)
                    except Exception as e:
                        raise PermissionError(f"Cannot write to directory {directory}: {e}")
                        
                except Exception as e:
                    print(f"Error with directory {directory}: {e}")
                    raise
            
            print(f"TaskMan-SV initialized successfully")
            
        except Exception as e:
            print(f"{Fore.RED}Error during initialization: {str(e)}")
            print(f"Current user: {os.getenv('USERNAME')}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Process user: {os.getlogin()}")
            raise

    def generate_key(self, password: str, salt: bytes = None) -> tuple:
        """Generate encryption key from password"""
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    def register_user(self, username: str, password: str) -> bool:
        """Register user"""
        try:
            user_file = os.path.join(self.users_dir, f"{username}.json")
            
            if os.path.exists(user_file):
                print(f"{Fore.RED}Username already exists!")
                return False
            
            # Generate salt and hash password
            salt = os.urandom(16)
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            # Generate encryption key
            key, key_salt = self.generate_key(password, salt)
            
            # Create user data
            user_data = {
                "username": username,
                "password": base64.b64encode(hashed).decode('utf-8'),
                "salt": base64.b64encode(salt).decode('utf-8'),
                "key_salt": base64.b64encode(key_salt).decode('utf-8')
            }
            
            # Write user data
            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error during registration: {str(e)}")
            return False

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user"""
        try:
            user_file = os.path.join(self.users_dir, f"{username}.json")
            
            if not os.path.exists(user_file):
                return False

            with open(user_file, 'r') as f:
                user_data = json.loads(f.read())
            
            stored_hash = base64.b64decode(user_data['password'].encode('utf-8'))
            
            if not bcrypt.checkpw(password.encode(), stored_hash):
                return False

            # Setup encryption
            key_salt = base64.b64decode(user_data['key_salt'].encode('utf-8'))
            self.key, _ = self.generate_key(password, key_salt)
            self.fernet = Fernet(self.key)
            self.user = username
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error during authentication: {str(e)}")
            return False

    def save_data(self, data: dict, data_type: str) -> bool:
        """Save data to JSON file"""
        file_path = os.path.join(self.data_dir, f"{self.user}_{data_type}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error saving data: {str(e)}")
            return False

    def load_data(self, data_type: str) -> dict:
        """Load data from JSON file"""
        file_path = os.path.join(self.data_dir, f"{self.user}_{data_type}.json")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error loading data: {str(e)}")
        return None

    def get_empty_data(self, data_type: str) -> dict:
        """Return empty data structure based on type"""
        today = date.today().isoformat()
        
        if data_type == "tasks":
            return {
                "date": today,
                "tasks": []
            }
        elif data_type == "notes":
            return {
                "modules": {},
                "last_modified": datetime.now().isoformat(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
        elif data_type == "fastnotes":
            return {
                "notes": [],
                "last_modified": datetime.now().isoformat(),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
        return {}

    def save_tasks(self, tasks: list, target_date: str = None) -> bool:
        """Save tasks with date-specific files"""
        if target_date is None:
            target_date = date.today().isoformat()
            
        task_data = {
            "date": target_date,
            "tasks": tasks,
            "last_modified": datetime.now().isoformat()
        }
        
        # Save to a date-specific file
        filename = f"{self.user}_tasks_{target_date}.enc"
        file_path = os.path.join(self.data_dir, "users", filename)
        
        encrypted_data = self.fernet.encrypt(json.dumps(task_data).encode())
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        return True
    
    def load_tasks(self, target_date: str = None) -> dict:
        """Load tasks and handle completed tasks"""
        if target_date is None:
            target_date = date.today().isoformat()

        # First try to load tasks for the specific date
        filename = f"{self.user}_tasks_{target_date}.enc"
        file_path = os.path.join(self.data_dir, "users", filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                task_data = json.loads(decrypted_data)
                
                # Add 'mode' field to existing tasks if missing
                if 'tasks' in task_data:
                    for task in task_data['tasks']:
                        if 'mode' not in task:
                            task['mode'] = 'custom'  # Set default mode for existing tasks
                
                return task_data
            except Exception as e:
                print(f"Error loading tasks: {str(e)}")
                return self.get_empty_data("tasks")
        
        # If loading today's tasks and file doesn't exist
        if target_date == date.today().isoformat():
            # Load yesterday's tasks to check for pending ones
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            yesterday_data = self.load_tasks(yesterday)
            
            if yesterday_data and "tasks" in yesterday_data:
                # Carry forward all incomplete tasks (any task that's not completed)
                incomplete_tasks = []
                for task in yesterday_data["tasks"]:
                    status = task.get("status", "").strip()
                    
                    # Check if task is completed by looking for completion indicators
                    # Using 'in' check on the original status to catch various completion formats
                    is_completed = (
                        "Completed" in status or 
                        "completed" in status.lower() or
                        "✅" in status
                    )
                    
                    # Carry forward any task that is NOT completed
                    if not is_completed:
                        # Reset status for carried forward tasks to Pending if they were In Progress or Interrupted
                        if "In Progress" in status or "Interrupted" in status:
                            task["status"] = f"{Fore.YELLOW}Pending"
                        
                        # CRITICAL FIX: Reset daily tracking data for carried-forward tasks
                        # This ensures timer and work hours start fresh each day
                        task["actual_time_worked"] = 0  # Reset work time tracking
                        task["work_sessions"] = []  # Clear previous day's work sessions
                        
                        # Clear timing-related fields that should reset daily
                        timing_fields_to_clear = [
                            "session_start_time", "last_update_time", "last_auto_save",
                            "start_time", "end_time", "pause_start_time"
                        ]
                        for field in timing_fields_to_clear:
                            if field in task:
                                del task[field]
                        
                        # Handle Pomodoro task reset
                        if task.get('mode') == 'pomodoro' and 'pomodoro_settings' in task:
                            # Reset Pomodoro progress for the new day while preserving settings
                            task['pomodoro_settings']['current_pomodoro'] = 0
                            task['pomodoro_history'] = []  # Clear yesterday's pomodoro history
                            
                            # Clear Pomodoro pause state
                            if 'paused_state' in task:
                                del task['paused_state']
                        
                        # Clear custom task remaining time and pause state
                        if 'remaining' in task:
                            del task['remaining']
                        
                        incomplete_tasks.append(task)
                
                # Ensure all tasks have the 'mode' field
                for task in incomplete_tasks:
                    if 'mode' not in task:
                        task['mode'] = 'custom'
                
                # Add carry-forward indicator for display purposes
                for task in incomplete_tasks:
                    task['carried_forward'] = True
                
                return {
                    "date": target_date,
                    "tasks": incomplete_tasks
                }
        
        return self.get_empty_data("tasks")
    
    def save_notes(self, notes_data: dict) -> bool:
        """Save notes modules"""
        if not isinstance(notes_data, dict):
            notes_data = {"modules": {}}
        
        if "modules" not in notes_data:
            notes_data["modules"] = {}
            
        notes_data["last_modified"] = datetime.now().isoformat()
        return self.save_data(notes_data, "notes")

    def load_notes(self) -> dict:
        """Load notes modules"""
        notes_data = self.load_data("notes")
        if not notes_data or not isinstance(notes_data, dict):
            return self.get_empty_data("notes")
        
        # Ensure required structure exists
        if "modules" not in notes_data:
            notes_data["modules"] = {}
        if "metadata" not in notes_data:
            notes_data["metadata"] = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        
        return notes_data

    def save_fastnotes(self, fastnotes: list) -> bool:
        """Save fast notes"""
        notes_data = {
            "notes": fastnotes if isinstance(fastnotes, list) else [],
            "last_modified": datetime.now().isoformat(),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        return self.save_data(notes_data, "fastnotes")

    def load_fastnotes(self) -> list:
        """Load fast notes"""
        data = self.load_data("fastnotes")
        if not data or not isinstance(data, dict):
            data = self.get_empty_data("fastnotes")
        return data.get("notes", [])

    def save_report(self, report: list, date_str: str = None) -> bool:
        """Save report to a secure location with encryption"""
        if not self.user or not self.fernet:
            return False

        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(self.data_dir, "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            # Set proper permissions
            if os.name == 'nt':
                self._set_windows_permissions(reports_dir)
            else:
                os.chmod(reports_dir, 0o700)

        # Prepare report data with metadata
        report_data = {
            "date": date_str,
            "content": report,
            "generated_at": datetime.now().isoformat(),
            "username": self.user
        }

        try:
            # Encrypt and save the report
            json_data = json.dumps(report_data).encode()
            encrypted_data = self.fernet.encrypt(json_data)
            
            filename = f"report_{date_str}_{int(time.time())}.enc"
            file_path = os.path.join(reports_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set proper permissions for the report file
            if os.name == 'nt':
                self._set_windows_permissions(file_path)
            else:
                os.chmod(file_path, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving report: {str(e)}")
            return False

    def load_report(self, date_str: str) -> dict:
        """Load and decrypt a report for a specific date"""
        if not self.user or not self.fernet:
            return None

        reports_dir = os.path.join(self.data_dir, "reports")
        if not os.path.exists(reports_dir):
            return None

        try:
            # Find the most recent report file for the given date
            report_files = [f for f in os.listdir(reports_dir) 
                           if f.startswith(f"report_{date_str}_") and f.endswith('.enc')]
            
            if not report_files:
                return None

            # Get the most recent report
            latest_report = sorted(report_files)[-1]
            file_path = os.path.join(reports_dir, latest_report)

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"Error loading report: {str(e)}")
            return None

    def _set_windows_permissions(self, path):
        """Set Windows-specific file permissions"""
        try:
            import win32security
            import ntsecuritycon as con
            
            # Get current user's SID
            username = os.getenv('USERNAME')
            domain = os.getenv('USERDOMAIN')
            sid = win32security.LookupAccountName(domain, username)[0]
            
            # Create DACL with full control only for current user
            dacl = win32security.ACL()
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION,
                con.FILE_ALL_ACCESS,
                sid
            )
            
            # Set security on file/directory
            security_desc = win32security.SECURITY_DESCRIPTOR()
            security_desc.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION,
                security_desc
            )
        except Exception as e:
            print(f"Warning: Could not set Windows permissions: {str(e)}")

def display_auth_screen():
    """Display an attractive authentication screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""
{Fore.CYAN}╔═══════════════════════════════════════════╗
║             {Fore.GREEN}TASKMAN LOGIN{Fore.CYAN}             ║
╚═══════════════════════════════════════════╝
""")

def get_credentials(mode="login") -> tuple:
    """Get username and password with improved UI"""
    display_auth_screen()
    
    print(f"{Fore.YELLOW}{'Login' if mode == 'login' else 'Register'} to TASKMAN")
    print(f"{Fore.CYAN}{'=' * 40}")
    
    username = input(f"{Fore.CYAN}Username: {Fore.WHITE}").strip()
    password = getpass.getpass(f"{Fore.CYAN}Password: {Fore.WHITE}")
    
    return username, password

def setup_backend():
    """Initialize backend and handle authentication with improved UI"""
    backend = TaskmanBackend()
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        display_auth_screen()
        print(f"{Fore.CYAN}1. {Fore.WHITE}Login")
        print(f"{Fore.CYAN}2. {Fore.WHITE}Register")
        print(f"{Fore.CYAN}3. {Fore.WHITE}Exit")
        print(f"{Fore.CYAN}{'=' * 40}")
        
        choice = input(f"{Fore.GREEN}Choice: {Fore.WHITE}").strip()
        
        if choice == "1":
            username, password = get_credentials("login")
            if backend.authenticate(username, password):
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen for animation
                return backend
            attempts += 1
            print(f"{Fore.RED}Invalid credentials! {max_attempts - attempts} attempts remaining.")
            time.sleep(1)
            
        elif choice == "2":
            username, password = get_credentials("register")
            if backend.register_user(username, password):
                print(f"{Fore.GREEN}Registration successful! Please login.")
                
                # Security warning for password storage
                print(f"\n{Fore.YELLOW}⚠️  IMPORTANT PASSWORD WARNING ⚠️{Style.RESET_ALL}")
                print(f"{Fore.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{Fore.YELLOW}🔐 STORE YOUR PASSWORD CAREFULLY!")
                print(f"{Fore.WHITE}• Your data is encrypted with your password")
                print(f"{Fore.WHITE}• If you forget it, ALL data will be LOST forever")
                print(f"{Fore.WHITE}• We cannot recover your password or data")
                print(f"{Fore.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{Fore.CYAN}Please save your password in a secure location...")
                print()
                print()
                print()
                input(f"{Fore.GREEN}Press Enter to continue to login... {Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Username already exists!")
                time.sleep(1)
                
        elif choice == "3":
            exit(0)
            
        else:
            print(f"{Fore.RED}Invalid choice!")
            time.sleep(1)
    
    print(f"{Fore.RED}Too many failed attempts. Please try again later.")
    exit(1)