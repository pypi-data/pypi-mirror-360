"""Models to create data instances."""

import datetime
from typing import List, Optional

from pandas import concat
from pydantic import BaseModel

from formations_api.utils import formations_to_df, metadata_to_df


class CrFormat(BaseModel):
    filename: str
    dir_cr_format: str
    revised_metadata: Optional[bool] = None
    revised_formation_top: Optional[bool] = None
    validated: Optional[bool] = None
    id: Optional[int] = None


class RawData(BaseModel):
    wellname: str
    uwi: str
    md: str
    units_md: str
    tvd: str
    units_tvd: str
    field: str
    company: str
    contract: str
    start_date: str
    end_date: str
    coor_syst: str
    coor_orig: str
    x_coor_bottom: str
    y_coor_bottom: str
    x_coor_rig: str
    y_coor_rig: str
    structure: str
    rotatory_table: str
    units_rotatory: str
    ground_elv: str
    units_ground: str
    units_formations: str
    cr_format_id: Optional[int] = None
    id: Optional[int] = None


class RevisedData(BaseModel):
    date: Optional[datetime.datetime] = None
    reviser_id: Optional[int] = None
    wellname: Optional[str] = None
    uwi: Optional[str] = None
    md: Optional[float] = None
    units_md: Optional[str] = None
    tvd: Optional[float] = None
    units_tvd: Optional[str] = None
    field: Optional[str] = None
    company: Optional[str] = None
    contract: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    coor_syst: Optional[str] = None
    coor_orig: Optional[str] = None
    x_coor_bottom: Optional[float] = None
    y_coor_bottom: Optional[float] = None
    x_coor_rig: Optional[float] = None
    y_coor_rig: Optional[float] = None
    structure: Optional[str] = None
    rotatory_table: Optional[float] = None
    units_rotatory: Optional[str] = None
    ground_elv: Optional[float] = None
    units_ground: Optional[str] = None
    units_formations: Optional[str] = None
    revised: Optional[bool] = None  # TODO: Eliminated this field when Jose updates the DB.
    cr_format_id: Optional[int] = None
    id: Optional[int] = None


class FormationTop(BaseModel):
    name: Optional[str] = None
    top_md: Optional[str] = None
    top_tvd: Optional[str] = None
    top_tvdss: Optional[str] = None
    base_md: Optional[str] = None
    base_tvd: Optional[str] = None
    base_tvdss: Optional[str] = None
    thickness_md: Optional[str] = None
    thickness_tvd: Optional[str] = None
    thickness_tvdss: Optional[str] = None
    raw_data_id: Optional[int] = None
    id: Optional[int] = None


class RevisedFormationTop(BaseModel):
    date: Optional[datetime.datetime] = None
    reviser_id: Optional[int] = None
    name: Optional[str] = None
    top_md: Optional[float] = None
    top_tvd: Optional[float] = None
    top_tvdss: Optional[float] = None
    base_md: Optional[float] = None
    base_tvd: Optional[float] = None
    base_tvdss: Optional[float] = None
    thickness_md: Optional[float] = None
    thickness_tvd: Optional[float] = None
    thickness_tvdss: Optional[float] = None
    revised: Optional[bool] = None
    revised_data_id: Optional[int] = None
    id: Optional[int] = None


class RawDataFormations(RawData):
    formations: Optional[List[FormationTop]] = None

    @property
    def df(self):
        return metadata_to_df(self)

    @property
    def formations_df(self):
        return formations_to_df(self.formations)


class RevisedDataFormation(RevisedData):
    formations: Optional[List[RevisedFormationTop]] = None

    @property
    def df(self):
        return metadata_to_df(self)

    @property
    def formations_df(self):
        return formations_to_df(self.formations)


class CrFormatData(CrFormat):
    raw_data: RawDataFormations
    revised_data: RevisedDataFormation

    @property
    def metadata_df(self):
        raw = self.raw_data.df
        rev = self.revised_data.df
        data = concat([raw, rev], ignore_index=True).T.reset_index()

        return data.rename(columns={"index": self.filename, 0: "Original", 1: "Changes"})
