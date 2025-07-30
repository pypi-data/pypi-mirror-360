from dataclasses import dataclass, field
from typing import Any, TypeVar

import numpy as np
from numpy.typing import NDArray

from peakfit.typing import FloatArray

ArrayInt = NDArray[np.int_]
T = TypeVar("T", float, FloatArray)

P1_MIN = 175.0
P1_MAX = 185.0


@dataclass
class SpectralParameters:
    size: int
    sw: float
    obs: float
    car: float
    aq_time: float
    apocode: float
    apodq1: float
    apodq2: float
    apodq3: float
    p180: bool
    direct: bool
    ft: bool
    delta: float = field(init=False)
    first: float = field(init=False)

    def __post_init__(self) -> None:
        # derived units (these are in ppm)
        self.delta = (
            -self.sw / (self.size * self.obs) if self.size * self.obs != 0.0 else 0.0
        )
        self.first = (
            self.car / self.obs - self.delta * self.size / 2.0
            if self.obs != 0.0
            else 0.0
        )

    def hz2pts_delta(self, hz: T) -> T:
        return hz / (self.obs * self.delta)

    def pts2hz_delta(self, pts: T) -> T:
        return pts * self.obs * self.delta

    def hz2pts(self, hz: T) -> T:
        return ((hz / self.obs) - self.first) / self.delta

    def hz2pt_i(self, hz: float) -> int:
        return int(round(self.hz2pts(hz))) % self.size

    def pts2hz(self, pts: T) -> T:
        return (pts * self.delta + self.first) * self.obs

    def ppm2pts(self, ppm: T) -> T:
        return (ppm - self.first) / self.delta

    def ppm2pt_i(self, ppm: float) -> int:
        return int(round(self.ppm2pts(ppm))) % self.size

    def pts2ppm(self, pts: T) -> T:
        return (pts * self.delta) + self.first

    def hz2ppm(self, hz: T) -> T:
        return hz / self.obs


def read_spectral_parameters(
    dic: dict[str, Any], data: FloatArray
) -> list[SpectralParameters]:
    spec_params: list[SpectralParameters] = []

    for i in range(data.ndim):
        size = data.shape[i]
        fdf = f"FDF{int(dic['FDDIMORDER'][data.ndim - 1 - i])}"
        is_direct = i == data.ndim - 1
        ft = dic.get(f"{fdf}FTFLAG", 0.0) == 1.0

        if ft:
            sw = dic.get(f"{fdf}SW", 1.0)
            orig = dic.get(f"{fdf}ORIG", 0.0)
            obs = dic.get(f"{fdf}OBS", 1.0)
            car = orig + sw / 2.0 - sw / size
            aq_time = dic.get(f"{fdf}APOD", 0.0) / max(sw, 1e-6)
            p180 = P1_MIN <= abs(dic.get(f"{fdf}P1", 0.0)) <= P1_MAX
        else:
            sw = obs = car = aq_time = 1.0
            p180 = False

        spec_params.append(
            SpectralParameters(
                size=size,
                sw=sw,
                obs=obs,
                car=car,
                aq_time=aq_time,
                apocode=dic.get(f"{fdf}APODCODE", 0.0),
                apodq1=dic.get(f"{fdf}APODQ1", 0.0),
                apodq2=dic.get(f"{fdf}APODQ2", 0.0),
                apodq3=dic.get(f"{fdf}APODQ3", 0.0),
                p180=p180,
                direct=is_direct,
                ft=ft,
            )
        )

    return spec_params


# def calculate_acquisition_time(
#     dic: dict[str, Any], fdf: str, size: int, *, is_direct: bool
# ) -> float:
#     if dic.get(f"{fdf}FTSIZE", 0.0) == 0.0:
#         return 0.0

#     aq_time = dic[f"{fdf}TDSIZE"] / dic[f"{fdf}SW"] * size / dic[f"{fdf}FTSIZE"]

#     if is_direct:
#         aq_time *= 1.0 - dic.get("FDDMXVAL", 0.0) / dic[f"{fdf}TDSIZE"]

#     correction_factor = 1.0 if dic.get(f"{fdf}APODCODE", 0.0) == 1.0 else 0.5
#     aq_time *= 1.0 - correction_factor / dic[f"{fdf}TDSIZE"]

#     return aq_time
