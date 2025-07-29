#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 数据模型

包含所有的数据模型定义。
"""

from .organization import OrganizeInsert, Organization, OrganizationTree, OrganizeUser
from .carrier import CarrierInsert, Carrier
from .response import BatchOperationResult, BatchOperationItem, SuccessResponse, ErrorResponse

# 尝试导入其他模型，如果文件不存在则跳过
try:
    from .security_capability import SecurityCapabilityInsert
except ImportError:
    pass

try:
    from .vulnerability import VulnerabilityInsert
except ImportError:
    pass

try:
    from .security_issue import SecurityIssueInsert
except ImportError:
    pass

try:
    from .component import ComponentInsert
except ImportError:
    pass

# 导入其他模型
from .security_capability import SecurityCapability

__all__ = [
    # 核心模型
    'OrganizeInsert',
    'Organization',
    'OrganizationTree',
    'OrganizeUser',
    'CarrierInsert',
    'Carrier',
    'BatchOperationResult',
    'BatchOperationItem',
    'SuccessResponse',
    'ErrorResponse',
    'SecurityCapability',
    'VulnerabilityInsert',
    'SecurityIssueInsert',
    'ComponentInsert'
] 