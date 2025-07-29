"""
Tests for fileio.data_source module
"""

import unittest

from datetime import datetime
from pathlib import Path

from orsopy.fileio import Polarization, base, data_source

pth = Path(__file__).absolute().parent


class TestExperiment(unittest.TestCase):
    """
    Testing the Experiment class.
    """

    def test_creation(self):
        """
        Creation with minimal set.
        """
        value = data_source.Experiment("My First Experiment", "A Lab Instrument", datetime(1992, 7, 14), "x-ray")
        assert value.title == "My First Experiment"
        assert value.instrument == "A Lab Instrument"
        assert value.start_date == datetime(1992, 7, 14)
        assert value.probe == "x-ray"
        assert value.facility is None
        assert value.proposalID is None
        assert value.doi is None

    def test_to_yaml(self):
        """
        Transformation to yaml with minimal set.
        """
        value = data_source.Experiment("My First Experiment", "A Lab Instrument", datetime(1992, 7, 14), "x-ray")
        assert (
            value.to_yaml()
            == "title: My First Experiment\n"
            + "instrument: A Lab Instrument\nstart_date: 1992-07-14T00:00:00"
            + "\nprobe: x-ray\n"
        )

    def test_creation_optionals(self):
        """
        Creation with optionals.
        """
        value = data_source.Experiment(
            "My First Neutron Experiment",
            "TAS8",
            datetime(1992, 7, 14),
            "neutron",
            facility="Risoe",
            proposalID="abc123",
            doi="10.0000/abc1234",
        )
        assert value.title == "My First Neutron Experiment"
        assert value.instrument == "TAS8"
        assert value.start_date == datetime(1992, 7, 14)
        assert value.probe == "neutron"
        assert value.facility == "Risoe"
        assert value.proposalID == "abc123"
        assert value.doi == "10.0000/abc1234"

    def test_to_yaml_optionals(self):
        """
        Transformation to yaml with optionals.
        """
        value = data_source.Experiment(
            "My First Neutron Experiment",
            "TAS8",
            datetime(1992, 7, 14),
            "neutron",
            facility="Risoe",
            proposalID="abc123",
            doi="10.0000/abc1234",
        )
        assert value.to_yaml() == (
            "title: My First Neutron Experiment\n"
            "instrument: TAS8\nstart_date: 1992-07-14T00:00:00"
            "\nprobe: neutron\nfacility: Risoe\nproposalID: "
            "abc123\ndoi: 10.0000/abc1234\n"
        )


class TestSample(unittest.TestCase):
    """
    Testing for the Sample class.
    """

    def test_creation(self):
        """
        Creation with a minimal set.
        """
        value = data_source.Sample("A Perfect Sample")
        assert value.name == "A Perfect Sample"
        assert value.category is None
        assert value.composition is None
        assert value.description is None
        assert value.size is None
        assert value.environment is None
        assert value.sample_parameters is None

    def test_to_yaml(self):
        """
        Transformation to yaml with a minimal set.
        """
        value = data_source.Sample("A Perfect Sample")
        assert value.to_yaml() == "name: A Perfect Sample\n"

    def test_creation_optionals(self):
        """
        Creation with a optionals.
        """
        value = data_source.Sample(
            "A Perfect Sample",
            category="solid/gas",
            composition="Si | SiO2(20 A) | Fe(200 A) | air(beam side)",
            description="The sample is without flaws",
            environment=["Temperature cell"],
            size=base.ValueVector(1.0, 2.0, 3.0, "mm"),
            sample_parameters={"a": base.Value(13.4)},
        )
        assert value.name == "A Perfect Sample"
        assert value.category == "solid/gas"
        assert value.composition == "Si | SiO2(20 A) | " + "Fe(200 A) | air(beam side)"
        assert value.description == "The sample is without flaws"
        assert value.size == base.ValueVector(1.0, 2.0, 3.0, "mm")
        assert value.environment == ["Temperature cell"]
        assert value.sample_parameters == {"a": base.Value(13.4)}

    def test_to_yaml_optionals(self):
        """
        Transformation to yaml with optionals.
        """
        value = data_source.Sample(
            "A Perfect Sample",
            category="solid/gas",
            composition="Si | SiO2(20 A) | Fe(200 A) | air(beam side)",
            description="The sample is without flaws",
            environment=["Temperature cell"],
            size=base.ValueVector(1.0, 2.0, 3.0, "mm"),
            sample_parameters={"a": base.Value(13.4)},
        )
        assert (
            value.to_yaml()
            == "name: A Perfect Sample\ncategory: "
            + "solid/gas\ncomposition: Si | SiO2(20 A) | Fe(200 A) | air"
            + "(beam side)\ndescription: The sample is without flaws\n"
            + "size: {x: 1.0, y: 2.0, z: 3.0, unit: mm}\n"
            + "environment:\n- Temperature cell\n"
            + "sample_parameters:\n  a: {magnitude: 13.4}\n"
        )


class TestDataSource(unittest.TestCase):
    """
    Tests for the DataSource class.
    """

    def test_creation(self):
        """
        Creation with only default.
        """
        inst = data_source.InstrumentSettings(base.Value(0.25, unit="deg"), base.ValueRange(2, 20, unit="angstrom"))
        df = [base.File("1.nx.hdf", datetime.now()), base.File("2.nx.hdf", datetime.now())]
        m = data_source.Measurement(inst, df, scheme="angle-dispersive")

        value = data_source.DataSource(
            base.Person("A Person", "Some Uni"),
            data_source.Experiment("My First Experiment", "A Lab Instrument", datetime(1992, 7, 14), "x-ray"),
            data_source.Sample("A Perfect Sample"),
            m,
        )
        assert value.owner.name == "A Person"
        assert value.owner.affiliation == "Some Uni"
        assert value.experiment.title == "My First Experiment"
        assert value.experiment.instrument == "A Lab Instrument"
        assert value.experiment.start_date == datetime(1992, 7, 14)
        assert value.experiment.probe == "x-ray"
        assert value.sample.name == "A Perfect Sample"


class TestInstrumentSettings(unittest.TestCase):
    """
    Tests for the InstrumentSettings class.
    """

    def test_creation(self):
        """
        Creation with minimal settings.
        """
        value = data_source.InstrumentSettings(base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"),)
        assert value.incident_angle.magnitude == 4.0
        assert value.incident_angle.unit == "deg"
        assert value.wavelength.min == 2.0
        assert value.wavelength.max == 12.0
        assert value.wavelength.unit == "angstrom"
        assert value.polarization is Polarization.unpolarized
        assert value.configuration is None

    def test_to_yaml(self):
        """
        Transformation to yaml with minimal set.
        """
        value = data_source.InstrumentSettings(base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"),)
        assert value.to_yaml() == (
            "incident_angle: {magnitude: 4.0, unit: deg}\n"
            "wavelength: {min: 2.0, max: 12.0, unit: angstrom}\n"
            "polarization: unpolarized\n"
        )

    def test_creation_config_and_polarization(self):
        """
        Creation with optional items.
        """
        value = data_source.InstrumentSettings(
            base.Value(4.0, "deg"),
            base.ValueRange(2.0, 12.0, "angstrom"),
            polarization="po",
            configuration="liquid surface",
        )
        assert value.incident_angle.magnitude == 4.0
        assert value.incident_angle.unit == "deg"
        assert value.wavelength.min == 2.0
        assert value.wavelength.max == 12.0
        assert value.wavelength.unit == "angstrom"
        assert value.polarization == data_source.Polarization.po
        assert value.configuration == "liquid surface"

    def test_to_yaml_config_and_polarization(self):
        """
        Transformation to yaml with optional items.
        """
        value = data_source.InstrumentSettings(
            base.Value(4.0, "deg"),
            base.ValueRange(2.0, 12.0, "angstrom"),
            polarization="po",
            configuration="liquid surface",
        )
        assert (
            value.to_yaml()
            == "incident_angle: {magnitude: 4.0, unit: deg}\n"
            + "wavelength: {min: 2.0, max: 12.0, unit: angstrom}\n"
            + "polarization: po\n"
            + "configuration: liquid surface\n"
        )

    def test_wrong_polarization(self):
        with self.assertWarns(RuntimeWarning):
            data_source.InstrumentSettings(
                base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"), polarization="p",
            )


class TestMeasurement(unittest.TestCase):
    """
    Tests for the Measurement class.
    """

    def test_creation(self):
        """
        Creation with minimal set.
        """
        fname = pth / "not_orso.ort"
        value = data_source.Measurement(
            data_source.InstrumentSettings(base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"),),
            [base.File(str(fname), None)],
        )
        assert value.instrument_settings.incident_angle.magnitude == 4.0
        assert value.instrument_settings.incident_angle.unit == "deg"
        assert value.instrument_settings.wavelength.min == 2.0
        assert value.instrument_settings.wavelength.max == 12.0
        assert value.instrument_settings.wavelength.unit == "angstrom"
        assert value.data_files[0].file == str(pth / "not_orso.ort")
        assert value.data_files[0].timestamp == datetime.fromtimestamp(fname.stat().st_mtime)

    def test_to_yaml(self):
        """
        Transform to yaml with minimal set.
        """
        fname = pth / "not_orso.ort"

        value = data_source.Measurement(
            data_source.InstrumentSettings(base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"),),
            [base.File(str(fname), None)],
        )
        assert value.to_yaml() == (
            "instrument_settings:\n"
            "  incident_angle: {magnitude: 4.0, unit: deg}\n"
            "  wavelength: {min: 2.0, max: 12.0, unit: angstrom}\n"
            "  polarization: unpolarized\n"
            "data_files:\n"
            f"- file: {str(fname.absolute())}\n"
            f"  timestamp: {datetime.fromtimestamp(fname.stat().st_mtime).isoformat()}\n"
        )

    def test_creation_optionals(self):
        """
        Creation with optionals.
        """
        fname0 = pth / "not_orso.ort"
        fname1 = pth / "test_base.py"

        value = data_source.Measurement(
            data_source.InstrumentSettings(base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"),),
            [base.File(str(fname0), None)],
            [base.File(str(fname1), None)],
        )
        assert value.instrument_settings.incident_angle.magnitude == 4.0
        assert value.instrument_settings.incident_angle.unit == "deg"
        assert value.instrument_settings.wavelength.min == 2.0
        assert value.instrument_settings.wavelength.max == 12.0
        assert value.instrument_settings.wavelength.unit == "angstrom"
        assert value.data_files[0].file == str(fname0)
        assert value.data_files[0].timestamp == datetime.fromtimestamp(fname0.stat().st_mtime)
        assert value.additional_files[0].file == str(fname1)
        assert value.additional_files[0].timestamp == datetime.fromtimestamp(fname1.stat().st_mtime)

    def test_to_yaml_optionals(self):
        """
        Transform to yaml with optionals.
        """
        fname0 = pth / "not_orso.ort"
        fname1 = pth / "test_base.py"

        value = data_source.Measurement(
            data_source.InstrumentSettings(base.Value(4.0, "deg"), base.ValueRange(2.0, 12.0, "angstrom"),),
            [base.File(str(fname0), None)],
            [base.File(str(fname1), None)],
            "energy-dispersive",
        )
        cmpstr = (
            "instrument_settings:\n"
            "  incident_angle: {magnitude: 4.0, unit: deg}\n"
            "  wavelength: {min: 2.0, max: 12.0, unit: angstrom}\n"
            "  polarization: unpolarized\n"
            "data_files:\n"
            f"- file: {str(fname0.absolute())}\n"
            f"  timestamp: {datetime.fromtimestamp(fname0.stat().st_mtime).isoformat()}\n"
            "additional_files:\n"
            f"- file: {str(fname1.absolute())}\n"
            f"  timestamp: {datetime.fromtimestamp(fname1.stat().st_mtime).isoformat()}\n"
            "scheme: energy-dispersive\n"
        )
        assert cmpstr == value.to_yaml()
