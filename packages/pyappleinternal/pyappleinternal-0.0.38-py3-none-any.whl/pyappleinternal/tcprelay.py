import subprocess
import os
import signal
from pyappleinternal.assign_ports import PortManager
from pyappleinternal.utils import get_tcprelay_path
class tcprelay():
    def __init__(self, udid):
        super().__init__()
        self.udid = udid
        self.status=False
        self.PortManager=PortManager()
        self.tcprelay_path=get_tcprelay_path()
        self.env = os.environ.copy()
        self.env["PYTHONUNBUFFERED"] = "1"
        self.proc = None
        self.command = None

    def start(self,local="0.0.0.0",udid=None, taskid=None, port=None, callback=None):
        try:
            self.status=True
            self.taskid=taskid
            self.proc = subprocess.Popen(
                f"'{self.tcprelay_path}' --serialnumber {self.udid} --portoffset {port-22} 22",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                universal_newlines=True,
                bufsize=1,
                env=self.env,
                shell=True,
                preexec_fn=os.setsid
            )
            while True:
                stdout_line = self.proc.stdout.readline()
                stderr_line = self.proc.stderr.readline()
                if not stdout_line and not stderr_line and self.proc.poll() is not None:
                    break
                if stdout_line:
                    if "Exiting thread to connect" in stdout_line.strip():
                        if callable(callback):
                            callback({"disconnect":"Connection closed by the peer."})
                    if "Could not connect" in stderr_line.strip():
                        if callable(callback):
                            callback({"connect_error":"failed to connect to port: 22"})
                if stderr_line:
                    if "Exiting thread to connect" in stderr_line.strip():
                        if callable(callback):
                            callback({"disconnect":"Connection closed by the peer."})
                    if "Could not connect" in stderr_line.strip():
                        if callable(callback):
                            callback({"connect_error":"failed to connect to port: 22"})     
        except Exception as e:
            print(e)
    
    def stop(self):
        try:
            if self.proc and self.status:
                self.status=False
                os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)
                self.PortManager.deallocate_port(self.taskid,self.udid)
        except:pass

