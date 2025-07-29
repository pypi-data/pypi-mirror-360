"""Lunch Money MCP Server"""

import os
import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Initialize the MCP server
server = Server("lunchmoney-mcp")

# Configuration
API_BASE_URL = "https://dev.lunchmoney.app"
ACCESS_TOKEN = os.getenv("LUNCHMONEY_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    import sys
    print("Error: LUNCHMONEY_ACCESS_TOKEN environment variable is required", file=sys.stderr)
    print("Get your token from: https://my.lunchmoney.app/developers", file=sys.stderr)
    sys.exit(1)

# HTTP client configuration
async def get_http_client() -> httpx.AsyncClient:
    """Get configured HTTP client"""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )

# Pydantic models for request/response validation
class UserResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    account_id: int
    budget_name: str
    api_key_label: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_income: bool
    exclude_from_budget: bool
    exclude_from_totals: bool
    archived: bool
    archived_on: Optional[str] = None
    updated_at: str
    created_at: str
    is_group: bool
    group_id: Optional[int] = None
    order: Optional[int] = None

class TransactionResponse(BaseModel):
    id: int
    date: str
    amount: str
    currency: str
    to_base: float
    payee: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_group_id: Optional[int] = None
    category_group_name: Optional[str] = None
    is_income: bool
    exclude_from_budget: bool
    exclude_from_totals: bool
    created_at: str
    updated_at: str
    status: str
    is_pending: bool
    date_created: str
    group_id: Optional[int] = None
    parent_id: Optional[int] = None
    is_group: bool
    group_description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    external_id: Optional[str] = None

# MCP Tools Implementation

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available Lunch Money API tools"""
    return [
        # User tools
        Tool(
            name="get_user",
            description="Get user information including account details and preferences",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Category tools
        Tool(
            name="get_all_categories",
            description="Get all categories with optional format (nested or flattened)",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["nested", "flattened"],
                        "description": "Format for category response"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_single_category",
            description="Get details of a specific category by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "category_id": {
                        "type": "integer",
                        "description": "ID of the category to retrieve"
                    }
                },
                "required": ["category_id"]
            }
        ),
        
        Tool(
            name="create_category",
            description="Create a new category",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the category"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the category"
                    },
                    "is_income": {
                        "type": "boolean",
                        "description": "Whether this is an income category"
                    },
                    "exclude_from_budget": {
                        "type": "boolean",
                        "description": "Whether to exclude from budget"
                    },
                    "exclude_from_totals": {
                        "type": "boolean",
                        "description": "Whether to exclude from totals"
                    },
                    "archived": {
                        "type": "boolean",
                        "description": "Whether the category is archived"
                    },
                    "group_id": {
                        "type": "integer",
                        "description": "ID of the category group"
                    }
                },
                "required": ["name"]
            }
        ),
        
        Tool(
            name="update_category",
            description="Update an existing category",
            inputSchema={
                "type": "object",
                "properties": {
                    "category_id": {
                        "type": "integer",
                        "description": "ID of the category to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the category"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the category"
                    },
                    "is_income": {
                        "type": "boolean",
                        "description": "Whether this is an income category"
                    },
                    "exclude_from_budget": {
                        "type": "boolean",
                        "description": "Whether to exclude from budget"
                    },
                    "exclude_from_totals": {
                        "type": "boolean",
                        "description": "Whether to exclude from totals"
                    },
                    "archived": {
                        "type": "boolean",
                        "description": "Whether the category is archived"
                    },
                    "group_id": {
                        "type": "integer",
                        "description": "ID of the category group"
                    }
                },
                "required": ["category_id"]
            }
        ),
        
        Tool(
            name="delete_category",
            description="Delete a category (soft delete)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category_id": {
                        "type": "integer",
                        "description": "ID of the category to delete"
                    }
                },
                "required": ["category_id"]
            }
        ),
        
        # Transaction tools
        Tool(
            name="get_all_transactions",
            description="Get all transactions with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_id": {
                        "type": "integer",
                        "description": "Filter by tag ID"
                    },
                    "recurring_id": {
                        "type": "integer",
                        "description": "Filter by recurring item ID"
                    },
                    "plaid_account_id": {
                        "type": "integer",
                        "description": "Filter by Plaid account ID"
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Filter by category ID"
                    },
                    "asset_id": {
                        "type": "integer",
                        "description": "Filter by asset ID"
                    },
                    "group_id": {
                        "type": "integer",
                        "description": "Filter by group ID"
                    },
                    "is_group": {
                        "type": "boolean",
                        "description": "Filter by group transactions"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["cleared", "uncleared", "recurring", "recurring_suggested"],
                        "description": "Filter by transaction status"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Limit for pagination"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date filter (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date filter (YYYY-MM-DD)"
                    },
                    "debit_as_negative": {
                        "type": "boolean",
                        "description": "Return debit amounts as negative"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_single_transaction",
            description="Get details of a specific transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "integer",
                        "description": "ID of the transaction to retrieve"
                    },
                    "debit_as_negative": {
                        "type": "boolean",
                        "description": "Return debit amounts as negative"
                    }
                },
                "required": ["transaction_id"]
            }
        ),
        
        Tool(
            name="insert_transactions",
            description="Insert one or more transactions",
            inputSchema={
                "type": "object",
                "properties": {
                    "transactions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "Date in ISO format (YYYY-MM-DD)"
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Amount of the transaction"
                                },
                                "currency": {
                                    "type": "string",
                                    "description": "Currency code (e.g., USD, EUR)"
                                },
                                "asset_id": {
                                    "type": "integer",
                                    "description": "Asset/account ID"
                                },
                                "payee": {
                                    "type": "string",
                                    "description": "Payee name"
                                },
                                "category_id": {
                                    "type": "integer",
                                    "description": "Category ID"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "Transaction notes"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["cleared", "uncleared"],
                                    "description": "Transaction status"
                                },
                                "external_id": {
                                    "type": "string",
                                    "description": "External ID for the transaction"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "description": "Array of tag IDs"
                                },
                                "plaid_account_id": {
                                    "type": "integer",
                                    "description": "Plaid account ID"
                                }
                            },
                            "required": ["date", "amount", "currency", "asset_id", "payee"]
                        }
                    },
                    "apply_rules": {
                        "type": "boolean",
                        "description": "Whether to apply rules to the transactions"
                    },
                    "skip_duplicates": {
                        "type": "boolean",
                        "description": "Whether to skip duplicate transactions"
                    },
                    "check_for_recurring": {
                        "type": "boolean",
                        "description": "Whether to check for recurring transactions"
                    },
                    "debit_as_negative": {
                        "type": "boolean",
                        "description": "Treat debit amounts as negative"
                    },
                    "skip_balance_update": {
                        "type": "boolean",
                        "description": "Whether to skip balance update"
                    }
                },
                "required": ["transactions"]
            }
        ),
        
        Tool(
            name="update_transaction",
            description="Update a specific transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "integer",
                        "description": "ID of the transaction to update"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in ISO format (YYYY-MM-DD)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of the transaction"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (e.g., USD, EUR)"
                    },
                    "payee": {
                        "type": "string",
                        "description": "Payee name"
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Category ID"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Transaction notes"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["cleared", "uncleared"],
                        "description": "Transaction status"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Array of tag IDs"
                    },
                    "plaid_account_id": {
                        "type": "integer",
                        "description": "Plaid account ID"
                    },
                    "debit_as_negative": {
                        "type": "boolean",
                        "description": "Treat debit amounts as negative"
                    },
                    "skip_balance_update": {
                        "type": "boolean",
                        "description": "Whether to skip balance update"
                    }
                },
                "required": ["transaction_id"]
            }
        ),
        
        # Tag tools
        Tool(
            name="get_all_tags",
            description="Get all tags",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Asset tools
        Tool(
            name="get_all_assets",
            description="Get all assets (accounts)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="create_asset",
            description="Create a new asset/account",
            inputSchema={
                "type": "object",
                "properties": {
                    "type_name": {
                        "type": "string",
                        "description": "Type of asset (e.g., 'checking', 'savings', 'credit')"
                    },
                    "subtype_name": {
                        "type": "string",
                        "description": "Subtype of asset"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the asset"
                    },
                    "display_name": {
                        "type": "string",
                        "description": "Display name for the asset"
                    },
                    "balance": {
                        "type": "number",
                        "description": "Current balance"
                    },
                    "balance_as_of": {
                        "type": "string",
                        "description": "Date of the balance (YYYY-MM-DD)"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code"
                    },
                    "institution_name": {
                        "type": "string",
                        "description": "Institution name"
                    }
                },
                "required": ["type_name", "name", "balance", "balance_as_of", "currency"]
            }
        ),
        
        Tool(
            name="update_asset",
            description="Update an existing asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "integer",
                        "description": "ID of the asset to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the asset"
                    },
                    "display_name": {
                        "type": "string",
                        "description": "Display name for the asset"
                    },
                    "balance": {
                        "type": "number",
                        "description": "Current balance"
                    },
                    "balance_as_of": {
                        "type": "string",
                        "description": "Date of the balance (YYYY-MM-DD)"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code"
                    },
                    "institution_name": {
                        "type": "string",
                        "description": "Institution name"
                    }
                },
                "required": ["asset_id"]
            }
        ),
        
        # Budget tools
        Tool(
            name="get_budget_summary",
            description="Get budget summary for a specific period",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        
        Tool(
            name="upsert_budget",
            description="Create or update budget data",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Category ID"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Budget amount"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code"
                    }
                },
                "required": ["start_date", "category_id", "amount"]
            }
        ),
        
        # Recurring items tools
        Tool(
            name="get_recurring_items",
            description="Get all recurring items",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Plaid account tools
        Tool(
            name="get_all_plaid_accounts",
            description="Get all Plaid accounts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="trigger_plaid_fetch",
            description="Trigger a fetch for latest data from Plaid",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for fetch (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for fetch (YYYY-MM-DD)"
                    },
                    "plaid_account_id": {
                        "type": "integer",
                        "description": "Specific Plaid account ID to fetch"
                    }
                },
                "required": []
            }
        ),
        
        # Crypto tools
        Tool(
            name="get_all_crypto",
            description="Get all crypto assets",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="update_manual_crypto",
            description="Update a manual crypto asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "crypto_id": {
                        "type": "integer",
                        "description": "ID of the crypto asset to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the crypto asset"
                    },
                    "display_name": {
                        "type": "string",
                        "description": "Display name"
                    },
                    "institution_name": {
                        "type": "string",
                        "description": "Institution name"
                    },
                    "balance": {
                        "type": "number",
                        "description": "Current balance"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Cryptocurrency symbol"
                    }
                },
                "required": ["crypto_id"]
            }
        )
    ]

# Tool call handlers
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    async with get_http_client() as client:
        try:
            if name == "get_user":
                response = await client.get("/v1/me")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_all_categories":
                params = {}
                if "format" in arguments:
                    params["format"] = arguments["format"]
                response = await client.get("/v1/categories", params=params)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_single_category":
                category_id = arguments["category_id"]
                response = await client.get(f"/v1/categories/{category_id}")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "create_category":
                response = await client.post("/v1/categories", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "update_category":
                category_id = arguments.pop("category_id")
                response = await client.put(f"/v1/categories/{category_id}", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "delete_category":
                category_id = arguments["category_id"]
                response = await client.delete(f"/v1/categories/{category_id}")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_all_transactions":
                params = {k: v for k, v in arguments.items() if v is not None}
                response = await client.get("/v1/transactions", params=params)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_single_transaction":
                transaction_id = arguments["transaction_id"]
                params = {}
                if "debit_as_negative" in arguments:
                    params["debit_as_negative"] = arguments["debit_as_negative"]
                response = await client.get(f"/v1/transactions/{transaction_id}", params=params)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "insert_transactions":
                response = await client.post("/v1/transactions", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "update_transaction":
                transaction_id = arguments.pop("transaction_id")
                response = await client.put(f"/v1/transactions/{transaction_id}", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_all_tags":
                response = await client.get("/v1/tags")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_all_assets":
                response = await client.get("/v1/assets")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "create_asset":
                response = await client.post("/v1/assets", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "update_asset":
                asset_id = arguments.pop("asset_id")
                response = await client.put(f"/v1/assets/{asset_id}", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_budget_summary":
                params = {k: v for k, v in arguments.items() if v is not None}
                response = await client.get("/v1/budgets", params=params)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "upsert_budget":
                response = await client.put("/v1/budgets", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_recurring_items":
                response = await client.get("/v1/recurring_items")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_all_plaid_accounts":
                response = await client.get("/v1/plaid_accounts")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "trigger_plaid_fetch":
                response = await client.post("/v1/plaid_accounts/fetch", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "get_all_crypto":
                response = await client.get("/v1/crypto")
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            elif name == "update_manual_crypto":
                crypto_id = arguments.pop("crypto_id")
                response = await client.put(f"/v1/crypto/manual/{crypto_id}", json=arguments)
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main server entry point"""
    import sys
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("Lunch Money MCP Server")
            print("=" * 30)
            print("A Model Context Protocol server for Lunch Money API")
            print()
            print("Usage:")
            print("  lunchmoney-mcp                    # Start MCP server")
            print("  lunchmoney-mcp --help            # Show this help")
            print("  lunchmoney-mcp --version         # Show version")
            print()
            print("Environment Variables:")
            print("  LUNCHMONEY_ACCESS_TOKEN          # Your Lunch Money API token")
            print("                                   # Get from: https://my.lunchmoney.app/developers")
            print()
            print("Documentation: https://github.com/yourusername/lunchmoney-mcp")
            return
        elif sys.argv[1] in ['--version', '-v']:
            from . import __version__
            print(f"lunchmoney-mcp {__version__}")
            return
    
    # Start the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 