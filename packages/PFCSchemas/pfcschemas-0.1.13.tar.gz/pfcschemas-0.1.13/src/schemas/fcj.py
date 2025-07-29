from __future__ import annotations

import datetime
import re

import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import Annotated


class FCJ(BaseModel):
    version: str
    comments: str
    name: str
    view: View
    parameters: Parameters
    scored: bool
    scores: list[float]
    human_scores: list[HumanResult] = []
    fcs_scores: list[Result] = []
    mans: list[Man]
    data: list[Data]
    jhash: int | None = None

    def score_df(self):
        return pd.concat(
            {fcjr.fa_version: fcjr.to_df() for fcjr in self.fcs_scores},
            axis=0,
            names=["version", "manoeuvre", "difficulty", "truncate"],
        )

    def man_df(self):
        return pd.DataFrame(
            [man.__dict__ for man in self.mans[1:-1]],
            index=pd.Index(range(len(self.mans[1:-1])), name="manoeuvre"),
        )

    def pfc_version_df(self):
        sdf = self.score_df().loc[pd.IndexSlice[:, :, 3, False]]
        return pd.concat(
            [sdf, sdf.mul(self.man_df().k, axis=0)], axis=1, keys=["raw", "kfac"]
        )

    def version_summary_df(self):
        return self.pfc_version_df().groupby("version").kfac.sum()

    def latest_version(self):
        return max([fcjr.fa_version for fcjr in self.fcs_scores])

    @property
    def id(self):
        return re.search(r"\d{8}", self.name)[0]

    @property
    def created(self):
        try:
            return datetime.datetime.strptime(
                re.search(r"_\d{2}_\d{2}_\d{2}_", self.name)[0], "_%y_%m_%d_"
            )
        except Exception:
            return None

    @property
    def origin(self):
        return Origin(
            lat=self.parameters.pilotLat,
            lng=self.parameters.pilotLng,
            alt=self.parameters.pilotAlt,
            heading=np.degrees(self.parameters.rotation),
            move_north=self.parameters.moveNorth,
            move_east=self.parameters.moveEast,
            move_down=self.parameters.elevate,
        )

class View(BaseModel):
    position: dict
    target: dict


class Parameters(BaseModel):
    rotation: float
    start: int
    stop: int
    moveEast: float
    moveNorth: float
    wingspan: float
    modelwingspan: float
    elevate: float
    originLat: float
    originLng: float
    originAlt: float
    pilotLat: str | float
    pilotLng: str | float
    pilotAlt: str | float
    centerLat: str | float
    centerLng: str | float
    centerAlt: str | float
    schedule: list[str]


class HumanResult(BaseModel):
    name: str
    date: datetime.date
    scores: list[float]


class Result(BaseModel):
    fa_version: str
    manresults: list[ManResult | None]

    def to_df(self) -> pd.DataFrame:
        return pd.concat(
            {i: fcjmr.to_df() for i, fcjmr in enumerate(self.manresults[1:]) if fcjmr},
            axis=0,
            names=["manoeuvre", "difficulty", "truncate"],
        )


class ManResult(BaseModel):
    els: list[El]
    results: list[Score] = []

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=[res.score.__dict__ for res in self.results],
            index=pd.MultiIndex.from_frame(
                pd.DataFrame([res.properties.__dict__ for res in self.results])
            ),
        )

    def get_score(self, props: ScoreProperties | None = None) -> ScoreValues | None:
        if props is None:
            props = ScoreProperties(difficulty=3, truncate=False)
        return [r for r in self.results if r.properties==props][0].score
        

class El(BaseModel):
    name: str
    start: float
    stop: float


class Score(BaseModel):
    score: ScoreValues
    properties: ScoreProperties


class ScoreValues(BaseModel):
    intra: float
    inter: float
    positioning: float
    total: float


class ScoreProperties(BaseModel):
    difficulty: int = 3
    truncate: bool = False

    def __eq__(self, other):
        if not isinstance(other, ScoreProperties):
            return False
        return self.difficulty == other.difficulty and self.truncate == other.truncate


class Man(BaseModel):
    name: str
    k: float
    id: str
    sp: int
    wd: float
    start: int
    stop: int
    sel: bool
    background: str


class Data(BaseModel):
    VN: float = None
    VE: float = None
    VD: float = None
    dPD: float = None  #
    r: float
    p: float
    yw: float
    N: float
    E: float
    D: float
    time: int
    roll: float
    pitch: float
    yaw: float


def get_scores(file: str) -> pd.DataFrame:
    fcj = FCJ.model_validate_json(open(file, "r").read())
    return fcj.pfc_version_df()


class Origin(BaseModel):
    lat: Annotated[float, "latitude in degrees"]
    lng: Annotated[float, "latitude in degrees"]
    alt: Annotated[float, "height AMSL in meters"]
    heading: Annotated[float, "heading (direction of box Y axis) in degrees from North"] 
    move_north: Annotated[float, "non-standard offset of box"]=0
    move_east: Annotated[float, "non-standard offset of box"]=0
    move_down: Annotated[float, "non-standard offset of box"]=0
    
    @staticmethod
    def zero():
        return Origin(lat=0, lng=0, alt=0, heading=0)