Large-File-Detector (Python Daemon and Systemd Service)This project is the solution to a practical exam requirement for the University of Ferrara (UNIFE) course "System, Network Administration and Cybersecurity" (or similar).The goal was to implement a robust, low-resource Python Daemon to monitor the filesystem periodically, coupled with a Systemd User Service for persistent, automatic execution in a modern Linux environment.🎯 Key Concepts DemonstratedSystem Daemon Implementation (Python): Design and implementation of a long-running, periodic background process using standard Python libraries (argparse, os, time).Filesystem Traversal: Efficient recursive scanning of large directory trees using os.walk to inspect file metadata.Robust Argument Parsing & Validation: Strict command-line argument handling (argparse) and validation (path existence, absolute path check, positive integer checks) to ensure daemon stability.Low-Level I/O: Safe append-mode file logging (open(..., "a")) for creating persistent log files.Systemd Integration (User Service): Configuration of a .service unit to manage the daemon's lifecycle, ensuring it:Starts automatically at system boot (WantedBy=default.target).Recovers automatically from failures (Restart=always).Runs in the user context, using environment variables like %h (Home Directory).📂 Project FilesFileDescriptionapp.pyThe core Python script that implements the periodic filesystem scanning, validation, size check, and logging loop (time.sleep).large-file-detector.serviceThe Systemd User Unit file (~/.config/systemd/user/) responsible for executing app.py as a system service.⚙️ Execution and Deployment1. Python Script UsageThe script requires exactly four mandatory arguments:Bash$ python3 app.py --target <ABSOLUTE_PATH> --size <BYTES> --interval <SECONDS> --log <LOG_DIR_PATH>
Example:Bash# Monitor the user's documents for files >= 10MB (10485760 bytes) every 600 seconds (10 minutes), logging to the home directory.
$ python3 app.py \
    --target /home/user/Documents \
    --size 10485760 \
    --interval 600 \
    --log /home/user/
2. Systemd Service DeploymentThe service unit large-file-detector.service is configured to run automatically using specific parameters:ParameterValueDescription--target%h/docsThe target directory to scan (e.g., ~/docs).--size100Files must be >= 100 bytes to be logged.--interval300The scan is repeated every 300 seconds (5 minutes).--log%hThe log file (large-file-detector.log) is saved in the user's home directory.Service Installation CommandsTo deploy and start the daemon as a Systemd User Service:Bash# Ricarica i file di configurazione di systemd
systemctl --user daemon-reload

# Abilita l'avvio all'avvio del sistema
systemctl --user enable large-file-detector.service

# Avvia il servizio immediatamente
systemctl --user start large-file-detector.service

# Visualizza lo stato e i log
journalctl --user -u large-file-detector.service -f
