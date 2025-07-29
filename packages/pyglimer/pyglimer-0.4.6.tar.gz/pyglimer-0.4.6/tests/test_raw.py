'''
:copyright:
   The PyGLImER development team (makus@gfz-potsdam.de).
:license:
   GNU Lesser General Public License, Version 3
   (https://www.gnu.org/copyleft/lesser.html)
:author:
   Peter Makus (makus@gfz-potsdam.de)

Created: Thursday, 8th September 2022 04:26:34 pm
Last Modified: Friday, 16th September 2022 02:42:07 pm
'''


import unittest
from unittest import mock
from unittest.mock import call, patch, MagicMock
import warnings
import os

from obspy import read, UTCDateTime, Stream, read_inventory
import numpy as np
import h5py

from pyglimer.database import raw
from pyglimer.utils import utils as pu


class TestConvertHeaderToHDF5(unittest.TestCase):
    def setUp(self):
        tr = read()[0]
        tr.decimate(4)  # so processing key is not empty
        self.stats = tr.stats

    def test_no_utc(self):
        # Check that all utcdatetime objects are now strings
        dataset = MagicMock()
        dataset.attrs = {}
        raw.convert_header_to_hdf5(dataset, self.stats)
        for v in dataset.attrs.values():
            self.assertNotIsInstance(v, UTCDateTime)

    def test_length(self):
        # Check that all keys are transferred
        dataset = MagicMock()
        dataset.attrs = {}
        raw.convert_header_to_hdf5(dataset, self.stats)
        self.assertEqual(dataset.attrs.keys(), self.stats.keys())


class TestReadHDF5Header(unittest.TestCase):
    def setUp(self) -> None:
        self.tr = read()[0]

    def test_result(self):
        dataset = MagicMock()
        dataset.attrs = {}
        self.tr.decimate(4)  # to put something into processing
        stats = self.tr.stats
        raw.convert_header_to_hdf5(dataset, stats)
        self.assertEqual(raw.read_hdf5_header(dataset), stats)

    def test_result_julday360(self):
        # There was a bug with that
        dataset = MagicMock()
        dataset.attrs = {}
        tr = read()[0]
        tr.decimate(4)  # to put something into processing
        stats = tr.stats
        self.tr.stats.starttime = UTCDateTime(
            year=2015, julday=360, hour=15, minute=3)
        raw.convert_header_to_hdf5(dataset, stats)
        self.assertEqual(raw.read_hdf5_header(dataset), stats)


def create_group_mock(d: dict, name: str, group: bool):
    """
    This is supposed to immitate the properties of
    :class:`h5py._hl.group.Group`

    :param d: dictionary
    :type d: dict
    :return: the mocked class
    :rtype: MagicMock
    """
    if group:
        m = MagicMock(spec=h5py._hl.group.Group)
    else:
        m = MagicMock()
    m.name = name
    m.__getitem__.side_effect = d.__getitem__
    m.__iter__.side_effect = d.__iter__
    m.__contains__.side_effect = d.__contains__
    m.keys.side_effect = d.keys
    m.values.side_effect = d.values
    return m


class TestAllTracesRecursive(unittest.TestCase):
    # The only thing I can do here is testing whether the conditions work
    @patch('pyglimer.database.raw.read_hdf5_header')
    def test_is_np_array(self, read_header_mock):
        read_header_mock.return_value = None
        d = {
            'a': create_group_mock({}, '/outer_group/testname', False),
            'b': create_group_mock({}, '/outer_group/different_name', False)}

        g = create_group_mock(d, '/outer_group', True)
        st = Stream()
        st = raw.all_traces_recursive(g, st, '/outer_group/testname')
        self.assertEqual(st.count(), 1)
        st = raw.all_traces_recursive(
            g, st.clear(), '/outer_group/different_name')
        self.assertEqual(st.count(), 1)
        st = raw.all_traces_recursive(g, st.clear(), '*name')
        self.assertEqual(st.count(), 2)
        st = raw.all_traces_recursive(g, st.clear(), 'no_match')
        self.assertEqual(st.count(), 0)

    @patch('pyglimer.database.raw.read_hdf5_header')
    def test_recursive(self, read_header_mock):
        # For this we need to patch fnmatch as well, as the names here aren't
        # full path
        read_header_mock.return_value = None
        d_innera = {
            'a': create_group_mock({}, '/outout/outer_group0/testname', False),
            'b': create_group_mock(
                {}, '/outout/outer_group0/different_name', False)}
        d_innerb = {
            'a': create_group_mock({}, '/outout/outer_group1/testname', False),
            'b': create_group_mock(
                {}, '/outout/outer_group1/different_name', False)}
        d_outer = {
            'A': create_group_mock(d_innera, '/outout/outer_group0', True),
            'B': create_group_mock(d_innerb, '/outout/outer_group1', True)}
        g = create_group_mock(d_outer, 'outout', True)
        st = Stream()
        st = raw.all_traces_recursive(
            g, st, '/outout/outer_group1/testname')
        self.assertEqual(st.count(), 1)
        st = raw.all_traces_recursive(g, st.clear(), '*')
        self.assertEqual(st.count(), 4)


class TestDBHandler(unittest.TestCase):
    @patch('pyglimer.database.raw.h5py.File.__init__')
    def setUp(self, super_mock):
        self.file_mock = MagicMock()
        super_mock.return_value = self.file_mock
        self.dbh = raw.DBHandler('a', 'r', 'gzip9')
        tr = read()[0]
        tr.data = np.ones_like(tr.data, dtype=int)
        tr.stats['phase'] = 'P'
        tr.stats['pol'] = 'v'
        tr.stats.station_latitude = 15
        tr.stats.station_longitude = -55
        tr.stats.station_elevation = 355
        tr.stats.event_time = tr.stats.starttime
        self.rftr = tr

    @patch('pyglimer.database.raw.h5py.File.__getitem__')
    def test_compression_indentifier(self, getitem_mock):
        d = {'test': 0}
        getitem_mock.side_effect = d.__getitem__
        self.assertEqual(self.dbh.compression, 'gzip')
        self.assertEqual(self.dbh.compression_opts, 9)
        self.assertEqual(self.dbh['test'], 0)

    @patch('pyglimer.database.raw.super')
    def test_forbidden_compression(self, super_mock):
        super_mock.return_value = None
        with self.assertRaises(ValueError):
            _ = raw.DBHandler('a', 'a', 'notexisting5')

    @patch('pyglimer.database.raw.super')
    def test_forbidden_compression_level(self, super_mock):
        super_mock.return_value = None
        with warnings.catch_warnings(record=True) as w:
            dbh = raw.DBHandler('a', 'a', 'gzip10')
            self.assertEqual(dbh.compression_opts, 9)
            self.assertEqual(len(w), 1)

    @patch('pyglimer.database.raw.super')
    def test_no_compression_level(self, super_mock):
        super_mock.return_value = None
        with self.assertRaises(IndexError):
            _ = raw.DBHandler('a', 'a', 'gzip')

    @patch('pyglimer.database.raw.super')
    def test_no_compression_name(self, super_mock):
        super_mock.return_value = None
        with self.assertRaises(IndexError):
            _ = raw.DBHandler('a', 'a', '9')

    def test_define_content(self):
        cont = {'Z': ['0', '1'], 'N': ['3', '4']}
        calls = [call('content', str(cont))]
        with patch.object(self.dbh, 'create_dataset') as create_ds_mock:
            self.dbh._define_content(cont)
            create_ds_mock.assert_called_once()
            create_ds_mock().attrs.__setitem__.assert_has_calls(calls)

    @patch('pyglimer.database.raw.h5py.File.__getitem__')
    def test_define_content_2(self, file_mock):
        attrs_mock = MagicMock()
        d = {'content': attrs_mock}
        file_mock.side_effect = d.__getitem__
        cont = {'Z': ['0', '1'], 'N': ['3', '4']}
        calls = [call('content', str(cont))]
        with patch.object(self.dbh, 'create_dataset') as create_ds_mock:
            create_ds_mock.side_effect = [ValueError('test'), attrs_mock]
            self.dbh._define_content(cont)
            create_ds_mock.assert_called_once()
            create_ds_mock().attrs.__setitem__.assert_has_calls(calls)

    @patch('pyglimer.database.raw.h5py.File.__getitem__')
    def test_get_content(self, file_mock):
        attrs_mock = MagicMock(name='attrs_mock')
        d2 = {'content': str({'Z': ["bla"], 'N': ["blub"]})}
        attrs_mock.attrs = d2
        d = {'content': attrs_mock}
        file_mock.side_effect = d.__getitem__
        toc = self.dbh._get_table_of_contents()
        self.assertDictEqual({'Z': ["bla"], 'N': ["blub"]}, toc)

    @patch('pyglimer.database.raw.h5py.File.__getitem__')
    def test_get_content_no_ds(self, file_mock):
        d = {}
        file_mock.side_effect = d.__getitem__
        cont = self.dbh._get_table_of_contents()
        self.assertEqual(cont, {})

    def test_add_already_available_data(self):
        st = self.rftr.stats
        path = raw.hierarchy.format(
            tag='raw',
            network=st.network, station=st.station,
            evt_id=pu.utc_save_str(st.event_time),
            channel=st.channel)
        with warnings.catch_warnings(record=True) as w:
            with patch.object(self.dbh, 'create_dataset') as create_ds_mock:
                create_ds_mock.side_effect = ValueError('test')
                self.dbh.add_waveform(self.rftr, evt_id=st.event_time)
                create_ds_mock.assert_called_with(
                    path, data=self.rftr.data,
                    compression=self.dbh.compression,
                    compression_opts=self.dbh.compression_opts)
            self.assertEqual(len(w), 1)

    @patch('pyglimer.database.raw.super')
    def test_add_different_object(self, super_mock):
        super_mock.return_value = None
        dbh = raw.DBHandler('a', 'r', 'gzip9')
        with self.assertRaises(TypeError):
            dbh.add_waveform(unittest.TestCase())

    @patch('pyglimer.database.raw.all_traces_recursive')
    @patch('pyglimer.database.raw.h5py.File.__getitem__')
    def test_get_data_wildcard(self, file_mock, all_tr_recursive_mock):
        all_tr_recursive_mock.return_value = Stream([self.rftr])
        st = self.rftr.stats
        net = st.network
        stat = st.station
        tag = 'rand'
        channel = st.channel
        starttime = st.starttime
        exp_path = raw.hierarchy.format(
            tag=tag, network=net, station=stat,
            evt_id=pu.utc_save_str(starttime),
            channel=channel)
        d = {
            exp_path: self.rftr.data,
            os.path.dirname(os.path.dirname(exp_path)): self.rftr.data}
        file_mock.side_effect = d.__getitem__

        _ = self.dbh.get_data(
            net, stat, starttime, tag=tag)
        file_mock.assert_called_with(
            f'/rand/BW/RJOB/{pu.utc_save_str(starttime)}')

    @patch('pyglimer.database.raw.BytesIO')
    @patch('pyglimer.database.raw.read_inventory')
    @patch('pyglimer.database.raw.h5py.File.__getitem__')
    def test_get_response(self, file_mock, read_inv_mock, b_mock):
        read_inv_mock.return_value = 'works'
        st = self.rftr.stats
        net = st.network
        stat = st.station
        tag = 'rand'
        exp_path = raw.hierarchy_xml.format(
            tag=tag, network=net, station=stat)
        d = {
            exp_path: [1, 2, 3]}
        file_mock.side_effect = d.__getitem__

        x = self.dbh.get_response(net, stat, tag=tag)
        self.assertEqual(x, 'works')
        file_mock.assert_called_with(exp_path)

    def test_add_response(self):
        inv = read_inventory()
        path = raw.hierarchy_xml.format(
            tag='response', network=inv[0].code, station=inv[0][0].code)
        with patch.object(self.dbh, 'create_dataset') as create_ds_mock:
            self.dbh.add_response(inv)
            create_ds_mock.assert_called_once_with(
                path, data=mock.ANY, compression=self.dbh.compression,
                compression_opts=self.dbh.compression_opts)


class TestCorrelationDataBase(unittest.TestCase):
    @patch('pyglimer.database.raw.DBHandler')
    def test_path_name(self, dbh_mock):
        cdb = raw.RawDatabase('a', None, 'r')
        self.assertEqual(cdb.path, 'a.h5')


if __name__ == "__main__":
    unittest.main()
