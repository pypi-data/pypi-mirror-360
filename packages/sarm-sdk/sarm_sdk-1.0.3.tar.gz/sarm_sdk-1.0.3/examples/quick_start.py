#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 快速开始示例

这个示例展示了 SARM SDK 的基本使用方法。
"""

from sarm_sdk import SARMClient
from sarm_sdk.models import OrganizeInsert, VulnInsert, SecurityCapability
from sarm_sdk.exceptions import SARMException

def main():
    # 初始化客户端
    client = SARMClient(
        base_url="https://your-api-platform.com",
        token="your-bearer-token"
    )
    
    try:
        # 1. 创建安全能力
        capability = SecurityCapability(
            capability_name="SonarQube扫描",
            capability_unique_id="SAST-001", 
            capability_desc="静态代码扫描",
            capability_type="Static Application Security Testing"
        )
        client.security_capabilities.create(capability)
        print("✅ 安全能力创建成功")
        
        # 2. 创建组织
        org = OrganizeInsert(
            organize_name="技术部",
            organize_unique_id="ORG-001",
            organize_punique_id="0",
            status="active"
        )
        result = client.organizations.create(org, execute_release=True)
        print(f"✅ 组织创建成功: {result.success_count}个")
        
        # 3. 刷新组织缓存
        client.organizations.refresh_cache()
        print("✅ 组织缓存刷新成功")
        
        # 4. 创建漏洞
        vuln = VulnInsert(
            vuln_unique_id="VULN-001",
            title="SQL注入漏洞",
            description="存在SQL注入风险",
            severity="high",
            security_capability_unique_id="SAST-001"
        )
        result = client.vulnerabilities.create(vuln, execute_release=True)
        print(f"✅ 漏洞创建成功: {result.success_count}个")
        
        print("🎉 SDK使用演示完成！")
        
    except SARMException as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main() 