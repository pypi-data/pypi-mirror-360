"""
Common table operations
"""


import re
import secrets
import subprocess
import tempfile
from dataclasses import dataclass
from io import BufferedIOBase, BytesIO, RawIOBase, StringIO, TextIOBase
from pathlib import Path
from typing import Literal, Sequence, Tuple, Union

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.coordinates import (SkyCoord, match_coordinates_sky,
                                 search_around_sky)
from astropy.table import Table
from astropy.utils.data import download_file
from tqdm import tqdm

from astromodule.io import PathOrFile, TableLike, read_table, write_table

RA_REGEX = re.compile(r'^ra_?\d*$', re.IGNORECASE)
DEC_REGEX = re.compile(r'^dec_?\d*$', re.IGNORECASE)

def _match_regex_against_sequence(
  regex: re.Pattern, 
  columns: Sequence[str]
) -> Tuple[int, str] | None:
  for i, col in enumerate(columns):
    if regex.match(col):
      return i, col
  return None


def guess_coords_columns(
  df: pd.DataFrame,
  ra: str | None = None,
  dec: str | None = None,
) -> Tuple[str, str]:
  """
  Receives a pandas dataframe and try to guess the columns names used to
  identify the RA and DEC coordinates.

  Parameters
  ----------
  df : pd.DataFrame
    A pandas dataframe
  ra : str | None, optional
    The column name used to name the RA column. If a string is passed, this
    function will skip the RA guessing and will return the value of RA passed
    by this parameter. If the value is set to ``None``, this function will
    guess the RA column name using a pre-defined regular expression and will
    return the value of the first match found following the sequence of
    the columns.
  dec : str | None, optional
    The column name used to name the DEC column. If a string is passed, this
    function will skip the DEC guessing and will return the value of DEC passed
    by this parameter. If the value is set to ``None``, this function will
    guess the DEC column name using a pre-defined regular expression and will
    return the value of the first match found following the sequence of
    the columns.

  Returns
  -------
  Tuple[str, str]
    A tuple of RA and DEC columns guessed.

  Raises
  ------
  ValueError
    Raises a error if the RA or DEC columns cannot be found.
  """
  cols = df.columns.to_list()
  if ra is None:
    _, ra = _match_regex_against_sequence(RA_REGEX, cols)
  if dec is None:
    _, dec = _match_regex_against_sequence(DEC_REGEX, cols)
  if ra is None or dec is None:
    raise ValueError(
      "Can't guess RA or DEC columns, please, specify the columns names "
      "via `ra` and `dec` parameters"
    )
  return ra, dec



def table_knn(
  left: TableLike | PathOrFile,
  right: TableLike | PathOrFile,
  nthneighbor: int = 1,
  left_ra: str = 'ra',
  left_dec: str = 'dec',
  right_ra: str = 'ra',
  right_dec: str = 'dec',
) -> Tuple[np.ndarray, np.ndarray]:
  left_df = read_table(left)
  right_df = read_table(right)
  
  left_coords = SkyCoord(
    ra=left_df[left_ra].values,
    dec=left_df[left_dec].values, 
    unit=u.deg,
  )
  right_coords = SkyCoord(
    ra=right_df[right_ra].values,
    dec=right_df[right_dec].values,
    unit=u.deg,
  )
  
  idx, d, _ = match_coordinates_sky(
    left_coords,
    right_coords,
    nthneighbor=nthneighbor
  )

  return np.array(idx), np.array(d)


def fast_crossmatch(
  left: TableLike | PathOrFile,
  right: TableLike | PathOrFile,
  radius: float | u.Quantity = 1*u.arcsec,
  join: Literal['inner', 'left'] = 'inner',
  nthneighbor: int = 1,
  left_ra: str | None = None,
  left_dec: str | None = None,
  left_columns: Sequence[str] | None = None,
  right_ra: str | None = None,
  right_dec: str | None = None,
  right_columns: Sequence[str] | None = None,
  include_sep: bool = True,
):
  left_df = read_table(left)
  left_ra, left_dec = guess_coords_columns(left_df, left_ra, left_dec)
  right_df = read_table(right)
  right_ra, right_dec = guess_coords_columns(right_df, right_ra, right_dec)
  
  idx, d = table_knn(
    left_df, 
    right_df, 
    nthneighbor=nthneighbor, 
    left_ra=left_ra,
    left_dec=left_dec,
    right_ra=right_ra,
    right_dec=right_dec,
  )
  
  if isinstance(radius, u.Quantity):
    radius = radius.to(u.deg).value
  else:
    radius = u.Quantity(radius, unit=u.arcsec).to(u.deg).value

  mask = d < radius

  left_idx = mask.nonzero()[0]
  right_idx = idx[mask]
  
  if left_columns is not None:
    left_df = left_df[left_columns].copy()
  if right_columns is not None:
    right_df = right_df[right_columns].copy()
  
  if join == 'inner':
    left_masked_df = left_df.iloc[left_idx]
    right_masked_df = right_df.iloc[right_idx]
    match_df = left_masked_df.copy(deep=True)
    for col in right_masked_df.columns.to_list():
      if not col in match_df.columns:
        match_df[col] = right_masked_df[col].to_numpy()
        # TODO: include a flag "replace" in this method to indicate if t2 must
        # replace or not t1 columns. This implementation consider replace=False.
    if include_sep:
      match_df['xmatch_sep'] = d[mask]
  elif join == 'left':
    right_masked_df = right_df.iloc[right_idx]
    cols = [col for col in right_masked_df.columns if col not in left_df.columns]
    match_df = left_df.copy(deep=True)
    match_df.loc[left_idx, cols] = right_masked_df[cols].values
    if include_sep:
      match_df.loc[left_idx, 'xmatch_sep'] = d[mask]
  return match_df

  # left_df_masked = left_df.iloc[primary_idx]
  # right_df_masked = right_df.iloc[secondary_idx]

  # left_df_subsample = left_df_masked[left_columns].copy() \
  #   if left_columns is not None else left_df_masked.copy()
  # right_df_subsample = right_df_masked[right_columns].copy() \
  #   if right_columns.columns is not None else right_df_masked.copy()

  # for col in right_df_subsample.columns.tolist():
  #   left_df_subsample[col] = right_df_subsample[col].to_numpy()
  #   # TODO: include a flag "replace" in this method to indicate if t2 must
  #   # replace or not t1 columns. This implementation consider replace=True.

  # r = CrossMatchResult()
  # r.distance = d[mask]
  # r.primary_idx = primary_idx
  # r.secondary_idx = secondary_idx
  # r.table = df1_subsample
  


@dataclass
class DropDuplicatesResult:
  df: pd.DataFrame
  distances: np.ndarray
  n_iterations: int
  drop_count: int

  
def drop_duplicates(
  table: TableLike | PathOrFile,
  radius: float | u.Quantity = 1*u.arcsec,
  ra: str | None = None,
  dec: str | None = None,
  columns: Sequence[str] | None = None,
  max_iterations: int = 20,
) -> DropDuplicatesResult:
  if isinstance(radius, u.Quantity):
    radius = radius.to(u.deg).value
  else:
    radius = u.Quantity(radius, unit=u.arcsec).to(u.deg).value
  
  df = read_table(table)
  ra, dec = guess_coords_columns(df, ra, dec)
  df_coords = df[[ra, dec]].copy(deep=True)
  total_drop_count = 0
  drop_count = -1
  iteration = 0
  
  while (drop_count != 0 and iteration <= max_iterations):
    print(drop_count, iteration)
    idx, d = table_knn(
      df_coords, 
      df_coords, 
      left_ra=ra, 
      left_dec=dec, 
      right_ra=ra, 
      right_dec=dec, 
      nthneighbor=2
    )

    mask = d < radius
    primary_idx = mask.nonzero()[0]
    secondary_idx = idx[mask]
    removed_idx = []

    for pid, sid in zip(primary_idx, secondary_idx):
      if sid not in removed_idx:
        removed_idx.append(pid)

    del_mask = np.isin(idx, removed_idx, invert=True).nonzero()[0]
    len_copy_df = len(df_coords)
    df_coords = df_coords.iloc[del_mask].copy()
    
    drop_count = len_copy_df - len(df_coords)
    total_drop_count += drop_count
    iteration += 1
  
  d = d[del_mask]
  final_df = df.iloc[df_coords.index]
  if columns is not None:
    final_df = final_df[columns]
  
  return DropDuplicatesResult(
    df=final_df,
    distances=d,
    n_iterations=iteration,
    drop_count=total_drop_count
  )



  
def crossmatch(
  table1: TableLike | PathOrFile,
  table2: TableLike | PathOrFile,
  ra1: str | None = None,
  dec1: str | None = None,
  ra2: str | None = None,
  dec2: str | None = None,
  radius: float | u.Quantity = 1 * u.arcsec,
  join: Literal['1and2', '1or2', 'all1', 'all2', '1not2', '2not1', '1xor2'] = '1and2',
  find: Literal['all', 'best', 'best1', 'best2'] = 'best',
  fixcols: Literal['dups', 'all', 'none'] = 'dups',
  suffix1: str = '_1',
  suffix2: str = '_2',
  scorecol: str | None = 'xmatch_sep',
  fmt: Literal['fits', 'csv', 'parquet'] = 'parquet',
) -> pd.DataFrame | None:
  """
  Performs a crossmatch between two tables using STILTS [#ST]_ as the backend.
  This function spawns a subprocess invoking the ``tmatch2`` [#tmatch2]_ 
  tool of the STILTS executable. 

  Parameters
  ----------
  table1 : TableLike | PathOrFile
    The first table that will be crossmatched. This parameter accepts a
    table-like object (pandas dataframe, astropy table), a path to a file
    represented as a string or pathlib.Path object, or a file object
    (BinaryIO, StringIO, file-descriptor, etc).
  
  table2 : TableLike | PathOrFile
    The second table that will be crossmatched. This parameter accepts a
    table-like object (pandas dataframe, astropy table), a path to a file
    represented as a string or pathlib.Path object, or a file object
    (BinaryIO, StringIO, file-descriptor, etc).
  
  ra1 : str | None, optional
    The name of the Right Ascension (RA) column in the first table. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  dec1 : str | None, optional
    The name of the Declination (DEC) column in the first table. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  ra2 : str | None, optional
    The name of the Right Ascension (RA) column in the second table. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  dec2 : str | None, optional
    The name of the Declination (DEC) column in the second table. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  radius : float | u.Quantity, optional
    The crossmatch max error radius. This function accepts a ``float`` value,
    that will be interpreted as ``arcsec`` unit, or a `~astropy.units.Quantity`
  
  join : Literal['1and2', '1or2', 'all1', 'all2', '1not2', '2not1', '1xor2'], optional
    Determines which rows are included in the output table. 
    The matching algorithm determines which of the rows from the first 
    table correspond to which rows from the second. This parameter 
    determines what to do with that information. Perhaps the most 
    obvious thing is to write out a table containing only rows which 
    correspond to a row in both of the two input tables. However, 
    you may also want to see the unmatched rows from one or both 
    input tables, or rows present in one table but unmatched in the other, 
    or other possibilities. The options are:

    * ``1and2``: An output row for each row represented in both input 
      tables (INNER JOIN)
    * ``1or2``: An output row for each row represented in either or both 
      of the input tables (FULL OUTER JOIN)
    * ``all1``: An output row for each matched or unmatched row in table 1 
      (LEFT OUTER JOIN)
    * ``all2``: An output row for each matched or unmatched row in table 2 
      (RIGHT OUTER JOIN)
    * ``1not2``: An output row only for rows which appear in the first 
      table but are not matched in the second table
    * ``2not1``: An output row only for rows which appear in the second 
      table but are not matched in the first table
    * ``1xor2``: An output row only for rows represented in one of the 
      input tables but not the other one

  find : Literal['all', 'best', 'best1', 'best2'], optional
    Determines what happens when a row in one table can be matched by more 
    than one row in the other table. The options are:

    * ``all``: All matches. Every match between the two tables is included 
      in the result. Rows from both of the input tables may appear multiple 
      times in the result.
    * ``best``: Best match, symmetric. The best pairs are selected in a 
      way which treats the two tables symmetrically. Any input row which 
      appears in one result pair is disqualified from appearing in any 
      other result pair, so each row from both input tables will appear 
      in at most one row in the result.
    * ``best1``: Best match for each Table 1 row. For each row in table 1, 
      only the best match from table 2 will appear in the result. Each row 
      from table 1 will appear a maximum of once in the result, but rows 
      from table 2 may appear multiple times.
    * ``best2``: Best match for each Table 2 row. For each row in table 2, 
      only the best match from table 1 will appear in the result. Each row 
      from table 2 will appear a maximum of once in the result, but rows 
      from table 1 may appear multiple times.

    The differences between ``best``, ``best1`` and ``best2`` are a bit subtle. 
    In cases where it's obvious which object in each table is the 
    best match for which object in the other, choosing betwen these 
    options will not affect the result. However, in crowded fields 
    (where the distance between objects within one or both tables is 
    typically similar to or smaller than the specified match radius) 
    it will make a difference. In this case one of the asymmetric 
    options (``best1`` or ``best2``) is usually more appropriate than best, 
    but you'll have to think about which of them suits your requirements. 
    The performance (time and memory usage) of the match may also differ 
    between these options, especially if one table is much bigger than 
    the other.
  
  fixcols : Literal['dups', 'all', 'none'], optional
    Determines how input columns are renamed before use in the output table. 
    The choices are:

    * ``none``: columns are not renamed
    * ``dups``: columns which would otherwise have duplicate names in the 
      output will be renamed to indicate which table they came from
    * ``all``: all columns will be renamed to indicate which table they 
      came from

    If columns are renamed, the new ones are determined by ``suffix*`` 
    parameters. 
  
  suffix1 : str, optional
    If the fixcols parameter is set so that input columns are renamed for 
    insertion into the output table, this parameter determines how the 
    renaming is done. It gives a suffix which is appended to all renamed 
    columns from table 1. 
  
  suffix2 : str, optional
    If the fixcols parameter is set so that input columns are renamed for 
    insertion into the output table, this parameter determines how the 
    renaming is done. It gives a suffix which is appended to all renamed 
    columns from table 2. 
  
  scorecol : str | None, optional
    Gives the name of a column in the output table to contain the "match score" 
    for each pairwise match. The meaning of this column is dependent on the 
    chosen ``matcher``, but it typically represents a distance of some kind 
    between the two matching points. If ``None`` is chosen, no score 
    column will be inserted in the output table. The default value of this 
    parameter depends on matcher. 
  
  fmt : Literal['fits', 'csv'], optional
    This function converts the two input tables to files to pass to 
    stilts backend. This parameter can be used to set the intermediate
    file types. Fits is faster and is the default file type.

  Returns
  -------
  pd.DataFrame | None
    The result table as a pandas dataframe  
  
  References
  ----------
  .. [#ST] STILTS - Starlink Tables Infrastructure Library Tool Set.
      `<https://www.star.bristol.ac.uk/mbt/stilts/>`_
  .. [#tmatch2] STILTS tmatch2 Documentation.
      `<https://www.star.bristol.ac.uk/mbt/stilts/sun256/tmatch2-usage.html>`_
  """
  tmpdir = Path(tempfile.gettempdir())
  token = secrets.token_hex(8)
  
  if isinstance(table1, (str, Path)) and Path(table1).suffix.lower() in ('.fits', '.csv', '.parquet'):
    tb1_path = Path(table1)
    fmt1 = tb1_path.suffix[1:]
    tmp1 = False
    if ra1 is None or dec1 is None:
      values1 = ''
    else:
      values1 = f'values2={ra2} {dec2}'
  else:
    fmt1 = 'parquet'
    tb1_path = tmpdir / f'xmatch_in1_{token}.{fmt1}'
    df1 = read_table(table1)
    if ra1 is None or dec1 is None:
      ra1, dec1 = guess_coords_columns(df1, ra1, dec1)
    values1 = f'values1={ra1} {dec1}'
    write_table(df1, tb1_path)
    tmp1 = True
      
  
  if isinstance(table2, (str, Path)) and Path(table2).suffix.lower() in ('.fits', '.csv', '.parquet'):
    tb2_path = Path(table2)
    fmt2 = tb2_path.suffix[1:]
    tmp2 = False
    if ra2 is None or dec2 is None:
      values2 = ''
    else:
      values2 = f'values2={ra2} {dec2}'
  else:
    fmt2 = 'parquet'
    tb2_path = tmpdir / f'xmatch_in2_{token}.{fmt2}'
    df2 = read_table(table2)
    if ra2 is None or dec2 is None:
      ra2, dec2 = guess_coords_columns(df2, ra2, dec2)
    values2 = f'values2={ra2} {dec2}'
    write_table(df2, tb2_path)
    tmp2 = True
  
  if isinstance(radius, u.Quantity):
    radius = float(radius.to(u.arcsec).value)
  else:
    radius = float(radius)
    
  topcatextra_path = download_file(
    'https://www.star.bris.ac.uk/~mbt/topcat/topcat-extra.jar', 
    cache=True, 
    pkgname='astromodule'
  )
  
  cmd = [
    'java',
    '-jar',
    topcatextra_path,
    '-stilts',
    'tmatch2',
    'matcher=sky',
    'progress=none',
    'runner=parallel',
    f'ifmt1={fmt1}',
    f'ifmt2={fmt2}',
    f'ofmt=parquet',
    'omode=out',
    f'out=-',
    values1,
    values2,
    f'params={radius}',
    f'join={join}',
    f'find={find}',
    f'fixcols={fixcols}',
    f'suffix1={suffix1}',
    f'suffix2={suffix2}',
    f'scorecol={scorecol or ""}',
    f'in1={str(tb1_path.absolute())}',
    f'in2={str(tb2_path.absolute())}',
  ]
  
  result = subprocess.run(
    cmd,
    stderr=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=False,
  )
  
  if tmp1:
    tb1_path.unlink()
  if tmp2:
    tb2_path.unlink()
  
  error = result.stderr.decode().strip()
  if error:
    print('STILTS proccess exited with an error signal.')
    print(error)
    return None
  
  df_out = read_table(BytesIO(result.stdout), fmt=fmt)
  return df_out



def selfmatch(
  table: TableLike | PathOrFile,
  radius: float | u.Quantity,
  action: Literal['identify', 'keep0', 'keep1', 'wide2', 'wideN'] = 'keep1',
  ra: str | None = None,
  dec: str | None = None,
  fmt: Literal['fits', 'csv', 'parquet'] = 'parquet',
) -> pd.DataFrame | None:
  """
  Performs a selfmatch in a table (crossmatch agains the same table) using 
  STILTS [#ST]_ as a backend (the same backend of TOPCAT [#TOPCAT]_). 
  This is useful for duplicates removal, groups detection, etc. 
  This function spawns a subprocess invoking the ``tmatch1`` [#tmatch1]_ 
  tool of the STILTS executable.

  Parameters
  ----------
  table : TableLike | PathOrFile
    The table that will be crossmatched. This parameter accepts a
    table-like object (pandas dataframe, astropy table), a path to a file
    represented as a `str` or `pathlib.Path` object, or a file object
    (BinaryIO, StringIO, file-descriptor, etc).
  
  radius : float | u.Quantity
    The crossmatch max error radius. This function accepts a ``float`` value,
    that will be interpreted as ``arcsec`` unit, or a `astropy.units.Quantity`
  
  action : Literal['identify', 'keep0', 'keep1', 'wide2', 'wideN'], optional
    Determines the form of the table which will be output as a result of the 
    internal match.

    * ``identify``: The output table is the same as the input table except 
      that it contains two additional columns, GroupID and GroupSize, 
      following the input columns. Each group of rows which matched is 
      assigned a unique integer, recorded in the GroupID column, and the 
      size of each group is recorded in the GroupSize column. Rows which 
      don't match any others (singles) have null values in both these columns.
    * ``keep0``: The result is a new table containing only "single" rows, 
      that is ones which don't match any other rows in the table. 
      Any other rows are thrown out.
    * ``keep1``: The result is a new table in which only one row 
      (the first in the input table order) from each group of matching 
      ones is retained. A subsequent intra-table match with the same 
      criteria would therefore show no matches.
    * ``wideN``: The result is a new "wide" table consisting of matched 
      rows in the input table stacked next to each other. Only groups of 
      exactly N rows in the input table are used to form the output table; 
      each row of the output table consists of the columns of the first 
      group member, followed by the columns of the second group member 
      and so on. The output table therefore has N times as many columns 
      as the input table. The column names in the new table have _1, _2, ... 
      appended to them to avoid duplication.

  ra : str | None, optional
    The name of the Right Ascension (RA) column. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  dec : str | None, optional
    The name of the Declination (DEC) column. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  fmt : Literal['fits', 'csv'], optional
    This function converts the input table to file before passing to 
    stilts backend. This parameter can be used to set the intermediate
    file type. Fits is faster and is the default file type.

  Returns
  -------
  pd.DataFrame | None
    A table of resulting selfmatch 
      
  References
  ----------
  .. [#TOPCAT] TOPCAT - Tool for OPerations on Catalogues And Tables.
      `<https://www.star.bristol.ac.uk/mbt/topcat/>`_
  .. [#ST] STILTS - Starlink Tables Infrastructure Library Tool Set.
      `<https://www.star.bristol.ac.uk/mbt/stilts/>`_
  .. [#tmatch1] STILTS tmatch1 Documentation.
      `<https://www.star.bristol.ac.uk/mbt/stilts/sun256/tmatch1-usage.html>`_
  """
  tmpdir = Path(tempfile.gettempdir())
  token = secrets.token_hex(8)
  in_path = tmpdir / f'xmatch_in_{token}.{fmt}'
  
  df = read_table(table)
  
  ra, dec = guess_coords_columns(df, ra, dec)
  
  write_table(df, in_path)
  
  # input_stream = BytesIO()
  # write_table(df, input_stream, fmt=fmt)
  # input_stream.seek(0)
  
  if isinstance(radius, u.Quantity):
    radius = float(radius.to(u.arcsec).value)
  else:
    radius = float(radius)
  
  topcatextra_path = download_file(
    'https://www.star.bris.ac.uk/~mbt/topcat/topcat-extra.jar', 
    cache=True, 
    pkgname='astromodule'
  )
  
  cmd = [
    'java',
    '-jar',
    topcatextra_path,
    '-stilts',
    'tmatch1',
    'matcher=sky',
    'progress=none',
    'runner=parallel',
    f'params={radius}',
    f'values={ra} {dec}',
    f'action={action}',
    f'ifmt={fmt}',
    f'ofmt={fmt}',
    'omode=out',
    'out=-',
    f'in={str(in_path.absolute())}',
  ]
  
  result = subprocess.run(
    cmd,
    stderr=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=False,
  )
  
  in_path.unlink()
  
  error = result.stderr.decode().strip()
  if error:
    print('STILTS proccess exited with an error signal.')
    print(error)
    return None
  
  df_out = read_table(BytesIO(result.stdout), fmt=fmt)
  return df_out




def crossmatch_cds(
  table: TableLike | PathOrFile,
  cds_table: str = 'simbad',
  radius: float | u.Quantity = 1.0,
  ra: str | None = None,
  dec: str | None = None,
  find: Literal['all', 'best', 'best-remote', 'each', 'each-dist'] = 'all',
  fixcols: Literal['none', 'dups', 'all'] = 'dups',
  suffix_in: str = '_in',
  suffix_remote: str = '_cds',
  block_size: int = 50_000,
  use_moc: bool = False,
  pre_sort: bool = False,
  service_url: str = None,
  fmt: Literal['fits', 'csv', 'parquet'] = 'parquet',
):
  """
  Uses the CDS X-Match service to join a local table to one of the tables 
  hosted by the Centre de Données astronomiques de Strasbourg. This includes 
  all of the VizieR tables and the SIMBAD database. The service is very fast, 
  and in most cases it is the best way to match a local table against a large 
  external table hosted by a service.
  
  The local table is uploaded to the X-Match service in chunks, and the matches 
  for each chunk are retrieved in turn and eventually stitched together to form 
  the final result. The tool only uploads sky position and an identifier for each 
  row of the input table, but all columns of the input table are reinstated in 
  the result for reference. 
  
  Parameters
  ----------
  table : TableLike | PathOrFile
    The table that will be crossmatched. This parameter accepts a
    table-like object (pandas dataframe, astropy table), a path to a file
    represented as a `str` or `pathlib.Path` object, or a file object
    (BinaryIO, StringIO, file-descriptor, etc).
  
  cds_table : str
    Identifier of the table from the CDS crossmatch service that is to be 
    matched against the local table. This identifier may be the standard VizieR 
    identifier (e.g. "II/246/out" for the 2MASS Point Source Catalogue) or 
    "simbad" to indicate SIMBAD data.

    See for instance the TAPVizieR table searching facility 
    at http://tapvizier.u-strasbg.fr/adql/ to find VizieR catalogue identifiers.
  
  radius : float | u.Quantity
    The crossmatch max error radius. This function accepts a ``float`` value,
    that will be interpreted as ``arcsec`` unit, or a `astropy.units.Quantity`.
  
  ra : str
    The name of the Right Ascension (RA) column. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  dec : str
    The name of the Declination (Dec) column. If ``None``
    is passed, this function will try to guess the RA column name based on
    predefined patterns using the function `~guess_coords_columns`, see this
    function's documentation for more details.
  
  find : "all" or "best" or "best-remote" or "each" or "each-dist"
    Determines which pair matches are included in the result.

    * ``all``: All matches
    * ``best``: Matched rows, best remote row for each input row
    * ``best-remote``: Matched rows, best input row for each remote row
    * ``each``: One row per input row, contains best remote match or blank
    * ``each-dist``: One row per input row, column giving distance only for best match

    Note only the all mode is symmetric between the two tables. 
    
    Note also that there is a bug in best-remote matching. If the match is done 
    in multiple blocks, it's possible for a remote table row to appear matched 
    against one local table row per uploaded block, rather than just once for 
    the whole result. If you're worried about that, set blocksize >= rowCount. 
    This may be fixed in a future release. 
  
  fixcols : "none" or "dups" or "all"
    Determines how input columns are renamed before use in the output table. The choices are:

    * ``none``: columns are not renamed
    * ``dups``: columns which would otherwise have duplicate names in the output 
        will be renamed to indicate which table they came from
    * ``all``: all columns will be renamed to indicate which table they came from

    If columns are renamed, the new ones are determined by ``suffix*`` parameters. 
    
  suffix_in : str
    If the fixcols parameter is set so that input columns are renamed for 
    insertion into the output table, this parameter determines how the renaming 
    is done. It gives a suffix which is appended to all renamed columns from the 
    input table. Default: "_in"
    
  suffix_remote : str
    If the fixcols parameter is set so that input columns are renamed for insertion 
    into the output table, this parameter determines how the renaming is done. 
    It gives a suffix which is appended to all renamed columns from the 
    CDS result table. Default: "_cds"
  
  block_sise : int
    The CDS Xmatch service operates limits on the maximum number of rows that 
    can be uploaded and the maximum number of rows that is returned as a result 
    from a single query. In the case of large input tables, they are broken down 
    into smaller blocks, and one request is sent to the external service for 
    each block. This parameter controls the number of rows in each block. 
    For an input table with fewer rows than this value, the whole thing is 
    done as a single request.

    At time of writing, the maximum upload size is 100Mb (about 3Mrow; 
    this does not depend on the width of your table), and the maximum 
    return size is 2Mrow.

    Large blocksizes tend to be good (up to a point) for reducing the total 
    amount of time a large xmatch operation takes, but they can make it harder 
    to see the job progressing. There is also the danger (for ALL-type find modes) 
    of exceeding the return size limit, which will result in truncation of the 
    returned result. 
  
  use_moc : bool
    If true, first acquire a MOC coverage map from CDS, and use that to 
    pre-filter rows before uploading them for matching. This should improve 
    efficiency, but have no effect on the result. 
  
  pre_sort : bool
    If true, the rows are sorted by HEALPix index before they are uploaded to 
    the CDS X-Match service. If the match is done in multiple blocks, this may 
    improve efficiency, since when matching against a large remote catalogue 
    the X-Match service likes to process requests in which sources are grouped 
    into a small region rather than scattered all over the sky.

    Note this will have a couple of other side effects that may be undesirable: 
    it will read all the input rows into the task at once, which may make it 
    harder to assess progress, and it will affect the order of the rows in the 
    output table.

    It is probably only worth setting true for rather large (multi-million-row?) 
    multi-block matches, where both local and remote catalogues are spread over a 
    significant fraction of the sky. But feel free to experiment. 
  
  service_url : str
    The URL at which the CDS Xmatch service can be found. Normally this should 
    not be altered from the default, but if other implementations of the same 
    service are known, this parameter can be used to access them. 
  
  fmt : "fits" or "csv" or "parquet"
    This function converts the input table to file before passing to 
    stilts backend. This parameter can be used to set the intermediate
    file type. Fits is faster and is the default file type.
  """
  tmpdir = Path(tempfile.gettempdir())
  token = secrets.token_hex(8)
  
  if isinstance(table, (str, Path)) and Path(table).suffix.lower() in ('.fits', '.csv', '.parquet'):
    in_path = Path(table)
    fmt = in_path.suffix[1:]
    tmp = False
  else:
    in_path = tmpdir / f'cdsmatch_{token}.{fmt}'
    df = read_table(table)
    if ra is None or dec is None:
      ra, dec = guess_coords_columns(df, ra, dec)
    write_table(df, in_path)
    tmp = True
  
  ra_param, dec_param = '', ''
  if ra: ra_param = f'ra={ra}'
  if dec: dec_param = f'dec={dec}'
    
  service_url_param = f'serviceurl={service_url}' if service_url else ''
  use_moc = 'true' if use_moc else 'false'
  pre_sort = 'true' if pre_sort else 'false'
  
  if isinstance(radius, u.Quantity):
    radius = float(radius.to(u.arcsec).value)
  else:
    radius = float(radius)
  
  topcatextra_path = download_file(
    'https://www.star.bris.ac.uk/~mbt/topcat/topcat-extra.jar', 
    cache=True, 
    pkgname='astromodule'
  )

  cmd = [
    'java',
    '-jar',
    topcatextra_path,
    '-stilts',
    'cdsskymatch',
    f'ifmt={fmt}',
    'omode=out',
    'out=-',
    f'ofmt={fmt}',
    ra_param,
    dec_param,
    f'radius={radius}',
    f'cdstable={cds_table}',
    f'find={find}',
    f'blocksize={block_size}',
    'compress=true',
    service_url_param,
    f'usemoc={use_moc}',
    f'presort={pre_sort}',
    f'fixcols={fixcols}',
    f'suffixin={suffix_in}',
    f'suffixremote={suffix_remote}',
    f'in={str(in_path.absolute())}',
  ]
  
  cmd = list(filter(lambda x: x != '', cmd))
  
  result = subprocess.run(
    cmd,
    stderr=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=False,
  )
  
  if tmp:
    in_path.unlink()
  
  error = result.stderr.decode().strip()
  if result.returncode != 0:
    print('STILTS proccess exited with an error signal.')
    print(error)
    return None
  elif error:
    print(error)
  
  df_out = read_table(BytesIO(result.stdout), fmt=fmt)
  return df_out



def radial_search(
  position: SkyCoord,
  table: TableLike,
  radius: float | u.Quantity,
  ra: str = None,
  dec: str = None,
  frame: str = 'icrs',
  cached_catalog: SkyCoord = None,
  include_sep: bool = False,
):
  df = read_table(table)
  ra, dec = guess_coords_columns(df, ra, dec)
    
  if not isinstance(radius, u.Quantity):
    radius = radius * u.arcsec
  
  if cached_catalog:
    catalog = cached_catalog
  else:
    catalog = SkyCoord(ra=df[ra].values, dec=df[dec].values, unit=u.deg, frame=frame)
  
  separation = catalog.separation(position)
  mask = separation < radius
  
  df2 = df.copy()
  
  if include_sep:
    df2.loc[:, 'separation'] = separation
  
  return df2[mask]
  



def concat_tables(
  tables: Sequence[TableLike | PathOrFile],
  progress: bool = False,
  **kwargs
) -> pd.DataFrame:
  """
  Concatenate tables into a single one. This function concatenate over the
  table rows and is usefull to concatenate tables with same columns, although 
  there is no error in concatenating tables with non-existent columns in other.
  If a table does not have a certain column, the values will be filled with 
  ``NaN`` values. This function does not attempt to apply any type of 
  duplicate row removal.

  Parameters
  ----------
  tables : Sequence[TableLike  |  PathOrFile]
    A sequence of tables to be concatenated. This parameter accepts a
    table-like object (pandas dataframe, astropy table), a path to a file
    represented as a string or pathlib.Path object, or a file object
    (BinaryIO, StringIO, file-descriptor, etc).
  kwargs : Any
    Arguments that will be passed to `~astromodule.io.read_table` function

  Returns
  -------
  pd.DataFrame
    A dataframe with concatenated tables or a empty dataframe
  """
  pb = tqdm if progress else lambda x, **_: x
  dfs = []
  for table in pb(tables, unit='table'):
    try:
      dfs.append(read_table(table, **kwargs))
    except pd.errors.EmptyDataError:
      pass
  if len(dfs) > 0:
    return pd.concat(dfs)
  return pd.DataFrame()


if __name__ == '__main__':
  # df = selfmatch(
  #   Path(__file__).parent.parent / 'tests' / 'selection_claudia+prepared.csv',
  #   radius=45*u.arcmin,
  #   action='identify',
  #   fmt='parquet'
  # )
  # df = crossmatch(
  #   Path(__file__).parent.parent / 'tests' / 'selection_claudia+prepared.csv',
  #   Path(__file__).parent.parent / 'tests' / 'selection_claudia+prepared+top20.csv',
  #   radius=1*u.arcsec,
  # )
  df = crossmatch_cds(
    Path(__file__).parent.parent / 'tests' / 'selection_claudia+prepared+top20.csv',
    ra='ra',
    dec='dec',
  )
  print(df)