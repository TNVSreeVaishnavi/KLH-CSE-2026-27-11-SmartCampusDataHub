from fastapi import APIRouter, Depends

from api.dependencies.services import get_lineage

router = APIRouter()


@router.get("")
def lineage(lineage=Depends(get_lineage)):
    return {
        "flow": lineage.get_pipeline_flow(),
        "stages": lineage.get_all_stages(),
        "domains": lineage.get_domain_path(),
    }
