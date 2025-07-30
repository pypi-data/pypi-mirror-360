from typing import List, Dict, Any, Optional, Tuple

import deprecation
from urllib3.util.retry import Retry

from .helpers import ClientBase
from .util import json


class StagingClient(ClientBase):
    """Staging area API bindings"""

    def __init__(self, api_url: str,
                 api_key: Optional[str] = None,
                 token: Optional[str] = None,
                 name: str = '',
                 retry: Optional[Retry] = None,
                 ) -> None:
        super().__init__(api_url, user=None, pw=None, api_key=api_key, token=token, name=name,
                         retry=retry)

    @json
    def get_staging_building_details(self) -> List[Dict]:
        """Fetch building-level details for all buildings in staging"""
        return self.get('/staging')

    @json
    def update_building_details(self, building_id: int,
                                details: Dict[str, Any]) -> Dict:
        """Update building-level details for a building in staging"""
        return self.patch(f"/staging/{building_id}/details", json=details)

    @json
    @deprecation.deprecated(deprecated_in="1.14.0", details="Replaced with get_staging_equipment")
    def get_staged_equipment(self, building_id: int) -> Dict:
        """Fetch staging equipment as Python objects"""
        return self.get(f'/staging/{building_id}')

    @json
    @deprecation.deprecated(deprecated_in="1.14.0", details="get_staging_points and "
                                                            "get_staging_equipment can be used and"
                                                            " results joined together as needed")
    def get_equipment_and_points(self, building_id: int) -> Dict:
        """Fetch staging equipment and point details together as Python objects"""
        return self.get(f'/staging/{building_id}?points=true')

    @json
    @deprecation.deprecated(deprecated_in="1.14.0", details="replaced with get_staging_points")
    def get_staged_points(self, building_id: int) -> Dict:
        """Fetch staging points as Python objects"""
        return self.get(f'/staging/{building_id}/points')

    @json
    @deprecation.deprecated(deprecated_in="1.14.0", details="replaced with get_staging_devices")
    def get_staged_devices(self, building_id: int) -> Dict:
        """Fetch staging devices as Python objects"""
        return self.get(f'/staging/{building_id}/devices')

    @json
    def get_staging_devices(self, building_id: int) -> List[Dict]:
        """Fetch staging devices as Python objects"""
        return self.get(f'/staging/{building_id}/devices')

    @json
    def get_staging_points(self, building_id: int) -> List[Dict]:
        """Fetch staging points as Python objects"""
        return self.get(f'/staging/{building_id}/points')

    @json
    def get_staging_equipment(self, building_id: int) -> List[Dict]:
        """Fetch staging equipment as Python objects"""
        return self.get(f'/staging/{building_id}/equipment')

    @deprecation.deprecated(deprecated_in="1.14.0",
                            details="CSV paths removed, get_staging_points and "
                                    "get_staging_equipment can be used and results joined together"
                                    " as needed")
    def get_staged_equipment_csv(self, building_id: int) -> str:
        """Fetch staged equipment and points together in tabular form"""

        @json
        def get_csv():
            return self.get(f'/staging/{building_id}',
                            headers={'Accept': 'text/csv'})

        get_csv.raw_response = True  # type: ignore[attr-defined]
        return get_csv().text

    @json
    @deprecation.deprecated(deprecated_in="1.14.0", details="Use update_staging_equipment instead")
    def update_staged_equipment(self, building_id: int, updates: List[Dict]) -> Dict:
        """Update staged equipment and points"""
        return self.post(f'/staging/{building_id}', json=updates)

    @json
    def update_staging_devices(self, building_id: int, updates: List[Dict]) -> Dict:
        """Update staged equipment and points"""
        return self.patch(f'/staging/{building_id}/devices', json=updates)

    @json
    def update_staging_points(self, building_id: int, updates: List[Dict]) -> Dict:
        """Update staged equipment and points"""
        return self.patch(f'/staging/{building_id}/points', json=updates)

    @json
    def update_staging_equipment(self, building_id: int, updates: List[Dict]) -> Dict:
        """Update staged equipment and points"""
        return self.patch(f'/staging/{building_id}/equipment', json=updates)

    @json
    def validate_staging_building(self, building_id: int) -> Dict:
        """Validate staged equipment and points, returning any errors"""
        return self.get(f'/staging/{building_id}/validate')

    @json
    def promote_from_staging(self, building_id: int,
                             equip_ids: List[str] = [], topics: List[str] = []) -> Dict:
        """Promote valid equipment and points to the primary tables, returning any errors
        If equip_ids or topics lists are non-empty then only promote those objects. Otherwise
        all valid objects are promoted."""
        promote_req = {'equip_ids': equip_ids, 'topics': topics}
        return self.post(f'/staging/{building_id}/apply', json=promote_req)

    @json
    def unpromote_from_staging(self,
                               building_id: int,
                               equipment_ids: List[int] = [], point_ids: List[int] = [],
                               equipment_point_pairs: List[Tuple[int, int]] = []) -> Dict:
        """Unpromote valid equipment, points, and their relationships to the primary tables,
        returning any errors.
        If equip_ids or topics lists are non-empty then only promote those objects. Otherwise
        all valid objects are promoted."""
        promote_req = {'equipment_ids': equipment_ids, 'point_ids': point_ids,
                       'point_equipment_relationships': [
                           {'equipment_id': equipment_id, 'point_id': point_id} for
                           equipment_id, point_id in equipment_point_pairs]}
        return self.delete(f'/staging/{building_id}/apply', json=promote_req)

    @json
    def delete_staging_equipment(self, building_id: int, equip_ids: List[str]) -> Dict:
        """Delete staged equipment, returning object describing deleted equipment"""
        return self.delete(f'/staging/{building_id}/equipment', json=equip_ids)


class OnboardStagingClient(StagingClient):
    def __init__(self, api_key: str) -> None:
        super().__init__('https://api.onboarddata.io', api_key)
