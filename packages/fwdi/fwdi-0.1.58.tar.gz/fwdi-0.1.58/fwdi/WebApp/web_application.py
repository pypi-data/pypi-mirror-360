#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import uvicorn
from typing import Callable, Any, TypeVar
from fastapi import FastAPI
import gradio as gr

from ..Application.Logging.manager_logging import ManagerLogging
from ..Utilites.ext_global_setting import ExtGlobalSetting
from ..Domain.Configure.global_setting_service import GlobalSettingService
from ..Application.DependencyInjection.resolve_provider import ResolveProviderFWDI
from ..Application.Abstractions.base_controller import BaseControllerFWDI
from .web_application_builder import WebApplicationBuilder
from ..Application.dependency_injection import DependencyInjection as ApplicationDependencyInjection
from ..Persistence.dependency_injection import DependencyInjection as PersistenceDependencyInjection
from ..Infrastructure.dependency_injection import DependencyInjection as InfrastructureDependencyInjection

T = TypeVar('T', bound='WebApplication')

class WebApplication():
    def __init__(self, config:GlobalSettingService = None, **kwargs):
        from ..Application.Logging.manager_logging import ManagerLogging
                
        if config is None:
            config = GlobalSettingService

        self._config:GlobalSettingService = config
        self.__log__ = ManagerLogging.get_logging('WebApplication', self._config) #SysLogging(logging_level=TypeLogging.DEBUG, filename='WebApplication')
        
        self.__log__(f"{__name__}:{kwargs}")
        self.__app:FastAPI = FastAPI()
        
        self.resolver:ResolveProviderFWDI = None
        self.Name:str = kwargs['name'] if 'name' in kwargs else ''

    @property
    def Debug(self)->bool:
        return self.__debug

    @property
    def app(self)->FastAPI:
        return self.__app

    def map_controller(self, controller:BaseControllerFWDI)->None:
        self.__log__(f"{__name__}:{controller}")
        if hasattr(controller, "routes"):
            self.__app.include_router(controller)
        else:
            raise Exception(f"{controller} has no have attribute routes !")

    def add_web_page(self, inst: gr.Blocks, path:str="/panel", is_auth:bool=False, allowed_paths:list[str]=None):
        from ..Presentation.DefaultControllers.http_auth import HttpAuthFWDI

        self.__log__(f"{__name__}:{path}:{inst}", 'debug')
        if not is_auth:
            self.__app = gr.mount_gradio_app(self.__app, inst, path=path, allowed_paths=allowed_paths, favicon_path='icons')
        else:
            self.__app = gr.mount_gradio_app(self.__app, inst, path=path, auth=HttpAuthFWDI.login, allowed_paths=allowed_paths, favicon_path='icons')
    
    def map_route(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_route(path=path, route=endpoint)

    def map_get(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["GET"])
    
    def map_post(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["POST"])

    def map_delete(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["DELETE"])

    def map_put(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["PUT"])
        
    @classmethod
    def create_builder(cls:type[T], **kwargs)->WebApplicationBuilder:
        ExtGlobalSetting.load('service_config.json')

        __log__ = ManagerLogging.get_logging('WebApplicationBuilder', GlobalSettingService)
        
        webapp_instance = cls(GlobalSettingService, **kwargs)
        webbuild_instance = WebApplicationBuilder(webapp_instance)
        
        #----------------------DEFAULT SERVICES DEPENDENCY------------------------------------
        
        __log__(f"Create dependency injection Persistence")
        PersistenceDependencyInjection.AddPersistence(webbuild_instance.services)
        __log__(f"Create dependency injection Application")
        ApplicationDependencyInjection.AddApplication(webbuild_instance.services)
        __log__(f"Create dependency injection Infrastructure")
        InfrastructureDependencyInjection.AddInfrastructure(webbuild_instance.services)
        
        from ..Presentation.dependency_injection import DependencyInjection as PresentationDependencyInjection
        PresentationDependencyInjection.AddPresentation(webbuild_instance.services)
        
        #----------------------/DEFAULT SERVICES DEPENDENCY-----------------------------------

        return webbuild_instance
    
    def run(self, **kwargs):
        self.__log__(f"Run service:{__name__}:{kwargs}")
        if not kwargs:
            uvicorn.run(self.__app, host=GlobalSettingService.current_host, port=GlobalSettingService.current_port)
        else:
            GlobalSettingService.current_host = kwargs.get('host', 'localhost')
            GlobalSettingService.current_port = kwargs.get('port', 5000)
            uvicorn.run(self.__app, **kwargs)