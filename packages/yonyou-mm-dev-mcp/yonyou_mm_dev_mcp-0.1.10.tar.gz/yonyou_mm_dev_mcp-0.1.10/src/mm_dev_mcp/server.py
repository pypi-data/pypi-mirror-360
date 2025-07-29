import httpx
import os
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
from datetime import datetime

# 从环境变量获取元数据服务URL（实际部署时需要配置）1
METADATA_SERVICE_URL = os.getenv("server", "https://imp-test.yyuap.com/mf-tools")
CONST_PROJECT = os.getenv("project", "")


# Initialize FastMCP server
mcp = FastMCP("mm_dev_mcp", "developer code API Integration")

async def make_metadata_request(path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    向元数据服务发送 POST 请求，并处理响应。
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    url = f"{METADATA_SERVICE_URL}/{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=json, headers=headers,params={"singlePage":True})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"请求失败: {url}，状态码: {e.response.status_code}，内容: {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"无法访问元数据服务: {url}，错误: {str(e)}") from e


# =========mcp tool 服务定义开始===========

@mcp.tool(name="get_code_metadata",description="依据项目和代码路径（包名），获取代码对应的业务模块、业务对象、代码类型等元数据信息")
async def get_code_metadata(filePath: str, project:str) -> Dict[str, Any]:
    """
    依据项目和代码路径或者包名，获取代码所属的业务模块、业务对象、代码类型等元数据信息

    参数:
        filePath: 代码文件路径,如: {moduleArtifact}/src/main/java/{com/yonyou/biz/mm/plan}/{layer}/{bizModule}/{bizObject}/{componentType}/Order.java
        project: 项目编码或者项目名称
    返回:
        solutionType: 解决方案类型(BE: 后端,FE: 前端)
        moduleArtifact:模块标识符
        basePackage: 基础包路径
        layer: 架构层次(entity、repository、resource、exception、operation、service、gateway、config、bootstrap、sdk)
        bizModule: 所属业务模块
        bizObject: 所属业务对象
        componentType: 组件类型(entity、enum、dto、repository、resource、exception、operation、service、gateway、ref、bootstrap、util、test)
        microserviceCode: 微服务编码
        standardFilePath: 标准文件路径
        description: 描述
    """
    if not filePath:
        raise ValueError("代码文件路径 不能为空")

    if not project:
        raise ValueError("项目不能为空")

    payload = {
        "project": project,
        "filePath": filePath,
    }
    return await make_metadata_request("solution/mcp/code/metadata", payload)


@mcp.tool(name="get_exception_code",description="获取异常编码: 依据项目、业务模块、业务对象、异常内容，获取异常编码")
async def get_exception_code(project: str, bizModule: str, bizObject: str, exceptionContent: str) -> Dict[str, Any]:
    """
    依据项目、业务模块、业务对象、异常内容，获取异常编码

    参数:
        project: 项目
        bizModule: 业务模块
        bizObject: 业务对象
        exceptionContent: 异常内容
    返回:
        exceptionId: 异常ID
        exceptionCode: 异常编码
        codeTepmplate: 异常编码模板
        standardFilePath: 标准文件路径
        description: 描述
    """
    if not project:
        raise ValueError("项目 不能为空")
    if not bizModule:
        raise ValueError("业务模块 不能为空")
    if not bizObject:
        raise ValueError("业务对象 不能为空")
    if not exceptionContent:
        raise ValueError("异常内容 不能为空")

    payload = {
        "project": project,  # 使用传入的project参数而不是常量
        "bizModule": bizModule,
        "bizObject": bizObject,
        "exceptionContent": exceptionContent,
    }
    return await make_metadata_request("solution/mcp/exception/metadata", payload)


@mcp.tool(name="get_generate_code_prompts",description="获取代码生成规则、代码优化规则。")
async def get_generate_code_prompts(project: Optional[str] = None,bizModule: Optional[str] = None,componentType: Optional[str] = None,topic: Optional[str] = None) -> str:
    """获取代码生成规则、代码优化规则。"""
    payload={
        "project": project,
        "bizModule": bizModule,
        "componentType": componentType,
        "topic": topic
    }
    return await make_metadata_request("solution/mcp/code/prompts", payload)


@mcp.tool(name="get_current_date",description="获取当前日期和时间")
def get_current_date(action: Optional[str] = None) -> str:
    """获取当前日期和时间"""
    current_date = datetime.now()
    # 格式化输出
    formatted_now = current_date.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_now


# =========mcp tool 服务定义结束===========


# =========mcp prompt 服务定义开始===========
@mcp.prompt(name="generate_code_request",description="生成代码注意事项")
def generate_code_request(language: str, task_description: str) -> str:
    """生成代码注意事项"""

    # 获取当前日期并格式化为字符串
    current_date = datetime.now().strftime("%Y-%m-%d")

    rule_item = f"""
    所有的类和方法都需要加上注解:@AICode(type = AICodeTypeEnum.CODE_GENERATION, author = "作者", date = "{current_date}", remark = "业务功能描述")
    AICode注解包在com.yonyou.biz.mm.common.annotation下。type=CODE_GENERATION|CODE_OPTIMIZATION|WHITE_BOX_TESTING
    """
    return rule_item


# =========mcp prompt 服务定义结束========2==
if __name__ == "__main__":
   mcp.run(transport="sse")
   #mcp.run(transport="stdio")