'''
:copyright:
   The PyGLImER development team (makus@gfz-potsdam.de).
:license:
    EUROPEAN UNION PUBLIC LICENCE v. 1.2
   (https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
:author:
   Peter Makus (makus@gfz-potsdam.de)

Created: Wednesday, 11th August 2021 03:20:09 pm
Last Modified: Friday, 20th January 2023 03:50:29 pm
'''

import fnmatch
import os
import re
from typing import Iterable, List, Tuple
import logging
import warnings

import numpy as np
# from numpy.core.fromnumeric import compress
from obspy.core.utcdatetime import UTCDateTime
from obspy.core import Stats
import h5py

from pyglimer.rf.create import RFStream, RFTrace


hierarchy = "/{tag}/{network}/{station}/{phase}/{pol}/{evt_time}"
h5_FMTSTR = os.path.join("{dir}", "{network}.{station}.h5")


class DBHandler(h5py.File):
    """
    The actual file handler of the hdf5 receiver function files.

    .. warning::

        **Should not be accessed directly. Access
        :class:`~pyglimer.database.rfh5.RFDataBase` instead.**

    Child object of :class:`h5py.File` and inherets all its attributes and
    functions in addition to functions that are particularly useful for
    receiver functions.
    """
    def __init__(self, path, mode, compression):
        super(DBHandler, self).__init__(path, mode=mode)
        if isinstance(compression, str):
            self.compression = re.findall(r'(\w+?)(\d+)', compression)[0][0]
            if self.compression != 'gzip':
                raise ValueError(
                    'Compression of type %s is not supported.'
                    % self.compression)
            self.compression_opts = int(
                re.findall(r'(\w+?)(\d+)', compression)[0][1])
            if self.compression_opts not in np.arange(1, 10, 1, dtype=int):
                ii = np.argmin(abs(
                    np.arange(1, 10, 1, dtype=int) - self.compression_opts))
                self.compression_opts = np.arange(1, 10, 1, dtype=int)[ii]
                warnings.warn(
                    'Chosen compression level is not available for %s. \
%s Has been chosen instead (closest)' % (
                        self.compression, str(self.compression_opts)))
        else:
            self.compression = None
            self.compression_opts = None

    def _close(self):
        self.close()

    def _add_known_waveform_data(self, ret: List[str], rej: List[str]):
        """
        Known waveforms to receive. Is just a dictionary with two keys (each
        of which has a list as item with all retained or rejected waveforms).

        :param ret: list of retained waveforms
        :type ret: List[str]
        :param rej: List of rejeccted waveforms
        type rej: List[str]
        """
        try:
            ds = self.create_dataset('known', data=np.empty(1))
        except ValueError:
            ds = self['known']
            # Already existing, just change attributes
        ds.attrs['ret'] = str(ret)
        ds.attrs['rej'] = str(rej)

    def add_rf(
            self, data: RFTrace or RFStream, tag: str = 'rf'):
        """
        Add receiver function to the hdf5 file. The data can later be accessed
        using the :meth:`~pyglimer.database.rfh5.DBHandler.get_data()` method.

        :param data: Data to save. Either a
            :class:`~pyglimer.rf.create.RFTrace` object or a
            :class:`~pyglimer.rf.create.RFStream` holding one or
            several traces.
        :type data: RFTrace or RFStream
        :param tag: The tag that the data should be saved under. By convention,
            receiver functions are saved with the tag `'rf'`.
        :raises TypeError: for wrong data type.
        """
        if not isinstance(data, RFTrace) and\
                not isinstance(data, RFStream):
            raise TypeError('Data has to be either a \
:class:`~pyglimer.rf.create.RFTrace` object or a \
:class:`~~pyglimer.rf.create.RFStream` object')

        if isinstance(data, RFTrace):
            data = [data]

        for tr in data:
            st = tr.stats
            path = hierarchy.format(
                tag=tag,
                network=st.network, station=st.station, phase=st.phase,
                pol=st.pol, evt_time=st.event_time.format_fissures())
            try:
                ds = self.create_dataset(
                    path, data=tr.data, compression=self.compression,
                    compression_opts=self.compression_opts)
                convert_header_to_hdf5(ds, st)
            except ValueError as e:
                print(e)
                warnings.warn("The dataset %s is already in file and will be \
omitted." % path, category=UserWarning)

    def get_data(
        self, network: str, station: str, phase: str, evt_time: UTCDateTime,
            tag: str = 'rf', pol: str = 'v') -> RFStream:
        """
        Returns a :class:`~pyglimer.rf.create.RFStream` holding
        all the requested data.

        .. note::

            `Wildcards are allowed for all parameters`.

        :param network: network code, e.g., IU
        :type network: str
        :param station: station code, e.g., HRV
        :type station: str
        :param phase: Teleseismic phase
        :type phase: str
        :param evt_time: Origin Time of the Event
        :type evt_time: UTCDateTime, optional
        :param tag: Data tag (e.g., 'rf'). Defaults to rf.
        :type tag: str, optional
        :param pol: RF Polarisation. Defaults to v.
        :type pol: str, optional
        :return: a :class:`~pyglimer.rf.create.RFStream` holding the requested
            data.
        :rtype: RFStream
        """
        try:
            evt_time = UTCDateTime(evt_time)
            evt_time = evt_time.format_fissures()
        except TypeError:
            evt_time = '*'

        path = hierarchy.format(
            tag=tag, network=network, station=station, phase=phase,
            pol=pol, evt_time=evt_time)
        # Extremely ugly way of changing the path
        if '*' not in path:
            data = np.array(self[path])
            header = read_hdf5_header(self[path])
            return RFStream(RFTrace(data, header=header))
        # Now, we need to differ between the fnmatch pattern and the actually
        # acessed path
        pattern = path.replace('/*', '*')
        path = path.split('*')[0]
        try:
            return all_traces_recursive(self[path], RFStream(), pattern)
        except KeyError:
            warnings.warn(
                f'Could not find data from {network}.{station} for phase '
                + f'{phase}, tag {tag}, polarisation {pol}, and time '
                + f'{evt_time}. Returning empty Stream.')
            return RFStream()

    def get_coords(
        self, network: str, station: str, phase: str = None,
            tag: str = 'rf') -> Tuple[float, float, float]:
        """
        Return the coordinates of the station.

        :param network: Network Code.
        :type network: str
        :param station: Station Code
        :type station: str
        :param phase: Teleseismic Phase, defaults to None
        :type phase: str, optional
        :return: Latitude (dec deg), Longitude (dec deg), Elevation (m)
        :rtype: Tuple[ float, float, float]
        """

        # This might look confusing but it's actually not looping but just
        # choosing the first available file
        try:
            for ph in self[tag][network][station].keys():
                phi = phase or ph
                for pol in self[tag][network][station][phi].keys():
                    for t in self[tag][network][station][phi][pol].keys():
                        rf = self.get_data(
                            network, station, phi, t, tag, pol)
                        if not rf.count():
                            continue
                        return (
                            rf[0].stats.station_latitude,
                            rf[0].stats.station_longitude,
                            rf[0].stats.station_elevation)
        except KeyError:
            # No data?
            warnings.warn(
                'No Data for station %s.%s and phase %s. Returns None.' % (
                    network, station, phase
                ))
            return None, None, None

    def _get_known_waveforms(self) -> Tuple[List[str], List[str]]:
        try:
            ds = self['known']
            rej = eval(ds.attrs['rej'])
            ret = eval(ds.attrs['ret'])
        except (KeyError, AttributeError):
            ret = []
            rej = []
        return ret, rej

    def walk(
        self, tag: str, network: str, station: str, phase: str,
            pol: str = 'v') -> Iterable[RFTrace]:
        """
        Iterate over all receiver functions with the given properties.

        :param tag: data tag
        :type tag: str
        :param network: Network code
        :type network: str
        :param station: Statio ncode
        :type station: str
        :param phase: Teleseismic phase
        :type phase: str
        :param pol: RF-Polarisation, defaults to 'v'
        :type pol: str, optional
        :return: Iterator
        :rtype: Iterable[RFTrace]
        :yield: one :class:`~pyglimer.rf.create.RFTrace` per receiver function.
        :rtype: Iterator[Iterable[RFTrace]]

        .. note::

            Does not accept wildcards.
        """
        for v in self[tag][network][station][phase][pol].values():
            yield RFTrace(np.array(v), header=read_hdf5_header(v))


class RFDataBase(object):
    """
    Base class to handle the hdf5 files that contain receiver functions.
    """
    def __init__(
            self, path: str, mode: str = 'a', compression: str = 'gzip3'):
        """
        Access an hdf5 file holding receiver functions. The resulting file can
        be accessed using all functionalities of
        `h5py <https://www.h5py.org/>`_ (for example as a dict).

        :param path: Full path to the file
        :type path: str
        :param mode: Mode to access the file. Options are: 'a' for all, 'w' for
            write, 'r+' for writing in an already existing file, or 'r' for
            read-only , defaults to 'a'.
        :type mode: str, optional
        :param compression: The compression algorithm and compression level
            that the arrays should be saved with. 'gzip3' tends to perform
            well, else you could choose 'gzipx' where x is a digit between
            1 and 9 (i.e., 9 is the highest compression) or None for fastest
            perfomance, defaults to 'gzip3'.
        :type compression: str, optional

        .. warning::

            **Access only through a context manager (see below):**

            >>> with RFDataBase('myfile.h5') as rfdb:
            >>>     type(rfdb)  # This is a DBHandler
            <class 'pyglimer.database.rfh5.DBHandler'>

        Example::

            >>> with RFDataBase(
                        '/path/to/db/XN.NEP06.h5') as rfdb:
            >>>     # find the available tags for existing db
            >>>     print(list(rfdb.keys()))
            ['rf', 'rfstack']
            >>>     # Get Data from all times and tag rf, phase P
            >>>     st = rfdb.get_data(
            >>>         'XN', 'NEP06', 'P', '*', 'rf')
            >>> print(st.count())
            250
        """

        # Create / read file
        if not path.split('.')[-1] == 'h5':
            path += '.h5'
        self.path = path
        self.mode = mode
        self.compression = compression

    def __enter__(self) -> DBHandler:
        self.db_handler = DBHandler(
            self.path, self.mode, self.compression)
        return self.db_handler

    def __exit__(self, exc_type, exc_value, tb) -> None or bool:
        self.db_handler._close()
        if exc_type is not None:
            return False


def all_traces_recursive(
    group: h5py._hl.group.Group, stream: RFStream,
        pattern: str) -> RFStream:
    """
    Recursively, appends all traces in a h5py group to the input stream.
    In addition this will check whether the data matches a certain pattern.

    :param group: group to search through
    :type group: class:`h5py._hl.group.Group`
    :param stream: Stream to append the traces to
    :type stream: Stream
    :param pattern: pattern for the path in the hdf5 file, see fnmatch for
        details.
    :type pattern: str
    :return: Stream with appended traces
    :rtype: Stream
    """
    for v in group.values():
        if isinstance(v, h5py._hl.group.Group):
            all_traces_recursive(v, stream, pattern)
        elif not fnmatch.fnmatch(v.name, pattern) and v.name not in pattern:
            continue
        else:
            # try:
            stream.append(
                RFTrace(np.array(v), header=read_hdf5_header(v)))
            # except ValueError:
            #     warnings.warn(
            #         'Header could not be converted. Attributes are: %s' % (
            #             str(v.attrs)))
    return stream


def convert_header_to_hdf5(dataset: h5py.Dataset, header: Stats):
    """
    Convert an :class:`~obspy.core.Stats` object and adds it to the provided
    hdf5 dataset.

    :param dataset: the dataset that the header should be added to
    :type dataset: h5py.Dataset
    :param header: The trace's header
    :type header: Stats
    """
    header = dict(header)
    for key in header:
        try:
            if isinstance(header[key], UTCDateTime):
                # convert time to string
                header[key] = header[key].format_fissures()
            dataset.attrs[key] = header[key]
        except TypeError:
            logging.debug(
                f'The header contains an item of type {type(header[key])}.'
                + 'Information of this type cannot be written to hdf5.')
            continue


def read_hdf5_header(dataset: h5py.Dataset) -> Stats:
    """
    Takes an hdf5 dataset as input and returns the header of the Trace.

    :param dataset: The dataset to be read from
    :type dataset: h5py.Dataset
    :return: The trace's header
    :rtype: Stats
    """
    attrs = dataset.attrs
    time_keys = ['starttime', 'endtime', 'onset', 'event_time']
    header = {}
    for key in attrs:
        if key in time_keys:
            try:
                header[key] = UTCDateTime(attrs[key])
            except ValueError as e:
                # temporary fix of obspy's UTCDateTime issue. SHould be removed
                # as soon as they release version 1.23
                if attrs[key][4:8] == '360T':
                    new = list(attrs[key])
                    new[6] = '1'
                    header[key] = UTCDateTime(''.join(new)) - 86400
                else:
                    raise e
        elif key == 'processing':
            header[key] = list(attrs[key])
        else:
            header[key] = attrs[key]
    return Stats(header)
