#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 完整使用示例

这个示例展示了如何使用 SARM SDK 进行完整的数据导入流程，
包括组织架构、软件成分、漏洞数据和安全问题的批量导入。
"""

import logging
from datetime import datetime
from sarm_sdk import SARMClient
from sarm_sdk.models import (
    OrganizeInsert,
    ComponentInsert, 
    VulnInsert,
    IssueInsert,
    SecurityCapability,
    VulnCvss,
    VulnContext,
    VulnSolution,
    VulnReference
)
from sarm_sdk.exceptions import SARMException, SARMAPIError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """主函数：完整的数据导入流程演示"""
    
    # 1. 初始化客户端
    client = SARMClient(
        base_url="https://your-platform-api.com",
        token="your-bearer-token-here"
    )
    
    try:
        # 测试连接
        logger.info("🔗 测试API连接...")
        api_info = client.get_api_info()
        logger.info(f"✅ API连接成功: {api_info}")
        
        # 2. 创建安全能力（前置依赖）
        logger.info("🛡️ 创建安全能力...")
        create_security_capabilities(client)
        
        # 3. 创建组织架构
        logger.info("🏢 创建组织架构...")
        create_organizations(client)
        
        # 4. 创建软件成分
        logger.info("📦 创建软件成分...")
        create_components(client)
        
        # 5. 创建漏洞数据
        logger.info("🐛 创建漏洞数据...")
        create_vulnerabilities(client)
        
        # 6. 创建安全问题
        logger.info("⚠️ 创建安全问题...")
        create_security_issues(client)
        
        logger.info("🎉 数据导入流程完成！")
        
    except SARMException as e:
        logger.error(f"❌ SARM SDK 错误: {e}")
        if hasattr(e, 'details') and e.details:
            logger.error(f"错误详情: {e.details}")
    except Exception as e:
        logger.error(f"💥 未知错误: {e}")
    finally:
        # 关闭客户端
        client.close()


def create_security_capabilities(client: SARMClient):
    """创建安全能力"""
    capabilities = [
        SecurityCapability(
            capability_name="SonarQube静态扫描",
            capability_unique_id="SAST-SONAR-001",
            capability_desc="基于SonarQube的静态代码安全分析",
            missing_rate_value=0.15,
            capability_type="Static Application Security Testing"
        ),
        SecurityCapability(
            capability_name="Snyk开源组件扫描", 
            capability_unique_id="SCA-SNYK-001",
            capability_desc="基于Snyk的开源组件漏洞扫描",
            missing_rate_value=0.08,
            capability_type="Software Composition Analysis"
        ),
        SecurityCapability(
            capability_name="OWASP ZAP动态扫描",
            capability_unique_id="DAST-ZAP-001", 
            capability_desc="基于OWASP ZAP的动态应用安全测试",
            missing_rate_value=0.25,
            capability_type="Dynamic Application Security Testing"
        )
    ]
    
    for capability in capabilities:
        try:
            result = client.security_capabilities.create(capability)
            logger.info(f"✅ 安全能力创建成功: {capability.capability_name}")
        except SARMAPIError as e:
            if "已存在" in str(e):
                logger.info(f"ℹ️ 安全能力已存在: {capability.capability_name}")
            else:
                logger.error(f"❌ 安全能力创建失败: {capability.capability_name}, 错误: {e}")


def create_organizations(client: SARMClient):
    """创建组织架构"""
    organizations = [
        OrganizeInsert(
            organize_name="公司A",
            organize_unique_id="1930296726111916032",
            organize_punique_id="0",  # 顶级组织
            organize_leader_unique_id="1932296726111916032",
            desc="一家综合性公司",
            status="active",
            dep_id="DEPT001"
        ),
        OrganizeInsert(
            organize_name="技术研发中心",
            organize_unique_id="1930296734248865792",
            organize_punique_id="1930296726111916032",  # 上级组织
            organize_leader_unique_id="1932296734248865792",
            desc="负责公司核心技术平台研发和基础设施建设",
            status="active",
            dep_id="DEPT002"
        ),
        OrganizeInsert(
            organize_name="应用安全团队",
            organize_unique_id="1930296742637821952",
            organize_punique_id="1930296734248865792",  # 上级组织
            organize_leader_unique_id="1932296742637821952",
            desc="负责应用安全测试、漏洞管理和安全工具建设",
            status="active",
            dep_id="DEPT003"
        )
    ]
    
    try:
        # 批量创建组织
        result = client.organizations.create_batch(organizations, execute_release=True)
        logger.info(f"✅ 组织创建完成: 总数{result.total_count}, 成功{result.success_count}, 失败{result.failed_count}")
        
        if result.failed_count > 0:
            for failed_item in result.failed_items:
                logger.warning(f"⚠️ 组织创建失败: {failed_item.unique_id}, 原因: {failed_item.msg}")
        
        # 刷新组织架构缓存
        logger.info("🔄 刷新组织架构缓存...")
        client.organizations.refresh_cache()
        logger.info("✅ 组织架构缓存刷新完成")
        
    except SARMAPIError as e:
        logger.error(f"❌ 组织创建失败: {e}")


def create_components(client: SARMClient):
    """创建软件成分"""
    components = [
        ComponentInsert(
            component_unique_id="spring-boot-starter-web-2.7.0",
            component_name="Spring Boot Starter Web",
            component_version="2.7.0",
            status="active",
            component_desc="Spring Boot Web应用开发核心starter包，包含Spring MVC、嵌入式Tomcat、JSON处理等功能",
            asset_category="软件成分",
            asset_type="open_source_component",
            vendor="Pivotal Software",
            ecosystem="Maven",
            repository="https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-starter-web/",
            tags=["spring", "web", "mvc", "java", "framework"],
            supplier_name="Spring团队",
            attributes={
                "groupId": "org.springframework.boot",
                "artifactId": "spring-boot-starter-web",
                "packaging": "jar",
                "license": "Apache-2.0",
                "dependencies_count": 42
            }
        ),
        ComponentInsert(
            component_unique_id="jackson-databind-2.13.2",
            component_name="Jackson Databind",
            component_version="2.13.2",
            status="active",
            component_desc="Jackson数据绑定库，用于JSON序列化和反序列化",
            asset_category="软件成分",
            asset_type="open_source_component",
            vendor="FasterXML",
            ecosystem="Maven",
            repository="https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/",
            tags=["jackson", "json", "serialization", "java"],
            supplier_name="FasterXML",
            attributes={
                "groupId": "com.fasterxml.jackson.core",
                "artifactId": "jackson-databind",
                "packaging": "jar",
                "license": "Apache-2.0"
            }
        ),
        ComponentInsert(
            component_unique_id="mysql-connector-java-8.0.28",
            component_name="MySQL Connector/J",
            component_version="8.0.28",
            status="active",
            component_desc="MySQL官方JDBC驱动程序",
            asset_category="软件成分",
            asset_type="open_source_component",
            vendor="Oracle Corporation",
            ecosystem="Maven",
            repository="https://repo1.maven.org/maven2/mysql/mysql-connector-java/",
            tags=["mysql", "jdbc", "database", "driver"],
            supplier_name="Oracle",
            attributes={
                "groupId": "mysql",
                "artifactId": "mysql-connector-java",
                "packaging": "jar",
                "license": "GPL-2.0-with-classpath-exception"
            }
        )
    ]
    
    try:
        result = client.components.create_batch(components, execute_release=True)
        logger.info(f"✅ 软件成分创建完成: 总数{result.total_count}, 成功{result.success_count}, 失败{result.failed_count}")
        
        if result.failed_count > 0:
            for failed_item in result.failed_items:
                logger.warning(f"⚠️ 软件成分创建失败: {failed_item.unique_id}, 原因: {failed_item.msg}")
                
    except SARMAPIError as e:
        logger.error(f"❌ 软件成分创建失败: {e}")


def create_vulnerabilities(client: SARMClient):
    """创建漏洞数据"""
    vulnerabilities = [
        VulnInsert(
            vuln_unique_id="vuln-001-jackson-deserialization-2024",
            title="Jackson反序列化远程代码执行漏洞",
            description="Jackson-databind在反序列化过程中存在远程代码执行漏洞，攻击者可以通过构造恶意的JSON数据包触发任意代码执行，获取服务器控制权。该漏洞影响Jackson-databind 2.13.2及更早版本。",
            severity="critical",
            status="open",
            vulnerability_type="反序列化漏洞",
            cwe_id="CWE-502",
            cve_id="CVE-2022-42003",
            tags=["jackson", "deserialization", "rce", "critical"],
            cvss=[
                VulnCvss(
                    score="9.8",
                    vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    version="3.1"
                )
            ],
            impact="攻击者可以远程执行任意代码，完全控制受影响的服务器，获取敏感数据，破坏系统完整性。",
            context=[
                VulnContext(
                    name="DefaultTyping配置",
                    type="配置",
                    context="ObjectMapper.enableDefaultTyping()被启用时触发",
                    description="当Jackson配置启用默认类型时，攻击者可以通过@class字段指定任意类进行反序列化"
                )
            ],
            solution=[
                VulnSolution(
                    type="版本升级",
                    details="升级Jackson-databind至2.13.4.2或更高版本",
                    description="新版本修复了已知的反序列化漏洞，建议立即升级"
                ),
                VulnSolution(
                    type="配置修复",
                    details="禁用enableDefaultTyping()或使用更安全的类型配置",
                    description="如无法立即升级，可通过安全配置降低风险"
                )
            ],
            reference=[
                VulnReference(
                    type="CVE",
                    url="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-42003"
                ),
                VulnReference(
                    type="Advisory",
                    url="https://github.com/FasterXML/jackson-databind/security/advisories"
                )
            ],
            discovery_at=datetime(2024, 1, 15, 10, 30, 0),
            owner_name="应用安全团队",
            security_capability_unique_id="SAST-SONAR-001"
        ),
        VulnInsert(
            vuln_unique_id="vuln-002-spring-boot-actuator-2024",
            title="Spring Boot Actuator敏感信息泄露",
            description="Spring Boot Actuator端点未正确配置访问控制，导致敏感的应用配置信息、环境变量、健康检查详情等信息暴露给未授权用户。",
            severity="high",
            status="open",
            vulnerability_type="信息泄露",
            cwe_id="CWE-200",
            tags=["spring-boot", "actuator", "information-disclosure"],
            cvss=[
                VulnCvss(
                    score="7.5",
                    vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                    version="3.1"
                )
            ],
            impact="攻击者可以获取应用配置、数据库连接信息、内部服务地址等敏感信息，为进一步攻击提供便利。",
            context=[
                VulnContext(
                    name="/actuator/env",
                    type="端点",
                    context="暴露所有环境变量和配置属性",
                    description="包含数据库密码、API密钥等敏感配置"
                ),
                VulnContext(
                    name="/actuator/configprops",
                    type="端点", 
                    context="暴露所有@ConfigurationProperties bean",
                    description="可能包含内部系统配置和连接信息"
                )
            ],
            solution=[
                VulnSolution(
                    type="配置修复",
                    details="配置Actuator端点访问控制，仅允许内网或授权用户访问",
                    description="在application.yml中添加security配置限制端点访问"
                ),
                VulnSolution(
                    type="端点禁用",
                    details="禁用不必要的Actuator端点，特别是敏感端点",
                    description="通过management.endpoints.web.exposure.exclude配置禁用敏感端点"
                )
            ],
            reference=[
                VulnReference(
                    type="Documentation",
                    url="https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html#actuator.endpoints.security"
                )
            ],
            discovery_at=datetime(2024, 1, 20, 14, 15, 0),
            owner_name="基础架构团队",
            security_capability_unique_id="DAST-ZAP-001"
        ),
        VulnInsert(
            vuln_unique_id="vuln-003-mysql-connector-sql-injection-2024",
            title="MySQL Connector/J SQL注入漏洞",
            description="MySQL Connector/J在处理特定配置时存在SQL注入风险，攻击者可能通过构造恶意连接参数绕过安全检查。",
            severity="medium",
            status="open",
            vulnerability_type="SQL注入",
            cwe_id="CWE-89",
            tags=["mysql", "jdbc", "sql-injection"],
            cvss=[
                VulnCvss(
                    score="6.5",
                    vector="CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N",
                    version="3.1"
                )
            ],
            impact="在特定配置下，攻击者可能执行未授权的SQL查询，获取或修改数据库数据。",
            solution=[
                VulnSolution(
                    type="版本升级",
                    details="升级到MySQL Connector/J 8.0.33或更高版本",
                    description="新版本修复了相关安全问题"
                ),
                VulnSolution(
                    type="配置加固",
                    details="审查和加固数据库连接配置，使用最小权限原则",
                    description="确保数据库用户权限最小化，启用连接参数验证"
                )
            ],
            discovery_at=datetime(2024, 1, 25, 9, 0, 0),
            owner_name="数据库团队",
            security_capability_unique_id="SCA-SNYK-001"
        )
    ]
    
    try:
        result = client.vulnerabilities.create_batch(vulnerabilities, execute_release=True)
        logger.info(f"✅ 漏洞数据创建完成: 总数{result.total_count}, 成功{result.success_count}, 失败{result.failed_count}")
        
        if result.failed_count > 0:
            for failed_item in result.failed_items:
                logger.warning(f"⚠️ 漏洞创建失败: {failed_item.unique_id}, 原因: {failed_item.msg}")
                
    except SARMAPIError as e:
        logger.error(f"❌ 漏洞数据创建失败: {e}")


def create_security_issues(client: SARMClient):
    """创建安全问题"""
    security_issues = [
        IssueInsert(
            issue_unique_id="issue-2024-001-jackson-rce",
            issue_owner_unique_id="1932296742637821952",  # 应用安全团队负责人
            issue_status="open",
            issue_title="Jackson组件存在严重远程代码执行漏洞",
            issue_level="critical",
            issue_desc="项目中使用的Jackson-databind组件存在远程代码执行漏洞(CVE-2022-42003)，影响多个核心业务系统。该漏洞可能导致攻击者完全控制受影响的服务器，获取敏感数据。需要立即进行修复。",
            solution="""修复方案：
1. 【紧急】立即升级Jackson-databind至2.13.4.2或更高版本
2. 【短期】在无法立即升级的系统中禁用enableDefaultTyping()配置
3. 【长期】建立依赖组件漏洞监控机制，及时发现和修复安全问题
4. 【验证】升级后进行安全测试，确认漏洞已修复

风险评估：
- 影响系统：用户管理系统、交易系统、报表系统
- 风险等级：严重
- 修复优先级：最高
- 预计修复时间：3个工作日""",
            discovery_at=datetime(2024, 1, 15, 10, 30, 0),
            vuln_unique_id=["vuln-001-jackson-deserialization-2024"],
            component_unique_id=["jackson-databind-2.13.2"]
        ),
        IssueInsert(
            issue_unique_id="issue-2024-002-spring-boot-info-disclosure",
            issue_owner_unique_id="1932296734248865792",  # 技术研发中心负责人
            issue_status="open", 
            issue_title="Spring Boot应用存在敏感信息泄露风险",
            issue_level="high",
            issue_desc="多个Spring Boot应用的Actuator端点配置不当，向未授权用户暴露了包括数据库连接信息、API密钥等在内的敏感配置信息。这些信息可能被攻击者利用进行进一步攻击。",
            solution="""修复方案：
1. 【立即】配置Actuator端点访问控制，仅允许内网访问
2. 【短期】禁用不必要的敏感端点（env、configprops等）
3. 【中期】实施统一的Spring Boot安全配置模板
4. 【长期】建立应用安全配置审计机制

配置示例：
```yaml
management:
  endpoints:
    web:
      exposure:
        exclude: env,configprops,beans,conditions
  endpoint:
    health:
      show-details: when-authorized
  security:
    enabled: true
```""",
            discovery_at=datetime(2024, 1, 20, 14, 15, 0),
            vuln_unique_id=["vuln-002-spring-boot-actuator-2024"],
            component_unique_id=["spring-boot-starter-web-2.7.0"]
        ),
        IssueInsert(
            issue_unique_id="issue-2024-003-mysql-security-review",
            issue_owner_unique_id="1932296734248865792",
            issue_status="open",
            issue_title="MySQL数据库组件安全风险评估",
            issue_level="medium",
            issue_desc="使用的MySQL Connector/J版本存在潜在的SQL注入风险，虽然利用条件较为苛刻，但建议进行版本升级和配置加固以降低安全风险。",
            solution="""修复方案：
1. 【计划中】升级MySQL Connector/J到最新稳定版本8.0.33
2. 【同步进行】审查所有数据库连接配置，确保使用最小权限原则
3. 【加强】启用数据库连接参数验证和审计日志
4. 【测试】在测试环境验证升级兼容性

注意事项：
- 升级前需要充分测试兼容性
- 建议在维护窗口期进行升级
- 升级后监控应用性能和稳定性""",
            discovery_at=datetime(2024, 1, 25, 9, 0, 0),
            vuln_unique_id=["vuln-003-mysql-connector-sql-injection-2024"],
            component_unique_id=["mysql-connector-java-8.0.28"]
        )
    ]
    
    try:
        result = client.security_issues.create_batch(security_issues, execute_release=True)
        logger.info(f"✅ 安全问题创建完成: 总数{result.total_count}, 成功{result.success_count}, 失败{result.failed_count}")
        
        if result.failed_count > 0:
            for failed_item in result.failed_items:
                logger.warning(f"⚠️ 安全问题创建失败: {failed_item.unique_id}, 原因: {failed_item.msg}")
                
    except SARMAPIError as e:
        logger.error(f"❌ 安全问题创建失败: {e}")


if __name__ == "__main__":
    main() 