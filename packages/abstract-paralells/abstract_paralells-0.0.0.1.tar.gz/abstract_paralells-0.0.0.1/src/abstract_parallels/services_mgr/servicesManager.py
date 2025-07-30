#!/usr/bin/env python3
"""
remote_service_viewer.py (PyQt5 service viewer with start, restart, reload, stop, enable/disable, and logs)
"""
import os
import paramiko
import subprocess
from datetime import datetime
from abstract_utilities import *
from abstract_utilities.cmd_utils import *
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, 
                            QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QHBoxLayout, QTextEdit)
from PyQt5.QtCore import Qt

service_copies_path = "/mnt/24T/service_copys"
os.makedirs(service_copies_path, exist_ok=True)
global_pids = set()

class SSHClient:
    def __init__(self, hostname, username, password=None, key_path=None, sudo_password=None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_path = key_path
        self.sudo_password = sudo_password
        self.connect()

    def connect(self):
        try:
            if self.key_path:
                self.client.connect(self.hostname, username=self.username, key_filename=self.key_path)
            else:
                self.client.connect(self.hostname, username=self.username, password=self.password)
        except Exception as e:
            raise ConnectionError(f"SSH connection failed: {str(e)}")

    def run_command(self, command, use_sudo=False):
        if use_sudo and self.sudo_password:
            command = f"echo {self.sudo_password} | sudo -S {command}"
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=10)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error and "incorrect password" in error.lower():
                raise PermissionError("Sudo password incorrect")
            return output, error
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {str(e)}")

    def close(self):
        self.client.close()

def is_active(item, ssh_client):
    item_path = f"/etc/systemd/system/{item}"
    output, _ = ssh_client.run_command(f"[ -f {item_path} ] && echo exists", use_sudo=True)
    if output != "exists":
        return False
    try:
        output, _ = ssh_client.run_command(f"systemctl is-active {item}", use_sudo=True)
        return output.strip() == "active"
    except:
        return False

def get_unit_property(unit, prop, ssh_client):
    output, _ = ssh_client.run_command(f"systemctl show {unit} --property={prop}", use_sudo=True)
    if output:
        return output.split("=", 1)[-1]
    return None

def get_pid_info(pid, ssh_client, global_pids=None):
    global_pids = global_pids or set()
    active, cpu, mem, all_children = False, 0, 0, []
    if pid and is_number(pid) and int(pid) not in global_pids:
        pid = int(pid)
        global_pids.add(pid)
        active = True
        try:
            output, _ = ssh_client.run_command(f"ps -p {pid}")
            if str(pid) not in output:
                return False, 0, 0, [], global_pids
            output, _ = ssh_client.run_command(f"ps -p {pid} -o %cpu,rss")
            lines = output.splitlines()
            if len(lines) > 1:
                cpu = float(lines[1].split()[0])
                mem = float(lines[1].split()[1]) / 1024
            output, _ = ssh_client.run_command(f"ps --ppid {pid} -o pid")
            child_pids = [int(p) for p in output.splitlines()[1:] if p.strip() and is_number(p)]
            for child_pid in child_pids:
                if child_pid not in global_pids:
                    child_active, child_cpu, child_mem, child_children, global_pids = get_pid_info(child_pid, ssh_client, global_pids)
                    mem += child_mem
                    child_js = {"pid": child_pid, "active": child_active, "cpu": child_cpu, "mem": child_mem, "all_children": child_children}
                    all_children.append(child_js)
        except:
            pass
    return active, cpu, mem, all_children, global_pids

def run_systemctl(item, ssh_client, command):
    if item and command:
        try:
            ssh_client.run_command(f"systemctl {command} {item}", use_sudo=True)
        except Exception as e:
            raise RuntimeError(f"Failed to run systemctl {command}: {str(e)}")

def get_refined_exec_start(exec_parts, info):
    for i, part in enumerate(exec_parts):
        if part.endswith("gunicorn"):
            info["gunicorn"] = True
        elif part.endswith(".py") or part.endswith(".ts"):
            info["execution_path"] = os.path.join(info["directory"], os.path.basename(part))
        elif part.startswith("--bind") and i + 1 < len(exec_parts) and ":" in exec_parts[i+1]:
            ip, port = exec_parts[i+1].split(":")
            info["ip_add"] = ip
            info["port"] = port
        elif part.startswith('--workers') and i + 1 < len(exec_parts):
            workers = exec_parts[i+1]
            info["workers"] = float(workers)
    return info

def format_uptime(timestamp_str):
    if not timestamp_str:
        return "N/A"
    try:
        start_time = datetime.strptime(timestamp_str, "%a %Y-%m-%d %H:%M:%S %Z")
        current_time = datetime.now(start_time.tzinfo)
        uptime = current_time - start_time
        seconds = int(uptime.total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    except:
        return "N/A"

class ServiceInfo:
    def __init__(self, name, service_copy_path, global_pids, ssh_client):
        self.name = name
        self.copy_path = service_copy_path
        self.global_pids = global_pids or set()
        self.ssh_client = ssh_client
        self.restart_count = 0
        self.info = {
            "name": name,
            "active": False,
            "enabled": False,
            "directory": None,
            "ExecStart": None,
            "execution_path": None,
            "conditions": {},
            "workers": 1,
            "cpu": 0,
            "mem": 0,
            "pid": None,
            "all_children": [],
            "ip_add": None,
            "port": None,
            "uptime": "N/A",
            "restart_count": 0
        }

    def load_metadata(self):
        if not self.ssh_client.run_command(f"[ -f /etc/systemd/system/{self.name} ] && echo exists", use_sudo=True)[0]:
            return
        self.info["ExecStart"] = get_unit_property(self.name, "ExecStart", self.ssh_client)
        self.info["directory"] = get_unit_property(self.name, "WorkingDirectory", self.ssh_client)
        self.info["uptime"] = format_uptime(get_unit_property(self.name, "ActiveEnterTimestamp", self.ssh_client))
        enabled_state = get_unit_property(self.name, "UnitFileState", self.ssh_client)
        self.info["enabled"] = enabled_state == "enabled"

    def parse_exec(self):
        if self.info["ExecStart"]:
            exec_parts = self.info["ExecStart"].split()
            self.info = get_refined_exec_start(exec_parts, self.info)

    def check_resources(self):
        pid = get_unit_property(self.name, "MainPID", self.ssh_client)
        self.info["active"], self.info["cpu"], self.info["mem"], self.info["all_children"], self.global_pids = get_pid_info(pid, self.ssh_client, self.global_pids)
        return self.global_pids

    def start(self):
        run_systemctl(self.name, self.ssh_client, "start")

    def restart(self):
        run_systemctl(self.name, self.ssh_client, "restart")
        self.restart_count += 1
        self.info["restart_count"] = self.restart_count

    def reload(self):
        run_systemctl(self.name, self.ssh_client, "reload")

    def stop(self):
        run_systemctl(self.name, self.ssh_client, "stop")

    def enable(self, enable=True):
        command = "enable" if enable else "disable"
        run_systemctl(self.name, self.ssh_client, command)
        self.info["enabled"] = enable

    def get_logs(self, lines=100):
        output, _ = self.ssh_client.run_command(f"journalctl -u {self.name} -n {lines}", use_sudo=True)
        return output

class LogViewerDialog(QDialog):
    def __init__(self, service_name, logs, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Logs for {service_name}")
        self.setGeometry(200, 200, 800, 600)
        layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setText(logs)
        layout.addWidget(self.log_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

class ConnectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Connect to Server")
        self.setFixedSize(400, 250)
        layout = QFormLayout()

        self.hostname = QLineEdit('192.168.0.100')##
        self.username = QLineEdit('solcatcher')#'solcatcher'#
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.key_path = QLineEdit('/home/computron/.ssh/config')
        self.sudo_password = QLineEdit()
        self.sudo_password.setEchoMode(QLineEdit.Password)

        layout.addRow("Hostname:", self.hostname)
        layout.addRow("Username:", self.username)
        layout.addRow("Password (optional):", self.password)
        layout.addRow("SSH Key Path (optional):", self.key_path)
        layout.addRow("Sudo Password (optional):", self.sudo_password)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_connection_details(self):
        return {
            "hostname": self.hostname.text().strip(),
            "username": self.username.text().strip(),
            "password": self.password.text() or None,
            "key_path": self.key_path.text().strip() or None,
            "sudo_password": self.sudo_password.text() or None
        }

class ServiceViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ssh_client = None
        self.services_js = {}
        self.total_mem = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Remote Systemd Service Viewer")
        self.setGeometry(100, 100, 1400, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Service", "Active", "PID", "CPU (%)", "Memory (MB)", 
            "Workers", "Host:Port", "Restart Count", "Uptime", "Actions", "Logs"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table)

        refresh_btn = QPushButton("Refresh Services")
        refresh_btn.clicked.connect(self.load_services)
        layout.addWidget(refresh_btn)

        connect_btn = QPushButton("Connect to Server")
        connect_btn.clicked.connect(self.connect_to_server)
        layout.addWidget(connect_btn)

    def connect_to_server(self):
        dialog = ConnectionDialog()
        if dialog.exec_():
            details = dialog.get_connection_details()
            try:
                self.ssh_client = SSHClient(**details)
                self.load_services()
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", str(e))

    def load_services(self):
        if not self.ssh_client:
            QMessageBox.critical(self, "Error", "Not connected to a server. Please connect first.")
            return

        global global_pids
        global_pids = set()
        old_services = self.services_js
        self.services_js = {}
        self.total_mem = 0
        self.table.setRowCount(0)

        try:
            output, _ = self.ssh_client.run_command("ls /etc/systemd/system/*.service", use_sudo=True)
            services = [os.path.basename(path) for path in output.splitlines() if path.endswith('.service')]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list services: {str(e)}")
            return

        for service in services:
            svc_path = os.path.join(service_copies_path, service)
            svc = ServiceInfo(service, svc_path, global_pids, self.ssh_client)
            if service in old_services:
                svc.restart_count = old_services[service].get("restart_count", 0)
            svc.load_metadata()
            global_pids = svc.check_resources()
            svc.parse_exec()
            svc.info["restart_count"] = svc.restart_count
            self.services_js[service] = svc.info
            if svc.info["active"] or svc.info["enabled"]:
                self.add_service_to_table(svc)

        self.table.setRowCount(self.table.rowCount() + 1)
        self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(f"Total RAM: {self.total_mem:.2f} MB"))
        self.table.item(self.table.rowCount() - 1, 0).setFlags(Qt.ItemIsEnabled)


class ServiceViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ssh_client = None
        self.services_js = {}
        self.total_mem = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Remote Systemd Service Viewer")
        self.setGeometry(100, 100, 1400, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Service", "Active", "PID", "CPU (%)", "Memory (MB)", 
            "Workers", "Host:Port", "Restart Count", "Uptime", "Actions", "Logs"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table)

        refresh_btn = QPushButton("Refresh Services")
        refresh_btn.clicked.connect(self.load_services)
        layout.addWidget(refresh_btn)

        connect_btn = QPushButton("Connect to Server")
        connect_btn.clicked.connect(self.connect_to_server)
        layout.addWidget(connect_btn)

    def connect_to_server(self):
        dialog = ConnectionDialog()
        if dialog.exec_():
            details = dialog.get_connection_details()
            try:
                self.ssh_client = SSHClient(**details)
                self.load_services()
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", str(e))

    def load_services(self):
        if not self.ssh_client:
            QMessageBox.critical(self, "Error", "Not connected to a server. Please connect first.")
            return

        global global_pids
        global_pids = set()
        old_services = self.services_js
        self.services_js = {}
        self.total_mem = 0
        self.table.setRowCount(0)

        try:
            output, _ = self.ssh_client.run_command("ls /etc/systemd/system/*.service", use_sudo=True)
            services = [os.path.basename(path) for path in output.splitlines() if path.endswith('.service')]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list services: {str(e)}")
            return

        for service in services:
            svc_path = os.path.join(service_copies_path, service)
            svc = ServiceInfo(service, svc_path, global_pids, self.ssh_client)
            if service in old_services:
                svc.restart_count = old_services[service].get("restart_count", 0)
            svc.load_metadata()
            global_pids = svc.check_resources()
            svc.parse_exec()
            svc.info["restart_count"] = svc.restart_count
            self.services_js[service] = svc.info
            if svc.info["active"] or svc.info["enabled"]:
                self.add_service_to_table(svc)

        self.table.setRowCount(self.table.rowCount() + 1)
        self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(f"Total RAM: {self.total_mem:.2f} MB"))
        self.table.item(self.table.rowCount() - 1, 0).setFlags(Qt.ItemIsEnabled)

    def add_service_to_table(self, svc):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(svc.name))
        self.table.setItem(row, 1, QTableWidgetItem("Yes" if svc.info["active"] else "No"))
        self.table.setItem(row, 2, QTableWidgetItem(str(svc.info["pid"]) if svc.info["pid"] else ""))
        self.table.setItem(row, 3, QTableWidgetItem(f"{svc.info['cpu']:.2f}"))
        self.table.setItem(row, 4, QTableWidgetItem(f"{svc.info['mem']:.2f}"))
        self.table.setItem(row, 5, QTableWidgetItem(str(svc.info["workers"])))
        host_port = f"{svc.info['ip_add']}:{svc.info['port']}" if svc.info["ip_add"] and svc.info["port"] else "N/A"
        self.table.setItem(row, 6, QTableWidgetItem(host_port))
        self.table.setItem(row, 7, QTableWidgetItem(str(svc.info["restart_count"])))
        self.table.setItem(row, 8, QTableWidgetItem(svc.info["uptime"]))

        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)

        start_btn = QPushButton("Start")
        start_btn.clicked.connect(lambda: self.execute_action(svc.start, "start", svc))
        action_layout.addWidget(start_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.clicked.connect(lambda: self.execute_action(svc.restart, "restart", svc))
        action_layout.addWidget(restart_btn)

        reload_btn = QPushButton("Reload")
        reload_btn.clicked.connect(lambda: self.execute_action(svc.reload, "reload", svc))
        action_layout.addWidget(reload_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(lambda: self.execute_action(svc.stop, "stop", svc))
        action_layout.addWidget(stop_btn)

        enable_btn = QPushButton("Disable" if svc.info["enabled"] else "Enable")
        enable_btn.clicked.connect(lambda: self.execute_action(lambda: svc.enable(not svc.info["enabled"]), 
                                                             "enable/disable", svc))
        action_layout.addWidget(enable_btn)

        self.table.setCellWidget(row, 9, action_widget)

        logs_btn = QPushButton("Logs")
        logs_btn.clicked.connect(lambda: self.show_logs(svc))
        self.table.setCellWidget(row, 10, logs_btn)

        for col in range(9):
            if self.table.item(row, col):
                self.table.item(row, col).setFlags(Qt.ItemIsEnabled)
        
        if svc.info["active"]:
            self.total_mem += svc.info["mem"]

    def execute_action(self, action, action_name, svc):
        try:
            action()
            QMessageBox.information(self, "Success", f"Service {svc.name} {action_name} successful.")
            self.load_services()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to {action_name} {svc.name}: {str(e)}")

    def show_logs(self, svc):
        try:
            logs = svc.get_logs()
            dialog = LogViewerDialog(svc.name, logs, self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch logs for {svc.name}: {str(e)}")

    def closeEvent(self, event):
        if self.ssh_client:
            self.ssh_client.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ServiceViewerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
