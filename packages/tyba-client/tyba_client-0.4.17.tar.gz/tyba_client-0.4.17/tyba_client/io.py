from __future__ import annotations
from generation_models import (
    PVModuleMermoudLejeune,
    ONDInverter,
    ONDEfficiencyCurve,
    ONDTemperatureDerateCurve,
)
from warnings import warn

warn("""tyba_client.io is deprecated in favor of using generation_models.utils.pvsyst_readers. Tyba will
cease to support tyba_client.io on 6/1/2025. See https://docs.tybaenergy.com/api/index.html or reach out
to us for help migrating.""", FutureWarning)


def read_pvsyst_file(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            blob = {}
            trace = [blob]
            lines = [line for line in f.readlines() if "=" in line]
            indentations = [len(line) - len(line.lstrip()) for line in lines]
            for indentation, line in zip(indentations, lines):
                if divmod(indentation, 2)[1] != 0:
                    raise PVSystFileError(f"invalid indentation at {line}")
            structure = [
                (y - x) // 2 for x, y in zip(indentations[:-1], indentations[1:])
            ]
            structure.append(0)
            for line, typ in zip(lines, structure):
                stripped = line.strip()
                k, v = stripped.split("=")
                if typ == 0:
                    trace[-1][k] = v
                elif typ == 1:
                    trace[-1][k] = {"type": v, "items": {}}
                    trace.append(trace[-1][k]["items"])
                elif typ < 0:
                    trace[-1][k] = v
                    for _ in range(-1 * typ):
                        trace.pop()
                else:
                    raise PVSystFileError(f"invalid structure at {line}")
    except UnicodeDecodeError:
        raise PVSystFileError(
            f"File not utf-8 encoded. Please encode the file to utf-8 and try again"
        )
    return blob


class PVSystFileError(ValueError):
    """:meta private:"""

    pass


def pv_module_from_pan(
    pan_file: str,
    bifacial_ground_clearance_height=1.0,
    bifacial_transmission_factor: float = 0.013,
) -> PVModuleMermoudLejeune:
    """DEPRECATED. See :func:`generation_models.utils.pvsyst_readers.pv_module_from_pan`."""
    pan_blob = read_pvsyst_file(pan_file)
    data = pan_blob["PVObject_"]["items"]
    commercial = data["PVObject_Commercial"]["items"]
    if "PVObject_IAM" in data:
        iam_points = [
            v.split(",")
            for k, v in data["PVObject_IAM"]["items"]["IAMProfile"]["items"].items()
            if k.startswith("Point_")
        ]
        iam_angles = [float(v[0]) for v in iam_points]
        iam_values = [float(v[1]) for v in iam_points]
    else:
        iam_angles = None
        iam_values = None
    return PVModuleMermoudLejeune(
        bifacial="BifacialityFactor" in data,
        bifacial_transmission_factor=bifacial_transmission_factor,
        bifaciality=float(data.get("BifacialityFactor", 0.65)),
        bifacial_ground_clearance_height=bifacial_ground_clearance_height,
        n_parallel=int(data["NCelP"]),
        n_diodes=int(data["NDiode"]),
        n_series=int(data["NCelS"]),
        t_ref=float(data["TRef"]),
        s_ref=float(data["GRef"]),
        i_sc_ref=float(data["Isc"]),
        v_oc_ref=float(data["Voc"]),
        i_mp_ref=float(data["Imp"]),
        v_mp_ref=float(data["Vmp"]),
        alpha_sc=float(data["muISC"]) * 1e-3,  # TODO: check units
        beta_oc=float(data["muVocSpec"]) * 1e-3,
        n_0=float(data["Gamma"]),
        mu_n=float(data["muGamma"]),
        r_sh_ref=float(data["RShunt"]),
        r_s=float(data["RSerie"]),
        r_sh_0=float(data["Rp_0"]),
        r_sh_exp=float(data["Rp_Exp"]),
        tech=data["Technol"],
        length=float(commercial["Height"]),
        width=float(commercial["Width"]),
        # faiman cell temp model used by PVSyst
        t_c_fa_alpha=float(data["Absorb"]),
        # IAM
        iam_c_cs_iam_value=iam_values,
        iam_c_cs_inc_angle=iam_angles,
        custom_d2_mu_tau=data.get("D2MuTau"),
    )


def inverter_from_ond(ond_file: str, includes_xfmr: bool = True) -> ONDInverter:
    """DEPRECATED. See :func:`generation_models.utils.pvsyst_readers.inverter_from_ond`."""
    ond = read_pvsyst_file(ond_file)
    data = ond["PVObject_"]["items"]
    converter = data["Converter"]["items"]
    voltage_curve_points = [float(v) for v in converter["VNomEff"].split(",") if v]
    if len(voltage_curve_points) != 3:
        raise NotImplementedError(
            "OND Inverter only accepts voltage curves of length 3"
        )
    temp_derate_curve = ONDTemperatureDerateCurve(
        ambient_temp=[
            -300,
            float(converter["TPMax"]),
            float(converter["TPNom"]),
            float(converter["TPLim1"]),
            float(converter["TPLimAbs"]),
        ],
        max_ac_power=[
            float(converter["PMaxOUT"]) * 1e3,
            float(converter["PMaxOUT"]) * 1e3,
            float(converter["PNomConv"]) * 1e3,
            float(converter["PLim1"]) * 1e3,
            float(converter.get("PlimAbs", 0.0)) * 1e3,
        ],
    )
    raw_power_curves = [converter[f"ProfilPIOV{i}"]["items"] for i in [1, 2, 3]]
    power_curves = []
    for curve in raw_power_curves:
        points = [
            [float(v) for v in curve[f"Point_{i}"].split(",")]
            for i in range(1, int(curve["NPtsEff"]) + 1)
        ]
        dc, ac = zip(*points)
        power_curves.append(ONDEfficiencyCurve(dc_power=dc, ac_power=ac))
    aux_loss = data.get("Aux_Loss")
    aux_loss_threshold = data.get("Aux_Thresh")
    if aux_loss is not None:
        aux_loss = float(aux_loss)
        aux_loss_threshold = float(aux_loss_threshold)
    return ONDInverter(
        mppt_low=float(converter["VMppMin"]),
        mppt_high=float(converter["VMPPMax"]),
        paco=float(converter["PMaxOUT"]) * 1e3,
        vdco=voltage_curve_points[1],
        temp_derate_curve=temp_derate_curve,
        nominal_voltages=voltage_curve_points,
        power_curves=power_curves,
        dc_turn_on=float(converter["PSeuil"]),
        pnt=float(data["Night_Loss"]),
        aux_loss=aux_loss,
        aux_loss_threshold=aux_loss_threshold,
        includes_xfmr=includes_xfmr,
    )
