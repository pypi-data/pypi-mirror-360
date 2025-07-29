import os
from typing import List
from fastapi.staticfiles import StaticFiles
from rich import print as rPrint
from rich.panel import Panel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from OpenRacer.Model import ModelInterface
from OpenRacer.Routes import Routes

server = FastAPI(title="OpenRacer API", redoc_url="/redocs", docs_url="/docs")

origins = [
    "http://localhost:5173",
]

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Interface:
    def __init__(self, model:ModelInterface, host:str="localhost", port:int=8000, debug:bool = False):
        self.host = host
        self.port = port
        self.model = model
        self.url = f"http://{host}:{port}"
        self.router = Routes(model=model)
        server.debug = debug
        server.mount("/assets", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend", "assets")))
        server.include_router(self.router.communicationRoutes)
        server.include_router(self.router.dashboard)
        
        
    def start(self):
        """ 
        Start the server. 
        Calls the fastapi server to start.
        Also creates sqlite db for each start.
        """
        self.printStart(intro=["Welcome to OperRacer", f"[link={self.url}]Home Page: {self.url}[/link]"])
        uvicorn.run("OpenRacer.Interface:server", host=self.host, port=self.port)
        
    def printStart(self, intro:List[str]=["Welcome to OperRacer"], padding:int = 5):
        """
        Print startup Box to welcome and show links

        Args:
            intro (List[str], optional): Lines to be shown in startup panel. Defaults to ["Welcome to OperRacer"].
            padding (int, optional): use to decied size of panel. Defaults to 5.
        """
        maxLength = len(max(intro, key = lambda x: len(x))) + padding*2
        rPrint(Panel(intro[1], title=intro[0], width=maxLength))
        

    