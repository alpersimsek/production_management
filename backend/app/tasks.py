import celery
from typing import Dict, List
import settings
from services import ProcessingConfig, MaskingMapService, PcapProcessingError, FileService
from database.session import Session
import time
from logger import logger
from charset_normalizer import from_path
from database.models import (
    User,
    File,
    FileStatus,
    ContentType,
)
from storage import FileStorage
import magic
import os
import pathlib
import tempfile


app = celery.Celery(
    "gdpr_backend",
    broker=settings.CELERY_BROKER,
    backend=None  # optional: can use rabbitMQ ("rpc://") or Redis for results
)

app.conf.update(
    # CRITICAL: Cancel long-running tasks on connection loss to prevent redelivery of completed tasks
    # Without this setting, completed long-duration tasks can be redelivered to the queue when workers
    # lose connection, causing duplicate processing of already finished work.
    worker_cancel_long_running_tasks_on_connection_loss=True,
)

def _process_file(config: ProcessingConfig, storage: FileStorage, file_id: str, file_service: FileService) -> None:
    """Process a single file with the given configuration."""
    db_session = file_service.session
    file_obj = file_service.get_by_id(file_id)

    file_obj.status = FileStatus.IN_PROGRESS
    content_type = file_obj.content_type
    src = storage.get(file_id)
    
    if not file_obj:
        logger.error({
            "event": "process_failed",
            "file_id": file_id,
            "error": "File not found",
        })
        file_obj.status = FileStatus.ERROR
        raise FileNotFoundError(f"File with id {file_id} not found.")

    if not src.exists():
        logger.error({
            "event": "process_failed",
            "file_id": file_id,
            "filename": file_obj.filename,
            "error": f"Source file does not exist: {src}",
        })
        file_obj.status = FileStatus.ERROR
        raise FileNotFoundError(f"Source file does not exist: {src}")

    mime = magic.from_file(str(src), mime=True)
    file_type_description = magic.from_file(str(src))
    is_capture_file = mime == "application/vnd.tcpdump.pcap"
    logger.info({
        "event": "file_processing_started",
        "file_id": file_id,
        "filename": file_obj.filename,
        "content_type": file_type_description,
        "mime_type": mime,
        "file_type_description": file_type_description,
        "is_capture_file": is_capture_file,
    })

    processor = config.make_processor(content_type=content_type.value)

    base, ext = os.path.splitext(file_obj.filename)
    # ext = ext.lower()
    # if ext in ['.txt', '.csv', '.pcap', '.json', '.log']:
    if ext is not None:
        dst_filename = f"{base}_masked{ext}" if not base.endswith('_masked') else file_obj.filename
    else:
        file_type = storage.get_type(file_id)
        dst_filename = f"{base}_masked.pcap" if file_type == storage.T_PCAP else f"{base}_masked"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_masked{ext}", dir=storage.base_dir) as temp_file:
        temp_dst = pathlib.Path(temp_file.name)
        try:
            if content_type == ContentType.TEXT:
                encoding = storage.get_encoding(src)

                done_size = 0
                unreported = 0
                total_size = storage.get_size(file_id)
                max_report_num = int(total_size / settings.REPORT_STEP)
                process_time = 0
                report_count = 1
                with temp_dst.open("w", newline="", encoding=encoding) as f_dst:
                    with src.open("r", newline="", encoding=encoding) as f_src:
                        operation_time = time.time()
                        for chunk in processor.feed(f_src):
                            f_dst.write(chunk)
                            chunk_bytes_len = len(chunk.encode())
                            done_size += chunk_bytes_len
                            unreported += chunk_bytes_len
                            if unreported >= settings.REPORT_STEP:
                                process_time += time.time() - operation_time
                                average_process_time = process_time / report_count
                                operation_time = time.time()
                                chunk_num = max_report_num - report_count
                                time_remain = int(chunk_num * average_process_time)
                                file_obj.completed_size = done_size
                                file_obj.time_remaining = time_remain
                                db_session.commit()
                                logger.debug({
                                    "event": "progress_update",
                                    "file_id": file_id,
                                    "completed_size": done_size,
                                    "time_remaining": time_remain,
                                })
                                report_count += 1
                                unreported = 0

            elif content_type == ContentType.PCAP:
                done_size = 0
                total_size = storage.get_size(file_id)
                operation_time = time.time()
                for item in processor.feed(src):
                    if len(item) != 3:
                        logger.error({
                            "event": "invalid_packet_tuple",
                            "file_id": file_id,
                            "filename": file_obj.filename,
                            "tuple": str(item),
                            "expected": "(ts, output_path, linktype)",
                        })
                        raise PcapProcessingError(f"Invalid packet tuple: {item}")
                    _ts, output_path, _linktype = item
                    done_size = os.path.getsize(output_path)
                    os.rename(output_path, temp_dst)
                    logger.info({
                        "event": "pcap_processed",
                        "file_id": file_id,
                        "filename": file_obj.filename,
                        "total_size": done_size,
                        "output_file": str(temp_dst),
                    })
                    break
                file_obj.completed_size = done_size
                file_obj.time_remaining = 0
                db_session.commit()

            else:
                logger.error({
                    "event": "process_failed",
                    "file_id": file_id,
                    "filename": file_obj.filename,
                    "error": f"Unsupported content type: {content_type}",
                })
                raise PcapProcessingError(f"Unsupported content type: {content_type}")

            logger.info({
                "event": "file_processed",
                "file_id": file_id,
                "filename": file_obj.filename,
                "new_filename": dst_filename,
                "src_path": str(temp_dst),
                "dst_path": str(src),
            })
            temp_dst.rename(src)
            file_obj.filename = dst_filename
            file_obj.status = FileStatus.DONE
            file_obj.completed_size = done_size
            file_obj.time_remaining = 0
            file_obj.file_size = storage.get_size(file_id)
            db_session.commit()

        except Exception as ex:
            logger.error({
                "event": "process_error",
                "file_id": file_id,
                "filename": file_obj.filename,
                "error": str(ex),
            })
            path = pathlib.Path(file_obj.filename)
            path_parts = list(path.parts)
            path_parts[-1] = "failed_" + path_parts[-1]
            filename = "/".join(path_parts)
            file_obj.status = FileStatus.ERROR
            file_obj.filename = filename
            if temp_dst.exists():
                temp_dst.unlink()
            db_session.commit()
            raise RuntimeError(f"Error processing file {file_id}: {str(ex)}")

@app.task
def process_file(files: Dict[str, str], rules_configs: Dict[str, List], user_id: str):
        """Preprocess a list of files with the given rules configurations."""

        db_session = Session()
        parent = None # if its archive file, get a handle for post processing / repack
        
        try:
            storage = FileStorage(settings.DATA_DIR)
            user = db_session.query(User).filter(User.id == user_id).first()
            file_service = FileService(db_session, user, storage)
            start_time = time.time()
            configs = {}
            for file_id, preset_id in files.items():
                config = configs.get(preset_id)
                if not config:
                    config = ProcessingConfig(
                        rules_config=rules_configs[preset_id],
                        maskingMapService=MaskingMapService(db_session),
                    )
                    configs[preset_id] = config
                _process_file(config, storage, file_id, file_service)

                processed_file = file_service.get_by_id(file_id)
                if processed_file and processed_file.archive_id:
                    parent = processed_file.archive
                    if parent.status == FileStatus.IN_PROGRESS:
                        processed_size = sum(
                            child.file_size
                            for child in parent.archive_files
                            if child.status == FileStatus.DONE
                        )
                        parent.completed_size = processed_size
                        if processed_size > 0:
                            elapsed = time.time() - start_time
                            if elapsed > 0:
                                rate = processed_size / elapsed
                                remaining = parent.extracted_size - processed_size
                                parent.time_remaining = (
                                    int(remaining / rate) if rate > 0 else 0
                                )
                        db_session.commit()
                        logger.debug({
                            "event": "archive_progress_updated",
                            "file_id": file_id,
                            "parent_id": parent.id,
                            "completed_size": parent.completed_size,
                            "time_remaining": parent.time_remaining,
                        })
                
            # file.content_type == ContentType.ARCHIVE
            if parent:
                storage.repack(parent)
                parent.status = FileStatus.DONE
                parent.completed_size = parent.file_size
                parent.time_remaining = 0
                db_session.commit()
                for child in parent.archive_files:
                    file_service.delete_file(child.id)
                logger.info({
                    "event": "archive_repacked",
                    "file_id": parent.id,
                    "filename": parent.filename,
                })

        except Exception as e:
            file_ids = list(files.keys())
            logger.error({
                "event": "preprocess_failed",
                "file_ids": file_ids,
                "error": str(e),
            }, extra={"context": {"file_id": file_ids}})

            db_session.query(File).filter(
                (File.status != FileStatus.DONE) & File.id.in_(file_ids)
            ).update({"status": FileStatus.ERROR})
            db_session.commit()
            raise RuntimeError(f"Preprocessing failed: {str(e)}")
        
        finally:
            db_session.close()