#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 应用载体 API

提供应用载体相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.carrier import CarrierInsert, Carrier
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class CarrierAPI:
    """应用载体API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def create_batch(
        self,
        carriers: List[CarrierInsert],
        execute_release: bool = False
    ) -> BatchOperationResult:
        """
        批量创建应用载体
        
        Args:
            carriers: 应用载体数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not carriers:
            raise SARMValidationError("应用载体列表不能为空")
        
        if len(carriers) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证数据
        carrier_data = []
        for carrier in carriers:
            if isinstance(carrier, CarrierInsert):
                carrier_data.append(carrier.dict())
            else:
                carrier_data.append(carrier)
        
        # 发送请求
        response = self.client.post(
            '/api/carrier/create',
            data=carrier_data,
            execute_release=execute_release
        )
        
        # 处理简单的成功响应
        if isinstance(response, dict) and 'code' in response:
            success = response.get('code') == 200
            # 创建批量操作结果
            from ..models.response import BatchOperationItem
            items = []
            for i, carrier in enumerate(carriers):
                # 正确获取载体信息
                if isinstance(carrier, dict):
                    unique_id = carrier.get('carrier_unique_id', f"carrier_{i}")
                    name = carrier.get('carrier_name', '')
                elif hasattr(carrier, 'carrier_unique_id'):
                    unique_id = getattr(carrier, 'carrier_unique_id', f"carrier_{i}")
                    name = getattr(carrier, 'carrier_name', '')
                else:
                    unique_id = f"carrier_{i}"
                    name = ''
                
                items.append(BatchOperationItem(
                    unique_id=unique_id,
                    name=name,
                    success=success,
                    msg="创建成功" if success else "创建失败"
                ))
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def create(self, carrier: CarrierInsert, execute_release: bool = False) -> BatchOperationResult:
        """创建单个应用载体"""
        return self.create_batch([carrier], execute_release=execute_release)
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 50,
        carrier_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取应用载体列表"""
        params = {"page": page, "limit": limit}
        if carrier_type:
            params["carrier_type"] = carrier_type
        
        response = self.client.get('/api/carrier/list', params=params)
        return response
    
    def update_batch(
        self,
        carriers: List[Dict[str, Any]],
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        批量更新应用载体
        
        Args:
            carriers: 应用载体数据列表
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not carriers:
            raise SARMValidationError("应用载体列表不能为空")
        
        response = self.client.post(
            '/api/carrier/update',
            data=carriers,
            execute_release=execute_release
        )
        return response
    
    def update(self, carrier_data: Dict[str, Any], execute_release: bool = False) -> Dict[str, Any]:
        """更新单个应用载体"""
        return self.update_batch([carrier_data], execute_release=execute_release)
    
    def delete_batch(self, carrier_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除应用载体
        
        Args:
            carrier_ids: 载体ID列表
            
        Returns:
            操作结果
        """
        if not carrier_ids:
            raise SARMValidationError("载体ID列表不能为空")
        
        response = self.client.delete('/api/carrier/delete', data=carrier_ids)
        return response
    
    def delete(self, carrier_id: str) -> Dict[str, Any]:
        """删除单个应用载体"""
        return self.delete_batch([carrier_id])
    
    def get_carrier_unique_id(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取载体唯一ID
        
        Args:
            filters: 查询过滤条件
            
        Returns:
            载体唯一ID列表
        """
        data = filters or {}
        response = self.client.post('/api/carrier/get_carrier_unique_id', data=data)
        return response 