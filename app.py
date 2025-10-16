# nome e cognome: danilo poli
# matricola: 185924
# path: ~/large-file-detector/app.py

import argparse
import os
import sys
import time
from pathlib import Path

# Funzione per eseguire la scansione e il logging
def check_for_large_files(target_dir: Path, min_size: int, log_path: Path):
    """
    Scansiona ricorsivamente la directory target e logga i file >= min_size.
    """
    
    # Prepara il percorso completo del file di log
    log_file_path = log_path / "large-file-detector.log"
    
    # Scrittura in append nel file di log
    try:
        with open(log_file_path, "a") as log_file:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting scan of {target_dir} for files >= {min_size} bytes...")

            # Percorri l'albero delle directory in modo ricorsivo
            for root, dirs, files in os.walk(target_dir):
                for file_name in files:
                    file_path = Path(root) / file_name
                    
                    try:
                        # Verifica se è un file regolare e calcola la dimensione
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            
                            # Confronta la dimensione con la soglia
                            if size >= min_size:
                                absolute_path = str(file_path.resolve())
                                
                                # Scrive il percorso assoluto nel log
                                log_file.write(f"{absolute_path}\n")
                                print(f"  -> Logged: {absolute_path} ({size} bytes)")
                                
                    except OSError as e:
                        # Ignora o segnala errori di permessi/accesso
                        print(f"Warning: Cannot access file {file_path}: {e}", file=sys.stderr)
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scan finished. Sleeping...")
            
    except IOError as e:
        print(f"FATAL: Error writing to log file {log_file_path}: {e}", file=sys.stderr)
        # Non uscire se c'è un errore di I/O, ma stampalo.
        # In un demone, l'uscita causa il riavvio se 'Restart=always' è impostato.
        
    except Exception as e:
        print(f"An unexpected error occurred during scan: {e}", file=sys.stderr)


def main():
    # 1. Parsing degli argomenti
    parser = argparse.ArgumentParser(
        description="A daemon script to periodically detect files larger than a specified size in a target directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Percorso assoluto della directory da monitorare (e sottodirectory)."
    )
    parser.add_argument(
        "--size",
        type=int,
        required=True,
        help="Dimensione minima del file in byte (intero positivo) da segnalare."
    )
    parser.add_argument(
        "--interval",
        type=int,
        required=True,
        help="Intervallo tra i controlli in secondi (intero positivo)."
    )
    parser.add_argument(
        "--log",
        type=str,
        required=True,
        help="Percorso della directory dove salvare 'large-file-detector.log'."
    )
    
    args = parser.parse_args()
    
    target_path = Path(args.target)
    log_dir_path = Path(args.log)
    
    # 2. Validazione degli input
    try:
        # Validazione --target
        if not target_path.is_absolute():
            raise ValueError(f"Target path '{args.target}' is not absolute.")
        if not target_path.exists():
            raise FileNotFoundError(f"Target path '{args.target}' does not exist.")
        if not target_path.is_dir():
            raise NotADirectoryError(f"Target path '{args.target}' is not a directory.")
        
        # Validazione --size e --interval
        if args.size <= 0:
            raise ValueError(f"Size threshold '{args.size}' must be a positive integer.")
        if args.interval <= 0:
            raise ValueError(f"Interval '{args.interval}' must be a positive integer.")
            
        # Validazione --log
        if not log_dir_path.exists():
            # Tenta di creare la directory se non esiste (buona pratica, anche se non strettamente richiesto)
            os.makedirs(log_dir_path, exist_ok=True)
            print(f"Created log directory at: {log_dir_path}")

        if not log_dir_path.is_dir():
            raise NotADirectoryError(f"Log path '{args.log}' is not a directory.")

    except (ValueError, FileNotFoundError, NotADirectoryError) as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Loop del demone
    print(f"Large File Detector started. Monitoring {target_path} every {args.interval} seconds.")
    print(f"Log file will be saved in: {log_dir_path / 'large-file-detector.log'}")
    
    # Il ciclo infinito necessario per un demone periodico
    while True:
        try:
            check_for_large_files(target_path, args.size, log_dir_path)
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nScript terminated by user (Ctrl+C).")
            break
        except Exception as e:
            print(f"Main loop error: {e}", file=sys.stderr)
            # Attende prima di riprovare (utile in caso di errori temporanei)
            time.sleep(args.interval)

if __name__ == "__main__":
    main()

