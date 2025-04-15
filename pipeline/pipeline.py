from prefect import flow, task
from prefect.logging import get_run_logger
from datetime import datetime

# Task di estrazione metadati
@task(retries=3, retry_delay_seconds=5)
def estrai_metadati():
    logger = get_run_logger()
    logger.info("🔍 Estrazione metadati in corso...")

    # Simuliamo l'estrazione da un database o API
    metadati = {"titolo": "Documento 1", "autore": "Alice", "timestamp": str(datetime.utcnow())}

    logger.info(f"✅ Metadati estratti: {metadati}")
    return metadati

# Task di trasformazione metadati
@task
def trasforma_metadati(metadati):
    logger = get_run_logger()
    logger.info("🔄 Trasformazione metadati...")

    # Esempio di trasformazione: rendiamo il nome dell'autore in maiuscolo
    metadati["autore"] = metadati["autoreeeee"].upper()

    logger.info(f"✅ Metadati trasformati: {metadati}")
    return metadati

# Task di caricamento metadati
@task
def carica_metadati(metadati):
    logger = get_run_logger()
    logger.info("📤 Caricamento metadati finali...")

    # In un caso reale, potremmo salvare i dati su un database o file
    logger.info(f"✅ Metadati caricati: {metadati}")

# Definiamo il flow principale
@flow(name="Pipeline Metadati")
def pipeline_metadati():
    logger = get_run_logger()
    logger.info("🚀 Avvio della pipeline di trasformazione metadati")

    metadati = estrai_metadati()
    metadati_trasformati = trasforma_metadati(metadati)
    carica_metadati(metadati_trasformati)

    logger.info("🎉 Pipeline completata con successo!")

# Avvia la pipeline se il file viene eseguito direttamente
if __name__ == "__main__":
    pipeline_metadati()