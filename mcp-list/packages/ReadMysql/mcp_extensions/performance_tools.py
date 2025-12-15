"""MCP 性能分析工具 - EXPLAIN 分析和慢查询检测"""

import asyncio
import json
import logging
import time
from typing import Any

from mcp.server import Server

logger = logging.getLogger(__name__)


def register_performance_tools(server: Server, db_ops: Any) -> None:
    """
    注册性能分析相关的 MCP Tools

    Args:
        server: MCP Server 实例
        db_ops: DatabaseOperations 实例
    """

    @server.tool()
    async def explain_query(
        database: str,
        query: str,
        format: str = "traditional"
    ) -> dict[str, Any]:
        """
        使用 EXPLAIN 分析查询执行计划

        Args:
            database: 数据库名称
            query: SQL 查询语句（仅支持 SELECT）
            format: EXPLAIN 格式（traditional/json/tree，默认 traditional）

        Returns:
            EXPLAIN 分析结果和优化建议
        """
        try:
            # 参数验证
            if format not in ("traditional", "json", "tree"):
                return {
                    "success": False,
                    "error": f"不支持的格式: {format}，支持的格式: traditional, json, tree"
                }

            # 验证是 SELECT 查询
            query_upper = query.strip().upper()
            if not query_upper.startswith("SELECT"):
                return {
                    "success": False,
                    "error": "只支持分析 SELECT 查询"
                }

            # 构建 EXPLAIN 查询
            if format == "json":
                explain_query = f"EXPLAIN FORMAT=JSON {query}"
            elif format == "tree":
                explain_query = f"EXPLAIN FORMAT=TREE {query}"
            else:
                explain_query = f"EXPLAIN {query}"

            # 执行 EXPLAIN（不使用 limit，EXPLAIN 不返回大量数据）
            explain_result = await asyncio.to_thread(
                db_ops.execute_query,
                database,
                explain_query,
                None,
                None,  # EXPLAIN 不需要 limit
                "explain_query"
            )

            if not explain_result.get("success"):
                return explain_result

            # 分析 EXPLAIN 结果
            analysis = _analyze_explain(explain_result.get("data", []), format)

            # 同时执行实际查询以获取执行时间
            start_time = time.time()
            actual_result = await asyncio.to_thread(
                db_ops.execute_query,
                database,
                query,
                None,
                10,  # 只取 10 行测试性能
                "explain_query_test"
            )
            execution_time = time.time() - start_time

            logger.info(
                f"EXPLAIN 分析: {database}.{query[:50]}... "
                f"(执行时间: {execution_time:.3f}s)"
            )

            return {
                "success": True,
                "database": database,
                "query": query,
                "format": format,
                "explain_result": explain_result.get("data", []),
                "execution_time": round(execution_time, 4),
                "analysis": analysis,
                "recommendations": _generate_recommendations(
                    explain_result.get("data", []),
                    execution_time,
                    format
                )
            }

        except Exception as e:
            logger.error(f"EXPLAIN 分析失败 [{database}]: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "database": database
            }

    @server.tool()
    async def analyze_slow_query(
        database: str,
        query: str,
        threshold: float = 1.0
    ) -> dict[str, Any]:
        """
        分析慢查询并提供优化建议

        Args:
            database: 数据库名称
            query: SQL 查询语句
            threshold: 慢查询阈值（秒，默认 1.0）

        Returns:
            慢查询分析结果和优化建议
        """
        try:
            # 参数验证
            if threshold < 0.1 or threshold > 60:
                return {
                    "success": False,
                    "error": "threshold 必须在 0.1-60 秒之间"
                }

            # 执行查询并测量时间
            start_time = time.time()
            result = await asyncio.to_thread(
                db_ops.execute_query,
                database,
                query,
                None,
                100,  # 限制 100 行用于性能测试
                "analyze_slow_query"
            )
            execution_time = time.time() - start_time

            if not result.get("success"):
                return result

            # 判断是否为慢查询
            is_slow = execution_time >= threshold

            # 获取 EXPLAIN 分析
            explain_query = f"EXPLAIN FORMAT=JSON {query}"
            explain_result = await asyncio.to_thread(
                db_ops.execute_query,
                database,
                explain_query,
                None,
                None,
                "analyze_slow_query_explain"
            )

            # 分析结果
            analysis = {
                "is_slow_query": is_slow,
                "execution_time": round(execution_time, 4),
                "threshold": threshold,
                "row_count": result.get("row_count", 0),
                "rows_per_second": round(result.get("row_count", 0) / execution_time, 2) if execution_time > 0 else 0
            }

            # 如果是慢查询，提供详细分析
            if is_slow:
                logger.warning(
                    f"检测到慢查询: {database}.{query[:50]}... "
                    f"(执行时间: {execution_time:.3f}s, 阈值: {threshold}s)"
                )

                # 提取 EXPLAIN 数据
                explain_data = []
                if explain_result.get("success"):
                    explain_data = explain_result.get("data", [])

                recommendations = _generate_slow_query_recommendations(
                    query,
                    execution_time,
                    explain_data
                )

                return {
                    "success": True,
                    "database": database,
                    "query": query,
                    "analysis": analysis,
                    "explain_result": explain_data,
                    "recommendations": recommendations,
                    "severity": _classify_slow_query_severity(execution_time, threshold)
                }
            else:
                logger.info(
                    f"查询性能正常: {database}.{query[:50]}... "
                    f"(执行时间: {execution_time:.3f}s)"
                )

                return {
                    "success": True,
                    "database": database,
                    "query": query,
                    "analysis": analysis,
                    "message": f"查询性能正常（{execution_time:.3f}s < {threshold}s）"
                }

        except Exception as e:
            logger.error(f"慢查询分析失败 [{database}]: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "database": database
            }


def _analyze_explain(explain_data: list[dict[str, Any]], format: str) -> dict[str, Any]:
    """分析 EXPLAIN 结果"""
    if not explain_data:
        return {"error": "EXPLAIN 结果为空"}

    analysis = {
        "total_rows": 0,
        "using_index": False,
        "using_temporary": False,
        "using_filesort": False,
        "full_table_scan": False,
        "join_type": [],
        "tables_scanned": []
    }

    try:
        if format == "json":
            # JSON 格式的 EXPLAIN 分析
            if explain_data and "EXPLAIN" in explain_data[0]:
                json_data = json.loads(explain_data[0]["EXPLAIN"])
                # 简化处理，提取关键信息
                analysis["format"] = "json"
                analysis["details"] = json_data
        else:
            # Traditional 格式的 EXPLAIN 分析
            for row in explain_data:
                # 表名
                if "table" in row:
                    analysis["tables_scanned"].append(row["table"])

                # 扫描行数
                if "rows" in row:
                    analysis["total_rows"] += int(row.get("rows", 0) or 0)

                # JOIN 类型
                if "type" in row:
                    join_type = row["type"]
                    analysis["join_type"].append(join_type)

                    # 检测全表扫描
                    if join_type in ("ALL", "index"):
                        analysis["full_table_scan"] = True

                # Extra 信息
                extra = row.get("Extra", "")
                if "Using index" in extra:
                    analysis["using_index"] = True
                if "Using temporary" in extra:
                    analysis["using_temporary"] = True
                if "Using filesort" in extra:
                    analysis["using_filesort"] = True

    except Exception as e:
        logger.error(f"分析 EXPLAIN 结果时出错: {str(e)}")
        analysis["parse_error"] = str(e)

    return analysis


def _generate_recommendations(
    explain_data: list[dict[str, Any]],
    execution_time: float,
    format: str
) -> list[str]:
    """生成优化建议"""
    recommendations = []

    analysis = _analyze_explain(explain_data, format)

    # 全表扫描警告
    if analysis.get("full_table_scan"):
        recommendations.append(
            "⚠️ 检测到全表扫描（type=ALL），建议添加适当的索引"
        )

    # 临时表警告
    if analysis.get("using_temporary"):
        recommendations.append(
            "⚠️ 使用了临时表（Using temporary），可能影响性能，考虑优化查询或添加索引"
        )

    # 文件排序警告
    if analysis.get("using_filesort"):
        recommendations.append(
            "⚠️ 使用了文件排序（Using filesort），考虑在 ORDER BY 字段上添加索引"
        )

    # 扫描行数警告
    total_rows = analysis.get("total_rows", 0)
    if total_rows > 10000:
        recommendations.append(
            f"⚠️ 扫描行数较多（{total_rows} 行），建议优化查询条件或添加索引"
        )

    # 执行时间警告
    if execution_time > 1.0:
        recommendations.append(
            f"⚠️ 查询执行时间较长（{execution_time:.3f}s），建议进行优化"
        )

    # 使用索引的好消息
    if analysis.get("using_index"):
        recommendations.append(
            "✅ 查询使用了索引（Using index），性能较好"
        )

    if not recommendations:
        recommendations.append("✅ 查询执行计划正常，暂无优化建议")

    return recommendations


def _generate_slow_query_recommendations(
    query: str,
    execution_time: float,
    explain_data: list[dict[str, Any]]
) -> list[str]:
    """为慢查询生成详细的优化建议"""
    recommendations = []

    # 基础建议
    recommendations.append(f"🐌 慢查询检测：执行时间 {execution_time:.3f} 秒")

    # EXPLAIN 分析建议
    if explain_data:
        analysis = _analyze_explain(explain_data, "traditional")

        if analysis.get("full_table_scan"):
            recommendations.append(
                "📌 优先建议：添加索引避免全表扫描\n"
                "   - 检查 WHERE 条件中的字段\n"
                "   - 为常用查询字段创建复合索引"
            )

        if analysis.get("using_temporary"):
            recommendations.append(
                "📌 优化建议：避免使用临时表\n"
                "   - 简化 GROUP BY 子句\n"
                "   - 为 GROUP BY 字段添加索引\n"
                "   - 考虑重写查询逻辑"
            )

        if analysis.get("using_filesort"):
            recommendations.append(
                "📌 优化建议：避免文件排序\n"
                "   - 为 ORDER BY 字段添加索引\n"
                "   - 确保索引顺序与 ORDER BY 一致"
            )

        # 扫描行数建议
        total_rows = analysis.get("total_rows", 0)
        if total_rows > 50000:
            recommendations.append(
                f"📌 数据量建议：扫描了 {total_rows} 行数据\n"
                "   - 添加更精确的 WHERE 条件\n"
                "   - 考虑分页查询\n"
                "   - 使用 LIMIT 限制返回行数"
            )

    # 查询语句分析
    query_upper = query.upper()

    # 检测是否缺少 WHERE
    if "WHERE" not in query_upper and "JOIN" in query_upper:
        recommendations.append(
            "📌 查询结构建议：缺少 WHERE 条件\n"
            "   - 添加适当的过滤条件\n"
            "   - 避免返回不必要的数据"
        )

    # 检测是否使用了 SELECT *
    if "SELECT *" in query_upper:
        recommendations.append(
            "📌 字段选择建议：避免使用 SELECT *\n"
            "   - 只查询需要的字段\n"
            "   - 减少网络传输和内存占用"
        )

    # 检测是否有子查询
    if query.count("SELECT") > 1:
        recommendations.append(
            "📌 子查询优化：考虑优化子查询\n"
            "   - 尝试使用 JOIN 替代子查询\n"
            "   - 确保子查询有适当的索引\n"
            "   - 考虑使用临时表拆分复杂查询"
        )

    return recommendations


def _classify_slow_query_severity(execution_time: float, threshold: float) -> str:
    """分类慢查询严重程度"""
    ratio = execution_time / threshold

    if ratio >= 10:
        return "critical"  # 严重（超过阈值 10 倍）
    elif ratio >= 5:
        return "high"      # 高（超过阈值 5 倍）
    elif ratio >= 2:
        return "medium"    # 中（超过阈值 2 倍）
    else:
        return "low"       # 低（略超阈值）
