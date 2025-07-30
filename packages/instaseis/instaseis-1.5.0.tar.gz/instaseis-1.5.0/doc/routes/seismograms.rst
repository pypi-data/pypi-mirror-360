GET/POST /seismograms
^^^^^^^^^^^^^^^^^^^^^

.. note::

    Some parts of this route require an advanced server setup. Please view the
    :doc:`../advanced_server_configuration` for details. The parts that don't
    will keep working even with a normal configuration.

Description
    Returns Instaseis seismograms. In addition to the functionality of the
    ``/seismograms_raw`` route this one has quite a couple of convenience
    function and is suitable to be queried by any program able to use HTTP.
    It is possible to ``GET`` and ``POST`` to this route: ``GET`` will just
    retrieve seismograms, ``POST`` allows one to upload a custom source time
    function, see below for details.

Content-Type
    * ``application/zip`` (if zipped SAC data is requested)
    * ``application/vnd.fdsn.mseed`` (if MiniSEED data is requested)

Special Response Headers
    ``Instaseis-Mu``: This transports the mu of the model for the given
    seismogram which is needed for some finite source calculations. Please make
    sure your proxy, if any, does not filter it.

Filetype
    Returns a ZIP archive with SAC files or MiniSEED files encoded with
    encoding format 4 (IEEE floating point).

    SAC files will have the following user defined variables set:

    * ``KUSER0``: "InstSeis"
    * ``KUSER1``: The first eight letters of the used velocity model.
    * ``KT7``: The first seven letters of the AxiSEM version number used to generate the model. Prefixed with ``A``.
    * ``KT8``: The first seven letters of the Instaseis version number used to generate the seismogram. Prefixed with ``I``.
    * ``USER0``: The scale factor used to generate the waveforms.

Custom STF
    A custom source time function can be uploaded with ``POST``. The request
    body in this case has to be a JSON file, the other parameters work as for
    the ``GET`` case, except otherwise noted. The JSON file must be akin to the
    following:

    .. code-block:: JSON

        {
            "units": "moment_rate",
            "relative_origin_time_in_sec": 5.0,
            "sample_spacing_in_sec": 10.0,
            "data": [0.0, 0.2, 0.5, 0.2, 0.0, 0.0, 0.0]
        }

    Keep in mind that what you are specifying is the moment rate, in seismology
    oftentimes called the source time function, which is the only currently
    supported ``unit``.  ``relative_origin_time_in_sec`` is the offset in
    seconds from the first sample which should be considered the origin time of
    the resulting seismogram (must be between 0 and 600 seconds).
    ``sample_spacing_in_sec`` is the sample interval in seconds and ``data``
    the actual data array. The exact units do not matter as it will be
    normalized in any case.

+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| Parameter                   | Type     | Required | Default Value               | Description                                                                          |
+=============================+==========+==========+=============================+======================================================================================+
| **Output parameters**                                                                                                                                                  |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``format``                  | String   | False    | saczip                      | Specify output file to be either MiniSEED or a ZIP archive of SAC files, either      |
|                             |          |          |                             | ``miniseed`` or ``saczip``.                                                          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``label``                   | String   | False    |                             | Specify a label to be included in file names and HTTP file name suggestions.         |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``components``              | String   | False    | ZNE, Z, or NE (depends on   | Specify the orientation of the synthetic seismograms as a list of any combination of |
|                             |          |          | what the DB supports)       | ``Z`` (vertical), ``N`` (north), ``E`` (east), ``R`` (radial), ``T`` (transverse).   |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``units``                   | String   | False    | displacement                | Specify either ``displacement``, ``velocity`` or ``acceleration`` for the synthetics.|
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``dt``                      | Float    | False    |                             | If given, seismograms will be resampled to the desired sample spacing.               |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``scale``                   | Float    | False    | 1.0                         | Scalar factor to multiply the seismograms with.                                      |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``kernelwidth``             | Integer  | False    | 12                          | Specify the width of the sinc kernel used for resampling to requested sample         |
|                             |          |          |                             | interval in terms of the original sampling interval.                                 |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourcewidth``             | Integer  | False    | 15.0                        | Optionally convolve the seismograms with a Gaussian source time function (moment     |
|                             |          |          |                             | rate) of approximately the given width in seconds. The origin time is assumed to be  |
|                             |          |          |                             | the peak of the Gaussian. Must be larger than the database period. Must not be used  |
|                             |          |          |                             | for a POST requests with a custom STF.                                               |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| **Time Parameters**                                                                                                                                                    |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``origintime``              | Datetime | False    | 1900-01-01T00:00:00.000000Z | Specify the source origin time. This must be specified as an                         |
|                             |          |          |                             | absolute date and time. This time coincides with the peak of the                     |
|                             |          |          |                             | source time function.                                                                |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``starttime``               | Datetime | False    |                             | Specifies the desired start time for the synthetic trace(s). This may be specified   |
|                             |          |          |                             | as either:                                                                           |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | * an absolute date and time                                                          |
|                             |          |          |                             | * a phase-relative offset                                                            |
|                             |          |          |                             | * an offset from origin time in seconds                                              |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | If the value is recognized as a date and time, it is interpreted as an absolute time.|
|                             |          |          |                             | If the value is in the form ``phase[+-]offset`` it is interpreted as a               |
|                             |          |          |                             | phase-relative time, for example ``P-10`` (meaning P-wave arrival time minus 10      |
|                             |          |          |                             | seconds). If the value is a numerical value it is interpreted as an offset, in       |
|                             |          |          |                             | seconds, from the origin time.                                                       |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``endtime``                 | Datetime | False    |                             | Specifies the desired end time for the synthetic trace(s). This may be specified     |
|                             |          |          |                             | as either:                                                                           |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | * an absolute date and time                                                          |
|                             |          |          |                             | * a phase-relative offset                                                            |
|                             |          |          |                             | * an offset (duration) from start time in seconds                                    |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | If the value is recognized as a date and time, it is interpreted as an absolute time.|
|                             |          |          |                             | If the value is in the form ``phase[+-]offset`` it is interpreted as a               |
|                             |          |          |                             | phase-relative time, for example ``P-10`` (meaning P-wave arrival time minus 10      |
|                             |          |          |                             | seconds). If the value is a numerical value it is interpreted as an offset, in       |
|                             |          |          |                             | seconds, from the start time.                                                        |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| **Receiver Parameters**                                                                                                                                                |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| Directly specify coordinates and network/station codes ...                                                                                                             |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``receiverlatitude``        | Float    | True     |                             | The geocentric latitude of the receiver.                                             |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``receiverlongitude``       | Float    | True     |                             | The longitude of the receiver.                                                       |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``receiverdepthinmeters``   | Float    | False    | 0.0                         | The depth of the receiver in meter.                                                  |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``networkcode``             | String   | False    | XX                          | Specify the network code of the final seismograms. Maximum of two letters.           |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``stationcode``             | String   | False    | SYN                         | Specify the station code of the final seismograms. Maximum of five letters.          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``locationcode``            | String   | False    | SE                          | Specify the location code of the final seismograms. Maximum of two letters.          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ... or use wildcard searches over network and station codes. Potentially returns multiple stations.                                                                    |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``network``                 | String   | False    |                             | Wildcarded network codes, e.g. ``I*,B?,AU``.                                         |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``station``                 | String   | False    |                             | Wildcarded station codes, e.g. ``A*,ANMO``.                                          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| **Source Parameters**                                                                                                                                                  |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| The source can by set by specifying an event id if the server has been set-up for this ...                                                                             |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``event_id``                | String   | False    |                             | The id of the event to use.                                                          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ... or by specify the source parameters in a variety of ways.                                                                                                          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourcelatitude``          | Float    | True     |                             | The geocentric latitude of the source.                                               |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourcelongitude``         | Float    | True     |                             | The longitude of the source.                                                         |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourcedepthinmeters``     | Float    | False    | 0.0                         | The depth of the source in meter.                                                    |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| **Source mechanism as a moment tensor**                                                                                                                                |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourcemomenttensor``      | List     | False    |                             | Specify a source in moment tensor components as a list: ``Mrr,Mtt,Mpp,Mrt,Mrp,Mtp``  |
|                             |          |          |                             | with values in Newton meters (Nm).                                                   |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | Example: ``1.04e22,-0.039e22,-1e22,0.304e22,-1.52e22,-0.119e22``                     |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| **Source mechanism as a double couple**                                                                                                                                |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourcedoublecouple``      | List     | False    |                             | Specify a source as a double couple. The list of values are ``strike,dip,rake[,M0]``,|
|                             |          |          |                             | where strike, dip and rake are in degrees and M0 is the scalar seismic moment in     |
|                             |          |          |                             | Newton meters (Nm). If not specified, a value of *1e19* will be used as the scalar   |
|                             |          |          |                             | moment.                                                                              |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | example: ``19,18,116,1e19``                                                          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| **Source mechanism as forces**                                                                                                                                         |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
| ``sourceforce``             | List     | False    |                             | Specify a force source as a list of ``Fr,Ft,Fp`` in units of Newtons (N).            |
|                             |          |          |                             |                                                                                      |
|                             |          |          |                             | example: ``1e22,1e22,1e22``                                                          |
+-----------------------------+----------+----------+-----------------------------+--------------------------------------------------------------------------------------+
