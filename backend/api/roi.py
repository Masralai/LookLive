from fastapi import APIRouter

router = APIRouter()
latest_roi = None

def set_roi(roi_data):
    global latest_roi
    latest_roi = roi_data

def get_roi():
    return latest_roi

@router.get("/roi")
async def get_latest_roi():
    """Return latest ROI data"""
    return {"roi": latest_roi}
