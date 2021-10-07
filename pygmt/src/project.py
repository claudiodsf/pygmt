"""
project - Project data onto lines or great circles, or generate tracks.
"""
import pandas as pd
from pygmt.clib import Session
from pygmt.exceptions import GMTInvalidInput
from pygmt.helpers import (
    GMTTempFile,
    build_arg_string,
    data_kind,
    dummy_context,
    fmt_docstring,
    kwargs_to_strings,
    use_alias,
)


@fmt_docstring
@use_alias(
    A="azimuth",
    E="endpoint",
    F="flags",
    G="generate",
    L="length",
    N="flatearth",
    Q="maptypeunits",
    S="sort",
    T="rotationpole",
    V="verbose",
    W="width",
    Z="ellipse",
    f="coltypes",
)
@kwargs_to_strings(E="sequence", L="sequence", T="sequence", W="sequence")
def project(points, center, outfile=None, **kwargs):
    r"""
    Project data onto lines or great circles, or generate tracks.

    Project reads arbitrary :math:`(x, y [, z])` data and returns any
    combination of :math:`(x, y, z, p, q, r, s)`, where :math:`(p, q)` are the
    coordinates in the projection, :math:`(r, s)` is the position in the
    :math:`(x, y)` coordinate system of the point on the profile (:math:`q = 0`
    path) closest to :math:`(x, y)`, and :math:`z` is all remaining columns in
    the input (beyond the required :math:`x` and :math:`y` columns).

    Alternatively, :doc:`pygmt.project` may be used to generate
    :math:`(r, s, p)` triples at equal increments along a profile using the
    ``generate`` parameter. In this case, the value of ``points`` is ignored
    (you can use, e.g., ``points=None``).

    Projections are defined in any (but only) one of three ways:

    1. By a ``center`` and an ``azimuth`` in degrees clockwise from North.
    2. By a ``center`` and ``endpoint`` of the projection path.
    3. By a ``center`` and a ``rotationpole`` position.

    To spherically project data along a great circle path, an oblique
    coordinate system is created which has its equator along that path, and the
    zero meridian through the Center. Then the oblique longitude (:math:`p`)
    corresponds to the distance from the Center along the great circle, and the
    oblique latitude (:math:`q`) corresponds to the distance perpendicular to
    the great circle path. When moving in the increasing (:math:`p`) direction,
    (toward B or in the azimuth direction), the positive (:math:`q`) direction
    is to your left. If a Pole has been specified, then the positive
    (:math:`q`) direction is toward the pole.

    To specify an oblique projection, use the ``rotationpole`` option to set
    the pole. Then the equator of the projection is already determined and the
    ``center`` option is used to locate the :math:`p = 0` meridian. The center
    *cx/cy* will be taken as a point through which the :math:`p = 0` meridian
    passes. If you do not care to choose a particular point, use the South pole
    (*cx* = 0, *cy* = -90).

    Data can be selectively windowed by using the ``length`` and ``width``
    options. If ``width`` is used, the projection width is set to use only
    points with :math:`w_{{min}} < q < w_{{max}}`. If ``length`` is set, then
    the length is set to use only those points with
    :math:`l_{{min}} < p < l_{{max}}`. If the ``endpoint`` option
    has been used to define the projection, then ``length="w"`` may be used to
    window the length of the projection to exactly the span from O to B.

    Flat Earth (Cartesian) coordinate transformations can also be made. Set
    ``flatearth=True`` and remember that azimuth is clockwise from North (the
    y axis), NOT the usual cartesian theta, which is counterclockwise from the
    x axis. azimuth = 90 - theta.

    No assumptions are made regarding the units for
    :math:`x, y, r, s, p, q, dist, l_{{min}}, l_{{max}}, w_{{min}}, w_{{max}}`.
    If -Q is selected, map units are assumed and :math:`x, y, r, s` must be in
    degrees and :math:`p, q, dist, l_{{min}}, l_{{max}}, w_{{min}}, w_{{max}}`
    will be in km.

    Calculations of specific great-circle and geodesic distances or for
    back-azimuths or azimuths are better done using :gmt-docs:`mapproject` as
    project is strictly spherical.

    :doc:`pygmt.project` is case sensitive: use lower case for the
    **xyzpqrs** letters in ``flags``.

    {aliases}

    Parameters
    ----------
    points : pandas.DataFrame or str
        Either a table with :math:`(x, y)` or (lon, lat) values in the first
        two columns, or a filename (e.g. csv, txt format). More columns may be
        present.

    center : str or list
        *cx*/*cy*.
        *cx/cy* sets the origin of the projection, in Definition 1 or 2. If
        Definition 3 is used, then *cx/cy* are the coordinates of a
        point through which the oblique zero meridian (:math:`p = 0`) should
        pass. The *cx/cy* is not required to be 90 degrees from the pole.

    azimuth : float or str
        defines the azimuth of the projection (Definition 1).

    endpoint : str or list
        *bx*/*by*.
        *bx/by* defines the end point of the projection path (Definition 2).

    flags : str
        Specify your desired output using any combination of **xyzpqrs**, in
        any order [Default is **xyzpqrs**]. Do not space between the letters.
        Use lower case. The output will be columns of values corresponding to
        your ``flags``. The **z** flag is special and refers to all numerical
        columns beyond the leading **x** and **y** in your input record. The
        **z** flag also includes any trailing text (which is placed at the end
        of the record regardless of the order of **z** in ``flags``). **Note**:
        If ``generate`` is True, then the output order is hardwired to be
        **rsp** and ``flags`` is not allowed.

    generate : str
        *dist* [/*colat*][**+c**\|\ **h**].
        Generate mode. No input is read and the value of ``points`` is ignored
        (you can use, e.g., ``points=None``). Create :math:`(r, s, p)` output
        points every *dist* units of :math:`p`. See `maptypeunits` option.
        Alternatively, append */colat* for a small circle instead [Default is a
        colatitude of 90, i.e., a great circle]. If setting a pole with
        ``rotationpole`` and you want the small circle to go through *cx*/*cy*,
        append **+c** to compute the required colatitude. Use ``center`` and
        ``endpoint`` to generate a circle that goes through the center and end
        point. Note, in this case the center and end point cannot be farther
        apart than :math:`2|\mbox{{colat}}|`. Finally, if you append **+h** then
        we will report the position of the pole as part of the segment header
        [Default is no header].

    length : str or list
        [**w**\|\ *l_min*/*l_max*].
        Length controls. Project only those points whose *p* coordinate is
        within :math:`l_{{min}} < p < l_{{max}}`. If ``endpoint`` has been set,
        then you may alternatively use **w** to stay within the distance from
        ``center`` to ``endpoint``.

    flatearth : bool
        If `True`, Make a Cartesian coordinate transformation in the plane.
        [Default uses spherical trigonometry.]

    maptypeunits : bool
        If `True`, project assumes :math:`x, y, r, s` are in degrees while
        :math:`p, q, dist, l_{{min}}, l_{{max}}, w_{{min}}, {{w_max}}` are in
        km. If not set (or ``False``), then all these are assumed to be in the
        same units.

    sort : bool
        Sort the output into increasing :math:`p` order. Useful when projecting
        random data into a sequential profile.

    rotationpole : str or list
        *px*/*py*.
        *px/py* sets the position of the rotation pole of the projection.
        (Definition 3).

    {V}

    width : str or list
        *w_min*/*w_max*
        Width controls. Project only those points whose :math:`q` coordinate is
        within :math:`w_{{min}} < q < w_{{max}}`.

    ellipse : str
        *major*/*minor*/*azimuth* [**+e**\|\ **n**].
        Used in conjunction with ``center`` (sets its center) and ``generate``
        (sets the distance increment) to create the coordinates of an ellipse
        with *major* and *minor* axes given in km (unless ``flatearth`` is
        given for a Cartesian ellipse) and the *azimuth* of the major axis in
        degrees. Append **+e** to adjust the increment set via ``generate`` so
        that the the ellipse has equal distance increments [Default uses the
        given increment and closes the ellipse].  Instead, append **+n** to set
        a specific number of unique equidistant points via ``generate``. For
        degenerate ellipses you can just supply a single *diameter* instead.  A
        geographic diameter may be specified in any desired unit other than km
        by appending the unit (e.g., 3d for degrees) [Default is km]; if so we
        assume the increment is also given in the same unit.  **Note**:
        For the Cartesian ellipse (which requires ``flatearth``), we expect
        *direction* counter-clockwise from the horizontal instead of an
        *azimuth*.

    outfile : str
        Required if ``points`` is a file. The file name for the output ASCII
        file.

    {f}

    Returns
    -------
    track: pandas.DataFrame or None
        Return type depends on whether the ``outfile`` parameter is set:

        - :class:`pandas.DataFrame` table with (x, y, ..., newcolname) if
          ``outfile`` is not set
        - None if ``outfile`` is set (track output will be stored in file set
          by ``outfile``)
    """
    # center ("C") is a required positional argument, so it cannot be
    # processed by decorator `@kwargs_to_strings`
    kwargs["C"] = "/".join(f"{item}" for item in center)

    with GMTTempFile(suffix=".csv") as tmpfile:
        if outfile is None:  # Output to tmpfile if outfile is not set
            outfile = tmpfile.name
        with Session() as lib:
            if "G" not in kwargs:
                # Store the pandas.DataFrame points table in virtualfile
                if data_kind(points) == "matrix":
                    table_context = lib.virtualfile_from_matrix(points.values)
                elif data_kind(points) == "file":
                    if outfile is None:
                        raise GMTInvalidInput("Please pass in a str to 'outfile'")
                    table_context = dummy_context(points)
                else:
                    raise GMTInvalidInput(f"Unrecognized data type {type(points)}")

                # Run project on the temporary (csv) points table
                with table_context as csvfile:
                    arg_str = " ".join(
                        [csvfile, build_arg_string(kwargs), "->" + outfile]
                    )
                    lib.call_module(module="project", args=arg_str)
            else:
                arg_str = " ".join([build_arg_string(kwargs), "->" + outfile])
                lib.call_module(module="project", args=arg_str)

        # if user did not set outfile, return pd.DataFrame
        if outfile == tmpfile.name:
            if "G" in kwargs:
                column_names = list("rsp")
            else:
                # Set output column names according to the "F" flag or use
                # default value
                if "F" in kwargs:
                    column_names = list(kwargs["F"])
                else:
                    column_names = list("xyzpqrs")
                # Find the indexes of "x", "y" and "z" column and
                # replace with input column names
                i_x = column_names.index("x")
                i_y = column_names.index("y")
                i_z = column_names.index("z")
                input_column_names = points.columns.to_list()
                column_names[i_x] = input_column_names[0]
                column_names[i_y] = input_column_names[1]
                # "z" can be actually more than one column
                column_names.pop(i_z)
                for col in reversed(input_column_names[2:]):
                    column_names.insert(i_z, col)
            result = pd.read_csv(tmpfile.name, sep="\t", names=column_names)
        # return None if outfile set, output in outfile
        elif outfile != tmpfile.name:
            result = None

    return result
