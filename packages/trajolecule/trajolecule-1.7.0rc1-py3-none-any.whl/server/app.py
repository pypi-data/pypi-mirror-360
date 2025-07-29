import inspect
import logging
import os
import socket
import threading
import time
import traceback
import webbrowser
from contextlib import closing
from urllib.request import urlopen

import pydash as py_
import uvicorn
from easytrajh5.fs import get_time_str, tic, toc, dump_yaml
from fastapi import FastAPI, File, UploadFile
from path import Path
from rich.pretty import pretty_repr
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles

this_dir = Path(__file__).parent

logger = logging.getLogger(__name__)


def make_app(config):
    from server import handlers

    logger.info("initialize handlers")
    handlers.init(config)

    client_dir = this_dir / "client"
    data_dir = this_dir / "data"
    logger.info(f"client_dir: {client_dir}")
    logger.info(f"data_dir: {data_dir}")

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    @app.post("/rpc-run")
    async def rpc_run(data: dict):
        job_id = data.get("id", None)
        method = data.get("method")
        params = data.get("params", [])
        start_time = time.perf_counter_ns()
        try:
            if not hasattr(handlers, method):
                raise Exception(f"rpc-run {method} is not found")
            lines = pretty_repr(tuple(params)).split("\n")
            lines[0] = f"rpc-run.{method}" + lines[0] + ":started..."
            # for l in lines:
            #     logger.info(l)
            fn = getattr(handlers, method)
            if inspect.iscoroutinefunction(fn):
                result = await fn(*params)
            else:
                result = fn(*params)
            result = {"result": result, "jsonrpc": "2.0", "id": job_id}
            elapsed_ms = round((time.perf_counter_ns() - start_time) / 1e6)
            time_str = get_time_str(elapsed_ms / 1000)
            logger.info(f"rpc-run.{method}:finished in {time_str}")
        except Exception:
            elapsed_ms = round((time.perf_counter_ns() - start_time) / 1e6)
            time_str = get_time_str(elapsed_ms / 1000)
            logger.info(f"rpc-run.{method}:error after {time_str}:")
            error_lines = str(traceback.format_exc()).splitlines()
            for line in error_lines:
                logger.error(line)
            result = {
                "error": {"code": -1, "message": error_lines},
                "jsonrpc": "2.0",
                "id": job_id,
            }
        return result

    @app.get("/parmed/{foam_id}")
    async def get_parmed(foam_id: str, i_frame: int = None):
        try:
            logger.info(f"get_parmed {foam_id} {i_frame}")
            blob = handlers.get_parmed_blob(foam_id, i_frame)
            return Response(content=blob, media_type="application/octet-stream")
        except Exception as e:
            error_lines = str(traceback.format_exc()).splitlines()
            for line in error_lines:
                logger.debug(line)
            raise e

    @app.post("/upload/")
    async def upload_file(file: UploadFile = File(...)):
        try:
            fname = py_.kebab_case(file.filename)
            full_fname = data_dir / Path("files") / Path(fname)
            parent = full_fname.parent
            stem = full_fname.stem
            suffix = full_fname.suffix
            i = 1
            while full_fname.exists():
                full_fname = parent / Path(f"{stem}_{i}.{suffix}")
                i += 1
            full_fname.parent.makedirs_p()
            with open(full_fname, "wb+") as f:
                f.write(file.file.read())
            logger.info(f"Saved {full_fname} for {fname}")
            return {"filename": fname}
        except Exception as e:
            error_lines = str(traceback.format_exc()).splitlines()
            for line in error_lines:
                logger.debug(line)
            raise e

    @app.get("/")
    async def serve_index(request: Request):
        return FileResponse(client_dir / "index.html")

    if client_dir:
        # All other calls diverted to static files
        app.mount("/", StaticFiles(directory=client_dir), name="dist")

    return app


def init_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s:%(name)s:%(funcName)s: %(message)s"
    )
    logging.getLogger("root").setLevel(logging.WARNING)
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).setLevel(logging.INFO)


def open_url_in_background(test_url, open_url=None, sleep_in_s=1):
    """
    Polls server in background thread then opens a url in webbrowser
    """
    if open_url is None:
        open_url = test_url

    def inner():
        elapsed = 0
        while True:
            try:
                response_code = urlopen(test_url).getcode()
                if response_code < 400:
                    logger.info(f"open_url_in_background open {open_url}")
                    webbrowser.open(open_url)
                    return
            except:
                time.sleep(sleep_in_s)
                elapsed += sleep_in_s
                logger.info(f"testing {test_url} waiting {elapsed}s")

    # creates a thread to poll server before opening client
    logger.debug(f"open_url_in_background testing {test_url} to open {open_url}")
    threading.Thread(target=inner).start()


def find_free_port():
    logger.info(tic("find port"))
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = s.getsockname()[1]
    logger.info(toc() + f": {port}")
    return port


def run_server(config):
    if config.is_dev:
        # dev client will start on 3333
        # this server will run on 9023 unless overridden
        port = 9023
        logger.info(f"port: {port}")
        open_url_in_background(
            f"http://localhost:{port}",
            "http://localhost:3333/#/foamtraj/0",
        )
        # Run uvicorn externally for reloading
        dump_yaml(config, Path(this_dir) / "app.yaml")
        os.system(f"cd {this_dir}; uvicorn run_app:app --reload --port {port}")
    else:
        port = config.get("port")
        if not port:
            # mix up ports so multiple copies can run
            port = find_free_port()
        logger.info(f"port: {port}")
        open_url_in_background(f"http://localhost:{port}/#/foamtraj/0")
        uvicorn.run(make_app(config), port=port, log_level="critical")
