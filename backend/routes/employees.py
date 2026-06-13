from fastapi import APIRouter, HTTPException

from backend.services.employee_lookup import get_employees_by_department

router = APIRouter(prefix="/api", tags=["employees"])


@router.get("/employees/{department}")
async def fetch_employees(department: str):
    """
    Query Splunk for all employees in a given department.
    Used by the frontend to auto-populate campaign recipients.
    """
    try:
        employees = get_employees_by_department(department)
        return {"department": department, "employees": employees, "count": len(employees)}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach Splunk: {e}. Check SPLUNK_MCP_ENDPOINT and SPLUNK_MCP_TOKEN.",
        )
