#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 业务系统数据模型

定义业务系统相关的数据结构。
基于实际SDK代码和API定义。
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class BusinessSystemStatus(str, Enum):
    """业务系统状态枚举（基于实际API）"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class BusinessSystemInsert(BaseModel):
    """业务系统创建数据模型（基于实际API字段）"""
    business_system_name: str = Field(..., description="业务系统名称")
    business_system_uuid: str = Field(..., description="业务系统唯一ID")
    business_system_puuid: Optional[str] = Field(None, description="上级业务系统ID")
    business_system_desc: str = Field(..., description="业务系统描述")
    business_system_status: str = Field(..., description="业务系统状态")


class BusinessSystemUpdate(BaseModel):
    """业务系统更新数据模型"""
    business_system_uuid: str = Field(..., description="业务系统唯一ID")
    business_system_name: Optional[str] = Field(None, description="业务系统名称")
    business_system_puuid: Optional[str] = Field(None, description="上级业务系统ID")
    business_system_desc: Optional[str] = Field(None, description="业务系统描述")
    business_system_status: Optional[str] = Field(None, description="业务系统状态")


class BusinessSystem(BaseModel):
    """业务系统完整信息模型"""
    business_system_id: Optional[int] = Field(None, description="业务系统ID（系统生成）")
    business_system_name: str = Field(..., description="业务系统名称")
    business_system_uuid: str = Field(..., description="业务系统唯一ID")
    business_system_puuid: Optional[str] = Field(None, description="上级业务系统ID")
    business_system_desc: Optional[str] = Field(None, description="业务系统描述")
    business_system_status: Optional[str] = Field("active", description="业务系统状态")
    organize_user_unique_id: Optional[str] = Field(None, description="负责人用户ID")
    organize_unique_id: Optional[str] = Field(None, description="关联组织ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    @property
    def is_root_system(self) -> bool:
        """是否为根系统（无上级系统）"""
        return not self.business_system_puuid
    
    @property
    def is_active(self) -> bool:
        """是否为活跃状态"""
        return self.business_system_status == "active"