import uuid
from hashlib import sha512

import numpy as np
from pydantic import BaseModel, Field, model_validator


class Epoch(BaseModel):
    L_0: int | float | None = None
    p0: list[float] | None = Field(repr=True, default=None)
    arrival_rate: float
    service_rate: float
    duration: float | None = None
    ls_max: int
    off_set: float | None = 0.0
    time_step: float

    @model_validator(mode="after")
    def check_initial(self):
        if self.L_0 is not None and self.p0 is not None:
            raise ValueError("Only L0 or p0 should be passed.")
        if self.p0 is not None and len(self.p0) != self.ls_max + 1:
            raise ValueError(
                f"Len of p0 ({len(self.p0)}) does not match ls_max ({self.ls_max})"
            )
        if self.L_0 is not None:
            if self.L_0 != int(self.L_0):
                self.p0 = [0] * (self.ls_max + 1)
                low = int(np.floor(self.L_0))
                high = low + 1
                if high < len(self.p0):
                    self.p0[low] = high - self.L_0
                    self.p0[high] = self.L_0 - low
                    self.L_0 = None
                else:
                    raise ValueError(f"lsmax={self.ls_max} is too low.")
            else:
                self.L_0 = int(self.L_0)

        return self

    def __hash__(self):
        return int.from_bytes(
            sha512(
                f"{self.__class__.__qualname__}::{self.model_dump_json()}".encode(
                    "utf-8", errors="ignore"
                )
            ).digest(),
            byteorder="big",
        )


class TimeDependentCase(BaseModel):
    L_0: int
    durations: list[float]
    arrival_rates: list[float]
    service_rates: list[float]
    ls_max: int
    time_step: float
    case_id: str | None = None

    @model_validator(mode="after")
    def validate_lengths(self):
        if (n_arr := len(self.arrival_rates)) != (
            n_srv := len(self.service_rates)
        ):
            raise ValueError(
                f"Len of arrival rates {n_arr} != len of service rates {n_srv}"
            )
        if self.case_id is None:
            self.case_id = uuid.uuid4()
        return self

    @property
    def n_epochs(self) -> int:
        return len(self.arrival_rates)

    def iter_epochs(self) -> list[Epoch]:
        current_t_end = 0
        for e, (duration, arrival_rate, service_rate) in enumerate(
            zip(self.durations, self.arrival_rates, self.service_rates)
        ):
            yield Epoch(
                arrival_rate=arrival_rate,
                service_rate=service_rate,
                time_step=self.time_step,
                ls_max=self.ls_max,
                L_0=self.L_0 if e == 0 else None,
                duration=duration,
                off_set=current_t_end,
            )
            current_t_end += duration
