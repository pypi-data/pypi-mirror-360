'''
This is a newer version of preprocess.py meant to be used with pyasdf.
Now, we will have to work in a very different manner than for .mseed files
and process files station wise rather than event wise.

:copyright:
   The PyGLImER development team (makus@gfz-potsdam.de).
:license:
    EUROPEAN UNION PUBLIC LICENCE v. 1.2
   (https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
:author:
    Peter Makus (makus@gfz-potsdam.de)

Created: Thursday, 18th February 2021 02:26:03 pm
Last Modified: Friday, 20th January 2023 03:50:29 pm
'''

from glob import glob
import logging
import os
from typing import List, Tuple

import numpy as np
from joblib import Parallel, delayed
from tqdm.auto import tqdm as tqdm_auto
import obspy
from obspy import Stream, UTCDateTime
from obspy.geodetics import gps2dist_azimuth, kilometer2degrees
from tqdm.std import tqdm

from pyglimer import constants
from pyglimer.database.rfh5 import RFDataBase
from pyglimer.database.raw import RawDatabase
from pyglimer.utils.log import create_mpi_logger
from .qc import qcp, qcs
from .rotate import rotate_LQT_min, rotate_PSV
from ..rf.create import RFStream, createRF


# program-specific Exceptions
class SNRError(Exception):
    """raised when the SNR is too high"""
    # Constructor method

    def __init__(self, value):
        self.value = value
    # __str__ display function

    def __str__(self):
        return repr(self.value)


class StreamLengthError(Exception):
    """raised when stream has fewer than 3 components"""
    # Constructor method

    def __init__(self, value):
        self.value = value
    # __str__ display function

    def __str__(self):
        return repr(self.value)


class ProgressParallel(Parallel):
    def __call__(self, *args, **kwargs):
        with tqdm_auto() as self._pbar:
            return Parallel.__call__(self, *args, **kwargs)

    def print_progress(self):
        self._pbar.total = self.n_dispatched_tasks
        self._pbar.n = self.n_completed_tasks
        self._pbar.refresh()


def preprocessh5(
    phase: str, rot: str, pol: str, taper_perc: float,
    model: obspy.taup.TauPyModel, taper_type: str, tz: int, ta: int,
    rawloc: str, rfloc: str, deconmeth: str, hc_filt: float, netrestr: str,
    statrestr: str, logger: logging.Logger, rflogger: logging.Logger,
        client: str, evtcat: obspy.Catalog, remove_response: bool):
    """
    Preprocess files saved in hdf5 (pyasdf) format. Will save the computed
    receiver functions in hdf5 format as well.

    Processing is done via a multiprocessing backend (either joblib or mpi).

    :param phase: The Teleseismic phase to consider
    :type phase: str
    :param rot: The Coordinate system that the seismogram should be rotated to.
    :type rot: str
    :param pol: Polarisationfor PRFs. Can be either 'v' or 'h' (vertical or
        horizontal).
    :type pol: str
    :param taper_perc: Percentage for the pre deconvolution taper.
    :type taper_perc: float
    :param model: TauPyModel to be used for travel time computations
    :type model: obspy.taup.TauPyModel
    :param taper_type: type of taper (see obspy)
    :type taper_type: str
    :param tz: Length of time window before theoretical arrival (seconds)
    :type tz: int
    :param ta: Length of time window after theoretical arrival (seconds)
    :type ta: int
    :param rawloc: Directory, in which the raw data is saved.
    :type rawloc: str
    :param rfloc: Directory to save the receiver functions in.
    :type rfloc: str
    :param deconmeth: Deconvolution method to use.
    :type deconmeth: str
    :param hc_filt: Second High-Cut filter (optional, can be None or False)
    :type hc_filt: float
    :param netrestr: Network restrictions
    :type netrestr: str
    :param statrestr: Station restrictions
    :type statrestr: str
    :param logger: Logger to use
    :type logger: logging.Logger
    :param rflogger: [description]
    :type rflogger: logging.Logger
    :param client: Multiprocessing Backend to use
    :type client: str
    :param evtcat: event Catalogue
    :type evtcat: obspy.catalog
    :raises NotImplementedError: For uknowns multiprocessing backends.
    """
    os.makedirs(rfloc, exist_ok=True)

    # Open ds
    fpattern = '%s.%s.h5' % (netrestr or '*', statrestr or '*')
    globstr = os.path.join(rawloc, fpattern)
    flist = list(glob(globstr))

    # Checking whether file list is actually seen
    logger.debug(f'RAWLOC: {rawloc}')
    logger.debug(f'GLOBSTRING: {globstr}')
    logger.debug(f'# of Files found: {len(flist)}')

    # Perform processing depending on client
    if client.lower() == 'mpi':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        psize = comm.Get_size()
        pmap = (np.arange(len(flist))*psize)/len(flist)
        pmap = pmap.astype(np.int32)
        ind = pmap == rank
        ind = np.arange(len(flist))[ind]

        # get new MPI compatible loggers
        logger = create_mpi_logger(logger, rank)
        rflogger = logging.getLogger("%s.RF" % logger.name)
        for ii in ind:
            _preprocessh5_single(
                phase, rot, pol, taper_perc, model, taper_type, tz, ta, rfloc,
                deconmeth, hc_filt, logger, rflogger, flist[ii], evtcat,
                remove_response)

    elif client.lower() == 'joblib':
        ProgressParallel(n_jobs=-1,)(
            delayed(_preprocessh5_single)(
                phase, rot, pol, taper_perc, model, taper_type, tz, ta, rfloc,
                deconmeth, hc_filt, logger, rflogger,
                f, evtcat, remove_response) for f in tqdm(flist))

    elif client.lower() == 'single':
        for f in tqdm(flist):
            _preprocessh5_single(
                phase, rot, pol, taper_perc, model, taper_type, tz, ta, rfloc,
                deconmeth, hc_filt, logger, rflogger,
                f, evtcat, remove_response)
    else:
        raise NotImplementedError(
            'Unknown multiprocessing backend %s.' % client
        )


def _preprocessh5_single(
        phase: str, rot: str, pol: str, taper_perc: float,
        model: obspy.taup.TauPyModel, taper_type: str, tz: int, ta: int,
        rfloc: str, deconmeth: str, hc_filt: float,
        logger: logging.Logger, rflogger: logging.Logger,
        hdf5_file: str, evtcat: obspy.Catalog, remove_response: bool):
    """
    Single core processing of one single hdf5 file.

    .. warning:: Should not be called use
        :func:`~seismic.waveform.preprocessh5.preprocess_h5`!
    """

    f = hdf5_file
    net, stat, _ = os.path.basename(f).split('.')
    code = '%s.%s' % (net, stat)

    outf = os.path.join(rfloc, code)

    # Local logger reset
    logger = logging.getLogger(logger.name)
    rflogger = logging.getLogger(rflogger.name)

    rflogger.info(f'Processing Station {code}')

    # Find out which files have already been processed:
    if os.path.isfile(outf+'.h5'):
        with RFDataBase(outf) as rfdb:
            ret, rej = rfdb._get_known_waveforms()
            rflogger.debug('Already processed waveforms: %s' % str(ret))
            rflogger.debug('\nAlready rejected waveforms: %s' % str(rej))
    else:
        ret = []
        rej = []

    with RawDatabase(f, mode='r') as rdb:
        # get station inventory
        try:
            inv = rdb.get_response(net, stat)
        except KeyError:
            logger.exception(
                f'Could not find station inventory for Station {net}.{stat}')
            # Can't process without Inventory
            return

        rf = RFStream()
        # There has to be a smarter way to do this. Only some events
        # have a corresponding waveform
        # At least only compute theoretical arrival if the distance is within
        # thresholds

        # Which times are available as raw data?
        list_of_times = list(rdb._get_table_of_contents().values())
        if len(list_of_times) == 0:
            rflogger.debug(f'No waveforms in {code}')
            return
        t_raw = list_of_times[0]
        t_raw = [UTCDateTime(t) for t in t_raw]
        t_raw_min = min(t_raw) - 600
        t_raw_max = max(t_raw) + 600
        # c_date = inv[0][0].creation_date
        # t_date = inv[0][0].termination_date

        for i, evt in tqdm(enumerate(evtcat)):
            # Already processed?
            ot = (evt.preferred_origin() or evt.origins[0]).time
            ot_fiss = UTCDateTime(ot).format_fissures()
            if ot_fiss in rej or ot_fiss in ret:
                rflogger.debug('RF with ot %s already processed.' % ot_fiss)
                continue
            # Skip events with no data.
            if ot < t_raw_min or t_raw_max < ot:
                rflogger.debug(f'No raw data for event {ot_fiss}.')
                continue
            try:
                toa, rayp, rayp_s_deg, baz, distance = compute_toa(
                    evt, inv[0][0].latitude, inv[0][0].longitude, phase, model)
            except IndexError:
                rflogger.debug('Phase not viable for epicentral distance')
                continue
            except ValueError as e:
                rflogger.debug(e)
                continue

            st = rdb.get_data(net, stat, ot)
            st = st.slice(starttime=toa-tz, endtime=toa+ta)
            if st.count() < 3:
                logger.info(
                    f'Only {st.count()} traces found for Station {net}.{stat}'
                    + f'and arrival time {toa}.')
                continue
            if st[0].stats.endtime - st[0].stats.starttime < tz+ta-20:
                logger.warning(
                    'Stream shorter than requested time window, skip.')
                continue
            try:
                rf_temp = __station_process__(
                    st, inv, evt, phase, rot, pol, taper_perc, taper_type, tz,
                    ta, deconmeth, hc_filt, logger, rflogger, net, stat, baz,
                    distance, rayp, rayp_s_deg, toa, rej, ret, remove_response)
            except Exception as e:
                rflogger.exception(
                    'RF Creation failed. Waveform Data:\n'
                    + f'{net}.{stat}.{ot_fiss}\noriginal error:\n'
                    + f'{e}')
                continue
            if rf_temp is not None:
                rf.append(rf_temp)
            # Write regularly to not clutter too much into the RAM
            if rf.count() >= 20:
                rflogger.info('Writing to file %s....' % outf)
                with RFDataBase(outf) as rfdb:
                    rfdb.add_rf(rf)
                    rfdb._add_known_waveform_data(ret, rej)
                rflogger.info('..written.')
                rf.clear()
    if rf.count():
        rflogger.info('Writing to file %s....' % outf)
        with RFDataBase(outf) as rfdb:
            rfdb.add_rf(rf)
            rfdb._add_known_waveform_data(ret, rej)
        rflogger.info('..written.')
    rf.clear()


def compute_toa(
    evt: obspy.core.event.Event, slat: float, slon: float,
    phase: str, model: obspy.taup.TauPyModel) -> Tuple[
        UTCDateTime, float, float, float]:
    """
    Compute time of theoretical arrival for teleseismic events and a given
    teleseismic phase at the provided station.

    :param evt: Event to compute the arrival for.
    :type evt: obspy.core.event.Event
    :param slat: station latitude
    :type slat: float
    :param slon: station longitude
    :type slon: float
    :param phase: The teleseismic phase to consider.
    :type phase: str
    :param model: Taupymodel to use
    :type model: obspy.taup.TauPyModel
    :return: A Tuple holding: [the time of theoretical arrival (UTC),
        the apparent slowness in s/km, the ray parameter in s/deg,
        the back azimuth, the distance between station and event in deg]
    :rtype: Tuple[UTCDateTime, float, float, float]
    """
    origin = evt.preferred_origin() or evt.origins[0]
    distance, baz, _ = gps2dist_azimuth(
        slat, slon, origin.latitude,
        origin.longitude)
    distance = kilometer2degrees(distance/1000)

    # compute time of first arrival & ray parameter
    odepth = origin.depth or 10000  # Some events have no depth information

    # Throw out events that should not be used for RFs
    if (constants.maxdepth[phase]
        and constants.maxdepth[phase] < odepth/1000) \
        or not (
            constants.min_epid[phase]
            <= distance <= constants.max_epid[phase]):
        raise ValueError(
            f'Distance {distance} deg or origin depth {odepth}m should not be '
            + 'used for RFs')

    arrival = model.get_travel_times(
        source_depth_in_km=odepth / 1000, distance_in_degree=distance,
        phase_list=[phase])[0]
    rayp_s_deg = arrival.ray_param_sec_degree
    rayp = rayp_s_deg / 111319.9  # apparent slowness
    toa = origin.time + arrival.time

    return toa, rayp, rayp_s_deg, baz, distance


def __station_process__(
    st, inv, evt, phase, rot, pol, taper_perc, taper_type, tz, ta,  deconmeth,
    hc_filt, logger, rflogger, net, stat, baz, distance, rayp,
    rayp_s_deg, toa, rej: List[str], ret: List[str],
        remove_response: bool):
    """
    Processing that is equal for each waveform recorded on one station
    """
    # Is the data already processed?
    origin = (evt.preferred_origin() or evt.origins[0])
    ot_fiss = UTCDateTime(origin.time).format_fissures()

    # Remove repsonse
    if remove_response:
        st.attach_response(inv)
        st.remove_response()

    # DEMEAN AND DETREND #
    st.detrend(type='demean')

    # TAPER #
    st.taper(
        max_percentage=taper_perc, type=taper_type, max_length=None,
        side='both')

    infodict = {}

    # create RF
    try:
        st, _, infodict = __rotate_qc(
            phase, st, inv, net, stat, baz, distance, ot_fiss, evt,
            origin.latitude, origin.longitude, origin.depth, rayp_s_deg, toa,
            logger, infodict, tz, pol)
        if hc_filt:
            st.filter('lowpass', freq=hc_filt, zerophase=True, corners=2)
        # Rotate to LQT or PSS
        if rot == "LQT":
            st, ia = rotate_LQT_min(st, phase)
            # additional QC
            if ia < 5 or ia > 75:
                raise SNRError(
                    "The estimated incidence angle is unrealistic with"
                    + '%s degree.' % str(ia))

        elif rot == "PSS":
            _, _, st = rotate_PSV(
                inv[0][0][0].latitude,
                inv[0][0][0].longitude,
                rayp, st, phase)

        # Create RF object
        if phase[-1] == "S":
            trim = [40, 0]
            if distance >= 70:
                trim[1] = ta - (-2*distance + 180)
            else:
                trim[1] = ta - 40
        elif phase[-1] == "P":
            trim = False

        RF = createRF(
            st, phase, pol=pol, info=infodict, trim=trim,
            method=deconmeth)
        ret.append(ot_fiss)

    except SNRError as e:
        rflogger.info(f'{e} {ot_fiss}')
        rej.append(ot_fiss)
        return None

    except Exception as e:
        rflogger.exception(
            'RF Creation failed. Waveform Data:\n'
            + f'{net}.{stat}.{ot_fiss}\noriginal error:\n'
            + f'{e}')
        return None

    return RF


def __rotate_qc(
    phase, st, station_inv, network, station, baz, distance, ot_fiss,
    event, evtlat, evtlon, depth, rayp_s_deg, first_arrival, logger, infodict,
        tz, pol):
    """
    REMOVE INSTRUMENT RESPONSE + convert to vel + SIMULATE
    """

    st.rotate(method='->ZNE', inventory=station_inv)

    st.rotate(method='NE->RT', inventory=station_inv,
              back_azimuth=baz)
    st.normalize()

    # Sometimes streams contain more than 3 traces:
    if st.count() > 3:
        stream = {}
        for tr in st:
            stream[tr.stats.component] = tr
        if "Z" in stream:
            st = Stream([stream["Z"], stream["R"], stream["T"]])
        elif "3" in stream:
            st = Stream([stream["3"], stream["R"], stream["T"]])
        del stream

    # SNR CRITERIA
    dt = st[0].stats.delta  # sampling interval
    sampling_f = st[0].stats.sampling_rate

    if phase[-1] == "P":
        st, crit, f, noisemat = qcp(st, dt, sampling_f, tz)
        if not crit:
            infodict['dt'] = dt
            infodict['sampling_rate'] = sampling_f
            infodict['network'] = network
            infodict['station'] = station
            infodict['statlat'] = station_inv[0][0][0].latitude
            infodict['statlon'] = station_inv[0][0][0].longitude
            infodict['statel'] = station_inv[0][0][0].elevation
            raise SNRError('QC rejected %s' % np.array2string(noisemat))

    elif phase[-1] == "S":
        st, crit, f, noisemat = qcs(st, dt, sampling_f, tz)

        if not crit:
            infodict['dt'] = dt
            infodict['sampling_rate'] = sampling_f
            infodict['network'] = network
            infodict['station'] = station
            infodict['statlat'] = station_inv[0][0][0].latitude
            infodict['statlon'] = station_inv[0][0][0].longitude
            infodict['statel'] = station_inv[0][0][0].elevation
            raise SNRError('QC rejected %s' % np.array2string(noisemat))

    # WRITE AN INFO FILE
    append_inf = [
        ['magnitude', (
            event.preferred_magnitude() or event.magnitudes[0])['mag']],
        ['magnitude_type', (
            event.preferred_magnitude() or event.magnitudes[0])[
                'magnitude_type']],
        ['evtlat', evtlat], ['evtlon', evtlon],
        ['ot_ret', ot_fiss], ['ot_all', ot_fiss],
        ['evt_depth', depth],
        ['evt_id', event.get('resource_id')],
        ['noisemat', noisemat],
        ['co_f', f], ['npts', st[1].stats.npts],
        ['rbaz', baz],
        ['rdelta', distance],
        ['rayp_s_deg', rayp_s_deg],
        ['onset', first_arrival],
        ['starttime', st[0].stats.starttime],
        ['pol', pol]]

    # Check if values are already in dict
    for key, value in append_inf:
        infodict.setdefault(key, []).append(value)

    infodict['dt'] = dt
    infodict['sampling_rate'] = sampling_f
    infodict['network'] = network
    infodict['station'] = station
    infodict['statlat'] = station_inv[0][0][0].latitude
    infodict['statlon'] = station_inv[0][0][0].longitude
    infodict['statel'] = station_inv[0][0][0].elevation

    logger.info(f"Stream accepted {ot_fiss}. Preprocessing successful")

    return st, crit, infodict
