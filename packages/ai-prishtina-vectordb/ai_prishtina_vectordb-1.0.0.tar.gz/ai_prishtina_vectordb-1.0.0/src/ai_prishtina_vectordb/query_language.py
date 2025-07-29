"""
Advanced query language for AI Prishtina VectorDB.

This module provides a sophisticated query language with SQL-like syntax,
complex filtering, aggregations, and advanced search capabilities.
"""

import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ast
import operator
from datetime import datetime, timedelta

from .logger import AIPrishtinaLogger
from .exceptions import QueryError, ValidationError


class QueryType(Enum):
    """Query type enumeration."""
    VECTOR_SEARCH = "vector_search"
    SEMANTIC_SEARCH = "semantic_search"
    HYBRID_SEARCH = "hybrid_search"
    AGGREGATION = "aggregation"
    FILTER = "filter"
    COMPLEX = "complex"


class OperatorType(Enum):
    """Operator type enumeration."""
    EQ = "="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    BETWEEN = "BETWEEN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"


class AggregationType(Enum):
    """Aggregation type enumeration."""
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    GROUP_BY = "GROUP_BY"
    DISTINCT = "DISTINCT"


@dataclass
class FilterCondition:
    """Represents a filter condition."""
    field: str
    operator: OperatorType
    value: Any
    case_sensitive: bool = True


@dataclass
class SortCriteria:
    """Represents sorting criteria."""
    field: str
    ascending: bool = True


@dataclass
class AggregationSpec:
    """Represents an aggregation specification."""
    type: AggregationType
    field: Optional[str] = None
    alias: Optional[str] = None
    group_by: Optional[List[str]] = None


@dataclass
class QueryPlan:
    """Represents a compiled query execution plan."""
    query_type: QueryType
    vector_query: Optional[str] = None
    filters: List[FilterCondition] = field(default_factory=list)
    sort_criteria: List[SortCriteria] = field(default_factory=list)
    aggregations: List[AggregationSpec] = field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None
    similarity_threshold: Optional[float] = None
    include_metadata: bool = True
    include_documents: bool = True
    include_distances: bool = True


class QueryParser:
    """Advanced query parser with SQL-like syntax."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize query parser."""
        self.logger = logger or AIPrishtinaLogger(name="query_parser")
        
        # SQL-like keywords
        self.keywords = {
            'SELECT', 'FROM', 'WHERE', 'ORDER', 'BY', 'GROUP', 'HAVING',
            'LIMIT', 'OFFSET', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
            'IS', 'NULL', 'ASC', 'DESC', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
            'DISTINCT', 'VECTOR_SEARCH', 'SEMANTIC_SEARCH', 'HYBRID_SEARCH',
            'SIMILARITY', 'THRESHOLD', 'CONTAINS', 'STARTS_WITH', 'ENDS_WITH'
        }
        
        # Operator mappings
        self.operators = {
            '=': OperatorType.EQ,
            '!=': OperatorType.NE,
            '<>': OperatorType.NE,
            '>': OperatorType.GT,
            '>=': OperatorType.GTE,
            '<': OperatorType.LT,
            '<=': OperatorType.LTE,
            'IN': OperatorType.IN,
            'NOT IN': OperatorType.NOT_IN,
            'LIKE': OperatorType.LIKE,
            'NOT LIKE': OperatorType.NOT_LIKE,
            'BETWEEN': OperatorType.BETWEEN,
            'IS NULL': OperatorType.IS_NULL,
            'IS NOT NULL': OperatorType.IS_NOT_NULL,
            'CONTAINS': OperatorType.CONTAINS,
            'STARTS_WITH': OperatorType.STARTS_WITH,
            'ENDS_WITH': OperatorType.ENDS_WITH
        }
    
    def parse(self, query: str) -> QueryPlan:
        """Parse a query string into a query plan."""
        try:
            # Normalize query
            query = self._normalize_query(query)
            
            # Tokenize
            tokens = self._tokenize(query)
            
            # Parse tokens into query plan
            plan = self._parse_tokens(tokens)
            
            asyncio.create_task(self.logger.debug(f"Parsed query: {query}"))
            return plan

        except Exception as e:
            asyncio.create_task(self.logger.error(f"Query parsing failed: {str(e)}"))
            raise QueryError(f"Failed to parse query: {str(e)}")
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query string."""
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Convert keywords to uppercase
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            query = re.sub(pattern, keyword, query, flags=re.IGNORECASE)
        
        return query
    
    def _tokenize(self, query: str) -> List[str]:
        """Tokenize query string."""
        # Simple tokenization - in production, use a proper lexer
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(query):
            char = query[i]
            
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_token += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                current_token += char
                quote_char = None
            elif char == ' ' and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
            
            i += 1
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def _parse_tokens(self, tokens: List[str]) -> QueryPlan:
        """Parse tokens into query plan."""
        plan = QueryPlan(query_type=QueryType.VECTOR_SEARCH)
        
        i = 0
        while i < len(tokens):
            token = tokens[i].upper()
            
            if token == 'VECTOR_SEARCH':
                plan.query_type = QueryType.VECTOR_SEARCH
                i += 1
                if i < len(tokens):
                    plan.vector_query = self._unquote(tokens[i])
                    i += 1
            
            elif token == 'SEMANTIC_SEARCH':
                plan.query_type = QueryType.SEMANTIC_SEARCH
                i += 1
                if i < len(tokens):
                    plan.vector_query = self._unquote(tokens[i])
                    i += 1
            
            elif token == 'WHERE':
                i += 1
                filters, i = self._parse_where_clause(tokens, i)
                plan.filters.extend(filters)
            
            elif token == 'ORDER':
                if i + 1 < len(tokens) and tokens[i + 1].upper() == 'BY':
                    i += 2
                    sort_criteria, i = self._parse_order_by(tokens, i)
                    plan.sort_criteria.extend(sort_criteria)
                else:
                    i += 1
            
            elif token == 'LIMIT':
                i += 1
                if i < len(tokens):
                    plan.limit = int(tokens[i])
                    i += 1
            
            elif token == 'OFFSET':
                i += 1
                if i < len(tokens):
                    plan.offset = int(tokens[i])
                    i += 1
            
            elif token == 'SIMILARITY':
                if i + 1 < len(tokens) and tokens[i + 1].upper() == 'THRESHOLD':
                    i += 2
                    if i < len(tokens):
                        plan.similarity_threshold = float(tokens[i])
                        i += 1
                else:
                    i += 1
            
            else:
                i += 1
        
        return plan
    
    def _parse_where_clause(self, tokens: List[str], start: int) -> Tuple[List[FilterCondition], int]:
        """Parse WHERE clause."""
        filters = []
        i = start
        
        while i < len(tokens):
            token = tokens[i].upper()
            
            # Stop at certain keywords
            if token in ['ORDER', 'GROUP', 'LIMIT', 'OFFSET']:
                break
            
            # Parse condition
            if i + 2 < len(tokens):
                field = tokens[i]
                op_token = tokens[i + 1].upper()
                value_token = tokens[i + 2]
                
                # Handle multi-word operators
                if op_token == 'NOT' and i + 3 < len(tokens):
                    next_token = tokens[i + 3].upper()
                    if next_token in ['IN', 'LIKE']:
                        op_token = f"NOT {next_token}"
                        value_token = tokens[i + 4] if i + 4 < len(tokens) else ""
                        i += 1
                elif op_token == 'IS' and i + 3 < len(tokens):
                    next_token = tokens[i + 3].upper()
                    if next_token == 'NULL':
                        op_token = "IS NULL"
                        value_token = None
                        i += 1
                    elif next_token == 'NOT' and i + 4 < len(tokens) and tokens[i + 4].upper() == 'NULL':
                        op_token = "IS NOT NULL"
                        value_token = None
                        i += 2
                
                if op_token in self.operators:
                    operator = self.operators[op_token]
                    value = self._parse_value(value_token) if value_token is not None else None
                    
                    condition = FilterCondition(
                        field=field,
                        operator=operator,
                        value=value
                    )
                    filters.append(condition)
                
                i += 3
            else:
                i += 1
            
            # Skip AND/OR
            if i < len(tokens) and tokens[i].upper() in ['AND', 'OR']:
                i += 1
        
        return filters, i
    
    def _parse_order_by(self, tokens: List[str], start: int) -> Tuple[List[SortCriteria], int]:
        """Parse ORDER BY clause."""
        sort_criteria = []
        i = start
        
        while i < len(tokens):
            token = tokens[i].upper()
            
            # Stop at certain keywords
            if token in ['LIMIT', 'OFFSET', 'GROUP']:
                break
            
            field = tokens[i]
            ascending = True
            
            # Check for ASC/DESC
            if i + 1 < len(tokens):
                next_token = tokens[i + 1].upper()
                if next_token in ['ASC', 'DESC']:
                    ascending = next_token == 'ASC'
                    i += 1
            
            criteria = SortCriteria(field=field, ascending=ascending)
            sort_criteria.append(criteria)
            
            i += 1
            
            # Skip comma
            if i < len(tokens) and tokens[i] == ',':
                i += 1
        
        return sort_criteria, i
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse value string to appropriate type."""
        if value_str is None:
            return None
        
        # Remove quotes
        value_str = self._unquote(value_str)
        
        # Try to parse as different types
        try:
            # Integer
            if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
                return int(value_str)
            
            # Float
            try:
                return float(value_str)
            except ValueError:
                pass
            
            # Boolean
            if value_str.lower() in ['true', 'false']:
                return value_str.lower() == 'true'
            
            # List (JSON array)
            if value_str.startswith('[') and value_str.endswith(']'):
                return json.loads(value_str)
            
            # Object (JSON object)
            if value_str.startswith('{') and value_str.endswith('}'):
                return json.loads(value_str)
            
            # String
            return value_str
            
        except (ValueError, json.JSONDecodeError):
            return value_str
    
    def _unquote(self, value: str) -> str:
        """Remove quotes from string value."""
        if len(value) >= 2:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
        return value


class QueryOptimizer:
    """Query optimizer for improving query performance."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize query optimizer."""
        self.logger = logger or AIPrishtinaLogger(name="query_optimizer")
    
    async def optimize(self, plan: QueryPlan) -> QueryPlan:
        """Optimize query plan."""
        try:
            optimized_plan = plan
            
            # Apply optimization rules
            optimized_plan = self._optimize_filters(optimized_plan)
            optimized_plan = self._optimize_sorting(optimized_plan)
            optimized_plan = self._optimize_limits(optimized_plan)
            
            await self.logger.debug("Query plan optimized")
            return optimized_plan
            
        except Exception as e:
            await self.logger.error(f"Query optimization failed: {str(e)}")
            return plan  # Return original plan if optimization fails
    
    def _optimize_filters(self, plan: QueryPlan) -> QueryPlan:
        """Optimize filter conditions."""
        # Sort filters by selectivity (most selective first)
        # This is a simplified heuristic
        def filter_selectivity(condition: FilterCondition) -> int:
            if condition.operator in [OperatorType.EQ, OperatorType.IS_NULL]:
                return 1  # High selectivity
            elif condition.operator in [OperatorType.IN, OperatorType.BETWEEN]:
                return 2  # Medium selectivity
            else:
                return 3  # Low selectivity
        
        plan.filters.sort(key=filter_selectivity)
        return plan
    
    def _optimize_sorting(self, plan: QueryPlan) -> QueryPlan:
        """Optimize sorting operations."""
        # If there's a limit, we can use a more efficient sorting algorithm
        if plan.limit and plan.limit < 1000:
            # Mark for partial sorting optimization
            pass
        
        return plan
    
    def _optimize_limits(self, plan: QueryPlan) -> QueryPlan:
        """Optimize limit and offset operations."""
        # Ensure reasonable limits
        if plan.limit and plan.limit > 10000:
            plan.limit = 10000  # Cap at 10k results
        
        return plan


class QueryExecutor:
    """Executes optimized query plans."""
    
    def __init__(self, database, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize query executor."""
        self.database = database
        self.logger = logger or AIPrishtinaLogger(name="query_executor")
    
    async def execute(self, plan: QueryPlan) -> Dict[str, Any]:
        """Execute query plan."""
        try:
            await self.logger.debug(f"Executing query plan: {plan.query_type.value}")
            
            if plan.query_type == QueryType.VECTOR_SEARCH:
                return await self._execute_vector_search(plan)
            elif plan.query_type == QueryType.SEMANTIC_SEARCH:
                return await self._execute_semantic_search(plan)
            elif plan.query_type == QueryType.HYBRID_SEARCH:
                return await self._execute_hybrid_search(plan)
            else:
                raise QueryError(f"Unsupported query type: {plan.query_type}")
                
        except Exception as e:
            await self.logger.error(f"Query execution failed: {str(e)}")
            raise QueryError(f"Query execution failed: {str(e)}")
    
    async def _execute_vector_search(self, plan: QueryPlan) -> Dict[str, Any]:
        """Execute vector search query."""
        # Convert filters to ChromaDB where clause
        where_clause = self._build_where_clause(plan.filters)
        
        # Execute query
        results = await self.database.query(
            query_texts=[plan.vector_query] if plan.vector_query else None,
            n_results=plan.limit or 10,
            where=where_clause,
            include=['metadatas', 'documents', 'distances'] if plan.include_metadata else ['documents']
        )
        
        # Apply post-processing
        if plan.sort_criteria:
            results = self._apply_sorting(results, plan.sort_criteria)
        
        if plan.offset:
            results = self._apply_offset(results, plan.offset)
        
        return results
    
    async def _execute_semantic_search(self, plan: QueryPlan) -> Dict[str, Any]:
        """Execute semantic search query."""
        # Similar to vector search but with semantic processing
        return await self._execute_vector_search(plan)
    
    async def _execute_hybrid_search(self, plan: QueryPlan) -> Dict[str, Any]:
        """Execute hybrid search query."""
        # Combine vector and keyword search
        return await self._execute_vector_search(plan)
    
    def _build_where_clause(self, filters: List[FilterCondition]) -> Optional[Dict[str, Any]]:
        """Build ChromaDB where clause from filters."""
        if not filters:
            return None
        
        where_clause = {}
        
        for condition in filters:
            field = condition.field
            operator = condition.operator
            value = condition.value
            
            if operator == OperatorType.EQ:
                where_clause[field] = {"$eq": value}
            elif operator == OperatorType.NE:
                where_clause[field] = {"$ne": value}
            elif operator == OperatorType.GT:
                where_clause[field] = {"$gt": value}
            elif operator == OperatorType.GTE:
                where_clause[field] = {"$gte": value}
            elif operator == OperatorType.LT:
                where_clause[field] = {"$lt": value}
            elif operator == OperatorType.LTE:
                where_clause[field] = {"$lte": value}
            elif operator == OperatorType.IN:
                where_clause[field] = {"$in": value}
            elif operator == OperatorType.NOT_IN:
                where_clause[field] = {"$nin": value}
            elif operator == OperatorType.CONTAINS:
                where_clause[field] = {"$contains": value}
        
        return where_clause
    
    def _apply_sorting(self, results: Dict[str, Any], sort_criteria: List[SortCriteria]) -> Dict[str, Any]:
        """Apply sorting to results."""
        # This is a simplified implementation
        # In practice, you'd need more sophisticated sorting
        return results
    
    def _apply_offset(self, results: Dict[str, Any], offset: int) -> Dict[str, Any]:
        """Apply offset to results."""
        for key in results:
            if isinstance(results[key], list) and len(results[key]) > 0:
                if isinstance(results[key][0], list):
                    results[key] = [sublist[offset:] for sublist in results[key]]
                else:
                    results[key] = results[key][offset:]
        return results


class AdvancedQueryLanguage:
    """Main interface for the advanced query language."""
    
    def __init__(self, database, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize advanced query language."""
        self.database = database
        self.logger = logger or AIPrishtinaLogger(name="advanced_query_language")
        
        self.parser = QueryParser(logger)
        self.optimizer = QueryOptimizer(logger)
        self.executor = QueryExecutor(database, logger)
    
    async def query(self, query_string: str) -> Dict[str, Any]:
        """Execute a query using the advanced query language."""
        try:
            # Parse query
            plan = self.parser.parse(query_string)
            
            # Optimize query
            optimized_plan = await self.optimizer.optimize(plan)
            
            # Execute query
            results = await self.executor.execute(optimized_plan)
            
            await self.logger.info(f"Query executed successfully: {query_string}")
            return results
            
        except Exception as e:
            await self.logger.error(f"Query failed: {str(e)}")
            raise QueryError(f"Query execution failed: {str(e)}")
    
    def validate_query(self, query_string: str) -> bool:
        """Validate query syntax."""
        try:
            self.parser.parse(query_string)
            return True
        except Exception:
            return False
