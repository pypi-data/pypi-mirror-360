# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

from __future__ import annotations
from abc import ABCMeta,abstractmethod
from aiohttp import web
class RouteHandler(metaclass=ABCMeta):
	@abstractmethod
	async def handle_get_restconf_root(self,request):0
	@abstractmethod
	async def handle_get_yang_library_version(self,request):0
	@abstractmethod
	async def handle_get_opstate_request(self,request):0
	@abstractmethod
	async def handle_get_config_request(self,request):0
	@abstractmethod
	async def handle_post_config_request(self,request):0
	@abstractmethod
	async def handle_put_config_request(self,request):0
	@abstractmethod
	async def handle_delete_config_request(self,request):0
	@abstractmethod
	async def handle_action_request(self,request):0
	@abstractmethod
	async def handle_rpc_request(self,request):0
class AppRouteHandler(RouteHandler,metaclass=ABCMeta):
	@abstractmethod
	def __init__(self,dal,yl_obj,proxy_info,nvh):0